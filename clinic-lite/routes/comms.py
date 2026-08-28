"""Issue #12 - appointments, reminders, announcements, secure messaging, inbox."""

from flask import abort, flash, g, redirect, render_template, request, url_for

from models import announcement as ann_model
from models import appointment as appt_model
from models import clinic as clinic_model
from models import message as msg_model
from models import user as user_model
from utils.auth import login_required, role_required
from utils.comms_workflow import WorkflowError, mark_attendance, post_announcement, run_reminder_job
from utils.email_handler import inbox_for, mark_all_read


def _may_message(user, other):
    if user.role == "patient" and other.role == "clinician":
        return clinic_model.shares_clinic(other.user_id, user.user_id)
    if user.role == "clinician" and other.role == "patient":
        return clinic_model.shares_clinic(user.user_id, other.user_id)
    return False


def register(app):
    app.config["NAV"] += [
        {"endpoint": "clinician_appointments", "label": "Appointments",
         "roles": ("clinician",), "order": 30},
        {"endpoint": "clinician_announcements", "label": "Announcements",
         "roles": ("clinician",), "order": 40},
        {"endpoint": "messages", "label": "Messages", "roles": ("clinician", "patient"),
         "order": 70, "badge": "unread_msgs"},
        {"endpoint": "inbox", "label": "Inbox", "roles": ("clinician", "patient"),
         "order": 80, "badge": "unread_notes"},
    ]

    @app.route("/clinician/appointments", methods=["GET", "POST"])
    @role_required("clinician")
    def clinician_appointments():
        clinic = clinic_model.for_clinician(g.user.user_id)
        if request.method == "POST":
            f = request.form
            if f.get("action") == "create":
                appt_model.create(clinic.clinic_id, f["patient"], g.user.user_id,
                                  f["when"], f.get("reason", ""))
                flash("Appointment scheduled.", "success")
            elif f.get("action") == "status":
                try:
                    mark_attendance(clinic.clinic_id, f["appointment_id"], f["status"])
                    flash("Attendance updated.", "success")
                except WorkflowError as e:
                    flash(str(e), "danger")
            return redirect(url_for("clinician_appointments"))
        appts = sorted(appt_model.for_clinic(clinic.clinic_id).items(),
                       key=lambda kv: kv[1]["when"], reverse=True)
        return render_template("clinician/appointments.html", appts=appts,
                               patients=[user_model.get(p) for p in clinic.patient_ids],
                               statuses=appt_model.STATUSES)

    @app.route("/clinician/announcements", methods=["GET", "POST"])
    @role_required("clinician")
    def clinician_announcements():
        clinic = clinic_model.for_clinician(g.user.user_id)
        if request.method == "POST":
            f = request.form
            try:
                post_announcement(g.user.user_id, f["title"].strip(), f["body"].strip(),
                                  bool(f.get("urgent")), f.get("publish_date"),
                                  f.get("expiry_date"))
                flash("Announcement posted.", "success")
            except WorkflowError as e:
                flash(str(e), "danger")
            return redirect(url_for("clinician_announcements"))
        return render_template("shared/announcements.html",
                               announcements=ann_model.all_for_clinic(clinic.clinic_id),
                               can_post=True)

    @app.route("/clinician/reminders/run")
    @role_required("clinician")
    def clinician_run_reminders():
        n = run_reminder_job()
        flash(f"Reminder job sent {n} notification(s).", "info")
        return redirect(url_for("clinician_dashboard"))

    @app.route("/messages")
    @login_required
    def messages():
        convos = msg_model.conversations_for(g.user.user_id)
        for c in convos:
            c["other"] = user_model.get(c["other_id"])
        if g.user.role == "patient":
            clinic = clinic_model.for_patient(g.user.user_id)
            contacts = [user_model.get(clinic.clinician_id)] if clinic else []
        else:
            clinic = clinic_model.for_clinician(g.user.user_id)
            contacts = [user_model.get(p) for p in clinic.patient_ids] if clinic else []
        return render_template("shared/messages.html", convos=convos,
                               contacts=[c for c in contacts if c])

    @app.route("/messages/<other_id>", methods=["GET", "POST"])
    @login_required
    def conversation(other_id):
        other = user_model.get(other_id)
        if not other or not _may_message(g.user, other):
            abort(403)
        if request.method == "POST":
            body = request.form.get("content", "").strip()
            if body:
                msg_model.send(g.user.user_id, other_id, body)
            return redirect(url_for("conversation", other_id=other_id))
        msg_model.mark_read(g.user.user_id, other_id)
        return render_template("shared/conversation.html", other=other,
                               messages=msg_model.thread(g.user.user_id, other_id))

    @app.route("/inbox")
    @login_required
    def inbox():
        notes = sorted(inbox_for(g.user.user_id), key=lambda n: n["timestamp"], reverse=True)
        mark_all_read(g.user.user_id)
        return render_template("shared/inbox.html", notes=notes)
