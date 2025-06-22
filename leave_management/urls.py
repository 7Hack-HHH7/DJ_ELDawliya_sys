"""
Leave Management URL Configuration
URL patterns for leave management views
"""
from django.urls import path, include
from . import views

app_name = 'leave_management'

# Leave Type URLs
leave_type_patterns = [
    path('', views.LeaveTypeListView.as_view(), name='leave_type_list'),
    path('create/', views.LeaveTypeCreateView.as_view(), name='leave_type_create'),
    path('<int:pk>/', views.LeaveTypeDetailView.as_view(), name='leave_type_detail'),
    path('<int:pk>/edit/', views.LeaveTypeUpdateView.as_view(), name='leave_type_edit'),
    path('<int:pk>/delete/', views.LeaveTypeDeleteView.as_view(), name='leave_type_delete'),
]

# Leave Request URLs
leave_request_patterns = [
    path('', views.LeaveRequestListView.as_view(), name='leave_request_list'),
    path('create/', views.LeaveRequestCreateView.as_view(), name='leave_request_create'),
    path('<uuid:pk>/', views.LeaveRequestDetailView.as_view(), name='leave_request_detail'),
    path('<uuid:pk>/edit/', views.LeaveRequestUpdateView.as_view(), name='leave_request_edit'),
    path('<uuid:pk>/cancel/', views.LeaveRequestCancelView.as_view(), name='leave_request_cancel'),
    path('<uuid:pk>/approve/', views.LeaveRequestApproveView.as_view(), name='leave_request_approve'),
    path('<uuid:pk>/reject/', views.LeaveRequestRejectView.as_view(), name='leave_request_reject'),
    path('my-requests/', views.MyLeaveRequestsView.as_view(), name='my_leave_requests'),
    path('pending-approval/', views.PendingApprovalView.as_view(), name='pending_approval'),
]

# Leave Balance URLs
leave_balance_patterns = [
    path('', views.LeaveBalanceListView.as_view(), name='leave_balance_list'),
    path('employee/<uuid:employee_id>/', views.EmployeeLeaveBalanceView.as_view(), name='employee_leave_balance'),
    path('my-balance/', views.MyLeaveBalanceView.as_view(), name='my_leave_balance'),
    path('update/', views.LeaveBalanceUpdateView.as_view(), name='leave_balance_update'),
]

# Holiday URLs
holiday_patterns = [
    path('', views.HolidayListView.as_view(), name='holiday_list'),
    path('create/', views.HolidayCreateView.as_view(), name='holiday_create'),
    path('<uuid:pk>/', views.HolidayDetailView.as_view(), name='holiday_detail'),
    path('<uuid:pk>/edit/', views.HolidayUpdateView.as_view(), name='holiday_edit'),
    path('<uuid:pk>/delete/', views.HolidayDeleteView.as_view(), name='holiday_delete'),
    path('calendar/', views.HolidayCalendarView.as_view(), name='holiday_calendar'),
]

# Leave Policy URLs
policy_patterns = [
    path('', views.LeavePolicyListView.as_view(), name='leave_policy_list'),
    path('create/', views.LeavePolicyCreateView.as_view(), name='leave_policy_create'),
    path('<uuid:pk>/', views.LeavePolicyDetailView.as_view(), name='leave_policy_detail'),
    path('<uuid:pk>/edit/', views.LeavePolicyUpdateView.as_view(), name='leave_policy_edit'),
    path('<uuid:pk>/delete/', views.LeavePolicyDeleteView.as_view(), name='leave_policy_delete'),
]

# API URLs
api_patterns = [
    path('leave-types/', views.LeaveTypeAPIView.as_view(), name='api_leave_types'),
    path('leave-requests/', views.LeaveRequestAPIView.as_view(), name='api_leave_requests'),
    path('leave-balances/', views.LeaveBalanceAPIView.as_view(), name='api_leave_balances'),
    path('holidays/', views.HolidayAPIView.as_view(), name='api_holidays'),
    path('policies/', views.LeavePolicyAPIView.as_view(), name='api_policies'),
]

# Main URL patterns
urlpatterns = [
    # Dashboard
    path('', views.LeaveManagementDashboardView.as_view(), name='dashboard'),
    
    # Leave Type management
    path('types/', include(leave_type_patterns)),
    
    # Leave Request management
    path('requests/', include(leave_request_patterns)),
    
    # Leave Balance management
    path('balances/', include(leave_balance_patterns)),
    
    # Holiday management
    path('holidays/', include(holiday_patterns)),
    
    # Policy management
    path('policies/', include(policy_patterns)),
    
    # API endpoints
    path('api/', include(api_patterns)),
    
    # Reports
    path('reports/', views.LeaveReportsView.as_view(), name='reports'),
    path('reports/export/', views.LeaveExportView.as_view(), name='export'),
    
    # Calendar view
    path('calendar/', views.LeaveCalendarView.as_view(), name='calendar'),
]
