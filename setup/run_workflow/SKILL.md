---
name: utilities_run_workflow
description: >-
  Shared execution context for all workflow skills: runtime HTTP contract, context assembly,
  credential resolution, small-step runs
"last updated": 2026-06-21
"last run": 2026-06-14
---

## Context assembly

Before a workflow reads workspace positioning, brand rules, or approved copy, sync the local asset layer.

1. Find `workspace_root` — the folder that contains the active workflow's `config.json`. Walk up from the active `SKILL.md` until you find it.
2. Run [sync_assets/SKILL.md](../sync_assets/SKILL.md) with that `workspace_root`.
3. Read materialized copy from `{workspace_root}/_assets/`. Check `{workspace_root}/_assets/asset-manifest.md` for `last_updated` and `sync_status`.
4. Prefer `{workspace_root}/_context/` and `_assets/` over live URLs when material exists, unless the active skill says to pull fresh copy.

Skip context assembly when the skill does not read workspace reference material.

Log: `[run-debug] context-assembly | workspace={workspace_root} | assets={count} | warns={warn_count}`

## Execution rules

### 1. Build API calls at runtime

Construct each request (URL, method, headers, body) at execution time. Use curl or an equivalent HTTP client.

### 2. Break tasks into small steps

Prefer several narrow tool calls over one large call.

### 3. Run debugging

- Echo the active skill name, UID or doc ID, and fetch path.
- Echo credentials loaded: repository, custom type, model ID, and API host only. Do not echo secrets.
- For each HTTP request: echo method, host, path (omit secret query parts), status, and content-length when present.
- On HTTP errors: echo status and the first ~500 characters of the body.

### 4. Log timing

When supported, log elapsed seconds per gate: fetch, model call, validate, write.

### 5. Print a checklist (optional)

```text
[run-debug] CHECKLIST | context-assembly -> fetch -> transform -> validate -> write -> done
```

Adjust phases to match the active skill. Omit `context-assembly` when the skill does not use reference assets.

### 6. Browserbase live session (when using Browserbase)

If you create a Browserbase session for any step, read [_workflows/ops/browser_automation/SKILL.md](../../_workflows/ops/browser_automation/SKILL.md) and **repeat the live view URL conspicuously in every user message while the session is open** (see `.cursor/rules/browserbase-live-session.mdc`). Paste the URL block immediately before any login/handoff ask — not only once at the start.

## Credentials

All credential lookups start at `{workspace_root}/credentials.json`.

See [README.md § Organization principles](../../README.md#organization-principles).

### Reference syntax

A string value may point at another file:

```text
@relative/path/to/credentials.json#dotted.key.path
```

Example: `@credentials.json#google.oauth_token_unified`

- Paths are relative to `workspace_root`.
- Resolve reference strings before use. Follow nested references when needed.
- An inline object or string at the same JSON path overrides a reference.
- After resolution, treat the value as inline.

### Resolution procedure

1. Load `{workspace_root}/credentials.json`. If it is missing, copy from `credentials.example.json` after the user supplies values.
2. Walk the JSON tree. Replace each `@path#key` string with the resolved secret.
3. If a required key is still missing, ask the user, add it to `./credentials.json`, and run `git check-ignore credentials.json`.
4. Delete `./credentials.json` when it would be empty (no keys and no references).
5. Do not commit credential files. Do not log secret values.

Skills name the JSON path they need (for example `google.oauth_token_unified`, `webflow.api_token`). They do not list multiple credential file paths.

## Adding a new skill

If the skill is part of a workflow sequence, link this file as Step 0. From `_workflows/{category}/{name}/`, use `../../../setup/run_workflow/SKILL.md` (add one `../` per path segment to repo root). From `_workflows/{category}/{name}/{NN}_{step}/`, use `../../../../setup/run_workflow/SKILL.md`.

If the workflow has more than three steps, add a dedicated `01_preflight` step before other work. See [setup/maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md).

If the skill is a main workflow orchestrator, add a `"reacts to"` list in frontmatter for observable triggers only. See [setup/maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md).

Do not copy instructions that already live in another skill or `_context/` file. Link to the canonical copy instead.

## Ephemeral data

Store scratch files, run folders, debug traces, and pipeline intermediates only under a directory named `tmp/`. The path may live at the workspace root, under `_workflows/{category}/{name}/`, or under a step folder — but the directory name must be `tmp/`.

- Do not use `tmp/`, `tmp/`, or `debug/` for ephemeral data.
- Delete or wipe `tmp/` contents when the skill says to clean up.
- Do not commit files under `tmp/` (gitignored via `**/tmp/`).

## AI models

Only use models for which resolved credentials exist.

## End of run

1. Suggest improvements to any skills that ran.
2. Update `"last run"` in the front matter of every executed `SKILL.md`. Use ISO date `YYYY-MM-DD`.
3. If a skill is stale, offer to run setup/maintain_skills and setup/maintain_workflows.
