"""Automated form-completeness check for .csv / .txt submissions.

STRICTLY STRUCTURAL. It checks that expected columns/fields are present, that
required cells are non-empty, and that columns declared numeric parse as
numbers. It NEVER interprets the clinical meaning of a value.

  OK to say:  "The 'date' column is missing."
  NOT OK:     "Your blood-pressure reading is high."
"""

import csv
import io
import os


def check_csv(text, expected_columns, numeric_columns=(), required_columns=None):
    """Return {'ok': bool, 'issues': [str], 'rows': int}."""
    required_columns = set(required_columns or expected_columns)
    issues = []
    reader = csv.reader(io.StringIO(text))
    try:
        header = next(reader)
    except StopIteration:
        return {"ok": False, "issues": ["File is empty - no header row found."], "rows": 0}

    header = [h.strip() for h in header]
    for col in expected_columns:
        if col not in header:
            issues.append(f"Expected column '{col}' is missing.")

    idx = {h: i for i, h in enumerate(header)}
    rows = list(reader)
    for r, row in enumerate(rows, start=2):
        for col in required_columns:
            if col in idx:
                if idx[col] >= len(row) or not row[idx[col]].strip():
                    issues.append(f"Row {r}: required field '{col}' is empty.")
        for col in numeric_columns:
            if col in idx and idx[col] < len(row) and row[idx[col]].strip():
                try:
                    float(row[idx[col]])
                except ValueError:
                    issues.append(f"Row {r}: column '{col}' expected a number, "
                                  f"got '{row[idx[col]]}'.")
    if not rows:
        issues.append("File has a header but no data rows.")
    return {"ok": not issues, "issues": issues, "rows": len(rows)}


def check_text(text, required_labels):
    """For .txt: check that each 'Label:' line is present and has a value."""
    issues = []
    lines = {}
    for ln in text.splitlines():
        if ":" in ln:
            k, _, v = ln.partition(":")
            lines[k.strip().lower()] = v.strip()
    for label in required_labels:
        key = label.strip().lower()
        if key not in lines:
            issues.append(f"Expected line '{label}:' is missing.")
        elif not lines[key]:
            issues.append(f"Line '{label}:' has no value.")
    return {"ok": not issues, "issues": issues, "rows": len(lines)}


def check_submission(path, spec):
    """Dispatch on extension. ``spec`` carries the structural expectations that
    the clinician attached to the health task."""
    ext = os.path.splitext(path)[1].lower()
    if not spec:
        return {"ok": True, "issues": [], "rows": 0, "skipped": True}
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError:
        return {"ok": False, "issues": ["Could not read the file."], "rows": 0}
    if ext == ".csv":
        return check_csv(text,
                         spec.get("expected_columns", []),
                         spec.get("numeric_columns", []),
                         spec.get("required_columns"))
    if ext == ".txt":
        return check_text(text, spec.get("required_labels", []))
    return {"ok": True, "issues": [], "rows": 0, "skipped": True}  # e.g. .pdf
