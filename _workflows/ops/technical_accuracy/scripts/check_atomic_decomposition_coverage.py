#!/usr/bin/env python3
"""Verify every sentence in <draft> has a row in <atomic_accounting>
(format: '<n>: assertions A1, A2' or '<n>: no atomic assertions').
Usage: check_atomic_decomposition_coverage.py <draft> <atomic_accounting>"""
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



_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'\(])")

def split_paragraphs(text):
    paras, cur = [], []
    def flush():
        if cur:
            j = "\n".join(cur).strip()
            if j: paras.append(j)
            cur.clear()
    for line in text.splitlines():
        s = line.strip()
        if not s: flush()
        elif s.startswith("#"): flush(); paras.append(s)
        else: cur.append(line)
    flush()
    return paras

def split_sentences(text):
    out = []
    for p in split_paragraphs(text):
        if p.startswith("#"): out.append(p); continue
        norm = " ".join(p.split())
        out.extend(x.strip() for x in _SPLIT.split(norm) if x.strip())
    return out

def parse(text):
    d, pat = {}, re.compile(r"^\s*(\d+)\s*[:.\-]\s*(.+)$")
    for line in text.splitlines():
        m = pat.match(line)
        if m: d[int(m.group(1))] = m.group(2).strip()
    return d

def main():
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(2)
    draft = read_input(sys.argv[1], "draft", allow_empty=False)
    acct = read_input(sys.argv[2], "atomic accounting table")
    sents = split_sentences(draft)
    rows = parse(acct)
    n = len(sents)
    missing = sorted(set(range(1, n + 1)) - set(rows))
    extra = sorted(set(rows) - set(range(1, n + 1)))
    empty = [i for i, v in rows.items() if not v.strip()]
    print(f"Sentences: {n}  Rows: {len(rows)}")
    if missing: print(f"MISSING: {missing}")
    if extra: print(f"EXTRA: {extra}")
    if empty: print(f"EMPTY: {empty}")
    ok = not (missing or extra or empty)
    print("Coverage confirmed." if ok else
          "Coverage INCOMPLETE — record the unaccounted sentences in the "
          "coverage line. This does not stop the run.")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
