"""JSON persistence layer for ClinicCare-Lite.

One JSON file per collection under data/. Every write goes through
``write_json`` which writes to a temp file and atomically replaces the target -
this avoids the classic ``r+`` / ``seek(0)`` bug where a shorter payload leaves
trailing bytes from the old content ("Extra data" JSON decode errors). The
brief calls this bug out explicitly; we fix it with atomic replace + explicit
truncation.
"""

import json
import os
import tempfile
import threading

from config import DATA_DIR

_LOCK = threading.RLock()

COLLECTIONS = (
    "users", "clinics", "health_tasks", "task_assignments", "task_submissions",
    "messages", "appointments", "announcements", "engagement", "notifications",
)


def _path(name):
    return os.path.join(DATA_DIR, f"{name}.json")


def ensure_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    for name in COLLECTIONS:
        p = _path(name)
        if not os.path.exists(p):
            _atomic_write(p, [] if name in ("messages", "notifications") else {})


def _atomic_write(path, obj):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)
            f.flush()
            f.truncate()            # explicit, per the brief's warning
            os.fsync(f.fileno())
        os.replace(tmp, path)       # atomic on the same filesystem
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def read_json(name, default=None):
    with _LOCK:
        p = _path(name)
        if not os.path.exists(p):
            return default if default is not None else ({} if name not in ("messages", "notifications") else [])
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            # corrupt/empty file - fail safe to an empty collection
            return default if default is not None else ({} if name not in ("messages", "notifications") else [])


def write_json(name, obj):
    with _LOCK:
        os.makedirs(DATA_DIR, exist_ok=True)
        _atomic_write(_path(name), obj)


def update_json(name, mutator, default=None):
    """Read, apply ``mutator(data)`` (which returns the new data), write. Locked."""
    with _LOCK:
        data = read_json(name, default)
        new = mutator(data)
        write_json(name, new if new is not None else data)
        return new if new is not None else data
