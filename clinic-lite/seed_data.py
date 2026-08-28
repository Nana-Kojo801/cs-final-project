"""Seed ClinicCare-Lite with fictional demo accounts and a full sample workflow.

All accounts are fictional. Default password for every demo account:  Clinic@2026

Run:  python seed_data.py            # create data/ + demo content (idempotent-ish)
      python seed_data.py --reset    # wipe data/ and submissions/ first
"""

import os
import shutil
import sys
from datetime import datetime, timedelta

import config
from utils.storage import ensure_data_files, write_json
from models import user as user_model
from models import clinic as clinic_model
from models import health_task as task_model
from models import appointment as appt_model
from models import message as msg_model
from utils import submission_workflow, comms_workflow

PW = "Clinic@2026"
CLINICIAN_ID = "10000000"
PATIENTS = [
    ("20142024", "Akosua Boadu", "akosua@example.com"),
    ("20232023", "Kwesi Appiah", "kwesi@example.com"),
    ("20452022", "Ama Darko", "ama@example.com"),
]


def _reset():
    for name in ("users", "clinics", "health_tasks", "task_assignments",
                 "task_submissions", "messages", "appointments", "announcements",
                 "engagement", "notifications"):
        p = os.path.join(config.DATA_DIR, f"{name}.json")
        if os.path.exists(p):
            os.remove(p)
    log = os.path.join(config.DATA_DIR, "notifications.log")
    if os.path.exists(log):
        os.remove(log)
    if os.path.isdir(config.SUBMISSIONS_DIR):
        shutil.rmtree(config.SUBMISSIONS_DIR)
    os.makedirs(config.SUBMISSIONS_DIR, exist_ok=True)


def seed(reset=False):
    if reset:
        _reset()
    ensure_data_files()

    clinician, err = user_model.register(CLINICIAN_ID, "Dr. Nana Mensima",
                                         "clinician@example.com", PW, "clinician")
    if err and "already" not in err:
        raise SystemExit(err)
    clinician = clinician or user_model.get(CLINICIAN_ID)
    clinic = clinic_model.for_clinician(CLINICIAN_ID) or clinic_model.Clinic(
        "c1", "Ridge Family Clinic", CLINICIAN_ID, []).save()

    patient_objs = []
    for pid, name, email in PATIENTS:
        p, err = user_model.register(pid, name, email, PW, "patient")
        p = p or user_model.get(pid)
        patient_objs.append(p)
        clinic_model.add_patient(clinic.clinic_id, pid)

    if task_model.for_clinic(clinic.clinic_id):
        print("Tasks already present - skipping sample workflow.")
        _print_accounts()
        return

    due_soon = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    past_due = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")

    t1 = task_model.create(
        "Weekly home blood-pressure log", "Record your morning and evening readings for one week "
        "and upload the CSV. Columns: date, systolic, diastolic.", due_soon, clinic.clinic_id,
        CLINICIAN_ID, check_spec={"expected_columns": ["date", "systolic", "diastolic"],
                                  "numeric_columns": ["systolic", "diastolic"]})
    t2 = task_model.create(
        "Upload referral letter", "Upload the scanned referral letter from your previous clinic (PDF).",
        due_soon, clinic.clinic_id, CLINICIAN_ID)
    t3 = task_model.create(
        "Medication list (text)", "List your current medications, one per line as 'Name: dose'.",
        past_due, clinic.clinic_id, CLINICIAN_ID,
        check_spec={"required_labels": ["Name", "Date"]})

    task_model.assign(t1.task_id, [p.user_id for p in patient_objs])
    task_model.assign(t2.task_id, [patient_objs[0].user_id, patient_objs[1].user_id])
    task_model.assign(t3.task_id, [patient_objs[0].user_id])

    # patient 1 submits task 1 (a valid CSV) -> clinician reviews it
    csv_bytes = (b"date,systolic,diastolic\n"
                 b"2026-08-20,128,82\n2026-08-21,124,79\n2026-08-22,130,85\n")
    submission_workflow.submit_task(patient_objs[0].user_id, t1.task_id, content=csv_bytes, ext=".csv")
    submission_workflow.review_submission(CLINICIAN_ID, patient_objs[0].user_id, t1.task_id,
                               "Reviewed - Normal", "Readings received, no action needed. "
                               "Keep logging for the full week.")

    # patient 2 submits task 1 with a structural problem (missing column)
    submission_workflow.submit_task(patient_objs[1].user_id, t1.task_id,
                         content=b"date,systolic\n2026-08-20,128\n", ext=".csv")

    # appointments
    appt_model.create(clinic.clinic_id, patient_objs[0].user_id, CLINICIAN_ID,
                      (datetime.now() + timedelta(days=1, hours=2)).isoformat(timespec="minutes"),
                      "BP follow-up")
    aid_past = appt_model.create(
        clinic.clinic_id, patient_objs[1].user_id, CLINICIAN_ID,
        (datetime.now() - timedelta(days=5)).isoformat(timespec="minutes"), "Initial consult")
    appt_model.set_status(aid_past, "No-show")
    aid_att = appt_model.create(
        clinic.clinic_id, patient_objs[2].user_id, CLINICIAN_ID,
        (datetime.now() - timedelta(days=3)).isoformat(timespec="minutes"), "Review")
    comms_workflow.mark_attendance(clinic.clinic_id, aid_att, "Attended")

    # announcement + messages
    comms_workflow.post_announcement(CLINICIAN_ID, "Flu vaccination clinic",
                               "Walk-in flu vaccinations available next week, 9am-1pm.",
                               False, None, None)
    msg_model.send(patient_objs[0].user_id, CLINICIAN_ID,
                   "Hi, should I keep taking the morning tablet during the log week?")
    msg_model.send(CLINICIAN_ID, patient_objs[0].user_id,
                   "Yes, continue as normal. We'll review at your appointment.")

    comms_workflow.run_reminder_job()
    print("Seeded clinic, 3 patients, 3 tasks, 2 submissions (1 reviewed), 3 appointments, "
          "1 announcement, 1 message thread.")
    _print_accounts()


def _print_accounts():
    print(f"\nDemo accounts (password {PW}):")
    print(f"  clinician  {CLINICIAN_ID}  Dr. Nana Mensima")
    for pid, name, _ in PATIENTS:
        print(f"  patient    {pid}  {name}")


if __name__ == "__main__":
    seed(reset="--reset" in sys.argv)
