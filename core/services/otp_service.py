import secrets
from datetime import timedelta
from django.utils import timezone


OTP_TTL_MINUTES = 5


def generate_otp():
    """Generate a 6-digit OTP."""
    return f"{secrets.randbelow(1000000):06d}"


def build_pending(phone, otp):
    """Build the session payload for a pending OTP verification."""
    return {
        'phone': phone,
        'otp': otp,
        'expires': (timezone.now() + timedelta(minutes=OTP_TTL_MINUTES)).isoformat(),
    }


def verify_pending(payload, submitted_otp):
    """Return (valid: bool, expired: bool)."""
    if not payload:
        return False, False
    from datetime import datetime
    from django.utils.dateparse import parse_datetime
    expires = parse_datetime(payload.get('expires', ''))
    if expires and timezone.now() > expires:
        return False, True
    if submitted_otp and submitted_otp == payload.get('otp'):
        return True, False
    return False, False