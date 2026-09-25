---
name: update_agent
description: >-
  Shared update agent: fetch an existing page, build crosslinks, plan
  surgical markup (crosslinks / FAQ / year freshness), copy the original
  article into a Google Doc, then paint red/blue agent_editor markup.
  Configure via workflow_specific.update_agent in config.json. Publishing
  is always a separate stage_content sub-skill after accept_agent_edits.
"last updated": 2026-09-20
P26-09-20
---

# Update agent (shared)

Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) before running this step.

Log line prefix:

`[run-debug] workflow=_workflows/update_agent | <PHASE> | <facts>`

## What this does

Refresh an existing live page by copying the **current article** into a new Google Doc, then painting today's work as [agent_editor](../../ops/agent_editor/SKILL.md) red-strikethrough / blue-addition markup. Reviewers see edits in place. There is no List of changes at the top of the Doc.

Typical edits: wrap existing phrases as internal crosslinks, append or improve FAQ when `include_faq` is true, replace stale "now" year references, plus any extras the workspace prompt names (Related reading, CTA, Key takeaways). Prefer wrap and insert over rewrite.

Publishing to WordPress, Webflow, Prismic, HubSpot, or any other CMS is never part of this workflow. After review, run [accept_agent_edits](../../ops/accept_agent_edits/SKILL.md), then `{workspace_root}/_workflows/stage_content/SKILL.md` (add this skill when you publish to a CMS; see [setup/maintain_workflows/SKILL.md](../../../setup/maintain_workflows/SKILL.md)).

## Configuration

Run this shared skill from `_workflows/edit/update_agent/SKILL.md`. Set `workflow_specific.update_agent` in `{workspace_root}/config.json` (see below).

Optional: add a thin entry skill at `_workflows/edit/update_agent/SKILL.md` that resolves `workspace_root`, passes inputs, and links here — do not fork shared steps 05 or 07.

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

- `source_fetch_steps` — optional list of relative paths to workspace step skills that fetch the source and must output `source_url`, `source_title`, and `source_html` or `source_markdown`. When empty, step 03 uses [../../ops/fetch_url/SKILL.md](../../ops/fetch_url/SKILL.md) on a web URL from chat.
- `include_faq` — when `false`, step 05 must not add an FAQ section.
- `enhance_prompt_path` — optional workspace prompt. Template must instruct a JSON **markup plan** (agent_editor schema), not a replacement article, JSON CMS patches, or span indices.
- `diff_summary_prompt_path` — unused for the review Doc (markup is the review surface). Leave empty.
- `output_format` — `markdown` (default) or `html`. Step 07 uploads the **original** body via [../../ops/markdown_to_google_doc/SKILL.md](../../ops/markdown_to_google_doc/SKILL.md); convert HTML to Markdown first unless a workspace converter supplies `html_fragment`.
- `calendar` — optional sheet notify preset; when `spreadsheet_id` is set, step 07 also runs [../../ops/write_google_sheet/SKILL.md](../../ops/write_google_sheet/SKILL.md) (update_agent calendar preset).

Read credentials from `{workspace_root}/credentials.json` only (resolve `@ref` per run_workflow).

## Run order

1. [01_preflight/SKILL.md](01_preflight/SKILL.md) — verify config, credentials, paths, and inputs.
2. [02_config/SKILL.md](02_config/SKILL.md) — resolve workspace config, inputs, and credentials.
3. [03_fetch_source/SKILL.md](03_fetch_source/SKILL.md) — load the current page (shared or workspace fetch steps).
4. [04_build_crosslinks/SKILL.md](04_build_crosslinks/SKILL.md) — [../../research/build_crosslinks/SKILL.md](../../research/build_crosslinks/SKILL.md).
5. [05_regenerate/SKILL.md](05_regenerate/SKILL.md) — markup plan JSON (`inline-markup-plan.json`).
6. [07_doc_handoff/SKILL.md](07_doc_handoff/SKILL.md) — upload the original article, run [agent_editor](../../ops/agent_editor/SKILL.md), optional sheet notify.

Step [06_human_gate/SKILL.md](06_human_gate/SKILL.md) is optional — use only when the user asks to preview the plan before Doc upload. Default: create the Doc, paint markup, and let the human review in Drive.

## Invariants

- Original Doc: step 07 uploads the fetched article as-is. Do not upload a regenerated replacement body. Do not prepend List of changes.
- Markup plan: step 05 returns agent_editor JSON only. Prefer `replaces` / `insert_after` / `insert_sections` over rewrite.
- Preserve identity: keep the same topic, URL/slug target, and brand voice. Do not rewrite paragraphs except the dated-year rule and workspace-prompt extras that insert missing sections.
- Crosslinks: use the list from step 04; wrap existing phrases.
- FAQ: when `include_faq` is true, append a clearly labeled FAQ when the page lacks one (or improve an existing FAQ in place via inserts).
- Dated-year freshness: replace stale "now" year references (e.g. `in 2025`, `© 2025`) with the current calendar year from the runtime clock. Do not change historical or citation years.
- Default end state: Google Doc URL in the workspace Drive folder, with red/blue markup still visible. No CMS write from this workflow. Do not run [accept_agent_edits](../../ops/accept_agent_edits/SKILL.md) unless the user asked to accept.

## After this workflow

1. Human reviews the Doc (red = deletion, blue = addition).
2. Run [accept_agent_edits](../../ops/accept_agent_edits/SKILL.md) when they want to keep the blue text.
3. Run `{workspace_root}/_workflows/stage_content` with the accepted Doc when they want a CMS draft. Stage/publish skills must refuse Docs that still have red/blue markup.
