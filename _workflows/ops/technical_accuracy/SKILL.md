---
name: technical_accuracy
description: >-
  Fact-checks technical writing before it publishes. Extracts every
  checkable claim, verifies each against primary sources, rates severity, and
  reports a changelog and score. Writes a findings changelog. Does not rewrite. Vendored from
  hydrofranz/technical-accuracy-check. Use for "fact-check this," "review before
  we publish," or generate_article.
"last updated": 2026-09-20
"last run": 2026-10-13
---

# Technical Accuracy Check

## Pipeline default (this ops skill)

Always, including generate_article and standalone runs:

- **Deep/atomic** depth. Do not ask Standard vs Deep.
- **Checker only.** After findings, write the changelog. Do not rewrite the manuscript. Do not ask.
  - generate_article: `{RUN_DIR}/{id-or-slug}-accuracy.md`
  - otherwise: `{stem}-accuracy.md` next to the manuscript
  Empty findings are valid (`Findings: none`). Next is the workspace implement step, if one exists.
- Claim-level fixes still apply when framing reports an ISSUE; include that ISSUE in the handoff.
- Refer to the product by its proper name, as set in the workspace context.

Step 8 (rewrite) lives in the workspace technical accuracy implement step, not here.

Read [run_workflow]({content_systems_public_root}/setup/run_workflow/SKILL.md) before running this step.

Log line prefix: `[run-debug] workflow=<workspace>/_workflows/ops/technical_accuracy | <PHASE> | <facts>`

