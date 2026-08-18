from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from core.decorators import staff_required
from core.services.subscription_service import plan_required
from core.models import Institution, Program, Department, Level, SchoolLevel, Course
from core.models import TheoryQuestion, MCQQuestion, MCQOption
from core.models import Flashcard
import json


@login_required(login_url='login')
@plan_required(['past_questions', 'past_questions_limited'])
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


@staff_required
@login_required(login_url='login')
def add_theory_page(request):
    return render(request, 'add_theory.html', {
        'courses': Course.objects.all(),
        'departments': Department.objects.all(),
        'levels': SchoolLevel.objects.all(),
        'levelnames': Level.objects.all()
    })


@staff_required
@login_required(login_url='login')
def add_mcq_page(request):
    return render(request, 'add_mcq.html', {
        'courses': Course.objects.all(),
        'departments': Department.objects.all(),
        'levels': SchoolLevel.objects.all(),
        'levelnames': Level.objects.all()
    })


@staff_required
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


@staff_required
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


def _resolve(value, queryset, lookup_field, label):
    """Resolve a model instance by its display field. Returns (instance, None) or (None, error)."""
    if not value:
        return None, None
    try:
        return queryset.get(**{lookup_field: value}), None
    except queryset.model.DoesNotExist:
        return None, f'{label} "{value}" not found'
    except queryset.model.MultipleObjectsReturned:
        return None, f'{label} "{value}" matches multiple records'


@staff_required
@login_required(login_url='login')
def upload_questions_page(request):
    results = None
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            messages.error(request, 'Please select a JSON file.')
            return redirect('upload_questions_page')

        try:
            data = json.load(file)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            messages.error(request, f'Invalid JSON file: {e}')
            return redirect('upload_questions_page')

        entries = data.get('questions', [])
        if not isinstance(entries, list) or not entries:
            messages.error(request, 'JSON file must contain a "questions" array.')
            return redirect('upload_questions_page')

        success = 0
        skipped = 0
        errors = []

        courses_cache = {c.coursename.lower(): c for c in Course.objects.all()}
        dept_cache = {d.name.lower(): d for d in Department.objects.all()}
        level_cache = {l.levelsname.lower(): l for l in Level.objects.all()}
        school_cache = {str(s.level_number): s for s in SchoolLevel.objects.all()}

        # Preload lookup cache functions
        def get_course(name):
            return courses_cache.get(name.lower()) if name else None
        def get_dept(name):
            return dept_cache.get(name.lower()) if name else None
        def get_level(name):
            return level_cache.get(name.lower()) if name else None
        def get_school_level(num):
            return school_cache.get(str(num)) if num is not None else None

        for i, entry in enumerate(entries):
            idx = i + 1
            qtype = entry.get('type', '').lower()

            if qtype not in ('theory', 'mcq', 'flashcard'):
                errors.append({'idx': idx, 'msg': f'Unknown type "{entry.get("type")}" — must be "theory", "mcq", or "flashcard"'})
                continue

            question_text = entry.get('question', '').strip()
            if not question_text:
                errors.append({'idx': idx, 'msg': 'Missing question text'})
                continue

            course = get_course(entry.get('course', ''))
            department = get_dept(entry.get('department', ''))
            level = get_level(entry.get('level', ''))
            school_level = get_school_level(entry.get('school_level'))

            # Build a unique-ish key for duplicate detection
            dup_key = (question_text.lower(), course.id if course else None)

            if qtype == 'theory':
                answer = entry.get('answer', '').strip()
                if not answer:
                    errors.append({'idx': idx, 'msg': 'Theory question missing answer'})
                    continue

                existing = TheoryQuestion.objects.filter(
                    question__iexact=question_text, course=course
                ).exists()
                if existing:
                    skipped += 1
                    continue

                TheoryQuestion.objects.create(
                    question=question_text, answer=answer,
                    course=course, department=department,
                    level=level, school_level=school_level,
                )
                success += 1

            elif qtype == 'mcq':
                options = entry.get('options', [])
                if not isinstance(options, list) or len(options) != 4:
                    errors.append({'idx': idx, 'msg': f'MCQ must have exactly 4 options (got {len(options) if isinstance(options, list) else "non-list"})'})
                    continue

                correct_count = sum(1 for o in options if isinstance(o, dict) and o.get('correct'))
                if correct_count != 1:
                    errors.append({'idx': idx, 'msg': f'MCQ must have exactly 1 correct option (found {correct_count})'})
                    continue

                existing = MCQQuestion.objects.filter(
                    question__iexact=question_text, course=course
                ).exists()
                if existing:
                    skipped += 1
                    continue

                mcq = MCQQuestion.objects.create(
                    question=question_text,
                    course=course, department=department,
                    level=level, school_level=school_level,
                )
                for o in options:
                    MCQOption.objects.create(
                        question=mcq,
                        text=str(o.get('text', '')).strip(),
                        is_correct=bool(o.get('correct', False)),
                    )
                success += 1

            elif qtype == 'flashcard':
                answer = entry.get('answer', '').strip()
                if not answer:
                    errors.append({'idx': idx, 'msg': 'Flashcard missing answer'})
                    continue

                existing = Flashcard.objects.filter(
                    question__iexact=question_text, course=course
                ).exists()
                if existing:
                    skipped += 1
                    continue

                Flashcard.objects.create(
                    question=question_text, answer=answer,
                    course=course, department=department,
                    level=level, school_level=school_level,
                )
                success += 1

        results = {
            'total': len(entries),
            'success': success,
            'skipped': skipped,
            'errors': errors,
        }

    return render(request, 'admin/upload_questions.html', {
        'results': results,
    })


@staff_required
@login_required(login_url='login')
def sample_questions_json(request):
    from django.http import HttpResponse
    sample = {
        "_instructions": [
            "Each question must have a 'type': 'theory', 'mcq', or 'flashcard'",
            "course, department, level, school_level are optional — matched by name",
            "Theory and flashcard require 'question' + 'answer'",
            "MCQ questions must have exactly 4 options, exactly 1 marked correct: true",
            "Duplicate questions (same text + same course) are skipped",
        ],
        "questions": [
            {
                "type": "theory",
                "course": "Introduction to Computing",
                "department": "Computer Science",
                "level": "Degree",
                "school_level": 100,
                "question": "Define the term algorithm.",
                "answer": "An algorithm is a step-by-step procedure for solving a problem in a finite number of steps.",
            },
            {
                "type": "flashcard",
                "course": "Introduction to Computing",
                "department": "Computer Science",
                "question": "What is the binary representation of the decimal number 10?",
                "answer": "1010",
            },
            {
                "type": "mcq",
                "course": "Introduction to Computing",
                "department": "Computer Science",
                "level": "Degree",
                "school_level": 100,
                "question": "What does CPU stand for?",
                "options": [
                    {"text": "Central Processing Unit", "correct": True},
                    {"text": "Central Program Utility", "correct": False},
                    {"text": "Computer Personal Unit",   "correct": False},
                    {"text": "Core Processing Utility",  "correct": False},
                ],
            },
        ],
    }
    response = HttpResponse(
        json.dumps(sample, indent=2),
        content_type='application/json',
    )
    response['Content-Disposition'] = 'attachment; filename="sample_questions.json"'
    return response
