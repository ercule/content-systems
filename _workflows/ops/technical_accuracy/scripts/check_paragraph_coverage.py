#!/usr/bin/env python3
"""
check_paragraph_coverage.py

Mechanically verifies that a technical-accuracy-check review accounted for
every paragraph in the source draft, instead of trusting the reviewer's
self-report that "the whole piece was read."

This exists because claim extraction can silently skip paragraphs -- a
missed claim produces no Unverified flag, no changelog row, nothing. Unlike
severity judgment (which requires model reasoning and can't be made fully
deterministic), "did every paragraph get a row in the accounting table" is
a structural, countable fact. This script checks that fact with code, not
with another round of asking the model if it was thorough.

Usage:
    python check_paragraph_coverage.py <draft.md> <accounting.txt>

draft.md:       the original piece being reviewed (markdown or plain text)
accounting.txt: the paragraph accounting table produced in step 3, one
                entry per paragraph, in order, e.g.:

                1: claims C1, C2
                2: no checkable claims
                3: claims C3
                ...

Exit code 0 = coverage confirmed (paragraph counts match, no gaps).
Exit code 1 = mismatch found; prints what's missing so it can be fixed
              before the review is considered complete.

This does NOT check whether the claims/severity/scoring are correct --
that's still the reviewer's judgment call. It only checks that nothing
was silently skipped at the extraction stage.
"""

import re
import sys

def _setup_error(msg):
    print(f"SETUP ERROR: {msg}")
    print("This is a tooling problem, not a review finding. It says nothing "
          "about the draft. Fix the invocation and re-run; report the check as "
          "'not run', never as a coverage gap.")
    sys.exit(3)


def read_input(path, label, allow_empty=True):
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        _setup_error(f"could not read {label} ({path}): {e}")
    if not allow_empty and not text.strip():
        _setup_error(f"{label} ({path}) is empty")
    return text




def split_paragraphs(text: str) -> list[str]:
    """Split on blank lines and markdown headers, drop empty chunks."""
    # Treat headers as their own paragraph boundary so they get their own
    # accounting row too (a heading can itself carry a claim, e.g. a title
    # like "Why CDNs Always Beat Origin Servers").
    lines = text.splitlines()
    paragraphs = []
    current: list[str] = []

    def flush():
        if current:
            joined = "\n".join(current).strip()
            if joined:
                paragraphs.append(joined)
            current.clear()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush()
        elif stripped.startswith("#"):
            flush()
            paragraphs.append(stripped)
        else:
            current.append(line)
    flush()
    return paragraphs


def parse_accounting(text: str) -> dict[int, str]:
    """Parse lines like '1: claims C1, C2' or '3: no checkable claims'."""
    entries = {}
    pattern = re.compile(r"^\s*(\d+)\s*[:.\-]\s*(.+)$")
    for line in text.splitlines():
        m = pattern.match(line)
        if m:
            idx = int(m.group(1))
            entries[idx] = m.group(2).strip()
    return entries


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)

    draft_path, accounting_path = sys.argv[1], sys.argv[2]

    draft_text = read_input(draft_path, "draft", allow_empty=False)
    accounting_text = read_input(accounting_path, "accounting table")

    paragraphs = split_paragraphs(draft_text)
    accounting = parse_accounting(accounting_text)

    expected_count = len(paragraphs)
    accounted_indices = set(accounting.keys())
    expected_indices = set(range(1, expected_count + 1))

    missing = sorted(expected_indices - accounted_indices)
    extra = sorted(accounted_indices - expected_indices)
    empty_entries = [
        idx for idx, val in accounting.items()
        if not val or val.strip() == ""
    ]

    ok = not missing and not extra and not empty_entries

    print(f"Draft paragraphs/headers found: {expected_count}")
    print(f"Accounting rows found:           {len(accounting)}")
    print()

    if missing:
        print(f"MISSING rows for paragraph(s): {missing}")
        for idx in missing:
            preview = paragraphs[idx - 1][:80].replace("\n", " ")
            print(f"  [{idx}] {preview}...")
    if extra:
        print(f"EXTRA rows with no matching paragraph: {extra}")
    if empty_entries:
        print(f"EMPTY entries (row exists but says nothing): {empty_entries}")

    if ok:
        print("Coverage confirmed: every paragraph has an accounting entry.")
        sys.exit(0)
    else:
        print()
        print("Coverage INCOMPLETE. Account for the paragraphs listed above "
              "if you can; if any remain unaccounted for, say so in the "
              "coverage line of the report. This does not stop the run.")
        sys.exit(1)


if __name__ == "__main__":
    main()
