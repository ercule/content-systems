---
name: build_crosslinks
description: >-
  Build internal crosslink opportunities for page refresh: bootstrap
  crosslinks.json from site nav when missing, then select links for the target
  keyword (SerpAPI + workspace crosslinks.json).
"last updated": 2026-06-28T23:30:00+00:00
"last run": never
---

# Build crosslinks

Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) before running this step.

Log line prefix: `[run-debug] workflow=build_crosslinks | <PHASE> | <facts>`

## Inputs

- `workspace_root` — required.
- `source_html` or `source_markdown` — current page body from the caller.
- `source_title`, `source_url` — page identity.
- `target_keyword` — optional; infer from title or H1 when omitted.
- `site_url` — optional homepage for nav bootstrap; infer from `source_url` scheme + host when omitted.

## Outputs

- `target_keyword`
- `crosslinks` — structured list of `{url, anchor, source}` entries
- `crosslinks_text` — plain-text block for `{crosslinks_context}` in update_agent step 05

## Procedure

### 1. Bootstrap crosslinks.json when missing

When `<workspace_root>/crosslinks.json` does not exist, create it from the site main navigation before selecting links.

Write `<workspace_root>/crosslinks.json` as a JSON array. Each entry:

```json
{
  "url": "https://example.com/products/foo",
  "anchors": ["Foo", "the Foo product"],
  "source": "site_nav",
  "added_utc": "YYYY-MM-DDTHH:MM:SSZ"
}
```

Steps:

1. `GET site_url` with the same fetch posture as [_workflows/ops/fetch_url/SKILL.md](../../ops/fetch_url/SKILL.md) (browser-like UA, 60s timeout, follow at most one redirect).
2. Parse `<a href>` under `<nav>`, `<header>`, role `navigation` / `menubar`, and common nav containers (`[data-nav]`, `[class*="nav" i]`, `[class*="menu" i]`).
3. Resolve hrefs to absolute URLs on the same host. Drop off-site, anchor-only, mailto/tel/javascript, and utility paths (`/login`, `/blog`, `/privacy`, etc.).
4. Keep product/solutions/platform/use-case/feature/integration paths.
5. Assemble up to 3 deduped anchors per URL; cap at 30 URLs.
6. Write pretty-printed JSON. If zero matches, write `[]` and log `crosslinks_init=empty` — SerpAPI results can still supply links in step 2.

When the file already exists, skip bootstrap unless the caller asks to refresh the seed list.

### 2. Select crosslinks for the page

1. Load `<workspace_root>/crosslinks.json`.
2. Resolve `target_keyword` from input, title, or primary H1.
3. Rank entries relevant to the keyword and page topic; add SerpAPI site-restricted results when configured (`serpapi.api_key` in `{workspace_root}/credentials.json`).
4. Emit `crosslinks`, `crosslinks_text` (one line per opportunity: `- {anchor} → {url}`), and `target_keyword`.

Do not weave links into body copy here — update_agent step 05 does that.
