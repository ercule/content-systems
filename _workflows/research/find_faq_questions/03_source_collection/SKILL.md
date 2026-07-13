---
name: find_faq_questions_03_source_collection
description: >-
  Step 03 for find_faq_questions: collect source text from Reddit and
  LinkedIn via SerpAPI, bounded by a recency window.
"last updated": 2026-06-28T23:30:00+00:00
"last run": 2026-07-08
---

# Find FAQ questions — 03 Source Collection

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

This step collects Reddit and LinkedIn sources only. Google Search Console runs separately in [../04_gsc_questions/SKILL.md](../04_gsc_questions/SKILL.md).

## Inputs

From [../02_sheet_and_topics/SKILL.md](../02_sheet_and_topics/SKILL.md):

- `topic_queue` - new Strategy topics, used to drive Reddit and LinkedIn searches.
- `existing_questions`
- `existing_sources`

From chat or caller:

- `sources` - optional, default `reddit,linkedin`. Controls which of the Reddit and LinkedIn source searches run.
- `source_max_age_months` - optional, default `6`. Reddit and LinkedIn posts/articles older than this are discarded before extraction.

## Credentials

- SerpAPI: `{workspace_root}/credentials.json` at `serpapi.api_key`.

## 1. Collect Reddit And LinkedIn Sources

For each topic, run enabled Reddit and LinkedIn searches. Process topics serially. Within one topic, sources may run in parallel if the user asked for parallelism and rate limits allow. Do not run a generic Google source. Use SerpAPI only to discover Reddit and LinkedIn URLs and snippets.

For each result, mine questions from SerpAPI fields in page order: title first, then snippet, highlighted words, and source description. Do not fetch Reddit pages. LinkedIn bodies may be fetched as a bonus only; do not depend on them. When a source is capped, keep questions that appear highest in the available text.

### Recency cutoff

Compute the cutoff once at the start of this step:

- `cutoff_date` = today minus `source_max_age_months` months (default 6, so roughly 180 days back).

Only Reddit threads and LinkedIn posts/articles published on or after `cutoff_date` may be mined. Enforce recency from SerpAPI data only. Do not fetch the source page to determine a date.

Constrain every SerpAPI query by date with a custom range so Google only returns results it dates within the window:

```text
tbs=cdr:1,cd_min:{cutoff_mm/dd/yyyy},cd_max:{today_mm/dd/yyyy}
```

Apply recency from SerpAPI as follows:

- Treat the `tbs` date-range window as the main recency gate.
- When a result has a SERP date (top-level `date`, or a date parsed from the snippet), parse it and drop the source if it is before `cutoff_date`.
- Do not skip a source merely because it has no explicit SERP `date`. The `tbs` window already bounds recency.

### Reddit

Call SerpAPI with query `{topic} site:reddit.com` and the recency `tbs` constraint above.

Do not fetch `reddit.com` or the `.json` endpoint; both return `403` for unauthenticated/datacenter requests and there is no Reddit OAuth. Mine questions from the SerpAPI organic result itself, using these fields in page order:

- `title` (Reddit thread titles are frequently the FAQ itself, e.g. `Has AI automation actually worked for you?`).
- `snippet` and `snippet_highlighted_words`.
- `about_this_result.source.description` when present (an extra sentence or two of thread text).

Rank questions by where the text appears: `title` outranks `snippet`, which outranks the `about_this_result` description. Apply the SerpAPI recency handling above (keep results inside the `tbs` window; drop only when an explicit SERP date is before `cutoff_date`). Record each kept source as `Reddit` paired with the relevant Reddit thread URL.

### LinkedIn

Call SerpAPI with query `{topic} site:linkedin.com` and the recency `tbs` constraint above.

Mine questions from the same SerpAPI result fields as Reddit (`title`, `snippet`, `snippet_highlighted_words`, `about_this_result.source.description`), ranked by where they appear. LinkedIn article/post bodies sometimes load for unauthenticated clients; you may optionally fetch the body for richer text and rank questions higher when they appear near the top. Treat any fetched body as a bonus only: never depend on it, and never skip a source because the body failed to load.

Apply the SerpAPI recency handling above. Use the `tbs` window as the recency gate and drop a source only when an explicit SERP date is before `cutoff_date`. Do not skip undated LinkedIn results that come back inside the window. Record each kept source as `LinkedIn` paired with the relevant LinkedIn post/article URL.

## Outputs For Next Step

Carry these values to [../04_gsc_questions/SKILL.md](../04_gsc_questions/SKILL.md):

- `source_bundles`: array of `{ topic, source_label, source_url, source_text, published_date, confidence }`. `source_text` is built from SerpAPI result fields (`title`, `snippet`, `snippet_highlighted_words`, `about_this_result.source.description`), plus an optional fetched LinkedIn body. `published_date` is the SERP date when present, otherwise `serp-window` to denote it was admitted by the `tbs` recency window. Bundles with an explicit SERP date before the cutoff are not carried forward.
- `failed_sources_count`

## Logging

```text
[run-debug] workflow=_workflows/find_faq_questions | SERP | topic="..." source=reddit results=N kept=N cutoff={cutoff_date}
[run-debug] workflow=_workflows/find_faq_questions | SOURCE | source=reddit url=... serp_date={date_or_serp-window} chars=N
[run-debug] workflow=_workflows/find_faq_questions | SKIP | source=linkedin url=... reason=too_old serp_date={date}
```

## Checks

- [ ] Enabled Reddit and LinkedIn sources searched with the `tbs` recency window.
- [ ] Recency cutoff computed (today minus `source_max_age_months`, default 6 months).
- [ ] Recency enforced from SerpAPI only: `tbs` window plus explicit SERP dates; no Reddit/LinkedIn page or `.json` fetch used to determine dates.
- [ ] Undated results inside the `tbs` window kept, not skipped.
- [ ] Questions mined from SerpAPI result fields (title, snippet, highlighted words, source description).
- [ ] No temporary files left behind.
