from django.shortcuts import render, redirect, get_object_or_404
from core.services.program_service import ProgramService
from core.models import Program, Interest, ProgramDetails, ProgramPrerequisite
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.decorators import staff_required
from core.messages.program_messages import ProgramMessages
from django.core.paginator import Paginator
from django.db.models import Count, Q as models_Q


@staff_required
@login_required(login_url='login')
def program_dashboard(request):
    search = request.GET.get('search')
    if not search:
        search = None

    program_list = ProgramService.get_all(search)
    program_list = program_list.annotate(
        institution_count=Count('programdetails', filter=models_Q(programdetails__is_active=True)),
        prereq_count=Count('prerequisites')
    ).prefetch_related('interests', 'prerequisites__subject')

    paginator = Paginator(program_list, 5)
    page_number = request.GET.get('page')
    programs = paginator.get_page(page_number)

    total_programs = Program.objects.filter(is_active=True).count()
    total_with_institutions = Program.objects.filter(programdetails__is_active=True).distinct().count()

    return render(request, 'admin/program.html', {
        'programs': programs,
        'total_programs': total_programs,
        'total_with_institutions': total_with_institutions,
        'search': search,
        'interests': Interest.objects.filter(is_active=True)
    })


@staff_required
@login_required(login_url='login')
def create_program(request):
    if request.method == 'POST':
        title = request.POST.get('title')

        if not title:
            messages.error(request, ProgramMessages.GENERAL_ERROR)
            return redirect('program_dashboard')

        ProgramService.create(request.POST)

        messages.success(request, ProgramMessages.CREATE_SUCCESS)

        return redirect('program_dashboard')


@staff_required
@login_required(login_url='login')
def update_program(request, program_id):
    if request.method == 'POST':
        try:
            ProgramService.update(program_id, request.POST)

            messages.success(request, ProgramMessages.UPDATE_SUCCESS)

        except Program.DoesNotExist:
            messages.error(request, ProgramMessages.NOT_FOUND)

        return redirect('program_dashboard')


@staff_required
@login_required(login_url='login')
def delete_program(request, program_id):
    try:
        ProgramService.delete(program_id)

        messages.success(request, ProgramMessages.DELETE_SUCCESS)

    except Program.DoesNotExist:
        messages.error(request, ProgramMessages.NOT_FOUND)

    return redirect('program_dashboard')
