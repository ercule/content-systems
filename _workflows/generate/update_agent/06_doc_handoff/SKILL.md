---
name: update_agent_06_doc_handoff
description: >-
  Shared update agent step 6: upload the regenerated article to Google Drive
  via update_doc_handoff and optionally write the Doc URL to a Google Sheet (notify).
"last updated": 2026-06-21T00:00:00+00:00
"last run": never
---

# Update agent — 06 Doc handoff

Step 0: Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md).

## Doc upload

Run [../../update_doc_handoff/SKILL.md](../../update_doc_handoff/SKILL.md) with:

- `enhanced_markdown` — from step 04 (convert HTML to Markdown first when needed)
- `change_summary_markdown`
- `source_title`, `source_url`, `target_keyword`
- `crosslinks_added_count` — count from step 03/04 logs
- `faq_added` — boolean from `include_faq` and whether FAQ content exists in output
- `drive_folder_id` from step 01

## Optional sheet notify

When `workflow_specific.update_agent.calendar.spreadsheet_id` is non-empty, run [../../../ops/google_sheet_write/SKILL.md](../../../ops/google_sheet_write/SKILL.md) using the **update_agent calendar preset** with `workspace_config`, `source_url`, `doc_url`, and optional `post_name` / `source_title`.

## End state

Report:

- `doc_url`
- `source_url`
- Reminder: run `{workspace_root}/_workflows/content_staging` with this Doc when ready to push a CMS draft (name the publish sub-skill from the routing table).

This workflow does not publish to the live site.
