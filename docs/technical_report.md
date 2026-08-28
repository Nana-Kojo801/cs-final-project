# Technical Report

**Integrated Data Science and Software Engineering Project**
National Electricity Grid Network Analysis · GridCare-Lite · ClinicCare-Lite

---

### Cover page

| | |
|---|---|
| **Title** | National Electricity Grid Network Analysis, GridCare-Lite, and ClinicCare-Lite |
| **Course** | CS 112 — Computer Programming for CS (Summer 2026) |
| **Cohort / Team** | Cohort A · Team 3 |
| **Team members** | Nana Kojo Atta-Benyah (90452029), Brian Edem Bedzrah (52722029), Shawn Tei Kpoti (24212029), Nana Ekow Amuah (91262029) |
| **Instructor** | Robert Sowah |
| **Date** | 28 August 2026 |
| **Repository** | https://github.com/Nana-Kojo801/cs-final-project |

---

## 1. Introduction

### 1.1 Background
Electricity and healthcare are two national-scale systems that depend on good
data management and reliable software. An electricity grid is a geographically
distributed, safety-critical network whose operation depends on accurate asset
records, connectivity analysis, and coordinated maintenance. An outpatient
clinic is a human-centred service that depends on secure records, timely
communication, privacy protection, and dependable administrative workflows.
This project builds one analytical component and two software components that,
between them, exercise data cleaning, network science, geospatial
visualisation, database design, secure authentication, role-based access
control, GUI/web development, testing, and technical communication.

### 1.2 Objectives
1. Produce a **reproducible** analysis of a synthetic national grid dataset:
   clean and validate it, integrate the three tables, run exploratory and
   network analysis (including a simplified N-1 contingency study), and
   communicate the findings through static and interactive visualisations.
2. Build **GridCare-Lite**, a role-based desktop application that runs the
   complete outage-to-resolution workflow for a utility, using the cleaned
   substation data as its reference asset register.
3. Build **ClinicCare-Lite**, a secure role-based clinic administration and
   communication web application that remains **strictly administrative and
   non-diagnostic**.

### 1.3 Problem statement
Real substation-level grid topology for Ghana is not publicly available in a
clean, structured form, and real patient data cannot be used in coursework.
The project therefore works from a **seeded synthetic dataset** and **fictional
demo accounts**, so every result is reproducible and no confidential
information is exposed, while still demonstrating the full development
lifecycle.

### 1.4 Summary of approach
- A single seeded generator script (`random.seed(42)`, unchanged) produces
  byte-identical CSVs for every run.
- The grid analysis is a sequence of standalone Python scripts, each writing a
  markdown report plus CSV/PNG/HTML artifacts to a dedicated output folder.
- GridCare-Lite separates a testable `core/` package (database, auth, RBAC,
  workflow state machines) from a thin Tkinter GUI.
- ClinicCare-Lite is a Flask app with a `models/` + `utils/` layer over JSON
  storage; every privacy and scope rule is enforced in that layer and covered
  by unit tests.
- 52 automated tests (24 GridCare-Lite, 28 ClinicCare-Lite) plus a documented
  manual test plan.

---

## 2. Dataset overview

### 2.1 Source
`grid-analysis/generate_grid_data.py`, run once with `random.seed(42)`. Output:

| File | Rows | Key fields |
|---|---|---|
| `utilities.csv` | 10 | Utility ID, Name, Alias, Code, Type, Country, Active |
| `substations.csv` | 44 | Substation ID, Name, Short Name, Region, Country, Latitude, Longitude, Voltage (kV), Capacity (MVA), Commissioning Year, Type, Status |
| `lines.csv` | 55 | Line ID, Utility ID, Source/Destination Substation ID + name, Voltage (kV), Length (km), Capacity (MVA), Status, Line Type |

The data is grounded in real Ghanaian geography and real utility names (ECG,
NEDCo, GRIDCo, VRA) with plausible West African Power Pool cross-border
interconnections. **All coordinates, capacities, commissioning years and
connections are synthetic and illustrative.**

### 2.2 Size and shape
10 utilities · 44 substations across 10 Ghanaian regions plus 8 cross-border
nodes · 55 lines (40 overhead, 15 underground). Voltage levels: 11, 33, 69,
161, 330 kV. Substation capacity ranges 6.4–506 MVA (median ≈ 108 MVA, a
right-skewed distribution).

