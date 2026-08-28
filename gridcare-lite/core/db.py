"""Database connection and schema initialisation for GridCare-Lite."""

import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
DEFAULT_DB = os.path.join(PROJECT_ROOT, "gridcare.db")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "schema.sql")


def connect(db_path=DEFAULT_DB):
    """Return a SQLite connection with foreign keys enforced and row access by name."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path=DEFAULT_DB, schema_path=SCHEMA_PATH):
    """Create every table from schema.sql if it does not already exist."""
    conn = connect(db_path)
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    return conn


def reset_db(db_path=DEFAULT_DB):
    """Delete the database file (used by tests and by seed_data.py --reset)."""
    if os.path.exists(db_path):
        os.remove(db_path)
