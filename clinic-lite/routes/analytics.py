"""Issue #13 - operational analytics (clinician) and private progress (patient)."""

from flask import g, render_template

from models import clinic as clinic_model
from utils import analytics, engagement
from utils.auth import role_required


def register(app):
    app.config["NAV"] += [
        {"endpoint": "clinician_analytics", "label": "Analytics",
         "roles": ("clinician",), "order": 50},
        {"endpoint": "patient_engagement", "label": "My Progress",
         "roles": ("patient",), "order": 20},
    ]

    @app.route("/clinician/analytics")
    @role_required("clinician")
    def clinician_analytics():
        clinic = clinic_model.for_clinician(g.user.user_id)
        return render_template("clinician/analytics.html",
                               metrics=analytics.clinic_operational(clinic.clinic_id),
                               clinic=clinic)

    @app.route("/patient/engagement")
    @role_required("patient")
    def patient_engagement():
        return render_template("patient/engagement.html",
                               summary=engagement.summary(g.user.user_id),
                               personal=analytics.patient_personal(g.user.user_id))
