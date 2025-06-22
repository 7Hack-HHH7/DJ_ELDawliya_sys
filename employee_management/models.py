"""
Employee Management Models
Comprehensive models for employee profiles, departments, jobs, and organizational structure
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, EmailValidator
from django.urls import reverse
import uuid

User = get_user_model()


class Department(models.Model):
    """Department model for organizational structure"""
    dept_code = models.AutoField(primary_key=True, verbose_name=_("رمز القسم"))
    dept_name = models.CharField(max_length=100, unique=True, verbose_name=_("اسم القسم"))
    dept_name_en = models.CharField(max_length=100, blank=True, verbose_name=_("اسم القسم بالإنجليزية"))
    description = models.TextField(blank=True, verbose_name=_("الوصف"))
    parent_department = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_departments',
        verbose_name=_("القسم الرئيسي")
    )
    manager = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments',
        verbose_name=_("مدير القسم")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("قسم")
        verbose_name_plural = _("الأقسام")
        ordering = ['dept_name']
        db_table = 'employee_management_department'

    def __str__(self):
        return self.dept_name

    def get_absolute_url(self):
        return reverse('employee_management:department_detail', kwargs={'pk': self.dept_code})

    @property
    def employee_count(self):
        return self.employees.filter(is_active=True).count()

    @property
    def hierarchy_level(self):
        level = 0
        parent = self.parent_department
        while parent:
            level += 1
            parent = parent.parent_department
        return level


class JobTitle(models.Model):
    """Job title/position model"""
    job_code = models.AutoField(primary_key=True, verbose_name=_("رمز الوظيفة"))
    job_title = models.CharField(max_length=100, unique=True, verbose_name=_("المسمى الوظيفي"))
    job_title_en = models.CharField(max_length=100, blank=True, verbose_name=_("المسمى الوظيفي بالإنجليزية"))
    description = models.TextField(blank=True, verbose_name=_("الوصف"))
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='job_titles',
        verbose_name=_("القسم")
    )
    grade_level = models.PositiveIntegerField(default=1, verbose_name=_("المستوى الوظيفي"))
    min_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("الحد الأدنى للراتب"))
    max_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("الحد الأقصى للراتب"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("وظيفة")
        verbose_name_plural = _("الوظائف")
        ordering = ['department', 'grade_level', 'job_title']
        db_table = 'employee_management_job_title'

    def __str__(self):
        return f"{self.job_title} - {self.department.dept_name}"

    def get_absolute_url(self):
        return reverse('employee_management:job_detail', kwargs={'pk': self.job_code})


class Employee(models.Model):
    """Comprehensive Employee model"""
    GENDER_CHOICES = [
        ('M', _('ذكر')),
        ('F', _('أنثى')),
    ]

    MARITAL_STATUS_CHOICES = [
        ('single', _('أعزب')),
        ('married', _('متزوج')),
        ('divorced', _('مطلق')),
        ('widowed', _('أرمل')),
    ]

    EMPLOYMENT_STATUS_CHOICES = [
        ('active', _('نشط')),
        ('inactive', _('غير نشط')),
        ('terminated', _('منتهي الخدمة')),
        ('suspended', _('موقوف')),
        ('on_leave', _('في إجازة')),
    ]

    # Primary Information
    emp_code = models.AutoField(primary_key=True, verbose_name=_("رمز الموظف"))
    employee_id = models.CharField(max_length=20, unique=True, verbose_name=_("الرقم الوظيفي"))

    # Personal Information
    first_name = models.CharField(max_length=50, verbose_name=_("الاسم الأول"))
    middle_name = models.CharField(max_length=50, blank=True, verbose_name=_("الاسم الأوسط"))
    last_name = models.CharField(max_length=50, verbose_name=_("اسم العائلة"))
    first_name_en = models.CharField(max_length=50, blank=True, verbose_name=_("الاسم الأول بالإنجليزية"))
    middle_name_en = models.CharField(max_length=50, blank=True, verbose_name=_("الاسم الأوسط بالإنجليزية"))
    last_name_en = models.CharField(max_length=50, blank=True, verbose_name=_("اسم العائلة بالإنجليزية"))

    # Identity Information
    national_id = models.CharField(
        max_length=20,
        unique=True,
        validators=[RegexValidator(r'^\d{10,20}$', _('رقم الهوية يجب أن يكون من 10-20 رقم'))],
        verbose_name=_("رقم الهوية الوطنية")
    )
    passport_number = models.CharField(max_length=20, blank=True, verbose_name=_("رقم جواز السفر"))

    # Contact Information
    email = models.EmailField(unique=True, validators=[EmailValidator()], verbose_name=_("البريد الإلكتروني"))
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', _('رقم الهاتف غير صحيح'))],
        verbose_name=_("رقم الهاتف")
    )
    mobile_number = models.CharField(
        max_length=15,
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', _('رقم الجوال غير صحيح'))],
        verbose_name=_("رقم الجوال")
    )

    # Address Information
    address = models.TextField(verbose_name=_("العنوان"))
    city = models.CharField(max_length=50, verbose_name=_("المدينة"))
    state = models.CharField(max_length=50, verbose_name=_("المنطقة/الولاية"))
    postal_code = models.CharField(max_length=10, blank=True, verbose_name=_("الرمز البريدي"))
    country = models.CharField(max_length=50, default='Saudi Arabia', verbose_name=_("البلد"))

    # Personal Details
    date_of_birth = models.DateField(verbose_name=_("تاريخ الميلاد"))
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name=_("الجنس"))
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES, verbose_name=_("الحالة الاجتماعية"))
    nationality = models.CharField(max_length=50, default='Saudi', verbose_name=_("الجنسية"))

    # Employment Information
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='employees',
        verbose_name=_("القسم")
    )
    job_title = models.ForeignKey(
        JobTitle,
        on_delete=models.PROTECT,
        related_name='employees',
        verbose_name=_("المسمى الوظيفي")
    )
    direct_manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates',
        verbose_name=_("المدير المباشر")
    )

    # Employment Dates
    hire_date = models.DateField(verbose_name=_("تاريخ التوظيف"))
    probation_end_date = models.DateField(null=True, blank=True, verbose_name=_("تاريخ انتهاء فترة التجربة"))
    termination_date = models.DateField(null=True, blank=True, verbose_name=_("تاريخ انتهاء الخدمة"))

    # Status and Settings
    employment_status = models.CharField(
        max_length=15,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default='active',
        verbose_name=_("حالة التوظيف")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))

    # Profile Image
    profile_image = models.ImageField(
        upload_to='employee_profiles/',
        null=True,
        blank=True,
        verbose_name=_("صورة الملف الشخصي")
    )

    # System Integration
    user_account = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_profile',
        verbose_name=_("حساب المستخدم")
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("موظف")
        verbose_name_plural = _("الموظفين")
        ordering = ['first_name', 'last_name']
        db_table = 'employee_management_employee'
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['national_id']),
            models.Index(fields=['email']),
            models.Index(fields=['department', 'employment_status']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"

    def get_absolute_url(self):
        return reverse('employee_management:employee_detail', kwargs={'pk': self.emp_code})

    @property
    def full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}".strip()

    @property
    def full_name_en(self):
        return f"{self.first_name_en} {self.middle_name_en} {self.last_name_en}".strip()

    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    @property
    def years_of_service(self):
        from datetime import date
        today = date.today()
        return today.year - self.hire_date.year - ((today.month, today.day) < (self.hire_date.month, self.hire_date.day))


class EmployeeNote(models.Model):
    """Employee notes for comprehensive reporting"""
    NOTE_TYPES = [
        ('performance', _('تقييم الأداء')),
        ('disciplinary', _('إجراء تأديبي')),
        ('achievement', _('إنجاز')),
        ('training', _('تدريب')),
        ('general', _('عام')),
        ('warning', _('تحذير')),
        ('commendation', _('تقدير')),
    ]

    PRIORITY_LEVELS = [
        ('low', _('منخفض')),
        ('medium', _('متوسط')),
        ('high', _('عالي')),
        ('critical', _('حرج')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_("الموظف")
    )
    title = models.CharField(max_length=200, verbose_name=_("عنوان الملاحظة"))
    note_type = models.CharField(max_length=15, choices=NOTE_TYPES, verbose_name=_("نوع الملاحظة"))
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium', verbose_name=_("الأولوية"))
    content = models.TextField(verbose_name=_("محتوى الملاحظة"))

    # Date and Author Information
    note_date = models.DateField(verbose_name=_("تاريخ الملاحظة"))
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='employee_notes_created',
        verbose_name=_("أنشئت بواسطة")
    )

    # Follow-up Information
    requires_followup = models.BooleanField(default=False, verbose_name=_("تتطلب متابعة"))
    followup_date = models.DateField(null=True, blank=True, verbose_name=_("تاريخ المتابعة"))
    followup_completed = models.BooleanField(default=False, verbose_name=_("تمت المتابعة"))

    # Visibility and Access
    is_confidential = models.BooleanField(default=False, verbose_name=_("سري"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("ملاحظة موظف")
        verbose_name_plural = _("ملاحظات الموظفين")
        ordering = ['-note_date', '-created_at']
        db_table = 'employee_management_employee_note'
        indexes = [
            models.Index(fields=['employee', 'note_type']),
            models.Index(fields=['note_date']),
            models.Index(fields=['priority']),
        ]

    def __str__(self):
        return f"{self.title} - {self.employee.full_name}"

    def get_absolute_url(self):
        return reverse('employee_management:note_detail', kwargs={'pk': self.id})


class EmployeeDocument(models.Model):
    """Employee document management"""
    DOCUMENT_TYPES = [
        ('contract', _('عقد العمل')),
        ('id_copy', _('صورة الهوية')),
        ('passport_copy', _('صورة جواز السفر')),
        ('certificate', _('شهادة')),
        ('cv', _('السيرة الذاتية')),
        ('medical_report', _('تقرير طبي')),
        ('performance_review', _('تقييم الأداء')),
        ('disciplinary_action', _('إجراء تأديبي')),
        ('other', _('أخرى')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_("الموظف")
    )
    title = models.CharField(max_length=200, verbose_name=_("عنوان الوثيقة"))
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, verbose_name=_("نوع الوثيقة"))
    description = models.TextField(blank=True, verbose_name=_("الوصف"))

    # File Information
    document_file = models.FileField(
        upload_to='employee_documents/',
        verbose_name=_("ملف الوثيقة")
    )
    file_size = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("حجم الملف"))

    # Date Information
    document_date = models.DateField(verbose_name=_("تاريخ الوثيقة"))
    expiry_date = models.DateField(null=True, blank=True, verbose_name=_("تاريخ الانتهاء"))

    # Upload Information
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='employee_documents_uploaded',
        verbose_name=_("رفعت بواسطة")
    )

    # Access Control
    is_confidential = models.BooleanField(default=False, verbose_name=_("سري"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("وثيقة موظف")
        verbose_name_plural = _("وثائق الموظفين")
        ordering = ['-document_date', '-created_at']
        db_table = 'employee_management_employee_document'
        indexes = [
            models.Index(fields=['employee', 'document_type']),
            models.Index(fields=['document_date']),
            models.Index(fields=['expiry_date']),
        ]

    def __str__(self):
        return f"{self.title} - {self.employee.full_name}"

    def get_absolute_url(self):
        return reverse('employee_management:document_detail', kwargs={'pk': self.id})

    @property
    def is_expired(self):
        if self.expiry_date:
            from datetime import date
            return date.today() > self.expiry_date
        return False

    def save(self, *args, **kwargs):
        if self.document_file:
            self.file_size = self.document_file.size
        super().save(*args, **kwargs)
