from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from core.models import SubscriptionPlan, UserSubscription, UserActivity, UserProfile
from core.services.otp_service import generate_otp, build_pending, verify_pending


def _normalize_phone(phone):
    return ''.join(ch for ch in (phone or '') if ch.isdigit())


def _is_valid_phone(phone):
    return 10 <= len(phone) <= 15


def _is_valid_pin(pin):
    return pin and pin.isdigit() and 4 <= len(pin) <= 6


def _display_otp(request, phone, otp):
    """No SMS gateway available yet — show the OTP on screen (simulated SMS)."""
    return otp


def login_view(request):
    if request.method == "POST":
        mode = request.POST.get("mode", "student")

        if mode == "staff":
            username = request.POST.get("username", "")
            password = request.POST.get("password", "")
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                UserActivity.objects.create(user=user, activity_type='LOGIN', description=f'Staff login from {request.META.get("REMOTE_ADDR", "unknown")}')
                return redirect('admin_dashboard')
            messages.error(request, "Invalid username or password.")
            return render(request, 'auth/login.html', {'mode': 'staff'})

        # Student mode: phone + master PIN
        phone = _normalize_phone(request.POST.get("phone", ""))
        pin = request.POST.get("pin", "")
        profile = UserProfile.objects.filter(phone=phone).select_related('user').first()

        if not profile:
            messages.error(request, "No account found for this phone number. Please sign up or use 'Forgot PIN'.")
            return render(request, 'auth/login.html', {'mode': 'student'})

        if not profile.has_master_pin():
            messages.warning(request, "No master PIN set yet. Use 'Forgot PIN' to create one.")
            return render(request, 'auth/login.html', {'mode': 'student'})

        if profile.verify_master_pin(pin):
            user = profile.user
            if not user.is_active:
                messages.error(request, "This account has been deactivated.")
                return render(request, 'auth/login.html', {'mode': 'student'})
            login(request, user)
            UserActivity.objects.create(user=user, activity_type='LOGIN', description=f'Logged in from {request.META.get("REMOTE_ADDR", "unknown")}')
            return redirect('home')

        messages.error(request, "Incorrect master PIN.")
        return render(request, 'auth/login.html', {'mode': 'student'})

    return render(request, 'auth/login.html', {'mode': 'student'})


def signup_view(request):
    """3-step flow stored in session: phone -> OTP (shown on screen) -> master PIN."""
    pending = request.session.get('signup_pending')

    if request.method == "POST":
        step = request.POST.get("step", "phone")

        if step == "phone":
            phone = _normalize_phone(request.POST.get("phone", ""))
            if not _is_valid_phone(phone):
                messages.error(request, "Enter a valid phone number (10-15 digits).")
                return render(request, 'auth/signup.html', {'step': 'phone'})

            if UserProfile.objects.filter(phone=phone).exists():
                messages.error(request, "This phone number is already registered. Please log in.")
                return render(request, 'auth/signup.html', {'step': 'phone'})

            otp = generate_otp()
            request.session['signup_pending'] = build_pending(phone, otp)
            request.session.modified = True
            display_otp = _display_otp(request, phone, otp)
            return render(request, 'auth/signup.html', {
                'step': 'otp',
                'phone': phone,
                'display_otp': display_otp,
            })

        if step == "otp":
            if not pending:
                messages.error(request, "Session expired. Start over.")
                return render(request, 'auth/signup.html', {'step': 'phone'})
            valid, expired = verify_pending(pending, request.POST.get("otp", "").strip())
            if expired:
                request.session.pop('signup_pending', None)
                messages.error(request, "OTP expired. Request a new one.")
                return render(request, 'auth/signup.html', {'step': 'phone'})
            if not valid:
                messages.error(request, "Incorrect OTP. Try again.")
                return render(request, 'auth/signup.html', {
                    'step': 'otp',
                    'phone': pending['phone'],
                    'display_otp': _display_otp(request, pending['phone'], pending['otp']),
                })

            return render(request, 'auth/signup.html', {
                'step': 'pin',
                'phone': pending['phone'],
            })

        if step == "pin":
            if not pending:
                messages.error(request, "Session expired. Start over.")
                return render(request, 'auth/signup.html', {'step': 'phone'})

            pin = request.POST.get("pin", "")
            confirm = request.POST.get("confirm_pin", "")
            if not _is_valid_pin(pin):
                messages.error(request, "Master PIN must be 4-6 digits.")
                return render(request, 'auth/signup.html', {'step': 'pin', 'phone': pending['phone']})
            if pin != confirm:
                messages.error(request, "PINs do not match.")
                return render(request, 'auth/signup.html', {'step': 'pin', 'phone': pending['phone']})

            phone = pending['phone']
            if UserProfile.objects.filter(phone=phone).exists():
                request.session.pop('signup_pending', None)
                messages.error(request, "This phone number is already registered. Please log in.")
                return render(request, 'auth/signup.html', {'step': 'phone'})

            username = f"user_{phone}" if not phone.isalpha() else phone
            # Ensure username uniqueness (phone-based usernames can collide with legacy users)
            base = username
            i = 2
            while User.objects.filter(username=username).exists():
                username = f"{base}_{i}"
                i += 1

            user = User.objects.create_user(username=username, password=None)
            user.set_unusable_password()
            user.save()

            UserProfile.objects.create(user=user, phone=phone)
            profile = UserProfile.objects.get(user=user)
            profile.set_master_pin(pin)

            UserActivity.objects.create(user=user, activity_type='SIGNUP', description=f'Signed up with phone {phone}')
            free_plan = SubscriptionPlan.objects.filter(slug='free').first()
            if free_plan:
                UserSubscription.objects.create(user=user, plan=free_plan, status='ACTIVE')

            request.session.pop('signup_pending', None)
            login(request, user)
            messages.success(request, "Account created. Welcome to EduPath!")
            return redirect('home')

    return render(request, 'auth/signup.html', {'step': 'phone'})


