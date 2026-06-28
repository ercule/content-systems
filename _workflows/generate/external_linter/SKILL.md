---
name: external_linter
description: >-
  Shared external linter. For a given workspace, runs the bare-brand SERPs
  ("What is {workspace_name}?" and "{workspace_name}"), takes every organic result up
  to position 50 that is NOT on the workspace's own domain, extracts the single
  paragraph from each page that talks about the brand, and writes one
  `Site | Mention` row per page to a brand-new Google Sheet in the workspace
  Drive folder. Use when the user asks to run or adapt the external linter for a
  workspace.
"last updated": 2026-06-08
"last run": 2026-06-09
---

# External Linter

Step 0: Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) (runtime HTTP, logging, ephemeral runs). Build calls at request time.

Do not create, persist, or commit standalone runner scripts for this workflow. If a run needs local helper code, keep it ephemeral for that run only and remove it before finishing.

## What this does

For one workspace, this workflow audits how the rest of the web describes the brand:

1. Run the two bare-brand searches on Google via SerpAPI:
   - `What is {workspace_name}?`
   - `{workspace_name}`
2. Collect organic results up to position 50 from each query, merge them, and drop any result whose host is on the **workspace's own domain**. What is left is the set of *external* pages that rank for the brand.
3. For each external page, **render with local Playwright** and extract the **single most relevant paragraph that talks about the brand** (the "mention").
4. Write one `Site | Mention` row per page to a **new Google Sheet** created in the workspace Drive folder.

No workspace-site pages are edited. The only durable output is the new sheet.

Log line prefix:

```text
[run-debug] workflow=_workflows/external_linter | <PHASE> | <facts>
```

## Inputs

