"""Import cleaned substation and line reference data into the GridCare-Lite DB.

Source of truth: the grid-analysis component's cleaned CSVs. This is the
integration point required by the brief - outages can only be logged against a
substation that exists in the analysed dataset. The critical_flag column is set
from the network-analysis betweenness-centrality ranking (a *structural* proxy
on synthetic data, clearly labelled as such in the UI and reports).

Run:  python import_grid_data.py
"""

import csv
import os

from core.db import init_db

HERE = os.path.dirname(os.path.abspath(__file__))
GRID = os.path.normpath(os.path.join(HERE, "..", "grid-analysis"))
CLEANED = os.path.join(GRID, "cleaned_data")
NETWORK = os.path.join(GRID, "network_analysis")

SUBS_CSV = os.path.join(CLEANED, "substations_clean.csv")
LINES_CSV = os.path.join(CLEANED, "lines_clean.csv")
METRICS_CSV = os.path.join(NETWORK, "network_metrics.csv")


def _critical_ids(top_n=5):
    if not os.path.exists(METRICS_CSV):
        return set()
    with open(METRICS_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    rows.sort(key=lambda r: float(r.get("Betweenness Centrality", 0) or 0), reverse=True)
    return {int(r["Substation ID"]) for r in rows[:top_n]}


def import_reference_data(db_path=None):
    conn = init_db(db_path) if db_path else init_db()
    if not os.path.exists(SUBS_CSV):
        raise FileNotFoundError(
            f"{SUBS_CSV} not found - run grid-analysis/task1_data_cleaning.py first.")

    critical = _critical_ids()
    with open(SUBS_CSV, newline="", encoding="utf-8") as f:
        subs = list(csv.DictReader(f))
    conn.executemany(
        "INSERT OR REPLACE INTO substations "
        "(substation_id, name, short_name, region, voltage_kv, capacity_mva, status, critical_flag)"
        " VALUES (?,?,?,?,?,?,?,?)",
        [(int(r["Substation ID"]), r["Name"], r["Short Name"], r["Region"],
          int(float(r["Voltage (kV)"])), float(r["Capacity (MVA)"]), r["Status"],
          1 if int(r["Substation ID"]) in critical else 0) for r in subs],
    )

    if os.path.exists(LINES_CSV):
        with open(LINES_CSV, newline="", encoding="utf-8") as f:
            lines = list(csv.DictReader(f))
        conn.executemany(
            "INSERT OR REPLACE INTO lines "
            "(line_id, utility, source_id, dest_id, voltage_kv, length_km, status)"
            " VALUES (?,?,?,?,?,?,?)",
            [(int(r["Line ID"]), r.get("Utility ID", ""),
              int(r["Source Substation ID"]), int(r["Destination Substation ID"]),
              int(float(r["Voltage (kV)"])), float(r["Length (km)"]), r["Status"])
             for r in lines],
        )
    conn.commit()
    n_sub = conn.execute("SELECT COUNT(*) c FROM substations").fetchone()["c"]
    n_line = conn.execute("SELECT COUNT(*) c FROM lines").fetchone()["c"]
    print(f"Imported {n_sub} substations ({len(critical)} flagged critical) and {n_line} lines.")
    return conn


if __name__ == "__main__":
    import_reference_data()
