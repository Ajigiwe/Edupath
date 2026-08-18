import uuid
import requests
from decimal import Decimal
from django.urls import reverse
from core.models import SiteSettings


PAYSTACK_BASE_URL = 'https://api.paystack.co'


def _get_settings():
    return SiteSettings.load()


def _headers():
    settings = _get_settings()
    return {
        'Authorization': f'Bearer {settings.paystack_secret_key}',
        'Content-Type': 'application/json',
    }


def _ghs_to_kobo(amount_ghs):
    """Convert a GHS amount (Decimal or str/number) to kobo without float rounding loss."""
    amount = Decimal(str(amount_ghs))
    return int((amount * 100).to_integral_value())


def _parse_json(resp):
    """Safely parse a requests response, handling non-JSON payloads."""
    try:
        return resp.json()
    except ValueError:
        return {'status': False, 'message': f'Invalid response from Paystack (HTTP {resp.status_code})'}


def initialize_transaction(email, amount_ghs, plan_slug, request):
    settings = _get_settings()
    if not settings.paystack_secret_key:
        return {'status': False, 'message': 'Paystack keys not configured. Please contact admin.'}

    # Basic validation before calling Paystack
    if not email or '@' not in email:
        return {'status': False, 'message': 'Invalid email address'}
    
    amount_kobo = _ghs_to_kobo(amount_ghs)
    if amount_kobo < 50:  # Paystack minimum is 50 kobo (GHS 0.50)
        return {'status': False, 'message': 'Amount too low (minimum GHS 0.50)'}

    reference = str(uuid.uuid4()).replace('-', '')[:20]

    callback_url = request.build_absolute_uri(
        reverse('paystack_callback')
    )

    payload = {
        'email': email,
        'amount': amount_kobo,
        'currency': 'GHS',
        'reference': reference,
        'callback_url': callback_url,
        'metadata': {
            'plan_slug': plan_slug,
        },
    }

    try:
        resp = requests.post(
            f'{PAYSTACK_BASE_URL}/transaction/initialize',
            json=payload,
            headers=_headers(),
            timeout=30,
        )
        if not resp.ok:
            return {'status': False, 'message': f'Paystack returned HTTP {resp.status_code}: {resp.text}'}
        data = _parse_json(resp)
        if data.get('status'):
            return {
                'status': True,
                'authorization_url': data['data']['authorization_url'],
                'reference': data['data']['reference'],
                'access_code': data['data']['access_code'],
            }
        return {'status': False, 'message': data.get('message', 'Payment initialization failed')}
    except requests.RequestException as e:
        return {'status': False, 'message': str(e)}


def verify_transaction(reference):
    settings = _get_settings()
    if not settings.paystack_secret_key:
        return {'status': False, 'message': 'Paystack keys not configured.'}

    try:
        resp = requests.get(
            f'{PAYSTACK_BASE_URL}/transaction/verify/{reference}',
            headers=_headers(),
            timeout=30,
        )
        if not resp.ok:
            return {'status': False, 'message': f'Paystack returned HTTP {resp.status_code}: {resp.text}'}
        data = _parse_json(resp)
        if data.get('status') and data['data'].get('status') == 'success':
            return {
                'status': True,
                'data': data['data'],
            }
        return {'status': False, 'message': data.get('message', 'Verification failed')}
    except requests.RequestException as e:
        return {'status': False, 'message': str(e)}
