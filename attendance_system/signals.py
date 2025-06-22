"""
Attendance System Signals
Handle automatic processing and calculations for attendance system
"""
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import models
from decimal import Decimal
from datetime import datetime, time, timedelta
from .models import (
    AttendanceRecord, DailyAttendance, AttendanceException,
    MonthlyAttendanceSummary, AttendanceRule
)


@receiver(post_save, sender=AttendanceRecord)
def process_attendance_record(sender, instance, created, **kwargs):
    """Process attendance record and update daily attendance"""
    if created and instance.is_valid and not instance.is_processed:
        try:
            # Get or create daily attendance record
            daily_attendance, created_daily = DailyAttendance.objects.get_or_create(
                employee=instance.employee,
                attendance_date=instance.punch_time.date(),
                defaults={
                    'status': 'incomplete',
                    'is_processed': False,
                }
            )
            
            # Update daily attendance based on punch type
            update_daily_attendance(daily_attendance, instance)
            
            # Mark record as processed
            instance.is_processed = True
            instance.save(update_fields=['is_processed'])
            
        except Exception as e:
            # Log error but don't fail the record creation
            instance.error_message = str(e)
            instance.is_valid = False
            instance.save(update_fields=['error_message', 'is_valid'])


def update_daily_attendance(daily_attendance, attendance_record):
    """Update daily attendance record with new punch data"""
    punch_time = attendance_record.punch_time.time()
    punch_type = attendance_record.punch_type
    
    # Update times based on punch type
    if punch_type == 'check_in':
        if not daily_attendance.check_in_time or punch_time < daily_attendance.check_in_time:
            daily_attendance.check_in_time = punch_time
    
    elif punch_type == 'check_out':
        if not daily_attendance.check_out_time or punch_time > daily_attendance.check_out_time:
            daily_attendance.check_out_time = punch_time
    
    elif punch_type == 'break_out':
        daily_attendance.break_out_time = punch_time
    
    elif punch_type == 'break_in':
        daily_attendance.break_in_time = punch_time
    
    # Calculate work hours and status
    calculate_daily_attendance_metrics(daily_attendance)
    daily_attendance.save()


def calculate_daily_attendance_metrics(daily_attendance):
    """Calculate work hours, overtime, and status for daily attendance"""
    # Get applicable attendance rule
    rule = get_applicable_attendance_rule(daily_attendance.employee, daily_attendance.attendance_date)
    daily_attendance.attendance_rule = rule
    
    if not rule:
        daily_attendance.status = 'incomplete'
        return
    
    # Calculate work hours
    if daily_attendance.check_in_time and daily_attendance.check_out_time:
        # Calculate total time
        check_in_datetime = datetime.combine(daily_attendance.attendance_date, daily_attendance.check_in_time)
        check_out_datetime = datetime.combine(daily_attendance.attendance_date, daily_attendance.check_out_time)
        
        # Handle overnight shifts
        if daily_attendance.check_out_time < daily_attendance.check_in_time:
            check_out_datetime += timedelta(days=1)
        
        total_minutes = (check_out_datetime - check_in_datetime).total_seconds() / 60
        
        # Calculate break duration
        break_minutes = 0
        if daily_attendance.break_out_time and daily_attendance.break_in_time:
            break_out_datetime = datetime.combine(daily_attendance.attendance_date, daily_attendance.break_out_time)
            break_in_datetime = datetime.combine(daily_attendance.attendance_date, daily_attendance.break_in_time)
            
            if daily_attendance.break_in_time > daily_attendance.break_out_time:
                break_minutes = (break_in_datetime - break_out_datetime).total_seconds() / 60
        
        daily_attendance.break_duration_minutes = int(break_minutes)
        
        # Calculate net work hours
        net_work_minutes = total_minutes - break_minutes
        daily_attendance.total_work_hours = Decimal(net_work_minutes / 60).quantize(Decimal('0.01'))
        
        # Calculate late minutes
        if rule.work_start_time:
            expected_start = datetime.combine(daily_attendance.attendance_date, rule.work_start_time)
            actual_start = check_in_datetime
            
            if actual_start > expected_start:
                late_minutes = (actual_start - expected_start).total_seconds() / 60
                daily_attendance.late_minutes = max(0, int(late_minutes - rule.late_grace_minutes))
        
        # Calculate early departure minutes
        if rule.work_end_time:
            expected_end = datetime.combine(daily_attendance.attendance_date, rule.work_end_time)
            actual_end = check_out_datetime
            
            if actual_end < expected_end:
                early_minutes = (expected_end - actual_end).total_seconds() / 60
                daily_attendance.early_departure_minutes = max(0, int(early_minutes - rule.early_departure_grace_minutes))
        
        # Calculate overtime
        if rule.overtime_threshold_minutes and net_work_minutes > rule.overtime_threshold_minutes:
            overtime_minutes = net_work_minutes - rule.overtime_threshold_minutes
            daily_attendance.overtime_hours = Decimal(overtime_minutes / 60).quantize(Decimal('0.01'))
        
        # Determine status
        if daily_attendance.late_minutes > 0:
            daily_attendance.status = 'late'
        elif daily_attendance.early_departure_minutes > 0:
            daily_attendance.status = 'early_departure'
        else:
            daily_attendance.status = 'present'
    
    else:
        # Incomplete attendance
        if daily_attendance.check_in_time and not daily_attendance.check_out_time:
            daily_attendance.status = 'incomplete'
        else:
            daily_attendance.status = 'absent'


