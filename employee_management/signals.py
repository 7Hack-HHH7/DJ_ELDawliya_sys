"""
Employee Management Signals
Handle automatic actions and notifications for employee management
"""
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .models import Employee, EmployeeNote, EmployeeDocument

User = get_user_model()


@receiver(post_save, sender=Employee)
def employee_post_save(sender, instance, created, **kwargs):
    """Handle employee creation and updates"""
    if created:
        # Create automatic welcome note for new employees
        EmployeeNote.objects.create(
            employee=instance,
            title=_("مرحباً بالموظف الجديد"),
            note_type='general',
            priority='medium',
            content=_("تم إنشاء ملف الموظف بنجاح. مرحباً بك في الشركة!"),
            note_date=instance.hire_date,
            created_by_id=1,  # System user
            requires_followup=True,
            followup_date=instance.hire_date
        )


@receiver(pre_save, sender=Employee)
def employee_pre_save(sender, instance, **kwargs):
    """Handle employee updates before saving"""
    if instance.pk:  # Existing employee
        try:
            old_instance = Employee.objects.get(pk=instance.pk)
            
            # Check for status changes
            if old_instance.employment_status != instance.employment_status:
                # Create note for status change
                status_change_note = EmployeeNote(
                    employee=instance,
                    title=_("تغيير حالة التوظيف"),
                    note_type='general',
                    priority='high',
                    content=_(f"تم تغيير حالة التوظيف من {old_instance.get_employment_status_display()} إلى {instance.get_employment_status_display()}"),
                    note_date=instance.updated_at.date() if instance.updated_at else instance.hire_date,
                    created_by_id=1,  # System user
                )
                # Note will be saved after the employee is saved
                
            # Check for department changes
            if old_instance.department != instance.department:
                dept_change_note = EmployeeNote(
                    employee=instance,
                    title=_("تغيير القسم"),
                    note_type='general',
                    priority='medium',
                    content=_(f"تم نقل الموظف من قسم {old_instance.department.dept_name} إلى قسم {instance.department.dept_name}"),
                    note_date=instance.updated_at.date() if instance.updated_at else instance.hire_date,
                    created_by_id=1,  # System user
                )
                
        except Employee.DoesNotExist:
            pass


@receiver(post_save, sender=EmployeeDocument)
def document_uploaded(sender, instance, created, **kwargs):
    """Handle document upload notifications"""
    if created:
        # Create note for document upload
        EmployeeNote.objects.create(
            employee=instance.employee,
            title=_("تم رفع وثيقة جديدة"),
            note_type='general',
            priority='low',
            content=_(f"تم رفع وثيقة جديدة: {instance.title} ({instance.get_document_type_display()})"),
            note_date=instance.document_date,
            created_by=instance.uploaded_by,
        )


@receiver(post_save, sender=EmployeeNote)
def note_followup_reminder(sender, instance, created, **kwargs):
    """Handle note follow-up reminders"""
    if created and instance.requires_followup and instance.followup_date:
        # Here you could integrate with a task queue or notification system
        # For now, we'll just mark it for follow-up
        pass


# Signal to handle user account linking
@receiver(post_save, sender=User)
def link_user_to_employee(sender, instance, created, **kwargs):
    """Automatically link user accounts to employee profiles when possible"""
    if created and instance.email:
        try:
            # Try to find an employee with matching email
            employee = Employee.objects.filter(email=instance.email, user_account__isnull=True).first()
            if employee:
                employee.user_account = instance
                employee.save()
        except Exception:
            pass  # Ignore errors in automatic linking
