"""
Employee Management Forms
Comprehensive forms for employee management with Arabic RTL support
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .models import Department, JobTitle, Employee, EmployeeNote, EmployeeDocument

User = get_user_model()


class DepartmentForm(forms.ModelForm):
    """Form for creating and editing departments"""
    
    class Meta:
        model = Department
        fields = [
            'dept_name', 'dept_name_en', 'description', 
            'parent_department', 'manager', 'is_active'
        ]
        widgets = {
            'dept_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('اسم القسم'),
                'dir': 'rtl'
            }),
            'dept_name_en': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Department Name in English'),
                'dir': 'ltr'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('وصف القسم'),
                'dir': 'rtl'
            }),
            'parent_department': forms.Select(attrs={
                'class': 'form-control',
                'dir': 'rtl'
            }),
            'manager': forms.Select(attrs={
                'class': 'form-control',
                'dir': 'rtl'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter active employees for manager selection
        self.fields['manager'].queryset = Employee.objects.filter(is_active=True)
        # Filter active departments for parent selection
        self.fields['parent_department'].queryset = Department.objects.filter(is_active=True)


class JobTitleForm(forms.ModelForm):
    """Form for creating and editing job titles"""
    
    class Meta:
        model = JobTitle
        fields = [
            'job_title', 'job_title_en', 'description', 'department',
            'grade_level', 'min_salary', 'max_salary', 'is_active'
        ]
        widgets = {
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('المسمى الوظيفي'),
                'dir': 'rtl'
            }),
            'job_title_en': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Job Title in English'),
                'dir': 'ltr'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('وصف الوظيفة'),
                'dir': 'rtl'
            }),
            'department': forms.Select(attrs={
                'class': 'form-control',
                'dir': 'rtl'
            }),
            'grade_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 20
            }),
            'min_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': _('الحد الأدنى للراتب')
            }),
            'max_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': _('الحد الأقصى للراتب')
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        min_salary = cleaned_data.get('min_salary')
        max_salary = cleaned_data.get('max_salary')
        
        if min_salary and max_salary and min_salary > max_salary:
            raise forms.ValidationError(_('الحد الأدنى للراتب يجب أن يكون أقل من الحد الأقصى'))
        
        return cleaned_data


class EmployeeForm(forms.ModelForm):
    """Form for creating and editing employees"""
    
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'first_name', 'middle_name', 'last_name',
            'first_name_en', 'middle_name_en', 'last_name_en',
            'national_id', 'passport_number', 'email', 'phone_number', 'mobile_number',
            'address', 'city', 'state', 'postal_code', 'country',
            'date_of_birth', 'gender', 'marital_status', 'nationality',
            'department', 'job_title', 'direct_manager',
            'hire_date', 'probation_end_date', 'employment_status',
            'profile_image', 'user_account', 'is_active'
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('الرقم الوظيفي')
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('الاسم الأول'),
                'dir': 'rtl'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('الاسم الأوسط'),
                'dir': 'rtl'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('اسم العائلة'),
                'dir': 'rtl'
            }),
            'first_name_en': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('First Name in English'),
                'dir': 'ltr'
            }),
            'middle_name_en': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Middle Name in English'),
                'dir': 'ltr'
            }),
            'last_name_en': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Last Name in English'),
                'dir': 'ltr'
            }),
            'national_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('رقم الهوية الوطنية')
            }),
            'passport_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('رقم جواز السفر')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('البريد الإلكتروني'),
                'dir': 'ltr'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('رقم الهاتف')
            }),
            'mobile_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('رقم الجوال')
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('العنوان'),
                'dir': 'rtl'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('المدينة'),
                'dir': 'rtl'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('المنطقة/الولاية'),
                'dir': 'rtl'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('الرمز البريدي')
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('البلد'),
                'dir': 'rtl'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control',
                'dir': 'rtl'
            }),
            'marital_status': forms.Select(attrs={
                'class': 'form-control',
                'dir': 'rtl'
            }),
            'nationality': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('الجنسية'),
                'dir': 'rtl'
            }),
            'department': forms.Select(attrs={
                'class': 'form-control',
                'dir': 'rtl'
            }),
            'job_title': forms.Select(attrs={
                'class': 'form-control',
                'dir': 'rtl'
            }),
            'direct_manager': forms.Select(attrs={
                'class': 'form-control',
                'dir': 'rtl'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'probation_end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'employment_status': forms.Select(attrs={
                'class': 'form-control',
                'dir': 'rtl'
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'user_account': forms.Select(attrs={
                'class': 'form-control',
                'dir': 'rtl'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter active departments and job titles
        self.fields['department'].queryset = Department.objects.filter(is_active=True)
        self.fields['job_title'].queryset = JobTitle.objects.filter(is_active=True)
        self.fields['direct_manager'].queryset = Employee.objects.filter(is_active=True)
        self.fields['user_account'].queryset = User.objects.filter(employee_profile__isnull=True)


class EmployeeNoteForm(forms.ModelForm):
    """Form for creating and editing employee notes"""
    
    class Meta:
        model = EmployeeNote
        fields = [
            'employee', 'title', 'note_type', 'priority', 'content',
            'note_date', 'requires_followup', 'followup_date',
            'is_confidential'
        ]
        widgets = {
            'employee': forms.Select(attrs={
                'class': 'form-control',
                'dir': 'rtl'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('عنوان الملاحظة'),
                'dir': 'rtl'
            }),
            'note_type': forms.Select(attrs={
                'class': 'form-control',
                'dir': 'rtl'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control',
                'dir': 'rtl'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': _('محتوى الملاحظة'),
                'dir': 'rtl'
            }),
            'note_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'followup_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'requires_followup': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_confidential': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(is_active=True)


class EmployeeDocumentForm(forms.ModelForm):
    """Form for uploading employee documents"""
    
    class Meta:
        model = EmployeeDocument
        fields = [
            'employee', 'title', 'document_type', 'description',
            'document_file', 'document_date', 'expiry_date', 'is_confidential'
        ]
        widgets = {
            'employee': forms.Select(attrs={
                'class': 'form-control',
                'dir': 'rtl'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('عنوان الوثيقة'),
                'dir': 'rtl'
            }),
            'document_type': forms.Select(attrs={
                'class': 'form-control',
                'dir': 'rtl'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('وصف الوثيقة'),
                'dir': 'rtl'
            }),
            'document_file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'document_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_confidential': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(is_active=True)
