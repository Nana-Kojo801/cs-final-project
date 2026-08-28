"""Notification delivery.

If SMTP is configured via environment variables, send a real email. Otherwise
(the default for the demo) append the notification to data/notifications.log
and record it in the in-app inbox. Credentials are never hard-coded.
"""

import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText

import config
from utils.storage import read_json, write_json

LOG_PATH = os.path.join(config.DATA_DIR, "notifications.log")


def _log(recipient, subject, body):
    os.makedirs(config.DATA_DIR, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat(timespec='seconds')}] TO {recipient} :: "
                f"{subject}\n{body}\n{'-' * 60}\n")


def send_notification(recipient_email, subject, body, recipient_id=None):
    """Best-effort. Returns 'sent' | 'logged' | 'failed'."""
    result = "logged"
    if config.SMTP_HOST and config.SMTP_USER and config.SMTP_PASSWORD:
        try:
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = config.SMTP_FROM
            msg["To"] = recipient_email
            with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=10) as s:
                s.starttls()
                s.login(config.SMTP_USER, config.SMTP_PASSWORD)
                s.send_message(msg)
            result = "sent"
        except Exception as e:            # network/auth failure must not crash the app
            _log(recipient_email, subject + " [SMTP FAILED: %s]" % e, body)
            result = "failed"
    if result != "sent":
        _log(recipient_email, subject, body)

    # mirror every notification into the in-app inbox
    if recipient_id is not None:
        inbox = read_json("notifications", [])
        inbox.append({
            "recipient_id": str(recipient_id),
            "subject": subject,
            "body": body,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "read": False,
            "delivery": result,
        })
        write_json("notifications", inbox)
    return result


def inbox_for(user_id):
    return [n for n in read_json("notifications", []) if n["recipient_id"] == str(user_id)]


def mark_all_read(user_id):
    def _m(items):
        for n in items:
            if n["recipient_id"] == str(user_id):
                n["read"] = True
        return items
    from utils.storage import update_json
    update_json("notifications", _m, [])
