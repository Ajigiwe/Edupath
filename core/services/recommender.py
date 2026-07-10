WAEC_GRADE_MAP = {
    'A1': 1, 'B2': 2, 'B3': 3,
    'C4': 4, 'C5': 5, 'C6': 6,
    'D7': 7, 'E8': 8, 'F9': 9,
}

GRADE_LABEL_MAP = {v: k for k, v in WAEC_GRADE_MAP.items()}

HARD_BLOCKERS = {
    'general-science': [],
    'general-arts': [
        'Medicine', 'Dentistry', 'Pharmacy', 'Veterinary Medicine',
        'Engineering', 'Nursing', 'Medical Laboratory Science',
        'Biomedical Science', 'Pure Sciences', 'Veterinary',
    ],
    'business': [
        'Medicine', 'Dentistry', 'Pharmacy', 'Veterinary Medicine',
        'Engineering', 'Nursing', 'Medical Laboratory Science',
        'Biomedical Science', 'Pure Sciences',
    ],
    'visual-arts': [
        'Medicine', 'Dentistry', 'Pharmacy', 'Engineering',
        'Computer Science', 'Pure Sciences',
    ],
    'home-economics': [
        'Engineering', 'Architecture', 'Computer Science',
        'Law', 'Medicine',
    ],
    'agricultural-science': [
        'Medicine', 'Law', 'Architecture',
    ],
    'technical': [
        'Medicine', 'Dentistry', 'Pharmacy', 'Law',
        'Pure Sciences',
    ],
    'stem': [],
}

STREAM_VIABLE_MAP = {
    'general-science': ['Engineering', 'Medicine', 'Dentistry', 'Pharmacy',
        'Veterinary Medicine', 'Computer Science', 'Pure Sciences',
        'Nursing', 'Medical Laboratory Science', 'Biomedical Science',
        'Environmental Science', 'Architecture', 'Mathematics',
        'Statistics', 'Psychology', 'Education',
        'Accounting', 'Finance', 'Economics',
        'Business Management', 'Journalism', 'Law (if exceptional English)',
        'Agriculture'],
    'general-arts': ['Law', 'Education', 'History', 'Philosophy',
        'Journalism', 'Language Studies', 'Public Administration',
        'Psychology', 'Geography', 'Economics (less quantitative)',
        'Business Management', 'Marketing', 'HRM',
        'Communication Studies', 'Political Science',
        'Environmental Science (with strong Geography)',
        'Hospitality Management'],
    'business': ['Accounting', 'Finance', 'Business Management',
        'Economics', 'Marketing', 'HRM', 'Public Administration',
        'Computer Science (if Math A)', 'Law (if strong English)',
        'Information Systems', 'Actuarial Science',
        'Logistics and Supply Chain Management',
        'Hospitality Management', 'Communication Studies',
        'Education (Business/Economics)'],
    'visual-arts': ['Architecture', 'Communication Design', 'Fine Arts',
        'Industrial Art', 'Education (Visual Arts)',
        'Hospitality Management', 'Journalism'],
    'home-economics': ['Dietetics', 'Nursing', 'Hospitality Management',
        'Family and Consumer Sciences', 'Education (Home Economics)',
        'Public Health', 'Food Science'],
    'agricultural-science': ['Agriculture', 'Agribusiness',
        'Agricultural Engineering', 'Veterinary Medicine',
        'Environmental Science', 'Food Science', 'Animal Science',
        'Crop Science'],
    'technical': ['Architecture', 'Building Technology',
        'Electrical Technology', 'Engineering (with catch-up)',
        'Computer Science (with catch-up)',
        'Technical Education', 'BTech programmes',
        'Quantity Surveying', 'Construction Technology'],
    'stem': ['Medicine', 'Engineering', 'Computer Science',
        'Robotics Engineering', 'Software Engineering',
        'Pure Sciences', 'Biomedical Science',
        'Aviation and Aerospace', 'Data Science'],
}

def calculate_aggregate(grades):
    """
    grades: dict of {subject_name: waec_value (1-9)}
    Returns: best 3 core + best 3 electives aggregate (lower is better), or None if insufficient
    """
    core_subjects = {'English Language', 'Core Mathematics', 'Integrated Science', 'Social Studies'}
    core_grades = []
    elective_grades = []

    for subj, val in grades.items():
        val = int(val)
        if subj.lower() in [c.lower() for c in core_subjects] or any(c.lower() in subj.lower() for c in core_subjects):
            core_grades.append(val)
        else:
            elective_grades.append(val)

    core_grades.sort()
    elective_grades.sort()

    best_3_core = core_grades[:3]
    best_3_elective = elective_grades[:3]

    if len(best_3_core) < 3 or len(best_3_elective) < 3:
        return None

    return sum(best_3_core) + sum(best_3_elective)


def is_hard_blocked(shs_stream_slug, program_name):
    blocked = HARD_BLOCKERS.get(shs_stream_slug, [])
    for b in blocked:
        if b.lower() in program_name.lower():
            return True
    return False


