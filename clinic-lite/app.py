from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify


# ---------------------------------------------------------------------------
# Application setup
# ---------------------------------------------------------------------------

APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / "clinic_data.json"
UPLOAD_DIR = APP_DIR / "uploads"
MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MiB per submission
ALLOWED_EXTENSIONS = {"txt", "csv", "pdf"}

DEFAULT_DATA = {
    "tasks": [],
    "submissions": [],
    "notifications": [],
}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# JSON storage helpers
# ---------------------------------------------------------------------------

def utc_now() -> str:
    """Return a consistent UTC timestamp for stored records."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_data() -> dict:
    """Load the JSON store, creating the required top-level collections."""
    if not DATA_FILE.exists() or DATA_FILE.stat().st_size == 0:
        save_data(DEFAULT_DATA)
        return json.loads(json.dumps(DEFAULT_DATA))

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        data = json.loads(json.dumps(DEFAULT_DATA))

    for collection in DEFAULT_DATA:
        if not isinstance(data.get(collection), list):
            data[collection] = []
    return data


def save_data(data: dict) -> None:
    """Persist JSON using UTF-8 and readable formatting."""
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def new_id(prefix: str) -> str:
    """Create a readable unique identifier for a stored record."""
    return f"{prefix}_{uuid4().hex[:12]}"


# ---------------------------------------------------------------------------
# Issue #11 validation helpers
# ---------------------------------------------------------------------------

def file_extension(filename: str) -> str:
    """Return a lowercase extension without the leading period."""
    return Path(filename).suffix.lower().lstrip(".")


def is_allowed_file(filename: str) -> bool:
    """Allow only the file types specified by the project requirements."""
    return bool(filename and file_extension(filename) in ALLOWED_EXTENSIONS)


@app.get("/")
def home():
    """Provide a minimal health check while the workflow UI is being built."""
    return jsonify(
        {
            "application": "ClinicCare-Lite",
            "status": "running",
            "scope": "administrative and communication only",
            "diagnosis_enabled": False,
        }
    )

# ---------------------------------------------------------------------------
# Task creation and task access routes
# ---------------------------------------------------------------------------

from datetime import date
from flask import request


REVIEW_OUTCOMES = {
    "Pending",
    "Reviewed — Normal",
    "Needs Follow-up",
    "Escalated",
}


def json_error(message: str, status_code: int = 400):
    return jsonify({"error": message}), status_code


def current_role() -> str:
    """Read the temporary role header used until Issue #10 adds login."""
    return request.headers.get("X-Role", "").strip().lower()


def current_user_id() -> str:
    """Read the temporary user header used until Issue #10 adds login."""
    return request.headers.get("X-User-Id", "").strip()


def require_role(*allowed_roles: str):
    role = current_role()
    if role not in allowed_roles:
        return json_error(
            "Unauthorized: this action requires an approved user role.",
            403,
        )
    return None


def validate_task_payload(payload: dict) -> list[str]:
    errors = []
    required_text = {
        "patient_id": "patient_id",
        "clinician_id": "clinician_id",
        "instructions": "instructions",
        "due_date": "due_date",
    }

    for field, label in required_text.items():
        if not isinstance(payload.get(field), str) or not payload[field].strip():
            errors.append(f"{label} is required.")

    due_date = payload.get("due_date")
    if isinstance(due_date, str) and due_date.strip():
        try:
            date.fromisoformat(due_date)
        except ValueError:
            errors.append("due_date must use YYYY-MM-DD format.")

    attachment = payload.get("attachment_filename", "")
    if attachment and not is_allowed_file(attachment):
        errors.append("attachment_filename must end in .txt, .csv, or .pdf.")

    return errors


