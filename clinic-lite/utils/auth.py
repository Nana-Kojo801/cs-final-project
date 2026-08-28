"""Session helpers and route-protection decorators for ClinicCare-Lite."""

from functools import wraps

from flask import g, redirect, session, url_for, flash, abort

from models import user as user_model


def load_user():
    uid = session.get("user_id")
    g.user = user_model.get(uid) if uid else None
    return g.user


def login_user(user):
    session.clear()
    session["user_id"] = user.user_id
    session["role"] = user.role
    session.permanent = True


def logout_user():
    session.clear()


def login_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if not getattr(g, "user", None):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view(*a, **kw)
    return wrapped


def role_required(role):
    def deco(view):
        @wraps(view)
        def wrapped(*a, **kw):
            if not getattr(g, "user", None):
                return redirect(url_for("login"))
            if g.user.role != role:
                abort(403)
            return view(*a, **kw)
        return wrapped
    return deco
