"""Message model - secure non-urgent patient<->clinician messaging.

Privacy rule: a patient can only ever see threads where they are a
participant. Enforced in ``thread`` / ``conversations_for``.
"""

from datetime import datetime

from utils.storage import read_json, write_json


def _all():
    return read_json("messages", [])


def send(sender_id, recipient_id, content, is_announcement=False):
    msgs = _all()
    msgs.append({
        "id": len(msgs) + 1,
        "sender_id": str(sender_id),
        "recipient_id": str(recipient_id),
        "content": content.strip(),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "read": False,
        "is_announcement": is_announcement,
    })
    write_json("messages", msgs)
    return msgs[-1]


def thread(user_a, user_b):
    a, b = str(user_a), str(user_b)
    out = [m for m in _all()
           if {m["sender_id"], m["recipient_id"]} == {a, b} and not m["is_announcement"]]
    return sorted(out, key=lambda m: m["timestamp"])


def conversations_for(user_id):
    """Distinct counterparties + last message + unread count."""
    uid = str(user_id)
    convo = {}
    for m in _all():
        if m["is_announcement"]:
            continue
        if uid not in (m["sender_id"], m["recipient_id"]):
            continue
        other = m["recipient_id"] if m["sender_id"] == uid else m["sender_id"]
        c = convo.setdefault(other, {"other_id": other, "last": None, "unread": 0})
        if c["last"] is None or m["timestamp"] > c["last"]["timestamp"]:
            c["last"] = m
        if m["recipient_id"] == uid and not m["read"]:
            c["unread"] += 1
    return sorted(convo.values(), key=lambda c: c["last"]["timestamp"], reverse=True)


def mark_read(reader_id, other_id):
    reader, other = str(reader_id), str(other_id)
    msgs = _all()
    for m in msgs:
        if m["sender_id"] == other and m["recipient_id"] == reader:
            m["read"] = True
    write_json("messages", msgs)


def unread_count(user_id):
    uid = str(user_id)
    return sum(1 for m in _all()
              if m["recipient_id"] == uid and not m["read"] and not m["is_announcement"])


def search(user_id, query):
    uid, q = str(user_id), (query or "").lower()
    return [m for m in _all()
            if uid in (m["sender_id"], m["recipient_id"]) and q in m["content"].lower()]
