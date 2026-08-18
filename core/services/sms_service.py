import requests
import logging
from django.conf import settings
from core.models import SiteSettings

logger = logging.getLogger(__name__)


def send_sms(phone, message):
    """Send SMS using configured provider. Returns (success: bool, error_message: str)."""
    site = SiteSettings.load()
    provider = site.sms_provider or 'custom'
    api_key = site.sms_api_key
    sender_id = site.sms_sender_id or 'EduPath'

    if not api_key:
        logger.warning("SMS API key not configured")
        return False, "SMS not configured"

    # Format phone: ensure international format
    phone = _format_phone_ghana(phone)

    try:
        if provider == 'termii':
            return _send_termii(phone, message, api_key, sender_id)
        elif provider == 'twilio':
            return _send_twilio(phone, message, api_key, sender_id)
        else:
            return _send_custom(phone, message, api_key, sender_id, site.sms_api_url)
    except Exception as e:
        logger.exception("SMS send failed")
        return False, str(e)


def _format_phone_ghana(phone):
    """Ensure phone is in international format for Ghana (+233...)."""
    digits = ''.join(ch for ch in phone if ch.isdigit())
    if digits.startswith('233'):
        return '+' + digits
    if digits.startswith('0'):
        return '+233' + digits[1:]
    if len(digits) == 10:  # local without leading 0
        return '+233' + digits
    return '+' + digits


def _send_termii(phone, message, api_key, sender_id):
    """Send via Termii API."""
    url = "https://api.ng.termii.com/api/sms/send"
    payload = {
        "api_key": api_key,
        "to": phone,
        "from": sender_id[:11],  # Termii sender ID max 11 chars
        "sms": message,
        "type": "plain",
        "channel": "generic",
    }
    resp = requests.post(url, json=payload, timeout=15)
    if resp.ok:
        data = resp.json()
        if data.get('code') == 'ok':
            return True, None
    return False, resp.text


def _send_twilio(phone, message, api_key, sender_id):
    """Send via Twilio. api_key should be 'account_sid:auth_token'."""
    if ':' not in api_key:
        return False, "Twilio API key must be 'account_sid:auth_token'"
    account_sid, auth_token = api_key.split(':', 1)
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    data = {
        "To": phone,
        "From": sender_id,
        "Body": message,
    }
    resp = requests.post(url, data=data, auth=(account_sid, auth_token), timeout=15)
    if resp.ok:
        return True, None
    return False, resp.text


def _send_custom(phone, message, api_key, sender_id, api_url):
    """Send via custom HTTP API."""
    if not api_url:
        return False, "Custom API URL not configured"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "phone": phone,
        "message": message,
        "sender_id": sender_id,
    }
    resp = requests.post(api_url, json=payload, headers=headers, timeout=15)
    if resp.ok:
        return True, None
    return False, resp.text


def send_otp_sms(phone, otp):
    """Send OTP via SMS."""
    message = f"Your EduPath verification code is {otp}. Valid for 5 minutes. Do not share."
    return send_sms(phone, message)