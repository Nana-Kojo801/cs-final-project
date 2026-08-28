# Diagrams

Entity-relationship, class, architecture, use-case and navigation diagrams for
all three components. Rendered with Mermaid (GitHub renders these inline; or
paste into https://mermaid.live).

---

## 1. grid-analysis — dataset ER diagram

```mermaid
erDiagram
    UTILITIES ||--o{ LINES : "owns/operates"
    SUBSTATIONS ||--o{ LINES : "is source of"
    SUBSTATIONS ||--o{ LINES : "is destination of"

    UTILITIES {
        int   Utility_ID PK
        string Name
        string Alias
        string Code
        string Type
        string Country
        string Active
    }
    SUBSTATIONS {
        int   Substation_ID PK
        string Name
        string Short_Name
        string Region
        string Country
        float Latitude
        float Longitude
        int   Voltage_kV
        float Capacity_MVA
        int   Commissioning_Year
        string Type
        string Status
    }
    LINES {
        int   Line_ID PK
        int   Utility_ID FK
        int   Source_Substation_ID FK
        int   Destination_Substation_ID FK
        int   Voltage_kV
        float Length_km
        float Capacity_MVA
        string Status
        string Line_Type
    }
```

See also `grid-analysis/er_diagram.md` and `grid-analysis/data_dictionary.md`.

### grid-analysis pipeline (data-flow)

```mermaid
flowchart LR
    G[generate_grid_data.py<br/>seed 42] --> R[(raw CSVs)]
    R --> T1[task1_data_cleaning.py] --> C[(cleaned_data/)]
    C --> T1b[task1b_data_integration.py] --> I[(integrated_data/)]
    C --> T2[task2_networkx_graph.py] --> N[(network_analysis/)]
    C --> T3[eda_charts.py] --> CH[(charts/*.png)]
    C --> T4[merge_analysis.py] --> I
    C --> T5[n1_contingency.py + interactive_map.py] --> M[(maps/*.html)]
    N --> IMP[gridcare-lite/import_grid_data.py]
    C --> IMP --> DB[(gridcare.db)]
    C & N & I & CH & M --> D[dashboard_app.py<br/>Streamlit]
```

---

## 2. GridCare-Lite

### 2.1 ER diagram

```mermaid
erDiagram
    USERS ||--o{ OUTAGES : reports
    USERS ||--o{ WORK_ORDERS : "creates / is assigned"
    USERS ||--o{ COMPLAINTS : logs
    USERS ||--o{ STATUS_HISTORY : changes
    SUBSTATIONS ||--o{ OUTAGES : "affected"
    SUBSTATIONS ||--o{ LINES : "source / destination"
    OUTAGES ||--|| WORK_ORDERS : "fixed by"
    OUTAGES ||--o{ COMPLAINTS : "linked to"

    USERS {
        int user_id PK
        string username UK
        string password_hash
        string full_name
        string role
        int active
    }
    SUBSTATIONS {
        int substation_id PK
        string name
        string region
        int voltage_kv
        real capacity_mva
        string status
        int critical_flag
    }
    OUTAGES {
        int outage_id PK
        int substation_id FK
        int reported_by FK
        string description
        string severity
        string status
        string reported_at
        string resolved_at
    }
    WORK_ORDERS {
        int work_order_id PK
        int outage_id FK
        int created_by FK
        int assigned_technician FK
        string scheduled_date
        string status
        string resolution_notes
        string completed_at
    }
    COMPLAINTS {
        int complaint_id PK
        int logged_by FK
        string customer_name
        string description
        int outage_id FK
        string status
        string created_at
    }
    STATUS_HISTORY {
        int id PK
        string entity_type
        int entity_id
        string old_status
        string new_status
        int changed_by FK
        string changed_at
    }
```

### 2.2 Class / module diagram

```mermaid
classDiagram
    class db {
        +connect(path)
        +init_db(path, schema)
        +reset_db(path)
    }
    class auth {
        +PERMISSIONS: dict
        +validate_password(pw)
        +hash_password(pw)
        +check_password(pw, hash)
        +create_user(conn, ...)
        +authenticate(conn, user, pw)
        +has_permission(role, perm)
        +require(user, perm)
    }
    class services {
        +create_outage(conn, user, sub, desc, sev)
        +set_outage_status(conn, user, id, status)
        +create_work_order(conn, user, outage, tech, date)
        +assign_technician(conn, user, wo, tech, date)
        +update_work_order_status(conn, user, wo, status, notes)
        +log_complaint(conn, user, ...)
        +link_complaint(conn, user, cid, oid)
        +operational_summary(conn, user)
    }
    class GridCareApp {
        <<Tkinter>>
        conn
        user
        show_login()
        show_main()
    }
    class MainView
    class OutageDashboard
    class NewOutageForm
    class WorkOrderView
    class TechnicianView
    class ComplaintView
    class ReportsView

    GridCareApp --> db
    GridCareApp --> auth
    MainView --> auth : filter nav by permission
    OutageDashboard --> services
    NewOutageForm --> services
    WorkOrderView --> services
    TechnicianView --> services
    ComplaintView --> services
    ReportsView --> services
    services --> auth : require(permission)
    services --> db
```

### 2.3 Use-case diagram

```mermaid
flowchart TB
    subgraph Actors
      E((Engineer))
      A((Administrator))
      T((Technician))
      C((Customer Service))
    end
    E --- UC1[Log outage]
    E --- UC2[View outage dashboard]
    A --- UC2
    A --- UC3[Create & assign work order]
    A --- UC7[View operational reports]
    T --- UC4[View my assignments]
    T --- UC5[Start work / mark complete]
    C --- UC6[Log & link complaint]
    C --- UC2
    UC5 -. resolves .-> UC1
```

### 2.4 Outage-to-resolution state machine

```mermaid
stateDiagram-v2
    [*] --> Open : engineer logs outage
    Open --> InProgress : technician starts work
    InProgress --> Resolved : work order completed (with notes)
    InProgress --> Open : reopened
    Resolved --> [*]

    state "Work order" as WO {
        [*] --> Pending : admin creates
        Pending --> Scheduled : technician + date assigned
        Scheduled --> Completed : technician completes
        Completed --> [*]
    }
```

---

## 3. ClinicCare-Lite

### 3.1 Data model (JSON collections)

```mermaid
erDiagram
    USERS ||--o{ CLINICS : "clinician runs"
    CLINICS ||--o{ USERS : "registers patients"
    CLINICS ||--o{ HEALTH_TASKS : contains
    HEALTH_TASKS ||--o{ TASK_ASSIGNMENTS : "assigned to patients"
    HEALTH_TASKS ||--o{ TASK_SUBMISSIONS : "submitted against"
    USERS ||--o{ TASK_SUBMISSIONS : submits
    USERS ||--o{ MESSAGES : "sends / receives"
    CLINICS ||--o{ APPOINTMENTS : schedules
    CLINICS ||--o{ ANNOUNCEMENTS : posts
    USERS ||--o{ ENGAGEMENT : "earns (private)"
    USERS ||--o{ NOTIFICATIONS : receives

    USERS {
        string user_id PK
        string name
        string email
        string role
        string password_hash
        string theme
        int engagement_points
    }
    CLINICS {
        string clinic_id PK
        string name
        string clinician_id FK
        list patient_ids
    }
    HEALTH_TASKS {
        string task_id PK
        string title
        string description
        string due_date
        string clinic_id FK
        string created_by FK
        object check_spec
    }
    TASK_SUBMISSIONS {
        string key PK "patientID_taskID"
        string patient_id FK
        string task_id FK
        string file_path
        string clinic_id FK
        string timestamp
        string review_status
        string notes
        string reviewer_id FK
        object completeness
        bool on_time
    }
    MESSAGES {
        int id PK
        string sender_id FK
        string recipient_id FK
        string content
        string timestamp
        bool read
        bool is_announcement
    }
    APPOINTMENTS {
        string id PK
        string clinic_id FK
        string patient_id FK
        string when
        string status
        bool reminder_sent
    }
    ENGAGEMENT {
        string patient_id PK
        list events "kind, ref, on_time, points, timestamp"
    }
```

### 3.2 Class diagram

```mermaid
classDiagram
    class User {
        user_id
        name
        email
        role
        theme
        engagement_points
        set_password(pw)
        check_password(pw)
        +register(id, name, email, pw, role)$
        +authenticate(id, pw)$
    }
    class Clinic {
        clinic_id
        name
        clinician_id
        patient_ids
        +shares_clinic(clinician, patient)$
    }
    class HealthTask {
        task_id
        title
        due_date
        check_spec
        +assign(task_id, patient_ids)$
        +tasks_for_patient(pid)$
    }
    class TaskSubmission {
        key
        review_status
        notes
        completeness
        on_time
        +record_review(pid, tid, reviewer, outcome, notes)$
    }
    class Message {
        +send(sender, recipient, content)$
        +thread(a, b)$
        +conversations_for(uid)$
    }
    class Appointment
    class Announcement

    class workflow {
        +submit_task(pid, tid, file)
        +review_submission(cid, pid, tid, outcome, notes)
        +mark_attendance(clinic, appt, status)
        +run_reminder_job()
        +post_announcement(...)
    }
    class engagement {
        +record_event(pid, kind, on_time, ref)
        +summary(pid)
    }
    class analytics {
        +clinic_operational(clinic_id)
        +patient_personal(patient_id)
    }
    class storage {
        +read_json(name)
        +write_json(name, obj) "atomic + truncate"
        +update_json(name, mutator)
    }

    workflow --> TaskSubmission
    workflow --> HealthTask
    workflow --> Clinic
    workflow --> engagement
    workflow --> Message
    User --> storage
    Clinic --> storage
    HealthTask --> storage
    TaskSubmission --> storage
    analytics --> Appointment
    analytics --> TaskSubmission
```

### 3.3 System architecture

```mermaid
flowchart TB
    B[Browser<br/>desktop / mobile] -->|HTTPS forms + 12s poll| F[Flask app.py]
    F --> AU[utils/auth.py<br/>login_required / role_required]
    F --> WF[utils/workflow.py]
    F --> AN[utils/analytics.py]
    WF --> M[models/*]
    AN --> M
    M --> ST[utils/storage.py<br/>atomic JSON]
    ST --> J[(data/*.json)]
    WF --> FH[utils/file_handler.py] --> FS[(submissions/clinic/patient/)]
    WF --> EM[utils/email_handler.py]
    EM -->|SMTP if configured| SMTP[(mail server)]
    EM -->|else| LOG[(data/notifications.log + inbox)]
```

### 3.4 Use-case diagram

```mermaid
flowchart TB
    subgraph Actors
      CL((Clinician))
      PA((Patient))
    end
    CL --- U1[Create & assign health task]
    CL --- U2[Filter & review submissions]
    CL --- U3[Record categorical outcome + notes]
    CL --- U4[Schedule appointment / mark attendance]
    CL --- U5[Post announcement]
    CL --- U6[View operational analytics]
    CL --- U7[Message a patient]
    PA --- U8[View assigned tasks]
    PA --- U9[Submit file + completeness check]
    PA --- U10[Read review outcome & notes]
    PA --- U11[View private engagement progress]
    PA --- U12[Message clinician]
    PA --- U13[Toggle theme]
    U9 -. notifies .-> U2
    U3 -. notifies .-> U10
```

### 3.5 Task-to-review state machine

```mermaid
stateDiagram-v2
    [*] --> Assigned : clinician assigns task
    Assigned --> Submitted : patient uploads file (structural check runs)
    Submitted --> Pending : stored, awaiting clinician
    Pending --> ReviewedNormal : clinician: Reviewed - Normal
    Pending --> NeedsFollowUp : clinician: Needs Follow-up
    Pending --> Escalated : clinician: Escalated
    ReviewedNormal --> [*]
    NeedsFollowUp --> [*]
    Escalated --> [*]
    note right of Pending
        Patient may replace the file
        while status is still Pending.
    end note
```

### 3.6 Navigation map

```mermaid
flowchart LR
    L[/login/] --> RG[/register/]
    L --> PD[Patient dashboard]
    L --> CD[Clinician dashboard]
    PD --> PT[Task detail + submit]
    PD --> PE[My progress / engagement]
    PD --> MSG[Messages] --> CONV[Conversation]
    PD --> INB[Inbox]
    CD --> SUB[Submissions + filters] --> REV[Review submission]
    CD --> APP[Appointments]
    CD --> ANN[Announcements]
    CD --> ANA[Analytics]
    CD --> MSG
    CD --> INB
```
