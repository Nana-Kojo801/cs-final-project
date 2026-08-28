"""Work orders - list all, and (admin only) create / assign."""

from tkinter import ttk

from core import auth, services
from ui._widgets import make_tree


class WorkOrderView(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.is_admin = app.user["role"] == "admin"
        ttk.Label(self, text="Work Orders", style="Header.TLabel").pack(anchor="w")
        self.tree = make_tree(self, ("WO", "Outage", "Substation", "Region", "Status",
                                     "Technician", "Scheduled"),
                              (40, 60, 150, 110, 90, 130, 100))
        if self.is_admin:
            box = ttk.LabelFrame(self, text="Create / assign work order", padding=8)
            box.pack(fill="x", pady=6)
            self.open_outages = [o for o in services.list_outages(app.conn)
                                 if o["status"] != "Resolved"]
            self.o_map = {f"#{o['outage_id']} {o['substation_name']}": o["outage_id"]
                          for o in self.open_outages}
            self.techs = [dict(r) for r in app.conn.execute(
                "SELECT user_id, full_name FROM users WHERE role='technician' AND active=1")]
            self.t_map = {t["full_name"]: t["user_id"] for t in self.techs}
            ttk.Label(box, text="Outage").grid(row=0, column=0, padx=4, pady=4, sticky="e")
            self.oc = ttk.Combobox(box, values=list(self.o_map), width=32, state="readonly")
            self.oc.grid(row=0, column=1, padx=4)
            ttk.Label(box, text="Technician").grid(row=0, column=2, padx=4, sticky="e")
            self.tc = ttk.Combobox(box, values=list(self.t_map), width=20, state="readonly")
            self.tc.grid(row=0, column=3, padx=4)
            ttk.Label(box, text="Date (YYYY-MM-DD)").grid(row=0, column=4, padx=4, sticky="e")
            self.dt = ttk.Entry(box, width=14)
            self.dt.grid(row=0, column=5, padx=4)
            ttk.Button(box, text="Save", command=self.create).grid(row=0, column=6, padx=6)
            self.msg = ttk.Label(box, text="", foreground="#c0392b")
            self.msg.grid(row=1, column=0, columnspan=7, sticky="w")
        self.load()

    def load(self):
        self.tree.delete(*self.tree.get_children())
        for w in services.list_work_orders(self.app.conn):
            self.tree.insert("", "end", values=(
                w["work_order_id"], w["outage_id"], w["substation_name"], w["region"],
                w["status"], w["technician_name"] or "-", w["scheduled_date"] or "-"))

    def create(self):
        if not self.oc.get():
            self.msg.config(text="Pick an outage.")
            return
        tech = self.t_map.get(self.tc.get())
        date = self.dt.get().strip() or None
        try:
            services.create_work_order(self.app.conn, self.app.user,
                                       self.o_map[self.oc.get()], tech, date)
        except (services.WorkflowError, auth.AuthError) as e:
            self.msg.config(text=str(e))
            return
        self.msg.config(text="Work order saved.", foreground="#27767b")
        self.load()


VIEW = {
    "key": "work_orders",
    "label": "Work Orders",
    "order": 30,
    "permission": "view_outages",
    "factory": WorkOrderView,
}
