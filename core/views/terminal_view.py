from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.decorators import staff_required
from core.models import TermReport, SHSStream, SHSStreamSubject
from core.services.subscription_service import plan_required
from core.services.terminal_analysis import analyze_term, compare_terms


@login_required(login_url='login')
@plan_required('terminal_analysis')
def terminal_home(request):
    reports = TermReport.objects.filter(user=request.user).select_related('stream')
    latest = reports.first()
    context = {
        'reports': reports,
        'latest': latest,
        'next_term': (reports.first().term_number + 1) if reports.first() else 1,
    }
    return render(request, 'terminal.html', context)


@login_required(login_url='login')
@plan_required('terminal_analysis')
def terminal_upload(request):
    streams = SHSStream.objects.filter(is_active=True)

    stream_subjects = {}
    for s in streams:
        subjects = SHSStreamSubject.objects.filter(stream=s).select_related('subject').order_by('subject__name')
        stream_subjects[str(s.slug)] = [
            {'name': ss.subject.name, 'category': ss.subject.category, 'is_core': ss.is_core}
            for ss in subjects
        ]

    last = TermReport.objects.filter(user=request.user).order_by('-term_number').first()
    next_term = (last.term_number + 1) if last else 1

    if request.method == 'POST':
        stream_slug = request.POST.get('stream', '')
        term_number = request.POST.get('term_number', '')
        grades = {}
        for key, value in request.POST.items():
            if key.startswith('grade_') and value:
                name = key[len('grade_'):]
                grades[name] = value

        stream = None
        if stream_slug:
            stream = SHSStream.objects.filter(slug=stream_slug, is_active=True).first()

        if not grades:
            messages.error(request, 'Enter at least one subject grade.')
            return render(request, 'terminal.html', {'mode': 'upload', 'streams': streams, 'stream_subjects_json': stream_subjects, 'next_term': next_term})

        try:
            term_number = int(term_number) if term_number else next_term
        except ValueError:
            term_number = next_term

        if term_number < 1:
            term_number = 1

        if TermReport.objects.filter(user=request.user, term_number=term_number).exists():
            messages.warning(request, f'Term {term_number} already exists. Use a different term number.')
            return render(request, 'terminal.html', {'mode': 'upload', 'streams': streams, 'stream_subjects_json': stream_subjects, 'next_term': next_term})

        analysis = analyze_term(request.user, stream, grades)

        cleaned_grades = {s['name']: s['grade_value'] for s in analysis['subjects']}

        report = TermReport.objects.create(
            user=request.user,
            stream=stream,
            term_number=term_number,
            grades=cleaned_grades,
            aggregate=analysis['aggregate'],
        )

        messages.success(request, f'Term {term_number} results saved.')
        return redirect('terminal_result', report_id=report.id)

    return render(request, 'terminal.html', {
        'mode': 'upload',
        'streams': streams,
        'stream_subjects_json': stream_subjects,
        'next_term': next_term,
    })


@login_required(login_url='login')
@plan_required('terminal_analysis')
def terminal_result(request, report_id):
    report = get_object_or_404(TermReport, id=report_id, user=request.user)
    analysis = analyze_term(request.user, report.stream, report.grades)

    prev_report = TermReport.objects.filter(
        user=request.user, term_number__lt=report.term_number
    ).order_by('-term_number').first()

    comparison = None
    if prev_report:
        prev_analysis = analyze_term(request.user, prev_report.stream, prev_report.grades)
        comparison = compare_terms(prev_analysis, analysis)

    reports = TermReport.objects.filter(user=request.user).select_related('stream').order_by('-term_number')

    return render(request, 'terminal.html', {
        'mode': 'result',
        'report': report,
        'analysis': analysis,
        'comparison': comparison,
        'reports': reports,
    })