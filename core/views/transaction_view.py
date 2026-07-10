from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from core.decorators import staff_required
from core.models import Payment, UserSubscription, SubscriptionPlan
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone


@staff_required
@login_required
def transaction_dashboard(request):
    search = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')
    provider_filter = request.GET.get('provider', '')

    payments = Payment.objects.select_related('user', 'subscription__plan')

    if search:
        payments = payments.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(transaction_id__icontains=search)
        )
    if status_filter:
        payments = payments.filter(status=status_filter)
    if provider_filter:
        payments = payments.filter(provider=provider_filter)

    total_revenue = payments.filter(status='SUCCESS').aggregate(Sum('amount'))['amount__sum'] or 0
    total_success = payments.filter(status='SUCCESS').count()
    total_pending = payments.filter(status='PENDING').count()
    total_failed = payments.filter(status='FAILED').count()

    plans = SubscriptionPlan.objects.filter(is_active=True)
    users = User.objects.filter(is_active=True).order_by('username')

    context = {
        'payments': payments,
        'total_revenue': total_revenue,
        'total_success': total_success,
        'total_pending': total_pending,
        'total_failed': total_failed,
        'search': search,
        'status_filter': status_filter,
        'provider_filter': provider_filter,
        'plans': plans,
        'users': users,
    }
    return render(request, 'admin/transactions.html', context)


@staff_required
@login_required
def record_transaction(request):
    if request.method == 'POST':
        user_id = request.POST.get('user')
        amount = request.POST.get('amount')
        provider = request.POST.get('provider', 'MANUAL')
        status = request.POST.get('status', 'SUCCESS')
        transaction_id = request.POST.get('transaction_id', '')
        notes = request.POST.get('notes', '')
        plan_id = request.POST.get('plan')

        if not user_id or not amount:
            messages.error(request, 'User and amount are required.')
            return redirect('transaction_dashboard')

        try:
            amount = Decimal(amount)
        except Exception:
            messages.error(request, 'Invalid amount.')
            return redirect('transaction_dashboard')

        user = get_object_or_404(User, id=user_id)
        sub = UserSubscription.objects.filter(user=user).first()

        Payment.objects.create(
            user=user,
            subscription=sub,
            amount=amount,
            provider=provider,
            status=status,
            transaction_id=transaction_id or f'manual-{user.id}-{timezone.now().timestamp()}',
            notes=notes,
        )

        if status == 'SUCCESS' and plan_id:
            plan = SubscriptionPlan.objects.filter(id=plan_id).first()
            if plan:
                if not sub:
                    sub = UserSubscription.objects.create(
                        user=user,
                        plan=plan,
                        status='ACTIVE'
                    )
                else:
                    sub.plan = plan
                    sub.status = 'ACTIVE'
                    sub.save()

        messages.success(request, 'Transaction recorded successfully.')
    return redirect('transaction_dashboard')


@staff_required
@login_required
def update_transaction_status(request, payment_id):
    if request.method == 'POST':
        payment = get_object_or_404(Payment, id=payment_id)
        new_status = request.POST.get('status')
        if new_status in dict(Payment.STATUS_CHOICES):
            payment.status = new_status
            payment.save()
            if new_status == 'SUCCESS' and payment.subscription:
                payment.subscription.status = 'ACTIVE'
                payment.subscription.save()
            messages.success(request, f'Transaction marked as {new_status.lower()}.')
        else:
            messages.error(request, 'Invalid status.')
    return redirect('transaction_dashboard')
