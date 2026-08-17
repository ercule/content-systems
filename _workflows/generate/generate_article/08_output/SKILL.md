---
name: generate_article_08_output
description: >-
  Step 08: create the Google Doc from final Markdown via the shared
  markdown_to_google_doc skill, then delete the run folder on success.
"last updated": 2026-08-16T05:30:00+00:00
"last run": never
---

# Generate article — 08 Output

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

Start this step after [../07_mechanical_rewrite/SKILL.md](../07_mechanical_rewrite/SKILL.md). Require `{id-or-slug}.md` in `RUN_DIR`. If it is missing, follow the missing-file stop in [../05_draft/SKILL.md](../05_draft/SKILL.md).

## Delivery

Call [markdown_to_google_doc](../../../ops/markdown_to_google_doc/SKILL.md) with:

- `markdown`: contents of `{id-or-slug}.md` in `RUN_DIR`
- `doc_name`: H1 plain text from that file
- `folder_id`: `workflow_specific.generate_article.drive_folder_id`
- `preset`: `standalone_article`

Pass those four inputs. Conversion, HTML shell, upload, and the post-upload check live in markdown_to_google_doc.

## After a successful upload

1. Set `run-status.md` in `RUN_DIR` to `status: complete` and record `doc_url`.
2. Report `doc_url` to the user.
3. Delete `RUN_DIR`.

Keep `RUN_DIR` until upload succeeds. On a Drive error, report the error and retry this step with the same `run_dir`.

Log: `[run-debug] workflow=_workflows/generate/generate_article | OUTPUT | doc_id={id} url={doc_url}`

This step has no next step.
