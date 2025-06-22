"""
Leave Management Admin Configuration
Comprehensive admin interface for leave management
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import LeaveType, LeaveBalance, LeaveRequest, LeaveApproval, Holiday, LeavePolicy


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = [
        'leave_type_code', 'leave_type_name', 'is_paid', 'requires_approval',
        'calculation_method', 'default_balance', 'is_active'
    ]
    list_filter = [
        'is_paid', 'requires_approval', 'requires_medical_certificate',
        'calculation_method', 'gender_restriction', 'is_active'
    ]
    search_fields = ['leave_type_name', 'leave_type_name_en', 'description']
    list_editable = ['is_active']
    readonly_fields = ['leave_type_code', 'created_at', 'updated_at']

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('leave_type_code', 'leave_type_name', 'leave_type_name_en', 'description')
        }),
        (_('إعدادات الإجازة'), {
            'fields': (
                'is_paid', 'requires_approval', 'requires_medical_certificate',
                'calculation_method', 'default_balance', 'max_balance'
            )
        }),
        (_('حدود الطلبات'), {
            'fields': (
                'min_days_per_request', 'max_days_per_request', 'max_requests_per_year',
                'min_advance_notice_days'
            )
        }),
        (_('القيود'), {
            'fields': (
                'gender_restriction', 'exclude_weekends', 'exclude_holidays'
            )
        }),
        (_('إعدادات الترحيل'), {
            'fields': (
                'allow_carryover', 'max_carryover_days', 'carryover_expiry_months'
            )
        }),
        (_('الحالة'), {
            'fields': ('is_active',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'leave_type', 'year', 'allocated_days',
        'used_days', 'pending_days', 'available_days'
    ]
    list_filter = ['year', 'leave_type', 'employee__department']
    search_fields = [
        'employee__first_name', 'employee__last_name', 'employee__employee_id',
        'leave_type__leave_type_name'
    ]
    readonly_fields = ['id', 'available_days', 'total_allocated', 'created_at', 'updated_at']

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('id', 'employee', 'leave_type', 'year')
        }),
        (_('الأرصدة'), {
            'fields': (
                'allocated_days', 'used_days', 'pending_days',
                'carried_over_days', 'available_days', 'total_allocated'
            )
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def available_days(self, obj):
        return obj.available_days
    available_days.short_description = _('الأيام المتاحة')


class LeaveApprovalInline(admin.TabularInline):
    model = LeaveApproval
    extra = 0
    readonly_fields = ['id', 'action_date']
    fields = ['approver', 'approval_level', 'action', 'approved_days', 'comments']


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = [
        'request_number', 'employee', 'leave_type', 'start_date', 'end_date',
        'requested_days', 'status', 'priority', 'submitted_at'
    ]
    list_filter = [
        'status', 'priority', 'leave_type', 'employee__department',
        'start_date', 'submitted_at'
    ]
    search_fields = [
        'request_number', 'employee__first_name', 'employee__last_name',
        'employee__employee_id', 'reason'
    ]
    readonly_fields = [
        'id', 'request_number', 'duration_in_days', 'is_overdue',
        'can_be_cancelled', 'can_be_approved', 'created_at', 'updated_at'
    ]
    inlines = [LeaveApprovalInline]
    date_hierarchy = 'start_date'

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('id', 'request_number', 'employee', 'leave_type')
        }),
        (_('تواريخ الإجازة'), {
            'fields': (
                'start_date', 'end_date', 'return_date', 'actual_return_date',
                'duration_in_days'
            )
        }),
        (_('المدة'), {
            'fields': ('requested_days', 'approved_days')
        }),
        (_('تفاصيل الطلب'), {
            'fields': ('reason', 'emergency_contact', 'emergency_phone', 'medical_certificate')
        }),
        (_('الحالة والأولوية'), {
            'fields': ('status', 'priority')
        }),
        (_('التقديم'), {
            'fields': ('submitted_by', 'submitted_at')
        }),
        (_('التعليقات'), {
            'fields': ('employee_comments', 'admin_comments')
        }),
        (_('حالة الطلب'), {
            'fields': ('is_overdue', 'can_be_cancelled', 'can_be_approved')
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LeaveApproval)
class LeaveApprovalAdmin(admin.ModelAdmin):
    list_display = [
        'leave_request', 'approver', 'approval_level', 'action',
        'approved_days', 'action_date'
    ]
    list_filter = ['action', 'approval_level', 'action_date']
    search_fields = [
        'leave_request__request_number', 'leave_request__employee__first_name',
        'leave_request__employee__last_name', 'approver__first_name', 'approver__last_name'
    ]
    readonly_fields = ['id', 'action_date']

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('id', 'leave_request', 'approver', 'approval_level')
        }),
        (_('الإجراء'), {
            'fields': ('action', 'approved_days', 'comments')
        }),
        (_('معلومات النظام'), {
            'fields': ('action_date',)
        }),
    )


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'date', 'end_date', 'holiday_type', 'duration_days',
        'is_recurring', 'affects_leave_calculation', 'is_active'
    ]
    list_filter = [
        'holiday_type', 'is_recurring', 'affects_leave_calculation',
        'applies_to_all', 'is_active', 'date'
    ]
    search_fields = ['name', 'name_en', 'description']
    list_editable = ['is_active']
    readonly_fields = ['id', 'duration_days', 'created_at', 'updated_at']
    filter_horizontal = ['departments']
    date_hierarchy = 'date'

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('id', 'name', 'name_en', 'description')
        }),
        (_('التواريخ'), {
            'fields': ('date', 'end_date', 'duration_days')
        }),
        (_('إعدادات العطلة'), {
            'fields': (
                'holiday_type', 'is_recurring', 'affects_leave_calculation'
            )
        }),
        (_('التطبيق'), {
            'fields': ('applies_to_all', 'departments')
        }),
        (_('الحالة'), {
            'fields': ('is_active',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def duration_days(self, obj):
        return obj.duration_days
    duration_days.short_description = _('مدة العطلة (أيام)')


@admin.register(LeavePolicy)
class LeavePolicyAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'effective_from', 'effective_to', 'applies_to_all', 'is_active'
    ]
    list_filter = ['applies_to_all', 'is_active', 'effective_from']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    readonly_fields = ['id', 'created_at', 'updated_at']
    filter_horizontal = ['departments', 'job_titles']
    date_hierarchy = 'effective_from'

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('id', 'name', 'description', 'policy_document')
        }),
        (_('التطبيق'), {
            'fields': ('applies_to_all', 'departments', 'job_titles')
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
