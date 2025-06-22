"""
Payroll Management Signals
Handle automatic calculations and processing for payroll management
"""
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import models
from decimal import Decimal
from datetime import datetime, date, timedelta
from .models import (
    PayrollPeriod, PayrollTransaction, EmployeePayslip, 
    PayslipComponent, EmployeeSalaryStructure
)


@receiver(post_save, sender=PayrollPeriod)
def initialize_payroll_period(sender, instance, created, **kwargs):
    """Initialize payroll period with employee count"""
    if created:
        # Count active employees
        from employee_management.models import Employee
        active_employees = Employee.objects.filter(
            is_active=True,
            hire_date__lte=instance.end_date
        ).exclude(
            termination_date__lt=instance.start_date
        ).count()
        
        instance.total_employees = active_employees
        instance.save(update_fields=['total_employees'])


@receiver(post_save, sender=PayrollTransaction)
def update_payroll_period_on_transaction(sender, instance, created, **kwargs):
    """Update payroll period when transactions are added"""
    if instance.is_approved and instance.is_processed:
        # Recalculate period totals
        calculate_payroll_period_totals(instance.payroll_period)


@receiver(post_save, sender=EmployeePayslip)
def update_payroll_period_on_payslip(sender, instance, created, **kwargs):
    """Update payroll period when payslips are processed"""
    if instance.status in ['calculated', 'approved', 'paid']:
        # Update processed employee count
        processed_count = EmployeePayslip.objects.filter(
            payroll_period=instance.payroll_period,
            status__in=['calculated', 'approved', 'paid']
        ).count()
        
        instance.payroll_period.processed_employees = processed_count
        instance.payroll_period.save(update_fields=['processed_employees'])
        
        # Recalculate period totals
        calculate_payroll_period_totals(instance.payroll_period)


def calculate_payroll_period_totals(payroll_period):
    """Calculate total amounts for a payroll period"""
    payslips = EmployeePayslip.objects.filter(
        payroll_period=payroll_period,
        status__in=['calculated', 'approved', 'paid']
    )
    
    totals = payslips.aggregate(
        total_gross=models.Sum('gross_salary'),
        total_deductions=models.Sum('total_deductions'),
        total_net=models.Sum('net_salary')
    )
    
    payroll_period.total_gross_salary = totals['total_gross'] or Decimal('0')
    payroll_period.total_deductions = totals['total_deductions'] or Decimal('0')
    payroll_period.total_net_salary = totals['total_net'] or Decimal('0')
    
    payroll_period.save(update_fields=[
        'total_gross_salary', 'total_deductions', 'total_net_salary'
    ])


