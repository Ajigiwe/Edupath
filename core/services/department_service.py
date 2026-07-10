# core/services/department_service.py

from core.models import Department

class DepartmentService:

    @staticmethod
    def get_all(search=None):
        queryset = Department.objects.filter(is_active=True).select_related('institution')

        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset.order_by('-id')

    @staticmethod
    def create(data):
        return Department.objects.create(
            name=data.get("name"),
            institution_id=data.get("institution"),
            is_active=True
        )

    @staticmethod
    def update(department_id, data):
        dept = Department.objects.get(id=department_id)

        dept.name = data.get("name")
        dept.institution_id = data.get("institution")
        dept.save()

        return dept

    @staticmethod
    def delete(department_id):
        dept = Department.objects.get(id=department_id)
        dept.is_active = False
        dept.save()