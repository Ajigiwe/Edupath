from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from core.decorators import staff_required
from core.models import TermReport, SHSStream, SHSStreamSubject, UserProfile
from core.services.subscription_service import plan_required
from core.services.terminal_analysis import analyze_term, compare_terms, analyze_overall


SHS_YEARS = [(1, 'SHS 1'), (2, 'SHS 2'), (3, 'SHS 3')]
TERMS = [(1, 'Term 1'), (2, 'Term 2')]


@login_required(login_url='login')
@plan_required('terminal_analysis')
def terminal_home(request):
    reports = TermReport.objects.filter(user=request.user).select_related('stream')
    latest = reports.first()
    if latest:
        # Suggest next year/term based on latest report
        y, t = latest.year, latest.term
        if t == 1:
            next_year, next_term = y, 2
        elif t == 2:
            next_year, next_term = y + 1, 1
        else:
            next_year, next_term = y, 1
        if next_year > 3:
            next_year, next_term = 3, 2
    else:
        next_year, next_term = 1, 1

    context = {
        'reports': reports,
        'latest': latest,
        'next_year': next_year,
        'next_term': next_term,
        'next_term_label': dict(SHS_YEARS)[next_year] if next_year <= 3 else 'SHS 3',
        'next_term_num': next_term,
    }
    return render(request, 'terminal.html', context)


@login_required(login_url='login')
@plan_required('terminal_analysis')
def terminal_upload(request):
    streams = SHSStream.objects.filter(is_active=True)

    # Build subject data per stream
    stream_subjects = {}
    for s in streams:
        subjects = SHSStreamSubject.objects.filter(stream=s).select_related('subject').order_by('is_core', 'subject__name')
        stream_subjects[str(s.slug)] = [
            {'name': ss.subject.name, 'category': ss.subject.category, 'is_core': ss.is_core}
            for ss in subjects
        ]

    # Pre-fill stream from user's profile if they have one
    profile = None
    try:
        profile = request.user.profile
    except (UserProfile.DoesNotExist, AttributeError):
        profile = None

    initial_stream_slug = ''
    if profile and profile.stream:
        initial_stream_slug = profile.stream.slug

    if request.method == 'POST':
        stream_slug = request.POST.get('stream', '')
        year = request.POST.get('year', '')
        term = request.POST.get('term', '')
        grades = {}
        for key, value in request.POST.items():
            if key.startswith('grade_') and value:
                name = key[len('grade_'):]
                grades[name] = value

        stream = None
        if stream_slug:
            stream = SHSStream.objects.filter(slug=stream_slug, is_active=True).first()

        # Validate year/term
        try:
            year = int(year)
            term = int(term)
        except (TypeError, ValueError):
            year, term = None, None

        if not year or year not in [1, 2, 3] or not term or term not in [1, 2]:
            messages.error(request, 'Please select a valid SHS year and term.')
            return render(request, 'terminal.html', {
                'mode': 'upload',
                'streams': streams,
                'stream_subjects_json': json.dumps(stream_subjects),
                'initial_stream_slug': initial_stream_slug,
                'shs_years': SHS_YEARS,
                'terms': TERMS,
            })

        if not stream:
            messages.error(request, 'Please select your SHS stream.')
            return render(request, 'terminal.html', {
                'mode': 'upload',
                'streams': streams,
                'stream_subjects_json': json.dumps(stream_subjects),
                'initial_stream_slug': initial_stream_slug,
                'shs_years': SHS_YEARS,
                'terms': TERMS,
            })

        if not grades:
            messages.error(request, 'Enter at least one subject grade.')
            return render(request, 'terminal.html', {
                'mode': 'upload',
                'streams': streams,
                'stream_subjects_json': json.dumps(stream_subjects),
                'initial_stream_slug': initial_stream_slug,
                'shs_years': SHS_YEARS,
                'terms': TERMS,
            })

        # Check if this year/term already exists
        if TermReport.objects.filter(user=request.user, year=year, term=term).exists():
            messages.warning(request, f'SHS {year} Term {term} already exists. Use a different year/term.')
            return render(request, 'terminal.html', {
                'mode': 'upload',
                'streams': streams,
                'stream_subjects_json': json.dumps(stream_subjects),
                'initial_stream_slug': initial_stream_slug,
                'shs_years': SHS_YEARS,
                'terms': TERMS,
            })

        analysis = analyze_term(request.user, stream, grades)

        cleaned_grades = {s['name']: s['grade_value'] for s in analysis['subjects']}

        report = TermReport.objects.create(
            user=request.user,
            stream=stream,
            year=year,
            term=term,
            grades=cleaned_grades,
            aggregate=analysis['aggregate'],
        )

        # Save stream to user's profile for future selections
        if profile:
            if not profile.stream_id == stream.id:
                profile.stream = stream
                profile.save(update_fields=['stream'])
        else:
            # Create profile with stream if it doesn't exist
            UserProfile.objects.create(user=request.user, stream=stream)

        messages.success(request, f'SHS {year} Term {term} results saved.')
        return redirect('terminal_result', report_id=report.id)

    return render(request, 'terminal.html', {
        'mode': 'upload',
        'streams': streams,
        'stream_subjects_json': json.dumps(stream_subjects),
        'initial_stream_slug': initial_stream_slug,
        'shs_years': SHS_YEARS,
        'terms': TERMS,
    })


@login_required(login_url='login')
@plan_required('terminal_analysis')
def terminal_result(request, report_id):
    report = get_object_or_404(TermReport, id=report_id, user=request.user)
    analysis = analyze_term(request.user, report.stream, report.grades)

    # Find previous term for comparison
    prev_report = TermReport.objects.filter(
        user=request.user
    ).filter(
        year__lt=report.year
    ).order_by('-year', '-term').first()

    comparison = None
    if prev_report:
        prev_analysis = analyze_term(request.user, prev_report.stream, prev_report.grades)
        comparison = compare_terms(prev_analysis, analysis)

    reports = TermReport.objects.filter(user=request.user).select_related('stream').order_by('-year', '-term')

    return render(request, 'terminal.html', {
        'mode': 'result',
        'report': report,
        'analysis': analysis,
        'comparison': comparison,
        'reports': reports,
    })


@login_required(login_url='login')
@plan_required('terminal_analysis')
def terminal_analysis_overall(request):
    """Overall analysis across all term reports — strengths, weaknesses, trends."""
    reports = TermReport.objects.filter(user=request.user).select_related('stream').order_by('-year', '-term')
    overall = analyze_overall(request.user, reports)

    return render(request, 'terminal.html', {
        'mode': 'analysis',
        'overall': overall,
        'reports': reports,
    })
