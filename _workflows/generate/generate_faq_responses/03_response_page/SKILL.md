---
name: generate_faq_responses_03_response_page
description: >-
  Step 03: resolve Response Page URL for each target row.
"last updated": 2026-06-28T23:30:00+00:00
"last run": never
---

# Generate FAQ responses — 03 Response page

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

For each target row, set `response_page_url`:

- **GSC** — reuse page from `source` (`GSC {page_url}`).
- **Reddit / LinkedIn** — when `main_domain_host` is set, SerpAPI `{question} site:{main_domain_host}`; take top organic on that host. Blank when none.
- **`main_domain_host` null** — leave blank for Reddit/LinkedIn.

Carry forward per row: `row_number`, `topic`, `question`, `source`, `response_page_url`, `source_type`.

Next: [../04_draft_response/SKILL.md](../04_draft_response/SKILL.md)
