"""
Attendance System Models
Comprehensive models for ZK device integration, attendance tracking, and analytics
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
import uuid
from datetime import date, time, datetime, timedelta

User = get_user_model()


class AttendanceDevice(models.Model):
    """ZK Fingerprint device configuration"""
    DEVICE_TYPES = [
        ('zk_teco', _('ZKTeco')),
        ('hikvision', _('Hikvision')),
        ('dahua', _('Dahua')),
        ('suprema', _('Suprema')),
        ('other', _('أخرى')),
    ]

    CONNECTION_TYPES = [
        ('tcp', _('TCP/IP')),
        ('udp', _('UDP')),
        ('serial', _('Serial')),
        ('usb', _('USB')),
    ]

    device_id = models.AutoField(primary_key=True, verbose_name=_("معرف الجهاز"))
    device_name = models.CharField(max_length=100, unique=True, verbose_name=_("اسم الجهاز"))
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES, verbose_name=_("نوع الجهاز"))

    # Connection Information
    ip_address = models.GenericIPAddressField(verbose_name=_("عنوان IP"))
    port = models.PositiveIntegerField(default=4370, verbose_name=_("المنفذ"))
    connection_type = models.CharField(max_length=10, choices=CONNECTION_TYPES, default='tcp', verbose_name=_("نوع الاتصال"))

    # Device Configuration
    serial_number = models.CharField(max_length=50, blank=True, verbose_name=_("الرقم التسلسلي"))
    firmware_version = models.CharField(max_length=20, blank=True, verbose_name=_("إصدار البرنامج الثابت"))
    max_users = models.PositiveIntegerField(default=1000, verbose_name=_("الحد الأقصى للمستخدمين"))
    max_records = models.PositiveIntegerField(default=100000, verbose_name=_("الحد الأقصى للسجلات"))

    # Location Information
    location = models.CharField(max_length=100, verbose_name=_("الموقع"))
    department = models.ForeignKey(
        'employee_management.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_devices',
        verbose_name=_("القسم")
    )

    # Sync Configuration
    auto_sync_enabled = models.BooleanField(default=True, verbose_name=_("المزامنة التلقائية مفعلة"))
    sync_interval_minutes = models.PositiveIntegerField(default=15, verbose_name=_("فترة المزامنة (دقائق)"))
    last_sync_time = models.DateTimeField(null=True, blank=True, verbose_name=_("آخر وقت مزامنة"))

    # Status
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    is_online = models.BooleanField(default=False, verbose_name=_("متصل"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("جهاز الحضور")
        verbose_name_plural = _("أجهزة الحضور")
        ordering = ['device_name']
        db_table = 'attendance_system_device'

    def __str__(self):
        return f"{self.device_name} ({self.ip_address})"

    def get_absolute_url(self):
        return reverse('attendance_system:device_detail', kwargs={'pk': self.device_id})


class AttendanceRule(models.Model):
    """Attendance rules and policies"""
    RULE_TYPES = [
        ('work_schedule', _('جدول العمل')),
        ('overtime', _('العمل الإضافي')),
        ('break_time', _('وقت الاستراحة')),
        ('grace_period', _('فترة السماح')),
        ('late_penalty', _('جزاء التأخير')),
    ]

    DAYS_OF_WEEK = [
        ('monday', _('الاثنين')),
        ('tuesday', _('الثلاثاء')),
        ('wednesday', _('الأربعاء')),
        ('thursday', _('الخميس')),
        ('friday', _('الجمعة')),
        ('saturday', _('السبت')),
        ('sunday', _('الأحد')),
    ]

    rule_id = models.AutoField(primary_key=True, verbose_name=_("معرف القاعدة"))
    rule_name = models.CharField(max_length=100, verbose_name=_("اسم القاعدة"))
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES, verbose_name=_("نوع القاعدة"))
    description = models.TextField(blank=True, verbose_name=_("الوصف"))

    # Work Schedule Configuration
    work_start_time = models.TimeField(null=True, blank=True, verbose_name=_("وقت بداية العمل"))
    work_end_time = models.TimeField(null=True, blank=True, verbose_name=_("وقت نهاية العمل"))
    break_start_time = models.TimeField(null=True, blank=True, verbose_name=_("وقت بداية الاستراحة"))
    break_end_time = models.TimeField(null=True, blank=True, verbose_name=_("وقت نهاية الاستراحة"))

    # Grace Period and Penalties
    late_grace_minutes = models.PositiveIntegerField(default=0, verbose_name=_("فترة السماح للتأخير (دقائق)"))
    early_departure_grace_minutes = models.PositiveIntegerField(default=0, verbose_name=_("فترة السماح للانصراف المبكر (دقائق)"))

    # Working Days
    working_days = models.JSONField(default=list, verbose_name=_("أيام العمل"))

    # Overtime Configuration
    overtime_threshold_minutes = models.PositiveIntegerField(default=480, verbose_name=_("حد العمل الإضافي (دقائق)"))
    overtime_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.5, verbose_name=_("مضاعف العمل الإضافي"))

    # Applicability
    applies_to_all = models.BooleanField(default=True, verbose_name=_("تطبق على الجميع"))
    departments = models.ManyToManyField(
        'employee_management.Department',
        blank=True,
        related_name='attendance_rules',
        verbose_name=_("الأقسام المحددة")
    )
    job_titles = models.ManyToManyField(
        'employee_management.JobTitle',
        blank=True,
        related_name='attendance_rules',
        verbose_name=_("الوظائف المحددة")
    )

    # Effective Dates
    effective_from = models.DateField(verbose_name=_("ساري من"))
    effective_to = models.DateField(null=True, blank=True, verbose_name=_("ساري حتى"))

    # Status
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("قاعدة الحضور")
        verbose_name_plural = _("قواعد الحضور")
        ordering = ['rule_name']
        db_table = 'attendance_system_rule'

    def __str__(self):
        return f"{self.rule_name} ({self.get_rule_type_display()})"

    def get_absolute_url(self):
        return reverse('attendance_system:rule_detail', kwargs={'pk': self.rule_id})


class AttendanceRecord(models.Model):
    """Raw attendance records from devices"""
    PUNCH_TYPES = [
        ('check_in', _('دخول')),
        ('check_out', _('خروج')),
        ('break_out', _('خروج استراحة')),
        ('break_in', _('عودة من الاستراحة')),
        ('overtime_in', _('دخول عمل إضافي')),
        ('overtime_out', _('خروج عمل إضافي')),
    ]

    VERIFICATION_METHODS = [
        ('fingerprint', _('بصمة الإصبع')),
        ('face', _('التعرف على الوجه')),
        ('card', _('البطاقة')),
        ('password', _('كلمة المرور')),
        ('manual', _('يدوي')),
    ]

    record_id = models.AutoField(primary_key=True, verbose_name=_("معرف السجل"))
    employee = models.ForeignKey(
        'employee_management.Employee',
        on_delete=models.CASCADE,
        related_name='attendance_records',
        verbose_name=_("الموظف")
    )
    device = models.ForeignKey(
        AttendanceDevice,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        verbose_name=_("الجهاز")
    )

    # Attendance Information
    punch_time = models.DateTimeField(verbose_name=_("وقت التسجيل"))
    punch_type = models.CharField(max_length=15, choices=PUNCH_TYPES, verbose_name=_("نوع التسجيل"))
    verification_method = models.CharField(max_length=15, choices=VERIFICATION_METHODS, verbose_name=_("طريقة التحقق"))

    # Device Information
    device_user_id = models.CharField(max_length=20, verbose_name=_("معرف المستخدم في الجهاز"))
    device_record_id = models.CharField(max_length=50, blank=True, verbose_name=_("معرف السجل في الجهاز"))

    # Processing Status
    is_processed = models.BooleanField(default=False, verbose_name=_("تم المعالجة"))
    is_valid = models.BooleanField(default=True, verbose_name=_("صحيح"))
    error_message = models.TextField(blank=True, verbose_name=_("رسالة الخطأ"))

    # Sync Information
    sync_time = models.DateTimeField(auto_now_add=True, verbose_name=_("وقت المزامنة"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))

    class Meta:
        verbose_name = _("سجل الحضور")
        verbose_name_plural = _("سجلات الحضور")
        ordering = ['-punch_time']
        db_table = 'attendance_system_record'
        indexes = [
            models.Index(fields=['employee', 'punch_time']),
            models.Index(fields=['device', 'punch_time']),
            models.Index(fields=['punch_time', 'punch_type']),
            models.Index(fields=['is_processed', 'is_valid']),
        ]
        unique_together = ['device', 'device_record_id']

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_punch_type_display()} ({self.punch_time})"

    def get_absolute_url(self):
        return reverse('attendance_system:record_detail', kwargs={'pk': self.record_id})


class DailyAttendance(models.Model):
    """Processed daily attendance summary"""
    STATUS_CHOICES = [
        ('present', _('حاضر')),
        ('absent', _('غائب')),
        ('late', _('متأخر')),
        ('early_departure', _('انصراف مبكر')),
        ('incomplete', _('غير مكتمل')),
        ('holiday', _('عطلة')),
        ('leave', _('إجازة')),
        ('weekend', _('عطلة نهاية الأسبوع')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        'employee_management.Employee',
        on_delete=models.CASCADE,
        related_name='daily_attendance',
        verbose_name=_("الموظف")
    )
    attendance_date = models.DateField(verbose_name=_("تاريخ الحضور"))

    # Attendance Times
    check_in_time = models.TimeField(null=True, blank=True, verbose_name=_("وقت الدخول"))
    check_out_time = models.TimeField(null=True, blank=True, verbose_name=_("وقت الخروج"))
    break_out_time = models.TimeField(null=True, blank=True, verbose_name=_("وقت خروج الاستراحة"))
    break_in_time = models.TimeField(null=True, blank=True, verbose_name=_("وقت عودة الاستراحة"))

    # Calculated Times
    total_work_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0,
        verbose_name=_("إجمالي ساعات العمل")
    )
    break_duration_minutes = models.PositiveIntegerField(default=0, verbose_name=_("مدة الاستراحة (دقائق)"))
    overtime_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0,
        verbose_name=_("ساعات العمل الإضافي")
    )

    # Late and Early Departure
    late_minutes = models.PositiveIntegerField(default=0, verbose_name=_("دقائق التأخير"))
    early_departure_minutes = models.PositiveIntegerField(default=0, verbose_name=_("دقائق الانصراف المبكر"))

    # Status and Flags
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name=_("الحالة"))
    is_holiday = models.BooleanField(default=False, verbose_name=_("عطلة"))
    is_weekend = models.BooleanField(default=False, verbose_name=_("عطلة نهاية الأسبوع"))
    is_on_leave = models.BooleanField(default=False, verbose_name=_("في إجازة"))

    # Applied Rules
    attendance_rule = models.ForeignKey(
        AttendanceRule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_attendance',
        verbose_name=_("قاعدة الحضور المطبقة")
    )

    # Comments and Notes
    comments = models.TextField(blank=True, verbose_name=_("التعليقات"))

    # Processing Information
    is_processed = models.BooleanField(default=False, verbose_name=_("تم المعالجة"))
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("وقت المعالجة"))
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_attendance',
        verbose_name=_("معالج بواسطة")
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("الحضور اليومي")
        verbose_name_plural = _("الحضور اليومي")
        ordering = ['-attendance_date', 'employee']
        db_table = 'attendance_system_daily_attendance'
        unique_together = ['employee', 'attendance_date']
        indexes = [
            models.Index(fields=['employee', 'attendance_date']),
            models.Index(fields=['attendance_date', 'status']),
            models.Index(fields=['is_processed', 'attendance_date']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.attendance_date} ({self.get_status_display()})"

    def get_absolute_url(self):
        return reverse('attendance_system:daily_attendance_detail', kwargs={'pk': self.id})

    @property
    def effective_work_hours(self):
        """Calculate effective work hours excluding break time"""
        if self.total_work_hours and self.break_duration_minutes:
            break_hours = Decimal(self.break_duration_minutes) / Decimal(60)
            return max(Decimal(0), self.total_work_hours - break_hours)
        return self.total_work_hours

    @property
    def is_late(self):
        """Check if employee was late"""
        return self.late_minutes > 0

    @property
    def is_early_departure(self):
        """Check if employee left early"""
        return self.early_departure_minutes > 0


class AttendanceException(models.Model):
    """Attendance exceptions and manual adjustments"""
    EXCEPTION_TYPES = [
        ('manual_adjustment', _('تعديل يدوي')),
        ('missing_punch', _('تسجيل مفقود')),
        ('system_error', _('خطأ في النظام')),
        ('device_malfunction', _('عطل في الجهاز')),
        ('approved_overtime', _('عمل إضافي معتمد')),
        ('field_work', _('عمل ميداني')),
        ('training', _('تدريب')),
        ('meeting', _('اجتماع')),
        ('other', _('أخرى')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        'employee_management.Employee',
        on_delete=models.CASCADE,
        related_name='attendance_exceptions',
        verbose_name=_("الموظف")
    )
    attendance_date = models.DateField(verbose_name=_("تاريخ الحضور"))

    # Exception Details
    exception_type = models.CharField(max_length=20, choices=EXCEPTION_TYPES, verbose_name=_("نوع الاستثناء"))
    description = models.TextField(verbose_name=_("الوصف"))

    # Time Adjustments
    adjusted_check_in = models.TimeField(null=True, blank=True, verbose_name=_("وقت الدخول المعدل"))
    adjusted_check_out = models.TimeField(null=True, blank=True, verbose_name=_("وقت الخروج المعدل"))
    adjusted_work_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("ساعات العمل المعدلة")
    )

    # Approval Information
    requested_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='requested_attendance_exceptions',
        verbose_name=_("طلب بواسطة")
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_attendance_exceptions',
        verbose_name=_("اعتمد بواسطة")
    )
    approval_date = models.DateTimeField(null=True, blank=True, verbose_name=_("تاريخ الاعتماد"))

    # Supporting Documents
    supporting_document = models.FileField(
        upload_to='attendance_exceptions/',
        null=True,
        blank=True,
        verbose_name=_("المستند المؤيد")
    )

    # Status
    is_approved = models.BooleanField(default=False, verbose_name=_("معتمد"))
    is_applied = models.BooleanField(default=False, verbose_name=_("مطبق"))

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("استثناء الحضور")
        verbose_name_plural = _("استثناءات الحضور")
        ordering = ['-attendance_date', '-created_at']
        db_table = 'attendance_system_exception'
        indexes = [
            models.Index(fields=['employee', 'attendance_date']),
            models.Index(fields=['exception_type', 'is_approved']),
            models.Index(fields=['requested_by', 'created_at']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_exception_type_display()} ({self.attendance_date})"

    def get_absolute_url(self):
        return reverse('attendance_system:exception_detail', kwargs={'pk': self.id})


class MonthlyAttendanceSummary(models.Model):
    """Monthly attendance summary for employees"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        'employee_management.Employee',
        on_delete=models.CASCADE,
        related_name='monthly_attendance_summaries',
        verbose_name=_("الموظف")
    )
    year = models.PositiveIntegerField(verbose_name=_("السنة"))
    month = models.PositiveIntegerField(verbose_name=_("الشهر"))

    # Attendance Statistics
    total_working_days = models.PositiveIntegerField(default=0, verbose_name=_("إجمالي أيام العمل"))
    present_days = models.PositiveIntegerField(default=0, verbose_name=_("أيام الحضور"))
    absent_days = models.PositiveIntegerField(default=0, verbose_name=_("أيام الغياب"))
    late_days = models.PositiveIntegerField(default=0, verbose_name=_("أيام التأخير"))
    early_departure_days = models.PositiveIntegerField(default=0, verbose_name=_("أيام الانصراف المبكر"))

    # Time Statistics
    total_work_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name=_("إجمالي ساعات العمل")
    )
    total_overtime_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name=_("إجمالي ساعات العمل الإضافي")
    )
    total_late_minutes = models.PositiveIntegerField(default=0, verbose_name=_("إجمالي دقائق التأخير"))
    total_early_departure_minutes = models.PositiveIntegerField(default=0, verbose_name=_("إجمالي دقائق الانصراف المبكر"))

    # Leave and Holiday Statistics
    leave_days = models.PositiveIntegerField(default=0, verbose_name=_("أيام الإجازة"))
    holiday_days = models.PositiveIntegerField(default=0, verbose_name=_("أيام العطل"))
    weekend_days = models.PositiveIntegerField(default=0, verbose_name=_("أيام عطلة نهاية الأسبوع"))

    # Performance Metrics
    attendance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("نسبة الحضور")
    )
    punctuality_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("نسبة الالتزام بالمواعيد")
    )

    # Processing Information
    is_finalized = models.BooleanField(default=False, verbose_name=_("مؤكد"))
    finalized_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='finalized_monthly_summaries',
        verbose_name=_("أكد بواسطة")
    )
    finalized_at = models.DateTimeField(null=True, blank=True, verbose_name=_("تاريخ التأكيد"))

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("ملخص الحضور الشهري")
        verbose_name_plural = _("ملخصات الحضور الشهرية")
        ordering = ['-year', '-month', 'employee']
        db_table = 'attendance_system_monthly_summary'
        unique_together = ['employee', 'year', 'month']
        indexes = [
            models.Index(fields=['employee', 'year', 'month']),
            models.Index(fields=['year', 'month']),
            models.Index(fields=['is_finalized']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.year}/{self.month:02d}"

    def get_absolute_url(self):
        return reverse('attendance_system:monthly_summary_detail', kwargs={'pk': self.id})

    @property
    def month_name(self):
        """Get month name in Arabic"""
        months = {
            1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
            5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
            9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
        }
        return months.get(self.month, str(self.month))

    def calculate_statistics(self):
        """Calculate attendance statistics"""
        if self.total_working_days > 0:
            self.attendance_percentage = (Decimal(self.present_days) / Decimal(self.total_working_days)) * 100

        if self.present_days > 0:
            punctual_days = self.present_days - self.late_days
            self.punctuality_percentage = (Decimal(punctual_days) / Decimal(self.present_days)) * 100
