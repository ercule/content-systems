# Workflows

Shipped skills under `{workspace_root}/_workflows/`. Workspaces may add custom pipelines alongside these folders.

Read [setup/run_workflow/SKILL.md](../setup/run_workflow/SKILL.md) before running any workflow.

## Layout

| Folder | Role |
|--------|------|
| **edit/** | Multi-step produce pipelines (e.g. page refresh) — produce only |
| **research/** | Discovery and enrichment (FAQ mining, external audit, crosslinks) — produce only |
| **generate/** | Content generation that writes net-new drafts — produce only |
| **ops/** | Staging, publish, evaluate, and atomic utilities (fetch, Doc conversion, browser fallback) |

Produce workflows never live in `ops/`. Staging and publish workflows always live in `ops/`.

Verb-first workflow folder names (`update_agent`, `build_crosslinks`, `stage_content`, `generate_article`, …). Numbered steps use `{NN}_{slug}` starting at `01_preflight`. Net-new article pipelines use `generate_article`, not `generate_article`.

## Shipped skills

### edit/

| Skill | Purpose |
|-------|---------|
| [update_agent](edit/update_agent/SKILL.md) | Refresh an existing page → Google Doc (uses research/build_crosslinks, ops/markdown_to_google_doc) |

### research/

| Skill | Purpose |
|-------|---------|
| [find_faq_questions](research/find_faq_questions/SKILL.md) | Mine FAQ questions into a sheet |
| [evaluate_external_brand](research/evaluate_external_brand/SKILL.md) | Audit external brand mentions |
| [build_crosslinks](research/build_crosslinks/SKILL.md) | Bootstrap `crosslinks.json` + select internal links (replaces legacy `init_crosslinks_json`) |

### generate/

| Skill | Purpose |
|-------|---------|
| [generate_faq_responses](generate/generate_faq_responses/SKILL.md) | Draft FAQ responses for sheet rows |

### ops/

| Skill | Purpose |
|-------|---------|
| [fetch_url](ops/fetch_url/SKILL.md) | Fetch page HTML |
| [write_google_sheet](ops/write_google_sheet/SKILL.md) | Append/update Google Sheet rows |
| [markdown_to_google_doc](ops/markdown_to_google_doc/SKILL.md) | Markdown → Google Doc upload |
| [google_doc_to_markdown](ops/google_doc_to_markdown/SKILL.md) | Google Doc → Markdown |
| [show_edits_in_google_doc](ops/show_edits_in_google_doc/SKILL.md) | Inline editorial markup |
| [accept_edits_google_doc](ops/accept_edits_google_doc/SKILL.md) | Finalize Doc markup |
| [evaluate_content](ops/evaluate_content/SKILL.md) | LLM content evaluation |
| [publish_wordpress_from_google_doc](ops/publish_wordpress_from_google_doc/SKILL.md) | Doc → WordPress draft |
| [youtube_transcription](ops/youtube_transcription/SKILL.md) | YouTube → transcript |
| [wikitext_editing](ops/wikitext_editing/SKILL.md) | Wikitext helpers |
| [browser_automation](ops/browser_automation/SKILL.md) | Browserbase fallback |

## Not shipped yet

- `_workflows/stage_content/` — workspace CMS publish router (add when you need staging)

## Maintenance

- Per-skill quality: [setup/maintain_skills/SKILL.md](../setup/maintain_skills/SKILL.md)
- Workflow layout and run order: [setup/maintain_workflows/SKILL.md](../setup/maintain_workflows/SKILL.md)
