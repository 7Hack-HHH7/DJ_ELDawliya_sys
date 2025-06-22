"""
Payroll Management Models
Comprehensive models for payroll processing, salary calculations, and voucher management
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


class SalaryComponent(models.Model):
    """Salary components (allowances, deductions, etc.)"""
    COMPONENT_TYPES = [
        ('basic_salary', _('الراتب الأساسي')),
        ('allowance', _('بدل')),
        ('bonus', _('مكافأة')),
        ('overtime', _('عمل إضافي')),
        ('commission', _('عمولة')),
        ('deduction', _('خصم')),
        ('tax', _('ضريبة')),
        ('insurance', _('تأمين')),
        ('loan_deduction', _('خصم قرض')),
        ('advance_deduction', _('خصم سلفة')),
    ]

    CALCULATION_METHODS = [
        ('fixed', _('مبلغ ثابت')),
        ('percentage', _('نسبة مئوية')),
        ('hourly', _('بالساعة')),
        ('daily', _('يومي')),
        ('formula', _('معادلة')),
    ]

    component_id = models.AutoField(primary_key=True, verbose_name=_("معرف المكون"))
    component_name = models.CharField(max_length=100, unique=True, verbose_name=_("اسم المكون"))
    component_name_en = models.CharField(max_length=100, blank=True, verbose_name=_("اسم المكون بالإنجليزية"))
    component_type = models.CharField(max_length=20, choices=COMPONENT_TYPES, verbose_name=_("نوع المكون"))
    description = models.TextField(blank=True, verbose_name=_("الوصف"))

    # Calculation Configuration
    calculation_method = models.CharField(max_length=15, choices=CALCULATION_METHODS, verbose_name=_("طريقة الحساب"))
    default_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("المبلغ الافتراضي")
    )
    percentage_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("معدل النسبة المئوية")
    )
    calculation_formula = models.TextField(blank=True, verbose_name=_("معادلة الحساب"))

    # Tax Configuration
    is_taxable = models.BooleanField(default=True, verbose_name=_("خاضع للضريبة"))
    is_insurance_applicable = models.BooleanField(default=True, verbose_name=_("خاضع للتأمين"))

    # Display Configuration
    display_order = models.PositiveIntegerField(default=0, verbose_name=_("ترتيب العرض"))
    is_mandatory = models.BooleanField(default=False, verbose_name=_("إجباري"))

    # Status
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("مكون الراتب")
        verbose_name_plural = _("مكونات الراتب")
        ordering = ['display_order', 'component_name']
        db_table = 'payroll_management_salary_component'

    def __str__(self):
        return f"{self.component_name} ({self.get_component_type_display()})"

    def get_absolute_url(self):
        return reverse('payroll_management:component_detail', kwargs={'pk': self.component_id})


class EmployeeSalaryStructure(models.Model):
    """Employee-specific salary structure"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        'employee_management.Employee',
        on_delete=models.CASCADE,
        related_name='salary_structures',
        verbose_name=_("الموظف")
    )

    # Salary Information
    basic_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("الراتب الأساسي")
    )
    currency = models.CharField(max_length=3, default='SAR', verbose_name=_("العملة"))

    # Effective Dates
    effective_from = models.DateField(verbose_name=_("ساري من"))
    effective_to = models.DateField(null=True, blank=True, verbose_name=_("ساري حتى"))

    # Bank Information
    bank_name = models.CharField(max_length=100, blank=True, verbose_name=_("اسم البنك"))
    bank_account_number = models.CharField(max_length=50, blank=True, verbose_name=_("رقم الحساب البنكي"))
    iban = models.CharField(max_length=34, blank=True, verbose_name=_("رقم الآيبان"))

    # Status
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_salary_structures',
        verbose_name=_("أنشئ بواسطة")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("هيكل راتب الموظف")
        verbose_name_plural = _("هياكل رواتب الموظفين")
        ordering = ['-effective_from']
        db_table = 'payroll_management_employee_salary_structure'
        indexes = [
            models.Index(fields=['employee', 'effective_from']),
            models.Index(fields=['is_active', 'effective_from']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.basic_salary} ({self.effective_from})"

    def get_absolute_url(self):
        return reverse('payroll_management:salary_structure_detail', kwargs={'pk': self.id})


class EmployeeSalaryComponent(models.Model):
    """Employee-specific salary component values"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    salary_structure = models.ForeignKey(
        EmployeeSalaryStructure,
        on_delete=models.CASCADE,
        related_name='salary_components',
        verbose_name=_("هيكل الراتب")
    )
    component = models.ForeignKey(
        SalaryComponent,
        on_delete=models.CASCADE,
        related_name='employee_components',
        verbose_name=_("مكون الراتب")
    )

    # Component Value
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("المبلغ")
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("النسبة المئوية")
    )

    # Configuration
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    notes = models.TextField(blank=True, verbose_name=_("ملاحظات"))

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("مكون راتب الموظف")
        verbose_name_plural = _("مكونات راتب الموظف")
        unique_together = ['salary_structure', 'component']
        db_table = 'payroll_management_employee_salary_component'

    def __str__(self):
        return f"{self.salary_structure.employee.full_name} - {self.component.component_name}"


class PayrollPeriod(models.Model):
    """Payroll processing periods"""
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('in_progress', _('قيد المعالجة')),
        ('calculated', _('محسوب')),
        ('approved', _('معتمد')),
        ('paid', _('مدفوع')),
        ('closed', _('مغلق')),
    ]

    period_id = models.AutoField(primary_key=True, verbose_name=_("معرف الفترة"))
    period_name = models.CharField(max_length=100, verbose_name=_("اسم الفترة"))

    # Period Dates
    start_date = models.DateField(verbose_name=_("تاريخ البداية"))
    end_date = models.DateField(verbose_name=_("تاريخ النهاية"))
    pay_date = models.DateField(verbose_name=_("تاريخ الدفع"))

    # Processing Information
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft', verbose_name=_("الحالة"))
    total_employees = models.PositiveIntegerField(default=0, verbose_name=_("إجمالي الموظفين"))
    processed_employees = models.PositiveIntegerField(default=0, verbose_name=_("الموظفين المعالجين"))

    # Financial Summary
    total_gross_salary = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name=_("إجمالي الراتب الإجمالي")
    )
    total_deductions = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name=_("إجمالي الخصومات")
    )
    total_net_salary = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name=_("إجمالي الراتب الصافي")
    )

    # Processing Information
    calculated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calculated_payroll_periods',
        verbose_name=_("حسب بواسطة")
    )
    calculated_at = models.DateTimeField(null=True, blank=True, verbose_name=_("تاريخ الحساب"))

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_payroll_periods',
        verbose_name=_("اعتمد بواسطة")
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("تاريخ الاعتماد"))

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("فترة الراتب")
        verbose_name_plural = _("فترات الراتب")
        ordering = ['-start_date']
        db_table = 'payroll_management_payroll_period'
        indexes = [
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['status', 'pay_date']),
        ]

    def __str__(self):
        return f"{self.period_name} ({self.start_date} - {self.end_date})"

    def get_absolute_url(self):
        return reverse('payroll_management:period_detail', kwargs={'pk': self.period_id})

    @property
    def processing_progress(self):
        """Calculate processing progress percentage"""
        if self.total_employees > 0:
            return (self.processed_employees / self.total_employees) * 100
        return 0

    @property
    def is_editable(self):
        """Check if period can be edited"""
        return self.status in ['draft', 'in_progress']


class PayrollTransaction(models.Model):
    """Manual payroll transactions (bonuses, deductions, etc.)"""
    TRANSACTION_TYPES = [
        ('bonus', _('مكافأة')),
        ('allowance', _('بدل')),
        ('overtime', _('عمل إضافي')),
        ('deduction', _('خصم')),
        ('advance', _('سلفة')),
        ('loan_payment', _('دفعة قرض')),
        ('penalty', _('جزاء')),
        ('adjustment', _('تعديل')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        'employee_management.Employee',
        on_delete=models.CASCADE,
        related_name='payroll_transactions',
        verbose_name=_("الموظف")
    )
    payroll_period = models.ForeignKey(
        PayrollPeriod,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name=_("فترة الراتب")
    )

    # Transaction Details
    transaction_type = models.CharField(max_length=15, choices=TRANSACTION_TYPES, verbose_name=_("نوع المعاملة"))
    description = models.CharField(max_length=200, verbose_name=_("الوصف"))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("المبلغ"))

    # Reference Information
    reference_number = models.CharField(max_length=50, blank=True, verbose_name=_("رقم المرجع"))
    reference_date = models.DateField(null=True, blank=True, verbose_name=_("تاريخ المرجع"))

    # Approval Information
    is_approved = models.BooleanField(default=False, verbose_name=_("معتمد"))
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_payroll_transactions',
        verbose_name=_("اعتمد بواسطة")
    )
    approval_date = models.DateTimeField(null=True, blank=True, verbose_name=_("تاريخ الاعتماد"))

    # Processing Information
    is_processed = models.BooleanField(default=False, verbose_name=_("معالج"))
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_payroll_transactions',
        verbose_name=_("أنشئ بواسطة")
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("معاملة الراتب")
        verbose_name_plural = _("معاملات الراتب")
        ordering = ['-created_at']
        db_table = 'payroll_management_payroll_transaction'
        indexes = [
            models.Index(fields=['employee', 'payroll_period']),
            models.Index(fields=['transaction_type', 'is_approved']),
            models.Index(fields=['is_processed', 'payroll_period']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_transaction_type_display()} ({self.amount})"

    def get_absolute_url(self):
        return reverse('payroll_management:transaction_detail', kwargs={'pk': self.id})


class EmployeePayslip(models.Model):
    """Employee payslip for each payroll period"""
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('calculated', _('محسوب')),
        ('approved', _('معتمد')),
        ('paid', _('مدفوع')),
        ('cancelled', _('ملغي')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payslip_number = models.CharField(max_length=20, unique=True, verbose_name=_("رقم قسيمة الراتب"))

    # Employee and Period Information
    employee = models.ForeignKey(
        'employee_management.Employee',
        on_delete=models.CASCADE,
        related_name='payslips',
        verbose_name=_("الموظف")
    )
    payroll_period = models.ForeignKey(
        PayrollPeriod,
        on_delete=models.CASCADE,
        related_name='payslips',
        verbose_name=_("فترة الراتب")
    )
    salary_structure = models.ForeignKey(
        EmployeeSalaryStructure,
        on_delete=models.PROTECT,
        related_name='payslips',
        verbose_name=_("هيكل الراتب")
    )

    # Attendance Information
    working_days = models.PositiveIntegerField(default=0, verbose_name=_("أيام العمل"))
    present_days = models.PositiveIntegerField(default=0, verbose_name=_("أيام الحضور"))
    absent_days = models.PositiveIntegerField(default=0, verbose_name=_("أيام الغياب"))
    leave_days = models.PositiveIntegerField(default=0, verbose_name=_("أيام الإجازة"))
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name=_("ساعات العمل الإضافي"))

    # Salary Calculations
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("الراتب الأساسي"))
    total_allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("إجمالي البدلات"))
    total_bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("إجمالي المكافآت"))
    overtime_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("مبلغ العمل الإضافي"))
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("الراتب الإجمالي"))

    # Deductions
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("إجمالي الخصومات"))
    tax_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("خصم الضريبة"))
    insurance_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("خصم التأمين"))
    loan_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("خصم القرض"))
    advance_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("خصم السلفة"))
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("خصومات أخرى"))

    # Net Salary
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("الراتب الصافي"))

    # Status and Processing
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft', verbose_name=_("الحالة"))
    calculation_date = models.DateTimeField(null=True, blank=True, verbose_name=_("تاريخ الحساب"))
    payment_date = models.DateTimeField(null=True, blank=True, verbose_name=_("تاريخ الدفع"))

    # Comments and Notes
    comments = models.TextField(blank=True, verbose_name=_("التعليقات"))

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("قسيمة راتب")
        verbose_name_plural = _("قسائم الرواتب")
        ordering = ['-payroll_period__start_date', 'employee']
        db_table = 'payroll_management_employee_payslip'
        unique_together = ['employee', 'payroll_period']
        indexes = [
            models.Index(fields=['employee', 'payroll_period']),
            models.Index(fields=['status', 'payroll_period']),
            models.Index(fields=['payslip_number']),
        ]

    def __str__(self):
        return f"{self.payslip_number} - {self.employee.full_name} ({self.payroll_period.period_name})"

    def get_absolute_url(self):
        return reverse('payroll_management:payslip_detail', kwargs={'pk': self.id})

    def save(self, *args, **kwargs):
        if not self.payslip_number:
            # Generate unique payslip number
            year = self.payroll_period.start_date.year
            month = self.payroll_period.start_date.month
            last_payslip = EmployeePayslip.objects.filter(
                payslip_number__startswith=f'PS{year}{month:02d}'
            ).order_by('-payslip_number').first()

            if last_payslip:
                last_number = int(last_payslip.payslip_number[-4:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.payslip_number = f'PS{year}{month:02d}{new_number:04d}'

        super().save(*args, **kwargs)

    @property
    def attendance_percentage(self):
        """Calculate attendance percentage"""
        if self.working_days > 0:
            return (self.present_days / self.working_days) * 100
        return 0


class PayslipComponent(models.Model):
    """Individual components in a payslip"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payslip = models.ForeignKey(
        EmployeePayslip,
        on_delete=models.CASCADE,
        related_name='payslip_components',
        verbose_name=_("قسيمة الراتب")
    )
    component = models.ForeignKey(
        SalaryComponent,
        on_delete=models.CASCADE,
        related_name='payslip_components',
        verbose_name=_("مكون الراتب")
    )

    # Component Values
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("المبلغ"))
    calculation_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("أساس الحساب")
    )
    rate_or_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("المعدل أو النسبة")
    )

    # Calculation Details
    calculation_notes = models.TextField(blank=True, verbose_name=_("ملاحظات الحساب"))

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))

    class Meta:
        verbose_name = _("مكون قسيمة الراتب")
        verbose_name_plural = _("مكونات قسيمة الراتب")
        unique_together = ['payslip', 'component']
        ordering = ['component__display_order', 'component__component_name']
        db_table = 'payroll_management_payslip_component'

    def __str__(self):
        return f"{self.payslip.payslip_number} - {self.component.component_name} ({self.amount})"


