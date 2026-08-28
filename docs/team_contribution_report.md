# Team Contribution Report

**CS 112 Final Project · Cohort A, Team 3**
Repository: https://github.com/Nana-Kojo801/cs-final-project

| Member | Student ID | GitHub |
|---|---|---|
| Nana Kojo Atta-Benyah | *[ID]* | Nana-Kojo801 |
| Brian Edem Bedzrah | *[ID]* | bedzrah |
| Shawn Tei Kpoti | *[ID]* | shawnteik |
| Nana Ekow Amuah | *[ID]* | nanaekow11 |

The team used a 2 + 2-leaning split: two members anchored the data-science and
visualisation work, two anchored the two applications, and everyone
contributed to integration, testing and documentation. Every member reviewed
at least one other member's pull requests.

---

## 1. Responsibility matrix (filled in with actual work done)

| Area | Primary owner | Supporting | Reviewer | Evidence |
|---|---|---|---|---|
| Project setup, repo, issue board, conventions | Nana Kojo Atta-Benyah | Shawn Tei Kpoti | team | `issue_list.md`, `issue_assignments.md`, branch/PR workflow |
| Dataset generation & reproducibility | Nana Kojo Atta-Benyah | Brian Edem Bedzrah | Nana Ekow Amuah | `grid-analysis/generate_grid_data.py` run notes; README reproducibility section |
| Data cleaning & validation (Task 1) | Nana Kojo Atta-Benyah | Brian Edem Bedzrah | Shawn Tei Kpoti | `task1_data_cleaning.py`, `cleaned_data/data_cleaning_report.md` |
| Data integration (Task 1b / Task 4) | Nana Kojo Atta-Benyah | Nana Ekow Amuah | Brian Edem Bedzrah | `task1b_data_integration.py`, `merge_analysis.py`, `integrated_data/` |
| EDA & charts (Task 3) | Brian Edem Bedzrah | Nana Ekow Amuah | Nana Kojo Atta-Benyah | `eda_charts.py`, `charts/eda_*.png`, `charts/eda_report.md` |
| NetworkX graph & metrics (Task 2) | Nana Kojo Atta-Benyah | Brian Edem Bedzrah | Shawn Tei Kpoti | `task2_networkx_graph.py`, `network_analysis/network_analysis_report.md` |
| N-1 contingency analysis (Task 5) | Brian Edem Bedzrah | Nana Kojo Atta-Benyah | Nana Ekow Amuah | `n1_contingency.py + interactive_map.py`, `network_analysis/n1_contingency_report.md` |
| Interactive map & Streamlit dashboard | Nana Ekow Amuah | Brian Edem Bedzrah | Nana Kojo Atta-Benyah | `maps/grid_interactive_map.html`, `maps/substation_map_plotly.html`, `dashboard_app.py` |
| GridCare-Lite schema & data dictionary | Shawn Tei Kpoti | Nana Kojo Atta-Benyah | Brian Edem Bedzrah | `gridcare-lite/schema.sql`, `data_dictionary.md` |
| GridCare-Lite auth & RBAC | Shawn Tei Kpoti | Nana Kojo Atta-Benyah | Brian Edem Bedzrah | `gridcare-lite/core/auth.py` |
| GridCare-Lite outage-to-resolution workflow | Shawn Tei Kpoti | Nana Kojo Atta-Benyah | Nana Ekow Amuah | `gridcare-lite/core/services.py`, `app.py` |
| GridCare-Lite reporting screen | Shawn Tei Kpoti | Nana Ekow Amuah | Nana Kojo Atta-Benyah | `services.operational_summary`, `ReportsView` |
| GridCare-Lite ↔ grid-analysis integration | Nana Kojo Atta-Benyah | Shawn Tei Kpoti | Brian Edem Bedzrah | `gridcare-lite/import_grid_data.py` |
| ClinicCare-Lite JSON data model | Nana Kojo Atta-Benyah | Brian Edem Bedzrah | Nana Ekow Amuah | `clinic-lite/models/*`, `utils/storage.py` |
| ClinicCare-Lite auth, sessions, RBAC, security | Brian Edem Bedzrah | Shawn Tei Kpoti | Nana Kojo Atta-Benyah | `utils/auth.py`, `utils/validator.py`, `models/user.py` |
| ClinicCare-Lite submission & file handling & completeness | Brian Edem Bedzrah | Nana Kojo Atta-Benyah | Shawn Tei Kpoti | `utils/file_handler.py`, `utils/completeness.py`, `utils/workflow.py` |
| ClinicCare-Lite engagement tracker (private) | Brian Edem Bedzrah | Nana Ekow Amuah | Nana Kojo Atta-Benyah | `utils/engagement.py` |
| ClinicCare-Lite clinician dashboard, review, appointments, announcements | Nana Ekow Amuah | Brian Edem Bedzrah | Shawn Tei Kpoti | `app.py` clinician routes, `templates/clinician/*`, `models/announcement.py`, `models/appointment.py` |
| ClinicCare-Lite messaging & notifications | Nana Ekow Amuah | Brian Edem Bedzrah | Shawn Tei Kpoti | `models/message.py`, `utils/email_handler.py`, `templates/shared/*` |
| ClinicCare-Lite analytics dashboard | Nana Ekow Amuah | Shawn Tei Kpoti | Brian Edem Bedzrah | `utils/analytics.py`, `templates/clinician/analytics.html` |
| Frontend / responsive CSS | Nana Ekow Amuah | Brian Edem Bedzrah | Nana Kojo Atta-Benyah | `clinic-lite/static/styles.css`, `scripts.js` |
| Test plan & test coordination | Shawn Tei Kpoti | whole team | Nana Kojo Atta-Benyah | `docs/test_plan.md` |
| GridCare-Lite tests | Shawn Tei Kpoti | Nana Kojo Atta-Benyah | Brian Edem Bedzrah | `gridcare-lite/tests/tests/` (24, split by issue) |
| ClinicCare-Lite tests | Brian Edem Bedzrah | Nana Ekow Amuah | Shawn Tei Kpoti | `clinic-lite/tests/tests/` (28, split by issue) |
| Integration testing across components | Shawn Tei Kpoti | whole team | Nana Kojo Atta-Benyah | `docs/test_report.md`, DEF-03 |
| Technical report | Nana Kojo Atta-Benyah | whole team | whole team | `docs/technical_report.md` |
| Data-science report | Brian Edem Bedzrah | Nana Kojo Atta-Benyah | Nana Ekow Amuah | `docs/data_science_report.md` |
| Diagrams | Nana Ekow Amuah | Shawn Tei Kpoti | Brian Edem Bedzrah | `docs/diagrams.md`, `grid-analysis/er_diagram.md` |
| User guides | Shawn Tei Kpoti (GridCare), Nana Ekow Amuah (ClinicCare) | Brian Edem Bedzrah | Nana Kojo Atta-Benyah | `docs/user_guides.md` |
| Defect log | whole team | Shawn Tei Kpoti coordinates | Nana Kojo Atta-Benyah | `docs/defect_log.md` |
| Presentation slides | Nana Ekow Amuah | whole team | whole team | `slides/presentation.md` |
| Demonstration video | Brian Edem Bedzrah | whole team | whole team | `video/demo_script.md` (recording done separately) |

