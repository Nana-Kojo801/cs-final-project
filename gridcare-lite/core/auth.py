"""Authentication and role-based access control for GridCare-Lite.

Passwords are hashed with bcrypt before storage. Permissions are checked in
application logic *and* enforced by database CHECK constraints / foreign keys -
role separation is not just "hide the button".
"""

import re
import bcrypt

ROLES = ("admin", "engineer", "technician", "customer_service")

# permission -> set of roles allowed to perform it
PERMISSIONS = {
    "view_outages":        {"admin", "engineer", "technician", "customer_service"},
    "create_outage":       {"admin", "engineer"},
    "create_work_order":   {"admin"},
    "assign_technician":   {"admin"},
    "update_work_order":   {"admin", "technician"},
    "resolve_outage":      {"admin", "technician"},
    "log_complaint":       {"admin", "customer_service"},
    "link_complaint":      {"admin", "customer_service"},
    "view_reports":        {"admin", "engineer"},
    "manage_users":        {"admin"},
}

PASSWORD_MIN_LEN = 8


class AuthError(Exception):
    """Raised on failed login or a permission violation."""


def validate_password(password):
    """Return (ok, message). Minimum length + at least one letter and one digit."""
    if len(password) < PASSWORD_MIN_LEN:
        return False, f"Password must be at least {PASSWORD_MIN_LEN} characters."
    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    return True, "OK"


def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password, password_hash):
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_user(conn, username, password, full_name, role):
    if role not in ROLES:
        raise ValueError(f"Unknown role: {role}")
    ok, msg = validate_password(password)
    if not ok:
        raise ValueError(msg)
    cur = conn.execute(
        "INSERT INTO users (username, password_hash, full_name, role) VALUES (?,?,?,?)",
        (username.strip(), hash_password(password), full_name.strip(), role),
    )
    conn.commit()
    return cur.lastrowid


def authenticate(conn, username, password):
    """Return a dict describing the user, or raise AuthError."""
    row = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username.strip(),)
    ).fetchone()
    if row is None or not row["active"]:
        raise AuthError("Invalid username or password.")
    if not check_password(password, row["password_hash"]):
        raise AuthError("Invalid username or password.")
    return {"user_id": row["user_id"], "username": row["username"],
            "full_name": row["full_name"], "role": row["role"]}


def has_permission(role, permission):
    return role in PERMISSIONS.get(permission, set())


def require(user, permission):
    """Raise AuthError if ``user`` (dict from authenticate) lacks ``permission``."""
    if not user or not has_permission(user.get("role"), permission):
        raise AuthError(
            f"Role '{user.get('role') if user else None}' is not permitted to: {permission}"
        )
