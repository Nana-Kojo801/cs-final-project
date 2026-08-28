"""HealthTask model + task-to-patient assignments.

A HealthTask is administrative: title, instructions, due date, optional
structural-check spec, optional attachment. Assignments live in a separate
collection (task_id -> [patient_id, ...]).
"""

from datetime import datetime

from utils.storage import read_json, update_json


class HealthTask:
    def __init__(self, task_id, title, description, due_date, clinic_id,
                 created_by, attachment=None, check_spec=None, created_at=None):
        self.task_id = str(task_id)
        self.title = title
        self.description = description
        self.due_date = due_date          # YYYY-MM-DD
        self.clinic_id = str(clinic_id)
        self.created_by = str(created_by)
        self.attachment = attachment
        self.check_spec = check_spec or {}
        self.created_at = created_at or datetime.now().isoformat(timespec="seconds")

    def to_dict(self):
        return {"title": self.title, "description": self.description,
                "due_date": self.due_date, "clinic_id": self.clinic_id,
                "created_by": self.created_by, "attachment": self.attachment,
                "check_spec": self.check_spec, "created_at": self.created_at}

    @classmethod
    def from_dict(cls, tid, d):
        return cls(tid, d["title"], d["description"], d["due_date"], d["clinic_id"],
                   d["created_by"], d.get("attachment"), d.get("check_spec"),
                   d.get("created_at"))

    def save(self):
        update_json("health_tasks", lambda data: {**data, self.task_id: self.to_dict()}, {})
        return self


def _next_id(data):
    nums = [int(k) for k in data if k.isdigit()]
    return str(max(nums) + 1 if nums else 1)


def create(title, description, due_date, clinic_id, created_by,
           attachment=None, check_spec=None):
    data = read_json("health_tasks", {})
    tid = _next_id(data)
    task = HealthTask(tid, title, description, due_date, clinic_id, created_by,
                      attachment, check_spec)
    task.save()
    return task


def get(task_id):
    d = read_json("health_tasks", {}).get(str(task_id))
    return HealthTask.from_dict(str(task_id), d) if d else None


def for_clinic(clinic_id):
    return [HealthTask.from_dict(t, d) for t, d in read_json("health_tasks", {}).items()
            if d["clinic_id"] == str(clinic_id)]


# --------------------------------------------------------------- assignments
def assign(task_id, patient_ids):
    def _m(data):
        cur = set(data.get(str(task_id), []))
        cur.update(str(p) for p in patient_ids)
        data[str(task_id)] = sorted(cur)
        return data
    update_json("task_assignments", _m, {})


def patients_for_task(task_id):
    return read_json("task_assignments", {}).get(str(task_id), [])


def tasks_for_patient(patient_id):
    assigned = []
    amap = read_json("task_assignments", {})
    for tid, pids in amap.items():
        if str(patient_id) in pids:
            t = get(tid)
            if t:
                assigned.append(t)
    return assigned


def is_assigned(task_id, patient_id):
    return str(patient_id) in read_json("task_assignments", {}).get(str(task_id), [])
