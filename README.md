# CS 112 Final Project — Grid Analysis, GridCare-Lite & ClinicCare-Lite

Integrated data-science and software-engineering course project (CS 112,
Summer 2026). Full requirements live in [`CS 112 Computer Programming for CS
Final Course Project Summer 2026.docx`](<CS%20112%20Computer%20Programming%20for%20CS%20Final%20Course%20Project%20Summer%202026.docx>)
— that document is the authoritative spec; everything below is a summary.

Three interrelated components:

1. **National Electricity Grid Network Analysis** (`grid-analysis/`) — clean,
   integrate, and analyse a synthetic (seeded, reproducible) Ghana/West-Africa
   grid dataset using pandas and NetworkX: data cleaning, exploratory
   analysis, graph modelling, network metrics, N-1 contingency analysis, and
   visualization.
2. **GridCare-Lite** (`gridcare-lite/`) — a role-based desktop GUI
   (Tkinter/PyQt) outage-and-maintenance-management system backed by SQLite,
   simulating the internal tool a utility like ECG or GRIDCo might use.
3. **ClinicCare-Lite** (`clinic-lite/`) — a secure, role-based clinic
   administration and communication system (health tasks, patient
   submissions, clinician review, messaging, analytics), backed by JSON
   storage. Administrative and communication only — it must never diagnose,
   interpret symptoms, or recommend treatment.

All three share the same standards for authentication/RBAC, testing
discipline, and documentation described in the spec.

## Repository structure

```
Datasets/                  Seeded dataset generator + raw CSVs (utilities, substations, lines)
grid-analysis/
  task1_data_cleaning.py       Load, inspect, clean, validate the raw datasets
  task1b_data_integration.py   Join the three datasets into a merged dataset
  task2_networkx_graph.py      Build the grid graph, EDA, network metrics
  cleaned_data/                 Cleaned CSVs + cleaning/validation report
  integrated_data/              Merged dataset + integration report
  network_analysis/             Per-substation metrics + analysis report
  data_dictionary.md            Field-by-field reference for every dataset above
  er_diagram.md                 ER diagram of the utilities/substations/lines relationships
gridcare-lite/              GridCare-Lite application (SQLite schema, GUI, workflow) — in progress
clinic-lite/                ClinicCare-Lite application (JSON model, GUI/web, workflow) — in progress
reports/                    Shared/cross-cutting documentation (technical report, test logs, etc.)
issue_list.md                Real GitHub issue numbers/state, grouped by component
guide.md                    Conventions for anyone (human or AI assistant) picking up an issue
```

## Getting started

```bash
# 1. Generate the seeded datasets (byte-identical for every team member)
cd Datasets && python generate_grid_data.py

# 2. Clean, integrate, and analyse the grid data
cd ../grid-analysis
python task1_data_cleaning.py        # -> cleaned_data/
python task1b_data_integration.py    # -> integrated_data/
python task2_networkx_graph.py       # -> network_analysis/
```

Requires `pandas`, `numpy`, `networkx`, and `scipy` (for PageRank). GridCare-Lite
and ClinicCare-Lite will add their own requirements (`sqlite3` is stdlib;
GUI/web framework TBD per component) as those components are built.

## Project status

Tracked entirely through GitHub issues — see [`issue_list.md`](issue_list.md)
for the current number/state/title of every issue, grouped by component. As
of the last sync:

- **grid-analysis**: data cleaning and NetworkX graph modelling done; N-1
  contingency analysis and interactive map still open.
- **gridcare-lite**, **clinic-lite**: not started.
- **shared** (integration testing, final report, presentation, demo video):
  not started.

## Contributing

- One feature branch per issue, off an up-to-date `main`; PR against `main`
  with `Closes #<issue-number>` in the body if it resolves the issue; merge
  only after review.
- If you're using an AI coding assistant (Claude Code, Copilot, etc.) to work
  an issue, read [`guide.md`](guide.md) first — it covers branching, commit
  conventions, and the expectation that finished work is checked against the
  spec docx, not just the issue's own checklist.
