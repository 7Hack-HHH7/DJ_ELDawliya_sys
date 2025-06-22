from django.apps import AppConfig


class PayrollManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payroll_management'
    verbose_name = 'إدارة الرواتب'  # Payroll Management in Arabic

    def ready(self):
        import payroll_management.signals