### 2.3 Data-quality checks performed (Task 1)
Even though the generator emits clean data, the cleaning script treats the
input as an untrusted asset register and checks:

- **Types** — Latitude/Longitude/Capacity/Length coerced to numeric with
  `errors='coerce'`; commissioning year and voltage checked as integers.
- **Missing values** — `isnull().sum()` per column; documented imputation
  policy (none required for this seed; policy stated for real data).
- **Duplicates** — full-row duplicate check on all three tables (0 found).
- **Coordinate plausibility** — every lat/long checked against West African
  bounds (roughly lat 4–12 °N, long −14–3 °E).
- **Foreign-key integrity** — every `Source/Destination Substation ID` in
  `lines.csv` verified against `substations.csv`; every `Utility ID` verified
  against `utilities.csv`. 0 orphaned references.
- **Categorical consistency** — Status, Type, Line Type values checked against
  their allowed sets.

Result: 0 rows dropped, 0 imputations required, 0 orphaned foreign keys.
Full detail: `grid-analysis/cleaned_data/data_cleaning_report.md`.

### 2.4 Sample (first rows of `substations.csv`)

| ID | Name | Region | Lat | Long | kV | MVA | Year | Type | Status |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Achimota Substation | Greater Accra | 5.6085 | −0.2193 | 11 | 6.4 | 2008 | Distribution | Active |
| 2 | Tema Substation | Greater Accra | 5.6596 | −0.0226 | 330 | 48.5 | 1997 | Transmission | Active |
| 3 | Mallam Substation | Greater Accra | 5.5600 | −0.2980 | 11 | 36.4 | … | Distribution | Active |

### 2.5 Integration (Task 1b / Task 4)
A left join keyed on `Utility ID` and the two substation-ID foreign keys
produces a 55-row master line-level table (`integrated_data/master_lines.csv`,
28 columns) with source/destination region and country and utility metadata
attached. Row count is unchanged by the join (55 → 55) and no data is lost,
confirming referential integrity.

---

## 3. Exploratory data analysis

Charts: `grid-analysis/charts/*.png`; narrative:
`grid-analysis/charts/eda_report.md`.

| Question | Finding |
|---|---|
| Which regions have the most substations? | Greater Accra (6), then Ashanti (5); Western, Central, Eastern, Volta (4 each). |
| Most common voltage level? | 161 kV (11 substations), closely followed by 330 kV (10) and 11 kV (9). |
| Which utility operates the most lines? | GRIDCo — 24 of 55 lines, consistent with its transmission-operator role. NEDCo 14, ECG 10. |
| Capacity distribution? | Right-skewed: median ≈ 108 MVA, mean ≈ 158 MVA, max 506 MVA — a few large transmission substations pull the mean up. |
| Oldest infrastructure? | Western region (earliest commissioning year 1967 in this seed). |
| Line status? | 53 Active, 2 Under Maintenance (≈ 96 % active). |
| Most-connected substation? | Mallam, Kumasi Central and Cape Coast tie at 5 connecting lines. |

Statistical note: with n = 44 substations and 55 lines the dataset is small;
all "distributions" are described, not inferentially tested, and comparisons
between regions are descriptive only.

---

## 4. Network analysis

Graph model: **undirected** (AC power can flow either way along a line).
Nodes = 44 substations (with region, voltage, capacity, coordinates, status
attributes). Edges = 55 lines (length, capacity, voltage, status, utility).
Code: `grid-analysis/task2_networkx_graph.py`,
`grid-analysis/n1_contingency.py + interactive_map.py`.

### 4.1 Graph construction
Building the graph from substation **IDs** (rather than names) preserves every
substation, including those with no lines. The resulting graph has **3
connected components**: one giant component of 41 substations plus two tiny
isolated groups (Savelugu; Conakry Transmission Hub). This is itself a
data-structure finding — a name-keyed graph would silently hide the isolates.

### 4.2 Centrality results
| Metric | Top substations |
|---|---|
| Degree | Mallam, Kumasi Central, Cape Coast (5 each) |
| Betweenness (length-weighted) | Cape Coast (0.526), Takoradi (0.516), Kumasi Central (0.501), Koforidua (0.498) |
| PageRank (capacity-weighted) | dominated by the 330 kV transmission and cross-border nodes |

