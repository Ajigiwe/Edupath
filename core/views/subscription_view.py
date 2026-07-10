from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.models import SubscriptionPlan, PlanFeature, UserSubscription, Payment, UserActivity
from core.services.paystack_service import initialize_transaction, verify_transaction
from decimal import Decimal


def plans_view(request):
    plans = SubscriptionPlan.objects.filter(is_active=True).prefetch_related('planfeaturethrough_set__feature')
    return render(request, 'plans.html', {
        'plans': plans,
    })


@login_required(login_url='login')
def my_subscription(request):
    try:
        sub = request.user.subscription
    except Exception:
        sub = None
    payments = Payment.objects.filter(user=request.user)[:10]
    plans = SubscriptionPlan.objects.filter(is_active=True)
    return render(request, 'my_subscription.html', {
        'subscription': sub,
        'payments': payments,
        'plans': plans,
    })


@login_required(login_url='login')
def subscribe(request, plan_slug):
    plan = get_object_or_404(SubscriptionPlan, slug=plan_slug, is_active=True)

    if plan.price_monthly == 0:
        sub, created = UserSubscription.objects.get_or_create(
            user=request.user,
            defaults={'plan': plan, 'status': 'ACTIVE'}
        )
        if not created:
            sub.plan = plan
            sub.status = 'ACTIVE'
            sub.save()
        UserActivity.objects.create(user=request.user, activity_type='PLAN_CHANGE', description=f'Subscribed to {plan.name} (Free)')
        Payment.objects.create(
            user=request.user,
            subscription=sub,
            amount=0,
            provider='FREE',
            status='SUCCESS',
            transaction_id=f'free-{plan.slug}',
            notes=f'Free subscription to {plan.name}',
        )
        messages.success(request, f'Subscribed to {plan.name}')
        return redirect('my_subscription')

    result = initialize_transaction(
        email=request.user.email,
        amount_ghs=float(plan.price_monthly),
        plan_slug=plan.slug,
        request=request,
    )

    if result.get('status'):
        sub, created = UserSubscription.objects.get_or_create(
            user=request.user,
            defaults={'plan': plan, 'status': 'TRIAL'}
        )
        if not created:
            sub.plan = plan
            sub.status = 'TRIAL'
            sub.save()
        UserActivity.objects.create(user=request.user, activity_type='PLAN_CHANGE', description=f'Started subscription to {plan.name} (GHS {plan.price_monthly}/mo)')
        Payment.objects.create(
            user=request.user,
            subscription=sub,
            amount=plan.price_monthly,
            provider='PAYSTACK',
            status='PENDING',
            transaction_id=result['reference'],
            notes=f'Payment for {plan.name}|{plan.slug}',
        )
        return redirect(result['authorization_url'])

    messages.error(request, result.get('message', 'Payment initialization failed.'))
    return redirect('plans')


@login_required(login_url='login')
def paystack_callback(request):
    reference = request.GET.get('reference', '')
    if not reference:
        messages.error(request, 'No transaction reference found.')
        return redirect('my_subscription')

    result = verify_transaction(reference)

    if result.get('status'):
        payment = Payment.objects.filter(transaction_id=reference, provider='PAYSTACK').first()
        if payment and payment.status == 'PENDING':
            payment.status = 'SUCCESS'
            payment.save()

            sub = payment.subscription
            if sub:
                sub.status = 'ACTIVE'
                plan_slug = payment.notes.split('|')[1] if '|' in payment.notes else None
                if plan_slug:
                    new_plan = SubscriptionPlan.objects.filter(slug=plan_slug).first()
                    if new_plan:
                        sub.plan = new_plan
                sub.save()
            UserActivity.objects.create(user=payment.user, activity_type='PLAN_CHANGE', description=f'Payment completed — {payment.notes.split("|")[0] if "|" in payment.notes else "plan activated"}')

            messages.success(request, 'Payment successful! Your subscription is now active.')
        else:
            messages.info(request, 'Payment already processed.')
    else:
        messages.error(request, result.get('message', 'Payment verification failed.'))

    return redirect('my_subscription')
