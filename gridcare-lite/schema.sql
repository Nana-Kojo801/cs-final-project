-- GridCare-Lite database schema (SQLite)
-- Outage and Maintenance Management System - CS 112 Final Project

PRAGMA foreign_keys = ON;

-- Application users. Passwords are bcrypt hashes, never plaintext.
CREATE TABLE IF NOT EXISTS users (
    user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name     TEXT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('admin','engineer','technician','customer_service')),
    active        INTEGER NOT NULL DEFAULT 1
);

-- Reference asset data, imported from the grid-analysis cleaned datasets.
CREATE TABLE IF NOT EXISTS substations (
    substation_id  INTEGER PRIMARY KEY,
    name           TEXT NOT NULL,
    short_name     TEXT NOT NULL,
    region         TEXT NOT NULL,
    voltage_kv     INTEGER,
    capacity_mva   REAL,
    status         TEXT NOT NULL DEFAULT 'Active' CHECK (status IN ('Active','Inactive')),
    critical_flag  INTEGER NOT NULL DEFAULT 0   -- set from network analysis (structural proxy only)
);

CREATE TABLE IF NOT EXISTS lines (
    line_id        INTEGER PRIMARY KEY,
    utility        TEXT,
    source_id      INTEGER NOT NULL REFERENCES substations(substation_id),
    dest_id        INTEGER NOT NULL REFERENCES substations(substation_id),
    voltage_kv     INTEGER,
    length_km      REAL,
    status         TEXT CHECK (status IN ('Active','Under Maintenance'))
);

-- An outage / fault logged against a valid substation.
CREATE TABLE IF NOT EXISTS outages (
    outage_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    substation_id INTEGER NOT NULL REFERENCES substations(substation_id),
    reported_by   INTEGER NOT NULL REFERENCES users(user_id),
    description   TEXT NOT NULL,
    severity      TEXT NOT NULL CHECK (severity IN ('Low','Medium','High','Critical')),
    status        TEXT NOT NULL DEFAULT 'Open' CHECK (status IN ('Open','In Progress','Resolved')),
    reported_at   TEXT NOT NULL DEFAULT (datetime('now')),
    resolved_at   TEXT
);

-- A work order created by an admin to fix an outage.
CREATE TABLE IF NOT EXISTS work_orders (
    work_order_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    outage_id           INTEGER NOT NULL REFERENCES outages(outage_id),
    created_by          INTEGER NOT NULL REFERENCES users(user_id),
    assigned_technician INTEGER REFERENCES users(user_id),
    scheduled_date      TEXT,
    status              TEXT NOT NULL DEFAULT 'Pending'
                        CHECK (status IN ('Pending','Scheduled','Completed')),
    resolution_notes    TEXT,
    completed_at        TEXT
);

-- Customer complaints, optionally linked to a known outage.
CREATE TABLE IF NOT EXISTS complaints (
    complaint_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    logged_by        INTEGER NOT NULL REFERENCES users(user_id),
    customer_name    TEXT NOT NULL,
    customer_contact TEXT,
    description      TEXT NOT NULL,
    outage_id        INTEGER REFERENCES outages(outage_id),
    status           TEXT NOT NULL DEFAULT 'Open' CHECK (status IN ('Open','Linked','Closed')),
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Immutable audit trail of every status transition.
CREATE TABLE IF NOT EXISTS status_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('outage','work_order','complaint')),
    entity_id   INTEGER NOT NULL,
    old_status  TEXT,
    new_status  TEXT NOT NULL,
    changed_by  INTEGER NOT NULL REFERENCES users(user_id),
    changed_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_outages_status      ON outages(status);
CREATE INDEX IF NOT EXISTS idx_outages_substation  ON outages(substation_id);
CREATE INDEX IF NOT EXISTS idx_wo_outage           ON work_orders(outage_id);
CREATE INDEX IF NOT EXISTS idx_wo_tech             ON work_orders(assigned_technician);
CREATE INDEX IF NOT EXISTS idx_complaints_outage   ON complaints(outage_id);
