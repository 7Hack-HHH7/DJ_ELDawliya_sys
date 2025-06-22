"""
Leave Management Models
Comprehensive models for leave types, requests, approvals, and balance tracking
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
import uuid
from datetime import date, timedelta

User = get_user_model()


class LeaveType(models.Model):
    """Leave type configuration model"""
    CALCULATION_METHODS = [
        ('fixed', _('ثابت')),
        ('monthly', _('شهري')),
        ('yearly', _('سنوي')),
        ('service_based', _('حسب سنوات الخدمة')),
    ]

    GENDER_RESTRICTIONS = [
        ('all', _('الجميع')),
        ('male', _('ذكور فقط')),
        ('female', _('إناث فقط')),
    ]

    leave_type_code = models.AutoField(primary_key=True, verbose_name=_("رمز نوع الإجازة"))
    leave_type_name = models.CharField(max_length=100, unique=True, verbose_name=_("اسم نوع الإجازة"))
    leave_type_name_en = models.CharField(max_length=100, blank=True, verbose_name=_("اسم نوع الإجازة بالإنجليزية"))
    description = models.TextField(blank=True, verbose_name=_("الوصف"))

    # Leave Configuration
    is_paid = models.BooleanField(default=True, verbose_name=_("مدفوعة الأجر"))
    requires_approval = models.BooleanField(default=True, verbose_name=_("تتطلب موافقة"))
    requires_medical_certificate = models.BooleanField(default=False, verbose_name=_("تتطلب شهادة طبية"))

    # Balance Configuration
    calculation_method = models.CharField(
        max_length=15,
        choices=CALCULATION_METHODS,
        default='yearly',
        verbose_name=_("طريقة الحساب")
    )
    default_balance = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("الرصيد الافتراضي")
    )
    max_balance = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الحد الأقصى للرصيد")
    )

    # Request Limits
    min_days_per_request = models.PositiveIntegerField(default=1, verbose_name=_("الحد الأدنى للأيام في الطلب"))
    max_days_per_request = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("الحد الأقصى للأيام في الطلب"))
    max_requests_per_year = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("الحد الأقصى للطلبات في السنة"))

    # Advance Notice
    min_advance_notice_days = models.PositiveIntegerField(default=1, verbose_name=_("الحد الأدنى للإشعار المسبق (أيام)"))

    # Restrictions
    gender_restriction = models.CharField(
        max_length=10,
        choices=GENDER_RESTRICTIONS,
        default='all',
        verbose_name=_("قيود الجنس")
    )
    exclude_weekends = models.BooleanField(default=True, verbose_name=_("استبعاد عطل نهاية الأسبوع"))
    exclude_holidays = models.BooleanField(default=True, verbose_name=_("استبعاد العطل الرسمية"))

    # Carryover Settings
    allow_carryover = models.BooleanField(default=False, verbose_name=_("السماح بالترحيل"))
    max_carryover_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الحد الأقصى لأيام الترحيل")
    )
    carryover_expiry_months = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("انتهاء صلاحية الترحيل (شهور)")
    )

    # Status
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("نوع إجازة")
        verbose_name_plural = _("أنواع الإجازات")
        ordering = ['leave_type_name']
        db_table = 'leave_management_leave_type'

    def __str__(self):
        return self.leave_type_name

    def get_absolute_url(self):
        return reverse('leave_management:leave_type_detail', kwargs={'pk': self.leave_type_code})


class LeaveBalance(models.Model):
    """Employee leave balance tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        'employee_management.Employee',
        on_delete=models.CASCADE,
        related_name='leave_balances',
        verbose_name=_("الموظف")
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        related_name='employee_balances',
        verbose_name=_("نوع الإجازة")
    )

    # Balance Information
    year = models.PositiveIntegerField(verbose_name=_("السنة"))
    allocated_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("الأيام المخصصة")
    )
    used_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("الأيام المستخدمة")
    )
    pending_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("الأيام المعلقة")
    )
    carried_over_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("الأيام المرحلة")
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("رصيد إجازة")
        verbose_name_plural = _("أرصدة الإجازات")
        unique_together = ['employee', 'leave_type', 'year']
        ordering = ['-year', 'employee', 'leave_type']
        db_table = 'leave_management_leave_balance'
        indexes = [
            models.Index(fields=['employee', 'year']),
            models.Index(fields=['leave_type', 'year']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.leave_type_name} ({self.year})"

    @property
    def available_days(self):
        """Calculate available leave days"""
        return self.allocated_days + self.carried_over_days - self.used_days - self.pending_days

    @property
    def total_allocated(self):
        """Total allocated days including carryover"""
        return self.allocated_days + self.carried_over_days


class LeaveRequest(models.Model):
    """Leave request model"""
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('submitted', _('مقدم')),
        ('approved', _('موافق عليه')),
        ('rejected', _('مرفوض')),
        ('cancelled', _('ملغي')),
        ('in_progress', _('قيد التنفيذ')),
        ('completed', _('مكتمل')),
    ]

    PRIORITY_LEVELS = [
        ('low', _('منخفض')),
        ('normal', _('عادي')),
        ('high', _('عالي')),
        ('urgent', _('عاجل')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_number = models.CharField(max_length=20, unique=True, verbose_name=_("رقم الطلب"))

    # Employee and Leave Information
    employee = models.ForeignKey(
        'employee_management.Employee',
        on_delete=models.CASCADE,
        related_name='leave_requests',
        verbose_name=_("الموظف")
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.PROTECT,
        related_name='leave_requests',
        verbose_name=_("نوع الإجازة")
    )

    # Leave Dates
    start_date = models.DateField(verbose_name=_("تاريخ البداية"))
    end_date = models.DateField(verbose_name=_("تاريخ النهاية"))
    return_date = models.DateField(null=True, blank=True, verbose_name=_("تاريخ العودة المتوقع"))
    actual_return_date = models.DateField(null=True, blank=True, verbose_name=_("تاريخ العودة الفعلي"))

    # Duration
    requested_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("عدد الأيام المطلوبة")
    )
    approved_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("عدد الأيام الموافق عليها")
    )

    # Request Details
    reason = models.TextField(verbose_name=_("سبب الإجازة"))
    emergency_contact = models.CharField(max_length=100, blank=True, verbose_name=_("جهة الاتصال في حالة الطوارئ"))
    emergency_phone = models.CharField(max_length=15, blank=True, verbose_name=_("هاتف الطوارئ"))

    # Status and Priority
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name=_("الحالة")
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_LEVELS,
        default='normal',
        verbose_name=_("الأولوية")
    )

    # Approval Information
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='submitted_leave_requests',
        verbose_name=_("قدم بواسطة")
    )
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("تاريخ التقديم"))

    # Medical Certificate
    medical_certificate = models.FileField(
        upload_to='leave_medical_certificates/',
        null=True,
        blank=True,
        verbose_name=_("الشهادة الطبية")
    )

    # Comments and Notes
    employee_comments = models.TextField(blank=True, verbose_name=_("تعليقات الموظف"))
    admin_comments = models.TextField(blank=True, verbose_name=_("تعليقات الإدارة"))

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("طلب إجازة")
        verbose_name_plural = _("طلبات الإجازات")
        ordering = ['-created_at']
        db_table = 'leave_management_leave_request'
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['leave_type', 'status']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['status', 'submitted_at']),
        ]

    def __str__(self):
        return f"{self.request_number} - {self.employee.full_name} ({self.leave_type.leave_type_name})"

    def get_absolute_url(self):
        return reverse('leave_management:leave_request_detail', kwargs={'pk': self.id})

    def save(self, *args, **kwargs):
        if not self.request_number:
            # Generate unique request number
            year = timezone.now().year
            last_request = LeaveRequest.objects.filter(
                request_number__startswith=f'LR{year}'
            ).order_by('-request_number').first()

            if last_request:
                last_number = int(last_request.request_number[-4:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.request_number = f'LR{year}{new_number:04d}'

        super().save(*args, **kwargs)

    @property
    def duration_in_days(self):
        """Calculate actual duration in days"""
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            return delta.days + 1
        return 0

    @property
    def is_overdue(self):
        """Check if employee is overdue to return"""
        if self.status == 'in_progress' and self.return_date:
            return date.today() > self.return_date
        return False

    @property
    def can_be_cancelled(self):
        """Check if request can be cancelled"""
        return self.status in ['draft', 'submitted']

    @property
    def can_be_approved(self):
        """Check if request can be approved"""
        return self.status == 'submitted'


class LeaveApproval(models.Model):
    """Leave approval workflow model"""
    APPROVAL_ACTIONS = [
        ('approve', _('موافقة')),
        ('reject', _('رفض')),
        ('request_info', _('طلب معلومات إضافية')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    leave_request = models.ForeignKey(
        LeaveRequest,
        on_delete=models.CASCADE,
        related_name='approvals',
        verbose_name=_("طلب الإجازة")
    )

    # Approver Information
    approver = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='leave_approvals',
        verbose_name=_("المعتمد")
    )
    approval_level = models.PositiveIntegerField(default=1, verbose_name=_("مستوى الاعتماد"))

    # Approval Details
    action = models.CharField(
        max_length=15,
        choices=APPROVAL_ACTIONS,
        verbose_name=_("الإجراء")
    )
    comments = models.TextField(blank=True, verbose_name=_("التعليقات"))
    approved_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الأيام الموافق عليها")
    )

    # Timestamps
    action_date = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإجراء"))

    class Meta:
        verbose_name = _("اعتماد إجازة")
        verbose_name_plural = _("اعتمادات الإجازات")
        ordering = ['-action_date']
        db_table = 'leave_management_leave_approval'
        indexes = [
            models.Index(fields=['leave_request', 'approval_level']),
            models.Index(fields=['approver', 'action_date']),
        ]

    def __str__(self):
        return f"{self.leave_request.request_number} - {self.get_action_display()} by {self.approver.get_full_name()}"


class Holiday(models.Model):
    """Public holidays and company holidays"""
    HOLIDAY_TYPES = [
        ('public', _('عطلة رسمية')),
        ('company', _('عطلة الشركة')),
        ('religious', _('عطلة دينية')),
        ('national', _('عطلة وطنية')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name=_("اسم العطلة"))
    name_en = models.CharField(max_length=100, blank=True, verbose_name=_("اسم العطلة بالإنجليزية"))
    description = models.TextField(blank=True, verbose_name=_("الوصف"))

    # Date Information
    date = models.DateField(verbose_name=_("التاريخ"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("تاريخ النهاية"))

    # Holiday Configuration
    holiday_type = models.CharField(
        max_length=15,
        choices=HOLIDAY_TYPES,
        verbose_name=_("نوع العطلة")
    )
    is_recurring = models.BooleanField(default=False, verbose_name=_("متكررة سنوياً"))
    affects_leave_calculation = models.BooleanField(default=True, verbose_name=_("تؤثر على حساب الإجازات"))

    # Applicability
    applies_to_all = models.BooleanField(default=True, verbose_name=_("تطبق على الجميع"))
    departments = models.ManyToManyField(
        'employee_management.Department',
        blank=True,
        related_name='holidays',
        verbose_name=_("الأقسام المحددة")
    )

    # Status
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("عطلة")
        verbose_name_plural = _("العطل")
        ordering = ['date']
        db_table = 'leave_management_holiday'
        indexes = [
            models.Index(fields=['date', 'is_active']),
            models.Index(fields=['holiday_type', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.date})"

    def get_absolute_url(self):
        return reverse('leave_management:holiday_detail', kwargs={'pk': self.id})

    @property
    def duration_days(self):
        """Calculate holiday duration in days"""
        if self.end_date:
            return (self.end_date - self.date).days + 1
        return 1


class LeavePolicy(models.Model):
    """Leave policies and rules"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name=_("اسم السياسة"))
    description = models.TextField(verbose_name=_("الوصف"))

    # Policy Rules
    policy_document = models.FileField(
        upload_to='leave_policies/',
        null=True,
        blank=True,
        verbose_name=_("وثيقة السياسة")
    )

    # Applicability
    applies_to_all = models.BooleanField(default=True, verbose_name=_("تطبق على الجميع"))
    departments = models.ManyToManyField(
        'employee_management.Department',
        blank=True,
        related_name='leave_policies',
        verbose_name=_("الأقسام المحددة")
    )
    job_titles = models.ManyToManyField(
        'employee_management.JobTitle',
        blank=True,
        related_name='leave_policies',
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
        verbose_name = _("سياسة إجازة")
        verbose_name_plural = _("سياسات الإجازات")
        ordering = ['-effective_from']
        db_table = 'leave_management_leave_policy'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('leave_management:leave_policy_detail', kwargs={'pk': self.id})