High-betweenness substations sit on the single north–south / east–west
corridors of this sparsely meshed network, so they carry a large share of the
shortest topological paths between other substation pairs.

### 4.3 Community detection
Greedy modularity finds **10 communities** that align closely with
administrative regions and with the cross-border clusters (e.g. the Togo/Benin
interconnection nodes form one community; the Burkina Faso corridor another).
Two singleton communities correspond to the isolated substations.

### 4.4 Bridges and efficiency
The graph has **21 bridge edges** (of 55) — lines whose removal increases the
component count. Global efficiency is 0.244 and the length-weighted average
shortest path within the giant component is ≈ 819 km, both reflecting a long,
thin, lightly meshed topology.

### 4.5 N-1 contingency findings
Report: `grid-analysis/network_analysis/n1_contingency_report.md`; impact
chart: `charts/n1_contingency_impact.png`.

- **Substation removal.** Removing **Kumasi Central** is the most disruptive
  single-node loss: 3 extra fragments and 15 substations cut from the giant
  component. Cape Coast and Takoradi each cut ~20 substations into 2 fragments.
  Removing a peripheral Greater Accra substation (Mallam, Legon) causes **no**
  additional fragmentation.
- **Line removal.** **21 of 55 single-line losses split the network** — exactly
  the bridge set from §4.4. Every cross-border interconnection and every
  inter-regional backbone line is a bridge in this seed.

Interpretation: this synthetic grid is **radial-leaning**, not well meshed, so
it is *not* N-1 secure at the topological level. A real operator would respond
by building loop connections around the identified bridges. This is a
**graph-topology approximation** — it ignores load flow, thermal limits,
voltage stability and protection behaviour, which a real contingency study
models.

### 4.6 Visualisation
- Static network diagram (geographic layout, node size ∝ capacity):
  `charts/network_graph.png`.
- Interactive Folium map with substation/line layers, voltage colour-coding,
  and maintenance highlighting: `maps/grid_interactive_map.html`.
- Plotly scatter-geo map: `maps/substation_map_plotly.html`.
- Streamlit dashboard (Overview / Network / Geography / Reliability / Search):
  `grid-analysis/dashboard_app.py`.

---

## 5. GridCare-Lite architecture

### 5.1 Data model
SQLite, schema in `gridcare-lite/schema.sql`, dictionary in
`gridcare-lite/data_dictionary.md`. Tables: `users`, `substations`, `lines`
(both imported from the grid analysis), `outages`, `work_orders`,
`complaints`, `status_history` (audit trail). Foreign keys are enforced
(`PRAGMA foreign_keys = ON`); severity, status and role are constrained by
`CHECK` clauses.

### 5.2 Roles and permissions
Four roles — **administrator, engineer, technician, customer-service**. A
permission→roles matrix in `core/auth.py` is checked by `auth.require()` in
every state-changing service function, *and* backed by database constraints
(e.g. a work order can only be assigned to a user whose role is `technician`).
Role separation is not merely UI hiding: the Tkinter nav is filtered by
permission, but the service layer rejects an out-of-role call even if it is
made directly.

### 5.3 Workflow
`Outage: Open → In Progress → Resolved` and
`Work order: Pending → Scheduled → Completed` are explicit transition maps.
The demonstration sequence: engineer logs an outage against a real substation →
admin creates and assigns a work order (technician + future date) → technician
starts work (outage → In Progress) → technician completes with mandatory
resolution notes (work order → Completed, outage → Resolved automatically) →
customer-service logs and links a complaint → the reports screen recomputes
open counts and average resolution time. Every transition writes a
`status_history` row.

### 5.4 Security controls
- bcrypt password hashing; login rejects unknown or inactive users with a
  single generic message.
- Invalid input is rejected with user-facing messages, not crashes: bad
  substation reference, empty description, invalid severity, past scheduled
  date, duplicate open outage, assigning a non-technician, completing without
  notes, invalid state transition, and a technician touching another
  technician's work order are all covered by tests.
- The DB file is local; the app opens one connection with foreign keys on.

