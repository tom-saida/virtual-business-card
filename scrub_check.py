#!/usr/bin/env python3
"""Fail loudly if anything git is tracking leaks your personal details.

    ./.venv/bin/python scrub_check.py

Reads your real card.json (which is gitignored), pulls out the values that identify
you, and greps every git-tracked file for them. Run before any push. A .gitignore
protects the working tree; this catches the case where something was force-added or
pasted into the README by mistake.
"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).parent
card = ROOT / "card.json"

if not card.exists():
    print("no card.json — nothing private to leak")
    sys.exit(0)

C = json.loads(card.read_text())

# Values worth guarding. Names are deliberately excluded: an author's name in a
# LICENSE or commit is expected, and flagging it would train you to ignore this.
secrets = []
for key in ("phone", "phone_display", "email", "linkedin", "linkedin_display"):
    v = str(C.get(key) or "").strip()
    if v:
        secrets.append((key, v))
        if key == "phone":
            # also catch the number written any other way (5551234567, 555-123-4567,
            # (555) 123 4567) by comparing digits-only
            digits = re.sub(r"\D", "", v)[-10:]
            if len(digits) == 10:
                secrets.append(("phone digits", digits))

tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                         text=True).stdout.split()
if not tracked:
    print("no git-tracked files yet")
    sys.exit(0)

hits = []
for rel in tracked:
    p = ROOT / rel
    try:
        body = p.read_text(errors="ignore")
    except (OSError, UnicodeDecodeError):
        continue
    flat = re.sub(r"\D", "", body)
    for label, value in secrets:
        if label == "phone digits":
            if value in flat:
                hits.append((rel, label, value))
        elif value.lower() in body.lower():
            hits.append((rel, label, value))

if hits:
    print("PRIVATE DATA IN TRACKED FILES — do not push:\n")
    for rel, label, value in hits:
        print(f"  {rel}: {label} -> {value}")
    sys.exit(1)

print(f"clean — {len(tracked)} tracked files, none contain your "
      f"{', '.join(sorted({l for l, _ in secrets}))}")
