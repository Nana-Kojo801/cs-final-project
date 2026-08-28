"""TaskSubmission model - a patient's file submission against a health task.

Review outcomes are CATEGORICAL administrative statuses, never numeric scores
and never automated diagnoses:
    Pending / Reviewed - Normal / Needs Follow-up / Escalated
"""

from datetime import datetime

from utils.storage import read_json, update_json

REVIEW_OUTCOMES = ("Pending", "Reviewed - Normal", "Needs Follow-up", "Escalated")


class TaskSubmission:
    def __init__(self, patient_id, task_id, file_path, clinic_id,
                 timestamp=None, review_status="Pending", notes=None,
                 reviewer_id=None, reviewed_at=None, notified=False,
                 completeness=None, on_time=None):
        self.patient_id = str(patient_id)
        self.task_id = str(task_id)
        self.file_path = file_path
        self.clinic_id = str(clinic_id)
        self.timestamp = timestamp or datetime.now().isoformat(timespec="seconds")
        self.review_status = review_status
        self.notes = notes
        self.reviewer_id = reviewer_id
        self.reviewed_at = reviewed_at
        self.notified = notified
        self.completeness = completeness or {}
        self.on_time = on_time

    @property
    def key(self):
        return f"{self.patient_id}_{self.task_id}"

    def to_dict(self):
        return {k: getattr(self, k) for k in (
            "patient_id", "task_id", "file_path", "clinic_id", "timestamp",
            "review_status", "notes", "reviewer_id", "reviewed_at", "notified",
            "completeness", "on_time")}

    @classmethod
    def from_dict(cls, d):
        return cls(**{k: d.get(k) for k in (
            "patient_id", "task_id", "file_path", "clinic_id", "timestamp",
            "review_status", "notes", "reviewer_id", "reviewed_at", "notified",
            "completeness", "on_time")})

    def save(self):
        update_json("task_submissions",
                    lambda data: {**data, self.key: self.to_dict()}, {})
        return self


def get(patient_id, task_id):
    d = read_json("task_submissions", {}).get(f"{patient_id}_{task_id}")
    return TaskSubmission.from_dict(d) if d else None


def for_clinic(clinic_id, task_id=None, patient_id=None, status=None):
    out = []
    for d in read_json("task_submissions", {}).values():
        if d["clinic_id"] != str(clinic_id):
            continue
        if task_id and d["task_id"] != str(task_id):
            continue
        if patient_id and d["patient_id"] != str(patient_id):
            continue
        if status and d["review_status"] != status:
            continue
        out.append(TaskSubmission.from_dict(d))
    return sorted(out, key=lambda s: s.timestamp, reverse=True)


def for_patient(patient_id):
    return [TaskSubmission.from_dict(d) for d in read_json("task_submissions", {}).values()
            if d["patient_id"] == str(patient_id)]


def record_review(patient_id, task_id, reviewer_id, outcome, notes):
    if outcome not in REVIEW_OUTCOMES:
        raise ValueError(f"Invalid review outcome: {outcome}")

    def _m(data):
        d = data.get(f"{patient_id}_{task_id}")
        if d:
            d["review_status"] = outcome
            d["notes"] = notes
            d["reviewer_id"] = str(reviewer_id)
            d["reviewed_at"] = datetime.now().isoformat(timespec="seconds")
            d["notified"] = False
        return data
    update_json("task_submissions", _m, {})


def mark_notified(patient_id, task_id):
    def _m(data):
        d = data.get(f"{patient_id}_{task_id}")
        if d:
            d["notified"] = True
        return data
    update_json("task_submissions", _m, {})
