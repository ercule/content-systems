---
name: init_crosslinks_json
description: >-
  Bootstrap a workspace crosslinks.json from the live site's main navigation.
  Used by build_crosslinks when no crosslinks.json exists at the workspace root.
"last updated": 2026-06-01T00:58:47+00:00
"last run": 2026-06-01T00:58:47+00:00
---

# Initialize crosslinks.json (shared)

Step 0: Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) (workflow standards: runtime HTTP, logging, ephemeral rules).

## When to run

Called by `_workflows/generate/build_crosslinks/SKILL.md` when `<workspace_root>/crosslinks.json` is missing. Can also be invoked directly to refresh a workspace seed list.

## Inputs

- `workspace_root` — required. Path to this repo (this repository's root).
- `site_url` — required. The site homepage to scan, e.g. `https://acme.com/`. If not supplied by the caller, infer from the active update agent's `source_url` (use the URL's scheme + host with no path).

## What to write

Write `<workspace_root>/crosslinks.json` as a JSON array. Each entry:

```json
{
  "url": "https://example.com/products/foo",
  "anchors": ["Foo", "the Foo product"],
  "source": "site_nav",
  "added_utc": "YYYY-MM-DDTHH:MM:SSZ"
}
```

## Procedure

1. `GET site_url` with the same fetch posture as `_workflows/ops/fetch_url_html/SKILL.md` (browser-like UA, 60s timeout, follow at most one redirect).
2. Parse the response and gather `<a href>` elements that are descendants of any `<nav>`, `<header>`, or any element with role `navigation` / `menubar`. Include common nav containers like `[data-nav]`, `[class*="nav" i]`, `[class*="menu" i]`.
3. Resolve every `href` against `site_url` to an absolute URL. Drop:
   - Off-site links (different host).
   - Anchor-only / `mailto:` / `tel:` / `javascript:` links.
   - Obvious utility paths: `/blog`, `/blog/*`, `/login`, `/signup`, `/contact`, `/careers`, `/about`, `/privacy`, `/terms`, `/legal*`, `/pricing` (pricing optional — skip by default).
4. Keep links whose path matches any of:
   - `/product` or `/products` (with or without sub-path)
   - `/solutions`
   - `/platform`
   - `/use-cases` or `/use_cases`
   - `/features`
   - `/integrations`
5. For each kept URL, assemble `anchors`:
   - Visible link text (collapsed whitespace, trimmed).
   - Last path segment, hyphens → spaces, title-cased.
   - Deduplicate case-insensitively; keep at most 3 anchors per URL.
6. Deduplicate URLs (keep first occurrence). Cap the list at 30 entries; log if more were available.
7. Write the JSON pretty-printed (2-space indent), trailing newline, UTF-8.
8. Log `crosslinks_init=ok count=N path=<workspace_root>/crosslinks.json`.

## Empty result

If step 5 yields zero entries (e.g. site nav is JS-rendered and the static HTML has no anchors), write an empty array `[]` and log `crosslinks_init=empty reason=js-rendered-nav-or-no-matches`. The build_crosslinks step will still succeed by relying on SerpAPI top results alone.
