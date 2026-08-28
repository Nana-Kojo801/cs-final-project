# Test Plan — GridCare-Lite & ClinicCare-Lite (+ grid-analysis)

**CS 112 Final Project · Cohort A, Team 3**

## 1. Objectives
Verify that each component meets its functional requirements, enforces its
security/privacy and scope rules, handles invalid input gracefully, and
produces reproducible results.

## 2. Scope
| In scope | Out of scope |
|---|---|
| Authentication, RBAC, workflow state machines | Load / performance / stress testing |
| Input validation & error handling | Penetration testing, real SMTP delivery |
| File handling & path safety (ClinicCare-Lite) | Cross-browser matrix beyond Chrome/Firefox |
| Privacy & non-diagnostic scope (ClinicCare-Lite) | Native packaging / installers |
| Data cleaning, integration, graph, N-1 reproducibility | Real power-flow validation |

## 3. Approach
- **Automated (`unittest`)** — run before every merge:
  `gridcare-lite/tests/` (24 tests), `clinic-lite/tests/` (28 tests).
- **Script reproducibility** — re-run the grid-analysis pipeline from the
  seeded generator and diff row counts / key metrics.
- **Manual** — the numbered cases in §5, executed against the seeded demo data
  by at least two team members.

## 4. Environment
Python 3.11+; dependencies from `requirements.txt`; fresh clone; seeded data
via each component's `seed_data.py --reset`. Every major workflow tested by ≥ 2
people.

## 5. Manual test cases

Each case records: objective · input · expected outcome · (actual outcome,
pass/fail, defect, corrective action, retest — filled in `test_report.md`).

### 5.1 GridCare-Lite

| ID | Objective | Input | Expected |
|---|---|---|---|
| GC-01 | Valid login routes by role | `engineer` / `Grid@2026` | Engineer dashboard; nav shows Log Outage, Outage Dashboard, Reports only |
| GC-02 | Invalid login rejected | `engineer` / `wrong` | "Invalid username or password", stays on login |
| GC-03 | Empty credentials | blank / blank | "Enter both a username and a password" |
| GC-04 | Engineer logs outage | valid substation, severity High, description | Outage #N created, appears on dashboard as Open |
| GC-05 | Outage against non-existent substation | (not selectable in UI; service call with id 999) | WorkflowError "No substation with id 999" |
| GC-06 | Empty description rejected | substation, severity, blank description | "Outage description is required" |
| GC-07 | Duplicate open outage rejected | same substation + same description twice | Second attempt: "An identical open outage already exists" |
| GC-08 | Only admin creates work order | engineer tries create_work_order | AuthError; UI has no such control for engineer |
| GC-09 | Past scheduled date rejected | date = yesterday | "Scheduled date cannot be in the past" |
| GC-10 | Assign to non-technician rejected | assign engineer as technician | "Work orders can only be assigned to a technician" |
| GC-11 | Technician sees only own assignments | login `tech1` | My Assignments lists only tech1's work orders |
| GC-12 | Technician cannot edit others' WO | tech2 completes tech1's WO (service call) | AuthError |
| GC-13 | Complete requires notes | mark complete, blank notes | "Resolution notes are required to complete a work order" |
| GC-14 | Full outage-to-resolution | engineer→admin→tech1 happy path | Work order Completed; outage auto Resolved with resolved_at; ≥ 4 status_history rows |
| GC-15 | Invalid state transition | move Open outage straight to Resolved | "Cannot move an outage from 'Open' to 'Resolved'" |
| GC-16 | Complaint linked to bad outage | outage # = 999 | "No outage with id 999 to link to" |
| GC-17 | Complaint linked to real outage | outage # = existing | Complaint saved, status "Linked", outage description shown |
| GC-18 | Report permission | technician opens Reports | Not in technician nav; service call raises AuthError |
| GC-19 | Report accuracy | after GC-14 | avg_resolution_hours non-null; "Open" count decremented |
| GC-20 | DB integrity | delete `gridcare.db`, run `app.py` | Tables recreated; login fails cleanly until `seed_data.py` run |

### 5.2 ClinicCare-Lite

