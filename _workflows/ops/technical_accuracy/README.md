# Technical Accuracy Check

*Version 2.0 — 2026-08-12*

A skill that reviews technical blog posts, documentation, whitepapers, and other technical writing — in any technical domain — before it publishes — catching the kind of mistakes an expert reader would notice immediately.

## What it does

1. **Asks how deep to go** — standard, which works paragraph by paragraph, or deep, which breaks every sentence into its smallest testable pieces. Deep mode finds 5–7x more claims and costs proportionally more time; you're told that tradeoff before you choose.
2. **Reads the whole piece and names its actual audience** — enterprise CDN operators, say, rather than "people who use CDNs." Every later claim gets checked against that audience's vendors, because "true for some vendor somewhere" is a much weaker bar than "true for the people this was written for."
3. **Checks the framing separately from the claims**, asking two independent questions: does this describe how the topic works *today*, and does the advice match what practitioners actually configure rather than what's merely permitted by the spec? A piece can have every sentence correct and still be describing an outdated picture.
4. **Pulls out every checkable claim** — definitions, statistics, comparisons, "how X works" explanations — and accounts for every paragraph (every sentence, in deep mode), so nothing gets skipped silently. Analogies get their own test: if a reader took this literally, what would they wrongly conclude? An analogy with no answer logged isn't finished being checked.
5. **Verifies each claim** against primary sources (specs, official docs, vendor engineering blogs), fetching every citation the draft itself points to rather than assuming it's correct, and searching adversarially — "what would make this false" rather than "how does this work."
6. **Rates each claim** on a six-level scale from harmless wording issues up to flatly wrong, with a written test for each level so ratings stay consistent between runs. Whether a given call is *right* is still judgment; the tests narrow the spread, they don't remove it.
7. **Scores the piece 1–10** on how its claims held up — capped at 3 if anything is flatly wrong — and reports what share of the piece it was actually able to check. Framing problems are reported alongside the score and never adjust it, since they aren't a claim-level defect.
8. **Shows you the findings first** (the full table of issues plus the score) **before** offering to produce a corrected version — so you decide whether a rewrite is worth doing, rather than getting one automatically.

Long pieces are split across several subagents working in parallel, each receiving everything established up front — the named audience, the map of which claims depend on which, the sources already fetched. Hand a worker conclusions instead of context and it can only confirm what the coordinator already suspected. Consistency across chunks is then resolved centrally, not by comparing the workers' outputs to each other.

If given many pieces at once (a folder, a batch), it reviews all of them first and lets you pick which ones are worth rewriting.

## What you get back

- A **changelog**: one row per issue found, with what's wrong, how bad it is, and the source that confirms it.
- A **framing report**: who the piece is written for, plus separate verdicts on whether it describes current practice and whether its advice matches what operators actually do.
- A **score out of 10**, with a coverage line stating how much of the piece was verified and naming anything that couldn't be checked. Below 40% coverage no score is given at all — a number drawn from a handful of resolved claims misleads more than it informs, and that's the expected result for pieces about proprietary or internal systems.
- Optionally, a **corrected draft** — but only after you've seen the findings, and not at all if the framing check failed. A framing problem has no line-level fix, so the rewrite is skipped deliberately and the reason is stated.

## Why it's set up this way

Earlier versions of this check relied on the model simply "trying hard" to read everything and fetch every source — which is exactly the kind of instruction that quietly gets shortcut under time pressure. This version replaces some of that trust with things that can actually be counted: every paragraph or sentence gets logged, every citation gets fetched and tracked, and every analogy gets its test. Five small scripts confirm those things really happened rather than being reported as done.

What the scripts can't do is judge whether the answers are any good. Whether a severity rating is right, whether a source really contradicts a claim, whether a fix is correct rather than merely different, what the framing check concludes — all of that stays judgment, and no amount of tooling changes it. The scripts guarantee coverage; they don't guarantee correctness.

## Install (Claude Code)

Copy the `technical-accuracy-check/` directory into either location — no other setup, no config file to edit:

```
~/.claude/skills/technical-accuracy-check/     # available in every project
.claude/skills/technical-accuracy-check/       # this project only, commit it to share with the team
```

Then start (or restart) Claude Code and ask it to fact-check a draft — the skill triggers on requests like "check this for technical accuracy," "review before we publish," or "does this get anything wrong."

Requires **Python 3.9+** on PATH for the coverage scripts (three of them use builtin generic annotations that fail on 3.8), and an environment with subagent dispatch available — deep mode and batch runs depend on it.

Verify the install:

```
python3 tests/test_scripts.py
```

33 checks, a few seconds, no network. It confirms each coverage script passes clean input and catches each kind of incomplete input in your Python. If it fails here, the problem is the environment, not your draft.

## Layout

```
technical-accuracy-check/
├── SKILL.md          # the workflow — the only file Claude reads up front
├── README.md         # this file
├── references/       # loaded on demand, mid-review
│   ├── severity-calibration.md      # the six-tier tests
│   └── framing-calibration.md       # scope-currency vs. practice-vs-spec, audience naming
├── tests/            # smoke tests for the scripts; Claude never reads these
└── scripts/          # coverage checks — run, not read
    ├── check_paragraph_coverage.py            # every paragraph accounted for
    ├── check_citation_coverage.py             # every cited source actually fetched
    ├── check_atomic_decomposition_coverage.py # deep mode: every sentence decomposed
    ├── check_analogy_coverage.py              # every analogy got its literal-reading test
    └── check_rewrite_coverage.py              # the rewrite touched what the changelog flagged
```

`references/` and `scripts/` are loaded only when the workflow reaches them, so the up-front context cost is SKILL.md alone.

## Coverage scripts and their exit codes

The scripts check things that are countable — did every paragraph get a row, did every cited URL get fetched, did every analogy get its test. They deliberately do **not** judge correctness; severity calls, framing verdicts, and whether a source really contradicts a claim stay with the model.

A failing check never halts a review:

| Exit | Meaning | What happens |
|------|---------|--------------|
| 0 | Confirmed | Continue |
| 1 | Genuine coverage gap | Continue; the gap is named in the report's coverage line so the reader can see what wasn't checked |
| 2 | Wrong arguments | Fix the invocation |
| 3 | Script couldn't run (missing file, bad path) | Reported as "not run" — a tooling failure that says nothing about the draft, and must never be read as a finding |

The 1-vs-3 split matters: without it, a mistyped path and a genuinely incomplete review produce the same signal, and a broken invocation reads as a damning result.
