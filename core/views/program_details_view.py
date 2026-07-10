from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.decorators import staff_required
from django.core.paginator import Paginator

from core.services.program_details_service import ProgramDetailsService
from core.models import ProgramDetails, Program, Institution


# def program_details_dashboard(request):
#     search = request.GET.get('search')
#     if not search:
#         search = None
#     detail_list = ProgramDetailsService.get_all(search)

#     paginator = Paginator(detail_list, 5)
#     page_number = request.GET.get('page')
#     details = paginator.get_page(page_number)

#     return render(request, 'admin/program_details.html', {
#         'details': details,
#         'search': search,
#         'programs': Program.objects.filter(is_active=True),
#         'institutions': Institution.objects.filter(is_active=True)
#     })

# def program_details_dashboard(request):
#     search = request.GET.get('search')
#     if not search:
#         search = None

#     detail_list = ProgramDetailsService.get_all(search)

#     # ✅ REMOVE DUPLICATES BY NAME (NOT ID)
#     seen = set()
#     unique_details = []

#     for d in detail_list:
#         key = (
#             d.program.programname.lower(),
#             d.institution.institutionname.lower()
#         )

#         if key not in seen:
#             seen.add(key)
#             unique_details.append(d)

#     paginator = Paginator(unique_details, 5)
#     page_number = request.GET.get('page')
#     details = paginator.get_page(page_number)

#     return render(request, 'admin/program_details.html', {
#         'details': details,
#         'search': search,
#         'programs': Program.objects.filter(is_active=True),
#         'institutions': Institution.objects.filter(is_active=True)
#     })

@staff_required
@login_required(login_url='login')
def program_details_dashboard(request):
    search = request.GET.get('search')
    if not search:
        search = None

    detail_list = ProgramDetailsService.get_all(search)

    # ✅ REMOVE DUPLICATES IN TABLE (OPTIONAL BUT GOOD)
    seen = set()
    unique_details = []

    for d in detail_list:
        key = (
            d.program.programname.lower(),
            d.institution.institutionname.lower()
        )

        if key not in seen:
            seen.add(key)
            unique_details.append(d)

    paginator = Paginator(unique_details, 5)
    page_number = request.GET.get('page')
    details = paginator.get_page(page_number)

    # ✅ REMOVE DUPLICATE INSTITUTIONS FOR DROPDOWN
    institutions_qs = Institution.objects.filter(is_active=True)

    seen_names = set()
    unique_institutions = []

    for i in institutions_qs:
        name = i.institutionname.lower()

        if name not in seen_names:
            seen_names.add(name)
            unique_institutions.append(i)

    return render(request, 'admin/program_details.html', {
        'details': details,
        'search': search,
        'programs': Program.objects.filter(is_active=True),
        'institutions': unique_institutions,  # ✅ FIXED
    })

@staff_required
@login_required(login_url='login')
def create_program_detail(request):
    if request.method == 'POST':
        try:
            ProgramDetailsService.create(request.POST)
            messages.success(request, "Added successfully ✅")
        except Exception:
            messages.error(request, "Already exists ❌")

        return redirect('program_details_dashboard')


@staff_required
@login_required(login_url='login')
def update_program_detail(request, detail_id):
    if request.method == 'POST':
        try:
            ProgramDetailsService.update(detail_id, request.POST)
            messages.success(request, "Updated successfully ✅")
        except ProgramDetails.DoesNotExist:
            messages.error(request, "Not found ❌")

        return redirect('program_details_dashboard')

# def update_program_detail(request, detail_id):
#     if request.method == 'POST':
#         ProgramDetailsService.update(detail_id, request.POST)
#         return redirect('program_details_dashboard')


@staff_required
@login_required(login_url='login')
def delete_program_detail(request, detail_id):
    try:
        ProgramDetailsService.delete(detail_id)
        messages.success(request, "Deleted successfully ✅")
    except ProgramDetails.DoesNotExist:
        messages.error(request, "Not found ❌")

    return redirect('program_details_dashboard')