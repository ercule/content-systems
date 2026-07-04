---
name: utilities_run_workflow
description: >-
  Shared execution context for all workflow skills: runtime HTTP contract, context assembly,
  credential resolution, small-step runs
"last updated": 2026-07-04T23:00:00+00:00
"last run": 2026-07-04
---

Canonical execution contract for workflow skills. [README.md § Documentation map](../../README.md#documentation-map). When auditing skills, enforce skill-level rules from [maintain_skills/SKILL.md](../maintain_skills/SKILL.md).

## Architecture decisions (runtime)

These rules are fixed — do not invent alternate path variables or credential locations.

| Decision | Rule |
|----------|------|
| Workspace root | Folder containing `config.json`; walk up from active skill. Workspace paths are implicit-relative — no path variable prefix in skill prose. |
| `{content_systems_public_root}` | Only named path variable. Resolved from `config.json` → `content_systems_public.path`; GitHub fallback via `content_systems_public.repo_url`. |
| This repo | Skills and utilities only. Never read or write `credentials.json` here. |
| Credentials entry | `credentials.json` at workspace root; external files via `more_credentials` + `@shared#…` (see [Credentials](#credentials)). |
| Cross-repo links | Workspace skills: `{content_systems_public_root}/…`. Skills in this repo: repo-relative `../` links. |

Design principles and produce/stage policy: [README.md § Design principles](../../README.md#design-principles). Workflow layout and preflight checklist: [maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md). Skill formatting: [maintain_skills/SKILL.md](../maintain_skills/SKILL.md).

---

## Workspace root

Walk up from the active `SKILL.md` until you find `config.json`. That folder is the workspace root. All workspace paths in skills (`config.json`, `credentials.json`, `_workflows/`, `_context/`, `_assets/`, etc.) are relative to it — no named variable.

Log the workspace root as a path in debug lines when useful.

## Content systems public

Shared skills and utilities live in a separate checkout. Resolve once in preflight:

```text
{content_systems_public_root} = <workspace root> / config.json → content_systems_public.path
```

If that path is missing locally, use `config.json` → `content_systems_public.repo_url` (GitHub).

Workspace workflow skills link across repos with `{content_systems_public_root}/…` (for example `{content_systems_public_root}/setup/run_workflow/SKILL.md`). Skills in this repo use repo-relative links (`../run_workflow/SKILL.md`).

## Context assembly

Before a workflow reads workspace positioning, brand rules, or approved copy, sync the local asset layer.

1. Find the workspace root (folder containing `config.json`).
2. Run [sync_assets/SKILL.md](../sync_assets/SKILL.md) from that folder.
3. Read materialized copy from `_assets/`. Check `_assets/asset-manifest.md` for `last_updated` and `sync_status`.
4. Prefer `_context/` and `_assets/` over live URLs when material exists, unless the active skill says to pull fresh copy.

Skip context assembly when the skill does not read workspace reference material.

Log: `[run-debug] context-assembly | workspace={path} | assets={count} | warns={warn_count}`

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

Browserbase sessions require API keys - so this only applies if one is available. If you create a Browserbase session for any step, read [_workflows/ops/browser_automation/SKILL.md](../../_workflows/ops/browser_automation/SKILL.md) and repeat the live view URL conspicuously in every user message while the session is open (see `.cursor/rules/browserbase-live-session.mdc`). Paste the URL block immediately before any login/handoff ask — not only once at the start.

## Credentials

All credential lookups start at `credentials.json` (workspace root).

Common keys and which skills need them: [credentials.example.json](../credentials.example.json). Storage policy: [README.md § Credentials](../../README.md#credentials).

### more_credentials

`@content_systems_public` never holds credentials. It is skills and shared utilities only. See [README.md § Credentials](../../README.md#credentials).

Workspace `credentials.json` declares external credential files under `more_credentials`:

```json
"more_credentials": {
  "shared": "@./credentials.shared.json"
}
```

Each value is an `@`-prefixed path relative to the workspace root — a credentials file, no `#key`.

Add other sources as needed:

```json
"more_credentials": {
  "shared": "@./credentials.shared.json",
  "local": "@credentials.local.json"
}
```

### Reference syntax

A string value may point at another file:

```text
@alias#dotted.key.path
@relative/path/to/credentials.json#dotted.key.path
```

Examples:

- `@shared#anthropic` — alias via `more_credentials`
- `@credentials.json#google.oauth_token_unified` — same file or path relative to workspace root

- Paths are relative to the workspace root.
- If the segment before `#` matches a `more_credentials` key, load that file; otherwise treat it as a path.
- Resolve reference strings before use. Follow nested references when needed.
- An inline object or string at the same JSON path overrides a reference.
- After resolution, treat the value as inline.
- Skip `more_credentials` itself when walking keys for skill lookups — it is a registry, not a credential namespace.

### Resolution procedure

1. Load `credentials.json`. If it is missing, copy from `credentials.example.json` after the user supplies values.
2. Resolve every `more_credentials` entry to a file path (follow nested `@` references if present).
3. Walk the JSON tree (except `more_credentials`). Replace each `@…#…` string with the resolved secret.
4. If a required key is still missing, ask the user, add it to `./credentials.json`, and run `git check-ignore credentials.json`.
5. Delete `./credentials.json` when it would be empty (no keys and no references).
6. Do not commit credential files. Do not log secret values.

Skills name the JSON path they need (for example `google.oauth_token_unified`, `webflow.api_token`). They do not list multiple credential file paths.

## Adding a new skill

If the skill is part of a workflow sequence, step 01 (and later steps when standalone) opens with a link to this file — do not call it "Step 0".

- Workspace workflow skills (under `_workflows/` in your workspace): `Read {content_systems_public_root}/setup/run_workflow/SKILL.md`. Resolve `{content_systems_public_root}` in preflight per Content systems public above.
- Skills in this repo: repo-relative link, e.g. [run_workflow/SKILL.md](../run_workflow/SKILL.md) from `setup/`.

See [maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md) for step numbering.

Every workflow starts with a dedicated `01_preflight` step. See [maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md).

If the skill is a main workflow orchestrator, add a `"reacts to"` list in frontmatter for observable triggers only. See [maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md).

Do not copy instructions that already live in another skill or `_context/` file. Link to the canonical copy instead.

## Ephemeral data

Store scratch files, run folders, debug traces, and pipeline intermediates only under a directory named `tmp/`. The path may live at the workspace root, under `_workflows/{category}/{name}/`, or under a step folder — but the directory name must be `tmp/`.

- Do not use `debug/` or other scratch directory names for ephemeral data.
- Delete or wipe `tmp/` contents when the skill says to clean up.
- Do not commit files under `tmp/` (gitignored via `**/tmp/`).

## AI models

Only use models for which resolved credentials exist.

## End of run

1. Suggest improvements to any skills that ran.
2. Update `"last run"` in the front matter of every executed `SKILL.md`. Use ISO date `YYYY-MM-DD`.
3. If a skill is stale, offer to run [maintain_skills/SKILL.md](../maintain_skills/SKILL.md) and [maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md).
