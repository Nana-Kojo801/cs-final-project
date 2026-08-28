"""Secure file handling for patient submissions.

Rules enforced here (per the brief):
  * only .txt / .csv / .pdf
  * renamed systematically to  patientID_taskID.ext
  * stored under submissions/<clinicID>/<patientID>/
  * size limit
  * no path traversal - the destination is rebuilt from validated ids only
"""

import os
import shutil

from config import ALLOWED_EXTENSIONS, MAX_UPLOAD_BYTES, SUBMISSIONS_DIR
from utils.validator import validate_extension


class FileError(Exception):
    pass


def _safe_component(value):
    """Allow only digits/letters/dash/underscore - blocks '..' and separators."""
    value = str(value)
    if not value or not all(c.isalnum() or c in "-_" for c in value):
        raise FileError(f"Unsafe path component: {value!r}")
    return value


def target_path(clinic_id, patient_id, task_id, ext):
    clinic_id = _safe_component(clinic_id)
    patient_id = _safe_component(patient_id)
    task_id = _safe_component(task_id)
    ext = ext.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise FileError(f"Extension {ext} not allowed.")
    folder = os.path.join(SUBMISSIONS_DIR, clinic_id, patient_id)
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, f"{patient_id}_{task_id}{ext}")


def save_stream(file_storage, clinic_id, patient_id, task_id):
    """Validate + persist a Werkzeug FileStorage. Returns the stored path."""
    ok, ext = validate_extension(file_storage.filename)
    if not ok:
        raise FileError("Only .txt, .csv and .pdf files are accepted.")

    file_storage.stream.seek(0, os.SEEK_END)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)
    if size == 0:
        raise FileError("The uploaded file is empty.")
    if size > MAX_UPLOAD_BYTES:
        raise FileError(f"File is too large ({size} bytes; limit {MAX_UPLOAD_BYTES}).")

    dest = target_path(clinic_id, patient_id, task_id, ext)
    file_storage.save(dest)
    return dest


def save_bytes(content, clinic_id, patient_id, task_id, ext):
    """Non-web variant used by tests / seed."""
    ok = ext.lower() in ALLOWED_EXTENSIONS
    if not ok:
        raise FileError("Only .txt, .csv and .pdf files are accepted.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise FileError("File is too large.")
    dest = target_path(clinic_id, patient_id, task_id, ext)
    with open(dest, "wb") as f:
        f.write(content)
    return dest


def read_preview(path, max_rows=50):
    """Return a small text/table preview for the clinician UI (never interprets it)."""
    ext = os.path.splitext(path)[1].lower()
    if not os.path.exists(path):
        return {"kind": "missing", "content": ""}
    if ext == ".pdf":
        return {"kind": "pdf", "content": f"{os.path.basename(path)} "
                                          f"({os.path.getsize(path)} bytes) - download to view."}
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()
    if ext == ".csv":
        rows = [ln.split(",") for ln in lines[:max_rows]]
        return {"kind": "csv", "content": rows}
    return {"kind": "text", "content": "\n".join(lines[:max_rows])}
