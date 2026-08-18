from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from core.models import UserSubscription, Payment, UserActivity, SubscriptionPlan, UserProfile


@login_required(login_url='login')
def profile_view(request):
    tab = request.GET.get('tab', 'profile')
    user = request.user

    try:
        sub = user.subscription
    except Exception:
        sub = None

    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = None

    payments = Payment.objects.filter(user=user)[:20]
    activities = UserActivity.objects.filter(user=user)[:15]
    plans = SubscriptionPlan.objects.filter(is_active=True)

    context = {
        'active_tab': tab,
        'sub': sub,
        'profile': profile,
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
        phone = request.POST.get('phone', '').strip()

        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            profile = None

        if email and email != user.email:
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, 'This email is already in use.')
                return redirect('profile')
            user.email = email

        if profile and phone and phone != profile.phone:
            from core.views.auth_view import _normalize_phone
            phone = _normalize_phone(phone)
            if not (10 <= len(phone) <= 15):
                messages.error(request, 'Enter a valid phone number (10-15 digits).')
                return redirect('profile')
            if UserProfile.objects.filter(phone=phone).exclude(id=profile.id).exists():
                messages.error(request, 'This phone number is already in use.')
                return redirect('profile')
            profile.phone = phone
            profile.save()

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

        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            profile = None

        if profile is not None:
            # Phone-based student: manage master PIN
            current = request.POST.get('current_pin', '')
            new_pin = request.POST.get('new_pin', '')
            confirm = request.POST.get('confirm_pin', '')

            if not profile.verify_master_pin(current):
                messages.error(request, 'Current master PIN is incorrect.')
                return redirect('profile?tab=security')

            if not (new_pin and new_pin.isdigit() and 4 <= len(new_pin) <= 6):
                messages.error(request, 'New PIN must be 4-6 digits.')
                return redirect('profile?tab=security')

            if new_pin != confirm:
                messages.error(request, 'New PINs do not match.')
                return redirect('profile?tab=security')

            profile.set_master_pin(new_pin)
            UserActivity.objects.create(
                user=user,
                activity_type='OTHER',
                description='Changed master PIN',
            )
            messages.success(request, 'Master PIN changed successfully.')
            return redirect('profile?tab=security')

        # Legacy/staff password-based account
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
