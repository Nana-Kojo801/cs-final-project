"""Appointment model - scheduling + reminders + no-show tracking (operational)."""

from datetime import datetime, timedelta

from utils.storage import read_json, update_json

STATUSES = ("Scheduled", "Attended", "No-show", "Cancelled")


def _next_id(data):
    nums = [int(k) for k in data if k.isdigit()]
    return str(max(nums) + 1 if nums else 1)


def create(clinic_id, patient_id, clinician_id, when, reason=""):
    def _m(data):
        aid = _next_id(data)
        data[aid] = {
            "clinic_id": str(clinic_id), "patient_id": str(patient_id),
            "clinician_id": str(clinician_id), "when": when, "reason": reason,
            "status": "Scheduled", "reminder_sent": False,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        return data
    data = update_json("appointments", _m, {})
    return max((k for k in data if k.isdigit()), key=int)


def get(aid):
    return read_json("appointments", {}).get(str(aid))


def for_patient(patient_id):
    return {aid: a for aid, a in read_json("appointments", {}).items()
            if a["patient_id"] == str(patient_id)}


def for_clinic(clinic_id):
    return {aid: a for aid, a in read_json("appointments", {}).items()
            if a["clinic_id"] == str(clinic_id)}


def set_status(aid, status):
    if status not in STATUSES:
        raise ValueError(status)

    def _m(data):
        if str(aid) in data:
            data[str(aid)]["status"] = status
        return data
    update_json("appointments", _m, {})


def due_for_reminder(within_hours=24):
    now = datetime.now()
    out = []
    for aid, a in read_json("appointments", {}).items():
        if a["status"] != "Scheduled" or a["reminder_sent"]:
            continue
        try:
            when = datetime.fromisoformat(a["when"])
        except ValueError:
            continue
        if now <= when <= now + timedelta(hours=within_hours):
            out.append((aid, a))
    return out


def mark_reminder_sent(aid):
    def _m(data):
        if str(aid) in data:
            data[str(aid)]["reminder_sent"] = True
        return data
    update_json("appointments", _m, {})
