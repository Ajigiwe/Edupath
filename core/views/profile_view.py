from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from core.models import UserSubscription, Payment, UserActivity, SubscriptionPlan


@login_required(login_url='login')
def profile_view(request):
    tab = request.GET.get('tab', 'profile')
    user = request.user

    try:
        sub = user.subscription
    except Exception:
        sub = None

    payments = Payment.objects.filter(user=user)[:20]
    activities = UserActivity.objects.filter(user=user)[:15]
    plans = SubscriptionPlan.objects.filter(is_active=True)

    context = {
        'active_tab': tab,
        'sub': sub,
        'payments': payments,
        'activities': activities,
        'plans': plans,
    }
    return render(request, 'profile.html', context)


@login_required(login_url='login')
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()

        if email and email != user.email:
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, 'This email is already in use.')
                return redirect('profile')
            user.email = email

        user.first_name = first_name
        user.last_name = last_name
        user.save()

        UserActivity.objects.create(
            user=user,
            activity_type='OTHER',
            description='Updated profile details',
        )

        messages.success(request, 'Profile updated successfully.')
    return redirect('profile')


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        user = request.user
        current = request.POST.get('current_password', '')
        new_pass = request.POST.get('new_password', '')
        confirm = request.POST.get('confirm_password', '')

        if not user.check_password(current):
            messages.error(request, 'Current password is incorrect.')
            return redirect('profile?tab=security')

        if len(new_pass) < 6:
            messages.error(request, 'New password must be at least 6 characters.')
            return redirect('profile?tab=security')

        if new_pass != confirm:
            messages.error(request, 'New passwords do not match.')
            return redirect('profile?tab=security')

        user.set_password(new_pass)
        user.save()
        update_session_auth_hash(request, user)

        UserActivity.objects.create(
            user=user,
            activity_type='OTHER',
            description='Changed password',
        )

        messages.success(request, 'Password changed successfully.')
    return redirect('profile')