| ID | Objective | Input | Expected |
|---|---|---|---|
| CC-01 | Clinician ID rule | register clinician `12345678` | "Clinician IDs must end in 0000" |
| CC-02 | Patient ID year rule | register patient `20142099` | "Patient IDs must end in a year 2022-2028" |
| CC-03 | Password complexity | `weak` | Rejected with the specific rule that failed |
| CC-04 | Password OK + bcrypt | `Clinic@2026` | Registered; `data/users.json` stores a bcrypt hash, not plaintext |
| CC-05 | Duplicate ID | register an existing ID | "That ID is already registered" |
| CC-06 | Login + role redirect | clinician / patient | Correct dashboard; dark theme for clinician |
| CC-07 | Unauthenticated dashboard | GET `/patient` logged out | 302 redirect to `/login` |
| CC-08 | Cross-role access | patient GET `/clinician` | 403 error page |
| CC-09 | Another patient's record | patient A GET `/patient/task/<B's task>` | 404 (not assigned) |
| CC-10 | Unsupported file type | upload `.exe` | "Only .txt, .csv and .pdf files are accepted" |
| CC-11 | Oversize file | upload > 2 MB | 413 page / "exceeds the upload size limit" |
| CC-12 | Empty file | upload 0-byte `.txt` | "The uploaded file is empty" |
| CC-13 | File naming & location | upload `mydata.csv` for task 1 | Stored as `submissions/<clinic>/<patient>/<patient>_1.csv` |
| CC-14 | Path traversal | task/clinic id `../../etc` (service call) | FileError "Unsafe path component" |
| CC-15 | Completeness: missing column | CSV missing `diastolic` | Flag "Expected column 'diastolic' is missing"; submission still stored |
| CC-16 | Completeness: non-numeric | `systolic` cell = `high` | Flag "column 'systolic' expected a number, got 'high'" |
| CC-17 | Completeness never interprets | any values | No message about the meaning/safety of a reading, ever |
| CC-18 | Categorical review + notify | outcome "Needs Follow-up" + notes | Submission status updated; patient inbox gets a "reviewed" notification; email logged to `notifications.log` |
| CC-19 | Invalid review outcome | outcome "A+" | "Invalid review outcome"; nothing changed |
| CC-20 | Review requires same clinic | clinician from another clinic reviews | "That patient is not registered to your clinic" |
| CC-21 | Messaging privacy | patient B opens A↔clinician thread URL | 403 / thread returns only B's own messages |
| CC-22 | Messaging emergency notice | open any conversation | Persistent "not monitored / not for emergencies" banner visible |
| CC-23 | Engagement is private | inspect `utils/engagement` API + patient pages | No leaderboard/ranking function; "My Progress" shows only the logged-in patient |
| CC-24 | Duplicate submission handling | submit again while Pending | Replaces the file; after review, further replacement blocked |
| CC-25 | Notification failure fallback | no SMTP configured | App does not crash; notification written to `data/notifications.log` and inbox |
| CC-26 | Corrupt JSON fail-safe | hand-edit `users.json` to invalid JSON | `read_json` returns `{}`, app still loads the login page |
| CC-27 | JSON truncation | write long then short payload | File contains only the short payload (no "Extra data") |
| CC-28 | Analytics isolation | clinician analytics page | Only aggregate clinic metrics; no single patient's identifiable data |
| CC-29 | Session timeout | idle > 30 min, then act | Redirected to login |
| CC-30 | Mobile layout | narrow viewport (375 px) | No horizontal scroll; tables scroll inside their container; forms usable |

### 5.3 grid-analysis

| ID | Objective | Expected |
|---|---|---|
| GA-01 | Generator reproducibility | `generate_grid_data.py` produces 10 / 44 / 55 rows, byte-identical across runs |
| GA-02 | Cleaning validation | 0 missing, 0 duplicates, 0 orphaned foreign keys reported |
| GA-03 | Integration | left join keeps 55 rows, 0 unmatched keys |
| GA-04 | Graph build | 44 nodes, 55 edges, 3 connected components |
| GA-05 | Metrics | betweenness/PageRank/community/bridge outputs written to `network_analysis/` |
| GA-06 | N-1 analysis | 21 of 55 lines identified as network-splitting; per-substation impact table produced |
| GA-07 | Artifacts | 10 EDA PNGs, `network_graph.png`, `n1_contingency_impact.png`, `grid_interactive_map.html`, `substation_map_plotly.html` all created |

## 6. Entry / exit criteria
- **Entry:** feature branch builds; component seeds without error.
- **Exit:** all automated tests pass; every manual case is Pass or has a logged
  defect with a fix and a passing retest; no open Critical/High defect.

## 7. Roles
| Activity | Owner |
|---|---|
| Test plan & coordination | Shawn Tei Kpoti |
| GridCare-Lite automated + manual | Shawn Tei Kpoti, Nana Kojo Atta-Benyah |
| ClinicCare-Lite automated + manual | Brian Edem Bedzrah, Nana Ekow Amuah |
| grid-analysis reproducibility | Nana Kojo Atta-Benyah, Brian Edem Bedzrah |
| Cross-review of all results | whole team |