### 5.5 Integration with the analysis
`import_grid_data.py` loads `substations_clean.csv` / `lines_clean.csv` and
sets a `critical_flag` on the top-5 betweenness-centrality substations from
`network_metrics.csv`. The reports screen surfaces "open outages on critical
substations", clearly labelled as a **structural proxy on synthetic data**.

---

## 6. ClinicCare-Lite architecture

### 6.1 Data model
JSON files under `clinic-lite/data/` (`users`, `clinics`, `health_tasks`,
`task_assignments`, `task_submissions`, `messages`, `appointments`,
`announcements`, `engagement`, `notifications`). Every write goes through
`utils/storage.py`, which writes to a temp file and atomically replaces the
target with an explicit `truncate()` + `fsync` — fixing the `r+`/`seek(0)`
"Extra data" corruption bug the brief calls out. Schemas are documented in
`docs/diagrams.md` and `clinic-lite`'s module docstrings.

### 6.2 Roles and workflow
Two roles — **clinician, patient**. Clinician creates and assigns health
tasks (with an optional structural check spec) → patient uploads a
`.txt/.csv/.pdf` file → the file is renamed `patientID_taskID.ext` and stored
under `submissions/<clinic>/<patient>/` → a structural completeness check runs
→ clinician reviews with a **categorical** outcome (`Pending / Reviewed –
Normal / Needs Follow-up / Escalated`) plus free-text notes → the patient is
notified (in-app inbox + email/log) and can read the outcome. Appointments,
reminders, announcements, messaging and analytics run alongside.

### 6.3 Security controls
- 8-digit ID validation (clinician ends `0000`; patient ends in a registration
  year 2022–2028); password complexity (≥ 8 chars, upper + lower + digit +
  special); **bcrypt** hashing.
- Session cookie with a 30-minute inactivity lifetime; `login_required` and
  `role_required` decorators protect every dashboard route; 403 on cross-role
  access.
- **Privacy:** a patient can only see their own tasks, submissions, messages,
  engagement and analytics. `message.thread()` returns messages only where the
  requester is a participant; `engagement` has *no* cross-patient function
  (no `leaderboard`, no `rank_patients` — asserted by a test); clinician
  review and download require `clinic.shares_clinic(clinician, patient)`.
- **File safety:** extension allow-list, 2 MB size cap, empty-file rejection,
  and path components validated to block traversal (`../` rejected).
- Secrets (`CLINIC_SECRET_KEY`, SMTP credentials) come from environment
  variables; `.env.example` is committed, `.env` is not. With no SMTP set,
  notifications are logged rather than sent.

### 6.4 Explicit non-diagnostic scope statement
**ClinicCare-Lite is an administrative and communication system only. It does
not diagnose patients, interpret symptoms, calculate disease risk, assign
health scores, recommend treatment, or prescribe medication.** The only
automated content feature (`utils/completeness.py`) is a *structural* check
that expected columns/labels are present and that columns declared numeric
parse as numbers — for example it may report "the 'date' column is missing",
and it is explicitly prevented from commenting on the meaning of any value.
The review outcome is a categorical administrative triage status set by a
human clinician, never an automated result. The wellness-engagement tracker is
private to each patient and never ranks or compares patients. This boundary
was maintained through analysis, design, implementation, testing and
documentation.

---

## 7. Testing summary

### 7.1 Approach
Testing was continuous. Each component has an automated suite (`unittest`) run
before every merge, plus a manual test plan (`docs/test_plan.md`) executed
against the seeded demo data. Results: `docs/test_report.md`; defects and
their fixes: `docs/defect_log.md`.

### 7.2 Coverage
| Area | Automated tests |
|---|---|
| grid-analysis | script-level: re-run produces identical row counts (10/44/55), 0 orphaned FKs, graph builds (44 nodes / 55 edges / 3 components), metrics computed, N-1 runs |
| GridCare-Lite | 24 tests — password rules, bcrypt round-trip, bad login, RBAC matrix, outage/work-order state machines, duplicate rejection, past-date rejection, non-technician assignment, cross-technician block, mandatory notes, full outage-to-resolution, complaint linking, report permission + shape, audit trail |
| ClinicCare-Lite | 28 tests — ID/password validation, atomic-write/no-trailing-bytes, corrupt-file fail-safe, register/authenticate, duplicate ID, completeness check (missing column / non-numeric / OK), file handler (bad extension / oversize / traversal / naming), submit→review→notify, unassigned-submission block, cross-clinic review block, invalid outcome, messaging privacy, engagement privacy, route protection (login required, patient→clinician 403, weak-password + bad-ID registration) |

