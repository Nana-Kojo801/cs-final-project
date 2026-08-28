# Demonstration Video Script

**CS 112 Final Project · Cohort A, Team 3**

Record **3–5 minutes per application** (grid-analysis may be combined with the
GridCare-Lite clip). Use the seeded demo data (`seed_data.py --reset` for each
app first). Screen-record at 1080p; each member narrates the part they built.

Save the final file(s) as `CohortA_Team03_<component>_demo.mp4` in this folder.
If a file is too large to include in the ZIP, replace it with `video_link.txt`
containing an unlisted YouTube / Google Drive link (viewable by anyone with the
link).

---

## Clip 1 — National Grid Analysis (~3 min) — *Nana Kojo & Nana Ekow*

| Time | On screen | Say |
|---|---|---|
| 0:00 | Terminal in `grid-analysis/` | "One seeded generator — `random.seed(42)` — so every run is byte-identical: 10 utilities, 44 substations, 55 lines." |
| 0:20 | Run `task1_data_cleaning.py`, show `data_cleaning_report.md` | "Cleaning validates types, coordinates and foreign keys. Zero missing, zero duplicates, zero orphaned keys — the point is the validation code, not the empty defect list." |
| 0:45 | `charts/eda_lines_per_utility.png`, `eda_substations_by_region.png` | "GRIDCo operates 24 of 55 lines — the transmission backbone. Greater Accra has the most substations." |
| 1:15 | `network_analysis/network_analysis_report.md` | "As a graph: 44 nodes, 55 edges, and 3 connected components — building from IDs, not names, is what exposes the 2 isolated substations. Highest betweenness: Cape Coast." |
| 1:50 | `n1_contingency_report.md` + `charts/n1_contingency_impact.png` | "N-1: remove Kumasi Central and 15 substations drop off the main grid. 21 of 55 individual lines split the network — this grid is radial-leaning, not N-1 secure." |
| 2:20 | Open `maps/grid_interactive_map.html` in a browser; toggle layers, click a substation | "Interactive map — voltage colour-coding, maintenance lines dashed, popups per asset." |
| 2:40 | `streamlit run dashboard_app.py` — click through the 5 tabs | "The dashboard ties it together: Overview, Network, Geography, Reliability, Search." |
| 2:55 | — | "All synthetic, all reproducible, all clearly labelled as structural proxies — not power-flow results." |

---

## Clip 2 — GridCare-Lite (~4 min) — *Shawn*

Pre-step (off camera): `python seed_data.py --reset` then `python app.py`.

| Time | Action | Say |
|---|---|---|
| 0:00 | Log in as `engineer` / `Grid@2026` | "Role-based login. The engineer only sees Log Outage, Outage Dashboard and Reports." |
| 0:25 | **Log Outage** — pick a substation, severity High, description; submit | "Outages can only be logged against a real substation imported from the grid analysis." |
| 0:45 | Try to submit the same outage again | "Duplicate open outage — rejected with a message, not a crash." |
| 1:00 | Log out, log in as `admin` | "The admin reviews the outage and creates a work order." |
| 1:20 | **Work Orders** — pick the outage, assign `Yaw Owusu`, date `2026-08-29`, Save | "Assigned and scheduled." |
| 1:40 | Try assigning a past date | "'Scheduled date cannot be in the past.'" |
| 1:55 | Log in as `tech1` → **My Assignments** | "The technician sees only their own work orders." |
| 2:15 | **Start work** | "Linked outage moves to In Progress." |
| 2:30 | **Mark complete…** — type resolution notes, confirm | "Notes are mandatory. The work order completes and the outage auto-resolves." |
| 2:55 | Log in as `csr` → **Complaints** — log one, link to the outage number | "Customer service logs and links a complaint." |
| 3:15 | Log in as `admin` → **Reports** | "The dashboard recomputed: open outages down, average resolution time populated, and any outage on a network-critical substation is flagged." |
| 3:35 | As `tech1`, try opening Reports (not in nav); mention the service still rejects it | "Role separation is enforced in the service layer, not just by hiding the button." |
| 3:55 | — | "Run `python -m unittest discover -s tests` — 19 tests, all green." |

---

## Clip 3 — ClinicCare-Lite (~5 min) — *Brian & Nana Ekow*

Pre-step: `python seed_data.py --reset` then `python app.py` → open `http://127.0.0.1:5000`.
Have a valid CSV (`date,systolic,diastolic` + rows) and a `.exe` file ready.

| Time | Action | Say |
|---|---|---|
| 0:00 | Show the login page; point at the footer | "Every page states this is administrative and communication only — it never diagnoses." |
| 0:15 | Log in as clinician `10000000` / `Clinic@2026` | "Clinician dashboard, dark theme." |
| 0:35 | **Create & assign a health task** — title, due date, select 2 patients; expand the completeness section, enter `date, systolic, diastolic` and numeric `systolic, diastolic` | "The optional check is *structural only* — expected columns present, numeric columns numeric." |
| 1:05 | Log out, register a **new patient** — try ID `12345678` | "'Patient IDs must end in a year 2022–2028.' Then a weak password is rejected with the exact rule." |
| 1:30 | Log in as patient `20142024` | "Colourful theme. Assigned tasks, private engagement summary, announcements." |
| 1:50 | Open the task, upload the `.exe` | "'Only .txt, .csv and .pdf files are accepted.'" |
| 2:05 | Upload a CSV missing the `diastolic` column | "Submitted — but the completeness check flags the missing column. It never comments on the values themselves." |
| 2:25 | Upload the correct CSV | "Check passes. File stored privately as `patientID_taskID.csv`." |
| 2:45 | Log in as clinician → **Submissions** — filter by status Pending → **Review** | "Preview on the left, categorical outcome on the right." |
| 3:10 | Choose **Needs Follow-up**, add notes, **Record review & notify patient** | "Categorical triage status plus notes — never a score or a diagnosis." |
| 3:30 | Log in as patient → task shows the outcome + notes; open **Inbox** | "The patient is notified and sees the outcome." |
| 3:50 | **My Progress** | "Engagement Points, on-time streak, personal trend — private to this patient. No leaderboard anywhere." |
| 4:10 | **Messages** — open the clinician thread; point at the banner | "'Not monitored in real time — not for emergencies.'" |
| 4:25 | In the URL bar, change the conversation ID to another patient's ID | "403 — you cannot see another patient's conversation." |
| 4:40 | Log in as clinician → **Analytics** | "Operational metrics for this clinic only: no-show rate by week, completion rate, pending reviews, turnaround — no individual patient's data." |
| 4:55 | — | "23 automated tests, all green. The full non-diagnostic scope held through design, build and test." |

---

## Wrap (all clips, ~15 s)
"Cohort A, Team 3. One reproducible analysis, two working role-based
applications, 42 automated tests, and a documented boundary we deliberately
did not cross."
