from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.decorators import staff_required
from core.models import SiteSettings


@staff_required
@login_required
def site_settings_view(request):
    settings_obj = SiteSettings.load()

    if request.method == 'POST':
        settings_obj.paystack_public_key = request.POST.get('paystack_public_key', '').strip()
        new_secret = request.POST.get('paystack_secret_key', '').strip()
        if new_secret:
            settings_obj.paystack_secret_key = new_secret
        settings_obj.save()
        messages.success(request, 'Paystack keys updated successfully.')
        return redirect('site_settings')

    return render(request, 'admin/settings.html', {
        'settings': settings_obj,
        'has_secret': bool(settings_obj.paystack_secret_key),
    })
