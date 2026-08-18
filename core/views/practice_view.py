import json
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from core.services.subscription_service import plan_required
from core.models import Course, MCQQuestion, MCQOption, TheoryQuestion, Flashcard, PracticeSession


@login_required(login_url='login')
@plan_required(['past_questions', 'past_questions_limited'])
def practice_home(request):
    courses = Course.objects.filter(is_active=True).order_by('coursename')
    # Active session countdown
    active_session = PracticeSession.objects.filter(
        user=request.user, completed=False
    ).order_by('-started_at').first()

    return render(request, 'practice.html', {
        'courses': courses,
        'active_session': active_session,
        'state': 'select',
    })


@login_required(login_url='login')
@plan_required(['past_questions', 'past_questions_limited'])
def practice_start(request):
    if request.method != 'POST':
        return redirect('practice_home')

    course_id = request.POST.get('course', '').strip()
    course = Course.objects.filter(id=course_id).first() if course_id else None
    qtype = request.POST.get('qtype', 'mixed').strip()

    questions = []

    if qtype in ('mixed', 'mcq'):
        mcqs = MCQQuestion.objects.filter(is_active=True).prefetch_related('options')
        if course:
            mcqs = mcqs.filter(course=course)
        limit = 30 if qtype == 'mcq' else 20
        mcqs = list(mcqs.order_by('?')[:limit])
        for q in mcqs:
            opts = [{'text': o.text, 'correct': o.is_correct} for o in q.options.all()]
            random.shuffle(opts)
            questions.append({
                'id': str(q.id),
                'type': 'mcq',
                'question': q.question,
                'options': opts,
            })

    if qtype in ('mixed', 'flashcard'):
        flashcards = Flashcard.objects.filter(is_active=True)
        if course:
            flashcards = flashcards.filter(course=course)
        limit = 30 if qtype == 'flashcard' else 10
        flashcards = list(flashcards.order_by('?')[:limit])
        for f in flashcards:
            questions.append({
                'id': str(f.id),
                'type': 'flashcard',
                'question': f.question,
                'answer': f.answer,
            })

    # Mixed: fill remaining with theory
    if qtype == 'mixed':
        remaining = 30 - len(questions)
        if remaining > 0:
            theories = TheoryQuestion.objects.filter(is_active=True)
            if course:
                theories = theories.filter(course=course)
            for t in theories.order_by('?')[:remaining]:
                questions.append({
                    'id': str(t.id),
                    'type': 'theory',
                    'question': t.question,
                    'answer': t.answer,
                })

    if not questions:
        messages.error(request, 'No questions available for this course yet.')
        return redirect('practice_home')

    random.shuffle(questions)
    questions = questions[:30]

    session = PracticeSession.objects.create(
        user=request.user,
        course=course,
        questions_json=questions,
        total=len(questions),
    )

    return redirect('practice_quiz', session_id=session.id)


@login_required(login_url='login')
@plan_required(['past_questions', 'past_questions_limited'])
def practice_quiz(request, session_id):
    session = get_object_or_404(PracticeSession, id=session_id, user=request.user, completed=False)

    q_index = session.current_index
    questions = session.questions_json

    if q_index >= len(questions):
        return redirect('practice_result', session_id=session.id)

    current_q = questions[q_index]

    # Check if it's a POST (answer submitted) or GET (show question)
    if request.method == 'POST':
        answers = session.answers_json

        if current_q['type'] == 'mcq':
            selected = request.POST.get('answer', '')
            correct_option = next((o for o in current_q['options'] if o['correct']), None)
            is_correct = correct_option and selected == correct_option['text']
            if is_correct:
                session.correct_count += 1
            answers.append({
                'q_idx': q_index,
                'type': 'mcq',
                'question': current_q['question'],
                'student_answer': selected,
                'correct_answer': correct_option['text'] if correct_option else '',
                'is_correct': is_correct,
            })

        elif current_q['type'] == 'flashcard':
            self_assess = request.POST.get('self_assess', 'review')
            answers.append({
                'q_idx': q_index,
                'type': 'flashcard',
                'question': current_q['question'],
                'student_answer': self_assess,
                'correct_answer': current_q.get('answer', ''),
                'is_correct': True if self_assess == 'got_it' else False,
            })
            if self_assess == 'got_it':
                session.correct_count += 1

        elif current_q['type'] == 'theory':
            student_text = request.POST.get('answer', '').strip()
            self_assess = request.POST.get('self_assess', 'review')
            answers.append({
                'q_idx': q_index,
                'type': 'theory',
                'question': current_q['question'],
                'student_answer': student_text,
                'correct_answer': current_q.get('answer', ''),
                'is_correct': True if self_assess == 'got_it' else False,
            })
            if self_assess == 'got_it':
                session.correct_count += 1

        session.answers_json = answers
        session.current_index = q_index + 1

        # Check if done
        if session.current_index >= session.total:
            session.completed = True
            session.completed_at = timezone.now()

        session.save()

        if session.completed:
            return redirect('practice_result', session_id=session.id)

        # Return JSON for AJAX or redirect for non-AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            next_q = questions[session.current_index] if session.current_index < len(questions) else None
            return JsonResponse({
                'next': next_q is not None,
                'index': session.current_index,
                'total': session.total,
                'correct': session.correct_count,
                'current_answer': answers[-1] if answers else None,
            })

        return redirect('practice_quiz', session_id=session.id)

    return render(request, 'practice.html', {
        'state': 'quiz',
        'session': session,
        'question': current_q,
        'q_index': q_index,
    })


@login_required(login_url='login')
@plan_required(['past_questions', 'past_questions_limited'])
def practice_result(request, session_id):
    session = get_object_or_404(PracticeSession, id=session_id, user=request.user, completed=True)
    total = session.total
    correct = session.correct_count
    pct = round(correct / total * 100) if total else 0
    return render(request, 'practice.html', {
        'state': 'result',
        'session': session,
        'pct': pct,
        'stroke_offset': round(327 * (1 - pct / 100)) if total else 327,
    })
