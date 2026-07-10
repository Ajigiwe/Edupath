from django.contrib.auth.models import User
from core.models import SubscriptionPlan, UserSubscription, Payment
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.decorators import staff_required
from django.core.paginator import Paginator
from datetime import datetime


@staff_required
@login_required(login_url='login')
def user_dashboard(request):
    search = request.GET.get('search') or None
    user_list = User.objects.all().order_by('-date_joined')
    if search:
        user_list = user_list.filter(username__icontains=search) | user_list.filter(email__icontains=search)
    paginator = Paginator(user_list.distinct(), 10)
    users = paginator.get_page(request.GET.get('page'))
    plans = SubscriptionPlan.objects.filter(is_active=True)
    total_users = User.objects.count()
    total_subs = UserSubscription.objects.filter(status='ACTIVE').count()
    return render(request, 'admin/user.html', {
        'users': users,
        'plans': plans,
        'total_users': total_users,
        'total_subs': total_subs,
        'search': search,
    })


@staff_required
@login_required(login_url='login')
def update_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.is_active = request.POST.get('is_active') == 'on'
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.save()
        messages.success(request, f"User {user.username} updated")
    return redirect('user_dashboard')


@staff_required
@login_required(login_url='login')
def manage_subscription(request, user_id):
    user = get_object_or_404(User, id=user_id)
    sub, created = UserSubscription.objects.get_or_create(user=user, defaults={'status': 'TRIAL'})
    if request.method == 'POST':
        plan_id = request.POST.get('plan')
        if plan_id:
            sub.plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        sub.status = request.POST.get('status', sub.status)
        end_date_str = request.POST.get('end_date', '')
        if end_date_str:
            from django.utils import timezone
            try:
                sub.end_date = timezone.make_aware(datetime.strptime(end_date_str, '%Y-%m-%d'))
            except ValueError:
                pass
        sub.auto_renew = request.POST.get('auto_renew') == 'on'
        sub.save()
        messages.success(request, f"Subscription updated for {user.username}")
    return redirect('user_dashboard')
