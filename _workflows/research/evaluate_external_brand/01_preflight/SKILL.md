---
name: evaluate_external_brand_01_preflight
description: >-
  Step 01 for evaluate_external_brand: verify workspace config, credentials,
  and Drive folder before SERP or Playwright work.
"last updated": 2026-06-28T23:30:00+00:00
"last run": never
---

# Evaluate external brand — 01 Preflight

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

Stop with a clear error listing anything missing or broken. Do not continue to step 02 until preflight passes.

## Downstream inventory

| Step | Needs |
|------|--------|
| 02_config_and_sheet | Workspace config; Google Drive + Sheets create |
| 03_serp_collection | SerpAPI; confirmed `workspace_name` |
| 04_extract_and_append | Playwright render; Anthropic extraction |

## Validate configuration

1. Confirm `workspace_root` resolves to a directory containing `config.json`.
2. Resolve or confirm `workspace_name` before any search (see orchestrator).
3. Resolve `workspace_domains` or confirm they can be derived from config.
4. Resolve `drive_folder_id` from input or `google_drive_url` in config — must be non-empty.

## Probe credentials

| Secret | Probe |
|--------|-------|
| `google.oauth_token_unified` | Refresh once; scopes include Drive and Sheets |
| `serpapi.api_key` | Present and non-empty |
| `anthropic.api_key` | Present and non-empty |

Log: `[run-debug] workflow=_workflows/evaluate_external_brand | PREFLIGHT | ok workspace=…`

Next: [../02_config_and_sheet/SKILL.md](../02_config_and_sheet/SKILL.md)
