# CS 112 — Computer Programming for CS · Final Course Project (Summer 2026)

**Cohort A · Team 3**
Public repository: <https://github.com/Nana-Kojo801/cs-final-project>

| Member | Student ID | Primary responsibility |
|---|---|---|
| Nana Kojo Atta-Benyah | *[student ID]* | Data engineering & network analysis lead (grid-analysis Tasks 1, 1b, 2, 4; ClinicCare-Lite data model) |
| Brian Edem Bedzrah | *[52722029]* | N-1 contingency analysis; ClinicCare-Lite auth & submission workflow |
| Shawn Tei Kpoti | *[student ID]* | GridCare-Lite lead (schema, RBAC, outage-to-resolution workflow, reporting); integration testing |
| Nana Ekow Amuah | *[student ID]* | Visualisation, interactive map & dashboards; ClinicCare-Lite messaging, analytics; slides |

> Replace *[student ID]* with each member's real ID before submitting.

---

## The three components

### 1. `grid-analysis/` — National Electricity Grid Network Analysis
A reproducible data-science pipeline over a **synthetic, seeded** Ghana / West-Africa
electricity-grid dataset (utilities, substations, transmission/distribution lines).
It cleans and validates the data, integrates the three tables, runs exploratory
analysis, models the grid as a NetworkX graph, computes centrality and community
metrics, performs a simplified **N-1 contingency analysis**, and exports static
charts plus an interactive map and a Streamlit dashboard. All figures are
illustrative, not official measurements of Ghana's grid.

### 2. `gridcare-lite/` — Outage & Maintenance Management System
A role-based **Tkinter desktop application** backed by **SQLite** that simulates
the internal tool a utility (ECG / GRIDCo) would use to run the outage lifecycle:
an engineer logs an outage against a real substation (imported from
grid-analysis), an administrator creates and assigns a work order, a technician
works and completes it (auto-resolving the outage), and customer-service staff
log and link complaints. RBAC and state-machine transitions are enforced in the
service layer and by database constraints — not just by hiding buttons.

### 3. `clinic-lite/` — Clinic Patient Administration & Communication System
A secure, role-based **Flask web application** (JSON storage) for clinician and
patient administrative workflows: health-task assignment, patient file
submission with a **structural** form-completeness check, categorical clinician
review, in-app notifications and secure non-urgent messaging, appointment
reminders, a **private** wellness-engagement tracker, and operational analytics.
**It is administrative and communication only — it never diagnoses, interprets
symptoms, scores health data, or recommends treatment.**

---

## Setup

Requires **Python 3.11+**. From this folder:

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate      macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
```

`tkinter` and `sqlite3` ship with CPython. On Debian/Ubuntu install
`python3-tk` if Tkinter is missing.

---

## Running each component

### grid-analysis
```bash
cd grid-analysis
python generate_grid_data.py            # (optional) regenerate the 3 raw CSVs
python task1_data_cleaning.py           # -> cleaned_data/
python task1b_data_integration.py       # -> integrated_data/
python task2_networkx_graph.py          # -> network_analysis/ (metrics + report)
python eda_charts.py              # -> charts/*.png
python merge_analysis.py          # -> integrated_data/master_lines.csv + charts
python n1_contingency.py + interactive_map.py # -> charts/, network_analysis/, maps/*.html
streamlit run dashboard_app.py          # (optional) interactive dashboard at :8501
```
Open `maps/grid_interactive_map.html` in a browser for the interactive map.

### gridcare-lite
```bash
cd gridcare-lite
python seed_data.py --reset             # build gridcare.db, import grid data, add demo content
python app.py                           # launches the Tkinter GUI
python -m unittest discover -s tests    # 24 tests
```
**Demo accounts** (password `Grid@2026` for all):
`admin` · `engineer` · `tech1` · `tech2` · `csr`

### clinic-lite
```bash
cd clinic-lite
cp .env.example .env                    # optional; app runs without it
python seed_data.py --reset             # create data/ + demo accounts and workflow
python app.py                           # http://127.0.0.1:5000
python -m unittest discover -s tests    # 28 tests
```
**Demo accounts** (password `Clinic@2026` for all):

| Role | ID |
|---|---|
| Clinician | `10000000` |
| Patient | `20142024` |
| Patient | `20232023` |
| Patient | `20452022` |

With no SMTP configured, all email notifications are written to
`clinic-lite/data/notifications.log` and mirrored to each user's in-app Inbox.

---

## Reproducibility

The dataset generator (`grid-analysis/generate_grid_data.py`) is run with
`random.seed(42)` **unchanged**, so every run produces byte-identical
`utilities.csv`, `substations.csv` and `lines.csv` (10 utilities, 44
substations, 55 lines). All analysis outputs in `cleaned_data/`,
`integrated_data/`, `network_analysis/`, `charts/` and `maps/` were generated
from that seeded data and can be regenerated with the commands above.

---

## Known limitations

- **Synthetic data.** Coordinates, capacities, commissioning years and
  connections are illustrative. Network metrics are *structural* observations,
  not electrical load / power-flow results. The N-1 analysis is a graph-topology
  approximation, not a real contingency study.
- **grid-analysis** cleaned graph has 3 connected components (a few isolated
  substations); this is reported and discussed rather than hidden.
- **GridCare-Lite** is a single-user desktop app (one SQLite file, no
  concurrent-write handling) and uses a simple `datetime('now')` clock.
- **ClinicCare-Lite** uses flat JSON files with a process-level lock — fine for
  a demo, not for real concurrency. Real-time messaging is periodic polling
  (12 s), not WebSockets. Email delivery is best-effort and falls back to a log
  file. Session storage is the default Flask signed cookie.
- Neither app is hardened for production (no rate limiting, CSRF tokens, or
  audited deployment configuration).

---

## Repository / documentation map

```
grid-analysis/      dataset generator, Task 1–5 scripts, cleaned/integrated/network outputs,
                    charts/ (PNG), maps/ (interactive HTML), dashboard_app.py, data_dictionary.md, er_diagram.md
gridcare-lite/      core/ (db, auth, services), app.py (Tkinter GUI), schema.sql,
                    import_grid_data.py, seed_data.py, data_dictionary.md, tests/
clinic-lite/   app.py, config.py, models/, utils/, templates/, static/, data/, submissions/,
                    seed_data.py, .env.example, tests/
docs/               technical report, data-science report, diagrams, user guides,
                    test plan & report, defect log, team contribution report
slides/             presentation slides
video/              demonstration video script (record separately)
requirements.txt    all Python dependencies
```
