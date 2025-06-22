"""
Payroll Management Admin Configuration
Comprehensive admin interface for payroll management
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import (
    SalaryComponent, EmployeeSalaryStructure, EmployeeSalaryComponent,
    PayrollPeriod, PayrollTransaction, EmployeePayslip, PayslipComponent,
    TaxConfiguration, PayrollReport
)


@admin.register(SalaryComponent)
class SalaryComponentAdmin(admin.ModelAdmin):
    list_display = [
        'component_id', 'component_name', 'component_type', 'calculation_method',
        'default_amount', 'is_taxable', 'is_mandatory', 'display_order', 'is_active'
    ]
    list_filter = [
        'component_type', 'calculation_method', 'is_taxable',
        'is_insurance_applicable', 'is_mandatory', 'is_active'
    ]
    search_fields = ['component_name', 'component_name_en', 'description']
    list_editable = ['is_active', 'display_order']
    readonly_fields = ['component_id', 'created_at', 'updated_at']

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('component_id', 'component_name', 'component_name_en', 'component_type', 'description')
        }),
        (_('إعدادات الحساب'), {
            'fields': (
                'calculation_method', 'default_amount', 'percentage_rate', 'calculation_formula'
            )
        }),
        (_('إعدادات الضريبة والتأمين'), {
            'fields': ('is_taxable', 'is_insurance_applicable')
        }),
        (_('إعدادات العرض'), {
            'fields': ('display_order', 'is_mandatory')
        }),
        (_('الحالة'), {
            'fields': ('is_active',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class EmployeeSalaryComponentInline(admin.TabularInline):
    model = EmployeeSalaryComponent
    extra = 0
    readonly_fields = ['id', 'created_at', 'updated_at']
    fields = ['component', 'amount', 'percentage', 'is_active', 'notes']


@admin.register(EmployeeSalaryStructure)
class EmployeeSalaryStructureAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'basic_salary', 'currency', 'effective_from', 'effective_to', 'is_active'
    ]
    list_filter = ['currency', 'is_active', 'effective_from', 'employee__department']
    search_fields = [
        'employee__first_name', 'employee__last_name', 'employee__employee_id'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [EmployeeSalaryComponentInline]
    date_hierarchy = 'effective_from'

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('id', 'employee', 'basic_salary', 'currency')
        }),
        (_('فترة السريان'), {
            'fields': ('effective_from', 'effective_to')
        }),
        (_('معلومات البنك'), {
            'fields': ('bank_name', 'bank_account_number', 'iban')
        }),
        (_('الحالة'), {
            'fields': ('is_active',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee', 'created_by')


@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    list_display = [
        'period_id', 'period_name', 'start_date', 'end_date', 'pay_date',
        'status', 'total_employees', 'processing_progress', 'total_net_salary'
    ]
    list_filter = ['status', 'start_date', 'pay_date']
    search_fields = ['period_name']
    readonly_fields = [
        'period_id', 'processing_progress', 'is_editable', 'created_at', 'updated_at'
    ]
    date_hierarchy = 'start_date'

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('period_id', 'period_name')
        }),
        (_('التواريخ'), {
            'fields': ('start_date', 'end_date', 'pay_date')
        }),
        (_('معلومات المعالجة'), {
            'fields': ('status', 'total_employees', 'processed_employees', 'processing_progress')
        }),
        (_('الملخص المالي'), {
            'fields': ('total_gross_salary', 'total_deductions', 'total_net_salary')
        }),
        (_('معلومات الحساب'), {
            'fields': ('calculated_by', 'calculated_at')
        }),
        (_('معلومات الاعتماد'), {
            'fields': ('approved_by', 'approved_at')
        }),
        (_('حالة التحرير'), {
            'fields': ('is_editable',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def processing_progress(self, obj):
        progress = obj.processing_progress
        color = 'green' if progress == 100 else 'orange' if progress > 50 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, progress
        )
    processing_progress.short_description = _('تقدم المعالجة')


@admin.register(PayrollTransaction)
class PayrollTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'payroll_period', 'transaction_type', 'amount',
        'is_approved', 'is_processed', 'created_at'
    ]
    list_filter = [
        'transaction_type', 'is_approved', 'is_processed',
        'payroll_period', 'employee__department'
    ]
    search_fields = [
        'employee__first_name', 'employee__last_name', 'employee__employee_id',
        'description', 'reference_number'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('id', 'employee', 'payroll_period')
        }),
        (_('تفاصيل المعاملة'), {
            'fields': ('transaction_type', 'description', 'amount')
        }),
        (_('معلومات المرجع'), {
            'fields': ('reference_number', 'reference_date')
        }),
        (_('معلومات الاعتماد'), {
            'fields': ('is_approved', 'approved_by', 'approval_date')
        }),
        (_('معلومات المعالجة'), {
            'fields': ('is_processed', 'created_by')
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'employee', 'payroll_period', 'approved_by', 'created_by'
        )


class PayslipComponentInline(admin.TabularInline):
    model = PayslipComponent
    extra = 0
    readonly_fields = ['id', 'created_at']
    fields = ['component', 'amount', 'calculation_base', 'rate_or_percentage', 'calculation_notes']


@admin.register(EmployeePayslip)
class EmployeePayslipAdmin(admin.ModelAdmin):
    list_display = [
        'payslip_number', 'employee', 'payroll_period', 'gross_salary',
        'total_deductions', 'net_salary', 'status', 'payment_date'
    ]
    list_filter = [
        'status', 'payroll_period', 'employee__department', 'calculation_date'
    ]
    search_fields = [
        'payslip_number', 'employee__first_name', 'employee__last_name',
        'employee__employee_id'
    ]
    readonly_fields = ['id', 'payslip_number', 'attendance_percentage', 'created_at', 'updated_at']
    inlines = [PayslipComponentInline]
    date_hierarchy = 'calculation_date'

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('id', 'payslip_number', 'employee', 'payroll_period', 'salary_structure')
        }),
        (_('معلومات الحضور'), {
            'fields': (
                'working_days', 'present_days', 'absent_days', 'leave_days',
                'overtime_hours', 'attendance_percentage'
            )
        }),
        (_('حسابات الراتب'), {
            'fields': (
                'basic_salary', 'total_allowances', 'total_bonuses',
                'overtime_amount', 'gross_salary'
            )
        }),
        (_('الخصومات'), {
            'fields': (
                'total_deductions', 'tax_deduction', 'insurance_deduction',
                'loan_deduction', 'advance_deduction', 'other_deductions'
            )
        }),
        (_('الراتب الصافي'), {
            'fields': ('net_salary',)
        }),
        (_('الحالة والمعالجة'), {
            'fields': ('status', 'calculation_date', 'payment_date')
        }),
        (_('التعليقات'), {
            'fields': ('comments',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'employee', 'payroll_period', 'salary_structure'
        )


@admin.register(TaxConfiguration)
class TaxConfigurationAdmin(admin.ModelAdmin):
    list_display = [
        'tax_name', 'calculation_method', 'tax_rate', 'minimum_taxable_amount',
        'effective_from', 'effective_to', 'is_active'
    ]
    list_filter = ['calculation_method', 'is_active', 'effective_from']
    search_fields = ['tax_name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'effective_from'

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('id', 'tax_name', 'description')
        }),
        (_('إعدادات الضريبة'), {
            'fields': (
                'calculation_method', 'tax_rate', 'minimum_taxable_amount',
                'maximum_taxable_amount'
            )
        }),
        (_('فترة السريان'), {
            'fields': ('effective_from', 'effective_to')
        }),
        (_('الحالة'), {
            'fields': ('is_active',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PayrollReport)
class PayrollReportAdmin(admin.ModelAdmin):
    list_display = [
        'report_name', 'report_type', 'payroll_period', 'generated_by',
        'generated_at', 'is_confidential'
    ]
    list_filter = ['report_type', 'is_confidential', 'generated_at', 'payroll_period']
    search_fields = ['report_name']
    readonly_fields = ['id', 'generated_at']
    filter_horizontal = ['departments']
    date_hierarchy = 'generated_at'

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('id', 'report_name', 'report_type')
        }),
        (_('معاملات التقرير'), {
            'fields': ('payroll_period', 'departments')
        }),
        (_('ملف التقرير'), {
            'fields': ('report_file',)
        }),
        (_('معلومات الإنشاء'), {
            'fields': ('generated_by', 'generated_at')
        }),
        (_('الحالة'), {
            'fields': ('is_confidential',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('payroll_period', 'generated_by')
