"""Customer complaint log - customer-service staff log and link complaints."""

import tkinter as tk
from tkinter import ttk

from core import auth, services
from ui._widgets import make_tree


class ComplaintView(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        ttk.Label(self, text="Customer Complaints", style="Header.TLabel").pack(anchor="w")
        self.tree = make_tree(self, ("ID", "Customer", "Description", "Status", "Outage", "Logged at"),
                              (40, 130, 320, 80, 60, 140))
        box = ttk.LabelFrame(self, text="Log a complaint", padding=8)
        box.pack(fill="x", pady=6)
        ttk.Label(box, text="Customer name").grid(row=0, column=0, sticky="e", padx=4, pady=3)
        self.name = ttk.Entry(box, width=24)
        self.name.grid(row=0, column=1, padx=4)
        ttk.Label(box, text="Contact").grid(row=0, column=2, sticky="e", padx=4)
        self.contact = ttk.Entry(box, width=18)
        self.contact.grid(row=0, column=3, padx=4)
        ttk.Label(box, text="Link to outage #").grid(row=0, column=4, sticky="e", padx=4)
        self.outage = ttk.Entry(box, width=8)
        self.outage.grid(row=0, column=5, padx=4)
        ttk.Label(box, text="Description").grid(row=1, column=0, sticky="ne", padx=4, pady=3)
        self.desc = tk.Text(box, width=60, height=3)
        self.desc.grid(row=1, column=1, columnspan=5, pady=3, sticky="w")
        ttk.Button(box, text="Save", command=self.save).grid(row=2, column=1, sticky="w", pady=4)
        self.msg = ttk.Label(box, text="", foreground="#c0392b")
        self.msg.grid(row=2, column=2, columnspan=4, sticky="w")
        self.load()

    def load(self):
        self.tree.delete(*self.tree.get_children())
        for c in services.list_complaints(self.app.conn):
            self.tree.insert("", "end", values=(
                c["complaint_id"], c["customer_name"], c["description"], c["status"],
                c["outage_id"] or "-", c["created_at"]))

    def save(self):
        oid = self.outage.get().strip()
        try:
            services.log_complaint(
                self.app.conn, self.app.user, self.name.get(), self.desc.get("1.0", "end"),
                customer_contact=self.contact.get().strip() or None,
                outage_id=int(oid) if oid else None)
        except ValueError:
            self.msg.config(text="Outage # must be a number.")
            return
        except (services.WorkflowError, auth.AuthError) as e:
            self.msg.config(text=str(e))
            return
        self.msg.config(text="Complaint saved.", foreground="#27767b")
        self.name.delete(0, "end")
        self.contact.delete(0, "end")
        self.outage.delete(0, "end")
        self.desc.delete("1.0", "end")
        self.load()


VIEW = {
    "key": "complaints",
    "label": "Complaints",
    "order": 50,
    "permission": "log_complaint",
    "factory": ComplaintView,
}