class TaxConfiguration(models.Model):
    """Tax configuration and brackets"""
    CALCULATION_METHODS = [
        ('flat_rate', _('معدل ثابت')),
        ('progressive', _('تدريجي')),
        ('bracket', _('شرائح')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tax_name = models.CharField(max_length=100, verbose_name=_("اسم الضريبة"))
    description = models.TextField(blank=True, verbose_name=_("الوصف"))

    # Tax Configuration
    calculation_method = models.CharField(max_length=15, choices=CALCULATION_METHODS, verbose_name=_("طريقة الحساب"))
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_("معدل الضريبة"))
    minimum_taxable_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("الحد الأدنى للمبلغ الخاضع للضريبة")
    )
    maximum_taxable_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الحد الأقصى للمبلغ الخاضع للضريبة")
    )

    # Effective Dates
    effective_from = models.DateField(verbose_name=_("ساري من"))
    effective_to = models.DateField(null=True, blank=True, verbose_name=_("ساري حتى"))

    # Status
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("إعداد الضريبة")
        verbose_name_plural = _("إعدادات الضرائب")
        ordering = ['-effective_from']
        db_table = 'payroll_management_tax_configuration'

    def __str__(self):
        return f"{self.tax_name} ({self.tax_rate}%)"

    def get_absolute_url(self):
        return reverse('payroll_management:tax_config_detail', kwargs={'pk': self.id})