- `workspace_root` — required. Path to the repo root (this repository's root). Used to read ``{workspace_root}/config.json`` for the domain and Drive folder, and to merge ``{workspace_root}/credentials.json``.
- `workspace_name` — optional. The brand string used verbatim in the two SERP queries (e.g. `Acme`). If omitted, resolve per [Resolve workspace display name](#resolve-workspace-display-name) and confirm with the user before searching.
- `workspace_domains` — optional. One or more apex hosts that count as "the workspace's domain" and are excluded from results (e.g. `acme.com`). If omitted, resolve from ``{workspace_root}/config.json`` per step 01.
- `drive_folder_id` — optional. Destination Drive folder for the new sheet. If omitted, derive from ``{workspace_root}/config.json`` `google_drive_url`.
- `max_results` — optional, default `50`. Highest SERP position considered per query.
- `serp_location` — optional. SerpAPI `location`/`gl`/`hl` overrides; default unset (Google defaults).
- `linter_model` — optional. Default `claude-sonnet-4-6` (root `config.json` at `anthropic.model_smart`). Must be a model on the permitted list in root `config.json`. Used to extract the relevant paragraph.

Do not hardcode a workspace, brand string, or sheet ID in this shared skill. Always take them from chat or from ``{workspace_root}/config.json``.

## Credentials

Read credentials from `{workspace_root}/credentials.json` (resolve `@ref` per run_workflow).json`` over the root values only for that run.

- Google OAuth for Drive + Sheets: `google.oauth_token_unified`. Scopes must include `https://www.googleapis.com/auth/drive` and `https://www.googleapis.com/auth/spreadsheets` (the new sheet is created via Drive and written via Sheets).
- SerpAPI key: `serpapi.api_key`.
- Anthropic key for paragraph extraction: `anthropic.api_key`.

Refresh the Google access token once at the start of the run with `POST {token_uri}`. Reuse it for every Drive and Sheets call. Never log OAuth tokens, API keys, or raw prompt bodies.

## Resolve workspace display name

`workspace_name` is the literal string typed into Google, so get it right before searching:

1. If the caller passed `workspace_name`, use it verbatim.
2. Else read ``{workspace_root}/config.json`` and use a `workspace_name` field if present.
3. Else infer a candidate from the resolved apex domain (e.g. `acme.com` → `Acme`, `getwidget.io` → `Widget`) or this repo name.
4. Show the inferred `workspace_name` and the exact two queries to the user and ask them to confirm or correct before running any search. The brand string materially changes the SERP, so do not guess silently.

## Sheet contract

The workflow creates a brand-new spreadsheet (it never appends to an existing one). The single working tab uses this header row:

```text
Site | Mention
```

- `Site` — the external page that ranked for the brand. Write the full result URL.
- `Mention` — the single paragraph from that page that talks about the brand, as extracted in step 03. One page per row.

## Mention quality rules

These apply to every `Mention` before it is written, in step 03:

- Keep exactly one paragraph per page: the one that most directly describes or characterizes the brand (what they are, what they do, a claim/opinion about them). Prefer a paragraph that names the brand.
- Quote the page's own words. Lightly trim to a clean paragraph (collapse whitespace, drop trailing nav/boilerplate); do not paraphrase, summarize, translate, reorder, stitch together, or invent text.
- **Verbatim is mandatory and verified, not trusted.** After the model returns a `mention`, the workflow must confirm it is a contiguous substring of the rendered page text (whitespace-normalized on both sides) before writing it. If it is not an exact span of the page, it is treated as a failed extraction — see step 03. The model selects which paragraph; it never authors the text.
- Strip cookie banners, nav chrome, "related articles" lists, and scrape-error text.
- If the page clearly ranks for the brand but no paragraph actually mentions or describes the brand (e.g. an unrelated page that merely contains the word), write `Mention = (no relevant paragraph found)` rather than forcing an unrelated quote. Still keep the row so the gap is visible.
- Cap length at ~1200 characters; if the natural paragraph is longer, keep the leading, brand-relevant portion.

## Run order

Run these child skills in order:

1. [01-config-and-sheet/SKILL.md](01_config_and_sheet/SKILL.md) — resolve `workspace_name`, workspace domains, and Drive folder; create the new `Site | Mention` sheet in that folder.
2. [02-serp-collection/SKILL.md](02_serp_collection/SKILL.md) — run the two brand SERPs (up to position `max_results`), merge, dedupe, and drop owned-domain results to produce `external_results`.
3. [03-extract-and-append/SKILL.md](03_extract_and_append/SKILL.md) — render each external page with local Playwright, extract the relevant paragraph, and append each `Site | Mention` row to the sheet as soon as it is found.

Append rows incrementally as each page is processed. Do not hold mentions in memory and write them only at the end of the run.

The end state is a new Google Sheet in the workspace Drive folder with one `Site | Mention` row per external page (up to two queries × position 50, deduped). No website pages are edited.

Pages that end up as `(No data)` because they could not be scraped (e.g. bot walls on review-aggregator or finance hosts) are expected. Surface them in the final summary as candidates that **might need manual content scraping**, so a human can capture the brand mention the automated render missed.

## Logging template

```text
[run-debug] workflow=_workflows/external_linter | START | workspace={workspace_slug} workspace_name="{workspace_name}"
[run-debug] workflow=_workflows/external_linter | SHEET | created spreadsheet_id={id} folder={folder_id}
[run-debug] workflow=_workflows/external_linter | SERP | query="..." results=N kept=N dropped_owned=N
[run-debug] workflow=_workflows/external_linter | MERGE | external_results=N
[run-debug] workflow=_workflows/external_linter | FETCH | url=... status=... chars=N
[run-debug] workflow=_workflows/external_linter | FETCH_RETRY | url=... attempt=N status=... chars=N reason=...
[run-debug] workflow=_workflows/external_linter | EXTRACT | url=... mention_chars=N
[run-debug] workflow=_workflows/external_linter | VERIFY | url=... verbatim={true|false}
[run-debug] workflow=_workflows/external_linter | APPEND | url=... row=N
[run-debug] workflow=_workflows/external_linter | DONE | rows=N pages_failed=N needs_manual_scrape=N sheet={url}
```

## Checklist

```text
Task Progress:
- [ ] workspace_slug and workspace_name confirmed
- [ ] workspace domains and Drive folder resolved
- [ ] Google access token refreshed
- [ ] [01-config-and-sheet/SKILL.md](01_config_and_sheet/SKILL.md) completed (new sheet created)
- [ ] [02-serp-collection/SKILL.md](02_serp_collection/SKILL.md) completed
- [ ] [03-extract-and-append/SKILL.md](03_extract_and_append/SKILL.md) completed
- [ ] Final summary includes row count, failed pages, and the new sheet URL
- [ ] Final summary flags `(No data)` / unscrapable pages that might need manual content scraping
```
