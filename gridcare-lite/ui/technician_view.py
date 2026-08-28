"""Technician view - a technician's own assignments, with start / complete actions."""

from tkinter import ttk

from core import auth, services
from ui._widgets import make_tree, SimpleDialog


class TechnicianView(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        ttk.Label(self, text="My Assignments", style="Header.TLabel").pack(anchor="w")
        self.tree = make_tree(self, ("WO", "Substation", "Region", "Status", "Scheduled", "Outage"),
                              (40, 150, 110, 90, 100, 300))
        btns = ttk.Frame(self)
        btns.pack(fill="x", pady=4)
        ttk.Button(btns, text="Start work", command=self.start).pack(side="left", padx=3)
        ttk.Button(btns, text="Mark complete...", command=self.complete).pack(side="left", padx=3)
        self.msg = ttk.Label(self, text="", foreground="#c0392b")
        self.msg.pack(anchor="w")
        self.load()

    def load(self):
        self.tree.delete(*self.tree.get_children())
        for w in services.list_work_orders(self.app.conn, technician_id=self.app.user["user_id"]):
            self.tree.insert("", "end", values=(
                w["work_order_id"], w["substation_name"], w["region"], w["status"],
                w["scheduled_date"] or "-", w["outage_description"]))

    def _selected(self):
        sel = self.tree.selection()
        return int(self.tree.item(sel[0])["values"][0]) if sel else None

    def start(self):
        wid = self._selected()
        if not wid:
            self.msg.config(text="Select a work order.")
            return
        try:
            services.start_work_order(self.app.conn, self.app.user, wid)
        except (services.WorkflowError, auth.AuthError) as e:
            self.msg.config(text=str(e))
            return
        self.msg.config(text=f"WO #{wid} in progress.", foreground="#27767b")
        self.load()

    def complete(self):
        wid = self._selected()
        if not wid:
            self.msg.config(text="Select a work order.")
            return
        notes = SimpleDialog(self, "Resolution notes", "Describe the work completed:").result
        if not notes:
            return
        try:
            services.update_work_order_status(self.app.conn, self.app.user, wid,
                                              "Completed", resolution_notes=notes)
        except (services.WorkflowError, auth.AuthError) as e:
            self.msg.config(text=str(e))
            return
        self.msg.config(text=f"WO #{wid} completed; outage resolved.", foreground="#27767b")
        self.load()


VIEW = {
    "key": "assignments",
    "label": "My Assignments",
    "order": 40,
    "permission": "update_work_order",
    "factory": TechnicianView,
}
