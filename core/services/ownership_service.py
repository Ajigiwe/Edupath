from django.shortcuts import get_object_or_404
from core.models import Ownership


class OwnershipService:

    @staticmethod
    def get_all(search=None):
        queryset = Ownership.objects.filter(is_active=True)

        if search:
            queryset = queryset.filter(name__icontains=search)  # ✅ FIXED

        return queryset.order_by('-created_at')

    @staticmethod
    def create(data):
        return Ownership.objects.create(
            name=data.get("title"),   # ✅ FIXED
            is_active=True
        )

    @staticmethod
    def update(ownership_id, data):
        ownership = get_object_or_404(Ownership, id=ownership_id)

        ownership.name = data.get("title")
        ownership.save()

        return ownership

    @staticmethod
    def delete(ownership_id):
        ownership = get_object_or_404(Ownership, id=ownership_id)

        ownership.is_active = False  # ✅ soft delete
        ownership.save()