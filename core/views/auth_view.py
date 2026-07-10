from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from core.models import SubscriptionPlan, UserSubscription, UserActivity



def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            UserActivity.objects.create(user=user, activity_type='LOGIN', description=f'Logged in from {request.META.get("REMOTE_ADDR", "unknown")}')
            if user.is_staff or user.is_superuser:
                return redirect('admin_dashboard')
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'auth/login.html')


def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm", "")

        if not username or not email or not password:
            messages.error(request, "All fields are required.")
            return render(request, "auth/signup.html")

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, "auth/signup.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, "auth/signup.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "auth/signup.html")

        user = User.objects.create_user(username=username, email=email, password=password)
        UserActivity.objects.create(user=user, activity_type='SIGNUP', description='Signed up for an account')
        # auto-assign free plan
        free_plan = SubscriptionPlan.objects.filter(slug='free').first()
        if free_plan:
            UserSubscription.objects.create(user=user, plan=free_plan, status='ACTIVE')
        login(request, user)
        messages.success(request, f"Welcome, {username}!")
        if user.is_staff or user.is_superuser:
            return redirect("admin_dashboard")
        return redirect("home")

    return render(request, "auth/signup.html")


def logout_view(request):
    logout(request)
    return redirect('login')



