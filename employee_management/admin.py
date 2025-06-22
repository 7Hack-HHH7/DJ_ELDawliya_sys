"""
Employee Management Admin Configuration
Comprehensive admin interface for employee management
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import Department, JobTitle, Employee, EmployeeNote, EmployeeDocument


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['dept_code', 'dept_name', 'parent_department', 'manager', 'employee_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent_department', 'created_at']
    search_fields = ['dept_name', 'dept_name_en', 'description']
    list_editable = ['is_active']
    readonly_fields = ['dept_code', 'created_at', 'updated_at', 'employee_count']
    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('dept_code', 'dept_name', 'dept_name_en', 'description')
        }),
        (_('الهيكل التنظيمي'), {
            'fields': ('parent_department', 'manager')
        }),
        (_('الحالة'), {
            'fields': ('is_active',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def employee_count(self, obj):
        return obj.employee_count
    employee_count.short_description = _('عدد الموظفين')


@admin.register(JobTitle)
class JobTitleAdmin(admin.ModelAdmin):
    list_display = ['job_code', 'job_title', 'department', 'grade_level', 'min_salary', 'max_salary', 'is_active']
    list_filter = ['department', 'grade_level', 'is_active', 'created_at']
    search_fields = ['job_title', 'job_title_en', 'description']
    list_editable = ['is_active']
    readonly_fields = ['job_code', 'created_at', 'updated_at']
    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('job_code', 'job_title', 'job_title_en', 'description')
        }),
        (_('التصنيف'), {
            'fields': ('department', 'grade_level')
        }),
        (_('نطاق الراتب'), {
            'fields': ('min_salary', 'max_salary')
        }),
        (_('الحالة'), {
            'fields': ('is_active',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class EmployeeNoteInline(admin.TabularInline):
    model = EmployeeNote
    extra = 0
    readonly_fields = ['created_at', 'updated_at']
    fields = ['title', 'note_type', 'priority', 'note_date', 'requires_followup', 'is_confidential']


class EmployeeDocumentInline(admin.TabularInline):
    model = EmployeeDocument
    extra = 0
    readonly_fields = ['created_at', 'updated_at', 'file_size']
    fields = ['title', 'document_type', 'document_date', 'expiry_date', 'is_confidential']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'emp_code', 'employee_id', 'full_name', 'department', 'job_title',
        'employment_status', 'hire_date', 'is_active'
    ]
    list_filter = [
        'department', 'job_title', 'employment_status', 'gender',
        'marital_status', 'is_active', 'hire_date'
    ]
    search_fields = [
        'employee_id', 'first_name', 'last_name', 'first_name_en', 'last_name_en',
        'national_id', 'email', 'phone_number'
    ]
    list_editable = ['employment_status', 'is_active']
    readonly_fields = ['emp_code', 'age', 'years_of_service', 'created_at', 'updated_at']
    inlines = [EmployeeNoteInline, EmployeeDocumentInline]

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('emp_code', 'employee_id', 'profile_image')
        }),
        (_('المعلومات الشخصية'), {
            'fields': (
                ('first_name', 'middle_name', 'last_name'),
                ('first_name_en', 'middle_name_en', 'last_name_en'),
                ('date_of_birth', 'gender', 'marital_status'),
                'nationality'
            )
        }),
        (_('معلومات الهوية'), {
            'fields': ('national_id', 'passport_number')
        }),
        (_('معلومات الاتصال'), {
            'fields': (
                'email',
                ('phone_number', 'mobile_number'),
                'address',
                ('city', 'state'),
                ('postal_code', 'country')
            )
        }),
        (_('معلومات التوظيف'), {
            'fields': (
                ('department', 'job_title'),
                'direct_manager',
                ('hire_date', 'probation_end_date'),
                'termination_date',
                'employment_status'
            )
        }),
        (_('ربط النظام'), {
            'fields': ('user_account',)
        }),
        (_('الحالة'), {
            'fields': ('is_active',)
        }),
        (_('معلومات النظام'), {
            'fields': ('age', 'years_of_service', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = _('الاسم الكامل')


@admin.register(EmployeeNote)
class EmployeeNoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'employee', 'note_type', 'priority', 'note_date', 'requires_followup', 'created_by']
    list_filter = ['note_type', 'priority', 'requires_followup', 'followup_completed', 'is_confidential', 'note_date']
    search_fields = ['title', 'content', 'employee__first_name', 'employee__last_name', 'employee__employee_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'note_date'

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('id', 'employee', 'title', 'note_type', 'priority')
        }),
        (_('المحتوى'), {
            'fields': ('content',)
        }),
        (_('التاريخ والمؤلف'), {
            'fields': ('note_date', 'created_by')
        }),
        (_('المتابعة'), {
            'fields': ('requires_followup', 'followup_date', 'followup_completed')
        }),
        (_('الوصول'), {
            'fields': ('is_confidential', 'is_active')
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'employee', 'document_type', 'document_date', 'expiry_date', 'is_expired', 'uploaded_by']
    list_filter = ['document_type', 'is_confidential', 'document_date', 'expiry_date']
    search_fields = ['title', 'description', 'employee__first_name', 'employee__last_name', 'employee__employee_id']
    readonly_fields = ['id', 'file_size', 'is_expired', 'created_at', 'updated_at']
    date_hierarchy = 'document_date'

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('id', 'employee', 'title', 'document_type', 'description')
        }),
        (_('الملف'), {
            'fields': ('document_file', 'file_size')
        }),
        (_('التواريخ'), {
            'fields': ('document_date', 'expiry_date', 'is_expired')
        }),
        (_('الرفع'), {
            'fields': ('uploaded_by',)
        }),
        (_('الوصول'), {
            'fields': ('is_confidential', 'is_active')
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_expired(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: red;">منتهي الصلاحية</span>')
        return format_html('<span style="color: green;">ساري</span>')
    is_expired.short_description = _('حالة الصلاحية')
