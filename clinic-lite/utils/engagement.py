"""Private wellness-engagement tracker.

Engagement Points (EP) reward on-time task completion and on-time appointment
attendance. DELIBERATELY NOT A LEADERBOARD: every function here is scoped to a
single ``patient_id`` and there is no cross-patient query anywhere in the
module. The data is visible only to the patient who earned it.
"""

from collections import Counter
from datetime import datetime

from models import user as user_model
from utils.storage import read_json, update_json

POINTS_ON_TIME_TASK = 10
POINTS_LATE_TASK = 2
POINTS_ON_TIME_APPT = 8


def _log(patient_id):
    return read_json("engagement", {}).get(str(patient_id), [])


def record_event(patient_id, kind, on_time, ref):
    """kind in {'task','appointment'}. Adds an EP event for this patient only."""
    points = 0
    if kind == "task":
        points = POINTS_ON_TIME_TASK if on_time else POINTS_LATE_TASK
    elif kind == "appointment":
        points = POINTS_ON_TIME_APPT if on_time else 0

    def _m(data):
        entries = data.setdefault(str(patient_id), [])
        if any(e["kind"] == kind and e["ref"] == str(ref) for e in entries):
            return data  # idempotent - don't double-count
        entries.append({
            "kind": kind, "ref": str(ref), "on_time": bool(on_time),
            "points": points, "timestamp": datetime.now().isoformat(timespec="seconds"),
        })
        return data
    update_json("engagement", _m, {})
    if points:
        user_model.add_engagement_points(patient_id, points)


def summary(patient_id):
    """Everything the patient's own dashboard needs. No other patient's data."""
    entries = _log(patient_id)
    total = sum(e["points"] for e in entries)
    on_time_tasks = sum(1 for e in entries if e["kind"] == "task" and e["on_time"])
    on_time_appts = sum(1 for e in entries if e["kind"] == "appointment" and e["on_time"])

    # current on-time task streak (most recent tasks, newest first)
    task_events = sorted([e for e in entries if e["kind"] == "task"],
                         key=lambda e: e["timestamp"], reverse=True)
    streak = 0
    for e in task_events:
        if e["on_time"]:
            streak += 1
        else:
            break

    by_month = Counter()
    for e in entries:
        if e["on_time"]:
            by_month[e["timestamp"][:7]] += 1

    return {
        "total_points": total,
        "on_time_tasks": on_time_tasks,
        "on_time_appointments": on_time_appts,
        "current_streak": streak,
        "on_time_by_month": dict(sorted(by_month.items())),
        "events": sorted(entries, key=lambda e: e["timestamp"], reverse=True),
    }
