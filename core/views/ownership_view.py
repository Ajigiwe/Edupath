from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.decorators import staff_required
from django.core.paginator import Paginator

from core.services.ownership_service import OwnershipService
from core.models import Ownership


@staff_required
@login_required(login_url='login')
def ownership_dashboard(request):
    search = request.GET.get('search')
    if not search:
        search = None
        
    ownership_list = OwnershipService.get_all(search)

    paginator = Paginator(ownership_list, 5)
    page_number = request.GET.get('page')
    ownerships = paginator.get_page(page_number)

    total_ownerships = ownership_list.count()

    return render(request, 'admin/ownership.html', {
        'ownerships': ownerships,
        'total_ownerships': total_ownerships,
        'search': search
    })


@staff_required
@login_required(login_url='login')
def create_ownership(request):
    if request.method == 'POST':
        OwnershipService.create(request.POST)
        messages.success(request, "Ownership added successfully ✅")
        return redirect('ownership_dashboard')


@staff_required
@login_required(login_url='login')
def update_ownership(request, ownership_id):
    if request.method == 'POST':
        OwnershipService.update(ownership_id, request.POST)
        messages.success(request, "Ownership updated successfully ✅")
        return redirect('ownership_dashboard')


@staff_required
@login_required(login_url='login')
def delete_ownership(request, ownership_id):
    OwnershipService.delete(ownership_id)
    messages.success(request, "Ownership deleted successfully ✅")
    return redirect('ownership_dashboard')