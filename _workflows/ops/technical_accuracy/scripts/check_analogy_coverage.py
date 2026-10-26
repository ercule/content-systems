#!/usr/bin/env python3
"""Verify every analogy-tagged claim in <accounting_file> has a matching
literal-reading-test line in <analogy_test_file> ('<n>: <label>: <answer>').
Usage: check_analogy_coverage.py <accounting_file> <analogy_test_file>"""
import re, sys

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



LABEL_RE = re.compile(r"^\s*(\d+)\s*[:.\-]\s*(.+)$")
ANALOGY_RE = re.compile(r"analog", re.IGNORECASE)
TEST_RE = re.compile(r"^\s*(\d+)\s*[:.\-]\s*([^:]+):\s*(.+)$")

def find_analogies(text):
    found = []
    for line in text.splitlines():
        m = LABEL_RE.match(line)
        if not m: continue
        idx = int(m.group(1))
        for lbl in (x.strip() for x in m.group(2).split(",")):
            if lbl and ANALOGY_RE.search(lbl):
                found.append((idx, lbl))
    return found

def parse_tests(text):
    """Index -> answer. Matching is by claim index only: the label is a human
    reminder of which analogy it was, not a key, and re-typing it verbatim in
    both files is not something a reviewer reliably does."""
    d = {}
    for line in text.splitlines():
        m = TEST_RE.match(line)
        if m: d[int(m.group(1))] = m.group(3).strip()
    return d

def main():
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(2)
    acct = read_input(sys.argv[1], "claim accounting table", allow_empty=False)
    tests = read_input(sys.argv[2], "analogy test file")
    claims = find_analogies(acct)
    entries = parse_tests(tests)
    print(f"Analogy claims: {len(claims)}  Test entries: {len(entries)}\n")
    if not claims:
        print("No analogy claims found — nothing to check.")
        sys.exit(0)
    missing = [c for c in claims if c[0] not in entries]
    empty = [c for c in claims if c[0] in entries and not entries[c[0]].strip()]
    if missing: print(f"MISSING test for: {missing}")
    if empty: print(f"EMPTY test for: {empty}")
    ok = not (missing or empty)
    print("Analogy coverage confirmed." if ok else
          "Analogy coverage INCOMPLETE — record the untested analogies in the "
          "coverage line. This does not stop the run.")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
