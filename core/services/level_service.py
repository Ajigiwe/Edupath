from django.shortcuts import get_object_or_404
from core.models import Level


class LevelService:

    @staticmethod
    def get_all(search=None):
        queryset = Level.objects.filter(is_active=True)

        if search:
            queryset = queryset.filter(levelsname__icontains=search)  # ✅ FIXED

        return queryset.order_by('-created_at')

    @staticmethod
    def create(data):
        return Level.objects.create(
            levelsname=data.get("levelsname"),  # ✅ FIXED
            is_active=True
        )

    @staticmethod
    def update(level_id, data):
        level = get_object_or_404(Level, id=level_id)

        level.levelsname = data.get("levelsname")
        level.save()

        return level

    @staticmethod
    def delete(level_id):
        level = get_object_or_404(Level, id=level_id)

        level.is_active = False  # ✅ soft delete
        level.save()