@app.post("/api/tasks")
def create_task():
    unauthorized = require_role("clinician")
    if unauthorized:
        return unauthorized

    payload = request.get_json(silent=True) or {}
    errors = validate_task_payload(payload)
    if errors:
        return jsonify({"errors": errors}), 400

    data = load_data()
    task = {
        "id": new_id("task"),
        "patient_id": payload["patient_id"].strip(),
        "clinician_id": payload["clinician_id"].strip(),
        "instructions": payload["instructions"].strip(),
        "due_date": payload["due_date"].strip(),
        "attachment_filename": payload.get("attachment_filename", "").strip(),
        "status": "Assigned",
        "submission_id": None,
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }
    data["tasks"].append(task)
    save_data(data)
    return jsonify(task), 201


@app.get("/api/tasks")
def list_tasks():
    role = current_role()
    data = load_data()

    if role == "clinician":
        return jsonify(data["tasks"])

    if role == "patient":
        user_id = current_user_id()
        if not user_id:
            return json_error("X-User-Id is required for patient access.", 401)
        patient_tasks = [
            task for task in data["tasks"] if task["patient_id"] == user_id
        ]
        return jsonify(patient_tasks)

    return json_error(
        "Unauthorized: use the clinician or patient role.",
        403,
    )


@app.get("/api/tasks/<task_id>")
def get_task(task_id: str):
    data = load_data()
    task = next((item for item in data["tasks"] if item["id"] == task_id), None)
    if task is None:
        return json_error("Task not found.", 404)

    role = current_role()
    if role == "clinician":
        return jsonify(task)
    if role == "patient" and current_user_id() == task["patient_id"]:
        return jsonify(task)
    return json_error("Unauthorized access to this task.", 403)


# ---------------------------------------------------------------------------
# Patient submission and upload-validation routes
# ---------------------------------------------------------------------------

import csv
import io
from pathlib import Path

from werkzeug.utils import secure_filename


ALLOWED_CONTENT_TYPES = {
    "txt": {"text/plain"},
    "csv": {"text/csv", "text/plain", "application/vnd.ms-excel"},
    "pdf": {"application/pdf"},
}


def safe_identifier(value: str, fallback: str = "unknown") -> str:
    cleaned = secure_filename(value.strip())
    return cleaned or fallback


def validate_uploaded_file(uploaded_file):
    """Validate filename, extension, MIME type, size, and basic completeness."""
    original_filename = uploaded_file.filename or ""
    safe_name = secure_filename(original_filename)
    extension = file_extension(safe_name)

    if not safe_name:
        return None, "A filename is required."
    if not is_allowed_file(safe_name):
        return None, "Only .txt, .csv, and .pdf files are accepted."
    if uploaded_file.mimetype not in ALLOWED_CONTENT_TYPES[extension]:
        return None, f"The uploaded content type is not valid for .{extension}."

    file_bytes = uploaded_file.read(MAX_UPLOAD_BYTES + 1)
    uploaded_file.seek(0)
    if len(file_bytes) == 0:
        return None, "The uploaded file is empty."
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        return None, "The uploaded file exceeds the 5 MiB size limit."

    return {
        "original_filename": original_filename,
        "safe_filename": safe_name,
        "extension": extension,
        "content_type": uploaded_file.mimetype,
        "file_bytes": file_bytes,
    }, None


def completeness_errors(file_info: dict, required_fields: list[str]) -> list[str]:
    """Check presence and basic formatting only; never interpret medical meaning."""
    extension = file_info["extension"]
    raw_bytes = file_info["file_bytes"]

    if extension == "pdf":
        # PDF contents are not interpreted by this administrative check.
        return []

    try:
        text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        return ["The .txt or .csv file must use UTF-8 text encoding."]

    if not text.strip():
        return ["The submitted form contains no text."]

    required = [field.strip() for field in required_fields if field.strip()]

    if extension == "csv":
        rows = list(csv.DictReader(io.StringIO(text)))
        if not rows:
            return ["The CSV must include a header row and at least one data row."]

        headers = list(rows[0].keys())
        errors = [
            f"Required CSV column is missing: {field}."
            for field in required
            if field not in headers
        ]

        for field in required:
            if field in headers and any(
                not str(row.get(field, "")).strip() for row in rows
            ):
                errors.append(
                    f"Required CSV column contains an empty cell: {field}."
                )
        return errors

    # For a text form, required fields are checked as labels only.
    return [
        f"Required text field is missing: {field}."
        for field in required
        if field.lower() not in text.lower()
    ]


