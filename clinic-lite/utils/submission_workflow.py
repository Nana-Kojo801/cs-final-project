"""Cross-model workflows: submission, review, appointment attendance, reminders.

Keeps app.py routes thin and gives tests a single entry point per workflow.
"""

from datetime import date, datetime

from models import announcement as ann_model
from models import appointment as appt_model
from models import clinic as clinic_model
from models import health_task as task_model
from models import task_submission as sub_model
from models import user as user_model
from utils import completeness, engagement
from utils.email_handler import send_notification
from utils.file_handler import FileError, save_stream, save_bytes


class WorkflowError(Exception):
    pass


# --------------------------------------------------------------------- submit
def _prevalidate(task_id, patient_id):
    task = task_model.get(task_id)
    if not task:
        raise WorkflowError("That health task does not exist.")
    if not task_model.is_assigned(task_id, patient_id):
        raise WorkflowError("This task is not assigned to you.")
    existing = sub_model.get(patient_id, task_id)
    if existing and existing.review_status != "Pending":
        raise WorkflowError("This submission has already been reviewed and cannot be replaced.")
    return task


def submit_task(patient_id, task_id, *, file_storage=None, content=None, ext=None):
    patient = user_model.get(patient_id)
    task = _prevalidate(task_id, patient_id)
    clinic_id = task.clinic_id
    try:
        if file_storage is not None:
            path = save_stream(file_storage, clinic_id, patient_id, task_id)
        else:
            path = save_bytes(content, clinic_id, patient_id, task_id, ext)
    except FileError as e:
        raise WorkflowError(str(e))

    check = completeness.check_submission(path, task.check_spec)
    on_time = bool(task.due_date) and date.today().isoformat() <= task.due_date

    sub = sub_model.TaskSubmission(
        patient_id, task_id, path, clinic_id,
        review_status="Pending", completeness=check, on_time=on_time)
    sub.save()

    engagement.record_event(patient_id, "task", on_time, ref=task_id)

    clinic = clinic_model.get(clinic_id)
    clinician = user_model.get(clinic.clinician_id) if clinic else None
    if clinician:
        send_notification(
            clinician.email,
            f"New submission for task '{task.title}'",
            f"Patient {patient.name} ({patient_id}) submitted task {task_id} on "
            f"{sub.timestamp}. Completeness check: "
            f"{'passed' if check.get('ok') else 'issues: ' + '; '.join(check.get('issues', []))}.",
            recipient_id=clinician.user_id)
    send_notification(
        patient.email, f"Submission received: {task.title}",
        f"We received your submission for '{task.title}' at {sub.timestamp}. "
        f"You'll be notified when a clinician has reviewed it.",
        recipient_id=patient_id)
    return sub, check


# --------------------------------------------------------------------- review
def review_submission(clinician_id, patient_id, task_id, outcome, notes):
    clinician = user_model.get(clinician_id)
    if not clinician or clinician.role != "clinician":
        raise WorkflowError("Only a clinician can review submissions.")
    if not clinic_model.shares_clinic(clinician_id, patient_id):
        raise WorkflowError("That patient is not registered to your clinic.")
    sub = sub_model.get(patient_id, task_id)
    if not sub:
        raise WorkflowError("No submission to review.")

    sub_model.record_review(patient_id, task_id, clinician_id, outcome, notes)
    task = task_model.get(task_id)
    patient = user_model.get(patient_id)
    send_notification(
        patient.email, f"Your submission for '{task.title}' has been reviewed",
        f"Outcome: {outcome}\n"
        f"Clinician notes: {notes or '(none)'}\n\n"
        f"This is an administrative review outcome, not a diagnosis. "
        f"Contact the clinic if you have questions.",
        recipient_id=patient_id)
    sub_model.mark_notified(patient_id, task_id)
    return outcome
