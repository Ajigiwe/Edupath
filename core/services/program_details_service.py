import re
from django.core.exceptions import ValidationError
from core.models import ProgramDetails


def _validate_integer(value, field_name, min_val=None, max_val=None):
    """Validate and return an integer value, raising ValidationError if invalid."""
    if value is None or str(value).strip() == '':
        return None
    try:
        val = int(value)
        if min_val is not None and val < min_val:
            raise ValidationError(f"{field_name} must be at least {min_val}")
        if max_val is not None and val > max_val:
            raise ValidationError(f"{field_name} must be at most {max_val}")
        return val
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a valid number")


def _validate_text(value, field_name, max_length=None):
    """Sanitize text input."""
    if value is None:
        return ''
    val = str(value).strip()
    if max_length and len(val) > max_length:
        val = val[:max_length]
    return val


class ProgramDetailsService:

    @staticmethod
    def get_all(search=None):
        queryset = ProgramDetails.objects.select_related(
            'program', 'institution'
        ).filter(is_active=True)

        if search:
            queryset = queryset.filter(
                program__programname__icontains=search
            )

        return queryset.order_by('-created_at')


    @staticmethod
    def create(data):
        cutoff = _validate_integer(data.get("cutoff_point"), "Cutoff point", 0, 100)
        job_score = _validate_integer(data.get("job_score"), "Job score", 0, 100)

        return ProgramDetails.objects.create(
            program_id=data.get("program"),
            institution_id=data.get("institution"),
            cutoff_point=cutoff,
            description=_validate_text(data.get("description"), "Description"),
            career_path=_validate_text(data.get("career_path"), "Career path"),
            job_score=job_score,
            job_chances=data.get("job_chances"),
        )


    @staticmethod
    def update(detail_id, data):
        detail = ProgramDetails.objects.get(id=detail_id)
        cutoff = _validate_integer(data.get("cutoff_point"), "Cutoff point", 0, 100)
        job_score = _validate_integer(data.get("job_score"), "Job score", 0, 100)

        detail.program_id = data.get("program")
        detail.institution_id = data.get("institution")
        detail.cutoff_point = cutoff
        detail.description = _validate_text(data.get("description"), "Description")
        detail.career_path = _validate_text(data.get("career_path"), "Career path")
        detail.job_score = job_score
        detail.job_chances = data.get("job_chances")

        detail.save()
        return detail


    @staticmethod
    def delete(detail_id):
        detail = ProgramDetails.objects.get(id=detail_id)
        detail.is_active = False
        detail.save()