@app.post("/api/tasks/<task_id>/submit")
def submit_task(task_id: str):
    unauthorized = require_role("patient")
    if unauthorized:
        return unauthorized

    patient_id = current_user_id()
    if not patient_id:
        return json_error("X-User-Id is required for patient submissions.", 401)

    data = load_data()
    task = next(
        (item for item in data["tasks"] if item["id"] == task_id),
        None,
    )

    if task is None:
        return json_error("Task not found.", 404)
    if task["patient_id"] != patient_id:
        return json_error("Unauthorized submission for this task.", 403)
    if task.get("submission_id"):
        return json_error("This task already has a submission.", 409)
    if task.get("status") != "Assigned":
        return json_error("This task is not accepting a submission.", 409)

    uploaded_file = request.files.get("file")
    if uploaded_file is None:
        return json_error("A file field is required.")

    file_info, error = validate_uploaded_file(uploaded_file)
    if error:
        return json_error(error)

    required_fields = task.get("required_fields", [])
    errors = completeness_errors(file_info, required_fields)
    if errors:
        return jsonify({"errors": errors, "form_check": "Incomplete"}), 400

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_patient_id = safe_identifier(patient_id, "patient")
    stored_filename = (
        f"{task_id}_{timestamp}_{file_info['safe_filename']}"
    )
    patient_directory = UPLOAD_DIR / safe_patient_id
    patient_directory.mkdir(parents=True, exist_ok=True)
    stored_path = patient_directory / stored_filename
    stored_path.write_bytes(file_info["file_bytes"])

    submission = {
        "id": new_id("submission"),
        "task_id": task_id,
        "patient_id": patient_id,
        "original_filename": file_info["original_filename"],
        "stored_filename": stored_filename,
        "stored_path": str(stored_path.relative_to(APP_DIR)),
        "extension": file_info["extension"],
        "content_type": file_info["content_type"],
        "size_bytes": len(file_info["file_bytes"]),
        "form_check": "Complete",
        "status": "Pending",
        "reviewer_id": None,
        "reviewed_at": None,
        "outcome": None,
        "notes": None,
        "notification_sent": False,
        "submitted_at": utc_now(),
    }
    data["submissions"].append(submission)

    task["submission_id"] = submission["id"]
    task["status"] = "Pending Review"
    task["updated_at"] = utc_now()

    data["notifications"].append({
        "id": new_id("notification"),
        "recipient_id": task["clinician_id"],
        "type": "submission_received",
        "task_id": task_id,
        "message": "A patient submission is ready for administrative review.",
        "read": False,
        "created_at": utc_now(),
    })
    save_data(data)

    return jsonify({
        "submission": submission,
        "task_status": task["status"],
        "message": "Submission accepted and queued for clinician review.",
    }), 201


@app.get("/api/submissions/<submission_id>")
def get_submission(submission_id: str):
    data = load_data()
    submission = next(
        (
            item
            for item in data["submissions"]
            if item["id"] == submission_id
        ),
        None,
    )

    if submission is None:
        return json_error("Submission not found.", 404)

    role = current_role()
    user_id = current_user_id()

    if role == "patient" and user_id == submission["patient_id"]:
        return jsonify(submission)

    if role == "clinician":
        task = next(
            (
                item
                for item in data["tasks"]
                if item["id"] == submission["task_id"]
            ),
            None,
        )
        if task and task["clinician_id"] == user_id:
            return jsonify(submission)

    return json_error("Unauthorized access to this submission.", 403)


