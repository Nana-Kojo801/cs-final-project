"""Configuration for ClinicCare-Lite.

Secrets come from environment variables (see .env.example). Nothing sensitive
is hard-coded. If python-dotenv is installed, a local .env file is loaded
automatically for development convenience.
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # dotenv is optional
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SUBMISSIONS_DIR = os.path.join(BASE_DIR, "submissions")

SECRET_KEY = os.environ.get("CLINIC_SECRET_KEY", "dev-only-insecure-key-change-me")

# File upload rules
ALLOWED_EXTENSIONS = {".txt", ".csv", ".pdf"}
MAX_UPLOAD_BYTES = int(os.environ.get("CLINIC_MAX_UPLOAD_BYTES", 2 * 1024 * 1024))  # 2 MB

# Session
SESSION_LIFETIME_MINUTES = int(os.environ.get("CLINIC_SESSION_MINUTES", 30))

# Email (optional). If CLINIC_SMTP_HOST is unset, notifications are written to
# data/notifications.log instead of being sent - the demo works with no SMTP.
SMTP_HOST = os.environ.get("CLINIC_SMTP_HOST")
SMTP_PORT = int(os.environ.get("CLINIC_SMTP_PORT", 587))
SMTP_USER = os.environ.get("CLINIC_SMTP_USER")
SMTP_PASSWORD = os.environ.get("CLINIC_SMTP_PASSWORD")
SMTP_FROM = os.environ.get("CLINIC_SMTP_FROM", "no-reply@cliniccare-lite.local")

# Registration years permitted in patient IDs
PATIENT_YEAR_MIN = 2022
PATIENT_YEAR_MAX = 2028
