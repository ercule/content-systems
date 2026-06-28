---
name: update_doc_handoff
description: >-
  Shared step for update_agent workflows. Produce a Google Doc that contains a
  list of changes at the top and the fully updated article at the bottom. Wraps
  the existing markdown_to_google_doc upload recipe.
"last updated": 2026-06-01T00:58:28+00:00
"last run": 2026-06-01T00:58:28+00:00
---

# Update Doc handoff (shared)

Step 0: Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) (workflow standards: runtime HTTP, logging, ephemeral rules).

## Inputs

- `enhanced_markdown` — required. The fully updated article (no agent commentary, no fences).
- `change_summary_markdown` — required. Bullet list (Markdown `-`) describing every change Gemini made: crosslinks added (with URL + anchor), FAQ entries added (with question), and any other diffs. Should be concise enough to be agent-readable on a re-run.
- `source_title` — required. Used in Doc title and metadata.
- `source_url` — required. The original article URL.
- `target_keyword` — required. Surfaced in metadata.
- `crosslinks_added_count` — integer.
- `faq_added` — boolean.
- `drive_folder_id` — required. Caller-resolved Drive folder for the new Doc.

## Doc title

`(Update) {source_title} — YYYY-MM-DD` (UTC date).

## Body composition

Build a single Markdown body in this exact structural order, then hand it to [../../edit/markdown_to_google_doc/SKILL.md](../../edit/markdown_to_google_doc/SKILL.md) for HTML conversion and Drive upload.

```markdown
# (Update) {source_title}

- **Original URL:** {source_url}
- **Generated:** {YYYY-MM-DD HH:MM:SS} UTC
- **Target keyword:** {target_keyword}
- **Crosslinks added:** {crosslinks_added_count}
- **FAQ section:** {Yes|No}

---

## List of changes

{change_summary_markdown}

---

## Updated article

{enhanced_markdown}
```

Notes for the converter:

- The metadata block is the bullet list per the markdown_to_google_doc metadata rule (Original URL, Generated, Changes made). Render `Crosslinks added:` and `FAQ section:` inline as part of the standard `Changes made:` line if a stricter caller demands the canonical wording — otherwise the labelled bullets above are preferred for downstream re-runs.
- The two `---` lines stay as Markdown `<hr />`.
- Keep `## List of changes` and `## Updated article` as the only `<h2>` headings inside the metadata wrapper.

## Drive upload

Call [../../edit/markdown_to_google_doc/SKILL.md](../../edit/markdown_to_google_doc/SKILL.md) with the composed Markdown body, `doc_name`, and `drive_folder_id`. Use preset `standalone_article` unless the metadata block above should render as the default update_agent list (then build metadata via Markdown bullets and still convert through the shared skill).

OAuth and verification: per the shared skill. Do not duplicate conversion or multipart steps here.

## Outputs (carry forward to caller)

- `doc_id` — from the Drive `files.create` response.
- `doc_url` — `https://docs.google.com/document/d/{doc_id}/edit` (or the response `webViewLink`).

## Verification

Read the Doc back (Drive `files.get` with `fields=name,parents,webViewLink` or a `documents.get` Docs API call) and log `doc_verify=ok` plus `doc_url`.

## Logging

```text
[run-debug] workflow=<caller> | doc-handoff | folder=<id> doc_id=<id> crosslinks_added=<n> faq_added=<bool>
```