@app.get("/api/notifications/<user_id>")
def list_notifications(user_id: str):
    if current_role() not in {"patient", "clinician"}:
        return json_error(
            "Unauthorized: use the clinician or patient role.",
            403,
        )

    if current_user_id() != user_id:
        return json_error("Unauthorized access to these notifications.", 403)

    data = load_data()
    return jsonify([
        item
        for item in data["notifications"]
        if item["recipient_id"] == user_id
    ])

# ---------------------------------------------------------------------------
# Clinician review and patient-visible outcome routes
# ---------------------------------------------------------------------------


@app.post("/api/submissions/<submission_id>/review")
def review_submission(submission_id: str):
    unauthorized = require_role("clinician")
    if unauthorized:
        return unauthorized

    clinician_id = current_user_id()
    if not clinician_id:
        return json_error("X-User-Id is required for clinician review.", 401)

    payload = request.get_json(silent=True) or {}
    outcome = payload.get("outcome")
    notes = payload.get("notes", "")

    if outcome not in REVIEW_OUTCOMES:
        return jsonify({
            "error": "outcome must be one of the approved administrative categories.",
            "allowed_outcomes": sorted(REVIEW_OUTCOMES),
        }), 400

    if not isinstance(notes, str):
        return json_error("notes must be text.")

    data = load_data()
    submission = next(
        (
            item
            for item in data["submissions"]
            if item["id"] == submission_id
        ),
        None,
    )

    if submission is None:
        return json_error("Submission not found.", 404)

    task = next(
        (
            item
            for item in data["tasks"]
            if item["id"] == submission["task_id"]
        ),
        None,
    )

    if task is None:
        return json_error("The task associated with this submission was not found.", 404)
    if task["clinician_id"] != clinician_id:
        return json_error("Unauthorized review for this task.", 403)
    if submission.get("status") != "Pending":
        return json_error("This submission has already been reviewed.", 409)

    reviewed_at = utc_now()
    submission["status"] = outcome
    submission["outcome"] = outcome
    submission["reviewer_id"] = clinician_id
    submission["reviewed_at"] = reviewed_at
    submission["notes"] = notes.strip()
    submission["notification_sent"] = True

    task["status"] = "Reviewed"
    task["updated_at"] = reviewed_at

    data["notifications"].append({
        "id": new_id("notification"),
        "recipient_id": submission["patient_id"],
        "type": "review_outcome",
        "task_id": task["id"],
        "submission_id": submission_id,
        "message": (
            "Your administrative submission has been reviewed. "
            f"Outcome: {outcome}."
        ),
        "read": False,
        "created_at": reviewed_at,
    })
    save_data(data)

    return jsonify({
        "message": "Administrative review recorded and patient notified.",
        "submission": submission,
        "task_status": task["status"],
    })


@app.get("/api/tasks/<task_id>/outcome")
def get_task_outcome(task_id: str):
    data = load_data()
    task = next((item for item in data["tasks"] if item["id"] == task_id), None)
    if task is None:
        return json_error("Task not found.", 404)

    role = current_role()
    user_id = current_user_id()
    if role == "patient" and user_id != task["patient_id"]:
        return json_error("Unauthorized access to this task outcome.", 403)
    if role == "clinician" and user_id != task["clinician_id"]:
        return json_error("Unauthorized access to this task outcome.", 403)
    if role not in {"patient", "clinician"}:
        return json_error("Unauthorized: use the clinician or patient role.", 403)

    submission = next(
        (
            item
            for item in data["submissions"]
            if item.get("task_id") == task_id
        ),
        None,
    )
    if submission is None:
        return jsonify({
            "task_id": task_id,
            "task_status": task["status"],
            "outcome": None,
            "message": "No submission has been received yet.",
        })

    return jsonify({
        "task_id": task_id,
        "submission_id": submission["id"],
        "task_status": task["status"],
        "submission_status": submission["status"],
        "outcome": submission.get("outcome"),
        "reviewed_at": submission.get("reviewed_at"),
        "notes": submission.get("notes"),
        "notification_sent": submission.get("notification_sent", False),
    })


if __name__ == "__main__":
    app.run(debug=True)



