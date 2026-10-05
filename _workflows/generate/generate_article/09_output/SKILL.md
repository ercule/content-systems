---
name: generate_article_09_output
description: >-
  Step 09: create the Google Doc from final Markdown by calling
  export_google_doc, then delete the run folder on success.
"last updated": 2026-08-16T05:30:00+00:00
"last run": never
tools:
  - export_google_doc
---

# Generate article — 09 Output

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

Start this step after [../08_mechanical_rewrites/SKILL.md](../08_mechanical_rewrites/SKILL.md). Require `{id-or-slug}.md` in `RUN_DIR`. If it is missing, follow the missing-file stop in [../05_draft/SKILL.md](../05_draft/SKILL.md).

## Delivery

Call `export_google_doc` with `path` set to the manuscript in RUN_DIR and `title` set to the Doc name. The tool reads the Drive folder from the client config.

## After a successful upload

1. Set `run-status.md` in `RUN_DIR` to `status: complete` and record `doc_url`.
2. Report `doc_url` to the user.
3. Delete `RUN_DIR`.

Keep `RUN_DIR` until upload succeeds. On a Drive error, report the error and retry this step with the same `run_dir`.

Log: `[run-debug] workflow=_workflows/generate/generate_article | OUTPUT | doc_id={id} url={doc_url}`

This step has no next step.
