from django.contrib import admin
from .models import Department, Employee, EmployeeTask, EmployeeLeave, Car, TaskStep

# Register stub models for admin interface
admin.site.register(Department)
admin.site.register(Employee)
admin.site.register(EmployeeTask)
admin.site.register(EmployeeLeave)
admin.site.register(Car)
admin.site.register(TaskStep)