def request_otp(request):
    """Forgot-PIN flow: verify phone via OTP, then set a new master PIN."""
    pending = request.session.get('otp_pending')

    if request.method == "POST":
        step = request.POST.get("step", "phone")

        if step == "phone":
            phone = _normalize_phone(request.POST.get("phone", ""))
            if not _is_valid_phone(phone):
                messages.error(request, "Enter a valid phone number (10-15 digits).")
                return render(request, 'auth/otp.html', {'step': 'phone'})

            profile = UserProfile.objects.filter(phone=phone).select_related('user').first()
            if not profile:
                messages.error(request, "No account found for this phone number.")
                return render(request, 'auth/otp.html', {'step': 'phone'})

            otp = generate_otp()
            request.session['otp_pending'] = build_pending(phone, otp)
            request.session.modified = True
            return render(request, 'auth/otp.html', {
                'step': 'otp',
                'phone': phone,
                'display_otp': _display_otp(request, phone, otp),
            })

        if step == "otp":
            if not pending:
                messages.error(request, "Session expired. Start over.")
                return render(request, 'auth/otp.html', {'step': 'phone'})
            valid, expired = verify_pending(pending, request.POST.get("otp", "").strip())
            if expired:
                request.session.pop('otp_pending', None)
                messages.error(request, "OTP expired. Request a new one.")
                return render(request, 'auth/otp.html', {'step': 'phone'})
            if not valid:
                messages.error(request, "Incorrect OTP. Try again.")
                return render(request, 'auth/otp.html', {
                    'step': 'otp',
                    'phone': pending['phone'],
                    'display_otp': _display_otp(request, pending['phone'], pending['otp']),
                })
            return render(request, 'auth/otp.html', {
                'step': 'pin',
                'phone': pending['phone'],
            })

        if step == "pin":
            if not pending:
                messages.error(request, "Session expired. Start over.")
                return render(request, 'auth/otp.html', {'step': 'phone'})

            pin = request.POST.get("pin", "")
            confirm = request.POST.get("confirm_pin", "")
            if not _is_valid_pin(pin):
                messages.error(request, "Master PIN must be 4-6 digits.")
                return render(request, 'auth/otp.html', {'step': 'pin', 'phone': pending['phone']})
            if pin != confirm:
                messages.error(request, "PINs do not match.")
                return render(request, 'auth/otp.html', {'step': 'pin', 'phone': pending['phone']})

            profile = UserProfile.objects.filter(phone=pending['phone']).first()
            if not profile:
                request.session.pop('otp_pending', None)
                messages.error(request, "Account not found.")
                return render(request, 'auth/otp.html', {'step': 'phone'})

            profile.set_master_pin(pin)
            request.session.pop('otp_pending', None)
            UserActivity.objects.create(user=profile.user, activity_type='OTHER', description='Reset master PIN via OTP')
            messages.success(request, "Master PIN set successfully. You can now log in.")
            return redirect('login')

    return render(request, 'auth/otp.html', {'step': 'phone'})


def logout_view(request):
    logout(request)
    return redirect('login')