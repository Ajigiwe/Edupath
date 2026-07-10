from django.shortcuts import get_object_or_404
from core.models import InstitutionType


class InstitutionTypeService:

    @staticmethod
    def get_all(search=None):
        queryset = InstitutionType.objects.filter(is_active=True)

        if search:
            queryset = queryset.filter(typename__icontains=search)  # ✅ FIXED

        return queryset.order_by('-created_at')

    @staticmethod
    def create(data):
        return InstitutionType.objects.create(
            typename=data.get("typename"),          # ✅ FIXED
            ownership_id=data.get("ownership"),     # ✅ FK
            is_active=True
        )

    @staticmethod
    def update(type_id, data):
        inst_type = get_object_or_404(InstitutionType, id=type_id)

        inst_type.typename = data.get("typename")
        inst_type.ownership_id = data.get("ownership")

        inst_type.save()
        return inst_type

    @staticmethod
    def delete(type_id):
        inst_type = get_object_or_404(InstitutionType, id=type_id)

        inst_type.is_active = False  # ✅ soft delete
        inst_type.save()