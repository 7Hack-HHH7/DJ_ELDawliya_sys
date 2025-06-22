"""
Employee Management Views
Comprehensive views for employee management functionality
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Department, JobTitle, Employee, EmployeeNote, EmployeeDocument
from .forms import (
    DepartmentForm, JobTitleForm, EmployeeForm, EmployeeNoteForm, EmployeeDocumentForm
)
from .serializers import (
    DepartmentSerializer, JobTitleSerializer, EmployeeSerializer,
    EmployeeNoteSerializer, EmployeeDocumentSerializer
)


class EmployeeManagementDashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard for employee management"""
    template_name = 'employee_management/dashboard.html'

    def get_context_data(self, **kwargs):
        from datetime import date, timedelta
        from django.db.models import Count
        from django.db import models

        context = super().get_context_data(**kwargs)

        # Basic statistics
        total_employees = Employee.objects.filter(is_active=True).count()
        total_departments = Department.objects.filter(is_active=True).count()
        total_job_titles = JobTitle.objects.filter(is_active=True).count()

        # New employees this month
        current_month = date.today().replace(day=1)
        new_employees_this_month = Employee.objects.filter(
            hire_date__gte=current_month,
            is_active=True
        ).count()

        # Recent activities (mock data for now)
        recent_activities = [
            {
                'title': 'تم إضافة موظف جديد',
                'description': 'تم تسجيل موظف جديد في قسم التطوير',
                'type': 'new',
                'icon': 'user-plus',
                'created_at': date.today() - timedelta(hours=2)
            },
            {
                'title': 'تحديث بيانات قسم',
                'description': 'تم تحديث بيانات قسم الموارد البشرية',
                'type': 'update',
                'icon': 'edit',
                'created_at': date.today() - timedelta(hours=5)
            },
            {
                'title': 'إضافة وظيفة جديدة',
                'description': 'تم إضافة مسمى وظيفي جديد: مطور أول',
                'type': 'new',
                'icon': 'briefcase',
                'created_at': date.today() - timedelta(days=1)
            }
        ]

        # Departments with employee count
        departments = Department.objects.filter(is_active=True).annotate(
            employee_count=Count('employees', filter=models.Q(employees__is_active=True))
        ).order_by('-employee_count')[:5]

        context.update({
            'total_employees': total_employees,
            'total_departments': total_departments,
            'total_job_titles': total_job_titles,
            'new_employees_this_month': new_employees_this_month,
            'recent_hires': Employee.objects.filter(is_active=True).order_by('-hire_date')[:5],
            'pending_notes': EmployeeNote.objects.filter(
                requires_followup=True,
                followup_completed=False
            ).count(),
            'expiring_documents': EmployeeDocument.objects.filter(
                expiry_date__isnull=False,
                is_active=True
            ).order_by('expiry_date')[:5],
            'recent_activities': recent_activities,
            'departments': departments,
        })
        return context


# Department Views
class DepartmentListView(LoginRequiredMixin, ListView):
    """List all departments"""
    model = Department
    template_name = 'employee_management/department_list.html'
    context_object_name = 'departments'
    paginate_by = 20

    def get_queryset(self):
        queryset = Department.objects.filter(is_active=True)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(dept_name__icontains=search) |
                Q(dept_name_en__icontains=search) |
                Q(description__icontains=search)
            )
        return queryset.order_by('dept_name')


class DepartmentDetailView(LoginRequiredMixin, DetailView):
    """Department detail view"""
    model = Department
    template_name = 'employee_management/department_detail.html'
    context_object_name = 'department'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = self.object.employees.filter(is_active=True)
        context['job_titles'] = self.object.job_titles.filter(is_active=True)
        return context


class DepartmentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Create new department"""
    model = Department
    form_class = DepartmentForm
    template_name = 'employee_management/department_form.html'
    permission_required = 'employee_management.add_department'
    success_url = reverse_lazy('employee_management:department_list')

    def form_valid(self, form):
        messages.success(self.request, _('تم إنشاء القسم بنجاح'))
        return super().form_valid(form)


class DepartmentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Update department"""
    model = Department
    form_class = DepartmentForm
    template_name = 'employee_management/department_form.html'
    permission_required = 'employee_management.change_department'

    def form_valid(self, form):
        messages.success(self.request, _('تم تحديث القسم بنجاح'))
        return super().form_valid(form)


class DepartmentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Delete department"""
    model = Department
    template_name = 'employee_management/department_confirm_delete.html'
    permission_required = 'employee_management.delete_department'
    success_url = reverse_lazy('employee_management:department_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, _('تم حذف القسم بنجاح'))
        return super().delete(request, *args, **kwargs)


# Job Title Views
class JobTitleListView(LoginRequiredMixin, ListView):
    """List all job titles"""
    model = JobTitle
    template_name = 'employee_management/job_list.html'
    context_object_name = 'job_titles'
    paginate_by = 20

    def get_queryset(self):
        queryset = JobTitle.objects.filter(is_active=True).select_related('department')
        search = self.request.GET.get('search')
        department = self.request.GET.get('department')

        if search:
            queryset = queryset.filter(
                Q(job_title__icontains=search) |
                Q(job_title_en__icontains=search) |
                Q(description__icontains=search)
            )

        if department:
            queryset = queryset.filter(department_id=department)

        return queryset.order_by('department__dept_name', 'grade_level', 'job_title')


class JobTitleDetailView(LoginRequiredMixin, DetailView):
    """Job title detail view"""
    model = JobTitle
    template_name = 'employee_management/job_detail.html'
    context_object_name = 'job_title'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = self.object.employees.filter(is_active=True)
        return context


class JobTitleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Create new job title"""
    model = JobTitle
    form_class = JobTitleForm
    template_name = 'employee_management/job_form.html'
    permission_required = 'employee_management.add_jobtitle'
    success_url = reverse_lazy('employee_management:job_list')

    def form_valid(self, form):
        messages.success(self.request, _('تم إنشاء الوظيفة بنجاح'))
        return super().form_valid(form)


class JobTitleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Update job title"""
    model = JobTitle
    form_class = JobTitleForm
    template_name = 'employee_management/job_form.html'
    permission_required = 'employee_management.change_jobtitle'

    def form_valid(self, form):
        messages.success(self.request, _('تم تحديث الوظيفة بنجاح'))
        return super().form_valid(form)


class JobTitleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Delete job title"""
    model = JobTitle
    template_name = 'employee_management/job_confirm_delete.html'
    permission_required = 'employee_management.delete_jobtitle'
    success_url = reverse_lazy('employee_management:job_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, _('تم حذف الوظيفة بنجاح'))
        return super().delete(request, *args, **kwargs)


# Employee Views
class EmployeeListView(LoginRequiredMixin, ListView):
    """List all employees"""
    model = Employee
    template_name = 'employee_management/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 20

    def get_queryset(self):
        queryset = Employee.objects.filter(is_active=True).select_related('department', 'job_title')
        search = self.request.GET.get('search')
        department = self.request.GET.get('department')

        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(email__icontains=search)
            )

        if department:
            queryset = queryset.filter(department_id=department)

        return queryset.order_by('first_name', 'last_name')


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    """Employee detail view"""
    model = Employee
    template_name = 'employee_management/employee_detail.html'
    context_object_name = 'employee'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notes'] = self.object.notes.filter(is_active=True).order_by('-created_at')[:5]
        context['documents'] = self.object.documents.filter(is_active=True).order_by('-created_at')[:5]
        return context


class EmployeeCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Create new employee"""
    model = Employee
    form_class = EmployeeForm
    template_name = 'employee_management/employee_form.html'
    permission_required = 'employee_management.add_employee'
    success_url = reverse_lazy('employee_management:employee_list')

    def form_valid(self, form):
        messages.success(self.request, _('تم إنشاء الموظف بنجاح'))
        return super().form_valid(form)


class EmployeeUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Update employee"""
    model = Employee
    form_class = EmployeeForm
    template_name = 'employee_management/employee_form.html'
    permission_required = 'employee_management.change_employee'

    def form_valid(self, form):
        messages.success(self.request, _('تم تحديث الموظف بنجاح'))
        return super().form_valid(form)


class EmployeeDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Delete employee"""
    model = Employee
    template_name = 'employee_management/employee_confirm_delete.html'
    permission_required = 'employee_management.delete_employee'
    success_url = reverse_lazy('employee_management:employee_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, _('تم حذف الموظف بنجاح'))
        return super().delete(request, *args, **kwargs)


# Employee Note Views
class EmployeeNoteListView(LoginRequiredMixin, ListView):
    """List employee notes"""
    model = EmployeeNote
    template_name = 'employee_management/note_list.html'
    context_object_name = 'notes'
    paginate_by = 20


class EmployeeNoteDetailView(LoginRequiredMixin, DetailView):
    """Employee note detail view"""
    model = EmployeeNote
    template_name = 'employee_management/note_detail.html'
    context_object_name = 'note'


class EmployeeNoteCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Create employee note"""
    model = EmployeeNote
    form_class = EmployeeNoteForm
    template_name = 'employee_management/note_form.html'
    permission_required = 'employee_management.add_employeenote'
    success_url = reverse_lazy('employee_management:note_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, _('تم إنشاء الملاحظة بنجاح'))
        return super().form_valid(form)


class EmployeeNoteUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Update employee note"""
    model = EmployeeNote
    form_class = EmployeeNoteForm
    template_name = 'employee_management/note_form.html'
    permission_required = 'employee_management.change_employeenote'

    def form_valid(self, form):
        messages.success(self.request, _('تم تحديث الملاحظة بنجاح'))
        return super().form_valid(form)


class EmployeeNoteDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Delete employee note"""
    model = EmployeeNote
    template_name = 'employee_management/note_confirm_delete.html'
    permission_required = 'employee_management.delete_employeenote'
    success_url = reverse_lazy('employee_management:note_list')


# Employee Document Views
class EmployeeDocumentListView(LoginRequiredMixin, ListView):
    """List employee documents"""
    model = EmployeeDocument
    template_name = 'employee_management/document_list.html'
    context_object_name = 'documents'
    paginate_by = 20


class EmployeeDocumentDetailView(LoginRequiredMixin, DetailView):
    """Employee document detail view"""
    model = EmployeeDocument
    template_name = 'employee_management/document_detail.html'
    context_object_name = 'document'


class EmployeeDocumentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Create employee document"""
    model = EmployeeDocument
    form_class = EmployeeDocumentForm
    template_name = 'employee_management/document_form.html'
    permission_required = 'employee_management.add_employeedocument'
    success_url = reverse_lazy('employee_management:document_list')

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        messages.success(self.request, _('تم رفع الوثيقة بنجاح'))
        return super().form_valid(form)


class EmployeeDocumentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Update employee document"""
    model = EmployeeDocument
    form_class = EmployeeDocumentForm
    template_name = 'employee_management/document_form.html'
    permission_required = 'employee_management.change_employeedocument'

    def form_valid(self, form):
        messages.success(self.request, _('تم تحديث الوثيقة بنجاح'))
        return super().form_valid(form)


class EmployeeDocumentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Delete employee document"""
    model = EmployeeDocument
    template_name = 'employee_management/document_confirm_delete.html'
    permission_required = 'employee_management.delete_employeedocument'
    success_url = reverse_lazy('employee_management:document_list')


class EmployeeDocumentDownloadView(LoginRequiredMixin, DetailView):
    """Download employee document"""
    model = EmployeeDocument

    def get(self, request, *args, **kwargs):
        # Implement file download logic
        return redirect('employee_management:document_list')


# Additional Views
class EmployeeProfileView(LoginRequiredMixin, DetailView):
    """Employee profile view"""
    model = Employee
    template_name = 'employee_management/employee_profile.html'
    context_object_name = 'employee'


class EmployeeReportsView(LoginRequiredMixin, TemplateView):
    """Employee reports view"""
    template_name = 'employee_management/reports.html'


class EmployeeExportView(LoginRequiredMixin, TemplateView):
    """Employee export view"""
    template_name = 'employee_management/export.html'


class EmployeeSearchView(LoginRequiredMixin, TemplateView):
    """Employee search view"""
    template_name = 'employee_management/search.html'


# API Views
class DepartmentAPIView(LoginRequiredMixin, TemplateView):
    """Department API view"""
    def get(self, request, *args, **kwargs):
        return JsonResponse({'message': 'Department API endpoint'})


class JobTitleAPIView(LoginRequiredMixin, TemplateView):
    """Job Title API view"""
    def get(self, request, *args, **kwargs):
        return JsonResponse({'message': 'Job Title API endpoint'})


class EmployeeAPIView(LoginRequiredMixin, TemplateView):
    """Employee API view"""
    def get(self, request, *args, **kwargs):
        return JsonResponse({'message': 'Employee API endpoint'})


class EmployeeDetailAPIView(LoginRequiredMixin, TemplateView):
    """Employee Detail API view"""
    def get(self, request, *args, **kwargs):
        return JsonResponse({'message': 'Employee Detail API endpoint'})


class EmployeeNoteAPIView(LoginRequiredMixin, TemplateView):
    """Employee Note API view"""
    def get(self, request, *args, **kwargs):
        return JsonResponse({'message': 'Employee Note API endpoint'})


class EmployeeDocumentAPIView(LoginRequiredMixin, TemplateView):
    """Employee Document API view"""
    def get(self, request, *args, **kwargs):
        return JsonResponse({'message': 'Employee Document API endpoint'})