class PayrollReport(models.Model):
    """Payroll reports and analytics"""
    REPORT_TYPES = [
        ('payroll_summary', _('ملخص الرواتب')),
        ('department_summary', _('ملخص الأقسام')),
        ('tax_report', _('تقرير الضرائب')),
        ('insurance_report', _('تقرير التأمين')),
        ('overtime_report', _('تقرير العمل الإضافي')),
        ('deductions_report', _('تقرير الخصومات')),
        ('bank_transfer', _('تحويل بنكي')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_name = models.CharField(max_length=100, verbose_name=_("اسم التقرير"))
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, verbose_name=_("نوع التقرير"))

    # Report Parameters
    payroll_period = models.ForeignKey(
        PayrollPeriod,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name=_("فترة الراتب")
    )
    departments = models.ManyToManyField(
        'employee_management.Department',
        blank=True,
        related_name='payroll_reports',
        verbose_name=_("الأقسام")
    )

    # Report File
    report_file = models.FileField(
        upload_to='payroll_reports/',
        null=True,
        blank=True,
        verbose_name=_("ملف التقرير")
    )

    # Generation Information
    generated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='generated_payroll_reports',
        verbose_name=_("أنشئ بواسطة")
    )
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))

    # Status
    is_confidential = models.BooleanField(default=True, verbose_name=_("سري"))

    class Meta:
        verbose_name = _("تقرير الرواتب")
        verbose_name_plural = _("تقارير الرواتب")
        ordering = ['-generated_at']
        db_table = 'payroll_management_payroll_report'

    def __str__(self):
        return f"{self.report_name} - {self.payroll_period.period_name}"

    def get_absolute_url(self):
        return reverse('payroll_management:report_detail', kwargs={'pk': self.id})
