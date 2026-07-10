from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.decorators import staff_required
from django.core.paginator import Paginator

from core.services.level_service import LevelService
from core.models import Level
from core.messages.program_messages import ProgramMessages  # reuse for now


# 📊 DASHBOARD
@staff_required
@login_required(login_url='login')
def level_dashboard(request):
    search = request.GET.get('search')
    if not search:
        search = None
        
    level_list = LevelService.get_all(search)

    paginator = Paginator(level_list, 5)
    page_number = request.GET.get('page')
    levels = paginator.get_page(page_number)

    total_levels = level_list.count()

    return render(request, 'admin/level.html', {
        'levels': levels,
        'total_levels': total_levels,
        'search': search
    })


# ➕ CREATE
@staff_required
@login_required(login_url='login')
def create_level(request):
    if request.method == 'POST':
        name = request.POST.get('levelsname')

        if not name:
            messages.error(request, ProgramMessages.GENERAL_ERROR)
            return redirect('level_dashboard')

        LevelService.create(request.POST)

        messages.success(request, "Level added successfully ✅")

        return redirect('level_dashboard')


# ✏️ UPDATE
@staff_required
@login_required(login_url='login')
def update_level(request, level_id):
    if request.method == 'POST':
        try:
            LevelService.update(level_id, request.POST)

            messages.success(request, "Level updated successfully ✅")

        except Level.DoesNotExist:
            messages.error(request, "Level not found ❌")

        return redirect('level_dashboard')


# ❌ SOFT DELETE
@staff_required
@login_required(login_url='login')
def delete_level(request, level_id):
    try:
        LevelService.delete(level_id)

        messages.success(request, "Level deleted successfully ✅")

    except Level.DoesNotExist:
        messages.error(request, "Level not found ❌")

    return redirect('level_dashboard')