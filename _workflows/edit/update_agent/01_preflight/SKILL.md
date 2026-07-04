---
name: update_agent_01_preflight
description: >-
  Shared update agent step 1: verify config, credentials, paths, and inputs
  before fetch or model work.
"last updated": 2026-06-28T23:30:00+00:00
"last run": never
---

# Update agent — 01 Preflight

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

Stop with a clear error listing anything missing or broken. Do not continue to step 02 until preflight passes.

## Downstream inventory

| Step | Needs |
|------|--------|
| 02_config | Chat inputs; `{workspace_root}/config.json` |
| 03_fetch_source | `source_url` or workspace fetch steps; fetch_url or custom fetch |
| 04_build_crosslinks | Page body from fetch; SerpAPI for site-restricted results |
| 05_regenerate | Enhancement model (Gemini or Anthropic); optional prompt files |
| 07_doc_handoff | Google Drive upload; optional Sheets calendar notify |

## Validate configuration

1. Confirm `workspace_root` resolves to a directory containing `config.json`.
2. Read `workflow_specific.update_agent` from config. Stop if missing.
3. When `source_fetch_steps` is empty, require `source_url` from chat or wrapper.
4. When `enhance_prompt_path` or `diff_summary_prompt_path` is set, confirm each file exists under `{workspace_root}/_workflows/edit/update_agent/`.

## Probe credentials

Load `{workspace_root}/credentials.json` and resolve `@ref` per run_workflow.

| Secret / API | Required when | Probe |
|--------------|---------------|-------|
| `google.oauth_token_unified` | Always (Doc handoff) | Refresh token once (`POST {token_uri}`) |
| `serpapi.api_key` | crosslinks SerpAPI path | Present and non-empty |
| `anthropic.api_key` or Gemini equivalent | Regenerate step | Present per configured model |
| `drive_folder_id` | Doc upload | From config or credentials; non-empty |

When `calendar.spreadsheet_id` is set, confirm Google OAuth scopes cover Sheets write.

## Probe paths

- `source_url` — when required, `HEAD` or lightweight GET returns 2xx (follow one redirect).
- `drive_folder_id` — Drive `files.get` or folder metadata returns 2xx.

Log: `[run-debug] workflow=_workflows/update_agent | PREFLIGHT | ok workspace=… source=… drive=…`

Next: [../02_config/SKILL.md](../02_config/SKILL.md)
