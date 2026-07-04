---
name: evaluate_external_brand_04_extract_and_append
description: >-
  Step 04 for evaluate_external_brand: fetch each external page, extract the
  single paragraph that talks about the brand, and append one Site | Mention
  row per page to the new sheet as it is found.
"last updated": 2026-06-28T23:30:00+00:00
"last run": 2026-06-09
---

# Evaluate external brand - 03 Extract And Append

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

## Inputs

From [../03_serp_collection/SKILL.md](../03_serp_collection/SKILL.md):

- `external_results` — array of `{ url, title, snippet, best_position, queries }`.
- `workspace_name`
- `spreadsheet_id`, `tab_title`, `sheet_url`

From chat or caller:

- `linter_model` — optional. Default `claude-sonnet-4-6` (root `config.json` at `anthropic.model_smart`). Must be on the permitted list in root `config.json`.

## Credentials

- Google OAuth for Sheets: `{workspace_root}/credentials.json` at `google.oauth_token_unified`.
- Anthropic: `{workspace_root}/credentials.json` at `anthropic.api_key`, used for paragraph extraction.

Do not log API keys, OAuth tokens, raw page bodies, or full model prompts.

Process pages incrementally. For each external result, fetch → extract → append before moving to the next. Do not collect every mention first and append once at the end; this keeps partial progress visible if the run fails.

## 1. Fetch the page (local Playwright — the only path)

For each `external_results` entry, in order, render the page with a local Playwright Chromium browser and extract `document.body.innerText` after the page has had time to hydrate. This is the **only** fetch path: there is no shared-skill fetch, no `curl` fallback, and no SERP-snippet fallback.

Use a local Playwright runtime. If Playwright is not already available, create an ephemeral virtualenv or temporary package install for the run, install Playwright and Chromium, and remove the temporary files before finishing. Do not commit runner scripts, package manifests, browser caches, or other generated artifacts.

### Runtime setup (load-bearing — this is where runs actually break)

These came out of real failed runs; skipping them wastes 10+ minutes per attempt:

- **Install and run the browser in the same execution mode / architecture.** If install runs under a sandbox or translation layer (e.g. Rosetta reporting `x86_64`) but the run executes natively (`arm64`), Playwright downloads the wrong-arch browser and launch fails with "Executable doesn't exist at …-mac-arm64/…". Run the browser install in the *same* unsandboxed, native-arch context you will launch from. Confirm with `arch` / `python -c "import platform; print(platform.machine())"` before installing.
- **Launch with `--no-sandbox --disable-dev-shm-usage`.** Without `--no-sandbox`, Chromium's own sandbox often fails to initialize in this environment and `chromium.launch` hangs until the 180s timeout instead of erroring. This is the single most common cause of a "stuck" run.
- **Install `chromium-headless-shell` too**, not just `chromium`; the headless shell is what actually launches here.
- **Smoke-test before the full run.** Launch once and load `https://example.com`; only proceed to the 50+ page loop once that prints a non-trivial `innerText` length. Cheap insurance against a long browser download followed by an immediate launch failure.

Recommended browser context:

```python
browser = await playwright.chromium.launch(
    headless=True,
    args=["--no-sandbox", "--disable-dev-shm-usage"],
    timeout=60000,
)
context = await browser.new_context(
    user_agent=(
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/149.0.0.0 Safari/537.36"
    ),
    locale="en-US",
    viewport={"width": 1366, "height": 900},
    extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
)
```

For each URL:

1. Attempt the primary render: `page.goto(url, wait_until="domcontentloaded", timeout=30000)`.
2. Try `page.wait_for_load_state("networkidle", timeout=8000)`, but continue if this times out.
3. Wait an additional short hydration delay (~1500ms).
4. Read `document.body.innerText`.
5. Collapse repeated blank lines while preserving page order.

If the primary attempt returns a transient navigation error, a timeout, a non-2xx response, or an empty/thin rendered body (under ~200 chars of text, i.e. a JS shell or bot wall), retry with Playwright before giving up:

1. Retry once in a fresh page in the same browser context after a short backoff (~2s), using `wait_until="load"` and a longer navigation timeout (~45000ms).
2. If the retry is still thin or fails, retry once more in a fresh incognito context with the same desktop user agent and headers.
3. Keep the best rendered body across attempts. If any attempt produces a 2xx response and >=200 chars of text, use that body for extraction.
4. If all attempts fail, record the page in `failed_pages` with `url`, final `status`, `chars`, `attempts`, and a short `reason`, then write `Mention = (No data)`.

Do not substitute the search snippet, `curl` HTML, or any other source as a fallback — Playwright-rendered page text is the only source allowed for verbatim mentions.

Expect a handful of `403` bot walls on every brand SERP. Review-aggregator and finance hosts reliably block headless Chromium — observed on `g2.com`, `capterra.com`, `trustpilot.com`, and `seekingalpha.com`. These are normal `(No data)` rows after the bounded retries above, not a runtime bug; don't burn time retrying them further.

Log:

```text
[run-debug] workflow=_workflows/evaluate_external_brand | FETCH | url=... status=... chars=N
[run-debug] workflow=_workflows/evaluate_external_brand | FETCH_RETRY | url=... attempt=N status=... chars=N reason=...
```

## 2. Extract the relevant paragraph

Use the rendered `document.body.innerText` from step 1 and call the configured `linter_model` once per page to pull the single most relevant paragraph.

Prompt contract:

