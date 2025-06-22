"""
Employee Management Serializers
REST API serializers for employee management
"""
from rest_framework import serializers
from .models import Department, JobTitle, Employee, EmployeeNote, EmployeeDocument


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model"""
    employee_count = serializers.ReadOnlyField()
    hierarchy_level = serializers.ReadOnlyField()
    
    class Meta:
        model = Department
        fields = [
            'dept_code', 'dept_name', 'dept_name_en', 'description',
            'parent_department', 'manager', 'employee_count', 'hierarchy_level',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['dept_code', 'created_at', 'updated_at']


class JobTitleSerializer(serializers.ModelSerializer):
    """Serializer for JobTitle model"""
    department_name = serializers.CharField(source='department.dept_name', read_only=True)
    
    class Meta:
        model = JobTitle
        fields = [
            'job_code', 'job_title', 'job_title_en', 'description',
            'department', 'department_name', 'grade_level',
            'min_salary', 'max_salary', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['job_code', 'created_at', 'updated_at']


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Employee model"""
    full_name = serializers.ReadOnlyField()
    full_name_en = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    years_of_service = serializers.ReadOnlyField()
    department_name = serializers.CharField(source='department.dept_name', read_only=True)
    job_title_name = serializers.CharField(source='job_title.job_title', read_only=True)
    manager_name = serializers.CharField(source='direct_manager.full_name', read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'emp_code', 'employee_id', 'first_name', 'middle_name', 'last_name',
            'first_name_en', 'middle_name_en', 'last_name_en', 'full_name', 'full_name_en',
            'national_id', 'passport_number', 'email', 'phone_number', 'mobile_number',
            'address', 'city', 'state', 'postal_code', 'country',
            'date_of_birth', 'age', 'gender', 'marital_status', 'nationality',
            'department', 'department_name', 'job_title', 'job_title_name',
            'direct_manager', 'manager_name', 'hire_date', 'years_of_service',
            'probation_end_date', 'termination_date', 'employment_status',
            'profile_image', 'user_account', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['emp_code', 'created_at', 'updated_at']


class EmployeeListSerializer(serializers.ModelSerializer):
    """Simplified serializer for employee lists"""
    full_name = serializers.ReadOnlyField()
    department_name = serializers.CharField(source='department.dept_name', read_only=True)
    job_title_name = serializers.CharField(source='job_title.job_title', read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'emp_code', 'employee_id', 'full_name', 'email',
            'department_name', 'job_title_name', 'employment_status',
            'hire_date', 'is_active'
        ]


class EmployeeNoteSerializer(serializers.ModelSerializer):
    """Serializer for EmployeeNote model"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = EmployeeNote
        fields = [
            'id', 'employee', 'employee_name', 'title', 'note_type', 'priority',
            'content', 'note_date', 'created_by', 'created_by_name',
            'requires_followup', 'followup_date', 'followup_completed',
            'is_confidential', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    """Serializer for EmployeeDocument model"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = EmployeeDocument
        fields = [
            'id', 'employee', 'employee_name', 'title', 'document_type',
            'description', 'document_file', 'file_size', 'document_date',
            'expiry_date', 'is_expired', 'uploaded_by', 'uploaded_by_name',
            'is_confidential', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'file_size', 'created_at', 'updated_at']


# Nested serializers for detailed views
class DepartmentDetailSerializer(DepartmentSerializer):
    """Detailed serializer for Department with related data"""
    employees = EmployeeListSerializer(many=True, read_only=True)
    job_titles = JobTitleSerializer(many=True, read_only=True)
    sub_departments = DepartmentSerializer(many=True, read_only=True)


class EmployeeDetailSerializer(EmployeeSerializer):
    """Detailed serializer for Employee with related data"""
    notes = EmployeeNoteSerializer(many=True, read_only=True)
    documents = EmployeeDocumentSerializer(many=True, read_only=True)
    subordinates = EmployeeListSerializer(many=True, read_only=True)


class JobTitleDetailSerializer(JobTitleSerializer):
    """Detailed serializer for JobTitle with related data"""
    employees = EmployeeListSerializer(many=True, read_only=True)
