---
name: generate_article
description: >-
  Shared produce pipeline for a new article: preflight, context pack, research,
  prompt pack, draft, extra components, mechanical rewrite, then a Google Doc
  via markdown_to_google_doc. Temporary files live under tmp/. Ends at a Doc.
  CMS publish is a separate staging workflow.
"last updated": 2026-08-16T05:30:00+00:00
"last run": 2026-08-23
---

# Generate article (shared)

Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) before running this step.

Log line prefix: `[run-debug] workflow=_workflows/generate/generate_article | <PHASE> | <facts>`

This is a produce workflow. The file you keep is a Google Doc. Publishing to a CMS is a later, separate workflow.

Other skills must link here and pass a title plus config.

## Configuration

Set this block in `config.json`:

```json
{
  "workflow_specific": {
    "generate_article": {
      "site_url": "https://example.com",
      "drive_folder_id": "",
      "target_word_count": 1200,
      "min_first_party_links": 7,
      "components": ["key_takeaways", "faqs"]
    }
  }
}
```

- `site_url`: site host for research, relevant articles, and crosslinks
- `drive_folder_id`: Drive folder for the output Doc
- `target_word_count`: body length target (default 1200). Key takeaways and FAQs sit outside this count
- `min_first_party_links`: how many distinct on-site URLs the crosslinks file and draft must include (default 7)
- `components`: extra blocks step 06 adds. Values: `key_takeaways`, `faqs`, `categories`

Resolve secrets from `credentials.json` per [run_workflow](../../../setup/run_workflow/SKILL.md). Key shapes: [credentials.example.json](../../../setup/credentials.example.json).

The required input is `title`. Other inputs live in [01_preflight/SKILL.md](01_preflight/SKILL.md). The run folder is created in [02_context_pack/SKILL.md](02_context_pack/SKILL.md). Cleanup lives in [08_output/SKILL.md](08_output/SKILL.md).

## Run order

Every run starts at 01 and walks 02, 03, 04, 05, 06, 07, then 08. Do not skip a step. Do not start 05 from 01. Start each step only after the previous step has finished. Each step names the files it requires from the prior step; if those files are missing, list them and end the run.

- 01 [01_preflight/SKILL.md](01_preflight/SKILL.md): config, credentials, and inputs ready. Next is always 02.
- 02 [02_context_pack/SKILL.md](02_context_pack/SKILL.md): `RUN_DIR` with verbatim copies under `context/`. Next is always 03.
- 03 [03_research/SKILL.md](03_research/SKILL.md): inventory, relevant articles, and crosslinks. Next is always 04.
- 04 [04_package_prompt/SKILL.md](04_package_prompt/SKILL.md): `prompt-pack.md` (brief, seven voice bullets, extra instructions, verbatim context); pause until the pack is approved. Next is 05 only after approval.
- 05 [05_draft/SKILL.md](05_draft/SKILL.md): manuscript from the approved pack. Next is always 06.
- 06 [06_components/SKILL.md](06_components/SKILL.md): FAQs, key takeaways, and/or categories. Next is always 07.
- 07 [07_mechanical_rewrite/SKILL.md](07_mechanical_rewrite/SKILL.md): checklist rewrite in place. Next is always 08.
- 08 [08_output/SKILL.md](08_output/SKILL.md): Google Doc via [markdown_to_google_doc](../../ops/markdown_to_google_doc/SKILL.md). No next step.

Step 04 is the only pause. After it writes `prompt-pack.md`, wait for approval, then run step 05. A later job still starts at 01. When `prompt-pack.approved` is missing, 01 ends. When it is present, 01 walks 02, 03, and 04 (reuse) before 05. Steps 02–04 reuse the existing folder when `prompt-pack.md` is already there; they must not wipe or rebuild it.

Treat the pack as approved only after `prompt-pack.approved` exists, or after the user accepts it in this chat (which writes that file).

## Related

- Conversion: [markdown_to_google_doc](../../ops/markdown_to_google_doc/SKILL.md)
- Fetch: [fetch_url](../../ops/fetch_url/SKILL.md)
- Context assembly: [sync_assets](../../../setup/sync_assets/SKILL.md)
