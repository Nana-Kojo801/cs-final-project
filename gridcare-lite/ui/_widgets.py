"""Small shared Tkinter helpers used by several views."""

import tkinter as tk
from tkinter import ttk


def make_tree(parent, columns, widths):
    tree = ttk.Treeview(parent, columns=columns, show="headings")
    for col, w in zip(columns, widths):
        tree.heading(col, text=col)
        tree.column(col, width=w, anchor="w")
    tree.pack(fill="both", expand=True, pady=6)
    return tree


class SimpleDialog(tk.Toplevel):
    """Minimal modal multi-line text-input dialog."""

    def __init__(self, parent, title, prompt):
        super().__init__(parent)
        self.title(title)
        self.result = None
        self.transient(parent)
        self.grab_set()
        ttk.Label(self, text=prompt, padding=10).pack(anchor="w")
        self.text = tk.Text(self, width=50, height=5)
        self.text.pack(padx=10)
        bar = ttk.Frame(self, padding=8)
        bar.pack()
        ttk.Button(bar, text="OK", command=self._ok).pack(side="left", padx=4)
        ttk.Button(bar, text="Cancel", command=self.destroy).pack(side="left", padx=4)
        self.text.focus_set()
        self.wait_window(self)

    def _ok(self):
        self.result = self.text.get("1.0", "end").strip()
        self.destroy()
