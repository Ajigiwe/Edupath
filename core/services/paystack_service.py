import uuid
import requests
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


def initialize_transaction(email, amount_ghs, plan_slug, request):
    settings = _get_settings()
    if not settings.paystack_secret_key:
        return {'status': False, 'message': 'Paystack keys not configured. Please contact admin.'}

    amount_kobo = int(amount_ghs * 100)
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
        data = resp.json()
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
        data = resp.json()
        if data.get('status') and data['data'].get('status') == 'success':
            return {
                'status': True,
                'data': data['data'],
            }
        return {'status': False, 'message': data.get('message', 'Verification failed')}
    except requests.RequestException as e:
        return {'status': False, 'message': str(e)}
