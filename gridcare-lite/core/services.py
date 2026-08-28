"""Domain services for GridCare-Lite: outages, work orders, complaints, reports.

Every state-changing function:
  * checks the caller's role via ``auth.require``
  * validates the state-machine transition
  * writes an audit row to status_history

State machines
--------------
outage:      Open -> In Progress -> Resolved
work_order:  Pending -> Scheduled -> Completed
"""

from datetime import datetime, date

from . import auth

OUTAGE_TRANSITIONS = {
    "Open": {"In Progress"},
    "In Progress": {"Resolved", "Open"},
    "Resolved": set(),
}
WORK_ORDER_TRANSITIONS = {
    "Pending": {"Scheduled"},
    "Scheduled": {"Completed", "Pending"},
    "Completed": set(),
}
SEVERITIES = ("Low", "Medium", "High", "Critical")


class WorkflowError(Exception):
    """Raised on an invalid state transition or invalid business input."""


def _audit(conn, entity_type, entity_id, old, new, user_id):
    conn.execute(
        "INSERT INTO status_history (entity_type, entity_id, old_status, new_status, changed_by)"
        " VALUES (?,?,?,?,?)",
        (entity_type, entity_id, old, new, user_id),
    )


def _valid_iso_date(text):
    try:
        datetime.strptime(text, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------------------------
# Substations (reference data)
# ---------------------------------------------------------------------------
def list_substations(conn, region=None):
    sql = "SELECT * FROM substations"
    params = ()
    if region:
        sql += " WHERE region = ?"
        params = (region,)
    return [dict(r) for r in conn.execute(sql + " ORDER BY name", params)]


def substation_exists(conn, substation_id):
    return conn.execute(
        "SELECT 1 FROM substations WHERE substation_id = ?", (substation_id,)
    ).fetchone() is not None


# ---------------------------------------------------------------------------
# Outages
# ---------------------------------------------------------------------------
def create_outage(conn, user, substation_id, description, severity):
    auth.require(user, "create_outage")
    if not substation_exists(conn, substation_id):
        raise WorkflowError(f"No substation with id {substation_id}.")
    if not description or not description.strip():
        raise WorkflowError("Outage description is required.")
    if severity not in SEVERITIES:
        raise WorkflowError(f"Severity must be one of {SEVERITIES}.")
    # reject an exact duplicate open outage for the same substation + description
    dup = conn.execute(
        "SELECT 1 FROM outages WHERE substation_id = ? AND description = ? AND status != 'Resolved'",
        (substation_id, description.strip()),
    ).fetchone()
    if dup:
        raise WorkflowError("An identical open outage already exists for this substation.")
    cur = conn.execute(
        "INSERT INTO outages (substation_id, reported_by, description, severity) VALUES (?,?,?,?)",
        (substation_id, user["user_id"], description.strip(), severity),
    )
    oid = cur.lastrowid
    _audit(conn, "outage", oid, None, "Open", user["user_id"])
    conn.commit()
    return oid


def set_outage_status(conn, user, outage_id, new_status):
    auth.require(user, "resolve_outage")
    row = conn.execute("SELECT status FROM outages WHERE outage_id = ?", (outage_id,)).fetchone()
    if row is None:
        raise WorkflowError(f"No outage with id {outage_id}.")
    old = row["status"]
    if new_status not in OUTAGE_TRANSITIONS.get(old, set()):
        raise WorkflowError(f"Cannot move an outage from '{old}' to '{new_status}'.")
    resolved_at = datetime.now().isoformat(timespec="seconds") if new_status == "Resolved" else None
    conn.execute(
        "UPDATE outages SET status = ?, resolved_at = ? WHERE outage_id = ?",
        (new_status, resolved_at, outage_id),
    )
    _audit(conn, "outage", outage_id, old, new_status, user["user_id"])
    conn.commit()


def list_outages(conn, status=None, region=None):
    sql = ("SELECT o.*, s.name AS substation_name, s.region, s.critical_flag, "
           "u.full_name AS reported_by_name "
           "FROM outages o "
           "JOIN substations s ON s.substation_id = o.substation_id "
           "JOIN users u ON u.user_id = o.reported_by")
    clauses, params = [], []
    if status:
        clauses.append("o.status = ?")
        params.append(status)
    if region:
        clauses.append("s.region = ?")
        params.append(region)
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY o.reported_at DESC"
    return [dict(r) for r in conn.execute(sql, params)]


# ---------------------------------------------------------------------------
# Work orders
# ---------------------------------------------------------------------------
def create_work_order(conn, user, outage_id, technician_id=None, scheduled_date=None):
    auth.require(user, "create_work_order")
    outage = conn.execute("SELECT status FROM outages WHERE outage_id = ?", (outage_id,)).fetchone()
    if outage is None:
        raise WorkflowError(f"No outage with id {outage_id}.")
    if conn.execute("SELECT 1 FROM work_orders WHERE outage_id = ?", (outage_id,)).fetchone():
        raise WorkflowError("This outage already has a work order.")
    if scheduled_date and not _valid_iso_date(scheduled_date):
        raise WorkflowError("Scheduled date must be YYYY-MM-DD.")
    if scheduled_date and datetime.strptime(scheduled_date, "%Y-%m-%d").date() < date.today():
        raise WorkflowError("Scheduled date cannot be in the past.")
    status = "Scheduled" if (technician_id and scheduled_date) else "Pending"
    if technician_id is not None:
        _assert_technician(conn, technician_id)
    cur = conn.execute(
        "INSERT INTO work_orders (outage_id, created_by, assigned_technician, scheduled_date, status)"
        " VALUES (?,?,?,?,?)",
        (outage_id, user["user_id"], technician_id, scheduled_date, status),
    )
    wid = cur.lastrowid
    _audit(conn, "work_order", wid, None, status, user["user_id"])
    conn.commit()
    return wid


def _assert_technician(conn, technician_id):
    row = conn.execute("SELECT role FROM users WHERE user_id = ? AND active = 1",
                       (technician_id,)).fetchone()
    if row is None:
        raise WorkflowError(f"No active user with id {technician_id}.")
    if row["role"] != "technician":
        raise WorkflowError("Work orders can only be assigned to a technician.")


def assign_technician(conn, user, work_order_id, technician_id, scheduled_date):
    auth.require(user, "assign_technician")
    row = conn.execute("SELECT status FROM work_orders WHERE work_order_id = ?",
                       (work_order_id,)).fetchone()
    if row is None:
        raise WorkflowError(f"No work order with id {work_order_id}.")
    if row["status"] == "Completed":
        raise WorkflowError("Cannot reassign a completed work order.")
    if not _valid_iso_date(scheduled_date):
        raise WorkflowError("Scheduled date must be YYYY-MM-DD.")
    if datetime.strptime(scheduled_date, "%Y-%m-%d").date() < date.today():
        raise WorkflowError("Scheduled date cannot be in the past.")
    _assert_technician(conn, technician_id)
    old = row["status"]
    conn.execute(
        "UPDATE work_orders SET assigned_technician = ?, scheduled_date = ?, status = 'Scheduled'"
        " WHERE work_order_id = ?",
        (technician_id, scheduled_date, work_order_id),
    )
    if old != "Scheduled":
        _audit(conn, "work_order", work_order_id, old, "Scheduled", user["user_id"])
    conn.commit()


def update_work_order_status(conn, user, work_order_id, new_status, resolution_notes=None):
    auth.require(user, "update_work_order")
    row = conn.execute(
        "SELECT wo.status, wo.assigned_technician, wo.outage_id "
        "FROM work_orders wo WHERE wo.work_order_id = ?", (work_order_id,)
    ).fetchone()
    if row is None:
        raise WorkflowError(f"No work order with id {work_order_id}.")
    # a technician may only touch their own work orders
    if user["role"] == "technician" and row["assigned_technician"] != user["user_id"]:
        raise auth.AuthError("Technicians can only update work orders assigned to them.")
    old = row["status"]
    if new_status not in WORK_ORDER_TRANSITIONS.get(old, set()):
        raise WorkflowError(f"Cannot move a work order from '{old}' to '{new_status}'.")
    if new_status == "Completed" and not (resolution_notes and resolution_notes.strip()):
        raise WorkflowError("Resolution notes are required to complete a work order.")
    completed_at = datetime.now().isoformat(timespec="seconds") if new_status == "Completed" else None
    conn.execute(
        "UPDATE work_orders SET status = ?, resolution_notes = COALESCE(?, resolution_notes),"
        " completed_at = ? WHERE work_order_id = ?",
        (new_status, resolution_notes, completed_at, work_order_id),
    )
    _audit(conn, "work_order", work_order_id, old, new_status, user["user_id"])
    # completing the work order moves the linked outage on as well
    if new_status == "Completed":
        o = conn.execute("SELECT status FROM outages WHERE outage_id = ?",
                         (row["outage_id"],)).fetchone()
        if o["status"] == "Open":
            conn.execute("UPDATE outages SET status = 'In Progress' WHERE outage_id = ?",
                         (row["outage_id"],))
            _audit(conn, "outage", row["outage_id"], "Open", "In Progress", user["user_id"])
        conn.execute(
            "UPDATE outages SET status = 'Resolved', resolved_at = ? WHERE outage_id = ?",
            (datetime.now().isoformat(timespec="seconds"), row["outage_id"]),
        )
        _audit(conn, "outage", row["outage_id"],
               "In Progress", "Resolved", user["user_id"])
    conn.commit()


def start_work_order(conn, user, work_order_id):
    """Convenience: technician marks a scheduled job as being worked (keeps it Scheduled,
    but moves the linked outage to 'In Progress')."""
    auth.require(user, "update_work_order")
    row = conn.execute("SELECT assigned_technician, outage_id FROM work_orders WHERE work_order_id = ?",
                       (work_order_id,)).fetchone()
    if row is None:
        raise WorkflowError(f"No work order with id {work_order_id}.")
    if user["role"] == "technician" and row["assigned_technician"] != user["user_id"]:
        raise auth.AuthError("Technicians can only update work orders assigned to them.")
    o = conn.execute("SELECT status FROM outages WHERE outage_id = ?", (row["outage_id"],)).fetchone()
    if o["status"] == "Open":
        conn.execute("UPDATE outages SET status = 'In Progress' WHERE outage_id = ?",
                     (row["outage_id"],))
        _audit(conn, "outage", row["outage_id"], "Open", "In Progress", user["user_id"])
        conn.commit()


def list_work_orders(conn, technician_id=None):
    sql = ("SELECT wo.*, o.description AS outage_description, s.name AS substation_name, "
           "s.region, t.full_name AS technician_name "
           "FROM work_orders wo "
           "JOIN outages o ON o.outage_id = wo.outage_id "
           "JOIN substations s ON s.substation_id = o.substation_id "
           "LEFT JOIN users t ON t.user_id = wo.assigned_technician")
    params = []
    if technician_id is not None:
        sql += " WHERE wo.assigned_technician = ?"
        params.append(technician_id)
    sql += " ORDER BY wo.scheduled_date IS NULL, wo.scheduled_date"
    return [dict(r) for r in conn.execute(sql, params)]


# ---------------------------------------------------------------------------
# Complaints
# ---------------------------------------------------------------------------
def log_complaint(conn, user, customer_name, description, customer_contact=None, outage_id=None):
    auth.require(user, "log_complaint")
    if not customer_name or not customer_name.strip():
        raise WorkflowError("Customer name is required.")
    if not description or not description.strip():
        raise WorkflowError("Complaint description is required.")
    if outage_id is not None and not conn.execute(
        "SELECT 1 FROM outages WHERE outage_id = ?", (outage_id,)
    ).fetchone():
        raise WorkflowError(f"No outage with id {outage_id} to link to.")
    status = "Linked" if outage_id else "Open"
    cur = conn.execute(
        "INSERT INTO complaints (logged_by, customer_name, customer_contact, description, outage_id, status)"
        " VALUES (?,?,?,?,?,?)",
        (user["user_id"], customer_name.strip(), customer_contact,
         description.strip(), outage_id, status),
    )
    conn.commit()
    return cur.lastrowid


def link_complaint(conn, user, complaint_id, outage_id):
    auth.require(user, "link_complaint")
    if not conn.execute("SELECT 1 FROM complaints WHERE complaint_id = ?", (complaint_id,)).fetchone():
        raise WorkflowError(f"No complaint with id {complaint_id}.")
    if not conn.execute("SELECT 1 FROM outages WHERE outage_id = ?", (outage_id,)).fetchone():
        raise WorkflowError(f"No outage with id {outage_id}.")
    conn.execute("UPDATE complaints SET outage_id = ?, status = 'Linked' WHERE complaint_id = ?",
                 (outage_id, complaint_id))
    conn.commit()


def list_complaints(conn):
    return [dict(r) for r in conn.execute(
        "SELECT c.*, u.full_name AS logged_by_name, o.description AS outage_description "
        "FROM complaints c JOIN users u ON u.user_id = c.logged_by "
        "LEFT JOIN outages o ON o.outage_id = c.outage_id "
        "ORDER BY c.created_at DESC")]
