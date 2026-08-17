---
name: utilities_run_workflow
description: >-
  Shared execution context for all workflow skills: runtime HTTP contract, context assembly,
  credential resolution, small-step runs
"last updated": 2026-08-15T00:00:00+00:00
P26-08-17
---

Canonical execution contract for workflow skills. [README.md § Documentation map](../../README.md#documentation-map).

## Path rules

- **Workspace root.** Walk up from the active `SKILL.md` until you find `config.json`. That folder is the workspace root. All workspace paths (`config.json`, `credentials.json`, `_workflows/`, `_context/`, `_assets/`, etc.) are implicit-relative to it.
- **`{content_systems_public_root}`.** The only named path variable. `config.json` → `content_systems_public.path`; if missing locally, fall back to `config.json` → `content_systems_public.repo_url` (GitHub).
- **Credentials entry.** `credentials.json` at workspace root; external files via `more_credentials` + `@shared#…` (see [Credentials](#credentials)).
- **Cross-repo links.** From a workspace skill, link to `{content_systems_public_root}/…`. From a skill in this repo, link repo-relative (`../`).

## Execution rules

1. **Build API calls at runtime.** Construct each request (URL, method, headers, body) at execution time, with curl or an equivalent HTTP client.
2. **Break tasks into small steps.** Prefer several narrow tool calls over one large call.
3. **Log as you go.**
   - Echo the active skill name, UID or doc ID, and fetch path.
   - Echo credentials loaded: repository, custom type, model ID, and API host only — never secrets.
   - For each HTTP request: echo method, host, path (omit secret query parts), status, and content-length when present.
   - On HTTP errors: echo status and the first ~500 characters of the body.

## Credentials

- All lookups start at `credentials.json` (workspace root). Common keys and which skills need them: [credentials.example.json](../credentials.example.json). Storage policy: [README.md § Credentials](../../README.md#credentials).
- Skills should name the JSON path they need (e.g. `google.oauth_token_unified`, `webflow.api_token`), not list multiple credential file paths.
- Workspace `credentials.json` can point to external credential files via `more_credentials`, e.g. `"more_credentials": { "shared": "@./credentials.shared.json" }`. Each value is an `@`-prefixed path relative to the workspace root (a credentials file, no `#key`). `@content_systems_public` never holds credentials — that repo is skills and shared utilities only.
- Any value can also be a reference straight to a key inside a credentials file, e.g. `@shared#anthropic` (via a `more_credentials` alias) or `@credentials.json#google.oauth_token_unified` (a direct path). If the part before `#` matches a `more_credentials` key, load that file; otherwise treat it as a path. Follow nested `@` references if they chain. An inline value at the same spot always overrides a reference. Skip `more_credentials` itself when walking keys — it's a registry, not a credential.
- To resolve: load `credentials.json` (copy from `credentials.example.json` after the user supplies values if it's missing), resolve every `more_credentials` entry to a file path, then walk the tree and replace each `@…#…` reference with its resolved secret. Treat the result as inline from then on.
- If a required key is still missing, ask the user, add it to `./credentials.json`, and run `git check-ignore credentials.json`.
- Delete `./credentials.json` when it would be empty. Never commit credential files or log secret values.

## Ephemeral data

Store scratch files, run folders, debug traces, and pipeline intermediates only under a directory named `tmp/` — at the workspace root, under `_workflows/{category}/{name}/`, or under a step folder. Don't use `debug/` or other names. 

Delete or wipe `tmp/` when this skill is run.

## AI models

Only use models for which resolved credentials exist.

## End of run

1. Suggest improvements to any skills that ran.
2. Update `"last run"` in the front matter of every executed `SKILL.md` (ISO date `YYYY-MM-DD`).
3. If a skill is stale, offer to run [maintain_skills/SKILL.md](../maintain_skills/SKILL.md) and [maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md).