def get_applicable_attendance_rule(employee, date):
    """Get the applicable attendance rule for an employee on a specific date"""
    rules = AttendanceRule.objects.filter(
        is_active=True,
        effective_from__lte=date,
    ).filter(
        models.Q(effective_to__isnull=True) | models.Q(effective_to__gte=date)
    )

    # Check for employee-specific rules
    employee_rules = rules.filter(
        models.Q(applies_to_all=False) &
        (models.Q(departments=employee.department) | models.Q(job_titles=employee.job_title))
    ).first()
    
    if employee_rules:
        return employee_rules
    
    # Fall back to general rules
    return rules.filter(applies_to_all=True).first()


@receiver(post_save, sender=AttendanceException)
def apply_attendance_exception(sender, instance, created, **kwargs):
    """Apply approved attendance exceptions to daily attendance"""
    if instance.is_approved and instance.is_applied == False:
        try:
            daily_attendance = DailyAttendance.objects.get(
                employee=instance.employee,
                attendance_date=instance.attendance_date
            )
            
            # Apply adjustments
            if instance.adjusted_check_in:
                daily_attendance.check_in_time = instance.adjusted_check_in
            
            if instance.adjusted_check_out:
                daily_attendance.check_out_time = instance.adjusted_check_out
            
            if instance.adjusted_work_hours:
                daily_attendance.total_work_hours = instance.adjusted_work_hours
            
            # Recalculate metrics
            calculate_daily_attendance_metrics(daily_attendance)
            daily_attendance.save()
            
            # Mark exception as applied
            instance.is_applied = True
            instance.save(update_fields=['is_applied'])
            
        except DailyAttendance.DoesNotExist:
            # Create daily attendance if it doesn't exist
            daily_attendance = DailyAttendance.objects.create(
                employee=instance.employee,
                attendance_date=instance.attendance_date,
                check_in_time=instance.adjusted_check_in,
                check_out_time=instance.adjusted_check_out,
                total_work_hours=instance.adjusted_work_hours or Decimal('0'),
                status='present',
                is_processed=True,
                processed_by=instance.approved_by,
                processed_at=timezone.now()
            )
            
            instance.is_applied = True
            instance.save(update_fields=['is_applied'])


@receiver(post_save, sender=DailyAttendance)
def update_monthly_summary(sender, instance, created, **kwargs):
    """Update monthly attendance summary when daily attendance changes"""
    if instance.is_processed:
        try:
            summary, created_summary = MonthlyAttendanceSummary.objects.get_or_create(
                employee=instance.employee,
                year=instance.attendance_date.year,
                month=instance.attendance_date.month,
                defaults={
                    'total_working_days': 0,
                    'present_days': 0,
                    'absent_days': 0,
                    'late_days': 0,
                    'early_departure_days': 0,
                    'total_work_hours': Decimal('0'),
                    'total_overtime_hours': Decimal('0'),
                    'total_late_minutes': 0,
                    'total_early_departure_minutes': 0,
                    'leave_days': 0,
                    'holiday_days': 0,
                    'weekend_days': 0,
                }
            )
            
            # Recalculate monthly statistics
            calculate_monthly_summary(summary)
            
        except Exception as e:
            # Log error but don't fail the daily attendance save
            pass


def calculate_monthly_summary(summary):
    """Calculate monthly attendance summary statistics"""
    from django.db import models
    
    # Get all daily attendance records for the month
    daily_records = DailyAttendance.objects.filter(
        employee=summary.employee,
        attendance_date__year=summary.year,
        attendance_date__month=summary.month,
        is_processed=True
    )
    
    # Calculate statistics
    summary.total_working_days = daily_records.exclude(
        status__in=['holiday', 'weekend', 'leave']
    ).count()
    
    summary.present_days = daily_records.filter(
        status__in=['present', 'late', 'early_departure']
    ).count()
    
    summary.absent_days = daily_records.filter(status='absent').count()
    summary.late_days = daily_records.filter(status='late').count()
    summary.early_departure_days = daily_records.filter(status='early_departure').count()
    summary.leave_days = daily_records.filter(status='leave').count()
    summary.holiday_days = daily_records.filter(status='holiday').count()
    summary.weekend_days = daily_records.filter(status='weekend').count()
    
    # Calculate time statistics
    aggregates = daily_records.aggregate(
        total_work=models.Sum('total_work_hours'),
        total_overtime=models.Sum('overtime_hours'),
        total_late=models.Sum('late_minutes'),
        total_early=models.Sum('early_departure_minutes')
    )
    
    summary.total_work_hours = aggregates['total_work'] or Decimal('0')
    summary.total_overtime_hours = aggregates['total_overtime'] or Decimal('0')
    summary.total_late_minutes = aggregates['total_late'] or 0
    summary.total_early_departure_minutes = aggregates['total_early'] or 0
    
    # Calculate performance metrics
    summary.calculate_statistics()
    summary.save()
