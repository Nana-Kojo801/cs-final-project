# CS112 Final Project — Issue List

Pulled directly from GitHub (`gh issue list --repo Nana-Kojo801/cs-final-project
--state all --limit 200 --json number,title,state,labels`) — the `#` column below
is the real issue number. Grouped by component (their actual GitHub creation
order); suggested week is a planning guide, not a hard deadline. Refresh this
file from the command above if issues change on GitHub — don't hand-renumber it.

## grid-analysis (Week 1–3)

| # | State | Title |
|---|-------|-------|
| 1 | Closed | Clean and validate grid datasets |
| 2 | Closed | Build NetworkX graph |
| 3 | Open | Run N-1 contingency analysis |
| 4 | Open | Build interactive map |

## gridcare-lite (Week 1–4)

| # | State | Title |
|---|-------|-------|
| 5 | Open | Design SQLite schema |
| 6 | Open | Implement login and role-based access control |
| 7 | Open | Build outage-to-resolution workflow |
| 8 | Open | Build reporting dashboard |

## clinic-lite (Week 1–4)

| # | State | Title |
|---|-------|-------|
| 9 | Open | Design JSON data model |
| 10 | Open | Implement auth with bcrypt password hashing |
| 11 | Open | Build task submission workflow |
| 12 | Open | Build messaging and notifications |
| 13 | Open | Build analytics dashboard |

## shared (Week 4–5)

| # | State | Title |
|---|-------|-------|
| 14 | Open | Integration testing across all components |
| 15 | Open | Write final technical report |
| 16 | Open | Prepare presentation slides |
| 17 | Open | Record demo video |

---

**Note:** issue #1's data-cleaning work also grew a follow-up commit
(`feature/grid-data-integration`, merged into main) adding the merged dataset,
data dictionary, and ER diagram that #1's acceptance criteria required but the
original PR missed. If you're picking up a "closed" issue above, check
`grid-analysis/` for what's actually there before assuming it's fully done.
