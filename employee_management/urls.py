"""
Employee Management URL Configuration
URL patterns for employee management views
"""
from django.urls import path, include
from . import views

app_name = 'employee_management'

# Department URLs
department_patterns = [
    path('', views.DepartmentListView.as_view(), name='department_list'),
    path('create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('<int:pk>/', views.DepartmentDetailView.as_view(), name='department_detail'),
    path('<int:pk>/edit/', views.DepartmentUpdateView.as_view(), name='department_edit'),
    path('<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),
]

# Job Title URLs
job_patterns = [
    path('', views.JobTitleListView.as_view(), name='job_list'),
    path('create/', views.JobTitleCreateView.as_view(), name='job_create'),
    path('<int:pk>/', views.JobTitleDetailView.as_view(), name='job_detail'),
    path('<int:pk>/edit/', views.JobTitleUpdateView.as_view(), name='job_edit'),
    path('<int:pk>/delete/', views.JobTitleDeleteView.as_view(), name='job_delete'),
]

# Employee URLs
employee_patterns = [
    path('', views.EmployeeListView.as_view(), name='employee_list'),
    path('create/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('<int:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('<int:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee_edit'),
    path('<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),
    path('<int:pk>/notes/', views.EmployeeNoteListView.as_view(), name='employee_notes'),
    path('<int:pk>/documents/', views.EmployeeDocumentListView.as_view(), name='employee_documents'),
    path('<int:pk>/profile/', views.EmployeeProfileView.as_view(), name='employee_profile'),
]

# Employee Note URLs
note_patterns = [
    path('', views.EmployeeNoteListView.as_view(), name='note_list'),
    path('create/', views.EmployeeNoteCreateView.as_view(), name='note_create'),
    path('<uuid:pk>/', views.EmployeeNoteDetailView.as_view(), name='note_detail'),
    path('<uuid:pk>/edit/', views.EmployeeNoteUpdateView.as_view(), name='note_edit'),
    path('<uuid:pk>/delete/', views.EmployeeNoteDeleteView.as_view(), name='note_delete'),
    path('employee/<int:employee_pk>/', views.EmployeeNoteListView.as_view(), name='employee_note_list'),
    path('employee/<int:employee_pk>/create/', views.EmployeeNoteCreateView.as_view(), name='employee_note_create'),
]

# Employee Document URLs
document_patterns = [
    path('', views.EmployeeDocumentListView.as_view(), name='document_list'),
    path('create/', views.EmployeeDocumentCreateView.as_view(), name='document_create'),
    path('<uuid:pk>/', views.EmployeeDocumentDetailView.as_view(), name='document_detail'),
    path('<uuid:pk>/edit/', views.EmployeeDocumentUpdateView.as_view(), name='document_edit'),
    path('<uuid:pk>/delete/', views.EmployeeDocumentDeleteView.as_view(), name='document_delete'),
    path('<uuid:pk>/download/', views.EmployeeDocumentDownloadView.as_view(), name='document_download'),
    path('employee/<int:employee_pk>/', views.EmployeeDocumentListView.as_view(), name='employee_document_list'),
    path('employee/<int:employee_pk>/upload/', views.EmployeeDocumentCreateView.as_view(), name='employee_document_upload'),
]

# API URLs
api_patterns = [
    path('departments/', views.DepartmentAPIView.as_view(), name='api_departments'),
    path('jobs/', views.JobTitleAPIView.as_view(), name='api_jobs'),
    path('employees/', views.EmployeeAPIView.as_view(), name='api_employees'),
    path('employees/<int:pk>/', views.EmployeeDetailAPIView.as_view(), name='api_employee_detail'),
    path('notes/', views.EmployeeNoteAPIView.as_view(), name='api_notes'),
    path('documents/', views.EmployeeDocumentAPIView.as_view(), name='api_documents'),
]

# Main URL patterns
urlpatterns = [
    # Dashboard
    path('', views.EmployeeManagementDashboardView.as_view(), name='dashboard'),
    
    # Department management
    path('departments/', include(department_patterns)),
    
    # Job title management
    path('jobs/', include(job_patterns)),
    
    # Employee management
    path('employees/', include(employee_patterns)),
    
    # Note management
    path('notes/', include(note_patterns)),
    
    # Document management
    path('documents/', include(document_patterns)),
    
    # API endpoints
    path('api/', include(api_patterns)),
    
    # Reports
    path('reports/', views.EmployeeReportsView.as_view(), name='reports'),
    path('reports/export/', views.EmployeeExportView.as_view(), name='export'),
    
    # Search
    path('search/', views.EmployeeSearchView.as_view(), name='search'),
]
