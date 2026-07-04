---
name: update_agent_03_fetch_source
description: >-
  Shared update agent step 3: load the current page as HTML or Markdown via
  fetch_url or workspace-specific fetch steps declared in config.
"last updated": 2026-06-28T23:30:00+00:00
"last run": never
---

# Update agent — 03 Fetch source

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

## Required outputs

Every fetch path must produce:

- `source_url` — canonical page URL.
- `source_title` — human title string.
- `source_html` or `source_markdown` — full main-body content of the page (not a single slice or excerpt).

## Path A — default (no workspace fetch steps)

When `source_fetch_steps` is empty:

1. Run [../../../ops/fetch_url/SKILL.md](../../../ops/fetch_url/SKILL.md) with `input = source_url`.
2. Set `source_html` from `content_html`, `source_title` from `source_title`.

If the workspace site needs a CSS selector, pass `content_selector` from config when present.

## Path B — workspace fetch steps

When `source_fetch_steps` lists one or more workspace step skills (e.g. WordPress REST or Prismic CDN):

1. Run each step in order from `{workspace_root}/_workflows/edit/update_agent/`.
2. The last step must emit the required outputs above.
3. Do not fetch only one Prismic slice or one WordPress excerpt — the full article body the publish workflow will overwrite.

## Normalization

- If only HTML is available, convert to Markdown in-session for step 05 when `output_format` is `markdown`, or keep HTML when the workspace enhance prompt expects HTML.
- Log `fetch_kind`, `source_url`, and content length.

Next: [../04_build_crosslinks/SKILL.md](../04_build_crosslinks/SKILL.md)
