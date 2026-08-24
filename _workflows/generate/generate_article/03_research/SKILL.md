---
name: generate_article_03_research
description: >-
  Step 03: write the inventory, a relevant-articles list, and a crosslinks list
  for this title. Later steps must use on-site URLs from the crosslinks list.
"last updated": 2026-08-17T00:40:00+00:00
"last run": 2026-08-23
---

# Generate article — 03 Research

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

Start this step after [../02_context_pack/SKILL.md](../02_context_pack/SKILL.md). `RUN_DIR` must exist and contain `context/`. If those are missing, list them and end the run.

When `{id-or-slug}-inventory.md`, `{id-or-slug}-relevant-articles.md`, and `{id-or-slug}-crosslinks.md` already exist in `RUN_DIR` and `prompt-pack.md` is present, leave those files and go to [../04_package_prompt/SKILL.md](../04_package_prompt/SKILL.md).

Fetch pages with [fetch_url](../../../ops/fetch_url/SKILL.md).

## Inputs

- `title`, `id-or-slug`, `target_keyword`, `specific_context`: [../01_preflight/SKILL.md](../01_preflight/SKILL.md)
- `site_url`, `min_first_party_links`, `target_word_count`: `workflow_specific.generate_article` in [../SKILL.md](../SKILL.md)
- Voice and audience: copied files in `RUN_DIR/context/` from [../02_context_pack/SKILL.md](../02_context_pack/SKILL.md)

## On-site pages

1. Read the host from `site_url`.
2. Fetch `site_url` and collect on-site article, docs, and product URLs that match `target_keyword` or `title`, published in the last six months.
3. Fetch each candidate with fetch_url. Keep pages whose body is relevant to the thesis.
4. The crosslinks file must list at least `min_first_party_links` distinct URLs on this host (and paths under it). When fewer matching pages exist, list the URLs found and end the run.

Later steps must use on-site URLs from the crosslinks file.

## Outside sources

When `specific_context` or the copied context files name an outside source, fetch it with fetch_url and add it to the relevant-articles list.

## Write `{id-or-slug}-inventory.md` in `RUN_DIR`

Include:

- Header lines: `created:`, `title:`, `target_keyword:`, `site_url:`
- One-sentence thesis
- Audience (from the copied context files)
- H2/H3 outline sized to `target_word_count`
- Proof points and stats with sources
- FAQ seeds (questions the article should answer)
- Thesis bullets for key takeaways (3–5 concrete takeaways)

## Write `{id-or-slug}-relevant-articles.md` in `RUN_DIR`

A bulleted list of articles that bear on this title. Include on-site pieces and outside sources you fetched. Each bullet: title, url, date (when known), why it is relevant.

## Write `{id-or-slug}-crosslinks.md` in `RUN_DIR`

The list of on-site URLs the draft must (or may) link to. Write a bulleted list.

Required: enough on-site pages for this thesis to meet `min_first_party_links`. Each bullet: `url` and `anchor_text` (a hint: a phrase the body would already say, not a page title or product name unless that phrase is already in the outline).

Approved additions: extra on-site URLs the draft may use. Each bullet: `url`, `suggested_anchor`, and `placement_note`.

End the file with `min_distinct_first_party_links:` and the number from config.

Log: `[run-debug] workflow=_workflows/generate/generate_article | RESEARCH | articles={n} required_links={n} inventory={path}`

Next: [../04_package_prompt/SKILL.md](../04_package_prompt/SKILL.md)