@receiver(pre_save, sender=EmployeePayslip)
def calculate_payslip_totals(sender, instance, **kwargs):
    """Calculate payslip totals before saving"""
    if instance.pk:
        # Calculate totals from components
        components = PayslipComponent.objects.filter(payslip=instance)
        
        # Calculate allowances and bonuses
        allowances = components.filter(
            component__component_type__in=['allowance', 'bonus', 'overtime', 'commission']
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
        
        # Calculate deductions
        deductions = components.filter(
            component__component_type__in=['deduction', 'tax', 'insurance', 'loan_deduction', 'advance_deduction']
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
        
        # Update payslip totals
        instance.total_allowances = allowances
        instance.total_deductions = deductions
        instance.gross_salary = instance.basic_salary + allowances
        instance.net_salary = instance.gross_salary - deductions


@receiver(post_save, sender='employee_management.Employee')
def create_default_salary_structure(sender, instance, created, **kwargs):
    """Create default salary structure for new employees"""
    if created and instance.job_title:
        # Create basic salary structure based on job title
        min_salary = instance.job_title.min_salary or Decimal('0')
        
        EmployeeSalaryStructure.objects.create(
            employee=instance,
            basic_salary=min_salary,
            effective_from=instance.hire_date,
            is_active=True,
            created_by_id=1  # System user - should be configurable
        )


def calculate_employee_payslip(employee, payroll_period):
    """Calculate payslip for an employee in a specific period"""
    try:
        # Get active salary structure
        salary_structure = EmployeeSalaryStructure.objects.filter(
            employee=employee,
            is_active=True,
            effective_from__lte=payroll_period.end_date
        ).filter(
            models.Q(effective_to__isnull=True) | models.Q(effective_to__gte=payroll_period.start_date)
        ).first()
        
        if not salary_structure:
            return None
        
        # Get or create payslip
        payslip, created = EmployeePayslip.objects.get_or_create(
            employee=employee,
            payroll_period=payroll_period,
            defaults={
                'salary_structure': salary_structure,
                'basic_salary': salary_structure.basic_salary,
                'status': 'draft'
            }
        )
        
        # Get attendance data
        attendance_data = get_employee_attendance_data(employee, payroll_period)
        
        # Update attendance information
        payslip.working_days = attendance_data['working_days']
        payslip.present_days = attendance_data['present_days']
        payslip.absent_days = attendance_data['absent_days']
        payslip.leave_days = attendance_data['leave_days']
        payslip.overtime_hours = attendance_data['overtime_hours']
        
        # Calculate pro-rated basic salary
        if payslip.working_days > 0:
            attendance_ratio = payslip.present_days / payslip.working_days
            payslip.basic_salary = salary_structure.basic_salary * Decimal(str(attendance_ratio))
        
        # Calculate salary components
        calculate_salary_components(payslip, salary_structure)
        
        # Calculate overtime
        calculate_overtime_amount(payslip)
        
        # Get approved transactions
        transactions = PayrollTransaction.objects.filter(
            employee=employee,
            payroll_period=payroll_period,
            is_approved=True
        )
        
        # Apply transactions
        for transaction in transactions:
            create_payslip_component_from_transaction(payslip, transaction)
        
        # Calculate taxes and deductions
        calculate_taxes_and_deductions(payslip)
        
        # Update status and save
        payslip.status = 'calculated'
        payslip.calculation_date = timezone.now()
        payslip.save()
        
        return payslip
        
    except Exception as e:
        # Log error and return None
        return None


def get_employee_attendance_data(employee, payroll_period):
    """Get attendance data for an employee in a payroll period"""
    try:
        from attendance_system.models import DailyAttendance
        
        daily_records = DailyAttendance.objects.filter(
            employee=employee,
            attendance_date__range=[payroll_period.start_date, payroll_period.end_date],
            is_processed=True
        )
        
        working_days = daily_records.exclude(status__in=['holiday', 'weekend']).count()
        present_days = daily_records.filter(status__in=['present', 'late', 'early_departure']).count()
        absent_days = daily_records.filter(status='absent').count()
        leave_days = daily_records.filter(status='leave').count()
        
        overtime_hours = daily_records.aggregate(
            total_overtime=models.Sum('overtime_hours')
        )['total_overtime'] or Decimal('0')
        
        return {
            'working_days': working_days,
            'present_days': present_days,
            'absent_days': absent_days,
            'leave_days': leave_days,
            'overtime_hours': overtime_hours
        }
        
    except ImportError:
        # Attendance system not available
        return {
            'working_days': 30,  # Default
            'present_days': 30,
            'absent_days': 0,
            'leave_days': 0,
            'overtime_hours': Decimal('0')
        }


def calculate_salary_components(payslip, salary_structure):
    """Calculate salary components for a payslip"""
    # Clear existing components
    PayslipComponent.objects.filter(payslip=payslip).delete()
    
    # Get employee salary components
    employee_components = salary_structure.salary_components.filter(is_active=True)
    
    for emp_component in employee_components:
        component = emp_component.component
        
        # Calculate amount based on calculation method
        if component.calculation_method == 'fixed':
            amount = emp_component.amount
        elif component.calculation_method == 'percentage':
            base_amount = payslip.basic_salary
            percentage = emp_component.percentage or component.percentage_rate or Decimal('0')
            amount = base_amount * (percentage / 100)
        else:
            amount = emp_component.amount
        
        # Create payslip component
        PayslipComponent.objects.create(
            payslip=payslip,
            component=component,
            amount=amount,
            calculation_base=payslip.basic_salary,
            rate_or_percentage=emp_component.percentage
        )


def calculate_overtime_amount(payslip):
    """Calculate overtime amount for a payslip"""
    if payslip.overtime_hours > 0:
        # Calculate hourly rate (basic salary / 30 days / 8 hours)
        hourly_rate = payslip.basic_salary / Decimal('240')  # 30 days * 8 hours
        overtime_multiplier = Decimal('1.5')  # Standard overtime multiplier
        
        payslip.overtime_amount = payslip.overtime_hours * hourly_rate * overtime_multiplier
    else:
        payslip.overtime_amount = Decimal('0')


def calculate_taxes_and_deductions(payslip):
    """Calculate taxes and mandatory deductions"""
    # This is a simplified calculation - should be based on TaxConfiguration
    taxable_income = payslip.gross_salary
    
    # Simple tax calculation (should use TaxConfiguration)
    if taxable_income > Decimal('3000'):
        payslip.tax_deduction = (taxable_income - Decimal('3000')) * Decimal('0.05')
    else:
        payslip.tax_deduction = Decimal('0')
    
    # Insurance deduction (example: 2% of basic salary)
    payslip.insurance_deduction = payslip.basic_salary * Decimal('0.02')


def create_payslip_component_from_transaction(payslip, transaction):
    """Create payslip component from a payroll transaction"""
    from .models import SalaryComponent
    
    # Try to find matching component or create a generic one
    try:
        component = SalaryComponent.objects.get(
            component_type=transaction.transaction_type,
            is_active=True
        )
    except SalaryComponent.DoesNotExist:
        # Create a generic component for this transaction type
        component, created = SalaryComponent.objects.get_or_create(
            component_name=f"{transaction.get_transaction_type_display()}",
            component_type=transaction.transaction_type,
            defaults={
                'calculation_method': 'fixed',
                'is_active': True
            }
        )
    
    # Create payslip component
    PayslipComponent.objects.create(
        payslip=payslip,
        component=component,
        amount=transaction.amount,
        calculation_notes=f"Transaction: {transaction.description}"
    )
