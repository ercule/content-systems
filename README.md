# content-systems

Open-source **agent skills** for content operations: Google Doc editorial markup, Doc ↔ Markdown, FAQ mining, CMS publish, page refresh, and more. Each skill is a `SKILL.md` file an agent reads and follows; deterministic steps call Python scripts in [scripts/](scripts/README.md).

Clone this repository and work from its **root** — the directory that contains `config.json`, `credentials.json`, `_context/`, `_workflows/`, `setup/`, and `scripts/`.

**Agents (Claude Code, Claude, Cursor):** read this file end to end before the first skill run. Execute the [Agent checklist](#agent-checklist) in order. Ask the user for missing values. **Do not print, log, or commit secrets.**

---

## Quick start

```bash
git clone <repository-url> content-systems
cd content-systems
cp setup/config.example.json config.json
cp setup/credentials.example.json credentials.example.json
cp setup/credentials.example.json credentials.json   # then fill secrets
```

A [`.gitignore`](.gitignore) ignores `credentials.json`, `**/tmp/`, local `.venv/` trees, and transcription scratch output.

**Verify:** `./setup/run_workflow/SKILL.md` and `./_workflows/edit/show_edits_in_google_doc/` exist.

---

## I want to…

| I want to… | Start here | Needs |
|------------|------------|--------|
| Mark up edits in a Google Doc | [_workflows/show_edits_in_google_doc](_workflows/edit/show_edits_in_google_doc/SKILL.md) | Google OAuth, `inline-markup-plan.json` |
| Finalize markup after review | [_workflows/edit/accept_edits_google_doc](_workflows/edit/accept_edits_in_google_doc/SKILL.md) | Google OAuth |
| Convert Doc → Markdown | [_workflows/google_doc_to_markdown](_workflows/ops/google_doc_to_markdown/SKILL.md) | Google OAuth |
| Create a Doc from Markdown | [_workflows/markdown_to_google_doc](_workflows/edit/markdown_to_google_doc/SKILL.md) | Google OAuth |
| Mine FAQ questions (sheet) | [_workflows/faq_question_finder](_workflows/generate/faq_question_finder/SKILL.md) | Google OAuth, SerpAPI, GSC |
| Draft FAQ responses | [_workflows/faq_question_responder](_workflows/generate/faq_question_responder/SKILL.md) | Google OAuth, SerpAPI, Anthropic |
| Audit external brand mentions | [_workflows/external_linter](_workflows/generate/external_linter/SKILL.md) | SerpAPI, Google OAuth, Playwright |
| Refresh an existing page | [_workflows/update_agent](_workflows/generate/update_agent/SKILL.md) | `workflow_specific.update_agent` in config |
| Publish Doc → WordPress | [_workflows/google_doc_to_wordpress](_workflows/ops/google_doc_to_wordpress/SKILL.md) | WP + Google OAuth |
| Browser fallback (CMS login) | [_workflows/browser_automation](_workflows/ops/browser_automation/SKILL.md) | Optional Browserbase |

---

## What's inside

| Layer | Path | Holds |
|-------|------|--------|
| **Workflows** | [_workflows/](_workflows/README.md) | Shipped skills + your custom pipelines |
| **Context (demo)** | [_context/](_context/README.md) | Fictional [Gallivant](_context/reference/gallivant-origin.md) canon — replace for production |
| **Scripts** | [scripts/](scripts/README.md) | Python runners |
| **Contract** | [run_workflow/](setup/run_workflow/SKILL.md) | Step 0 for every skill |
| **Asset sync** | [setup/sync_assets/](setup/sync_assets/SKILL.md) | Materialize `_assets/` from `external_assets.md` |
| **Hygiene** | [setup/maintain_skills/](setup/maintain_skills/SKILL.md), [setup/maintain_workflows/](setup/maintain_workflows/SKILL.md) | Author audits |
| **Setup templates** | [setup/](setup/) | Example config and credential shapes |

Every skill run resolves **workspace root**: the directory that contains `config.json`. Walk up from the active `SKILL.md` until you find it (repo root in a normal setup).

---

## Agent checklist

### 1. Clone and enter the repo

See [Quick start](#quick-start).

### 2. Ensure git ignores secrets

```bash
git check-ignore -v credentials.json
```

Must be ignored before writing secrets.

### 3. Create config.json

Edit `config.json`:

- `repo.url` — URL for this repository (blank until published is OK)
- Model names under `anthropic` / `gemini` if the user has preferences
- Service-specific IDs (sheet IDs, site URLs) as needed — **not secrets**

**Verify:** `jq . config.json` succeeds.

### 4. Create credentials.json

Fill inline values for each key the planned skills require. See [Credentials](#credentials).

Optional: split secrets using `@` references — see [Reference syntax](#reference-syntax).

### 5. Set up context (when skills need brand/canon)

Skills read from **`{workspace_root}/_context/`**.

- **Demo:** use shipped [Gallivant](_context/README.md) canon as-is.
- **Production:** replace `_context/` with real messaging canon ([context-builder](https://github.com/janessa-lantz/context-builder) shape).

Optional: `{workspace_root}/_assets/` and `external_assets.md` for [setup/sync_assets/SKILL.md](setup/sync_assets/SKILL.md).

### 6. Pull latest (ongoing)

```bash
git pull --ff-only
```

### 7. Smoke-test

1. Read [run_workflow/SKILL.md](setup/run_workflow/SKILL.md).
2. Read the target skill's `SKILL.md` (see [Skill catalog](#skill-catalog)).
3. Run context assembly only if the skill reads `_context/` or `_assets/`.
4. Execute steps; run `python3 scripts/...` from repo root when the skill names a script.

---

## Credentials

### Rules

- **Runtime lookups start at `{workspace_root}/credentials.json` only.**
- Do not commit populated credential files.
- Put non-secrets in `config.json`.

### Reference syntax

```text
@relative/path/to/credentials.json#dotted.key.path
```

Example: `@secrets/vendor-keys.json#google.oauth_token_unified`

Paths are relative to `workspace_root`. Inline values override references. Procedure: [run_workflow/SKILL.md](setup/run_workflow/SKILL.md).

### Google OAuth

Most Google skills need `google.oauth_token_unified` with scopes in [setup/credentials.example.json](setup/credentials.example.json).

1. Create OAuth **Desktop** client in Google Cloud Console → `google.oauth_installed_client`.
2. Run installed-app flow → `google.oauth_token_unified`.

### Keys by skill (common)

| Skill area | Credential paths |
|------------|------------------|
| Google Docs / Sheets / Drive | `google.oauth_token_unified` |
| FAQ finder (GSC) | `google.oauth_token_unified` (+ optional `_2`) |
| FAQ finder (Reddit/LinkedIn) | `serpapi.api_key` |
| LLM steps | `anthropic.api_key`, `gemini.api_key` |
| Browser automation | `browserbase.api_key` when enabled in config |
| Webflow publish | `webflow.api_token` |

---

## Config vs credentials

| File | Committed? | Contents |
|------|------------|----------|
| `config.json` | Yes | IDs, URLs, models, `repo.url`, `browserbase.enabled` |
| `credentials.json` | No | API keys, tokens, OAuth bundles |
| `credentials.example.json` | Yes | Key shapes — no secrets |

Templates: [setup/config.example.json](setup/config.example.json), [setup/credentials.example.json](setup/credentials.example.json).

---

## How to run a skill

1. **Step 0** — [run_workflow/SKILL.md](setup/run_workflow/SKILL.md)
2. **Read the skill** — `_workflows/{category}/{name}/SKILL.md`
3. **Resolve workspace root** — directory containing `config.json`
4. **Context assembly** — when the skill reads canon, ensure `_context/` / `_assets/` are ready
5. **Execute** — small steps, `[run-debug]` logging
6. **End of run** — update `"last run"` in skill frontmatter (ISO date)

```bash
python3 scripts/google_doc/apply_inline_doc_markup.py --help
```

**Editorial markup pipeline:**

```
[your _workflows/ pipeline or plan JSON]
        ↓  inline-markup-plan.json
show_edits_in_google_doc  →  scripts/google_doc/apply_inline_doc_markup.py
        ↓  human review in Google Doc
accept_edits_google_doc   →  scripts/google_doc/resolve_doc_markup.py
```

---

## Skill catalog

Grouped catalog: [_workflows/README.md](_workflows/README.md).

| Category | Skills |
|----------|--------|
| edit | show_edits_in_google_doc, accept_edits_google_doc, markdown_to_google_doc, evaluate_content |
| generate | faq_question_finder, faq_question_responder, external_linter, update_agent, build_crosslinks, init_crosslinks_json, update_doc_handoff |
| ops | fetch_url_html, google_doc_to_markdown, google_doc_to_wordpress, wikitext_editing, browser_automation, google_sheet_write, youtube_transcription_yt |

### Roadmap (not shipped yet)

Documented in maintain docs but **no `SKILL.md` in this repo yet**:

- `_workflows/content_staging` — CMS publish router (add under `_workflows/` when you need it)
- Suggest/propose edit orchestrators, standalone `converters/` utility folder

Do not link agents to these until the skill files exist.

---

## Organization principles

### Folder layout

```
<repo-root>/
├── README.md
├── config.json
├── credentials.json              (gitignored)
├── _context/                     messaging canon (Gallivant demo → replace)
├── _assets/                      materialized copy (optional; see sync_assets)
├── external_assets.md            optional registry for sync_assets
├── _workflows/                   skills by category (see _workflows/README.md)
│   ├── edit/ generate/ ops/
├── setup/                        config templates, run_workflow, maintain_*, sync_assets
│   ├── run_workflow/             Step 0 contract
│   ├── sync_assets/
│   ├── maintain_skills/
│   ├── maintain_workflows/
│   ├── config.example.json
│   └── credentials.example.json
├── scripts/                      Python runners
```

### Ephemeral data

Scratch files **only** in directories named `tmp/`. Gitignore `**/tmp/` (see [`.gitignore`](.gitignore)).

### Skills and references

- **Shipped skills:** `_workflows/{category}/{name}/SKILL.md` — link from custom orchestrators; do not fork.
- **Custom pipelines:** add `_workflows/{edit|generate|ops}/{your_pipeline}/SKILL.md` and link to shipped skills below; do not copy their steps.
- Every step starts with Step 0: [run_workflow/SKILL.md](setup/run_workflow/SKILL.md).
- Say each instruction once — link to canonical skills ([setup/maintain_skills/SKILL.md](setup/maintain_skills/SKILL.md)).

### sync_assets

Before skills read materialized copy, run [setup/sync_assets/SKILL.md](setup/sync_assets/SKILL.md) to populate `{workspace_root}/_assets/` from `external_assets.md` and local paths. See [run_workflow/SKILL.md § Context assembly](setup/run_workflow/SKILL.md).

### Repo hygiene

Do not commit:

- Populated `credentials.json`
- Anything under `**/tmp/`
- Local Python envs (`**/.venv/`, e.g. under `scripts/video_transcription/`)
- Transcription scratch (`scripts/**/youtube_transcripts/`)

---

## For Claude Code and Cursor

- Register skills under `_workflows/`.
- Point `CLAUDE.md` or a Cursor rule at this **README** and [run_workflow/SKILL.md](setup/run_workflow/SKILL.md).
- Browserbase: [_workflows/browser_automation](_workflows/ops/browser_automation/SKILL.md) — repeat the live session URL while the session is open.

---

## Maintenance

```bash
python3 scripts/maintain/scan_step_zero.py
python3 scripts/maintain/scan_skill_links.py
python3 scripts/maintain/scan_reacts_to.py
```

See [setup/maintain_skills/SKILL.md](setup/maintain_skills/SKILL.md) and [setup/maintain_workflows/SKILL.md](setup/maintain_workflows/SKILL.md).

---

## Troubleshooting

| Symptom | Check |
|---------|--------|
| `credentials.json` not found | File at repo root next to `config.json` |
| Google 403 / invalid_grant | OAuth scopes; re-run token flow |
| Script cannot find workspace | Run from repo root |
| Skill not found | Look under `_workflows/{category}/{name}/` — see [_workflows/README.md](_workflows/README.md) |
| Canon ignored | Replace `_context/` at repo root for production |

---

## Example context

[_context/](_context/README.md) ships **fictional Gallivant** messaging. Replace with real canon for production work.
