# GridCare-Lite — Database Data Dictionary

SQLite database (`gridcare.db`), schema in [`schema.sql`](schema.sql).
Foreign keys are enforced (`PRAGMA foreign_keys = ON`). All timestamps are
ISO-8601 text in local time.

## `users`
| Column | Type | Notes |
|---|---|---|
| user_id | INTEGER PK | autoincrement |
| username | TEXT | unique, not null |
| password_hash | TEXT | bcrypt hash — never plaintext |
| full_name | TEXT | display name |
| role | TEXT | `admin` \| `engineer` \| `technician` \| `customer_service` (CHECK) |
| active | INTEGER | 1 = can log in, 0 = disabled |

## `substations` (reference data, imported from grid-analysis)
| Column | Type | Notes |
|---|---|---|
| substation_id | INTEGER PK | matches `Substation ID` in `substations_clean.csv` |
| name | TEXT | full substation name |
| short_name | TEXT | place name for labels |
| region | TEXT | administrative region / bordering country |
| voltage_kv | INTEGER | 11 / 33 / 69 / 161 / 330 |
| capacity_mva | REAL | rated capacity |
| status | TEXT | `Active` \| `Inactive` (CHECK) |
| critical_flag | INTEGER | 1 if in the top-5 betweenness-centrality ranking from the network analysis (structural proxy on synthetic data) |

## `lines` (reference data, imported from grid-analysis)
| Column | Type | Notes |
|---|---|---|
| line_id | INTEGER PK | matches `Line ID` in `lines_clean.csv` |
| utility | TEXT | owning utility id/code |
| source_id | INTEGER FK → substations | one end |
| dest_id | INTEGER FK → substations | other end |
| voltage_kv | INTEGER | operating voltage |
| length_km | REAL | approx length |
| status | TEXT | `Active` \| `Under Maintenance` (CHECK) |

## `outages`
| Column | Type | Notes |
|---|---|---|
| outage_id | INTEGER PK | autoincrement |
| substation_id | INTEGER FK → substations | must be a real asset |
| reported_by | INTEGER FK → users | the engineer/admin who logged it |
| description | TEXT | required, free text |
| severity | TEXT | `Low` \| `Medium` \| `High` \| `Critical` (CHECK) |
| status | TEXT | `Open` → `In Progress` → `Resolved` (state machine) |
| reported_at | TEXT | set on insert |
| resolved_at | TEXT | set when status becomes `Resolved` |

## `work_orders`
| Column | Type | Notes |
|---|---|---|
| work_order_id | INTEGER PK | autoincrement |
| outage_id | INTEGER FK → outages | one work order per outage (enforced in service layer) |
| created_by | INTEGER FK → users | the admin who created it |
| assigned_technician | INTEGER FK → users | must have role `technician` |
| scheduled_date | TEXT | `YYYY-MM-DD`, not in the past |
| status | TEXT | `Pending` → `Scheduled` → `Completed` (state machine) |
| resolution_notes | TEXT | required to move to `Completed` |
| completed_at | TEXT | set when status becomes `Completed` |

## `complaints`
| Column | Type | Notes |
|---|---|---|
| complaint_id | INTEGER PK | autoincrement |
| logged_by | INTEGER FK → users | customer-service rep / admin |
| customer_name | TEXT | required |
| customer_contact | TEXT | optional phone/email |
| description | TEXT | required |
| outage_id | INTEGER FK → outages | nullable — set when linked to a known outage |
| status | TEXT | `Open` \| `Linked` \| `Closed` (CHECK) |
| created_at | TEXT | set on insert |

## `status_history` (audit trail)
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | autoincrement |
| entity_type | TEXT | `outage` \| `work_order` \| `complaint` |
| entity_id | INTEGER | id within that table |
| old_status | TEXT | null on creation |
| new_status | TEXT | not null |
| changed_by | INTEGER FK → users | who made the change |
| changed_at | TEXT | set on insert |

## Relationships (summary)
```
users 1───* outages          (reported_by)
users 1───* work_orders       (created_by, assigned_technician)
users 1───* complaints        (logged_by)
substations 1───* outages     (substation_id)
substations 1───* lines       (source_id, dest_id)
outages 1───1 work_orders     (outage_id)
outages 1───* complaints      (outage_id, optional)
* ───* status_history         (entity_type + entity_id, polymorphic)
```