```text
You are auditing how external websites describe a company called "{workspace_name}".

From the page text below, return the SINGLE paragraph that most directly
describes or characterizes {workspace_name} — what it is, what it does, or a
claim/opinion about it. Prefer a paragraph that names {workspace_name}.

Return JSON only:
{ "mention": "the exact paragraph text", "mentions_brand": true }

Rules:
- Copy an exact, unmodified span of the page text character for character. Do not paraphrase, summarize, translate, fix grammar/spelling, reorder, or stitch sentences from different places. The returned text must appear verbatim in the page.
- Return exactly one paragraph (you may trim surrounding boilerplate/nav/whitespace).
- Ignore cookie banners, navigation, "related articles" lists, ads, and scrape-error text.
- If no paragraph actually describes or mentions {workspace_name}, set "mentions_brand" to false and return "mention": "".

Page title: {page_title}
Page text (top to bottom):
<<<
{page_text}
>>>
```

Parse the response as JSON. Models often wrap JSON in Markdown fences or add a sentence first: before parsing, strip surrounding fences and take the substring from the first `{` to the last `}`. Do not `JSON.parse` the raw response directly.

If parsing fails, retry once with a short output-repair prompt. If it still fails, treat the page as no mention found and log the first 500 characters of the response.

### Verbatim verification (required gate)

The model only *selects* the paragraph; it must never *author* it. Before a mention is allowed onto the sheet, confirm it is an exact span of the page:

1. Normalize both strings the same way: collapse every run of whitespace (spaces, tabs, newlines) to a single space and trim. Do not lowercase, strip punctuation, or alter characters — normalization is whitespace only.
2. Check that the normalized `mention` is a contiguous substring of the normalized rendered `document.body.innerText` from step 1.
3. If it is **not** a substring, the model paraphrased, translated, fixed grammar, or stitched text together. Retry once with a repair instruction: "Return only an exact, unmodified span of the page text — copy it character for character, do not edit it." Re-run the same substring check on the retry.
4. If the retry still fails the substring check, do not write the model's text. Set the cell to `(No data)` and record the page in `failed_pages` with reason `non_verbatim`.

Only mentions that pass this check (or the explicit `(...)` placeholders) are written. The cell value is taken from the page text span, not re-emitted by the model.

Expect a non-trivial share of `non_verbatim` results — roughly a quarter of fetched pages in practice — and don't treat them as a bug. Review-aggregator, vendor-profile, and Q&A pages (e.g. Gartner, Quora, Atlassian Marketplace, company-profile roundups) render the brand description as fragmented list items, star ratings, and stitched UI text, so there is often no single contiguous paragraph to quote. The gate correctly rejects the model's reconstructed sentence and writes `(No data)`. That is the gate doing its job, not a failure to fix.

Log:

```text
[run-debug] workflow=_workflows/evaluate_external_brand | VERIFY | url=... verbatim={true|false}
```

Apply the [Mention quality rules](../SKILL.md#mention-quality-rules):

- Use the verified page-text span (trimmed and whitespace-collapsed), capped at ~1200 characters (keep the leading brand-relevant portion if longer). When you cap a long paragraph, only truncate — never add or alter characters, so the cell stays an exact prefix of the page span.
- If `mentions_brand` is false or `mention` is empty, set the cell to `(no relevant paragraph found)`. Still write the row so the gap is visible.
- If the mention failed the verbatim verification gate above, set the cell to `(No data)`. Still write the row.
- If the page could not be fetched after the bounded Playwright retries in step 1, set the cell to `(No data)`. Keep the detailed fetch reason in `failed_pages`; do not fall back to the search snippet.

Log:

```text
[run-debug] workflow=_workflows/evaluate_external_brand | EXTRACT | url=... mention_chars=N mentions_brand={true|false}
```

## 3. Append the row as you go

Right after extracting a page's mention, append one row to the sheet, then move on to the next page. Do not batch to the end.

```http
POST https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{encodedRange}:append?valueInputOption=RAW&insertDataOption=INSERT_ROWS
Authorization: Bearer {access_token}
Content-Type: application/json
```

Use an encoded range covering the two output columns, e.g. `'{tab_title}'!A:B`. Body:

```json
{ "values": [["{url}", "{mention}"]] }
```

- `Site` (column A) = the external page `url`.
- `Mention` (column B) = the extracted paragraph, `(no relevant paragraph found)`, or `(No data)`.

If an append call fails, log it, keep the row in `failed_appends`, and continue with the next page rather than aborting.

Log:

```text
[run-debug] workflow=_workflows/evaluate_external_brand | APPEND | url=... row=N
```

## Outputs

Return:

- `rows_written`
- `pages_failed` (fetch failures)
- `failed_appends`, if any
- `sheet_url`

## Final summary

Report to the user: rows written, pages that failed to fetch, and the new sheet URL.

If any pages were written as `(No data)` because they could not be scraped (entries in `failed_pages`), call this out explicitly in the summary: list those page URLs and note that they **might need manual content scraping** to capture the brand mention the linter could not extract automatically. Keep this separate from `(no relevant paragraph found)` rows, which are pages that scraped fine but genuinely had no relevant paragraph.

```text
[run-debug] workflow=_workflows/evaluate_external_brand | DONE | rows=N pages_failed=N needs_manual_scrape=N sheet={sheet_url}
```

## Checks

- [ ] Each external page fetched (or recorded in `failed_pages`).
- [ ] Fetch failures retried with Playwright before writing `(No data)`.
- [ ] Model responses parsed or safely handled; one paragraph per page.
- [ ] Every written mention passed the substring verbatim check against the rendered page text (whitespace-normalized); paraphrased extractions rejected.
- [ ] Mentions are verbatim page text, trimmed and capped; no paraphrasing.
- [ ] Pages with no real mention written as `(no relevant paragraph found)`; non-verbatim extractions written as `(No data)`.
- [ ] One `Site | Mention` row appended per page, incrementally.
- [ ] Final summary includes row count, failed pages, and the sheet URL.
- [ ] Summary flags `(No data)` pages that might need manual content scraping.
- [ ] No temporary files left behind.
