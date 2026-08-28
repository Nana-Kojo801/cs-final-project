"""ClinicCare-Lite - Flask web application (entry point).

Clinic Patient Administration and Communication System (CS 112 Final Project).

ADMINISTRATIVE AND COMMUNICATION ONLY. This system does not diagnose patients,
interpret symptoms, calculate risk, or recommend treatment. The only automated
content check (utils/completeness.py) is a structural form-completeness check.

Run:
  python seed_data.py       # first time: create data/ + demo accounts and content
  python app.py             # http://127.0.0.1:5000

Routes live in the routes/ package. Each routes/<name>.py exposes
``register(app)`` and is discovered automatically, and each may add entries to
``app.config['NAV']`` - so adding a feature never means editing app.py or
base.html.
"""

import importlib
import pkgutil
from datetime import timedelta

from flask import Flask, g, render_template, session

import config
import routes
from models import message as msg_model
from models import user as user_model
from models import health_task as task_model
from utils.email_handler import inbox_for
from utils.storage import ensure_data_files


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_UPLOAD_BYTES + 4096
    app.config["NAV"] = []
    app.permanent_session_lifetime = timedelta(minutes=config.SESSION_LIFETIME_MINUTES)
    ensure_data_files()

    @app.before_request
    def _load_user():
        uid = session.get("user_id")
        g.user = user_model.get(uid) if uid else None

    @app.template_filter("assigned_count")
    def _assigned_count(task_id):
        return len(task_model.patients_for_task(task_id))

    @app.context_processor
    def _inject():
        nav = []
        if g.get("user"):
            for item in app.config["NAV"]:
                if g.user.role in item.get("roles", ()):
                    nav.append(item)
            nav.sort(key=lambda i: i.get("order", 100))
        unread_msgs = msg_model.unread_count(g.user.user_id) if g.get("user") else 0
        unread_notes = (sum(1 for n in inbox_for(g.user.user_id) if not n["read"])
                        if g.get("user") else 0)
        return dict(current_user=g.get("user"), nav_items=nav,
                    unread_msgs=unread_msgs, unread_notes=unread_notes)

    @app.errorhandler(403)
    def _403(e):
        return render_template("error.html", code=403,
                               message="You are not authorised to view that."), 403

    @app.errorhandler(404)
    def _404(e):
        return render_template("error.html", code=404,
                               message="That page or record was not found."), 404

    @app.errorhandler(413)
    def _413(e):
        return render_template("error.html", code=413,
                               message="That file exceeds the upload size limit."), 413

    for mod_info in pkgutil.iter_modules(routes.__path__):
        module = importlib.import_module(f"routes.{mod_info.name}")
        if hasattr(module, "register"):
            module.register(app)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
