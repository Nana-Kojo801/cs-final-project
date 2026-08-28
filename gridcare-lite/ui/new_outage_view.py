"""New outage form - engineers / admins log a fault against a real substation."""

import tkinter as tk
from tkinter import ttk

from core import auth, services


class NewOutageForm(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        ttk.Label(self, text="Log a New Outage", style="Header.TLabel").pack(anchor="w")
        form = ttk.Frame(self, padding=(0, 10))
        form.pack(fill="x")
        self.subs = services.list_substations(app.conn)
        self.sub_map = {f"{s['name']} ({s['region']})": s["substation_id"] for s in self.subs}
        ttk.Label(form, text="Substation").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.sub = ttk.Combobox(form, values=list(self.sub_map), width=44, state="readonly")
        self.sub.grid(row=0, column=1, pady=6)
        ttk.Label(form, text="Severity").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        self.sev = ttk.Combobox(form, values=list(services.SEVERITIES), width=20, state="readonly")
        self.sev.current(1)
        self.sev.grid(row=1, column=1, sticky="w", pady=6)
        ttk.Label(form, text="Description").grid(row=2, column=0, sticky="ne", padx=6, pady=6)
        self.desc = tk.Text(form, width=46, height=6)
        self.desc.grid(row=2, column=1, pady=6)
        ttk.Button(self, text="Submit Outage", command=self.submit).pack(anchor="w", pady=6)
        self.msg = ttk.Label(self, text="", foreground="#c0392b")
        self.msg.pack(anchor="w")

    def submit(self):
        if not self.sub.get():
            self.msg.config(text="Select a substation.")
            return
        try:
            oid = services.create_outage(
                self.app.conn, self.app.user, self.sub_map[self.sub.get()],
                self.desc.get("1.0", "end").strip(), self.sev.get())
        except (services.WorkflowError, auth.AuthError) as e:
            self.msg.config(text=str(e), foreground="#c0392b")
            return
        self.msg.config(text=f"Outage #{oid} logged.", foreground="#27767b")
        self.desc.delete("1.0", "end")


VIEW = {
    "key": "new_outage",
    "label": "Log Outage",
    "order": 20,
    "permission": "create_outage",
    "factory": NewOutageForm,
}
