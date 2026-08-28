"""Clinic model - groups one clinician with their registered patients."""

from utils.storage import read_json, update_json


class Clinic:
    def __init__(self, clinic_id, name, clinician_id, patient_ids=None):
        self.clinic_id = str(clinic_id)
        self.name = name
        self.clinician_id = str(clinician_id)
        self.patient_ids = [str(p) for p in (patient_ids or [])]

    def to_dict(self):
        return {"name": self.name, "clinician_id": self.clinician_id,
                "patient_ids": self.patient_ids}

    @classmethod
    def from_dict(cls, cid, d):
        return cls(cid, d["name"], d["clinician_id"], d.get("patient_ids", []))

    def save(self):
        update_json("clinics", lambda data: {**data, self.clinic_id: self.to_dict()}, {})
        return self


def get(clinic_id):
    d = read_json("clinics", {}).get(str(clinic_id))
    return Clinic.from_dict(str(clinic_id), d) if d else None


def all_clinics():
    return [Clinic.from_dict(cid, d) for cid, d in read_json("clinics", {}).items()]


def for_clinician(clinician_id):
    for cid, d in read_json("clinics", {}).items():
        if d["clinician_id"] == str(clinician_id):
            return Clinic.from_dict(cid, d)
    return None


def for_patient(patient_id):
    for cid, d in read_json("clinics", {}).items():
        if str(patient_id) in d.get("patient_ids", []):
            return Clinic.from_dict(cid, d)
    return None


def add_patient(clinic_id, patient_id):
    def _m(data):
        c = data.get(str(clinic_id))
        if c and str(patient_id) not in c["patient_ids"]:
            c["patient_ids"].append(str(patient_id))
        return data
    update_json("clinics", _m, {})


def shares_clinic(clinician_id, patient_id):
    c = for_clinician(clinician_id)
    return bool(c and str(patient_id) in c.patient_ids)
