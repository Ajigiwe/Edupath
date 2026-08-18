from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from core.services.subscription_service import plan_required
from core.models import Institution


@login_required(login_url='login')
@plan_required(['past_questions', 'past_questions_limited'])
def institutions_list(request):
    all_institutions = Institution.objects.filter(is_active=True)

    seen = set()
    unique_institutions = []

    for inst in all_institutions:
        if inst.institutionname not in seen:
            seen.add(inst.institutionname)
            unique_institutions.append(inst)

    return render(request, 'institutions_list.html', {
        'institutions': unique_institutions
    })


