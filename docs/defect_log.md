# Defect Log

**CS 112 Final Project · Cohort A, Team 3**
Each defect: objective/context · trigger input · expected vs actual · severity ·
corrective action · retest result.

---

## DEF-01 — JSON save corrupts file on shorter payload (ClinicCare-Lite)

| Field | Detail |
|---|---|
| Component | `clinic-lite/utils/storage.py` (originally in `models/*.save()`) |
| Found by | Brian Edem Bedzrah, Phase 3 |
| Trigger | Save a collection, then save a smaller collection to the same file (e.g. delete a user) |
| Expected | File contains only the new JSON |
| Actual | Early implementation used `open(path,'r+')` + `seek(0)` + `json.dump` with no `truncate()`; leftover bytes from the longer previous payload stayed on disk → next `json.load` raised `json.decoder.JSONDecodeError: Extra data`. This is the exact bug the project brief calls out. |
| Severity | **High** (silent data corruption) |
| Fix | Rewrote all persistence to go through `storage.write_json`, which writes to a temp file, `flush()` + `truncate()` + `fsync()`, then `os.replace()` (atomic). `read_json` also now fails safe to an empty collection on a decode error. |
| Retest | `TestStorageTruncate.test_atomic_write_no_trailing_bytes` and `test_corrupt_file_fails_safe` — **pass**. Manual CC-27, CC-26 — **pass**. |

---

## DEF-02 — Name-keyed graph silently drops isolated substations (grid-analysis)

| Field | Detail |
|---|---|
| Component | `grid-analysis/task2_networkx_graph.py`, `n1_contingency.py + interactive_map.py` |
| Found by | Nana Kojo Atta-Benyah, Phase 4 |
| Trigger | Build the graph with `nx.from_pandas_edgelist(lines, source='Source Substation', target='Destination Substation')` as in the brief's snippet |
| Expected | All 44 substations represented as nodes |
| Actual | Only substations that appear on at least one line become nodes (~42), so isolated substations (Savelugu, Conakry Transmission Hub) vanished and the graph looked "fully connected". Node/edge counts also disagreed with the cleaned data. |
| Severity | **Medium** (misleading analysis result) |
| Fix | Build nodes explicitly from `substations_clean.csv` by **ID**, then add edges. The graph now correctly shows 44 nodes / 55 edges / **3 connected components**; efficiency and average-path-length metrics are scoped to the giant component and the 3-component result is reported and discussed. |
| Retest | GA-04 — **pass**. Network report and data-science report updated. |

---

## DEF-03 — Completing a work order left its outage Open (GridCare-Lite)

| Field | Detail |
|---|---|
| Component | `gridcare-lite/core/services.py::update_work_order_status` |
| Found by | Shawn Tei Kpoti, Phase 5 integration |
| Trigger | Technician marks a work order `Completed` |
| Expected | The outage the work order fixes moves to `Resolved` with `resolved_at` set; audit rows written |
| Actual | Work order status changed but the linked outage stayed `Open`; the operational report still counted it as open and average resolution time never populated. |
| Severity | **High** (breaks the core outage-to-resolution workflow and the report) |
| Fix | On completion, `update_work_order_status` now drives the linked outage `Open → In Progress → Resolved`, stamps `resolved_at`, and writes the corresponding `status_history` rows. |
| Retest | `TestWorkOrders.test_full_outage_to_resolution`, `TestAudit.test_status_history_written` — **pass**. Manual GC-14, GC-19 — **pass**. |

---

## DEF-04 — Any technician could update any technician's work order (GridCare-Lite)

| Field | Detail |
|---|---|
| Component | `gridcare-lite/core/services.py::update_work_order_status`, `start_work_order` |
| Found by | Shawn Tei Kpoti, role-access testing |
| Trigger | `tech2` calls `update_work_order_status` on a work order assigned to `tech1` |
| Expected | Rejected — a technician only touches their own assignments |
| Actual | The RBAC check only verified the `update_work_order` permission (which every technician has), not ownership, so the update went through. |
| Severity | **Medium** (role-scope violation) |
| Fix | Added an ownership guard: if `user['role'] == 'technician'` and `assigned_technician != user['user_id']`, raise `AuthError`. Applied to both `update_work_order_status` and `start_work_order`. |
| Retest | `TestWorkOrders.test_technician_cannot_touch_others_wo` — **pass**. Manual GC-12 — **pass**. |

---

## DEF-05 — `assigned_count` template filter missing (ClinicCare-Lite)

| Field | Detail |
|---|---|
| Component | `clinic-lite/templates/clinician/dashboard.html` / `app.py` |
| Found by | Nana Ekow Amuah, Phase 4 |
| Trigger | Load the clinician dashboard after adding the "Assigned" column to the task table |
| Expected | Column shows the number of patients assigned to each task |
| Actual | `jinja2.exceptions.TemplateAssertionError: No filter named 'assigned_count'` — 500 error on the whole dashboard. |
| Severity | **Medium** (dashboard unusable) |
| Fix | Registered `@app.template_filter("assigned_count")` returning `len(task_model.patients_for_task(task_id))`. |
| Retest | Clinician dashboard renders; route-protection tests and CC-06 — **pass**. |

---

## Summary

| Severity | Found | Fixed | Open |
|---|---|---|---|
| High | 2 | 2 | 0 |
| Medium | 3 | 3 | 0 |
| Low | 0 | 0 | 0 |

All defects found during development were fixed and covered by a regression
test before the relevant PR was merged.
