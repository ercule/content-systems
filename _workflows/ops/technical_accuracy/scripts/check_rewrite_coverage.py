#!/usr/bin/env python3
"""
check_rewrite_coverage.py

Mechanically checks the OUTPUT of a review, not the input. The other two
scripts in this folder confirm the review stage was done properly (every
paragraph accounted for, every citation fetched). This one checks the part
that happens after that: did the rewrite actually address what the
changelog flagged, and did it correctly skip the rewrite entirely when a
framing issue was found?

This can't fully verify a fix is *correct* -- that still requires judgment,
same as severity itself. What it CAN verify mechanically: whether the
flagged claim text still appears essentially unchanged in the "corrected"
draft (a sign the fix was never actually made, regardless of what the
changelog's Fix column claims), and whether a framing-flagged piece
produced a full rewrite when it should have produced the skip banner
instead.

Usage:
    python check_rewrite_coverage.py <original.md> <corrected.md> \
        <changelog.txt> [--framing-issue]

original.md:   the draft as originally submitted
corrected.md:  the rewritten draft output A produced (or the skip-banner
               note, if a framing issue was found)
changelog.txt: one line per flagged claim, in the format:
                   <severity>|<claim text>
               e.g.:
                   Incorrect|IETF RFC 7336 defines a structure for cross-CDN log exchange
                   Outdated|Purging takes seconds to minutes depending on provider
                   Unverified|Providers together account for 80 percent of global CDN traffic
               (severity is case-insensitive; Unverified rows are skipped --
               those are allowed to still appear in some form, softened or
               flagged, so exact-match absence isn't a meaningful check for them)

--framing-issue: pass this flag if step 2 found a framing issue for this
                 piece. When set, the script checks that corrected.md is
                 the skip-banner note rather than a full rewrite, instead
                 of checking claim-by-claim fixes.

Exit code 0 = coverage confirmed.
Exit code 1 = a claim that should have been fixed still appears essentially
              unchanged in the corrected draft, or a framing-flagged piece
              produced a full rewrite instead of the skip banner.

This checks a rough proxy (near-exact text persistence), not fix quality.
A claim can pass this check by being changed at all, correctly or not --
whether the *replacement* is accurate is still a judgment call for a human
or a separate review pass, same as everything upstream of this script.
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



SEVERITIES_REQUIRING_FIX = {"severe", "incorrect", "outdated", "imprecise", "vague"}
SKIP_BANNER_MARKER = "Rewrite skipped"


def normalize(text: str) -> str:
    """Lowercase, collapse whitespace, strip punctuation noise for fuzzy comparison."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_changelog(text: str) -> list[tuple[str, str]]:
    entries = []
    for line in text.splitlines():
        line = line.strip()
        if not line or "|" not in line:
            continue
        severity, claim = line.split("|", 1)
        entries.append((severity.strip().lower(), claim.strip()))
    return entries


def claim_still_present(claim: str, corrected_text: str) -> bool:
    """Rough check: does a long near-verbatim run of the claim still appear?"""
    norm_claim = normalize(claim)
    norm_corrected = normalize(corrected_text)
    # Require most of the claim to appear as a contiguous run -- a short
    # coincidental overlap shouldn't count as "unfixed." Use the claim
    # itself if short, or a substantial slice of it if long.
    probe = norm_claim if len(norm_claim) <= 60 else norm_claim[:60]
    return probe in norm_corrected


def main():
    args = sys.argv[1:]
    framing_issue = "--framing-issue" in args
    args = [a for a in args if a != "--framing-issue"]

    if len(args) != 3:
        print(__doc__)
        sys.exit(2)

    original_path, corrected_path, changelog_path = args

    corrected_text = read_input(corrected_path, "corrected draft", allow_empty=False)

    if framing_issue:
        if SKIP_BANNER_MARKER in corrected_text:
            print("Framing issue was flagged, and corrected.md correctly "
                  "contains the skip banner instead of a full rewrite.")
            sys.exit(0)
        else:
            print("MISMATCH: a framing issue was flagged for this piece, "
                  f"but corrected.md does not contain the expected "
                  f"'{SKIP_BANNER_MARKER}' marker -- it looks like a full "
                  "rewrite was produced anyway. Per the skill, the rewrite "
                  "should be skipped entirely when framing fails, not "
                  "partially or fully rewritten.")
            sys.exit(1)

    changelog_text = read_input(changelog_path, "changelog")

    entries = parse_changelog(changelog_text)
    to_check = [
        (sev, claim) for sev, claim in entries
        if sev in SEVERITIES_REQUIRING_FIX
    ]

    print(f"Changelog entries requiring a fix: {len(to_check)}")
    print()

    unfixed = []
    for sev, claim in to_check:
        if claim_still_present(claim, corrected_text):
            unfixed.append((sev, claim))

    if unfixed:
        print(f"POSSIBLY UNFIXED -- {len(unfixed)} claim(s) still appear "
              f"essentially unchanged in the corrected draft:")
        for sev, claim in unfixed:
            print(f"  [{sev}] {claim[:80]}...")
        print()
        print("This is a rough textual check, not a correctness check -- "
              "confirm by reading these spots directly. If the claim "
              "genuinely wasn't touched, the rewrite is incomplete.")
        sys.exit(1)
    else:
        print("Coverage confirmed: no flagged claim requiring a fix still "
              "appears essentially unchanged in the corrected draft.")
        sys.exit(0)


if __name__ == "__main__":
    main()
