import json
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from core.models import SubscriptionPlan, UserSubscription, Payment, UserActivity
from core.services.paystack_service import initialize_transaction, verify_transaction, _ghs_to_kobo


def plans_view(request):
    plans = SubscriptionPlan.objects.filter(is_active=True).prefetch_related('planfeaturethrough_set__feature')
    return render(request, 'plans.html', {
        'plans': plans,
    })


@login_required(login_url='login')
def my_subscription(request):
    try:
        sub = request.user.subscription
    except UserSubscription.DoesNotExist:
        sub = None
    payments = Payment.objects.filter(user=request.user)[:10]
    plans = SubscriptionPlan.objects.filter(is_active=True)

    # While a paid subscription is active, users may upgrade or renew but not
    # downgrade to a cheaper plan.
    downgrade_locked = False
    if sub and sub.plan and sub.plan.price_monthly > 0:
        downgrade_locked = (
            sub.status in ('ACTIVE', 'TRIAL')
            and (not sub.end_date or sub.end_date > timezone.now())
        )

    return render(request, 'my_subscription.html', {
        'subscription': sub,
        'payments': payments,
        'plans': plans,
        'downgrade_locked': downgrade_locked,
    })


@login_required(login_url='login')
def subscribe(request, plan_slug):
    plan = get_object_or_404(SubscriptionPlan, slug=plan_slug, is_active=True)

    # Block downgrading to a cheaper plan while a paid subscription is active.
    # Upgrades to higher-priced plans and renewals of the same plan are allowed.
    try:
        current_sub = request.user.subscription
    except UserSubscription.DoesNotExist:
        current_sub = None

    if current_sub and current_sub.plan and current_sub.plan.price_monthly > 0:
        is_currently_active = (
            current_sub.status in ('ACTIVE', 'TRIAL')
            and (not current_sub.end_date or current_sub.end_date > timezone.now())
        )
        is_downgrade = current_sub.plan.price_monthly > plan.price_monthly
        if is_currently_active and is_downgrade and current_sub.plan_id != plan.id:
            end_display = current_sub.end_date.strftime('%B %d, %Y') if current_sub.end_date else 'the end of your period'
            messages.warning(
                request,
                f'Your {current_sub.plan.name} subscription is active until {end_display}. '
                'You can downgrade to a cheaper plan after it expires.'
            )
            return redirect('my_subscription')

    if plan.price_monthly == 0:
        sub, created = UserSubscription.objects.get_or_create(
            user=request.user,
            defaults={'plan': plan, 'status': 'ACTIVE'}
        )
        if not created:
            sub.plan = plan
            sub.status = 'ACTIVE'
            sub.end_date = None
            sub.save()
        UserActivity.objects.create(user=request.user, activity_type='PLAN_CHANGE', description=f'Subscribed to {plan.name} (Free)')
        Payment.objects.create(
            user=request.user,
            subscription=sub,
            amount=0,
            provider='FREE',
            status='SUCCESS',
            transaction_id=f'free-{plan.slug}-{request.user.id}',
            notes=f'Free subscription to {plan.name}',
        )
        messages.success(request, f'Subscribed to {plan.name}')
        return redirect('my_subscription')

    result = initialize_transaction(
        email=request.user.email,
        amount_ghs=plan.price_monthly,
        plan_slug=plan.slug,
        request=request,
    )

    if result.get('status'):
        # Keep the user's current subscription untouched until payment succeeds.
        try:
            sub = request.user.subscription
        except UserSubscription.DoesNotExist:
            free_plan = SubscriptionPlan.objects.filter(slug='free').first()
            sub = UserSubscription.objects.create(
                user=request.user,
                plan=free_plan,
                status='ACTIVE',
            )

        Payment.objects.create(
            user=request.user,
            subscription=sub,
            amount=plan.price_monthly,
            provider='PAYSTACK',
            status='PENDING',
            transaction_id=result['reference'],
            notes=json.dumps({'plan_slug': plan.slug, 'plan_name': plan.name}),
        )
        messages.info(request, 'Complete the payment to activate your new plan.')
        return redirect(result['authorization_url'])

    messages.error(request, result.get('message', 'Payment initialization failed.'))
    return redirect('plans')


@login_required(login_url='login')
def paystack_callback(request):
    reference = request.GET.get('reference', '')
    if not reference:
        messages.error(request, 'No transaction reference found.')
        return redirect('my_subscription')

    payment = Payment.objects.filter(transaction_id=reference, provider='PAYSTACK').first()
    if not payment:
        messages.error(request, 'Payment record not found.')
        return redirect('my_subscription')

    # Ownership check — the payment must belong to the requesting user.
    if payment.user_id != request.user.id:
        messages.error(request, 'This payment does not belong to your account.')
        return redirect('my_subscription')

    if payment.status == 'SUCCESS':
        messages.info(request, 'Payment already processed.')
        return redirect('my_subscription')

    result = verify_transaction(reference)

    if result.get('status'):
        # Amount verification — ensure what was charged matches what we recorded.
        paid_kobo = int(result['data'].get('amount', 0))
        expected_kobo = _ghs_to_kobo(payment.amount)
        if paid_kobo != expected_kobo:
            messages.error(request, 'Payment amount does not match the plan price. Please contact support.')
            return redirect('my_subscription')

        payment.status = 'SUCCESS'
        payment.save()

        sub = payment.subscription
        if not sub:
            sub, _ = UserSubscription.objects.get_or_create(user=request.user)

        plan_slug = None
        plan_name = 'plan activated'
        if payment.notes:
            try:
                notes = json.loads(payment.notes)
                plan_slug = notes.get('plan_slug')
                plan_name = notes.get('plan_name', 'plan activated')
            except (ValueError, TypeError):
                plan_slug = None

        if plan_slug:
            new_plan = SubscriptionPlan.objects.filter(slug=plan_slug).first()
            if new_plan:
                sub.plan = new_plan
                plan_name = new_plan.name

        sub.status = 'ACTIVE'
        if sub.plan and sub.plan.price_monthly > 0:
            sub.end_date = timezone.now() + timedelta(days=sub.plan.duration_days or 30)
        else:
            sub.end_date = None
        sub.save()
        UserActivity.objects.create(user=payment.user, activity_type='PLAN_CHANGE', description=f'Payment completed — {plan_name}')

        messages.success(request, 'Payment successful! Your subscription is now active.')
    else:
        payment.status = 'FAILED'
        payment.save()
        messages.error(request, result.get('message', 'Payment verification failed.'))

    return redirect('my_subscription')
