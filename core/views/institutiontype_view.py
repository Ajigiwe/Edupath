from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.decorators import staff_required
from django.core.paginator import Paginator

from core.services.institutiontype_service import InstitutionTypeService
from core.models import InstitutionType, Ownership


# 📊 DASHBOARD
@staff_required
@login_required(login_url='login')
def institutiontype_dashboard(request):
    search = request.GET.get('search')
    if not search:
        search = None
        
    type_list = InstitutionTypeService.get_all(search)

    paginator = Paginator(type_list, 5)
    page_number = request.GET.get('page')
    institutiontypes = paginator.get_page(page_number)

    total_types = type_list.count()

    return render(request, 'admin/institutiontype.html', {
        'institutiontypes': institutiontypes,
        'total_types': total_types,
        'search': search,
        'ownerships': Ownership.objects.filter(is_active=True)  # dropdown
    })


# ➕ CREATE
@staff_required
@login_required(login_url='login')
def create_institutiontype(request):
    if request.method == 'POST':
        typename = request.POST.get('typename')

        if not typename:
            messages.error(request, "Institution type name is required ❌")
            return redirect('institutiontype_dashboard')

        InstitutionTypeService.create(request.POST)

        messages.success(request, "Institution Type added successfully ✅")

        return redirect('institutiontype_dashboard')


# ✏️ UPDATE
@staff_required
@login_required(login_url='login')
def update_institutiontype(request, type_id):
    if request.method == 'POST':
        try:
            InstitutionTypeService.update(type_id, request.POST)

            messages.success(request, "Institution Type updated successfully ✅")

        except InstitutionType.DoesNotExist:
            messages.error(request, "Institution Type not found ❌")

        return redirect('institutiontype_dashboard')


# ❌ DELETE (SOFT)
@staff_required
@login_required(login_url='login')
def delete_institutiontype(request, type_id):
    try:
        InstitutionTypeService.delete(type_id)

        messages.success(request, "Institution Type deleted successfully ✅")

    except InstitutionType.DoesNotExist:
        messages.error(request, "Institution Type not found ❌")

    return redirect('institutiontype_dashboard')