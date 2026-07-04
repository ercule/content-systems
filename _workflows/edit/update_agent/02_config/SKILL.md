---
name: update_agent_02_config
description: >-
  Shared update agent step 2: resolve workspace_root, source URL, FAQ flag, fetch
  steps, prompt paths, and Drive folder from workspace config and credentials.
"last updated": 2026-06-28T23:30:00+00:00
"last run": never
---

# Update agent — 02 Config

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

## Inputs (from chat or workspace wrapper)

- `workspace_root` — required. Path to the repo root (this repository's root).
- `source_url` — required unless workspace fetch steps derive it (e.g. WP slug flow).
- `include_faq` — optional override of config default.
- `target_keyword` — optional; passed through to crosslinks when supplied.

## Steps

1. Resolve `workspace_root` from chat input.
2. Read `{workspace_root}/config.json` → `workflow_specific.update_agent`. Stop if missing; the workspace wrapper must document how to add it.
3. Load credentials from `{workspace_root}/credentials.json` (resolve `@ref` per run_workflow).
4. Resolve `drive_folder_id` from config, else credentials, else stop and ask.
5. Resolve `include_faq` from chat override, else config (default `true`).
6. Resolve `source_fetch_steps` from config (may be empty).
7. Resolve `enhance_prompt_path` and `diff_summary_prompt_path` relative to `{workspace_root}/_workflows/edit/update_agent/` when set.
8. Log `[run-debug] workflow=_workflows/update_agent | CONFIG | workspace=… include_faq=… fetch_steps=N`.

## Outputs (carry forward)

- `workspace_root`, `source_url`, `include_faq`, `target_keyword`
- `source_fetch_steps`, `enhance_prompt_path`, `diff_summary_prompt_path`, `output_format`
- `drive_folder_id`, merged credentials, `calendar` block when configured

Next: [../03_fetch_source/SKILL.md](../03_fetch_source/SKILL.md)
