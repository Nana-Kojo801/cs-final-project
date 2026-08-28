"""Input validation for ClinicCare-Lite (IDs, passwords, files, form fields)."""

import os
import re

from config import (ALLOWED_EXTENSIONS, PATIENT_YEAR_MAX, PATIENT_YEAR_MIN)

ID_RE = re.compile(r"^\d{8}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SPECIAL_RE = re.compile(r"[!@#$%^&*()_\-+=\[\]{};:'\",.<>/?\\|`~]")


def validate_id(user_id, role):
    """8 digits; clinician ends 0000; patient ends in a year 2022..2028."""
    user_id = str(user_id)
    if not ID_RE.match(user_id):
        return False, "ID must be exactly 8 digits."
    if role == "clinician":
        if user_id[-4:] != "0000":
            return False, "Clinician IDs must end in 0000."
    elif role == "patient":
        year = int(user_id[-4:])
        if not (PATIENT_YEAR_MIN <= year <= PATIENT_YEAR_MAX):
            return False, f"Patient IDs must end in a year {PATIENT_YEAR_MIN}-{PATIENT_YEAR_MAX}."
    else:
        return False, "Unknown role."
    return True, "OK"


def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password needs an uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password needs a lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password needs a digit."
    if not SPECIAL_RE.search(password):
        return False, "Password needs a special character."
    return True, "OK"


def validate_email(email):
    return bool(EMAIL_RE.match((email or "").strip()))


def validate_extension(filename):
    ext = os.path.splitext(filename or "")[1].lower()
    return ext in ALLOWED_EXTENSIONS, ext


def require_fields(form, fields):
    """Return a list of missing/blank field names."""
    return [f for f in fields if not (form.get(f) or "").strip()]