def calculate_fit_score(grades, program, prerequisites, interest_ids):
    score = 0.0
    grade_points = {1: 4.0, 2: 3.5, 3: 3.0, 4: 2.5, 5: 2.0, 6: 1.5, 7: 1.0, 8: 0.5, 9: 0.0}

    subject_score = 0.0
    subject_weight = 0
    for prereq in prerequisites:
        grade_val = None
        for subj_name, g in grades.items():
            if prereq.subject.name.lower() in subj_name.lower() or subj_name.lower() in prereq.subject.name.lower():
                grade_val = int(g)
                break

        if grade_val is not None:
            points = grade_points.get(grade_val, 0)
            weight = 40 if prereq.requirement_level == 'REQ' else 20
            subject_score += weight * (points / 4.0)
            subject_weight += weight

    if subject_weight > 0:
        score += subject_score / subject_weight * 40
    else:
        score += 20

    avg = 0
    count = 0
    for v in grades.values():
        avg += int(v)
        count += 1
    if count > 0:
        avg = avg / count
        if avg <= 2:
            score += 30
        elif avg <= 4:
            score += 25
        elif avg <= 6:
            score += 15
        else:
            score += 5

    interest_matched = False
    for interest in program.interests.all():
        if str(interest.id) in interest_ids or interest.id in interest_ids:
            interest_matched = True
            break
    score += 20 if interest_matched else 5

    score += 5

    return min(score, 100)


def get_category(score):
    if score >= 90:
        return ('EXCELLENT', 'Highly Recommended')
    elif score >= 75:
        return ('GOOD', 'Recommended')
    elif score >= 60:
        return ('MODERATE', 'Consider Carefully')
    elif score >= 40:
        return ('CHALLENGING', 'Possible but Difficult')
    return ('NOT_VIABLE', 'Not Recommended')


def get_subject_match_details(grades, prerequisites):
    details = []
    for prereq in prerequisites:
        grade_val = None
        grade_label = '—'
        for subj_name, g in grades.items():
            if prereq.subject.name.lower() in subj_name.lower() or subj_name.lower() in prereq.subject.name.lower():
                grade_val = int(g)
                grade_label = GRADE_LABEL_MAP.get(grade_val, str(grade_val))
                break
        met = grade_val is not None and grade_val <= prereq.min_grade
        details.append({
            'subject': prereq.subject.name,
            'level': prereq.get_requirement_level_display(),
            'min_grade': GRADE_LABEL_MAP.get(prereq.min_grade, str(prereq.min_grade)),
            'student_grade': grade_label,
            'met': met,
        })
    return details


def recommend(shs_stream_slug, grades, interest_ids, passion_area=None):
    from core.models import Program, ProgramDetails, ProgramPrerequisite

    results = []
    stretch = []
    not_viable = []

    programs = Program.objects.filter(is_active=True).prefetch_related(
        'prerequisites__subject', 'interests', 'programdetails_set__institution',
        'programdetails_set__admission_tiers', 'programdetails_set__alternative_pathways'
    )

    for program in programs:
        program_name = program.programname

        if is_hard_blocked(shs_stream_slug, program_name):
            not_viable.append({
                'program': program,
                'reason': f'Your SHS stream does not provide the foundation needed for {program_name}.',
                'suggestion': 'Consider related programmes with lower prerequisites.',
            })
            continue

        prerequisites = list(program.prerequisites.select_related('subject').all())
        details = get_subject_match_details(grades, prerequisites)
        all_required_met = all(
            d['met'] for d in details if d['level'] == 'Required'
        )

        student_aggregate = calculate_aggregate(grades)
        best_tier = None
        best_pd = None

        for pd in program.programdetails_set.filter(is_active=True):
            tiers = pd.admission_tiers.filter(is_active=True)
            for tier in tiers:
                if student_aggregate is not None and student_aggregate <= tier.cutoff_aggregate:
                    if best_tier is None or tier.cutoff_aggregate < best_tier.cutoff_aggregate:
                        best_tier = tier
                        best_pd = pd
            if not tiers and student_aggregate is not None and pd.cutoff_point:
                if student_aggregate <= pd.cutoff_point:
                    if best_tier is None or pd.cutoff_point < best_tier.cutoff_aggregate:
                        best_tier = type('obj', (object,), {
                            'tier_name': 'Regular',
                            'cutoff_aggregate': pd.cutoff_point,
                            'get_gender_display': lambda: 'Any',
                        })()
                        best_pd = pd

        fit_score = calculate_fit_score(grades, program, prerequisites, interest_ids)

        if not all_required_met:
            if fit_score >= 40:
                stretch.append({
                    'program': program,
                    'program_details': best_pd,
                    'tier': best_tier,
                    'fit_score': fit_score,
                    'category': get_category(fit_score),
                    'subject_details': details,
                    'aggregate': student_aggregate,
                    'missing_required': [d for d in details if d['level'] == 'Required' and not d['met']],
                })
            else:
                not_viable.append({
                    'program': program,
                    'reason': 'Missing required prerequisite subjects.',
                    'suggestion': 'Consider taking bridging courses or an access programme.',
                    'subject_details': details,
                })
            continue

        if best_pd is None:
            if fit_score >= 40:
                stretch.append({
                    'program': program,
                    'program_details': None,
                    'tier': None,
                    'fit_score': fit_score,
                    'category': get_category(fit_score),
                    'subject_details': details,
                    'aggregate': student_aggregate,
                    'missing_required': [],
                    'below_cutoff': True,
                })
            continue

        alternatives = list(best_pd.alternative_pathways.filter(is_active=True)) if best_pd else []

        results.append({
            'program': program,
            'program_details': best_pd,
            'tier': best_tier,
            'fit_score': fit_score,
            'category': get_category(fit_score),
            'subject_details': details,
            'aggregate': student_aggregate,
            'alternatives': alternatives,
        })

    results.sort(key=lambda r: r['fit_score'], reverse=True)
    stretch.sort(key=lambda r: r['fit_score'], reverse=True)

    return {
        'primary': results,
        'stretch': stretch,
        'not_viable': not_viable,
    }
