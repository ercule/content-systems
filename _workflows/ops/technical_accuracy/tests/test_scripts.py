#!/usr/bin/env python3
"""
Smoke tests for the six coverage scripts in ../scripts/.

Each script is a hard blocker in the workflow: a false FAIL stalls a review,
a false PASS defeats the point of having the script at all. These tests check
both directions -- that a correct input exits 0, and that each distinct kind
of incomplete input exits 1.

Run from anywhere:
    python3 tests/test_scripts.py

Exit 0 = all scripts behave correctly. Exit 1 = failures listed.
"""

import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(HERE), "scripts")

RESULTS = []


def write(d, name, content):
    p = os.path.join(d, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p


def run(script, *args):
    proc = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, script), *args],
        capture_output=True, text=True,
    )
    return proc.returncode, proc.stdout + proc.stderr


def check(name, got, want):
    ok = got == want
    RESULTS.append((ok, name, f"exit {got}, expected {want}"))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}  (exit {got}, expected {want})")


DRAFT = """# How CDNs Work

A CDN caches content at the edge. It is like a warehouse near the customer.

Anycast routes by BGP path cost, per https://www.rfc-editor.org/rfc/rfc4786.

Origin still receives uncached traffic.
"""


def test_paragraph_coverage(d):
    print("\ncheck_paragraph_coverage.py")
    draft = write(d, "draft.md", DRAFT)
    # header + 3 paragraphs = 4 rows
    ok = write(d, "acct_ok.txt", "1: no checkable claims\n2: claims C1, C2\n3: claims C3\n4: claims C4\n")
    check("complete accounting", run("check_paragraph_coverage.py", draft, ok)[0], 0)

    missing = write(d, "acct_missing.txt", "1: no checkable claims\n2: claims C1\n3: claims C3\n")
    check("missing final row", run("check_paragraph_coverage.py", draft, missing)[0], 1)

    extra = write(d, "acct_extra.txt", "1: a\n2: b\n3: c\n4: d\n5: e\n")
    check("extra phantom row", run("check_paragraph_coverage.py", draft, extra)[0], 1)

    empty = write(d, "acct_empty.txt", "1: a\n2: b\n3: c\n4:  \n")
    check("row present but blank", run("check_paragraph_coverage.py", draft, empty)[0], 1)

    check("no args prints usage", run("check_paragraph_coverage.py")[0], 2)


def test_citation_coverage(d):
    print("\ncheck_citation_coverage.py")
    draft = write(d, "cite_draft.md", DRAFT)
    ok = write(d, "fetched_ok.txt", "https://www.rfc-editor.org/rfc/rfc4786\n")
    check("cited URL was fetched", run("check_citation_coverage.py", draft, ok)[0], 0)

    slash = write(d, "fetched_slash.txt", "https://www.rfc-editor.org/rfc/rfc4786/\n")
    check("trailing-slash normalization", run("check_citation_coverage.py", draft, slash)[0], 0)

    none = write(d, "fetched_none.txt", "https://example.com/unrelated\n")
    check("cited URL never fetched", run("check_citation_coverage.py", draft, none)[0], 1)

    md = write(d, "md_draft.md", "See [the spec](https://www.rfc-editor.org/rfc/rfc9213) for details.\n")
    mdf = write(d, "md_fetched.txt", "https://www.rfc-editor.org/rfc/rfc9213\n")
    check("markdown-link URL parsed without paren", run("check_citation_coverage.py", md, mdf)[0], 0)

    nourl = write(d, "nourl.md", "No links here at all.\n")
    check("draft with no citations", run("check_citation_coverage.py", nourl, none)[0], 0)


def test_rewrite_coverage(d):
    print("\ncheck_rewrite_coverage.py")
    orig = write(d, "orig.md", "Purging takes seconds to minutes depending on provider. CDNs mirror your whole site.\n")
    changelog = write(d, "changelog.txt",
                      "Outdated|Purging takes seconds to minutes depending on provider\n"
                      "Incorrect|CDNs mirror your whole site\n")

    fixed = write(d, "fixed.md", "Purging typically completes within seconds on major providers. CDNs cache on demand rather than replicating everything.\n")
    check("both flagged claims rewritten", run("check_rewrite_coverage.py", orig, fixed, changelog)[0], 0)

    partial = write(d, "partial.md", "Purging takes seconds to minutes depending on provider. CDNs cache on demand.\n")
    check("one claim left verbatim", run("check_rewrite_coverage.py", orig, partial, changelog)[0], 1)

    unver = write(d, "unver_changelog.txt", "Unverified|Purging takes seconds to minutes depending on provider\n")
    check("Unverified rows exempt from fix check",
          run("check_rewrite_coverage.py", orig, orig, unver)[0], 0)

    banner = write(d, "banner.md", "Rewrite skipped: framing issue found in step 2.\n")
    check("framing issue + skip banner present",
          run("check_rewrite_coverage.py", orig, banner, changelog, "--framing-issue")[0], 0)

    check("framing issue + full rewrite instead",
          run("check_rewrite_coverage.py", orig, fixed, changelog, "--framing-issue")[0], 1)


