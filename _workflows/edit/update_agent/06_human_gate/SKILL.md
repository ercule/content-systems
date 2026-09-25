---
name: update_agent_06_human_gate
description: >-
  Optional shared update agent step: present the markup plan and wait for
  explicit user approval before Doc upload. Skip by default — review happens
  in the painted Google Doc, then accept_agent_edits, then stage_content.
"last updated": 2026-09-20
"last run": never
---

# Update agent — 06 Human gate (optional)

Skip this step unless the user asks to preview the plan before the Doc is created.

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

## Steps

1. Show the user a short inventory of `markup_plan` from step 05: replace count, insert_after count, insert_sections headings (FAQ questions, Related reading, CTA, and so on). Do not dump the full original article.
2. Ask: proceed to copy the original article into a Google Doc and paint this plan as red/blue markup?
3. Continue only on `y` or `yes` (case-insensitive). Stop on anything else.

Do not upload to Drive or write to any CMS before approval.

Next: [../07_doc_handoff/SKILL.md](../07_doc_handoff/SKILL.md)
