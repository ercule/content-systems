---
name: update_agent_07_doc_handoff
description: >-
  Shared update agent step 7: upload the regenerated article to Google Drive
  via markdown_to_google_doc and optionally write the Doc URL to a Google Sheet (notify).
"last updated": 2026-06-28T23:30:00+00:00
"last run": never
---

# Update agent — 07 Doc handoff

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

## Doc upload

1. Assemble `markdown`: `enhanced_markdown` from step 05, then a `## Changes made` section with `change_summary_markdown`.
2. Set `doc_name` to `{source_title} (update)` unless the workspace overrides it.
3. Run [../../../ops/markdown_to_google_doc/SKILL.md](../../../ops/markdown_to_google_doc/SKILL.md) with:

- `markdown` — assembled body from step 1
- `doc_name`, `folder_id` — `drive_folder_id` from step 02
- `preset: update_agent_default` — metadata uses `source_url` and runtime date; include change summary in the body

Inputs from upstream steps for metadata and logging:

- `source_title`, `source_url`, `target_keyword`
- `crosslinks_added_count` — from step 04/05 logs
- `faq_added` — from `include_faq` and step 05 output

## Optional sheet notify

When `workflow_specific.update_agent.calendar.spreadsheet_id` is non-empty, run [../../../ops/write_google_sheet/SKILL.md](../../../ops/write_google_sheet/SKILL.md) using the **update_agent calendar preset** with `workspace_config`, `source_url`, `doc_url`, and optional `post_name` / `source_title`.

## End state

Report:

- `doc_url`
- `source_url`
- Reminder: run `{workspace_root}/_workflows/stage_content` with this Doc when ready to push a CMS draft (name the publish sub-skill from the routing table).

This workflow does not publish to the live site.

## Cleanup

Do not leave scratch Markdown, HTML dumps, or temp files under `{workspace_root}/tmp/`.
