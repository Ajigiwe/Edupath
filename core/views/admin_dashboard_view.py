from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from core.decorators import staff_required
from core.models import Program, Institution, Interest, Department, Course, SchoolLevel, ProgramDetails, Level, Ownership, InstitutionType, Subject, SHSStream, TheoryQuestion, MCQQuestion, UserSubscription, SubscriptionPlan, Payment
from django.contrib.auth.models import User

@staff_required
@login_required
def admin_dashboard(request):
    total_programs = Program.objects.count()
    total_institutions = Institution.objects.count()
    total_users = User.objects.count()
    total_interests = Interest.objects.count()
    total_departments = Department.objects.count()
    total_courses = Course.objects.count()
    total_school_levels = SchoolLevel.objects.count()
    total_program_details = ProgramDetails.objects.count()
    total_levels = Level.objects.count()
    total_ownerships = Ownership.objects.count()
    total_institution_types = InstitutionType.objects.count()
    total_subjects = Subject.objects.count()
    total_streams = SHSStream.objects.count()
    total_theory = TheoryQuestion.objects.count()
    total_mcq = MCQQuestion.objects.count()
    total_subscriptions_active = UserSubscription.objects.filter(status='ACTIVE').count()
    total_payments = Payment.objects.filter(status='SUCCESS').count()

    recent_programs = Program.objects.order_by('-created_at')[:5]

    programs_by_institution = (
        ProgramDetails.objects
        .values('institution__institutiontype__typename')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    prog_inst_labels = [item['institution__institutiontype__typename'] or 'Other' for item in programs_by_institution]
    prog_inst_data = [item['count'] for item in programs_by_institution]

    programs_by_level = (
        ProgramDetails.objects
        .values('institution__level__levelsname')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    prog_level_labels = [item['institution__level__levelsname'] or 'Other' for item in programs_by_level]
    prog_level_data = [item['count'] for item in programs_by_level]

    users_by_plan = (
        UserSubscription.objects
        .filter(status='ACTIVE')
        .values('plan__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    plan_labels = [item['plan__name'] or 'No Plan' for item in users_by_plan]
    plan_data = [item['count'] for item in users_by_plan]

    sub_statuses = (
        UserSubscription.objects
        .values('status')
        .annotate(count=Count('id'))
        .order_by('status')
    )
    status_labels = [item['status'] for item in sub_statuses]
    status_data = [item['count'] for item in sub_statuses]

    six_months_ago = timezone.now() - timedelta(days=180)
    recent_users = User.objects.filter(date_joined__gte=six_months_ago).order_by('date_joined')
    month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    monthly_counts = {}
    for u in recent_users:
        key = u.date_joined.strftime('%Y-%m')
        monthly_counts[key] = monthly_counts.get(key, 0) + 1
    sorted_months = sorted(monthly_counts.keys())
    signup_labels = []
    signup_data = []
    for ym in sorted_months:
        y, m = ym.split('-')
        signup_labels.append(f"{month_names[int(m)-1]} {y}")
        signup_data.append(monthly_counts[ym])

    context = {
        'total_programs': total_programs,
        'total_institutions': total_institutions,
        'total_users': total_users,
        'total_interests': total_interests,
        'total_departments': total_departments,
        'total_courses': total_courses,
        'total_school_levels': total_school_levels,
        'total_program_details': total_program_details,
        'total_levels': total_levels,
        'total_ownerships': total_ownerships,
        'total_institution_types': total_institution_types,
        'total_subjects': total_subjects,
        'total_streams': total_streams,
        'total_theory': total_theory,
        'total_mcq': total_mcq,
        'total_subscriptions': total_subscriptions_active,
        'total_payments': total_payments,
        'recent_programs': recent_programs,
        'prog_inst_labels': prog_inst_labels,
        'prog_inst_data': prog_inst_data,
        'prog_level_labels': prog_level_labels,
        'prog_level_data': prog_level_data,
        'plan_labels': plan_labels,
        'plan_data': plan_data,
        'status_labels': status_labels,
        'status_data': status_data,
        'signup_labels': signup_labels,
        'signup_data': signup_data,
    }
    return render(request, 'admin_dashboard.html', context)
