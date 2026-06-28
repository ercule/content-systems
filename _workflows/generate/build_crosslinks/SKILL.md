---
name: build_crosslinks
description: >-
  Build the runtime crosslink list for an update_agent run by merging the workspace's
  crosslinks.json with the SerpAPI top 10 organic results for the page's target
  keyword (filtering out anything older than 1 year).
"last updated": 2026-06-01T00:57:13+00:00
"last run": 2026-06-01T00:57:13+00:00
---

# Build crosslinks (shared)

Step 0: Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) (workflow standards: runtime HTTP, logging, ephemeral rules).

## Inputs

- `workspace_root` — required. Path to this repo (this repository's root).
- `source_html` or `source_markdown` — required. From [../../ops/fetch_url_html/SKILL.md](../../ops/fetch_url_html/SKILL.md).
- `source_title` — required. Used as a fallback for keyword inference.
- `source_url` — required. The page being updated.
- `target_keyword` (optional) — if not supplied, infer per the rules below.

## Outputs

- `target_keyword` — string (2 or 3 words, lowercase).
- `crosslinks` — array of `{ url, anchors[], source }`. `source` is `"workspace_file"` or `"serp"`.
- `crosslinks_text` — a plain-text rendering of `crosslinks` suitable for inlining into a Gemini prompt.

## 1. Ensure workspace crosslinks.json exists

If `<workspace_root>/crosslinks.json` does not exist, run [../init_crosslinks_json/SKILL.md](../init_crosslinks_json/SKILL.md) with `workspace_root` and `site_url` (derived from `source_url`'s scheme + host).

Read `<workspace_root>/crosslinks.json` and treat it as the base crosslinks list.

## 2. Infer target_keyword (if not supplied)

Pick the 2 or 3 words that best describe the page's primary topic. Choose in this order:

1. The page's first `<h1>` text (strip site name suffixes like `" | Brand"`).
2. `og:title`.
3. `<title>`.
4. `source_title`.

Then squeeze it down: lowercase; remove brand names that match the host; remove stop words (`the`, `a`, `an`, `to`, `for`, `of`, `and`, `or`, `with`, `on`, `in`, `is`, `what`, `how`, `your`, `you`); keep the 2 or 3 most informative remaining words in their original order. If only 1 word remains, that is fine — log `target_keyword_words=1` and continue.

Log `target_keyword=<value> source=<h1|og|title|source_title>`.

## 3. SerpAPI top 10

`GET https://serpapi.com/search` with params:

- `engine=google`
- `q={target_keyword}`
- `num=10`
- `api_key={serpapi.api_key}` from `./credentials.json` (resolved at `workspace_root`) (`serpapi.api_key`).

Use the first 10 organic results that have a usable `link` and a `title`. Drop:

- Results whose host equals the host of `source_url` (no self-links).
- Results whose `link` equals `source_url` exactly.

## 4. Freshness filter (≤ 1 year old)

For each candidate, determine a `published_at` timestamp:

1. SerpAPI result `date` field, if present and parseable.
2. Else `GET` the URL (60s timeout, browser-like UA), parse HTML and read the first available of:
   - `<meta property="article:published_time">`
   - `<meta property="og:updated_time">`
   - `<meta property="article:modified_time">`
   - First `<time datetime="…">` element.
3. If none, treat `published_at` as unknown.

Drop the result when `published_at` is older than 365 days before today (UTC). Drop results with unknown `published_at` as well — fresh signal only.

Cap the kept SerpAPI results at 10. Log `serp_kept=N serp_dropped_age=X serp_dropped_unknown=Y`.

## 5. Merge

Build `crosslinks` array:

- Each entry from `crosslinks.json` → `{ url, anchors, source: "workspace_file" }`.
- Each kept SerpAPI result → `{ url, anchors: [result.title, target_keyword], source: "serp" }`.

Deduplicate by URL (case-insensitive host + path), preserving the first occurrence (so workspace_file entries win over serp).

## 6. Render `crosslinks_text`

For inclusion in the Gemini enhance prompt, render one entry per line:

```text
- {url} — anchors: {a1}; {a2}; {a3}
```

This is the value to substitute for `{crosslinks}` in the existing per-workspace `prompts/gemini_enhance_*.txt` files.

## Logging summary

```text
[run-debug] workflow=<caller> | crosslinks | target_keyword=<...> base=<count> serp_kept=<count> total=<count>
```
