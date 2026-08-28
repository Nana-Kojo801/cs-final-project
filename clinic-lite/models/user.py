"""User model (clinician / patient) with bcrypt-hashed passwords."""

import bcrypt

from utils.storage import read_json, update_json
from utils.validator import validate_id, validate_password, validate_email


class User:
    def __init__(self, user_id, name, email, role, password_hash=None,
                 theme=None, engagement_points=0):
        self.user_id = str(user_id)
        self.name = name
        self.email = email
        self.role = role
        self.password_hash = password_hash
        self.theme = theme or ("dark" if role == "clinician" else "colorful")
        self.engagement_points = engagement_points

    # ---------------------------------------------------------------- passwords
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, password):
        try:
            return bcrypt.checkpw(password.encode("utf-8"),
                                  self.password_hash.encode("utf-8"))
        except (ValueError, TypeError, AttributeError):
            return False

    # ---------------------------------------------------------------- (de)serialise
    def to_dict(self):
        return {
            "name": self.name, "email": self.email, "role": self.role,
            "password": self.password_hash, "theme": self.theme,
            "engagement_points": self.engagement_points,
        }

    @classmethod
    def from_dict(cls, user_id, d):
        return cls(user_id, d["name"], d["email"], d["role"],
                   password_hash=d.get("password"), theme=d.get("theme"),
                   engagement_points=d.get("engagement_points", 0))

    def save(self):
        update_json("users", lambda data: {**data, self.user_id: self.to_dict()}, {})
        return self


# --------------------------------------------------------------------- queries
def get(user_id):
    data = read_json("users", {})
    d = data.get(str(user_id))
    return User.from_dict(str(user_id), d) if d else None


def by_email(email):
    for uid, d in read_json("users", {}).items():
        if d["email"].lower() == (email or "").lower():
            return User.from_dict(uid, d)
    return None


def all_of_role(role):
    return [User.from_dict(uid, d) for uid, d in read_json("users", {}).items()
            if d["role"] == role]


def register(user_id, name, email, password, role):
    """Validate everything, then persist. Returns (User | None, error | None)."""
    ok, msg = validate_id(user_id, role)
    if not ok:
        return None, msg
    ok, msg = validate_password(password)
    if not ok:
        return None, msg
    if not validate_email(email):
        return None, "Enter a valid email address."
    if get(user_id):
        return None, "That ID is already registered."
    if by_email(email):
        return None, "That email is already registered."
    u = User(user_id, name.strip(), email.strip(), role)
    u.set_password(password)
    u.save()
    return u, None


def authenticate(user_id, password):
    u = get(user_id)
    if u and u.check_password(password):
        return u
    return None


def set_theme(user_id, theme):
    if theme not in ("dark", "colorful"):
        return False
    update_json("users", lambda data: _apply(data, str(user_id), "theme", theme), {})
    return True


def add_engagement_points(user_id, points):
    def _m(data):
        d = data.get(str(user_id))
        if d:
            d["engagement_points"] = d.get("engagement_points", 0) + points
        return data
    update_json("users", _m, {})


def _apply(data, key, field, value):
    if key in data:
        data[key][field] = value
    return data
