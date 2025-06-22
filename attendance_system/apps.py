from django.apps import AppConfig


class AttendanceSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'attendance_system'
    verbose_name = 'نظام الحضور والانصراف'  # Attendance System in Arabic

    def ready(self):
        import attendance_system.signals
