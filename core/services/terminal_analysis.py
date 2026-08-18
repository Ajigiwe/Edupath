from core.services.recommender import calculate_aggregate, GRADE_LABEL_MAP, is_hard_blocked


def _grade_value(val):
    """Accept WAEC labels (A1..F9) or numeric values."""
    try:
        return int(val)
    except (TypeError, ValueError):
        label = str(val).strip().upper()
        rev = {v: k for k, v in GRADE_LABEL_MAP.items()}
        return rev.get(label)


def _fmt_grade(val):
    if val is None:
        return '—'
    return GRADE_LABEL_MAP.get(val, str(val))


def analyze_term(user, stream, grades):
    """
    Analyze a single term's grades for a student on a given SHS stream.
    Returns a structured report dict.
    """
    from core.models import Program, ProgramDetails, ProgramAdmissionTier

    cleaned = {}
    for name, val in grades.items():
        if val in (None, ''):
            continue
        gv = _grade_value(val)
        if gv is not None:
            cleaned[str(name).strip()] = gv

    aggregate = calculate_aggregate(cleaned)

    # Determine the stream slug used by recommender maps
    stream_slug = stream.slug if stream else ''

    # Per-subject performance
    subjects = []
    failing = []
    strong = []

    # Build subject name → is_core map from stream
    is_core_map = {}
    if stream:
        from core.models import SHSStreamSubject
        for ss in SHSStreamSubject.objects.filter(stream=stream).select_related('subject'):
            is_core_map[ss.subject.name.strip()] = ss.is_core

    for name, gv in cleaned.items():
        is_core = is_core_map.get(str(name).strip(), False)
        subj = {
            'name': name,
            'grade_value': gv,
            'grade_label': _fmt_grade(gv),
            'is_core': is_core,
            'status': 'weak' if gv >= 6 else ('strong' if gv <= 3 else 'ok'),
        }
        subjects.append(subj)
        if gv >= 6:
            failing.append(subj)
        elif gv <= 3:
            strong.append(subj)

    subjects.sort(key=lambda s: s['grade_value'])

    # Programme guidance: reuse the recommender's viability rules
    programs = Program.objects.filter(is_active=True)
    likely = []
    not_viable = []
    for program in programs:
        name = program.programname
        if is_hard_blocked(stream_slug, name):
            not_viable.append({'name': name})
            continue
        if aggregate is not None:
            pd = program.programdetails_set.filter(is_active=True).first()
            cutoff = None
            if pd:
                tier = pd.admission_tiers.filter(is_active=True).order_by('cutoff_aggregate').first()
                if tier:
                    cutoff = tier.cutoff_aggregate
                elif pd.cutoff_point:
                    cutoff = pd.cutoff_point
            if cutoff is not None and aggregate <= cutoff:
                likely.append({'name': name, 'cutoff': cutoff})
            else:
                not_viable.append({'name': name, 'reason': 'aggregate', 'cutoff': cutoff})

    likely.sort(key=lambda x: x['cutoff'] or 99)
    not_viable.sort(key=lambda x: x.get('cutoff') or 99)

    # Overall standing
    if aggregate is None:
        standing = 'INCOMPLETE'
        verdict = 'Incomplete record'
    elif aggregate <= 12:
        standing = 'STRONG'
        verdict = 'Very strong — you are on track for top programmes.'
    elif aggregate <= 18:
        standing = 'ON_TRACK'
        verdict = 'Solid performance — most programmes remain within reach.'
    elif aggregate <= 24:
        standing = 'RISK'
        verdict = 'Fair performance — some programmes may be out of reach. Focus on weak subjects.'
    else:
        standing = 'REVIEW'
        verdict = 'Urgent review needed — prioritise your weakest subjects and seek help early.'

    # Focus areas
    focus_areas = [s['name'] for s in failing]
    if not focus_areas and strong:
        focus_areas = ['Keep sustaining your strong subjects: ' + ', '.join(s['name'] for s in strong)]

    return {
        'aggregate': aggregate,
        'subjects': subjects,
        'failing': failing,
        'strong': strong,
        'likely': likely,
        'not_viable': not_viable,
        'standing': standing,
        'verdict': verdict,
        'focus_areas': focus_areas,
    }


def compare_terms(prev, cur):
    """
    Compare two analyzed terms (dicts from analyze_term).
    Returns a comparison dict with per-subject deltas, aggregate delta, trend.
    """
    if not prev or not cur:
        return None

    prev_grades = {s['name']: s['grade_value'] for s in prev['subjects']}
    cur_grades = {s['name']: s['grade_value'] for s in cur['subjects']}

    deltas = []
    for name, gv in cur_grades.items():
        if name in prev_grades:
            delta = prev_grades[name] - gv  # negative = got worse (higher value is worse)
            deltas.append({
                'name': name,
                'prev': prev_grades[name],
                'cur': gv,
                'prev_label': _fmt_grade(prev_grades[name]),
                'cur_label': _fmt_grade(gv),
                'delta': delta,
                'improved': delta > 0,
                'declined': delta < 0,
            })

    improved = [d for d in deltas if d['improved']]
    declined = [d for d in deltas if d['declined']]

    agg_prev = prev.get('aggregate')
    agg_cur = cur.get('aggregate')
    agg_delta = None
    if agg_prev is not None and agg_cur is not None:
        agg_delta = agg_prev - agg_cur

    if agg_delta is not None:
        if agg_delta > 0:
            trend = 'IMPROVING'
        elif agg_delta < 0:
            trend = 'DECLINING'
        else:
            trend = 'STEADY'
    else:
        trend = 'UNKNOWN'

    return {
        'deltas': deltas,
        'improved': improved,
        'declined': declined,
        'agg_prev': agg_prev,
        'agg_cur': agg_cur,
        'agg_delta': agg_delta,
        'trend': trend,
    }