---

## 2. Individual contribution summaries

### Nana Kojo Atta-Benyah — Data engineering & analysis lead
Set up the repository, branch conventions and issue board. Owned the seeded
dataset workflow, data cleaning/validation, dataset integration, and the
NetworkX graph construction and metrics. Built the grid-analysis →
GridCare-Lite import bridge. Wrote the data model for ClinicCare-Lite's JSON
layer. Lead author of the technical report. Found and fixed DEF-02.

### Brian Edem Bedzrah — Analysis + ClinicCare-Lite security/submission lead
Owned the EDA + chart pipeline and the N-1 contingency analysis (the headline
data-science finding: 21/55 lines are single points of failure). On
ClinicCare-Lite, implemented authentication, sessions, RBAC, input validation,
secure file handling, the structural completeness check, and the private
engagement tracker. Wrote the 23-test ClinicCare-Lite suite. Found and fixed
DEF-01. Lead author of the data-science report; owns the demo recording.

### Shawn Tei Kpoti — GridCare-Lite lead & test coordinator
Designed the SQLite schema and data dictionary. Implemented authentication,
the permission matrix, the full outage-to-resolution workflow with
state-machine validation and audit trail, and the reporting screen. Wrote the
19-test GridCare-Lite suite. Coordinated the test plan and cross-component
integration testing. Found and fixed DEF-03 and DEF-04.

### Nana Ekow Amuah — Visualisation & ClinicCare-Lite clinician/comms lead
Built the interactive Folium map, the Plotly map, and the Streamlit dashboard.
On ClinicCare-Lite, implemented the clinician dashboard, submission review,
appointments, announcements, the messaging system, notifications, the
operational analytics, and the entire responsive frontend (self-contained CSS,
two themes, mobile layout). Authored the diagrams and the slide deck. Found
and fixed DEF-05.

---

## 3. Collaboration evidence
- One feature branch per issue; PRs reviewed by the assigned reviewer before
  merge to `main`; `Closes #<n>` used to auto-close issues.
- Weekly demos of working software (not "almost done").
- Conventions agreed up front (branching, commit style, PR + review); every
  finished issue checked against the brief, not just the issue checklist.
- Every defect in `docs/defect_log.md` links a finder, a fix commit, and a
  regression test.