def test_atomic_coverage(d):
    print("\ncheck_atomic_decomposition_coverage.py")
    draft = write(d, "atomic_draft.md", DRAFT)
    code, out = run("check_atomic_decomposition_coverage.py", draft, write(d, "empty.txt", ""))
    n = int(out.split("Sentences:")[1].split()[0])
    ok = write(d, "atomic_ok.txt", "".join(f"{i}: assertions A{i}\n" for i in range(1, n + 1)))
    check("every sentence decomposed", run("check_atomic_decomposition_coverage.py", draft, ok)[0], 0)

    short = write(d, "atomic_short.txt", "".join(f"{i}: assertions A{i}\n" for i in range(1, n)))
    check("last sentence missing", run("check_atomic_decomposition_coverage.py", draft, short)[0], 1)

    noassert = write(d, "atomic_none.txt", "".join(f"{i}: no atomic assertions\n" for i in range(1, n + 1)))
    check("'no atomic assertions' accepted", run("check_atomic_decomposition_coverage.py", draft, noassert)[0], 0)

    blank = write(d, "atomic_blank.txt", "".join(f"{i}: assertions A{i}\n" for i in range(1, n)) + f"{n}:   \n")
    check("row present but blank", run("check_atomic_decomposition_coverage.py", draft, blank)[0], 1)


def test_analogy_coverage(d):
    print("\ncheck_analogy_coverage.py")
    acct = write(d, "an_acct.txt", "1: definition\n2: analogy: warehouse near the customer\n3: number claim\n")
    ok = write(d, "an_ok.txt", "2: analogy: a reader would wrongly conclude content is pre-shipped everywhere\n")
    check("analogy has its literal-reading test", run("check_analogy_coverage.py", acct, ok)[0], 0)

    none = write(d, "an_none.txt", "")
    check("analogy with no test logged", run("check_analogy_coverage.py", acct, none)[0], 1)

    empty = write(d, "an_empty.txt", "2: analogy: \n")
    check("test line present but no answer", run("check_analogy_coverage.py", acct, empty)[0], 1)

    noan = write(d, "an_noan.txt", "1: definition\n3: number claim\n")
    check("draft with no analogies at all", run("check_analogy_coverage.py", noan, none)[0], 0)

    multi = write(d, "an_multi.txt", "2: analogy: warehouse; also analogy: highway\n")
    multi_test = write(d, "an_multi_test.txt", "2: analogy: reader concludes wrong thing\n")
    check("multiple analogies on one line", run("check_analogy_coverage.py", multi, multi_test)[0], 0)


def test_setup_errors(d):
    """A bad invocation must exit 3 (tooling), never 1 (coverage gap) --
    otherwise a wrong path reads as a damning finding about the draft."""
    print("\nsetup errors exit 3, not 1")
    draft = write(d, "se_draft.md", DRAFT)
    acct = write(d, "se_acct.txt", "1: a\n2: b\n3: c\n4: d\n")
    missing = os.path.join(d, "does_not_exist.txt")

    check("paragraph: missing draft", run("check_paragraph_coverage.py", missing, acct)[0], 3)
    check("paragraph: missing accounting", run("check_paragraph_coverage.py", draft, missing)[0], 3)
    check("citation: missing fetched list", run("check_citation_coverage.py", draft, missing)[0], 3)
    check("atomic: missing draft", run("check_atomic_decomposition_coverage.py", missing, acct)[0], 3)
    check("analogy: missing accounting", run("check_analogy_coverage.py", missing, acct)[0], 3)
    check("rewrite: missing corrected draft",
          run("check_rewrite_coverage.py", draft, missing, acct)[0], 3)
    empty = write(d, "se_empty.md", "   \n")
    check("empty draft is a setup error", run("check_paragraph_coverage.py", empty, acct)[0], 3)

    code, out = run("check_paragraph_coverage.py", missing, acct)
    check("setup error labels itself as tooling", 0 if "SETUP ERROR" in out else 1, 0)
    check("setup error disclaims being a finding",
          0 if "not a review finding" in out else 1, 0)


def main():
    print(f"Testing scripts in: {SCRIPTS}")
    with tempfile.TemporaryDirectory() as d:
        test_paragraph_coverage(d)
        test_citation_coverage(d)
        test_rewrite_coverage(d)
        test_atomic_coverage(d)
        test_analogy_coverage(d)
        test_setup_errors(d)

    failed = [r for r in RESULTS if not r[0]]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed")
    if failed:
        print("\nFAILED:")
        for _, name, detail in failed:
            print(f"  {name}: {detail}")
        sys.exit(1)
    print("All scripts behave correctly in both directions.")
    sys.exit(0)


if __name__ == "__main__":
    main()
