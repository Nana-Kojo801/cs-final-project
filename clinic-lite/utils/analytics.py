"""Operational analytics.

Clinician view  -> aggregated operational metrics for THEIR clinic only.
Patient view    -> that patient's own history only.

No function mixes the two. Nothing here exposes one patient's data to another.
"""

from collections import Counter
from datetime import date, datetime

from models import appointment as appt_model
from models import health_task as task_model
from models import task_submission as sub_model


def _parse(d):
    try:
        return datetime.fromisoformat(d)
    except (ValueError, TypeError):
        return None


def clinic_operational(clinic_id):
    appts = appt_model.for_clinic(clinic_id)
    subs = sub_model.for_clinic(clinic_id)
    tasks = task_model.for_clinic(clinic_id)

    finished = [a for a in appts.values() if a["status"] in ("Attended", "No-show")]
    no_shows = [a for a in finished if a["status"] == "No-show"]
    no_show_rate = round(100 * len(no_shows) / len(finished), 1) if finished else 0.0

    by_week = {}
    for a in finished:
        w = _parse(a["when"])
        if not w:
            continue
        key = f"{w.isocalendar().year}-W{w.isocalendar().week:02d}"
        d = by_week.setdefault(key, {"total": 0, "no_show": 0})
        d["total"] += 1
        d["no_show"] += (a["status"] == "No-show")
    no_show_by_week = {k: round(100 * v["no_show"] / v["total"], 1)
                       for k, v in sorted(by_week.items())}

    total_expected = 0
    for t in tasks:
        total_expected += len(task_model.patients_for_task(t.task_id))
    submitted = len(subs)
    completion_rate = round(100 * submitted / total_expected, 1) if total_expected else 0.0

    pending = [s for s in subs if s.review_status == "Pending"]
    turnarounds = []
    for s in subs:
        if s.reviewed_at and s.timestamp:
            a, b = _parse(s.timestamp), _parse(s.reviewed_at)
            if a and b:
                turnarounds.append((b - a).total_seconds() / 3600)
    avg_turnaround = round(sum(turnarounds) / len(turnarounds), 1) if turnarounds else None

    today = date.today().isoformat()
    overdue = 0
    for t in tasks:
        if t.due_date and t.due_date < today:
            for p in task_model.patients_for_task(t.task_id):
                if not sub_model.get(p, t.task_id):
                    overdue += 1

    submissions_by_task = Counter(s.task_id for s in subs)
    monthly_appts = Counter(
        (_parse(a["when"]).strftime("%Y-%m") if _parse(a["when"]) else "unknown")
        for a in appts.values())

    return {
        "appointment_no_show_rate": no_show_rate,
        "no_show_rate_by_week": no_show_by_week,
        "task_completion_rate": completion_rate,
        "pending_reviews": len(pending),
        "avg_review_turnaround_hours": avg_turnaround,
        "monthly_task_volume": len(tasks),
        "overdue_submissions": overdue,
        "submissions_by_task": {task_model.get(tid).title if task_model.get(tid) else tid: n
                                for tid, n in submissions_by_task.items()},
        "monthly_appointment_volume": dict(sorted(monthly_appts.items())),
        "review_outcome_mix": dict(Counter(s.review_status for s in subs)),
    }


def patient_personal(patient_id):
    appts = appt_model.for_patient(patient_id)
    subs = sub_model.for_patient(patient_id)
    finished = [a for a in appts.values() if a["status"] in ("Attended", "No-show")]
    attended = [a for a in finished if a["status"] == "Attended"]

    by_month = Counter()
    for s in subs:
        m = _parse(s.timestamp)
        if m:
            by_month[m.strftime("%Y-%m")] += 1

    return {
        "tasks_submitted": len(subs),
        "reviews_received": sum(1 for s in subs if s.review_status != "Pending"),
        "appointments_total": len(appts),
        "appointments_attended": len(attended),
        "attendance_rate": round(100 * len(attended) / len(finished), 1) if finished else None,
        "submission_trend_by_month": dict(sorted(by_month.items())),
        "outcome_mix": dict(Counter(s.review_status for s in subs)),
    }
