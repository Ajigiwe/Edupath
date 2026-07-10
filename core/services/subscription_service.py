from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from core.models import PlanFeature


def get_user_plan_features(user):
    """Returns set of feature codenames the user has access to."""
    if not user.is_authenticated:
        return set()
    try:
        sub = user.subscription
        if sub.status not in ('ACTIVE', 'TRIAL') or not sub.plan:
            return set()
        return set(
            sub.plan.planfeaturethrough_set.values_list('feature__codename', flat=True)
        )
    except user.__class__.subscription.RelatedObjectDoesNotExist:
        return set()


def user_has_feature(user, codename):
    """Check if user has access to a specific feature."""
    if not user.is_authenticated:
        return False
    try:
        sub = user.subscription
        if sub.status not in ('ACTIVE', 'TRIAL'):
            return False
        return sub.plan.planfeaturethrough_set.filter(feature__codename=codename).exists()
    except Exception:
        return False


def plan_required(feature_codename):
    """Decorator: redirects to plans page if user lacks the feature."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not user_has_feature(request.user, feature_codename):
                messages.warning(request, 'Upgrade your plan to access this feature.')
                return redirect('plans')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
