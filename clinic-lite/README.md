# ClinicCare-Lite

ClinicCare-Lite is an administrative and communication prototype for the CS112 final project. It uses Flask and JSON storage to support health-task assignment, patient file submission, clinician administrative review, and patient notifications.

## Scope boundary

The application does not diagnose, interpret symptoms, calculate medical risk, recommend treatment, or replace clinical judgment. Automated checks verify only file type, file size, required fields or cells, and basic formatting.

## Issue #11 workflow

A clinician creates a task, an assigned patient submits an approved `.txt`, `.csv`, or `.pdf` file, and a clinician records an administrative review outcome. The patient can then view the outcome and receive a notification.

The current `X-Role` and `X-User-Id` headers are temporary testing scaffolding. Issue #10 will replace them with real authentication and bcrypt password hashing.

Runtime files such as `clinic_data.json` and `uploads/` must not contain real patient information and should not be committed.
