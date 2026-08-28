"""Issue #10 - registration, login, logout, session, theme, role redirect."""

from flask import current_app, g, redirect, render_template, request, url_for, flash

from models import clinic as clinic_model
from models import user as user_model
from utils.auth import login_user, logout_user, login_required


def register(app):

    @app.route("/")
    def index():
        if not g.user:
            return redirect(url_for("login"))
        target = f"{g.user.role}_dashboard"
        if target in current_app.view_functions:
            return redirect(url_for(target))
        # dashboard module not installed yet (incremental rollout)
        return render_template("error.html", code=200,
                               message=f"Logged in as {g.user.name}. Your "
                                       f"{g.user.role} dashboard is not installed yet.")

    @app.route("/register", methods=["GET", "POST"], endpoint="register")
    def register_view():
        if request.method == "POST":
            f = request.form
            role = f.get("role")
            user, err = user_model.register(
                f.get("user_id", "").strip(), f.get("name", "").strip(),
                f.get("email", "").strip(), f.get("password", ""), role)
            if err:
                flash(err, "danger")
                return render_template("register.html", form=f)
            if role == "patient":
                demo = clinic_model.all_clinics()
                if demo:
                    clinic_model.add_patient(demo[0].clinic_id, user.user_id)
            else:
                clinic_model.Clinic(f"c{user.user_id}", f"{user.name}'s Clinic",
                                    user.user_id, []).save()
            flash("Registration successful - please log in.", "success")
            return redirect(url_for("login"))
        return render_template("register.html", form={})

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            uid = request.form.get("user_id", "").strip()
            pw = request.form.get("password", "")
            user = user_model.authenticate(uid, pw)
            if not user:
                flash("Invalid ID or password.", "danger")
                return render_template("login.html")
            login_user(user)
            flash(f"Welcome, {user.name}.", "success")
            return redirect(url_for("index"))
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        logout_user()
        flash("You have been logged out.", "info")
        return redirect(url_for("login"))

    @app.route("/theme/<theme>")
    @login_required
    def set_theme(theme):
        if g.user.role == "patient" and user_model.set_theme(g.user.user_id, theme):
            flash(f"Theme set to {theme}.", "success")
        return redirect(request.referrer or url_for("index"))
