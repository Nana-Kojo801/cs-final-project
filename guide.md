# AI Collaboration Guide — CS 112 Final Project

If you (a teammate) are using Claude Code, GitHub Copilot Chat, or another AI
coding assistant to work an issue on this project, point it at this file
first — it isn't loaded automatically.

## What this project is

Three components, defined in full in `CS 112 Computer Programming for CS
Final Course Project Summer 2026.docx` (the authoritative spec — if anything
here conflicts with it, the docx wins):

- `grid-analysis/` — National Electricity Grid Network Analysis (data
  science: pandas, NetworkX, visualization)
- `gridcare-lite/` — Outage and Maintenance Management System (SQLite +
  Tkinter/PyQt desktop app)
- `clinic-lite/` — Clinic Patient Administration and Communication System
  (JSON storage, Flask or Tkinter)

`issue_list.md` maps every GitHub issue number to a title, component, and
suggested week. Treat the issue numbers there as authoritative — they're
pulled directly from `gh issue list`, not guessed.

## Before starting any issue

1. Read the actual issue body on GitHub (`gh issue view <number> --repo
   Nana-Kojo801/cs-final-project`) for its Objective / Tasks / Acceptance
   Criteria — that's the spec for the issue, not just the title.
2. Check `issue_list.md` for the real issue number if you only know the
   title.
3. Look at what's already in the target component folder before writing
   anything new. Match existing conventions (see below) instead of
   introducing a new style.

## Branching

- One feature branch per issue, branched off an up-to-date `main`:
  `git checkout main && git pull && git checkout -b feature/<short-slug>`
- Branch name should describe the work, not just repeat the issue title
  verbatim (e.g. `feature/networkx-graph`, not `feature/issue-2`).
- Never commit directly to `main` or `develop`.
- One branch per issue — don't bundle unrelated issues into the same
  branch/PR unless the user explicitly asks for it.

## Doing the work

- **grid-analysis/** Python scripts follow the pattern established in
  `task1_data_cleaning.py`, `task1b_data_integration.py`, and
  `task2_networkx_graph.py`: a `log()`/`section()` helper that both prints
  and accumulates into a markdown report, numbered sections, outputs written
  to a dedicated subfolder (`cleaned_data/`, `integrated_data/`,
  `network_analysis/`), a `.md` report plus any `.csv` artifacts. Follow
  this pattern for new grid-analysis tasks unless there's a good reason not
  to.
- Always run the script after writing it and check the output before
  considering the task done — don't hand back code that hasn't been
  executed.
- For gridcare-lite/clinic-lite work, check whatever schema/data-dictionary
  files already exist in that folder before adding new tables/fields.
- Don't add features, error handling, or abstractions beyond what the
  issue's acceptance criteria ask for. A data-cleaning task doesn't need a
  CLI framework; a schema task doesn't need an ORM unless the team has
  already agreed to use one.
- If an issue's acceptance criteria call for a deliverable (data dictionary,
  ER diagram, test log, etc.), produce that literal artifact — don't
  consider the issue done because the code runs. `data_dictionary.md` and
  `er_diagram.md` in `grid-analysis/` are examples of this being done right.

## Before calling the work done

Once the issue's tasks are implemented and the acceptance criteria appear
met, re-read the relevant section(s) of `CS 112 Computer Programming for CS
Final Course Project Summer 2026.docx` (not just the GitHub issue body — the
docx is the authoritative source and the issue text is a paraphrase of it)
and check the actual output against it line by line: required deliverables
produced, required fields/tables/metrics present, nothing silently skipped.
If a gap turns up between what the docx asks for and what exists, say so
explicitly rather than treating "the issue's checklist passes" as equivalent
to "the spec is satisfied" — the two have already drifted apart once on this
project (issue #1 vs the docx's data-dictionary/merge/ER-diagram
requirements).

## Committing

- Only commit when explicitly asked to. Don't commit automatically at the
  end of a task.
- Stage specific files by name, not `git add -A` / `git add .`.
- Commit message: short summary line (why, not just what), body only if the
  reasoning isn't obvious from the diff. End every AI-authored commit with:

  ```
  Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
  ```
  (or the equivalent trailer for whichever assistant made the change).
- Never use `--no-verify`, `--amend` on already-pushed commits, or force
  push, unless the user explicitly asks for it.

## Pull requests

- Push the branch, then open a PR against `main`.
- If the PR fully resolves a GitHub issue, put `Closes #<number>` in the PR
  body (using the real number from `issue_list.md` / `gh issue list` —
  double-check it, titles alone are not reliable enough to guess from).
  This is what makes the issue auto-close on merge; approving the review
  does **not** close it, only merging with that keyword present does.
- This team merges after review, not automatically — don't merge your own
  PR unless the user explicitly says to. Default to: push, open PR, stop and
  report the PR link.

## Keeping issue_list.md accurate

`issue_list.md` must reflect real GitHub issue numbers, not a guessed
sequence. If issues are added, renamed, or renumbered on GitHub, refresh it
from source rather than hand-editing:

```
gh issue list --repo Nana-Kojo801/cs-final-project --state all --limit 200 --json number,title,state,labels
```

## Environment notes (Windows / Git Bash)

- `gh` and `jq` may not be on the Bash tool's PATH even when they work in an
  interactive Git Bash terminal. If a command fails with `command not
  found`, locate the exe (`where.exe <name>`) and prepend its directory to
  `PATH` for that command rather than assuming the tool isn't installed.
