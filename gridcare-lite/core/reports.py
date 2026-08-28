"""Operational reporting for GridCare-Lite (admin / engineer)."""

from datetime import datetime

from . import auth


def operational_summary(conn, user):

    auth.require(user, "view_reports")
    total = conn.execute("SELECT COUNT(*) c FROM outages").fetchone()["c"]
    by_status = {r["status"]: r["c"] for r in conn.execute(
        "SELECT status, COUNT(*) c FROM outages GROUP BY status")}
    by_region = {r["region"]: r["c"] for r in conn.execute(
        "SELECT s.region, COUNT(*) c FROM outages o "
        "JOIN substations s ON s.substation_id = o.substation_id GROUP BY s.region")}
    by_severity = {r["severity"]: r["c"] for r in conn.execute(
        "SELECT severity, COUNT(*) c FROM outages GROUP BY severity")}
    # average resolution time in hours
    rows = conn.execute(
        "SELECT reported_at, resolved_at FROM outages WHERE resolved_at IS NOT NULL").fetchall()
    hrs = []
    for r in rows:
        try:
            a = datetime.fromisoformat(r["reported_at"].replace(" ", "T"))
            b = datetime.fromisoformat(r["resolved_at"].replace(" ", "T"))
            hrs.append((b - a).total_seconds() / 3600)
        except (ValueError, AttributeError):
            continue
    avg_res = round(sum(hrs) / len(hrs), 1) if hrs else None
    critical_open = conn.execute(
        "SELECT COUNT(*) c FROM outages o JOIN substations s ON s.substation_id = o.substation_id "
        "WHERE o.status != 'Resolved' AND s.critical_flag = 1").fetchone()["c"]
    return {
        "total_outages": total,
        "outages_by_status": by_status,
        "outages_by_region": by_region,
        "outages_by_severity": by_severity,
        "avg_resolution_hours": avg_res,
        "open_outages_on_critical_substations": critical_open,
        "open_work_orders": conn.execute(
            "SELECT COUNT(*) c FROM work_orders WHERE status != 'Completed'").fetchone()["c"],
        "complaints_open": conn.execute(
            "SELECT COUNT(*) c FROM complaints WHERE status != 'Closed'").fetchone()["c"],
    }
