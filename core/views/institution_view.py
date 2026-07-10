from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.decorators import staff_required
from django.core.paginator import Paginator

from core.services.institution_service import InstitutionService
from core.models import Institution, InstitutionType, Level
from core.messages.program_messages import ProgramMessages  # you can rename later


# 🏫 DASHBOARD
@staff_required
@login_required(login_url='login')
def institution_dashboard(request):
    search = request.GET.get('search')
    if not search:
        search = None

    institution_list = InstitutionService.get_all(search)

    paginator = Paginator(institution_list, 5)
    page_number = request.GET.get('page')
    institutions = paginator.get_page(page_number)

    total_institutions = institution_list.count()

    return render(request, 'admin/institution.html', {
        'institutions': institutions,
        'total_institutions': total_institutions,
        'search': search,
         # ✅ FIXED
    'institution_types': InstitutionType.objects.filter(is_active=True),
    'levels': Level.objects.filter(is_active=True),
    })


# ➕ CREATE
@staff_required
@login_required(login_url='login')
def create_institution(request):
    if request.method == 'POST':
        name = request.POST.get('institutionname')

        if not name:
            messages.error(request, ProgramMessages.GENERAL_ERROR)
            return redirect('institution_dashboard')

        InstitutionService.create(request.POST)

        messages.success(request, "Institution added successfully ✅")

        return redirect('institution_dashboard')


# ✏️ UPDATE
@staff_required
@login_required(login_url='login')
def update_institution(request, institution_id):
    if request.method == 'POST':
        try:
            InstitutionService.update(institution_id, request.POST)

            messages.success(request, "Institution updated successfully ✅")

        except Institution.DoesNotExist:
            messages.error(request, "Institution not found ❌")

        return redirect('institution_dashboard')


# ❌ SOFT DELETE
@staff_required
@login_required(login_url='login')
def delete_institution(request, institution_id):
    try:
        InstitutionService.delete(institution_id)

        messages.success(request, "Institution deleted successfully ✅")

    except Institution.DoesNotExist:
        messages.error(request, "Institution not found ❌")

    return redirect('institution_dashboard')