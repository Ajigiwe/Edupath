# core/services/schoollevel_service.py

from core.models import SchoolLevel

class SchoolLevelService:

    @staticmethod
    def get_all(search=None):
        queryset = SchoolLevel.objects.filter(is_active=True)

        if search:
            queryset = queryset.filter(level_number__icontains=search)

        return queryset.order_by('-id')

    @staticmethod
    def create(data):
        return SchoolLevel.objects.create(
            level_number=data.get("level_number"),
            is_active=True
        )

    @staticmethod
    def update(level_id, data):
        level = SchoolLevel.objects.get(id=level_id)

        level.level_number = data.get("level_number")
        level.save()

        return level

    @staticmethod
    def delete(level_id):
        level = SchoolLevel.objects.get(id=level_id)
        level.is_active = False
        level.save()