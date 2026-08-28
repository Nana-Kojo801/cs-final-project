# User Guides

Short role-by-role walkthroughs for both applications. Setup is in the
top-level `README.md`. All accounts below are fictional demo accounts.

---

# GridCare-Lite

Start:
```bash
cd gridcare-lite
python seed_data.py --reset      # first run only
python app.py
```
Log in with a demo username and password `Grid@2026`.

The left-hand navigation only shows the screens your role is allowed to use.

## Administrator (`admin`)
1. **Log in** as `admin`.
2. **Outage Dashboard** — see every outage; filter by status.
3. **Work Orders** — in the "Create / assign work order" box: pick an open
   outage, choose a technician, enter a scheduled date (`YYYY-MM-DD`, not in
   the past), click **Save**. The work order becomes *Scheduled*.
   - Leaving technician/date blank creates a *Pending* work order to assign
     later.
4. **Reports** — total outages, open work orders, open complaints, average
   resolution time (hours), and open outages on network-critical substations
   (a structural proxy from the grid analysis). Breakdown tables by status,
   region and severity.
5. The admin can also do anything an engineer or technician can.

## Engineer (`engineer`)
1. **Log in** as `engineer`.
2. **Log Outage** — choose a substation from the list (only real substations
   from the imported dataset appear), pick a severity, type a description,
   click **Submit Outage**. Blank descriptions and duplicate open outages for
   the same substation are rejected with a message.
3. **Outage Dashboard** — track the outages you and others have logged.
4. **Reports** — same operational report as the admin.

## Technician (`tech1`, `tech2`)
1. **Log in** as `tech1`.
2. **My Assignments** — only work orders assigned to *you*.
3. Select a row and click **Start work** — the linked outage moves to
   *In Progress*.
4. Select the row and click **Mark complete…** — enter the resolution notes
   (required) and confirm. The work order becomes *Completed* and its outage is
   automatically *Resolved*.
5. You cannot open or modify another technician's work orders.

## Customer-service representative (`csr`)
1. **Log in** as `csr`.
2. **Complaints** — fill in customer name, optional contact, description, and
   optionally an existing outage number to link it to. Click **Save**.
3. Linked complaints show the outage description in the table.
4. **Outage Dashboard** — read-only view to check whether a customer's problem
   matches a known outage before logging.

---

# ClinicCare-Lite

Start:
```bash
cd clinic-lite
python seed_data.py --reset      # first run only
python app.py                    # http://127.0.0.1:5000
```

| Role | Demo ID | Password |
|---|---|---|
| Clinician | `10000000` | `Clinic@2026` |
| Patient | `20142024` / `20232023` / `20452022` | `Clinic@2026` |

Every page carries the footer reminder that the system is administrative and
non-diagnostic. The messaging screens carry a persistent "not monitored in
real time — not for emergencies" notice.

## Clinician
1. **Log in** with ID `10000000`. The interface uses a dark theme.
2. **Dashboard**
   - *Create & assign a health task*: title, instructions, due date, and
     select one or more patients. Optionally expand "structural completeness
     check" to declare expected CSV columns / numeric columns / expected TXT
     labels — the app will check submissions against this **structure only**.
   - *Submissions awaiting review*: click **Review** on any row.
   - *Run 24h reminder job*: sends reminder notifications for appointments and
     due-soon tasks.
3. **Submissions** — filter by task, patient, or review status. Each row shows
   whether the submission was on time and whether the structural check passed.
   **Review** opens the file; **Download** saves it.
4. **Review a submission**
   - Left: a preview (CSV as a table, TXT as text, PDF as a download link) and
     any structural-check issues.
   - Right: choose a **categorical outcome** — *Pending / Reviewed – Normal /
     Needs Follow-up / Escalated* — add free-text notes, click **Record review
     & notify patient**. The patient gets an inbox notification (and email if
     SMTP is configured).
   - Outcomes are administrative triage statuses, never scores or diagnoses.
5. **Appointments** — schedule an appointment for a patient; update its status
   to *Attended / No-show / Cancelled*. Marking *Attended* on time credits the
   patient's private engagement record.
6. **Announcements** — post a clinic-wide notice with optional publish/expiry
   dates; tick *Urgent* to also email every registered patient.
7. **Analytics** — operational metrics for your clinic only: appointment
   no-show rate (overall and by week), task-completion rate, pending reviews,
   average review turnaround, overdue submissions, submissions by task,
   monthly appointment volume, review-outcome mix. No individual patient's
   data is exposed here.
8. **Messages / Inbox** — start or continue a conversation with one of your
   registered patients; the Inbox lists submission/review/reminder/announcement
   notifications.

## Patient
1. **Register** (if needed): choose *Patient*, enter an 8-digit ID **ending in
   a registration year 2022–2028**, your name, email, and a password with an
   uppercase letter, a lowercase letter, a digit and a special character.
   Or **log in** with a demo ID.
2. **Dashboard**
   - Private engagement summary (points, on-time streak) — visible only to you.
   - Clinic announcements.
   - Your health tasks with status: *Pending / Submitted / Reviewed / Overdue*.
   - Upcoming appointments.
3. **Open a task** → **Submit**
   - Upload a `.txt`, `.csv` or `.pdf` file (max 2 MB). Other types, empty
     files and oversize files are rejected with a message.
   - If the clinician attached a structural check, any missing columns/labels
     or non-numeric values in a column expected to be numeric are listed —
     this is a completeness check, not an interpretation of your readings.
   - The file is renamed `yourID_taskID.ext` and stored privately.
   - You may replace the file while the status is still *Pending*.
4. **Read your review** — once a clinician reviews it, the task shows the
   outcome and the clinician's notes, and you get an inbox notification.
5. **My Progress** — your Engagement Points, on-time streak, on-time
   completions by month, your attendance rate, and your submission trend.
   **This page is private to you and never compares you with other patients.**
6. **Messages** — message your assigned clinician about logistics and
   follow-up only. Not for emergencies.
7. **Theme** — toggle between the colourful and dark themes from the top bar.
