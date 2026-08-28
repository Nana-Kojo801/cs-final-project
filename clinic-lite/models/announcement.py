"""Clinic announcement model - clinic-wide notices on the patient dashboard."""

from datetime import date, datetime

from utils.storage import read_json, update_json


def _next_id(data):
    nums = [int(k) for k in data if k.isdigit()]
    return str(max(nums) + 1 if nums else 1)


def create(clinic_id, author_id, title, body, urgent=False,
           publish_date=None, expiry_date=None):
    def _m(data):
        aid = _next_id(data)
        data[aid] = {
            "clinic_id": str(clinic_id), "author_id": str(author_id),
            "title": title, "body": body, "urgent": bool(urgent),
            "publish_date": publish_date or date.today().isoformat(),
            "expiry_date": expiry_date,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        return data
    data = update_json("announcements", _m, {})
    return max((k for k in data if k.isdigit()), key=int)


def active_for_clinic(clinic_id, on=None):
    on = on or date.today().isoformat()
    out = []
    for aid, a in read_json("announcements", {}).items():
        if a["clinic_id"] != str(clinic_id):
            continue
        if a["publish_date"] > on:
            continue
        if a.get("expiry_date") and a["expiry_date"] < on:
            continue
        out.append({"id": aid, **a})
    return sorted(out, key=lambda a: (not a["urgent"], a["publish_date"]), reverse=False)


def all_for_clinic(clinic_id):
    return [{"id": aid, **a} for aid, a in read_json("announcements", {}).items()
            if a["clinic_id"] == str(clinic_id)]
