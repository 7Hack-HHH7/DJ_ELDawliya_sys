"""
Payroll Management URL Configuration
URL patterns for payroll management views
"""
from django.urls import path, include
from . import views

app_name = 'payroll_management'

# Salary Component URLs
component_patterns = [
    path('', views.SalaryComponentListView.as_view(), name='component_list'),
    path('create/', views.SalaryComponentCreateView.as_view(), name='component_create'),
    path('<int:pk>/', views.SalaryComponentDetailView.as_view(), name='component_detail'),
    path('<int:pk>/edit/', views.SalaryComponentUpdateView.as_view(), name='component_edit'),
    path('<int:pk>/delete/', views.SalaryComponentDeleteView.as_view(), name='component_delete'),
]

# Salary Structure URLs
structure_patterns = [
    path('', views.EmployeeSalaryStructureListView.as_view(), name='structure_list'),
    path('create/', views.EmployeeSalaryStructureCreateView.as_view(), name='structure_create'),
    path('<uuid:pk>/', views.EmployeeSalaryStructureDetailView.as_view(), name='structure_detail'),
    path('<uuid:pk>/edit/', views.EmployeeSalaryStructureUpdateView.as_view(), name='structure_edit'),
    path('<uuid:pk>/delete/', views.EmployeeSalaryStructureDeleteView.as_view(), name='structure_delete'),
    path('employee/<uuid:employee_id>/', views.EmployeeSalaryStructureView.as_view(), name='employee_structure'),
]

# Payroll Period URLs
period_patterns = [
    path('', views.PayrollPeriodListView.as_view(), name='period_list'),
    path('create/', views.PayrollPeriodCreateView.as_view(), name='period_create'),
    path('<int:pk>/', views.PayrollPeriodDetailView.as_view(), name='period_detail'),
    path('<int:pk>/edit/', views.PayrollPeriodUpdateView.as_view(), name='period_edit'),
    path('<int:pk>/calculate/', views.PayrollPeriodCalculateView.as_view(), name='period_calculate'),
    path('<int:pk>/approve/', views.PayrollPeriodApproveView.as_view(), name='period_approve'),
    path('<int:pk>/close/', views.PayrollPeriodCloseView.as_view(), name='period_close'),
    path('<int:pk>/reopen/', views.PayrollPeriodReopenView.as_view(), name='period_reopen'),
]

# Payroll Transaction URLs
transaction_patterns = [
    path('', views.PayrollTransactionListView.as_view(), name='transaction_list'),
    path('create/', views.PayrollTransactionCreateView.as_view(), name='transaction_create'),
    path('<uuid:pk>/', views.PayrollTransactionDetailView.as_view(), name='transaction_detail'),
    path('<uuid:pk>/edit/', views.PayrollTransactionUpdateView.as_view(), name='transaction_edit'),
    path('<uuid:pk>/approve/', views.PayrollTransactionApproveView.as_view(), name='transaction_approve'),
    path('<uuid:pk>/delete/', views.PayrollTransactionDeleteView.as_view(), name='transaction_delete'),
    path('bulk-create/', views.BulkTransactionCreateView.as_view(), name='bulk_transaction_create'),
]

# Payslip URLs
payslip_patterns = [
    path('', views.EmployeePayslipListView.as_view(), name='payslip_list'),
    path('<uuid:pk>/', views.EmployeePayslipDetailView.as_view(), name='payslip_detail'),
    path('<uuid:pk>/edit/', views.EmployeePayslipUpdateView.as_view(), name='payslip_edit'),
    path('<uuid:pk>/approve/', views.EmployeePayslipApproveView.as_view(), name='payslip_approve'),
    path('<uuid:pk>/print/', views.EmployeePayslipPrintView.as_view(), name='payslip_print'),
    path('<uuid:pk>/email/', views.EmployeePayslipEmailView.as_view(), name='payslip_email'),
    path('my-payslips/', views.MyPayslipsView.as_view(), name='my_payslips'),
    path('generate/', views.GeneratePayslipsView.as_view(), name='generate_payslips'),
]

# Tax Configuration URLs
tax_patterns = [
    path('', views.TaxConfigurationListView.as_view(), name='tax_list'),
    path('create/', views.TaxConfigurationCreateView.as_view(), name='tax_create'),
    path('<uuid:pk>/', views.TaxConfigurationDetailView.as_view(), name='tax_detail'),
    path('<uuid:pk>/edit/', views.TaxConfigurationUpdateView.as_view(), name='tax_edit'),
    path('<uuid:pk>/delete/', views.TaxConfigurationDeleteView.as_view(), name='tax_delete'),
]

# Report URLs
report_patterns = [
    path('', views.PayrollReportListView.as_view(), name='report_list'),
    path('create/', views.PayrollReportCreateView.as_view(), name='report_create'),
    path('<uuid:pk>/', views.PayrollReportDetailView.as_view(), name='report_detail'),
    path('<uuid:pk>/download/', views.PayrollReportDownloadView.as_view(), name='report_download'),
    path('<uuid:pk>/delete/', views.PayrollReportDeleteView.as_view(), name='report_delete'),
    path('payroll-summary/', views.PayrollSummaryReportView.as_view(), name='payroll_summary'),
    path('tax-report/', views.TaxReportView.as_view(), name='tax_report'),
    path('bank-transfer/', views.BankTransferReportView.as_view(), name='bank_transfer'),
]

# API URLs
api_patterns = [
    path('components/', views.SalaryComponentAPIView.as_view(), name='api_components'),
    path('structures/', views.EmployeeSalaryStructureAPIView.as_view(), name='api_structures'),
    path('periods/', views.PayrollPeriodAPIView.as_view(), name='api_periods'),
    path('transactions/', views.PayrollTransactionAPIView.as_view(), name='api_transactions'),
    path('payslips/', views.EmployeePayslipAPIView.as_view(), name='api_payslips'),
    path('tax-configs/', views.TaxConfigurationAPIView.as_view(), name='api_tax_configs'),
    path('reports/', views.PayrollReportAPIView.as_view(), name='api_reports'),
]

# Main URL patterns
urlpatterns = [
    # Dashboard
    path('', views.PayrollManagementDashboardView.as_view(), name='dashboard'),
    
    # Salary Component management
    path('components/', include(component_patterns)),
    
    # Salary Structure management
    path('structures/', include(structure_patterns)),
    
    # Payroll Period management
    path('periods/', include(period_patterns)),
    
    # Transaction management
    path('transactions/', include(transaction_patterns)),
    
    # Payslip management
    path('payslips/', include(payslip_patterns)),
    
    # Tax Configuration
    path('tax-configs/', include(tax_patterns)),
    
    # Report management
    path('reports/', include(report_patterns)),
    
    # API endpoints
    path('api/', include(api_patterns)),
    
    # Quick actions
    path('calculate-payroll/', views.QuickCalculatePayrollView.as_view(), name='quick_calculate'),
    path('salary-items/', views.SalaryItemListView.as_view(), name='salary_item_list'),
]
