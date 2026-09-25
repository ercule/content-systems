---
name: update_agent_07_doc_handoff
description: >-
  Shared update agent step 7: upload the original article to Google Drive,
  paint the step-05 markup plan via agent_editor, optionally write the Doc
  URL to a Google Sheet. No List of changes.
"last updated": 2026-09-20
P26-09-20
---

# Update agent — 07 Doc handoff

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

## Doc upload (original article only)

The Doc is a copy of the live article. Markup is the review surface. Never prepend List of changes. Never upload `enhanced_markdown` as a replacement body.

1. Assemble `markdown` (or `html_fragment`) from the **fetched original** (`source_markdown` or converted `source_html`). Start with `# {source_title}` when the body does not already include that H1.
2. Set `doc_name` to `{source_title} (update)` unless the workspace overrides it.
3. Run [../../../ops/markdown_to_google_doc/SKILL.md](../../../ops/markdown_to_google_doc/SKILL.md) with:

- `markdown` — original article only
- `doc_name`, `folder_id` — `drive_folder_id` from step 02
- `preset: update_agent_default` (Original URL + Generated metadata, then the original body)

Inputs from upstream for metadata and logging:

- `source_title`, `source_url`, `target_keyword`
- `markup_plan` from step 05

## Match plan against the Doc

`old` strings must exist in the uploaded Doc (visible text after Markdown/HTML import).

1. Export or `documents.get` the new Doc.
2. For each `replaces` / `styled_replaces` `old`, each `insert_after` anchor, each `strike_only` string, and each `insert_section(s).insert_before`: confirm it appears. Normalize only trivial whitespace if needed.
3. If any needle is missing, stop with the failing snippet. Do not paint a partial plan. Do not invent a different `old`.
4. Write the verified plan to `{workspace_root}/tmp/inline-markup-plan.json`.

## Paint markup (agent_editor)

Run [../../../ops/agent_editor/SKILL.md](../../../ops/agent_editor/SKILL.md) against the new Doc:

```bash
python3 {content_systems_public}/scripts/google_doc/apply_inline_doc_markup.py \
  "{doc_url}" \
  --plan {workspace_root}/tmp/inline-markup-plan.json \
  --workspace {workspace_root}
```

Do not run [accept_agent_edits](../../../ops/accept_agent_edits/SKILL.md) in this step.

## Optional sheet notify

When `workflow_specific.update_agent.calendar.spreadsheet_id` is non-empty, run [../../../ops/write_google_sheet/SKILL.md](../../../ops/write_google_sheet/SKILL.md) using the **update_agent calendar preset** with `workspace_config`, `source_url`, `doc_url`, and optional `post_name` / `source_title`.

## End state

Report:

- `doc_url`
- `source_url`
- Reminder: review red/blue markup in the Doc, then run [accept_agent_edits](../../../ops/accept_agent_edits/SKILL.md). After accept, run `{workspace_root}/_workflows/stage_content` when ready to push a CMS draft. Stage/publish must refuse remaining red/blue markup.

This workflow does not publish to the live site.

## Cleanup

Delete `{workspace_root}/tmp/inline-markup-plan.json` after a successful apply unless the caller asked to keep it. Do not leave scratch Markdown or HTML dumps under `{workspace_root}/tmp/`.
