"""GridCare-Lite - Tkinter desktop GUI (entry point).

Outage and Maintenance Management System (CS 112 Final Project).

Run:  python seed_data.py --reset     # first time: build + seed the database
      python app.py

Demo accounts (password  Grid@2026  for all):
  admin / engineer / tech1 / tech2 / csr

The GUI is a thin shell over core/ (db, auth, services, reports). Screens live
in the ui/ package; each ui/*_view.py module exposes a VIEW spec and app.py
discovers them automatically, so adding a screen never means editing app.py.
"""

import importlib
import pkgutil
import tkinter as tk
from tkinter import ttk

import ui
from core import auth
from core.db import init_db

APP_TITLE = "GridCare-Lite - Outage & Maintenance Management"


def discover_views():
    """Return the VIEW specs exported by every ui/*_view.py module, ordered."""
    specs = []
    for mod_info in pkgutil.iter_modules(ui.__path__):
        if not mod_info.name.endswith("_view"):
            continue
        module = importlib.import_module(f"ui.{mod_info.name}")
        spec = getattr(module, "VIEW", None)
        if spec:
            specs.append(spec)
    return sorted(specs, key=lambda s: s.get("order", 100))


class GridCareApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1040x640")
        self.minsize(900, 560)
        self.conn = init_db()
        self.user = None
        self.view_specs = discover_views()
        self._build_style()
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.show_login()

    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("Sub.TLabel", font=("Segoe UI", 10), foreground="#555")
        style.configure("Nav.TButton", anchor="w", padding=(12, 8))
        style.configure("Treeview", rowheight=24)

    def _clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    def show_login(self):
        self.user = None
        self._clear()
        from ui.login import LoginView
        LoginView(self.container, self).pack(expand=True)

    def on_login(self, user):
        self.user = user
        self.show_main()

    def logout(self):
        self.show_login()

    def show_main(self):
        self._clear()
        MainView(self.container, self).pack(fill="both", expand=True)


class MainView(ttk.Frame):
    """Top bar + permission-filtered left nav + swappable content area."""

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        user = app.user

        top = ttk.Frame(self, padding=(16, 10))
        top.pack(fill="x")
        ttk.Label(top, text=user["full_name"], style="Header.TLabel").pack(side="left")
        ttk.Label(top, text=f"  ({user['role']})", style="Sub.TLabel").pack(side="left")
        ttk.Button(top, text="Log Out", command=app.logout).pack(side="right")
        ttk.Separator(self).pack(fill="x")

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True)
        nav = ttk.Frame(body, padding=8, width=190)
        nav.pack(side="left", fill="y")
        nav.pack_propagate(False)
        self.content = ttk.Frame(body, padding=12)
        self.content.pack(side="left", fill="both", expand=True)

        self.registry = {}
        first = None
        for spec in app.view_specs:
            perm = spec.get("permission")
            if perm and not auth.has_permission(user["role"], perm):
                continue
            key = spec["key"]
            self.registry[key] = spec["factory"]
            ttk.Button(nav, text=spec["label"], style="Nav.TButton",
                       command=lambda k=key: self.select(k)).pack(fill="x", pady=2)
            first = first or key
        if first:
            self.select(first)

    def select(self, key):
        for w in self.content.winfo_children():
            w.destroy()
        self.registry[key](self.content, self.app).pack(fill="both", expand=True)


def _smoke_test():
    """Build every permitted view for each demo role without a mainloop."""
    app = GridCareApp()
    print(f"discovered views: {[s['key'] for s in app.view_specs]}")
    for username in ("admin", "engineer", "tech1", "csr"):
        try:
            user = auth.authenticate(app.conn, username, "Grid@2026")
        except auth.AuthError:
            print(f"  (no demo user '{username}' - run seed_data.py)")
            continue
        app.user = user
        app.show_main()
        main = app.container.winfo_children()[0]
        for key in list(main.registry):
            main.select(key)
        print(f"  ok: {sorted(main.registry)} for role '{user['role']}'")
    app.destroy()
    print("smoke test passed")


if __name__ == "__main__":
    import sys
    if "--smoke" in sys.argv:
        _smoke_test()
    else:
        GridCareApp().mainloop()
