---
name: evaluate_external_brand_03_serp_collection
description: >-
  Step 03 for evaluate_external_brand: run the two bare-brand SERPs via
  SerpAPI (up to position 50 each), merge and dedupe organic results, and drop
  every result on the workspace's own domain to produce the external page set.
"last updated": 2026-06-28T23:30:00+00:00
"last run": 2026-06-09
---

# Evaluate external brand — 03 SERP collection

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

## Inputs

From [../02_config_and_sheet/SKILL.md](../02_config_and_sheet/SKILL.md):

- `workspace_name` — confirmed brand string.
- `workspace_hosts` — apex host exclusion set.

From chat or caller:

- `max_results` — optional, default `50`. Highest SERP position considered per query.
- `serp_location` — optional. SerpAPI `location` / `gl` / `hl` overrides.

## Credentials

- SerpAPI: `{workspace_root}/credentials.json` at `serpapi.api_key`.

## 1. Build the two queries

Use `workspace_name` verbatim:

- Query A: `What is {workspace_name}?`
- Query B: `{workspace_name}`

## 2. Run each query through SerpAPI

For each query, call:

```http
GET https://serpapi.com/search
```

Params:

- `engine=google`
- `q={query}`
- `num={max_results}` (default `50`)
- `api_key={serpapi.api_key}` from `{workspace_root}/credentials.json` (resolved at `workspace_root`) (`serpapi.api_key`)
- when `serp_location` is supplied, also pass its `location` / `gl` / `hl` values.

Google no longer honors `num` or a hand-built `start` offset reliably: a single call returns only the first page (~5–10 organic results), and reissuing the same query with `start=10/20/…` just returns page 1 again. **Paginate by following the `serpapi_pagination.next` URL** from each response instead of constructing `start` yourself. Append `api_key` to that `next` URL and keep following it until you have covered positions 1–`max_results` or there is no `next` link. (Verified behavior: a manual `start` loop collapses to ~10 results; following `next` for 5 pages yields ~50.)

The per-page `position` field **resets to 1–10 on every page**, so it is not a global rank. Do not dedupe or cap on the raw `position`. Compute an **absolute position** yourself as `(page_index * 10) + local_position` (or simply the running count of results seen in page order), and **dedupe by normalized `link`**, not by `position`. Deduping by the raw `position` will silently collapse every page down to ~10 results — this was a real bug.

From each response, read the `organic_results` array. For each result keep `link` (the page URL), `title`, `snippet`, and the computed absolute position. Ignore non-organic blocks (ads, people-also-ask, knowledge graph, top stories).

Keep only organic results whose absolute position is `<= max_results`.

Log per query:

```text
[run-debug] workflow=_workflows/evaluate_external_brand | SERP | query="..." results=N
```

## 3. Drop owned-domain results

For every result, compute its host: lowercase, strip scheme and path, strip a leading `www.`, reduce to the apex host.

Drop the result when its apex host equals (or is a subdomain of) any host in `workspace_hosts`. This is what makes the linter *external*: the workspace site's own pages never appear in the output.

Log per query:

```text
[run-debug] workflow=_workflows/evaluate_external_brand | SERP | query="..." kept=N dropped_owned=N
```

## 4. Merge and dedupe across both queries

Combine the surviving results from Query A and Query B into one list.

Deduplicate by normalized URL: lowercase scheme and host, drop the URL fragment, drop common `utm_*` query params, and trim a trailing slash. When the same URL appears in both queries, keep one entry and record which queries surfaced it (`queries: ["A","B"]`).

Preserve a stable order: sort by best (lowest) `position` seen across the two queries, then by first appearance, so the most prominent external pages are processed first.

## Outputs for next step

Carry these values to [../04_extract_and_append/SKILL.md](../04_extract_and_append/SKILL.md):

- `external_results` — array of `{ url, title, snippet, best_position, queries }`, deduped and owned-domain-free.

Pass through unchanged:

- `workspace_name`
- `spreadsheet_id`, `tab_title`, `sheet_url`

Log:

```text
[run-debug] workflow=_workflows/evaluate_external_brand | MERGE | external_results=N
```

## Checks

- [ ] Both queries built with `workspace_name` verbatim (`What is {workspace_name}?` and `{workspace_name}`).
- [ ] Organic results collected up to position `max_results` (paginated if needed).
- [ ] Every owned-domain result dropped (apex + subdomains).
- [ ] Results merged and deduped by normalized URL across both queries.
- [ ] `external_results` ordered by best SERP position.
- [ ] No temporary files left behind.

Next: [../04_extract_and_append/SKILL.md](../04_extract_and_append/SKILL.md)
