"""Seed GridCare-Lite with demo users and a sample outage-to-resolution workflow.

All accounts are fictional demo accounts. Default password for every demo
account is  Grid@2026  (meets the complexity rule: letter + digit + >=8 chars).

Run:  python seed_data.py            # create DB, import grid data, seed demo content
      python seed_data.py --reset    # delete the DB first
"""

import sys

from core.db import DEFAULT_DB, reset_db
from core import auth, services
from import_grid_data import import_reference_data

DEMO_PASSWORD = "Grid@2026"

DEMO_USERS = [
    ("admin",   "Ama Mensah",      "admin"),
    ("engineer", "Kofi Boateng",   "engineer"),
    ("tech1",   "Yaw Owusu",       "technician"),
    ("tech2",   "Efua Sarpong",    "technician"),
    ("csr",     "Adjoa Nyarko",    "customer_service"),
]


def seed(reset=False):
    if reset:
        reset_db()
    conn = import_reference_data()

    existing = {r["username"] for r in conn.execute("SELECT username FROM users")}
    ids = {}
    for username, full_name, role in DEMO_USERS:
        if username in existing:
            ids[username] = conn.execute(
                "SELECT user_id FROM users WHERE username = ?", (username,)).fetchone()["user_id"]
            continue
        ids[username] = auth.create_user(conn, username, DEMO_PASSWORD, full_name, role)
    print(f"Demo users: {', '.join(ids)}  (password: {DEMO_PASSWORD})")

    if conn.execute("SELECT COUNT(*) c FROM outages").fetchone()["c"] > 0:
        print("Outages already present - skipping sample workflow.")
        return conn

    engineer = auth.authenticate(conn, "engineer", DEMO_PASSWORD)
    admin = auth.authenticate(conn, "admin", DEMO_PASSWORD)
    tech1 = auth.authenticate(conn, "tech1", DEMO_PASSWORD)
    csr = auth.authenticate(conn, "csr", DEMO_PASSWORD)

    subs = services.list_substations(conn)
    s0, s1, s2 = subs[0]["substation_id"], subs[1]["substation_id"], subs[2]["substation_id"]

    # 1. engineer logs outages
    o1 = services.create_outage(conn, engineer, s0,
                                "Transformer bay 2 tripped on overcurrent; supply lost.", "High")
    o2 = services.create_outage(conn, engineer, s1,
                                "Vegetation contact on incoming feeder, intermittent faults.", "Medium")
    services.create_outage(conn, engineer, s2,
                           "Routine inspection found corroded earth strap.", "Low")

    # 2. admin creates + assigns work orders
    w1 = services.create_work_order(conn, admin, o1, technician_id=tech1["user_id"],
                                    scheduled_date="2026-08-29")
    services.create_work_order(conn, admin, o2)

    # 3. technician works and completes the first job -> outage auto-resolves
    services.start_work_order(conn, tech1, w1)
    services.update_work_order_status(conn, tech1, w1, "Completed",
                                      resolution_notes="Replaced protection relay, meggered cable, "
                                                       "restored supply, load normal.")

    # 4. customer service logs a complaint and links it to the open outage
    services.log_complaint(conn, csr, "Kwabena A.", "No power since last night, food spoiling.",
                           customer_contact="024-000-0000", outage_id=o2)

    print("Seeded 3 outages, 2 work orders (1 completed), 1 complaint.")
    print(f"Database: {DEFAULT_DB}")
    return conn


if __name__ == "__main__":
    seed(reset="--reset" in sys.argv)
