from django.shortcuts import render
from django.http import JsonResponse
from core.models import ProgramDetails, Interest, Program, SHSStream, Subject, SHSStreamSubject, UserActivity
from core.services.recommender import recommend, calculate_fit_score, get_category, calculate_aggregate
from django.core.paginator import Paginator
from django.db.models import Prefetch


def home(request):
    return render(request, 'home.html')


def alreadyknow(request):
    cutoff = request.GET.get('cutoff')
    program_id = request.GET.get('program')

    programs = ProgramDetails.objects.select_related('program', 'institution')
    program_list = Program.objects.filter(is_active=True).prefetch_related('prerequisites__subject')

    if cutoff:
        try:
            cutoff_int = int(cutoff)
            programs = programs.filter(cutoff_point=cutoff_int)
        except ValueError:
            cutoff_int = None
    else:
        cutoff_int = None

    if program_id:
        programs = programs.filter(program_id=program_id)

    programs = programs.order_by('-created_at')

    selected_program = None
    prereq_info = []
    viable_streams = []
    if program_id:
        try:
            selected_program = Program.objects.get(id=program_id)
            prereq_info = list(selected_program.prerequisites.select_related('subject').all())
            # Determine viable SHS streams
            from core.services.recommender import HARD_BLOCKERS
            all_streams = SHSStream.objects.filter(is_active=True)
            for stream in all_streams:
                blocked_list = HARD_BLOCKERS.get(stream.slug, [])
                is_blocked = any(b.lower() in selected_program.programname.lower() for b in blocked_list)
                if not is_blocked:
                    viable_streams.append(stream)
        except Program.DoesNotExist:
            pass

    paginator = Paginator(programs, 6)
    page_number = request.GET.get('page')
    programs_page = paginator.get_page(page_number)

    return render(request, 'alreadyknow.html', {
        'programs': programs_page,
        'programs_list': program_list,
        'selected_cutoff': cutoff or '',
        'selected_program': program_id or '',
        'prereq_info': prereq_info,
        'viable_streams': viable_streams,
        'selected_program_obj': selected_program,
    })


def careeroutcome(request):
    program_id = request.GET.get('program')

    programs = ProgramDetails.objects.select_related('program', 'institution')
    program_list = Program.objects.filter(is_active=True).prefetch_related('prerequisites__subject')

    if program_id:
        programs = programs.filter(program_id=program_id)

    paginator = Paginator(programs, 6)
    page_number = request.GET.get('page')
    programs_page = paginator.get_page(page_number)

    selected_program = None
    prereq_info = []
    if program_id:
        try:
            selected_program = Program.objects.get(id=program_id)
            prereq_info = list(selected_program.prerequisites.select_related('subject').all())
        except Program.DoesNotExist:
            pass

    return render(request, 'careeroutcome.html', {
        'programs': programs_page,
        'programs_list': program_list,
        'selected_program': program_id or '',
        'selected_program_obj': selected_program,
        'prereq_info': prereq_info,
    })


def findmypath(request):
    shs_streams = SHSStream.objects.filter(is_active=True)

    step = request.GET.get('step', '1')
    stream_slug = request.GET.get('stream', '')
    interest_ids = request.GET.getlist('interest')

    selected_stream = None
    if stream_slug:
        try:
            selected_stream = SHSStream.objects.get(slug=stream_slug, is_active=True)
        except SHSStream.DoesNotExist:
            selected_stream = None

    grades = {}
    for key, value in request.GET.items():
        if key.startswith('grade_') and value:
            subj_name = key[len('grade_'):]
            grades[subj_name] = value

    if step == '4':
        result = recommend(
            shs_stream_slug=stream_slug,
            grades=grades,
            interest_ids=interest_ids,
        )

        if request.user.is_authenticated:
            interest_names = list(Interest.objects.filter(id__in=interest_ids).values_list('name', flat=True))
            UserActivity.objects.create(
                user=request.user,
                activity_type='SEARCH',
                description=f'Searched paths: {selected_stream.name if selected_stream else "Any"} stream, interests: {", ".join(interest_names) or "None"}',
            )

        return render(request, 'findmypath.html', {
            'step': '4',
            'shs_streams': shs_streams,
            'selected_stream': selected_stream,
            'grades': grades,
            'interests': Interest.objects.filter(is_active=True),
            'selected_interests': interest_ids,
            'results': result,
        })

    stream_subjects_json = {}
    for s in shs_streams:
        subjects = SHSStreamSubject.objects.filter(stream=s).select_related('subject')
        stream_subjects_json[str(s.slug)] = [
            {'name': ss.subject.name, 'category': ss.subject.category, 'is_core': ss.is_core}
            for ss in subjects
        ]

    return render(request, 'findmypath.html', {
        'step': step,
        'shs_streams': shs_streams,
        'selected_stream': selected_stream,
        'interests': Interest.objects.filter(is_active=True),
        'selected_interests': interest_ids,
        'grades': grades,
        'stream_subjects_json': stream_subjects_json,
    })


def stream_subjects_api(request, stream_slug):
    try:
        stream = SHSStream.objects.get(slug=stream_slug, is_active=True)
    except SHSStream.DoesNotExist:
        return JsonResponse({'error': 'Stream not found'}, status=404)

    subjects = SHSStreamSubject.objects.filter(stream=stream).select_related('subject')
    data = [
        {'id': str(ss.subject.id), 'name': ss.subject.name, 'is_core': ss.is_core}
        for ss in subjects
    ]
    return JsonResponse(data, safe=False)
