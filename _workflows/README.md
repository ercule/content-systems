# Workflows

Shipped skills live here, grouped by job. Each workflow is a folder with a root `SKILL.md`. Multi-step pipelines add numbered subfolders (`01_preflight/`, `02_fetch/`, …).

Every step starts with Step 0: [run_workflow/SKILL.md](../setup/run_workflow/SKILL.md). Full setup and catalog: [README.md](../README.md).

**Custom pipelines:** add `_workflows/{edit|generate|ops}/{your_pipeline}/SKILL.md` and link to shipped skills below instead of copying their steps.

## By category

| Category | Skills |
|----------|--------|
| **edit/** | [show_edits_in_google_doc](edit/show_edits_in_google_doc/SKILL.md), [accept_edits_google_doc](edit/accept_edits_google_doc/SKILL.md), [markdown_to_google_doc](edit/markdown_to_google_doc/SKILL.md), [evaluate_content](edit/evaluate_content/SKILL.md) |
| **generate/** | [faq_question_finder](generate/faq_question_finder/SKILL.md), [faq_question_responder](generate/faq_question_responder/SKILL.md), [external_linter](generate/external_linter/SKILL.md), [update_agent](generate/update_agent/SKILL.md), [build_crosslinks](generate/build_crosslinks/SKILL.md), [init_crosslinks_json](generate/init_crosslinks_json/SKILL.md), [update_doc_handoff](generate/update_doc_handoff/SKILL.md) |
| **ops/** | [fetch_url_html](ops/fetch_url_html/SKILL.md), [google_doc_to_markdown](ops/google_doc_to_markdown/SKILL.md), [google_doc_to_wordpress](ops/google_doc_to_wordpress/SKILL.md), [wikitext_editing](ops/wikitext_editing/SKILL.md), [browser_automation](ops/browser_automation/SKILL.md), [google_sheet_write](ops/google_sheet_write/SKILL.md), [youtube_transcription_yt](ops/youtube_transcription_yt/SKILL.md) |

Python runners: [scripts/](../scripts/README.md) (linked from individual skills).

Store run artifacts only in `tmp/` (this folder or repo root).
