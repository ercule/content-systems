---
name: update_agent
description: >-
  Shared update agent: fetch an existing page, build crosslinks, fully regenerate
  the article (crosslinks woven in; FAQ optional), human gate, Google Doc handoff.
  Configure via workflow_specific.update_agent in config.json — do not patch CMS
  structures in place. Publishing is always a separate content_staging sub-skill.
"last updated": 2026-06-21T00:00:00+00:00
"last run": never
---

# Update agent (shared)

Step 0: Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) (workflow standards: runtime HTTP, logging, ephemeral rules).

Log line prefix:

`[run-debug] workflow=_workflows/update_agent | <PHASE> | <facts>`

## What this does

Refresh an existing live page by regenerating the full article body from scratch, then handing off a review Google Doc. The model weaves in internal crosslinks and may append an FAQ section when configured. We do not patch slices, spans, or partial HTML in the CMS — full regenerate only.

Publishing to WordPress, Webflow, Prismic, HubSpot, or any other CMS is never part of this workflow. After review, route through `{workspace_root}/_workflows/content_staging/SKILL.md` (add this skill when you publish to a CMS; see [setup/maintain_workflows/SKILL.md](../../../setup/maintain_workflows/SKILL.md)) to the correct publish sub-skill (`publish_wordpress_from_google_doc`, `google_doc_to_webflow`, Prismic migration PUT, etc.).

## Configuration

Run this shared skill from `_workflows/generate/update_agent/SKILL.md`. Set `workflow_specific.update_agent` in `{workspace_root}/config.json` (see below).

Optional: add a thin entry skill at `_workflows/{name}/SKILL.md` that resolves `workspace_root`, passes inputs, and links here — do not duplicate steps 03–06.

## Config block

In `{workspace_root}/config.json`:

```json
{
  "workflow_specific": {
    "update_agent": {
      "site_url": "https://example.com",
      "include_faq": true,
      "source_fetch_steps": [],
      "enhance_prompt_path": "",
      "diff_summary_prompt_path": "",
      "output_format": "markdown",
      "drive_folder_id": "",
      "calendar": {
        "spreadsheet_id": "",
        "tab": "",
        "url_match_column": "",
        "doc_url_column": "",
        "create_row_if_missing": false
      }
    }
  }
}
```

- `source_fetch_steps` — optional list of relative paths to workspace step skills that fetch the source and must output `source_url`, `source_title`, and `source_html` or `source_markdown`. When empty, step 02 uses [../../ops/fetch_url_html/SKILL.md](../../ops/fetch_url_html/SKILL.md) on a web URL from chat.
- `include_faq` — when `false`, step 04 must not add an FAQ section.
- `enhance_prompt_path` — required when the workspace supplies a custom Gemini/Anthropic prompt template. Template must instruct full-document output, not JSON patches or span edits.
- `output_format` — `markdown` (default) or `html`. Handoff step accepts either; [../update_doc_handoff/SKILL.md](../update_doc_handoff/SKILL.md) expects Markdown unless a workspace converter normalizes first.
- `calendar` — optional sheet notify preset; when `spreadsheet_id` is set, step 06 also runs [../../ops/google_sheet_write/SKILL.md](../../ops/google_sheet_write/SKILL.md) (update_agent calendar preset).

Read credentials from `{workspace_root}/credentials.json` only (resolve `@ref` per run_workflow).

## Run order

1. [01-config/SKILL.md](01_config/SKILL.md) — resolve workspace config, inputs, and credentials.
2. [02-fetch-source/SKILL.md](02_fetch_source/SKILL.md) — load the current page (shared or workspace fetch steps).
3. [03-build_crosslinks/SKILL.md](03_build_crosslinks/SKILL.md) — [../build_crosslinks/SKILL.md](../build_crosslinks/SKILL.md).
4. [04-regenerate/SKILL.md](04_regenerate/SKILL.md) — full article regenerate with crosslinks (and FAQ when enabled).
5. [06-doc-handoff/SKILL.md](06_doc_handoff/SKILL.md) — [../update_doc_handoff/SKILL.md](../update_doc_handoff/SKILL.md) and optional sheet notify row.

Step [05-human-gate/SKILL.md](05_human_gate/SKILL.md) is optional — use only when the user asks to preview changes before Doc upload. Default: upload the Doc and let the human choose when to run `{workspace_root}/_workflows/content_staging`.

## Invariants

- Full regenerate: the enhancement model returns a complete replacement article. No in-place CMS edits, no Prismic span indices, no partial DOM patches.
- Preserve identity: keep the same topic, URL/slug target, and brand voice. Wording may change; structure may be reorganized.
- Crosslinks: use the list from step 03; weave links into existing prose where natural.
- FAQ: when `include_faq` is true, append a clearly labeled FAQ section at the end of the regenerated body.
- Dated-year freshness: replace stale "now" year references (e.g. `in 2025`, `© 2025`) with the current calendar year from the runtime clock. Do not change historical or citation years.
- Default end state: Google Doc URL in the workspace Drive folder. No CMS write from this workflow.

## After this workflow

Tell the user to run `{workspace_root}/_workflows/content_staging` with the reviewed Doc when they want a CMS draft. The content_staging routing table must name the correct publish sub-skill.
