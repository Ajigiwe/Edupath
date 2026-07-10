from core.models import SubscriptionPlan, PlanFeature, PlanFeatureThrough
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.decorators import staff_required
from django.core.paginator import Paginator


@staff_required
@login_required(login_url='login')
def plan_dashboard(request):
    search = request.GET.get('search') or None
    plan_list = SubscriptionPlan.objects.all()
    if search:
        plan_list = plan_list.filter(name__icontains=search)
    paginator = Paginator(plan_list, 10)
    plans = paginator.get_page(request.GET.get('page'))
    features = PlanFeature.objects.filter(is_active=True)
    total_plans = SubscriptionPlan.objects.count()
    return render(request, 'admin/plan.html', {
        'plans': plans,
        'features': features,
        'total_plans': total_plans,
        'search': search,
    })


@staff_required
@login_required(login_url='login')
def create_plan(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        slug = request.POST.get('slug', '').strip()
        if not name or not slug:
            messages.error(request, "Name and slug are required")
            return redirect('plan_dashboard')
        plan = SubscriptionPlan.objects.create(
            name=name,
            slug=slug,
            description=request.POST.get('description', ''),
            price_monthly=request.POST.get('price_monthly', 0),
            price_yearly=request.POST.get('price_yearly', 0),
            is_active=request.POST.get('is_active') == 'on',
            sort_order=request.POST.get('sort_order', 0),
            badge_label=request.POST.get('badge_label', ''),
            color=request.POST.get('color', '#1e3a5f'),
        )
        for fid in request.POST.getlist('features'):
            try:
                PlanFeatureThrough.objects.create(plan=plan, feature_id=fid)
            except Exception:
                pass
        messages.success(request, "Plan created successfully")
    return redirect('plan_dashboard')


@staff_required
@login_required(login_url='login')
def update_plan(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    if request.method == 'POST':
        plan.name = request.POST.get('name', plan.name)
        plan.slug = request.POST.get('slug', plan.slug)
        plan.description = request.POST.get('description', '')
        plan.price_monthly = request.POST.get('price_monthly', 0)
        plan.price_yearly = request.POST.get('price_yearly', 0)
        plan.is_active = request.POST.get('is_active') == 'on'
        plan.sort_order = request.POST.get('sort_order', 0)
        plan.badge_label = request.POST.get('badge_label', '')
        plan.color = request.POST.get('color', '#1e3a5f')
        plan.save()
        plan.features.clear()
        for fid in request.POST.getlist('features'):
            try:
                PlanFeatureThrough.objects.create(plan=plan, feature_id=fid)
            except Exception:
                pass
        messages.success(request, "Plan updated successfully")
    return redirect('plan_dashboard')


@staff_required
@login_required(login_url='login')
def delete_plan(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    plan.delete()
    messages.success(request, "Plan deleted successfully")
    return redirect('plan_dashboard')
