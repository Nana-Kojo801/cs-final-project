"""Issue #11 - patient dashboard and health-task submission."""

from datetime import date

from flask import abort, flash, g, redirect, render_template, request, url_for

from models import announcement as ann_model
from models import appointment as appt_model
from models import clinic as clinic_model
from models import health_task as task_model
from models import task_submission as sub_model
from utils import engagement
from utils.auth import role_required
from utils.submission_workflow import WorkflowError, submit_task


def register(app):
    app.config["NAV"].append(
        {"endpoint": "patient_dashboard", "label": "Dashboard",
         "roles": ("patient",), "order": 10})

    @app.route("/patient")
    @role_required("patient")
    def patient_dashboard():
        pid = g.user.user_id
        clinic = clinic_model.for_patient(pid)
        today = date.today().isoformat()
        rows = []
        for t in task_model.tasks_for_patient(pid):
            sub = sub_model.get(pid, t.task_id)
            rows.append({
                "task": t, "submission": sub,
                "state": ("Reviewed" if sub and sub.review_status != "Pending"
                          else "Submitted" if sub
                          else "Overdue" if t.due_date and t.due_date < today
                          else "Pending"),
            })
        appts = sorted(appt_model.for_patient(pid).items(), key=lambda kv: kv[1]["when"])
        announcements = ann_model.active_for_clinic(clinic.clinic_id) if clinic else []
        return render_template("patient/dashboard.html", rows=rows, appts=appts,
                               announcements=announcements,
                               engagement=engagement.summary(pid))

    @app.route("/patient/task/<task_id>", methods=["GET", "POST"])
    @role_required("patient")
    def patient_task(task_id):
        pid = g.user.user_id
        task = task_model.get(task_id)
        if not task or not task_model.is_assigned(task_id, pid):
            abort(404)
        sub = sub_model.get(pid, task_id)
        if request.method == "POST":
            file = request.files.get("submission")
            if not file or not file.filename:
                flash("Choose a file to upload.", "danger")
                return redirect(request.url)
            try:
                sub, check = submit_task(pid, task_id, file_storage=file)
            except WorkflowError as e:
                flash(str(e), "danger")
                return redirect(request.url)
            if check.get("issues"):
                flash("Submitted. Form-completeness check found: " +
                      "; ".join(check["issues"]), "warning")
            else:
                flash("Submitted successfully. Completeness check passed.", "success")
            return redirect(url_for("patient_task", task_id=task_id))
        return render_template("patient/task.html", task=task, submission=sub)
