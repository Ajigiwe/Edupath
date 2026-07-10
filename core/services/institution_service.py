import re
from django.core.exceptions import ValidationError
from core.models import Institution


def _validate_phone(value):
    """Validate phone number: 10 digits, optionally starting with 0."""
    if not value:
        return ''
    cleaned = re.sub(r'[\s\-\(\)]', '', str(value))
    if not re.match(r'^0?\d{9,10}$', cleaned):
        raise ValidationError("Phone number must be a valid 10-digit number")
    return cleaned


def _validate_text(value, max_length=None):
    """Sanitize and truncate text input."""
    if value is None:
        return ''
    val = str(value).strip()
    if max_length and len(val) > max_length:
        val = val[:max_length]
    return val


class InstitutionService:

    @staticmethod
    def get_all(search=None):
        queryset = Institution.objects.filter(is_active=True)

        if search:
            queryset = queryset.filter(institutionname__icontains=search)

        return queryset.order_by('-created_at')

    @staticmethod
    def create(data):
        return Institution.objects.create(
            institutionname=_validate_text(data.get("institutionname"), 100),
            institutiontype_id=data.get("institutiontype"),
            level_id=data.get("level"),
            location=_validate_text(data.get("location"), 100),
            phonenumber=_validate_phone(data.get("phonenumber")),
            is_active=True
        )

    @staticmethod
    def update(institution_id, data):
        institution = Institution.objects.get(id=institution_id)

        institution.institutionname = _validate_text(data.get("institutionname"), 100)
        institution.institutiontype_id = data.get("institutiontype")
        institution.level_id = data.get("level")
        institution.location = _validate_text(data.get("location"), 100)
        institution.phonenumber = _validate_phone(data.get("phonenumber"))

        institution.save()
        return institution

    @staticmethod
    def delete(institution_id):
        institution = Institution.objects.get(id=institution_id)
        institution.is_active = False  # ✅ soft delete
        institution.save()