Vendored from [hydrofranz/technical-accuracy-check](https://github.com/hydrofranz/technical-accuracy-check). Coverage scripts live in [scripts/](scripts/). Calibration: [references/severity-calibration.md](references/severity-calibration.md), [references/framing-calibration.md](references/framing-calibration.md).

Requires an environment with subagent dispatch — deep mode and batch runs depend on it, and there is no browser/no-subagent fallback.

## Produce-pipeline override

When a workspace `generate_article` technical accuracy step calls this skill:

- Run steps 1–7 (review only). Do not run step 8. Skip chunked subagent dispatch.
- Prefetch the source ledger from `{id-or-slug}-relevant-articles.md` and `{id-or-slug}-crosslinks.md` in `RUN_DIR` when those files exist.
- Write `{RUN_DIR}/{id-or-slug}-accuracy.md` with only the changelog, framing report, score/coverage line, and 5b tally.
- Do not write sentence-level accounting, analogy logs, or dispatch transcripts into that file or the reply.
- Do not paste the changelog into the reply. The reply is the one-line log.

Standalone runs follow the same Deep/atomic + findings-only defaults. Do not rewrite unless the caller also runs the workspace technical accuracy implement step.

## Why this exists

Bar: would a genuinely knowledgeable reader wince? Three independent failure modes, check all three, none substitutes for another:
1. **Claim-level**: a sentence is wrong, outdated, or unsupported.
2. **Framing-level**: every sentence checks out but the piece's scope/thesis describes an outdated or wrong-audience picture of the domain (step 2).
3. **Credibility-level**: true claims delivered with unsupported superlatives, circular vendor logic, or empty aphorisms (folded into steps 2 and 5).

A fourth, process-level failure caused a real review to miss issues it had already surfaced: **what the orchestrator knows is not what the subagent doing the work knows.** Any time work is dispatched (3b, batch mode), everything established up front — the audience line, the dependency and restatement maps, the source ledger — goes into every dispatch prompt in full. Hand a worker conclusions instead of context and it can only confirm what you already suspected.

## Workflow

### 0. Depth

Always **Deep/atomic**. Do not ask Standard vs Deep.

### 1. Read the whole draft, log two maps

Read start to finish. While reading, log two maps.

**Narrative dependency map**: any later claim whose force depends on an earlier one being true (`D1: <earlier claim> -> <later claim that depends on it>`). Usually 2-8 entries. This is what step 4's Pass A resolves — it is not the same thing as diffing subagent outputs against each other, which only catches terminology drift, not logical contradiction.

**Restatement map**: claims asserted more than once (`R1: <claim> @ sentences 3, 47, 112`). Concentrated in TL;DR, intro, section summaries and conclusion — the same places step 3 flags for smuggling claims in under cover of restating. Each cluster is verified **once**, in the chunk owning its first occurrence; every other occurrence inherits that verdict, marked `inherited from R<n>`, and is not re-searched. This is a correctness fix as much as a cost one: a claim stated three times currently gets searched three times and counted three times in the score, silently tripling its weight.

### 2. Framing check (whole piece, never chunked)

Two independent sub-checks, both required even if every claim passes step 5:

- **2.-1 Name the audience first.** One line: who actually reads this (e.g. "enterprise CDN operators on Akamai/Fastly" vs. "self-serve consumer tier"), inferred from the piece/publisher. Every thesis/premise claim later gets verified against *this* audience's vendors, not "any CDN" — "true for some vendor" is a much weaker bar than "true for this audience's vendors," and is the single most common way a framing miss slips through.
- **2a Scope currency**: does this match current practice, or an outdated picture? Derive the scope-currency questions from the piece's own domain during the step 1 read — write them down as an explicit list before clearing any, so one cleared question can't stand in for all of them. (In a CDN piece: "discusses cacheable dynamic content" ≠ "mentions acceleration of uncached dynamic traffic"; both need their own verdict. Every domain has pairs like this.)
- **2b Practice vs. spec**: does the advice match what practitioners actually configure, not just what's spec-valid? Search adversarially ("what do operators actually configure by default"), not supportively ("how does X work").
- **2c Representativeness** (gated): only run on examples inside a section 2a already flagged ISSUE — is this example what a current practitioner would reach for first?
- **2d Omissions**: what would a practitioner from the 2.-1 audience expect this piece to address, that it never does? Every other step checks claims the draft makes; this is the only one that can catch what it failed to say, and an omission produces no changelog row because there is no sentence to flag.

  Candidates come from one adversarial search ("what gets left out of <topic> explanations" / "what do practitioners wish <topic> guides mentioned"), not from free association. Each candidate must clear **both** filters or it is dropped, silently and without comment:
  1. **In the piece's own stated scope** — not an adjacent topic it never promised to cover. "Doesn't discuss HTTP/3" fails this for a piece about cache keys.
  2. **Its absence changes what a reader would do** — name the concrete consequence for the named audience. "Doesn't say this only applies to pull CDNs" passes: an Akamai operator would act on it wrongly.

  **There is no cap, and no target.** Most pieces have none; reporting zero is the ordinary result and not a sign of insufficient effort. Report every candidate that clears both filters, however many that is — truncating to a tidy number would hide the deficiency from a reader who has no way to know anything was withheld.

  **Volume is itself a finding.** If more than about three clear both filters, the piece is usually not a piece with omissions but a piece scoped wrong or aimed at the wrong audience. Say so and escalate to a 2a framing ISSUE — which routes it to the machinery that already exists for that, rather than leaving a long list to be read as a punch list of additions.

A framing ISSUE outranks any severity tier as the headline finding, is reported separately from the score (never adjusts it), and blocks a rewrite (step 8) regardless of what was asked for. 2d omissions are reported the same way — alongside the score, never adjusting it — but do **not** block a rewrite unless their volume escalated them into a 2a ISSUE; an omission is additive, not evidence the piece is built wrong. Read `references/framing-calibration.md` for the 2a-vs-2b test and a worked audience-naming failure.

### 3. Extract every claim

Number every paragraph; for each, list claim IDs or write "no checkable claims" — no silent skips. Run `scripts/check_paragraph_coverage.py <draft> <accounting>` after.

Watch especially: **summary/TL;DR/conclusion paragraphs** (routinely smuggle in a new claim under cover of "just restating"); **should/must/rather-than sentences** (strip the framing, extract the comparative premise underneath); **thesis/premise claims** (verify against the named audience from 2.-1, not generically).

Claim types: definitions, mechanisms, protocol/spec behavior, numbers (including hedged/conditional ones), comparisons, absolutes/superlatives, analogies.

**Analogies get a mandatory literal-reading test — the only claim type with no natural "go verify this" trigger, which is exactly why they get waved through otherwise.** For every analogy-tagged assertion: "if a reader took this literally, they'd wrongly conclude ___." "No wrong conclusion" is a valid answer; an absent one is not. Log as `<n>: <label>: <answer>` in a companion file, run `scripts/check_analogy_coverage.py <accounting> <analogy_test_file>`.

**Dispatch completeness (3b, batch).** Everything established before dispatch goes into every prompt in full — audience line, dependency map, restatement clusters, section skeleton, source ledger — not summarized, not pre-filtered to "what I think is relevant." This is the most common way a review confirms its own assumptions: the orchestrator does the thinking, hands workers its conclusions rather than the material, and gets back agreement.

### 3b. Deep mode: atomic decomposition + chunked dispatch

Only if deep mode was chosen. Number every sentence in the draft; decompose each into its smallest testable assertions (`<n>: assertions A1, A2` / `<n>: no atomic assertions`). This replaces paragraph-level claims for scoring — don't run both. Verify with `scripts/check_atomic_decomposition_coverage.py <draft> <atomic_accounting>`.

**Long piece → chunk across subagents:**
1. Do steps 0-2 yourself first (depth, full read, dependency map, audience name, framing check) — framing never chunks.
2. **Split on section boundaries first**, target ~40-60 sentences/chunk, numbered ranges that don't overlap. Only split *within* a section if it exceeds ~80 sentences, and never across a dependency-map edge — a chunk boundary through an argument forces both subagents to establish the same premise and manufactures a seam Pass A then has to reconcile. An uneven 30/70 split along a real boundary beats an even 50/50 through the middle of one.
3. Dispatch one subagent per chunk: atomic decomposition + analogy test + Pass B search + severity, scoped to its sentence range. Each prompt carries, instead of the whole draft:
   - its own sentence range, verbatim and numbered;
   - the **dependency map** and **restatement clusters** from step 1 — already the distilled version of what one chunk needs to know about the rest;
   - the **audience line** from 2.-1, so thesis claims are checked against the right vendors;
   - a **section skeleton**: every heading in order with a one-line gist, so the chunk knows where it sits in the argument;
   - the **pre-fetched source ledger**.

   A subagent whose claim turns on text outside its range asks for that text rather than guessing — an explicit request is cheap; a confident guess about an unseen paragraph is the failure this replaces. Sending the entire draft to every chunk costs N × the draft and mostly buys context the dependency map already carries; what it uniquely bought was cross-chunk contradiction spotting, and that is Pass A's job, done centrally in step 4 of this list, not something to pay for N times over.
4. **Pass A is yours, not a diff of subagent outputs.** Resolve every dependency-map line (still holds / contradicted) plus a terminology/number drift scan across chunks. An unresolved line is disclosed in the coverage line the same as a failed script — neither halts the review.
5. Reassemble: concatenate accounting rows, changelogs, analogy-test rows into one master set. Inherited verdicts keep their accounting row (coverage is unaffected) but enter scoring **once per cluster, not once per occurrence**. Run `scripts/check_atomic_decomposition_coverage.py` and `scripts/check_analogy_coverage.py` against the full draft/reassembled tables.
6. One combined score across all resolved assertions (weighted, not averaged per chunk). One combined changelog + framing write-up, noting chunked deep mode in the tally.

Rewrite after chunked review: same per-chunk dispatch, each subagent gets only its slice of the changelog; you do the cross-chunk seam check yourself; run `scripts/check_rewrite_coverage.py` once on the reassembled draft.

### 4. Verify — two passes

**Pass A (no search):** resolve the dependency map from step 1, plus a terminology/number drift scan. Do this first, it's free. Not the same as cross-chunk output diffing (that catches naming drift only).

**Pass B (search):** for anything not fully certain — nearly everything technical. Priority: RFCs/specs → MDN/vendor docs → vendor engineering blogs → textbooks. Deprioritize generic SEO/AI-explainer content. If a source is cited in the draft, fetch it — every time, track fetched URLs, run `scripts/check_citation_coverage.py <draft> <fetched_urls>` before finalizing.

**Fetch each source once, and read it once.** Before dispatch, pull every URL the draft cites into a shared ledger (`<url> | <what it says that bears on this draft>`) and hand that ledger to every subagent, which appends anything new it fetches. Then **group verification by source rather than by claim**: ten assertions resting on RFC 9111 are one fetch and one careful read, not ten searches. Without this, a spec cited in three chunks is fetched three times and read three times, and the three readings can disagree. Check corroboration independence (two sources from the same lineage ≠ confirmation). Search adversarially for thesis claims ("what would make this false"), and against the audience named in 2.-1 specifically, not "any vendor."

### 5. Severity (six tiers, use the test not a gut feel)

- **Severe** — a general reader would catch it. Caps score at 3.
- **Incorrect** — needs domain expertise to catch; a source directly contradicts it.
- **Outdated** — was true, a source shows a real before/after.
- **Imprecise** — true but omits something that flips the takeaway.
- **Vague** — no accuracy problem, just unclear.
- **Unverified** — genuinely searched, couldn't resolve (never from skipping a fetch).

Read `references/severity-calibration.md` for the Outdated-vs-Incorrect and Imprecise-vs-Vague tests.

**Credibility/tone** (separate axis, no tier, no changelog row): unsupported superlatives, circular vendor logic, empty aphorisms. Flag during extraction, report as a short callout.

### 5b. Adversarial pass over the findings

Every script so far checks that work *happened*. Nothing checks whether a conclusion *holds* — a confidently wrong severity call passes every guardrail in this skill. One subagent, one pass, whose only job is to argue the opposite of what was concluded.

**Scoped to findings, not to sentences — this is what keeps it cheap.** Its cost tracks the number of serious findings (usually a handful), not draft length, so it costs roughly the same on a 40-sentence piece as on a chunked deep run. Send it, in priority order:
1. every **Severe** and **Incorrect** row — these cap the score and drive the rewrite;
2. any verdict resting on **inference rather than a fetched source**;
3. **load-bearing Confirmed** claims — thesis/premise claims and anything on the dependency map.

Stop at ~12 items; if there are more, take them in that order and say how many went untested. Skip Vague and Imprecise (low stakes) and Unverified (nothing to falsify).

It receives the claims, the verdicts, and the source ledger — arguing from the ledger first, fetching only when a challenge genuinely needs a source the ledger lacks. For each it returns **holds / weakened / overturned**, with the reason. Overturned and weakened verdicts are corrected in the changelog **before** scoring, since they move the number.

Report the tally with the score: "12 findings challenged, 1 overturned, 2 weakened." A pass that overturns nothing is a real and useful result; a pass that overturns nothing *every time* means it is rubber-stamping, and should be treated as broken rather than reassuring.

### 6. Score

Weights: Confirmed 1.0, Vague 0.9, Imprecise 0.75, Outdated 0.6, Incorrect 0.2, Severe 0.0. Unverified excluded from both numerator and denominator.

`Score = (Σweights / resolved claims) × 10`, round to nearest whole (report X.5 as-is if exact). **Cap at 3 if any Severe.** Framing/2c/2d/credibility findings never adjust the score — report them alongside it, headline finding first if one exists. Verdicts overturned or weakened in 5b **do** move the score, because they change the tier itself; score after that pass, never before. Report coverage (resolved/total) every time; flag low coverage (<50%) explicitly. **Below 40% coverage, report no score at all** — state the coverage, the changelog, and one line on why the number is being withheld. A 9/10 drawn from four resolved claims out of sixty is not a weak signal, it is a misleading one, and the score is the part people quote. This is the expected outcome for pieces about proprietary or internal systems, where little is externally sourceable; say that plainly rather than producing a number that implies otherwise. **Any coverage script that exited 1 is named in that same line with its gap** (e.g. "coverage 41/47 (87%); 3 paragraphs unaccounted for, 1 cited URL unfetched") — one place the reader looks to see what was actually checked. A script that exited 3 is a setup failure: report it as "not run," never as a gap, and never let it read as a finding about the draft.

### 7. Review first, always — then ask about rewrite

Always run 1-6. Show changelog + framing check before asking about a rewrite.

**Changelog:** one row per flagged claim only — never a row for Confirmed. Columns: # | Claim | Issue | Severity | Fix | Source. Close with a tally (all tiers incl. confirmed count), the score/coverage line, and any credibility callout.

**Framing report:** 2a and 2b every time (state OK explicitly if clean, confirm every distinct scope question was checked individually), 2c only if triggered. **2d omissions** every time — one line ("Omissions: none material") when clean, otherwise every entry that cleared both filters with its concrete consequence. Include the 5b challenge tally next to the score.

Do not ask. Do not rewrite. Write the changelog to the accuracy file. Next is the workspace implement step, if one exists.

### 8. Rewrite (only for pieces selected)

Do not run this section in the checker. It lives in the workspace technical accuracy implement step.

**If step 2 found a framing issue, still apply claim-level Fixes and report the ISSUE in the handoff. Do not skip claim rewrites** — even for independently-Severe claims. Open the note with `Rewrite skipped:` followed by the reason — that exact opening is the marker `scripts/check_rewrite_coverage.py --framing-issue` looks for. A framing problem has no line-level fix.

Otherwise: fix Severe/Incorrect/dated-Outdated fully; Imprecise/Vague with the minimum edit; Unverified by softening or an inline `[UNVERIFIED: ...]` flag; credibility-flagged sentences too. Each 2d omission is either addressed or explicitly declined with a reason — silently dropping one puts the rewrite back where the original was. New facts introduced during a fix must be verified now, same sourcing bar as step 4.

**Minimum-edit rule:** smallest edit that fixes it. If that breaks comprehension, expand to the clause, then the paragraph — **stop at the paragraph boundary**; needing more than that signals a framing problem, not a claim problem, and should be named as such instead of chased further.

After rewriting: one bounded, zero-fetch re-read of edited paragraphs + immediate neighbors, checking only for a seam break at the paragraph boundary. Run `scripts/check_rewrite_coverage.py` before calling it done.

## Batch runs (multiple pieces)

**Wave 1 — review only, one subagent per piece**, steps 1-6 (including 5b) at the batch's chosen depth, each on a clean context. Each prompt carries the full dispatch payload from 3b — same risk, same fix. Present one summary table (Framing ISSUE rows first, then Score/Coverage/Claims-checked columns), then ask which numbers to rewrite (all/some/none).

**Wave 2 — rewrite only, selected pieces**, one subagent per piece, each given only its own wave-1 changelog (not re-extraction). Update the Files column afterward; don't regenerate the summary.

Close the batch with any **recurring pattern across pieces** (same stale benchmark, same oversimplified model) — a pattern showing up in every piece is also worth checking against your own review process, not just the drafts.

## Notes

- Never invent a citation. Cite only what was actually found.
- Style/voice passes stay separate from this one; don't let a style preference override a needed correction (credibility/tone is the one narrow exception — it's evidentiary posture, not voice).
- **Top three real-review misses, check these first if something was missed:** TL;DR/summary paragraphs waved through as restatement; should/rather-than sentences waved through as opinion; analogies logged but never tested (nothing to search).
- **Ceiling of search-based review:** weak on operator-level detail no one would think to search for (an obscure named vendor feature, precise internal architecture). This is a different, more forgivable miss than skipping the audience-naming or omissions steps — one is a discipline failure, the other is a real limit fixable only by a human domain expert. Flag it in the framing report rather than presenting the automated pass as final.

