---
name: find_faq_questions
description: >-
  Shared FAQ question finder converted from the n8n FAQ Finder template. Reads
  topics from a Google Sheet Strategy tab, finds FAQ questions from Reddit,
  LinkedIn, and Google Search Console, and appends them to the FAQ Coverage tab.
  Use when the user asks to run or adapt the FAQ question finder workflow for any
  workspace sheet. To fill Response Page and Draft Response afterward, run the
  separate generate-faq-responses workflow.
"last updated": 2026-06-28T23:30:00+00:00
"last run": 2026-07-02
---

# Find FAQ questions

Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) before running this step.

Build calls at request time and do not depend on the exported n8n workflow IDs.

Do not create, persist, or commit standalone runner scripts for this workflow. If a run needs local helper code, keep it ephemeral for that run only and remove it before finishing.

This shared workflow finds candidate questions from Reddit, LinkedIn, and Google Search Console. It appends only `Topic | Question | Source` rows to `FAQ Coverage`. The [generate_faq_responses](../../generate/generate_faq_responses/SKILL.md) workflow fills `Response Page` and `Draft Response` later.

Log line prefix:

```text
[run-debug] workflow=_workflows/find_faq_questions | <PHASE> | <facts>
```

## Inputs

- `sheet_url_or_id` - required. Google Sheet URL or bare spreadsheet ID.
- `workspace_root` - optional. Repo root (this repository's root). Used to derive the GSC property when `gsc_site_url` is not given, and to merge `{workspace_root}/credentials.json`.
- `max_new_topics` - optional, default `30`. Maximum Strategy topics processed per run.
- `sources` - optional, default `reddit,linkedin`. Available sources: `reddit`, `linkedin`. Google Search Console always runs and is not controlled by this list.
- `source_max_age_months` - optional, default `6`. Reddit and LinkedIn posts/articles older than this are discarded; only posts published less than this many months ago are used. Does not affect GSC, which uses `gsc_lookback_days`.
- `gsc_site_url` - optional. The Search Console property, e.g. `sc-domain:acme.com` or `https://acme.com/`. If omitted, derive it from `workspace_slug` (legacy alias: `client`; see [Resolve GSC property](#resolve-gsc-property)).
- `gsc_lookback_days` - optional, default `30`. GSC question mining window, ending on the most recent date GSC has data.
- `gsc_min_words` - optional, default `5`. Minimum query word count (inclusive, so 5+ words).
- `gsc_min_impressions` - optional, default `5` meaning strictly greater than 5 (keep queries with `impressions >= 6`).
- `finder_model` - optional. Default `claude-sonnet-4-6` (root `config.json` at `anthropic.model_smart`). Must be a model on the permitted list in root `config.json`.

Do not hardcode a sheet ID in this shared skill. Always take the sheet from chat or from a workspace wrapper skill.

## Credentials

Read credentials from `{workspace_root}/credentials.json` (resolve `@ref` per run_workflow). When a workspace wrapper calls this skill, merge wrapper credentials over the root values only for that run.

- Google OAuth for Sheets: `google.oauth_token_unified`.
- Google OAuth for GSC: `google.oauth_token_unified`. The token must include `https://www.googleapis.com/auth/webmasters.readonly`. GSC runs on every run, so this scope is always required.
- Optional GSC fallback account: `google.oauth_token_unified_2`, if present. Step 04 falls back to it only when the primary account cannot read a matching Search Console property. Generate it with the standard Google OAuth installed-app flow (Desktop client in `google.oauth_installed_client`).
- SerpAPI key: `serpapi.api_key`.
- Anthropic key for question extraction: `anthropic.api_key`.

Refresh the Google access token once at the start of the run with `POST {token_uri}`. Use the resulting access token on all Sheets calls. Never log OAuth tokens, API keys, or raw prompt bodies that contain sensitive workspace context.

## Sheet Contract

Resolve tab names via the Sheets API instead of assuming gids. Expected tabs:

- `🎯 Strategy` - source topics, column A row 2+.
- `FAQ Coverage` - working tab where questions are appended.

Map by header name when present. If headers are missing, create or normalize the header row to:

```text
Topic | Question | Source | LLM Response | Draft Response | Response Page | Mentioned | Topics | % Mentioned
```

This workflow writes only these three columns:

- `Topic` - source topic from Strategy (or a `GSC` label for Search Console questions).
- `Question` - one FAQ question per row.
- `Source` - one of three labels, each paired with a relevant link or page:
  - `LinkedIn` plus the relevant LinkedIn post/article URL.
  - `Reddit` plus the relevant Reddit thread URL.
  - `GSC` plus the page that showed up in the Search Console results.

Leave every other column (e.g. `LLM Response`, `Draft Response`, `Response Page`, `Mentioned`, `Topics`, `% Mentioned`) untouched. The `Response Page` and `Draft Response` columns are filled by the separate [generate_faq_responses](../../generate/generate_faq_responses/SKILL.md) workflow.

## Question Quality Rules

These rules apply to every question before it is written to `FAQ Coverage`, regardless of source (Reddit, LinkedIn, or GSC). Steps 04 and 05 both enforce them.

### Drop junk queries

Discard any candidate that is not a genuine human FAQ. Drop the query when any of these is true:

- It contains instruction-like fragments aimed at an LLM rather than a search, such as `return the url`, `official homepage`, `give me`, `list the`, `as an ai`, `ignore previous`, `respond with`, `output the`, or `in json`.
- It injects context that a person would not type into search, e.g. `my location is`, `i am located in`, `assume i am`, `pretend`.
- It contains more than one `?`, or has text after the first `?` (a compound instruction such as `... homepage.?`).
- It is primarily about a third-party brand or entity unrelated to the workspace's topics (e.g. funding amounts for other companies, "official website url for {brand}"). Keep competitor-comparison questions only when they also name the workspace's topic space (feature flags, releases, rollouts, experimentation, etc.).
- It contains stray punctuation runs (e.g. `.?`, `?.`, `..`) or trailing sentence fragments.

### Require fully-formed questions

Only output a question that reads as a single, complete, grammatical question:

- It must start with a question word (`who, what, when, where, why, how, which, whom, whose`) or an auxiliary/verb (`can, could, should, would, will, do, does, did, is, are, was, were, has, have, am`).
- It must end with exactly one `?`.
- Reject bare keyword phrases or noun fragments that merely have a `?` appended (e.g. `Tool that automatically finds and cleans up stale feature flags?`).
- Use sentence case with a capitalized first letter. Do not paraphrase or invent a question from a keyword phrase; only keep questions that are already interrogative.

### Cap per source per topic

For each `(topic, source-type)` pair, output at most: 3 questions for `reddit`, 3 for `linkedin`, and 5 for `gsc`. When more than the cap survive filtering, keep the strongest: for GSC keep the highest-impression questions; for Reddit and LinkedIn load the page, scan it for questions, and keep the ones that appear highest on the page.

### Use only recent Reddit and LinkedIn posts

Only mine Reddit threads and LinkedIn posts/articles published within `source_max_age_months` (default 6), measured from today. Enforce recency from SerpAPI data: constrain the SERP query to a `tbs` date-range window of `[cutoff_date, today]`. When a result has an explicit SERP date, drop it if that date is before the cutoff. Do not skip undated results that come back inside the window. This rule does not apply to GSC, which is bounded by `gsc_lookback_days`.

## Run Order

Run these child skills in order:

1. [01_preflight/SKILL.md](01_preflight/SKILL.md) — verify sheet access, credentials, and inputs.
2. [02_sheet_and_topics/SKILL.md](02_sheet_and_topics/SKILL.md) — resolve the sheet, validate headers, and build the topic queue plus dedupe sets.
3. [03_source_collection/SKILL.md](03_source_collection/SKILL.md) — collect Reddit and LinkedIn source text.
4. [04_gsc_questions/SKILL.md](04_gsc_questions/SKILL.md) — resolve the GSC property and mine GSC question candidates matched to Strategy topics.
5. [05_extract_and_append/SKILL.md](05_extract_and_append/SKILL.md) — extract questions, filter them, and append each `Topic | Question | Source` row to `FAQ Coverage` as soon as it is found.

Append rows incrementally as results are found. Do not hold questions in memory and write them only at the end of the run.

The end state is appended rows in `FAQ Coverage` with `Topic`, `Question`, and `Source` populated. No website pages are edited. To fill `Response Page` and `Draft Response` on those rows, run the [generate_faq_responses](../../generate/generate_faq_responses/SKILL.md) workflow next.

## Logging Template

```text
[run-debug] workflow=_workflows/find_faq_questions | START | sheet={spreadsheet_id}
[run-debug] workflow=_workflows/find_faq_questions | SHEET | strategy="{strategy_title}" faq="{faq_title}"
[run-debug] workflow=_workflows/find_faq_questions | QUEUE | topics=N max={max_new_topics}
[run-debug] workflow=_workflows/find_faq_questions | SERP | topic="..." source=reddit results=N kept=N
[run-debug] workflow=_workflows/find_faq_questions | SCRAPE | source=reddit url=... status=... chars=N
[run-debug] workflow=_workflows/find_faq_questions | EXTRACT | topic="..." source=reddit questions=N
[run-debug] workflow=_workflows/find_faq_questions | GSC | window={start}..{end} rows_fetched=N kept_questions=N
[run-debug] workflow=_workflows/find_faq_questions | APPEND | topic="..." rows=N
[run-debug] workflow=_workflows/find_faq_questions | DONE | appended_rows=N skipped_dupes=N failed_sources=N
```

## Checklist

```text
Task Progress:
- [ ] Sheet URL/ID confirmed from chat
- [ ] Google access token refreshed
- [ ] [01_preflight/SKILL.md](01_preflight/SKILL.md) completed
- [ ] [02_sheet_and_topics/SKILL.md](02_sheet_and_topics/SKILL.md) completed
- [ ] [03_source_collection/SKILL.md](03_source_collection/SKILL.md) completed
- [ ] [04_gsc_questions/SKILL.md](04_gsc_questions/SKILL.md) completed
- [ ] [05_extract_and_append/SKILL.md](05_extract_and_append/SKILL.md) completed
- [ ] Final summary includes appended_rows, skipped_dupes, failed_sources
```
