"""Landing screen shown after login - summarises the user's role and permissions."""

from tkinter import ttk

from core import auth


class HomeView(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        user = app.user
        ttk.Label(self, text=f"Signed in as {user['full_name']}",
                  style="Header.TLabel").pack(anchor="w")
        ttk.Label(self, text=f"Role: {user['role']}", style="Sub.TLabel").pack(anchor="w", pady=(0, 12))

        allowed = sorted(p for p, roles in auth.PERMISSIONS.items() if user["role"] in roles)
        box = ttk.LabelFrame(self, text="What you can do", padding=10)
        box.pack(fill="x")
        for perm in allowed:
            ttk.Label(box, text="• " + perm.replace("_", " ")).pack(anchor="w")

        ttk.Label(self, text="Use the menu on the left. You only see the screens your "
                             "role is permitted to use; the service layer also rejects "
                             "any out-of-role action.",
                  style="Sub.TLabel", wraplength=560).pack(anchor="w", pady=12)


VIEW = {
    "key": "home",
    "label": "Home",
    "order": 0,
    "permission": None,
    "factory": HomeView,
}