## Why this is deterministic and what isn't

Prose instructions get skipped under time pressure — that's why the checkable parts are scripts, not just emphasis: `scripts/check_paragraph_coverage.py` / `scripts/check_citation_coverage.py` (review completeness), `scripts/check_atomic_decomposition_coverage.py` (deep-mode sentence coverage), `scripts/check_analogy_coverage.py` (every analogy got its test), `scripts/check_rewrite_coverage.py` (the rewrite touched what the changelog flagged). In chunked runs, the paragraph and analogy checks only mean something run against the *full* draft and the reassembled tables — per-chunk only proves that chunk, not the reassembly.

**Exit codes are a contract, and a failing check never halts the review.** `0` = confirmed. `1` = a real coverage gap: disclose it in the coverage line and keep going. `2` = wrong arguments. `3` = the script could not run at all (missing file, bad path) — a tooling failure that says nothing about the draft, reported as "not run" and never as a gap. Treating a `3` as evidence of a bad piece is a misread, and treating a `1` as a reason to abandon the review is worse: the gap is information for the reader, not a stop condition.

What stays judgment-only, permanently, because there's no ground-truth list to diff against: whether a severity call is right, whether a source really contradicts a claim, whether a dependency-map resolution is correct, whether an analogy's test *answer* is right (not just present), whether a fix is correct (not just changed), what framing concludes. Scripts guarantee coverage; they don't guarantee correctness.
