"""Outage dashboard - table of outages, filterable by status."""

import tkinter as tk
from tkinter import ttk

from core import services
from ui._widgets import make_tree


class OutageDashboard(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        bar = ttk.Frame(self)
        bar.pack(fill="x")
        ttk.Label(bar, text="Outage Dashboard", style="Header.TLabel").pack(side="left")
        self.status = tk.StringVar(value="All")
        ttk.Label(bar, text="  Status:").pack(side="left")
        ttk.Combobox(bar, textvariable=self.status, width=14, state="readonly",
                     values=["All", "Open", "In Progress", "Resolved"]).pack(side="left")
        ttk.Button(bar, text="Refresh", command=self.load).pack(side="left", padx=6)
        self.tree = make_tree(self, ("ID", "Substation", "Region", "Severity", "Status",
                                     "Reported by", "Reported at", "Critical"),
                              (40, 150, 110, 70, 90, 130, 140, 60))
        self.load()

    def load(self):
        self.tree.delete(*self.tree.get_children())
        s = None if self.status.get() == "All" else self.status.get()
        for o in services.list_outages(self.app.conn, status=s):
            self.tree.insert("", "end", values=(
                o["outage_id"], o["substation_name"], o["region"], o["severity"],
                o["status"], o["reported_by_name"], o["reported_at"],
                "YES" if o["critical_flag"] else ""))


VIEW = {
    "key": "outages",
    "label": "Outage Dashboard",
    "order": 10,
    "permission": "view_outages",
    "factory": OutageDashboard,
}
