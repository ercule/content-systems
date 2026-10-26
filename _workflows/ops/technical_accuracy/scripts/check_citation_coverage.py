#!/usr/bin/env python3
"""
check_citation_coverage.py

Mechanically verifies that every URL cited/linked in the draft was actually
fetched during the review, instead of trusting the reviewer's self-report.

This exists because "fetch every cited source" (step 4) is an instruction,
not an enforced constraint -- nothing stops a reviewer from citing a source
in the changelog's Source column without having actually fetched it, the
same way a citation can look sourced without being checked. Which specific
URLs appear in the draft, and which specific URLs were fetched, are both
countable facts. Whether the *content* of a fetch supports a claim still
requires judgment -- this script only checks that the fetch was attempted
at all, not whether the reviewer read it correctly.

Usage:
    python check_citation_coverage.py <draft.md> <fetched_urls.txt>

draft.md:          the original piece being reviewed
fetched_urls.txt:   one URL per line, the URLs actually fetched during
                     verification (step 4) -- e.g. copy these straight out
                     of your own tool-call history for the review

Exit code 0 = every URL in the draft was fetched.
Exit code 1 = one or more URLs in the draft were never fetched; prints
              which ones so they can be fetched before the review is
              considered complete.
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



URL_PATTERN = re.compile(r"https?://[^\s\)\]\"'>]+")


def normalize(url: str) -> str:
    """Strip trailing punctuation and normalize trailing slashes for comparison."""
    url = url.rstrip(".,;:)")
    return url.rstrip("/")


def extract_urls(text: str) -> set[str]:
    return {normalize(u) for u in URL_PATTERN.findall(text)}


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)

    draft_path, fetched_path = sys.argv[1], sys.argv[2]

    draft_text = read_input(draft_path, "draft", allow_empty=False)
    fetched_lines = [l.strip() for l in read_input(fetched_path, "fetched-URL list").splitlines() if l.strip()]

    cited_urls = extract_urls(draft_text)
    fetched_urls = {normalize(u) for u in fetched_lines}

    unfetched = sorted(cited_urls - fetched_urls)
    unused_fetches = sorted(fetched_urls - cited_urls)

    print(f"URLs cited in draft:    {len(cited_urls)}")
    print(f"URLs fetched in review: {len(fetched_urls)}")
    print()

    if unfetched:
        print(f"NOT FETCHED -- {len(unfetched)} cited URL(s) with no matching fetch:")
        for u in unfetched:
            print(f"  {u}")

    if unused_fetches:
        print(f"\nFetched but not cited in this draft (informational, not an error):")
        for u in unused_fetches:
            print(f"  {u}")

    if not unfetched:
        print("Citation coverage confirmed: every cited URL was fetched.")
        sys.exit(0)
    else:
        print()
        print("Citation coverage INCOMPLETE. Claims resting on the URLs above "
              "should not be marked Confirmed, Incorrect, or Outdated without a "
              "fetch -- Unverified is the correct tier, and the unfetched count "
              "belongs in the coverage line. This does not stop the run.")
        sys.exit(1)


if __name__ == "__main__":
    main()
