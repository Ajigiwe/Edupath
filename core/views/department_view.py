# core/views/department_view.py

from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib import messages

from core.services.department_service import DepartmentService
from core.models import Department, Institution


# def department_dashboard(request):
#     search = request.GET.get('search')

#     dept_list = DepartmentService.get_all(search)

#     paginator = Paginator(dept_list, 5)
#     page_number = request.GET.get('page')
#     departments = paginator.get_page(page_number)

#     return render(request, 'admin/department.html', {
#         'departments': departments,
#         'institutions': Institution.objects.filter(is_active=True),
#         'search': search
#     })


# core/views/department_view.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.decorators import staff_required
from django.core.paginator import Paginator

from core.models import Department, Institution


@staff_required
@login_required(login_url='login')
def department_dashboard(request):
    search = request.GET.get('search')

    departments = Department.objects.select_related('institution').all()

    if search:
        departments = departments.filter(name__icontains=search)

    paginator = Paginator(departments, 5)
    page_number = request.GET.get('page')
    departments_page = paginator.get_page(page_number)

    # ✅ REMOVE DUPLICATE INSTITUTIONS FOR DROPDOWN
    institutions_qs = Institution.objects.filter(is_active=True)

    seen = set()
    unique_institutions = []

    for inst in institutions_qs:
        name = inst.institutionname.strip().lower()

        if name not in seen:
            seen.add(name)
            unique_institutions.append(inst)

    return render(request, 'admin/department.html', {
        'departments': departments_page,
        'institutions': unique_institutions,
        'search': search
    })


@staff_required
@login_required(login_url='login')
def create_department(request):
    if request.method == 'POST':
        DepartmentService.create(request.POST)
        messages.success(request, "Department added ✅")
        return redirect('department_dashboard')


@staff_required
@login_required(login_url='login')
def update_department(request, department_id):
    if request.method == 'POST':
        DepartmentService.update(department_id, request.POST)
        messages.success(request, "Updated ✅")
        return redirect('department_dashboard')


@staff_required
@login_required(login_url='login')
def delete_department(request, department_id):
    DepartmentService.delete(department_id)
    messages.success(request, "Deleted ✅")
    return redirect('department_dashboard')