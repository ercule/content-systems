---
name: update_agent_05_human_gate
description: >-
  Optional shared update agent step: present the change summary and wait for
  explicit user approval before Doc upload. Skip by default — review happens
  between the produce run and a separate content_staging run.
"last updated": 2026-06-21T00:00:00+00:00
"last run": never
---

# Update agent — 05 Human gate (optional)

Skip this step unless the user asks to preview changes before the Doc is created.

Step 0: Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md).

## Steps

1. Show the user `change_summary_markdown` from step 04.
2. Optionally show a short excerpt of the regenerated opening (first ~500 characters) — not the full body unless they ask.
3. Ask: proceed to create the review Google Doc?
4. Continue only on `y` or `yes` (case-insensitive). Stop on anything else.

Do not upload to Drive or write to any CMS before approval.

Next: [../06-doc-handoff/SKILL.md](../06_doc_handoff/SKILL.md)
