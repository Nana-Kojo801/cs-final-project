"""GridCare-Lite GUI screens.

Each ``ui/<name>_view.py`` module exports a ``VIEW`` dict:

    VIEW = {
        "key": "outages",            # unique id
        "label": "Outage Dashboard", # nav button text
        "order": 10,                 # nav sort order
        "permission": "view_outages",# core.auth permission, or None for always-on
        "factory": OutageDashboard,  # ttk.Frame subclass (parent, app)
    }

app.py discovers these automatically - adding a screen never means editing app.py.
"""
