"""
Leave Management Signals
Handle automatic actions and notifications for leave management
"""
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal
from .models import LeaveRequest, LeaveApproval, LeaveBalance, LeaveType


@receiver(post_save, sender=LeaveRequest)
def leave_request_post_save(sender, instance, created, **kwargs):
    """Handle leave request creation and updates"""
    if created:
        # Update pending days in leave balance
        try:
            balance, created_balance = LeaveBalance.objects.get_or_create(
                employee=instance.employee,
                leave_type=instance.leave_type,
                year=instance.start_date.year,
                defaults={
                    'allocated_days': instance.leave_type.default_balance,
                    'used_days': 0,
                    'pending_days': 0,
                    'carried_over_days': 0,
                }
            )
            
            # Add to pending days
            balance.pending_days += instance.requested_days
            balance.save()
            
        except Exception as e:
            # Log error but don't fail the request creation
            pass
    
    # Handle status changes
    if instance.pk:
        try:
            old_instance = LeaveRequest.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                handle_status_change(old_instance, instance)
        except LeaveRequest.DoesNotExist:
            pass


@receiver(post_save, sender=LeaveApproval)
def leave_approval_post_save(sender, instance, created, **kwargs):
    """Handle leave approval actions"""
    if created:
        leave_request = instance.leave_request
        
        if instance.action == 'approve':
            # Update leave request status
            leave_request.status = 'approved'
            leave_request.approved_days = instance.approved_days or leave_request.requested_days
            leave_request.save()
            
            # Update leave balance
            update_leave_balance_on_approval(leave_request)
            
        elif instance.action == 'reject':
            # Update leave request status
            leave_request.status = 'rejected'
            leave_request.save()
            
            # Remove from pending days
            remove_from_pending_balance(leave_request)


def handle_status_change(old_instance, new_instance):
    """Handle leave request status changes"""
    if old_instance.status == 'submitted' and new_instance.status == 'cancelled':
        # Remove from pending days
        remove_from_pending_balance(new_instance)
    
    elif old_instance.status == 'approved' and new_instance.status == 'in_progress':
        # Leave has started - no balance changes needed as already handled in approval
        pass
    
    elif old_instance.status == 'in_progress' and new_instance.status == 'completed':
        # Leave completed - update actual return date if not set
        if not new_instance.actual_return_date:
            new_instance.actual_return_date = timezone.now().date()
            new_instance.save()


def update_leave_balance_on_approval(leave_request):
    """Update leave balance when request is approved"""
    try:
        balance = LeaveBalance.objects.get(
            employee=leave_request.employee,
            leave_type=leave_request.leave_type,
            year=leave_request.start_date.year
        )
        
        # Move from pending to used
        approved_days = leave_request.approved_days or leave_request.requested_days
        balance.pending_days -= leave_request.requested_days
        balance.used_days += approved_days
        
        # Ensure pending days don't go negative
        if balance.pending_days < 0:
            balance.pending_days = 0
            
        balance.save()
        
    except LeaveBalance.DoesNotExist:
        # Create balance if it doesn't exist
        LeaveBalance.objects.create(
            employee=leave_request.employee,
            leave_type=leave_request.leave_type,
            year=leave_request.start_date.year,
            allocated_days=leave_request.leave_type.default_balance,
            used_days=leave_request.approved_days or leave_request.requested_days,
            pending_days=0,
            carried_over_days=0,
        )


def remove_from_pending_balance(leave_request):
    """Remove days from pending balance when request is cancelled/rejected"""
    try:
        balance = LeaveBalance.objects.get(
            employee=leave_request.employee,
            leave_type=leave_request.leave_type,
            year=leave_request.start_date.year
        )
        
        balance.pending_days -= leave_request.requested_days
        
        # Ensure pending days don't go negative
        if balance.pending_days < 0:
            balance.pending_days = 0
            
        balance.save()
        
    except LeaveBalance.DoesNotExist:
        pass


@receiver(post_save, sender='employee_management.Employee')
def create_initial_leave_balances(sender, instance, created, **kwargs):
    """Create initial leave balances for new employees"""
    if created:
        # Get all active leave types
        leave_types = LeaveType.objects.filter(is_active=True)
        current_year = timezone.now().year
        
        for leave_type in leave_types:
            # Calculate allocated days based on hire date and leave type
            allocated_days = calculate_initial_allocation(instance, leave_type, current_year)
            
            LeaveBalance.objects.get_or_create(
                employee=instance,
                leave_type=leave_type,
                year=current_year,
                defaults={
                    'allocated_days': allocated_days,
                    'used_days': 0,
                    'pending_days': 0,
                    'carried_over_days': 0,
                }
            )


def calculate_initial_allocation(employee, leave_type, year):
    """Calculate initial leave allocation for an employee"""
    if leave_type.calculation_method == 'fixed':
        return leave_type.default_balance
    
    elif leave_type.calculation_method == 'yearly':
        # Pro-rate based on hire date if hired during the year
        hire_year = employee.hire_date.year
        if hire_year == year:
            # Calculate pro-rated allocation
            days_in_year = 365 if year % 4 != 0 else 366
            days_remaining = (timezone.datetime(year, 12, 31).date() - employee.hire_date).days + 1
            pro_rate = days_remaining / days_in_year
            return Decimal(str(float(leave_type.default_balance) * pro_rate)).quantize(Decimal('0.01'))
        else:
            return leave_type.default_balance
    
    elif leave_type.calculation_method == 'monthly':
        # Calculate based on months of service
        hire_year = employee.hire_date.year
        if hire_year == year:
            months_remaining = 12 - employee.hire_date.month + 1
            monthly_allocation = leave_type.default_balance / 12
            return Decimal(str(float(monthly_allocation) * months_remaining)).quantize(Decimal('0.01'))
        else:
            return leave_type.default_balance
    
    elif leave_type.calculation_method == 'service_based':
        # Calculate based on years of service (simplified)
        years_of_service = year - employee.hire_date.year
        if years_of_service < 1:
            return leave_type.default_balance
        elif years_of_service < 5:
            return leave_type.default_balance
        elif years_of_service < 10:
            return leave_type.default_balance + Decimal('5')  # 5 extra days
        else:
            return leave_type.default_balance + Decimal('10')  # 10 extra days
    
    return leave_type.default_balance


# Signal to handle year-end carryover
@receiver(post_save, sender=LeaveBalance)
def handle_carryover_calculation(sender, instance, created, **kwargs):
    """Handle automatic carryover calculation at year end"""
    if not created:
        # Check if this is a year-end update that might trigger carryover
        if instance.leave_type.allow_carryover and instance.available_days > 0:
            next_year = instance.year + 1
            
            # Check if next year balance exists
            next_balance, created_next = LeaveBalance.objects.get_or_create(
                employee=instance.employee,
                leave_type=instance.leave_type,
                year=next_year,
                defaults={
                    'allocated_days': instance.leave_type.default_balance,
                    'used_days': 0,
                    'pending_days': 0,
                    'carried_over_days': 0,
                }
            )
            
            if created_next:
                # Calculate carryover amount
                max_carryover = instance.leave_type.max_carryover_days or instance.available_days
                carryover_amount = min(instance.available_days, max_carryover)
                
                next_balance.carried_over_days = carryover_amount
                next_balance.save()
