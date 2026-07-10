from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.decorators import staff_required
from django.core.paginator import Paginator

from core.services.course_service import CourseService
from core.models import Course, Department, Interest


@staff_required
@login_required(login_url='login')
def course_dashboard(request):
    search = request.GET.get('search')
    if not search:
        search = None

    course_list = CourseService.get_all(search)

    paginator = Paginator(course_list, 5)
    page_number = request.GET.get('page')
    courses = paginator.get_page(page_number)

    return render(request, 'admin/course.html', {
        'courses': courses,
        'search': search,
        'departments': Department.objects.filter(is_active=True),
        'interests': Interest.objects.filter(is_active=True),
    })


@staff_required
@login_required(login_url='login')
def create_course(request):
    if request.method == 'POST':
        CourseService.create(request.POST)
        messages.success(request, "Course added successfully ✅")
        return redirect('course_dashboard')


@staff_required
@login_required(login_url='login')
def update_course(request, course_id):
    if request.method == 'POST':
        CourseService.update(course_id, request.POST)
        messages.success(request, "Course updated successfully ✅")
        return redirect('course_dashboard')


@staff_required
@login_required(login_url='login')
def delete_course(request, course_id):
    CourseService.delete(course_id)
    messages.success(request, "Course deleted successfully ✅")
    return redirect('course_dashboard')