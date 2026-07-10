from core.models import Interest
from django.shortcuts import get_object_or_404


class InterestService:

    @staticmethod
    def get_all(search=None):
        queryset = Interest.objects.filter(is_active=True)

        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset.order_by('-id')


    @staticmethod
    def create(data):
        return Interest.objects.create(
            name=data.get("name"),
            is_active=True
        )


    @staticmethod
    def update(interest_id, data):
        interest = get_object_or_404(Interest, id=interest_id)

        interest.name = data.get("name")
        interest.save()

        return interest


    @staticmethod
    def delete(interest_id):
        interest = get_object_or_404(Interest, id=interest_id)

        # ✅ SOFT DELETE
        interest.is_active = False
        interest.save()