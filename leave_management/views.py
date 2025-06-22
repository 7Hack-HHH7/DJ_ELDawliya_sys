"""
Leave Management Views
Basic view stubs for leave management application
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import LeaveType, LeaveBalance, LeaveRequest, LeaveApproval, Holiday, LeavePolicy


@method_decorator(login_required, name='dispatch')
class LeaveManagementDashboardView(TemplateView):
    """Leave Management Dashboard"""
    template_name = 'leave_management/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'إدارة الإجازات',
            'total_leave_types': LeaveType.objects.filter(is_active=True).count(),
            'pending_requests': LeaveRequest.objects.filter(status='submitted').count(),
            'approved_requests': LeaveRequest.objects.filter(status='approved').count(),
            'recent_requests': LeaveRequest.objects.order_by('-created_at')[:5],
        })
        return context


# Leave Type Views
@method_decorator(login_required, name='dispatch')
class LeaveTypeListView(ListView):
    model = LeaveType
    template_name = 'leave_management/leave_type_list.html'
    context_object_name = 'leave_types'
    paginate_by = 20


@method_decorator(login_required, name='dispatch')
class LeaveTypeDetailView(DetailView):
    model = LeaveType
    template_name = 'leave_management/leave_type_detail.html'


@method_decorator(login_required, name='dispatch')
class LeaveTypeCreateView(CreateView):
    model = LeaveType
    template_name = 'leave_management/leave_type_form.html'
    fields = ['leave_type_name', 'leave_type_name_en', 'description', 'is_paid', 'requires_approval']
    success_url = reverse_lazy('leave_management:leave_type_list')


@method_decorator(login_required, name='dispatch')
class LeaveTypeUpdateView(UpdateView):
    model = LeaveType
    template_name = 'leave_management/leave_type_form.html'
    fields = ['leave_type_name', 'leave_type_name_en', 'description', 'is_paid', 'requires_approval']
    success_url = reverse_lazy('leave_management:leave_type_list')


@method_decorator(login_required, name='dispatch')
class LeaveTypeDeleteView(DeleteView):
    model = LeaveType
    template_name = 'leave_management/leave_type_confirm_delete.html'
    success_url = reverse_lazy('leave_management:leave_type_list')


# Leave Request Views
@method_decorator(login_required, name='dispatch')
class LeaveRequestListView(ListView):
    model = LeaveRequest
    template_name = 'leave_management/leave_request_list.html'
    context_object_name = 'leave_requests'
    paginate_by = 20


@method_decorator(login_required, name='dispatch')
class LeaveRequestDetailView(DetailView):
    model = LeaveRequest
    template_name = 'leave_management/leave_request_detail.html'


@method_decorator(login_required, name='dispatch')
class LeaveRequestCreateView(CreateView):
    model = LeaveRequest
    template_name = 'leave_management/leave_request_form.html'
    fields = ['employee', 'leave_type', 'start_date', 'end_date', 'reason']
    success_url = reverse_lazy('leave_management:leave_request_list')


@method_decorator(login_required, name='dispatch')
class LeaveRequestUpdateView(UpdateView):
    model = LeaveRequest
    template_name = 'leave_management/leave_request_form.html'
    fields = ['leave_type', 'start_date', 'end_date', 'reason']
    success_url = reverse_lazy('leave_management:leave_request_list')


@method_decorator(login_required, name='dispatch')
class LeaveRequestCancelView(TemplateView):
    template_name = 'leave_management/leave_request_cancel.html'


@method_decorator(login_required, name='dispatch')
class LeaveRequestApproveView(TemplateView):
    template_name = 'leave_management/leave_request_approve.html'


@method_decorator(login_required, name='dispatch')
class LeaveRequestRejectView(TemplateView):
    template_name = 'leave_management/leave_request_reject.html'


@method_decorator(login_required, name='dispatch')
class MyLeaveRequestsView(ListView):
    model = LeaveRequest
    template_name = 'leave_management/my_leave_requests.html'
    context_object_name = 'leave_requests'


@method_decorator(login_required, name='dispatch')
class PendingApprovalView(ListView):
    model = LeaveRequest
    template_name = 'leave_management/pending_approval.html'
    context_object_name = 'leave_requests'


# Leave Balance Views
@method_decorator(login_required, name='dispatch')
class LeaveBalanceListView(ListView):
    model = LeaveBalance
    template_name = 'leave_management/leave_balance_list.html'
    context_object_name = 'leave_balances'


@method_decorator(login_required, name='dispatch')
class EmployeeLeaveBalanceView(TemplateView):
    template_name = 'leave_management/employee_leave_balance.html'


@method_decorator(login_required, name='dispatch')
class MyLeaveBalanceView(TemplateView):
    template_name = 'leave_management/my_leave_balance.html'


@method_decorator(login_required, name='dispatch')
class LeaveBalanceUpdateView(TemplateView):
    template_name = 'leave_management/leave_balance_update.html'


# Holiday Views
@method_decorator(login_required, name='dispatch')
class HolidayListView(ListView):
    model = Holiday
    template_name = 'leave_management/holiday_list.html'
    context_object_name = 'holidays'


@method_decorator(login_required, name='dispatch')
class HolidayDetailView(DetailView):
    model = Holiday
    template_name = 'leave_management/holiday_detail.html'


@method_decorator(login_required, name='dispatch')
class HolidayCreateView(CreateView):
    model = Holiday
    template_name = 'leave_management/holiday_form.html'
    fields = ['name', 'name_en', 'date', 'holiday_type', 'is_recurring']
    success_url = reverse_lazy('leave_management:holiday_list')


@method_decorator(login_required, name='dispatch')
class HolidayUpdateView(UpdateView):
    model = Holiday
    template_name = 'leave_management/holiday_form.html'
    fields = ['name', 'name_en', 'date', 'holiday_type', 'is_recurring']
    success_url = reverse_lazy('leave_management:holiday_list')


@method_decorator(login_required, name='dispatch')
class HolidayDeleteView(DeleteView):
    model = Holiday
    template_name = 'leave_management/holiday_confirm_delete.html'
    success_url = reverse_lazy('leave_management:holiday_list')


@method_decorator(login_required, name='dispatch')
class HolidayCalendarView(TemplateView):
    template_name = 'leave_management/holiday_calendar.html'


# Leave Policy Views
@method_decorator(login_required, name='dispatch')
class LeavePolicyListView(ListView):
    model = LeavePolicy
    template_name = 'leave_management/leave_policy_list.html'
    context_object_name = 'leave_policies'


@method_decorator(login_required, name='dispatch')
class LeavePolicyDetailView(DetailView):
    model = LeavePolicy
    template_name = 'leave_management/leave_policy_detail.html'


@method_decorator(login_required, name='dispatch')
class LeavePolicyCreateView(CreateView):
    model = LeavePolicy
    template_name = 'leave_management/leave_policy_form.html'
    fields = ['name', 'description', 'effective_from', 'effective_to']
    success_url = reverse_lazy('leave_management:leave_policy_list')


@method_decorator(login_required, name='dispatch')
class LeavePolicyUpdateView(UpdateView):
    model = LeavePolicy
    template_name = 'leave_management/leave_policy_form.html'
    fields = ['name', 'description', 'effective_from', 'effective_to']
    success_url = reverse_lazy('leave_management:leave_policy_list')


@method_decorator(login_required, name='dispatch')
class LeavePolicyDeleteView(DeleteView):
    model = LeavePolicy
    template_name = 'leave_management/leave_policy_confirm_delete.html'
    success_url = reverse_lazy('leave_management:leave_policy_list')


# Additional Views
@method_decorator(login_required, name='dispatch')
class LeaveReportsView(TemplateView):
    template_name = 'leave_management/reports.html'


@method_decorator(login_required, name='dispatch')
class LeaveExportView(TemplateView):
    template_name = 'leave_management/export.html'


@method_decorator(login_required, name='dispatch')
class LeaveCalendarView(TemplateView):
    template_name = 'leave_management/calendar.html'


# API Views (stubs)
@method_decorator(login_required, name='dispatch')
class LeaveTypeAPIView(TemplateView):
    def get(self, request, *args, **kwargs):
        return JsonResponse({'message': 'Leave Type API endpoint'})


@method_decorator(login_required, name='dispatch')
class LeaveRequestAPIView(TemplateView):
    def get(self, request, *args, **kwargs):
        return JsonResponse({'message': 'Leave Request API endpoint'})


@method_decorator(login_required, name='dispatch')
class LeaveBalanceAPIView(TemplateView):
    def get(self, request, *args, **kwargs):
        return JsonResponse({'message': 'Leave Balance API endpoint'})


@method_decorator(login_required, name='dispatch')
class HolidayAPIView(TemplateView):
    def get(self, request, *args, **kwargs):
        return JsonResponse({'message': 'Holiday API endpoint'})


@method_decorator(login_required, name='dispatch')
class LeavePolicyAPIView(TemplateView):
    def get(self, request, *args, **kwargs):
        return JsonResponse({'message': 'Leave Policy API endpoint'})
