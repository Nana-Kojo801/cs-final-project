"""Issue #11 - clinician dashboard, task creation/assignment, submission review."""

from flask import abort, flash, g, redirect, render_template, request, send_file, url_for

from models import clinic as clinic_model
from models import health_task as task_model
from models import task_submission as sub_model
from models import user as user_model
from utils.auth import role_required
from utils.file_handler import read_preview
from utils.submission_workflow import WorkflowError, review_submission


def register(app):
    app.config["NAV"].append(
        {"endpoint": "clinician_dashboard", "label": "Dashboard",
         "roles": ("clinician",), "order": 10})
    app.config["NAV"].append(
        {"endpoint": "clinician_submissions", "label": "Submissions",
         "roles": ("clinician",), "order": 20})

    @app.route("/clinician")
    @role_required("clinician")
    def clinician_dashboard():
        clinic = clinic_model.for_clinician(g.user.user_id)
        tasks = task_model.for_clinic(clinic.clinic_id) if clinic else []
        patients = [user_model.get(p) for p in clinic.patient_ids] if clinic else []
        pending = sub_model.for_clinic(clinic.clinic_id, status="Pending") if clinic else []
        return render_template("clinician/dashboard.html", clinic=clinic, tasks=tasks,
                               patients=patients, pending=pending)

    @app.route("/clinician/task/new", methods=["POST"])
    @role_required("clinician")
    def clinician_create_task():
        clinic = clinic_model.for_clinician(g.user.user_id)
        f = request.form
        if not f.get("title") or not f.get("due_date"):
            flash("Title and due date are required.", "danger")
            return redirect(url_for("clinician_dashboard"))
        spec = {}
        if f.get("expected_columns"):
            spec["expected_columns"] = [c.strip() for c in f["expected_columns"].split(",") if c.strip()]
        if f.get("numeric_columns"):
            spec["numeric_columns"] = [c.strip() for c in f["numeric_columns"].split(",") if c.strip()]
        if f.get("required_labels"):
            spec["required_labels"] = [c.strip() for c in f["required_labels"].split(",") if c.strip()]
        task = task_model.create(f["title"].strip(), f.get("description", "").strip(),
                                 f["due_date"], clinic.clinic_id, g.user.user_id,
                                 check_spec=spec or None)
        patient_ids = request.form.getlist("patients")
        if patient_ids:
            task_model.assign(task.task_id, patient_ids)
        flash(f"Task '{task.title}' created and assigned to {len(patient_ids)} patient(s).",
              "success")
        return redirect(url_for("clinician_dashboard"))

    @app.route("/clinician/task/<task_id>/assign", methods=["POST"])
    @role_required("clinician")
    def clinician_assign(task_id):
        clinic = clinic_model.for_clinician(g.user.user_id)
        task = task_model.get(task_id)
        if not task or task.clinic_id != clinic.clinic_id:
            abort(404)
        task_model.assign(task_id, request.form.getlist("patients"))
        flash("Assignment updated.", "success")
        return redirect(url_for("clinician_dashboard"))

    @app.route("/clinician/submissions")
    @role_required("clinician")
    def clinician_submissions():
        clinic = clinic_model.for_clinician(g.user.user_id)
        subs = sub_model.for_clinic(clinic.clinic_id,
                                    task_id=request.args.get("task") or None,
                                    patient_id=request.args.get("patient") or None,
                                    status=request.args.get("status") or None)
        enriched = [{"sub": s, "task": task_model.get(s.task_id),
                     "patient": user_model.get(s.patient_id)} for s in subs]
        return render_template("clinician/submissions.html", subs=enriched,
                               tasks=task_model.for_clinic(clinic.clinic_id),
                               patients=[user_model.get(p) for p in clinic.patient_ids],
                               outcomes=sub_model.REVIEW_OUTCOMES,
                               filters=request.args)

    @app.route("/clinician/review/<patient_id>/<task_id>", methods=["GET", "POST"])
    @role_required("clinician")
    def clinician_review(patient_id, task_id):
        if not clinic_model.shares_clinic(g.user.user_id, patient_id):
            abort(403)
        sub = sub_model.get(patient_id, task_id)
        if not sub:
            abort(404)
        if request.method == "POST":
            try:
                review_submission(g.user.user_id, patient_id, task_id,
                                  request.form.get("outcome"),
                                  request.form.get("notes", "").strip())
            except (WorkflowError, ValueError) as e:
                flash(str(e), "danger")
                return redirect(request.url)
            flash("Review recorded and the patient has been notified.", "success")
            return redirect(url_for("clinician_submissions"))
        return render_template("clinician/review.html", sub=sub,
                               task=task_model.get(task_id),
                               patient=user_model.get(patient_id),
                               preview=read_preview(sub.file_path),
                               outcomes=sub_model.REVIEW_OUTCOMES)

    @app.route("/clinician/download/<patient_id>/<task_id>")
    @role_required("clinician")
    def clinician_download(patient_id, task_id):
        if not clinic_model.shares_clinic(g.user.user_id, patient_id):
            abort(403)
        sub = sub_model.get(patient_id, task_id)
        if not sub:
            abort(404)
        return send_file(sub.file_path, as_attachment=True)
