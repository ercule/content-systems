---
name: generate_topic_ideas_01_preflight
description: >-
  Step 01 for generate_topic_ideas: verify credentials, brand inputs, and
  output path before research or file writes.
"last updated": 2026-08-31T03:45:00+00:00
"last run": 2026-08-30
---

# Generate topic ideas — 01 Preflight

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

Stop with a clear error listing anything missing or broken. Stay on this step until preflight passes.

## Downstream inventory

- 02_research: SerpAPI; [fetch_url](../../../ops/fetch_url/SKILL.md); `brand_title`; `brand_domain`
- 03_draft_and_score: Anthropic; research notes from step 02
- 04_output: local markdown and JSON; `output_path`; topic rows from step 03

## Validate inputs

- `workspace_root`: when set, confirm `config.json` exists. When omitted, resolve per run_workflow.
- `brand_title`: required before step 02. Caller value, else `{workspace_root}/config.json` `workspace_name`. Confirm inferred names with the user.
- `brand_domain`: required before step 02. Caller value, else `{workspace_root}/config.json` `main_domain`, `domain`, or first `workspace_domains` host. Normalize to an apex host (lowercase, strip scheme, path, and a leading `www.`).
- `output_path`: optional. Default `{workspace_root}/_context/topic-ideas.md`. Confirm the parent directory exists, or create it.

Wipe `{workspace_root}/tmp/generate_topic_ideas/` at the start of this step, then create that folder for this run.

## Probe credentials

Load `{workspace_root}/credentials.json` when `workspace_root` is set; resolve `@ref` per run_workflow.

- `serpapi.api_key`: present and non-empty
- `anthropic.api_key`: present and non-empty

Log: `[run-debug] workflow=_workflows/generate_topic_ideas | PREFLIGHT | ok brand="{brand_title}" domain={brand_domain} output={output_path}`

Next: [../02_research/SKILL.md](../02_research/SKILL.md)
