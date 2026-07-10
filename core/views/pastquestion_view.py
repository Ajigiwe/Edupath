from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from core.models import Institution, Program, Department, Level, SchoolLevel, Course
from core.models import TheoryQuestion, MCQQuestion, MCQOption


def past_questions(request, id):
    institution = get_object_or_404(Institution, id=id)

    programs = Program.objects.filter(
        programdetails__institution=institution
    ).distinct()

    departments = Department.objects.filter(institution=institution)
    school_levels = SchoolLevel.objects.all()
    courses = Course.objects.all()

    theory_qs = TheoryQuestion.objects.all().order_by('-created_at')
    theory_paginator = Paginator(theory_qs, 3)
    theory_page = request.GET.get('theory_page')
    theory_questions = theory_paginator.get_page(theory_page)

    mcq_qs = MCQQuestion.objects.all().order_by('-created_at')
    mcq_total_questions = mcq_qs.count()
    mcq_paginator = Paginator(mcq_qs, 3)
    mcq_page = request.GET.get('mcq_page')
    mcq_questions = mcq_paginator.get_page(mcq_page)

    return render(request, 'pastquestion.html', {
        'institution': institution,
        'programs': programs,
        'departments': departments,
        'school_levels': school_levels,
        'courses': courses,
        'theory_questions': theory_questions,
        'mcq_questions': mcq_questions,
        'mcq_total_questions': mcq_total_questions,
    })


@login_required(login_url='login')
def add_theory_page(request):
    return render(request, 'add_theory.html', {
        'courses': Course.objects.all(),
        'departments': Department.objects.all(),
        'levels': SchoolLevel.objects.all(),
        'levelnames': Level.objects.all()
    })


@login_required(login_url='login')
def add_mcq_page(request):
    return render(request, 'add_mcq.html', {
        'courses': Course.objects.all(),
        'departments': Department.objects.all(),
        'levels': SchoolLevel.objects.all(),
        'levelnames': Level.objects.all()
    })


@login_required(login_url='login')
def create_theory(request):
    if request.method == "POST":
        TheoryQuestion.objects.create(
            question=request.POST.get('question'),
            answer=request.POST.get('answer'),
            course_id=request.POST.get('course'),
            department_id=request.POST.get('department'),
            level_id=request.POST.get('levelname'),
            school_level_id=request.POST.get('level'),
        )
        messages.success(request, "Theory Question Added")

    return redirect('add_theory_page')


@login_required(login_url='login')
def create_mcq(request):
    if request.method == "POST":
        q = MCQQuestion.objects.create(
            question=request.POST.get('question'),
            course_id=request.POST.get('course'),
            department_id=request.POST.get('department'),
            level_id=request.POST.get('levelname'),
            school_level_id=request.POST.get('level'),
        )

        MCQOption.objects.create(
            question=q,
            text=request.POST.get('opt1'),
            is_correct=(request.POST.get('correct') == '1')
        )
        MCQOption.objects.create(
            question=q,
            text=request.POST.get('opt2'),
            is_correct=(request.POST.get('correct') == '2')
        )
        MCQOption.objects.create(
            question=q,
            text=request.POST.get('opt3'),
            is_correct=(request.POST.get('correct') == '3')
        )
        MCQOption.objects.create(
            question=q,
            text=request.POST.get('opt4'),
            is_correct=(request.POST.get('correct') == '4')
        )

        messages.success(request, "MCQ Question Added")

    return redirect('add_mcq_page')
