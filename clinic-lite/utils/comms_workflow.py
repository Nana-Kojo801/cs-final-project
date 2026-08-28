"""Communication workflows: appointments, reminders, announcements (issue #12)."""

from datetime import date, datetime

from models import announcement as ann_model
from models import appointment as appt_model
from models import clinic as clinic_model
from models import user as user_model
from utils import engagement
from utils.email_handler import send_notification


class WorkflowError(Exception):
    pass


# ---------------------------------------------------------------- appointments
def mark_attendance(clinic_id, appointment_id, status):
    a = appt_model.get(appointment_id)
    if not a or a["clinic_id"] != str(clinic_id):
        raise WorkflowError("Appointment not found for this clinic.")
    appt_model.set_status(appointment_id, status)
    if status == "Attended":
        when = datetime.fromisoformat(a["when"]) if a.get("when") else None
        on_time = bool(when) and when >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        engagement.record_event(a["patient_id"], "appointment", True, ref=appointment_id)
    return status


def run_reminder_job():
    """Send 24h reminders for appointments and due-soon tasks. Returns count sent."""
    sent = 0
    for aid, a in appt_model.due_for_reminder(24):
        patient = user_model.get(a["patient_id"])
        if patient:
            send_notification(
                patient.email, "Appointment reminder",
                f"Reminder: you have an appointment on {a['when']}. "
                f"Reason: {a.get('reason') or 'n/a'}.",
                recipient_id=patient.user_id)
            appt_model.mark_reminder_sent(aid)
            sent += 1
    return sent


# ---------------------------------------------------------------- announcements
def post_announcement(clinician_id, title, body, urgent, publish_date, expiry_date):
    clinic = clinic_model.for_clinician(clinician_id)
    if not clinic:
        raise WorkflowError("No clinic found for this clinician.")
    aid = ann_model.create(clinic.clinic_id, clinician_id, title, body, urgent,
                           publish_date or None, expiry_date or None)
    if urgent:
        for pid in clinic.patient_ids:
            p = user_model.get(pid)
            if p:
                send_notification(p.email, f"Clinic announcement: {title}", body,
                                  recipient_id=pid)
    return aid
