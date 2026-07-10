from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.models import SiteSettings


@login_required(login_url='login')
def site_settings_view(request):
    settings_obj = SiteSettings.load()

    if request.method == 'POST':
        settings_obj.paystack_public_key = request.POST.get('paystack_public_key', '').strip()
        settings_obj.paystack_secret_key = request.POST.get('paystack_secret_key', '').strip()
        settings_obj.save()
        messages.success(request, 'Paystack keys updated successfully.')
        return redirect('site_settings')

    return render(request, 'admin/settings.html', {
        'settings': settings_obj,
    })