def analyze_overall(user, reports):
    """
    Analyze all term reports for a user.
    Returns a structured report with strengths, weaknesses, trends, and recommendations.
    """
    from core.models import SHSStreamSubject

    if not reports:
        return None

    # Sort reports chronologically by year, term
    sorted_reports = sorted(reports, key=lambda r: (r.year, r.term))

    # Analyze each term
    term_analyses = []
    for report in sorted_reports:
        analysis = analyze_term(user, report.stream, report.grades)
        term_analyses.append({
            'report': report,
            'analysis': analysis,
            'year': report.year,
            'term': report.term,
            'aggregate': analysis['aggregate'],
            'standing': analysis['standing'],
            'verdict': analysis['verdict'],
        })

    # Track subject performance across all terms
    subject_history = {}  # {subject_name: [(year, term, grade_value), ...]}
    for ta in term_analyses:
        for s in ta['analysis']['subjects']:
            if s['name'] not in subject_history:
                subject_history[s['name']] = []
            subject_history[s['name']].append({
                'year': ta['year'],
                'term': ta['term'],
                'grade_value': s['grade_value'],
                'grade_label': s['grade_label'],
                'is_core': s['is_core'],
            })

    # Find consistent strengths (grade <= 3 in 75%+ of terms)
    strengths = []
    for name, history in subject_history.items():
        strong_count = sum(1 for h in history if h['grade_value'] <= 3)
        if len(history) >= 2 and strong_count >= len(history) * 0.75:
            strengths.append({
                'name': name,
                'is_core': history[0]['is_core'],
                'grade_label': history[-1]['grade_label'],
                'consistency': round(strong_count / len(history) * 100),
            })

    # Find consistent weaknesses (grade >= 6 in 25%+ of terms, or grade >= 6 in most recent term)
    weaknesses = []
    for name, history in subject_history.items():
        weak_count = sum(1 for h in history if h['grade_value'] >= 6)
        latest_grade = history[-1]['grade_value']
        if weak_count > 0 or latest_grade >= 6:
            weaknesses.append({
                'name': name,
                'is_core': history[0]['is_core'],
                'grade_label': history[-1]['grade_label'],
                'latest_grade': latest_grade,
                'weak_count': weak_count,
                'total_terms': len(history),
            })

    # Aggregate trend (first to last)
    aggregates = [ta['aggregate'] for ta in term_analyses if ta['aggregate'] is not None]
    agg_trend = None
    if len(aggregators := [a for a in aggregates if a is not None]) >= 2:
        agg_trend = 'IMPROVING' if aggregates[-1] < aggregates[0] else (
            'DECLINING' if aggregates[-1] > aggregates[0] else 'STEADY'
        )

    # Subject-specific trend
    improved_subjects = []
    declined_subjects = []
    for name, history in subject_history.items():
        if len(history) >= 2:
            first_grade = history[0]['grade_value']
            last_grade = history[-1]['grade_value']
            if last_grade < first_grade:
                improved_subjects.append(name)
            elif last_grade > first_grade:
                declined_subjects.append(name)

    # Overall recommendation
    latest_analysis = term_analyses[-1]['analysis']
    all_grades = []
    for ta in term_analyses:
        for s in ta['analysis']['subjects']:
            all_grades.append(s['grade_value'])

    avg_aggregate = sum(a for a in aggregates if a is not None) / len(aggregates) if aggregates else None

    if avg_aggregate is not None:
        if avg_aggregate <= 15:
            recommendation = 'Excellent! Your consistent performance puts strong university programmes well within reach. Keep sustaining your strong subjects and maintain focus across all areas.'
        elif avg_aggregate <= 20:
            recommendation = 'Good progress overall. Focus on improving your weakest subjects — even small grade improvements will significantly increase your aggregate and programme options.'
        elif avg_aggregate <= 27:
            recommendation = 'You have potential but need targeted improvement. Prioritise your core subjects (English, Math, Science/Social Studies) and address elective weaknesses immediately.'
        else:
            recommendation = 'Significant improvement needed. Create a study plan focusing on failing subjects, seek extra help, and consider speaking with your teacher or counselor.'
    else:
        recommendation = 'Incomplete performance data. Upload more term results to get detailed recommendations.'

    # Year-by-year breakdown
    year_terms = []
    for ta in term_analyses:
        year_terms.append({
            'year': ta['year'],
            'term': ta['term'],
            'aggregate': ta['aggregate'],
            'standing': ta['standing'],
            'label': f"SHS {ta['year']} Term {ta['term']}",
        })

    # All subjects with full history
    all_subjects = []
    for name, history in sorted(subject_history.items(), key=lambda x: (not x[1][0]['is_core'], x[0])):
        grade_cells = []
        for h in history:
            grade_cells.append({
                'label': h['grade_label'],
                'value': h['grade_value'],
            })
        all_subjects.append({
            'name': name,
            'is_core': history[0]['is_core'],
            'latest_grade': history[-1]['grade_label'] if history else '—',
            'grade_cells': grade_cells,
        })

    return {
        'term_analyses': term_analyses,
        'subject_history': all_subjects,
        'strengths': strengths,
        'weaknesses': weaknesses,
        'agg_trend': agg_trend,
        'aggregates': aggregates,
        'avg_aggregate': round(avg_aggregate, 1) if avg_aggregate is not None else None,
        'improved_subjects': improved_subjects,
        'declined_subjects': declined_subjects,
        'recommendation': recommendation,
        'year_terms': year_terms,
        'latest_standing': latest_analysis['standing'],
        'latest_verdict': latest_analysis['verdict'],
        'likely_programs': latest_analysis['likely'],
    }