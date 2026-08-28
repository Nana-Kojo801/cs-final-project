"""ClinicCare-Lite route modules.

Each module exposes ``register(app)`` and is auto-discovered by app.create_app().
A module may also append nav entries::

    app.config["NAV"].append(
        {"endpoint": "patient_dashboard", "label": "Dashboard",
         "roles": ("patient",), "order": 10})
"""
