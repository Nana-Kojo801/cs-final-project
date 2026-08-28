"""Operational reports screen (admin / engineer)."""

from tkinter import ttk

from core import auth, reports


class ReportsView(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        ttk.Label(self, text="Operational Reports", style="Header.TLabel").pack(anchor="w")
        try:
            s = reports.operational_summary(app.conn, app.user)
        except auth.AuthError as e:
            ttk.Label(self, text=str(e), foreground="#c0392b").pack(anchor="w")
            return
        grid = ttk.Frame(self, padding=(0, 10))
        grid.pack(anchor="w")
        rows = [
            ("Total outages", s["total_outages"]),
            ("Open work orders", s["open_work_orders"]),
            ("Open complaints", s["complaints_open"]),
            ("Avg resolution (hours)", s["avg_resolution_hours"]),
            ("Open outages on critical substations", s["open_outages_on_critical_substations"]),
        ]
        for i, (k, v) in enumerate(rows):
            ttk.Label(grid, text=k + ":", style="Sub.TLabel").grid(row=i, column=0, sticky="e", padx=6, pady=3)
            ttk.Label(grid, text=str(v), font=("Segoe UI", 11, "bold")).grid(row=i, column=1, sticky="w")
        for title, data in (("Outages by status", s["outages_by_status"]),
                            ("Outages by region", s["outages_by_region"]),
                            ("Outages by severity", s["outages_by_severity"])):
            lf = ttk.LabelFrame(self, text=title, padding=8)
            lf.pack(fill="x", pady=4)
            if not data:
                ttk.Label(lf, text="(none)").pack(anchor="w")
            for k, v in sorted(data.items(), key=lambda kv: -kv[1]):
                ttk.Label(lf, text=f"{k}: {v}").pack(anchor="w")
        ttk.Label(self, text="'Critical' = top betweenness-centrality substations from the "
                             "network analysis (structural proxy on synthetic data).",
                  style="Sub.TLabel", wraplength=640).pack(anchor="w", pady=(8, 0))


VIEW = {
    "key": "reports",
    "label": "Reports",
    "order": 60,
    "permission": "view_reports",
    "factory": ReportsView,
}
