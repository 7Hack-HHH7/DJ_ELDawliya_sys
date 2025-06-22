"""
Attendance System URL Configuration
URL patterns for attendance system views
"""
from django.urls import path, include
from . import views

app_name = 'attendance_system'

# Device URLs
device_patterns = [
    path('', views.AttendanceDeviceListView.as_view(), name='device_list'),
    path('create/', views.AttendanceDeviceCreateView.as_view(), name='device_create'),
    path('<int:pk>/', views.AttendanceDeviceDetailView.as_view(), name='device_detail'),
    path('<int:pk>/edit/', views.AttendanceDeviceUpdateView.as_view(), name='device_edit'),
    path('<int:pk>/delete/', views.AttendanceDeviceDeleteView.as_view(), name='device_delete'),
    path('<int:pk>/sync/', views.AttendanceDeviceSyncView.as_view(), name='device_sync'),
    path('<int:pk>/test/', views.AttendanceDeviceTestView.as_view(), name='device_test'),
]

# Attendance Rule URLs
rule_patterns = [
    path('', views.AttendanceRuleListView.as_view(), name='rule_list'),
    path('create/', views.AttendanceRuleCreateView.as_view(), name='rule_create'),
    path('<int:pk>/', views.AttendanceRuleDetailView.as_view(), name='rule_detail'),
    path('<int:pk>/edit/', views.AttendanceRuleUpdateView.as_view(), name='rule_edit'),
    path('<int:pk>/delete/', views.AttendanceRuleDeleteView.as_view(), name='rule_delete'),
]

# Attendance Record URLs
record_patterns = [
    path('', views.AttendanceRecordListView.as_view(), name='record_list'),
    path('<int:pk>/', views.AttendanceRecordDetailView.as_view(), name='record_detail'),
    path('<int:pk>/edit/', views.AttendanceRecordUpdateView.as_view(), name='record_edit'),
    path('<int:pk>/delete/', views.AttendanceRecordDeleteView.as_view(), name='record_delete'),
    path('manual/', views.ManualAttendanceRecordView.as_view(), name='manual_record'),
    path('import/', views.AttendanceRecordImportView.as_view(), name='record_import'),
]

# Daily Attendance URLs
daily_patterns = [
    path('', views.DailyAttendanceListView.as_view(), name='daily_list'),
    path('<uuid:pk>/', views.DailyAttendanceDetailView.as_view(), name='daily_detail'),
    path('<uuid:pk>/edit/', views.DailyAttendanceUpdateView.as_view(), name='daily_edit'),
    path('employee/<uuid:employee_id>/', views.EmployeeDailyAttendanceView.as_view(), name='employee_daily'),
    path('my-attendance/', views.MyDailyAttendanceView.as_view(), name='my_daily'),
    path('process/', views.ProcessDailyAttendanceView.as_view(), name='process_daily'),
]

# Exception URLs
exception_patterns = [
    path('', views.AttendanceExceptionListView.as_view(), name='exception_list'),
    path('create/', views.AttendanceExceptionCreateView.as_view(), name='exception_create'),
    path('<uuid:pk>/', views.AttendanceExceptionDetailView.as_view(), name='exception_detail'),
    path('<uuid:pk>/edit/', views.AttendanceExceptionUpdateView.as_view(), name='exception_edit'),
    path('<uuid:pk>/approve/', views.AttendanceExceptionApproveView.as_view(), name='exception_approve'),
    path('<uuid:pk>/reject/', views.AttendanceExceptionRejectView.as_view(), name='exception_reject'),
    path('pending/', views.PendingExceptionsView.as_view(), name='pending_exceptions'),
]

# Monthly Summary URLs
summary_patterns = [
    path('', views.MonthlyAttendanceSummaryListView.as_view(), name='summary_list'),
    path('<uuid:pk>/', views.MonthlyAttendanceSummaryDetailView.as_view(), name='summary_detail'),
    path('employee/<uuid:employee_id>/', views.EmployeeMonthlySummaryView.as_view(), name='employee_summary'),
    path('generate/', views.GenerateMonthlySummaryView.as_view(), name='generate_summary'),
    path('finalize/', views.FinalizeMonthlySummaryView.as_view(), name='finalize_summary'),
]

# API URLs
api_patterns = [
    path('devices/', views.AttendanceDeviceAPIView.as_view(), name='api_devices'),
    path('rules/', views.AttendanceRuleAPIView.as_view(), name='api_rules'),
    path('records/', views.AttendanceRecordAPIView.as_view(), name='api_records'),
    path('daily/', views.DailyAttendanceAPIView.as_view(), name='api_daily'),
    path('exceptions/', views.AttendanceExceptionAPIView.as_view(), name='api_exceptions'),
    path('summaries/', views.MonthlyAttendanceSummaryAPIView.as_view(), name='api_summaries'),
]

# Main URL patterns
urlpatterns = [
    # Dashboard
    path('', views.AttendanceSystemDashboardView.as_view(), name='dashboard'),
    
    # Device management
    path('devices/', include(device_patterns)),
    
    # Rule management
    path('rules/', include(rule_patterns)),
    
    # Record management
    path('records/', include(record_patterns)),
    
    # Daily attendance
    path('daily/', include(daily_patterns)),
    
    # Exception management
    path('exceptions/', include(exception_patterns)),
    
    # Monthly summaries
    path('summaries/', include(summary_patterns)),
    
    # API endpoints
    path('api/', include(api_patterns)),
    
    # Reports
    path('reports/', views.AttendanceReportsView.as_view(), name='reports'),
    path('reports/export/', views.AttendanceExportView.as_view(), name='export'),
    
    # Real-time monitoring
    path('monitor/', views.AttendanceMonitorView.as_view(), name='monitor'),
    
    # Quick actions
    path('mark-attendance/', views.MarkAttendanceView.as_view(), name='mark_attendance'),
]
