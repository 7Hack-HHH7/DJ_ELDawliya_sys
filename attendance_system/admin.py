"""
Attendance System Admin Configuration
Comprehensive admin interface for attendance system management
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import (
    AttendanceDevice, AttendanceRule, AttendanceRecord,
    DailyAttendance, AttendanceException, MonthlyAttendanceSummary
)


@admin.register(AttendanceDevice)
class AttendanceDeviceAdmin(admin.ModelAdmin):
    list_display = [
        'device_id', 'device_name', 'device_type', 'ip_address', 'port',
        'location', 'is_online', 'is_active', 'auto_sync_enabled', 'last_sync_time'
    ]
    list_filter = [
        'device_type', 'connection_type', 'is_active', 'is_online',
        'auto_sync_enabled', 'department'
    ]
    search_fields = ['device_name', 'ip_address', 'serial_number', 'location']
    list_editable = ['is_active', 'auto_sync_enabled']
    readonly_fields = ['device_id', 'is_online', 'last_sync_time', 'created_at', 'updated_at']

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('device_id', 'device_name', 'device_type', 'location', 'department')
        }),
        (_('إعدادات الاتصال'), {
            'fields': ('ip_address', 'port', 'connection_type')
        }),
        (_('معلومات الجهاز'), {
            'fields': ('serial_number', 'firmware_version', 'max_users', 'max_records')
        }),
        (_('إعدادات المزامنة'), {
            'fields': (
                'auto_sync_enabled', 'sync_interval_minutes', 'last_sync_time'
            )
        }),
        (_('الحالة'), {
            'fields': ('is_active', 'is_online')
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('department')


@admin.register(AttendanceRule)
class AttendanceRuleAdmin(admin.ModelAdmin):
    list_display = [
        'rule_id', 'rule_name', 'rule_type', 'work_start_time', 'work_end_time',
        'applies_to_all', 'effective_from', 'effective_to', 'is_active'
    ]
    list_filter = [
        'rule_type', 'applies_to_all', 'is_active', 'effective_from'
    ]
    search_fields = ['rule_name', 'description']
    list_editable = ['is_active']
    readonly_fields = ['rule_id', 'created_at', 'updated_at']
    filter_horizontal = ['departments', 'job_titles']
    date_hierarchy = 'effective_from'

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('rule_id', 'rule_name', 'rule_type', 'description')
        }),
        (_('جدول العمل'), {
            'fields': (
                'work_start_time', 'work_end_time', 'break_start_time', 'break_end_time',
                'working_days'
            )
        }),
        (_('فترات السماح والجزاءات'), {
            'fields': (
                'late_grace_minutes', 'early_departure_grace_minutes'
            )
        }),
        (_('العمل الإضافي'), {
            'fields': ('overtime_threshold_minutes', 'overtime_multiplier')
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


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = [
        'record_id', 'employee', 'device', 'punch_time', 'punch_type',
        'verification_method', 'is_processed', 'is_valid'
    ]
    list_filter = [
        'punch_type', 'verification_method', 'is_processed', 'is_valid',
        'device', 'punch_time'
    ]
    search_fields = [
        'employee__first_name', 'employee__last_name', 'employee__employee_id',
        'device__device_name', 'device_user_id'
    ]
    list_editable = ['is_processed', 'is_valid']
    readonly_fields = ['record_id', 'sync_time', 'created_at']
    date_hierarchy = 'punch_time'

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('record_id', 'employee', 'device')
        }),
        (_('تفاصيل التسجيل'), {
            'fields': (
                'punch_time', 'punch_type', 'verification_method'
            )
        }),
        (_('معلومات الجهاز'), {
            'fields': ('device_user_id', 'device_record_id')
        }),
        (_('حالة المعالجة'), {
            'fields': ('is_processed', 'is_valid', 'error_message')
        }),
        (_('معلومات النظام'), {
            'fields': ('sync_time', 'created_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee', 'device')


@admin.register(DailyAttendance)
class DailyAttendanceAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'attendance_date', 'check_in_time', 'check_out_time',
        'total_work_hours', 'overtime_hours', 'status', 'is_processed'
    ]
    list_filter = [
        'status', 'is_processed', 'is_holiday', 'is_weekend', 'is_on_leave',
        'attendance_date', 'employee__department'
    ]
    search_fields = [
        'employee__first_name', 'employee__last_name', 'employee__employee_id'
    ]
    list_editable = ['is_processed']
    readonly_fields = [
        'id', 'effective_work_hours', 'is_late', 'is_early_departure',
        'created_at', 'updated_at'
    ]
    date_hierarchy = 'attendance_date'

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('id', 'employee', 'attendance_date')
        }),
        (_('أوقات الحضور'), {
            'fields': (
                'check_in_time', 'check_out_time', 'break_out_time', 'break_in_time'
            )
        }),
        (_('الساعات المحسوبة'), {
            'fields': (
                'total_work_hours', 'effective_work_hours', 'break_duration_minutes',
                'overtime_hours'
            )
        }),
        (_('التأخير والانصراف المبكر'), {
            'fields': (
                'late_minutes', 'is_late', 'early_departure_minutes', 'is_early_departure'
            )
        }),
        (_('الحالة والعلامات'), {
            'fields': (
                'status', 'is_holiday', 'is_weekend', 'is_on_leave'
            )
        }),
        (_('القاعدة المطبقة'), {
            'fields': ('attendance_rule',)
        }),
        (_('التعليقات'), {
            'fields': ('comments',)
        }),
        (_('معلومات المعالجة'), {
            'fields': ('is_processed', 'processed_at', 'processed_by')
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee', 'attendance_rule', 'processed_by')


@admin.register(AttendanceException)
class AttendanceExceptionAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'attendance_date', 'exception_type', 'requested_by',
        'is_approved', 'is_applied', 'created_at'
    ]
    list_filter = [
        'exception_type', 'is_approved', 'is_applied', 'attendance_date'
    ]
    search_fields = [
        'employee__first_name', 'employee__last_name', 'employee__employee_id',
        'description'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'attendance_date'

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('id', 'employee', 'attendance_date', 'exception_type')
        }),
        (_('تفاصيل الاستثناء'), {
            'fields': ('description', 'supporting_document')
        }),
        (_('التعديلات'), {
            'fields': (
                'adjusted_check_in', 'adjusted_check_out', 'adjusted_work_hours'
            )
        }),
        (_('معلومات الاعتماد'), {
            'fields': ('requested_by', 'approved_by', 'approval_date')
        }),
        (_('الحالة'), {
            'fields': ('is_approved', 'is_applied')
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee', 'requested_by', 'approved_by')


@admin.register(MonthlyAttendanceSummary)
class MonthlyAttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'year', 'month_name', 'present_days', 'absent_days',
        'total_work_hours', 'attendance_percentage', 'is_finalized'
    ]
    list_filter = [
        'year', 'month', 'is_finalized', 'employee__department'
    ]
    search_fields = [
        'employee__first_name', 'employee__last_name', 'employee__employee_id'
    ]
    readonly_fields = [
        'id', 'month_name', 'attendance_percentage', 'punctuality_percentage',
        'created_at', 'updated_at'
    ]

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('id', 'employee', 'year', 'month', 'month_name')
        }),
        (_('إحصائيات الحضور'), {
            'fields': (
                'total_working_days', 'present_days', 'absent_days',
                'late_days', 'early_departure_days'
            )
        }),
        (_('إحصائيات الوقت'), {
            'fields': (
                'total_work_hours', 'total_overtime_hours',
                'total_late_minutes', 'total_early_departure_minutes'
            )
        }),
        (_('الإجازات والعطل'), {
            'fields': ('leave_days', 'holiday_days', 'weekend_days')
        }),
        (_('مقاييس الأداء'), {
            'fields': ('attendance_percentage', 'punctuality_percentage')
        }),
        (_('معلومات التأكيد'), {
            'fields': ('is_finalized', 'finalized_by', 'finalized_at')
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def month_name(self, obj):
        return obj.month_name
    month_name.short_description = _('الشهر')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee', 'finalized_by')
