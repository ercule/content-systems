---
name: generate_article_01_preflight
description: >-
  Step 01: verify config, Drive folder, Google OAuth, a writing model, and run
  inputs before context or research work.
"last updated": 2026-08-16T05:30:00+00:00
"last run": 2026-08-23
---

# Generate article — 01 Preflight

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

Read the orchestrator [../SKILL.md](../SKILL.md). List every missing or broken check, then end the run. Start [../02_context_pack/SKILL.md](../02_context_pack/SKILL.md) only after every check passes. This step's next step is always 02.

## Downstream inventory

- 02_context_pack: `_context/`; [sync_assets](../../../../setup/sync_assets/SKILL.md); creates or reuses `RUN_DIR`
- 03_research: `site_url`; [fetch_url](../../../ops/fetch_url/SKILL.md)
- 04_package_prompt: files from 02 and 03
- 05_draft: `prompt-pack.md` and `prompt-pack.approved` in the run folder
- 06_components: manuscript; `components` list from config
- 07_mechanical_rewrite: manuscript after components
- 08_output: final Markdown; `drive_folder_id`; [markdown_to_google_doc](../../../ops/markdown_to_google_doc/SKILL.md)

## Validate configuration

1. Walk up from this skill until you find `config.json`. That folder is the workspace root.
2. Read `workflow_specific.generate_article` from the orchestrator config list. End the run if the block is missing.
3. `site_url` and `drive_folder_id` must be non-empty.
4. Use `target_word_count` 1200 and `min_first_party_links` 7 when those keys are omitted.
5. `components` values must be from this list: `key_takeaways`, `faqs`, `categories`. Use `key_takeaways` and `faqs` when the key is omitted.

## Validate inputs

Need one of: `run_dir`, `id-or-slug`, or `title` (to derive the slug). Optional: `specific_context` (facts, angle, or pasted sources). Optional: `target_keyword` (otherwise derive from `title`).

When the user omits `id-or-slug`, derive it as kebab-case from `title`.

Find the candidate folder:

1. If `run_dir` is supplied, that folder is the candidate.
2. Else look under `tmp/generate_article/{id-or-slug}/`. If several timestamp folders exist, use the newest that contains `prompt-pack.md`.

Reuse (candidate contains `prompt-pack.md` and `prompt-pack.approved`):

- Set `RUN_DIR` to that folder so step 02 can reuse it.
- If `title` is omitted, read it from `RUN_DIR/run-status.md`.

Awaiting approval (candidate contains `prompt-pack.md` and no `prompt-pack.approved`):

- Report `status=awaiting_prompt_approval` and end this run. Do not start 05. Do not start 02.

New pack (no candidate, or the candidate has no `prompt-pack.md`):

- `title` must be present. Step 02 will create `RUN_DIR`.

This step never starts 05. After a pass, next is always 02.

## Probe credentials

Load `credentials.json` at the workspace root and resolve `@ref` per run_workflow. Shapes: [credentials.example.json](../../../../setup/credentials.example.json).

- `google.oauth_token_unified`: always (Doc upload). Probe: refresh token once (`POST {token_uri}`)
- `anthropic.api_key` or `gemini.api_key`: draft and rewrite. Probe: present for the model named in `config.json`

## Probe paths

- `{content_systems_public_root}` resolves (this repo, or `config.json` → `content_systems_public.path`).
- `_context/` exists at the workspace root.
- `site_url` — `HEAD` or a light GET returns 2xx (follow one redirect).
- `drive_folder_id` — Drive folder metadata returns 2xx.

## Run folder

New pack: [../02_context_pack/SKILL.md](../02_context_pack/SKILL.md) creates `RUN_DIR`.

Reuse: `RUN_DIR` is the candidate folder (supplied `run_dir`, or the newest pack folder for this slug).

Log: `[run-debug] workflow=_workflows/generate/generate_article | PREFLIGHT | ok workspace=… slug=… run_dir=… mode=new|reuse`

Next: [../02_context_pack/SKILL.md](../02_context_pack/SKILL.md)
