from django import template
from core.services.subscription_service import user_has_feature, get_user_plan_features

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])


@register.filter
def has_feature(user, codename):
    return user_has_feature(user, codename)


@register.simple_tag(takes_context=True)
def user_features(context):
    request = context.get('request')
    if request and request.user.is_authenticated:
        return get_user_plan_features(request.user)
    return set()


@register.simple_tag(takes_context=True)
def user_plan_name(context):
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return 'Free'
    try:
        sub = request.user.subscription
        if sub.plan:
            return sub.plan.name
    except Exception:
        pass
    return 'Free'
