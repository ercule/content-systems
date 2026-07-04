---
name: generate_faq_responses
description: >-
  Shared FAQ response generator. Fills Response Page and Draft Response columns on
  FAQ Coverage rows that already have Topic, Question, and Source (from
  find_faq_questions). Runs standalone or as a follow-on handoff.
"last updated": 2026-06-28T23:30:00+00:00
"last run": 2026-06-07
---

# Generate FAQ responses

Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) before running this step.

Second pass over `FAQ Coverage` rows with `Topic | Question | Source` filled by [find_faq_questions](../../research/find_faq_questions/SKILL.md). Fills optional columns only when they exist on the sheet:

- `Response Page` — main-domain page ranking for the question
- `Draft Response` — ~50-word recap of that page

Never edits website pages or writes `Topic`, `Question`, `Source`, `LLM Response`, `Mentioned`, `Topics`, or `% Mentioned`.

Log line prefix: `[run-debug] workflow=_workflows/generate_faq_responses | <PHASE> | <facts>`

## Inputs

- `sheet_url_or_id` — required
- `workspace_root` — optional; for `main_domain_host` and credentials
- `gsc_site_url`, `main_domain_host`, `finder_model` — optional (see step 02)
- `appended_rows_detail` — optional handoff from find_faq_questions step 05

## Run order

1. [01_preflight/SKILL.md](01_preflight/SKILL.md) — verify sheet access and credentials.
2. [02_resolve_targets/SKILL.md](02_resolve_targets/SKILL.md) — resolve tab, headers, and target rows.
3. [03_response_page/SKILL.md](03_response_page/SKILL.md) — resolve Response Page URL per row.
4. [04_draft_response/SKILL.md](04_draft_response/SKILL.md) — draft ~50-word answers from page text.
5. [05_write_cells/SKILL.md](05_write_cells/SKILL.md) — write optional columns and report counts.

## Outputs

- `response_pages_written`, `draft_responses_written`, `failed_response_writes`
