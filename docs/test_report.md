# Test Report

**CS 112 Final Project · Cohort A, Team 3**
Executed against a fresh clone, dependencies from `requirements.txt`, seeded
demo data. Test plan: `docs/test_plan.md`. Defects: `docs/defect_log.md`.

## 1. Automated test summary

| Suite | Command | Tests | Result | Runtime |
|---|---|---|---|---|
| GridCare-Lite | `python -m unittest discover -s tests` (in `gridcare-lite/`) | 24 | **24 passed, 0 failed** | ~75 s (bcrypt work factor dominates) |
| ClinicCare-Lite | `python -m unittest discover -s tests` (in `clinic-lite/`) | 28 | **28 passed, 0 failed** | ~12 s |
| **Total** | | **52** | **52 passed** | |

GridCare-Lite tests are split one file per issue (#6 auth/RBAC, #7 workflow, #8 reports, #14 integration). Coverage: password rules, bcrypt round-trip, bad
login, RBAC matrix, outage state machine, work-order state machine, duplicate
outage rejection, past-date rejection, non-technician assignment rejection,
cross-technician block, mandatory resolution notes, full outage-to-resolution,
complaint linking (+ bad-outage rejection), report permission + shape, audit
trail row count.

ClinicCare-Lite tests are split one file per issue (#9 models, #10 auth routes, #11 submission, #12 messaging, #13 analytics). Coverage: ID validation (clinician/patient/length),
password complexity (each rule), atomic write leaves no trailing bytes,
corrupt-JSON fail-safe, register/authenticate, duplicate-ID rejection,
completeness check (missing column / non-numeric / OK), file handler (bad
extension / oversize / path traversal / naming+location), submit→review→notify,
unassigned-submission block, cross-clinic review block, invalid outcome
rejection, messaging privacy, engagement privacy (no ranking API), route
protection (login required, patient→clinician 403, weak-password registration,
bad-ID registration).

## 2. grid-analysis reproducibility

| ID | Objective | Actual | Status |
|---|---|---|---|
| GA-01 | Generator reproducibility | `utilities.csv` 10, `substations.csv` 44, `lines.csv` 55; re-run byte-identical | Pass |
| GA-02 | Cleaning validation | 0 missing, 0 full-row duplicates, 0 orphaned FKs, all coords in bounds | Pass |
| GA-03 | Integration | left join 55 → 55 rows, 0 unmatched keys, 28-column master table | Pass |
| GA-04 | Graph build | 44 nodes, 55 edges, **3 connected components** (41-node giant + 2 isolates) | Pass (see DEF-02) |
| GA-05 | Metrics | betweenness top = Cape Coast 0.526; 10 communities; 21 bridges; efficiency 0.244 | Pass |
| GA-06 | N-1 analysis | 21/55 lines split the network; worst node = Kumasi Central (3 extra fragments, 15 nodes cut) | Pass |
| GA-07 | Artifacts | 10 EDA PNGs + `network_graph.png` + `n1_contingency_impact.png` + `grid_interactive_map.html` + `substation_map_plotly.html` all generated | Pass |

## 3. Manual test results — GridCare-Lite

| ID | Actual outcome | Status |
|---|---|---|
| GC-01 | Engineer nav shows Log Outage / Outage Dashboard / Reports only; routes to engineer view | Pass |
| GC-02 | "Invalid username or password"; remains on login | Pass |
| GC-03 | "Enter both a username and a password" | Pass |
| GC-04 | Outage created, shows as Open on dashboard | Pass |
| GC-05 | `WorkflowError: No substation with id 999.` | Pass |
| GC-06 | `WorkflowError: Outage description is required.` | Pass |
| GC-07 | `WorkflowError: An identical open outage already exists for this substation.` | Pass |
| GC-08 | `AuthError: Role 'engineer' is not permitted to: create_work_order` | Pass |
| GC-09 | `WorkflowError: Scheduled date cannot be in the past.` | Pass |
| GC-10 | `WorkflowError: Work orders can only be assigned to a technician.` | Pass |
| GC-11 | My Assignments lists only tech1's work orders | Pass |
| GC-12 | `AuthError: Technicians can only update work orders assigned to them.` | Pass |
| GC-13 | `WorkflowError: Resolution notes are required to complete a work order.` | Pass |
| GC-14 | Work order Completed; outage auto-Resolved with `resolved_at` set; 5 status_history rows | Pass |
| GC-15 | `WorkflowError: Cannot move an outage from 'Open' to 'Resolved'.` | Pass |
| GC-16 | `WorkflowError: No outage with id 999 to link to.` | Pass |
| GC-17 | Complaint saved, status "Linked", outage description shown in table | Pass |
| GC-18 | `AuthError: Role 'technician' is not permitted to: view_reports` | Pass |
| GC-19 | `operational_summary` returns `avg_resolution_hours` non-null; Open count decremented | Pass |
| GC-20 | Deleting `gridcare.db` and running `app.py` recreates all tables; login fails cleanly until re-seed | Pass |

## 4. Manual test results — ClinicCare-Lite

| ID | Actual outcome | Status |
|---|---|---|
| CC-01 | "Clinician IDs must end in 0000." | Pass |
| CC-02 | "Patient IDs must end in a year 2022-2028." | Pass |
| CC-03 | Rejected: "Password needs a special character." (etc. per input) | Pass |
| CC-04 | `data/users.json` stores a `$2b$` bcrypt hash; no plaintext | Pass |
| CC-05 | "That ID is already registered." | Pass |
| CC-06 | Clinician → dark dashboard; patient → colourful dashboard | Pass |
| CC-07 | GET `/patient` while logged out → 302 to `/login` | Pass |
| CC-08 | Patient GET `/clinician` → 403 error page | Pass |
| CC-09 | Patient GET a task not assigned to them → 404 | Pass |
| CC-10 | "Only .txt, .csv and .pdf files are accepted." | Pass |
| CC-11 | `MAX_CONTENT_LENGTH` triggers 413 page; service-level check also rejects | Pass |
| CC-12 | "The uploaded file is empty." | Pass |
| CC-13 | Stored as `submissions/c1/20142024/20142024_1.csv` | Pass |
| CC-14 | `FileError: Unsafe path component: '../../etc'` | Pass |
| CC-15 | Flagged "Expected column 'diastolic' is missing."; submission still saved as Pending | Pass |
| CC-16 | Flagged "Row 2: column 'systolic' expected a number, got 'high'." | Pass |
| CC-17 | No message ever references the meaning/normality of a value — check output is structural only | Pass |
| CC-18 | Review recorded; `notifications.json` gains a "…has been reviewed" entry for the patient; line appended to `notifications.log` | Pass |
| CC-19 | "Invalid review outcome"; submission unchanged | Pass |
| CC-20 | "That patient is not registered to your clinic." | Pass |
| CC-21 | Patient B GET the A↔clinician conversation URL → 403 | Pass |
| CC-22 | "not monitored in real time … unsuitable for emergencies" banner present on messages + conversation pages | Pass |
| CC-23 | `utils/engagement` exposes no `leaderboard` / `rank_patients`; "My Progress" queries only `session['user_id']` | Pass |
| CC-24 | Re-upload while Pending replaces the file; attempt after review → "already been reviewed and cannot be replaced" | Pass |
| CC-25 | With no SMTP env vars, `send_notification` returns `logged`; app does not raise | Pass |
| CC-26 | Hand-corrupted `users.json` → `read_json` returns `{}`; `/login` still renders | Pass |
| CC-27 | Long-then-short `write_json` leaves only the short payload; `read_json` succeeds (no "Extra data") | Pass |
| CC-28 | Analytics page shows only aggregate counts/rates for the clinic | Pass |
| CC-29 | After 30 min idle, next request redirects to `/login` | Pass |
| CC-30 | At 375 px width: body has no horizontal scroll; `.table-wrap` scrolls internally; forms stack | Pass |

## 5. Outstanding issues
No open Critical or High defects. Known limitations (by design, documented in
`README.md` and the technical report): single-user desktop DB for GridCare-Lite;
flat-file JSON with a process lock and 12 s polling for ClinicCare-Lite;
best-effort email; synthetic dataset. See `docs/defect_log.md` for the four
defects found and fixed during development.

## 6. Sign-off
Every manual case executed by at least two team members against the seeded
demo data. Automated suites are green on `main`.