### 7.3 Key defects found and fixed
1. **JSON truncation bug** (ClinicCare-Lite) — an early `r+`/`seek(0)` save
   left trailing bytes and caused "Extra data" decode errors. Fixed with
   atomic temp-file replace + explicit `truncate()`; regression test added.
2. **ID-keyed vs name-keyed graph** (grid-analysis) — the name-keyed graph in
   the brief silently drops isolated substations. Switched to ID-keyed
   construction; the 3-component result is now reported.
3. **Work-order completion did not advance the outage** — completing a work
   order left its outage `Open`. Fixed so completion drives the linked outage
   to `Resolved` and writes the audit rows; covered by
   `test_full_outage_to_resolution`.
4. **Cross-technician update** — any technician could complete any work order.
   Added an ownership check (`assigned_technician == user_id`); covered by
   `test_technician_cannot_touch_others_wo`.

---

## 8. Discussion and challenges

**What worked.** Separating a testable core from the GUI/web layer let us build
confidently — 52 tests catch regressions in seconds (the bcrypt tests are the
slow part). The seeded generator made every result reproducible and every bug
repeatable. Writing a markdown report from each analysis script kept the
analysis auditable.

**What was hard.** (a) The synthetic network turned out to be radial-leaning,
so our first N-1 expectation ("a meshed network won't fragment") was wrong —
we kept the finding and discussed it rather than re-seeding to get a tidier
answer. (b) Keeping ClinicCare-Lite strictly non-diagnostic required active
restraint: the "obvious" feature (flagging abnormal readings) is exactly the
thing the scope forbids, so the completeness check is deliberately limited to
structure. (c) Enforcing privacy meant auditing every query for an implicit
cross-patient path; we moved all data access into `models/` so the checks live
in one place.

**Lessons learned.** Enforce rules in a service layer, not the UI. Write the
regression test at the moment the bug is found. Treat "clean" data as
untrusted anyway — the validation code is the deliverable, not the (empty)
list of problems it found this time.

---

## 9. Conclusion and recommendations

The project delivers a reproducible grid analysis and two working, tested
role-based applications that share authentication, RBAC, workflow-tracking and
testing conventions while keeping domain-specific data models and rules.

**Real-world relevance.** The N-1 analysis mirrors, in miniature, the
redundancy planning a utility like GRIDCo does before scheduling maintenance:
identify the bridges, build loops around them. GridCare-Lite mirrors the
internal ticketing a utility uses to move a fault from report to resolution.
ClinicCare-Lite mirrors the administrative half of a clinic system while
deliberately staying out of clinical decision-making.

**Future work.** grid-analysis: incorporate real load/outage time-series;
weight the contingency analysis by capacity; animate grid growth by
commissioning year. GridCare-Lite: multi-user server backend, SLA timers,
crew scheduling. ClinicCare-Lite: patient self-scheduling, WebSocket
messaging, a proper database, deployment hardening (CSRF tokens, rate
limiting, audited session store).

---

## 10. References

- NetworkX Developers. *NetworkX documentation* (v3.x). https://networkx.org/
- The pandas development team. *pandas documentation*. https://pandas.pydata.org/
- Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. *Computing in
  Science & Engineering*, 9(3), 90–95.
- Waskom, M. (2021). seaborn: statistical data visualization. *Journal of Open
  Source Software*, 6(60), 3021.
- Plotly Technologies Inc. *Plotly Python graphing library*. https://plotly.com/python/
- python-visualization. *Folium documentation*. https://python-visualization.github.io/folium/
- Pallets. *Flask documentation* (v3.x). https://flask.palletsprojects.com/
- Provos, N., & Mazières, D. (1999). A future-adaptable password scheme
  (bcrypt). *USENIX Annual Technical Conference*.
- West African Power Pool. *About WAPP*. https://www.ecowapp.org/
- Ghana Grid Company (GRIDCo). *Company overview*. https://www.gridcogh.com/
- Dataset: synthetic, generated by `grid-analysis/generate_grid_data.py`
  (`random.seed(42)`), provided with the course project brief.
