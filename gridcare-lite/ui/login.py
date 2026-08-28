"""Login screen (pre-authentication - not an auto-discovered VIEW)."""

from tkinter import ttk

from core import auth


class LoginView(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=40)
        self.app = app
        ttk.Label(self, text="GridCare-Lite", style="Header.TLabel").grid(
            row=0, column=0, columnspan=2, pady=(0, 4))
        ttk.Label(self, text="Outage & Maintenance Management System",
                  style="Sub.TLabel").grid(row=1, column=0, columnspan=2, pady=(0, 20))
        ttk.Label(self, text="Username").grid(row=2, column=0, sticky="e", padx=6, pady=6)
        self.username = ttk.Entry(self, width=28)
        self.username.grid(row=2, column=1, pady=6)
        ttk.Label(self, text="Password").grid(row=3, column=0, sticky="e", padx=6, pady=6)
        self.password = ttk.Entry(self, width=28, show="*")
        self.password.grid(row=3, column=1, pady=6)
        ttk.Button(self, text="Log In", command=self.attempt).grid(
            row=4, column=0, columnspan=2, pady=(16, 6), ipadx=10)
        self.msg = ttk.Label(self, text="", foreground="#c0392b")
        self.msg.grid(row=5, column=0, columnspan=2)
        ttk.Label(self, text="Demo: admin / engineer / tech1 / tech2 / csr  (pw: Grid@2026)",
                  style="Sub.TLabel").grid(row=6, column=0, columnspan=2, pady=(18, 0))
        self.username.focus_set()
        self.bind_all("<Return>", lambda _e: self.attempt())

    def attempt(self):
        u, p = self.username.get().strip(), self.password.get()
        if not u or not p:
            self.msg.config(text="Enter both a username and a password.")
            return
        try:
            user = auth.authenticate(self.app.conn, u, p)
        except auth.AuthError as e:
            self.msg.config(text=str(e))
            return
        self.unbind_all("<Return>")
        self.app.on_login(user)
