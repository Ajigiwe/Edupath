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
    for name, gv in cleaned.items():
        subj = {
            'name': name,
            'grade_value': gv,
            'grade_label': _fmt_grade(gv),
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