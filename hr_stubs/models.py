"""
Temporary stub models to maintain dependencies during HR app removal.
These models provide minimal functionality to prevent import errors.
They will be replaced by the new modular HR applications.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Department(models.Model):
    """Temporary stub for Department model"""
    dept_code = models.IntegerField(primary_key=True, verbose_name=_("رمز القسم"))
    dept_name = models.CharField(max_length=50, verbose_name=_("اسم القسم"))
    
    def __str__(self):
        return self.dept_name or ''
    
    class Meta:
        verbose_name = _("قسم")
        verbose_name_plural = _("الأقسام")
        db_table = 'hr_stubs_department'


class Employee(models.Model):
    """Temporary stub for Employee model"""
    emp_code = models.IntegerField(primary_key=True, verbose_name=_("رمز الموظف"))
    emp_name = models.CharField(max_length=100, verbose_name=_("اسم الموظف"))
    department = models.ForeignKey(
        Department, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_("القسم")
    )
    
    def __str__(self):
        return self.emp_name or ''
    
    class Meta:
        verbose_name = _("موظف")
        verbose_name_plural = _("الموظفين")
        db_table = 'hr_stubs_employee'


class EmployeeTask(models.Model):
    """Temporary stub for EmployeeTask model"""
    title = models.CharField(max_length=200, verbose_name=_('عنوان المهمة'))
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name='tasks', 
        verbose_name=_('الموظف')
    )
    status = models.CharField(
        max_length=20, 
        default='pending', 
        verbose_name=_('الحالة')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    
    def __str__(self):
        return f"{self.title} - {self.employee}"
    
    class Meta:
        verbose_name = _('مهمة الموظف')
        verbose_name_plural = _('مهام الموظفين')
        db_table = 'hr_stubs_employeetask'


class EmployeeLeave(models.Model):
    """Temporary stub for EmployeeLeave model"""
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name='leaves', 
        verbose_name=_('الموظف')
    )
    start_date = models.DateField(verbose_name=_('تاريخ البداية'))
    end_date = models.DateField(verbose_name=_('تاريخ النهاية'))
    status = models.CharField(
        max_length=20, 
        default='pending', 
        verbose_name=_('الحالة')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    
    def __str__(self):
        return f"{self.employee} - {self.start_date} to {self.end_date}"
    
    class Meta:
        verbose_name = _('إجازة الموظف')
        verbose_name_plural = _('إجازات الموظفين')
        db_table = 'hr_stubs_employeeleave'


class Car(models.Model):
    """Temporary stub for Car model"""
    car_code = models.IntegerField(primary_key=True, verbose_name=_("رمز السيارة"))
    car_name = models.CharField(max_length=100, verbose_name=_("اسم السيارة"))
    
    def __str__(self):
        return self.car_name or ''
    
    class Meta:
        verbose_name = _("سيارة")
        verbose_name_plural = _("السيارات")
        db_table = 'hr_stubs_car'


# Temporary TaskStep model for compatibility
class TaskStep(models.Model):
    """Temporary stub for TaskStep model"""
    task = models.ForeignKey(
        EmployeeTask, 
        on_delete=models.CASCADE, 
        related_name='steps', 
        verbose_name=_('المهمة')
    )
    title = models.CharField(max_length=200, verbose_name=_('عنوان الخطوة'))
    status = models.CharField(
        max_length=20, 
        default='pending', 
        verbose_name=_('الحالة')
    )
    
    def __str__(self):
        return f"{self.task.title} - {self.title}"
    
    class Meta:
        verbose_name = _('خطوة المهمة')
        verbose_name_plural = _('خطوات المهام')
        db_table = 'hr_stubs_taskstep'
