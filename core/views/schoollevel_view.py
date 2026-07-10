from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.decorators import staff_required
from django.core.paginator import Paginator

from core.services.schoollevel_service import SchoolLevelService
from core.models import SchoolLevel


@staff_required
@login_required(login_url='login')
def schoollevel_dashboard(request):
    search = request.GET.get('search')
    if not search:
        search = None

    level_list = SchoolLevelService.get_all(search)

    paginator = Paginator(level_list, 5)
    page_number = request.GET.get('page')
    levels = paginator.get_page(page_number)

    return render(request, 'admin/schoollevel.html', {
        'levels': levels,
        'search': search
    })


@staff_required
@login_required(login_url='login')
def create_schoollevel(request):
    if request.method == 'POST':
        SchoolLevelService.create(request.POST)
        messages.success(request, "Level added ✅")
        return redirect('schoollevel_dashboard')


@staff_required
@login_required(login_url='login')
def update_schoollevel(request, level_id):
    if request.method == 'POST':
        SchoolLevelService.update(level_id, request.POST)
        messages.success(request, "Updated ✅")
        return redirect('schoollevel_dashboard')


@staff_required
@login_required(login_url='login')
def delete_schoollevel(request, level_id):
    SchoolLevelService.delete(level_id)
    messages.success(request, "Deleted ✅")
    return redirect('schoollevel_dashboard')