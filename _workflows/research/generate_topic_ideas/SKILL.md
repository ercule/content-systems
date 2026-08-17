---
name: generate_topic_ideas
description: >-
  Shared topic-idea generator for Topic research sheets. Researches a brand,
  competitors, and category trends, then writes 30–45 unbranded 1–4 word topics
  with one tag and a 0–5 relevance score to the topicIdeas tab. Use when the
  user asks to generate topic ideas, fill topicIdeas, or run topic research
  for a workspace sheet.
"last updated": 2026-08-16T00:00:00+00:00
"last run": 2026-08-16
---

# Generate topic ideas

Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) before running this step.

Keep helper code ephemeral for this run only and remove it before finishing.

This workflow is the agent-run equivalent of the n8n `topic research 1.0` webhook (`POST topic-research/trigger`) and the Sheets menu Generate topic ideas. It writes only the `topicIdeas` tab. The Topics tab stays untouched.

Log line prefix:

```text
[run-debug] workflow=_workflows/generate_topic_ideas | <PHASE> | <facts>
```

## Inputs

- `sheet_url_or_id` — required. Google Sheet URL or bare spreadsheet ID.
- `workspace_root` — optional. Repo root used to merge `{workspace_root}/credentials.json` and to derive brand fields from `{workspace_root}/config.json`.
- `brand_title` — optional. Display name used in research. If omitted, resolve from `{workspace_root}/config.json` `workspace_name`, then confirm with the user.
- `brand_domain` — optional. Apex host. If omitted, resolve from `{workspace_root}/config.json` (`main_domain`, `domain`, or `workspace_domains`), then confirm with the user.
- `research_model` — optional. Default `claude-sonnet-4-6` (root `config.json` at `anthropic.model_smart`). Must be a model on the permitted list in root `config.json`.

Take the sheet, brand title, and domain from chat or from a workspace wrapper skill. Resolve those values at run time.

## Credentials

Read credentials from `{workspace_root}/credentials.json` (resolve `@ref` per run_workflow). When a workspace wrapper calls this skill, merge wrapper credentials over the root values only for that run.

- Google OAuth for Sheets: `google.oauth_token_unified`. Spreadsheets scope is required.
- SerpAPI key: `serpapi.api_key`.
- Anthropic key for draft and score: `anthropic.api_key`.

Refresh the Google access token once at the start of the run with `POST {token_uri}`. Reuse it for every Sheets call. Log credential names and hosts only.

## Sheet contract

Resolve tabs via the Sheets API by title. Working tab:

- `topicIdeas` — created when missing, then cleared and replaced for this run.

Header row (write this exact header):

```text
Topic | Tag | Rel
```

Columns:

- `Topic` — unbranded conceptual hub, 1–4 words, lowercase.
- `Tag` — one of 4–7 topical tags defined for this brand, lowercase.
- `Rel` — integer 0–5.

This workflow writes only `topicIdeas`. Other tabs (Topics, Strategy, topicReport, topicData, and the rest of a Topic research workbook) stay as they are.

Topic research 0.4 copies often have no `topicIdeas` tab. Creating it is expected.

## Topic quality rules

These rules apply to every row before it is written, in step 03:

- Length: 1–4 words, preferably 1–2. Letters and numbers only, plus punctuation that is part of a technical term.
- Form: unbranded conceptual hubs. Each topic can host many long-tail queries. Brand names, product names, and marketing slogans stay off the list.
- Case: Topic and Tag are lowercase.
- Tags: 4–7 short human-readable phrases (examples of tag style: `core data`, `analytics`, `supply chain`, `category & assortment`, `promotion & media`, `ai & agents`, `people & culture`). Each topic gets exactly one tag. Prefer tags that cover multiple topics.
- Relevance: 5 = core to the brand's product and main narrative; 4 = very important, strong adjacency; 3 = relevant but supporting; 2 = tangential or niche; 1–0 = weak.
- Count: 30–45 rows after prune. Draft 50–70 candidates, then merge near-duplicates and drop topics that are too generic, too long-tail, or only weakly connected to the brand.

## Run order

Run these child skills in order:

1. [01_preflight/SKILL.md](01_preflight/SKILL.md) — verify sheet access, credentials, and brand inputs.
2. [02_research/SKILL.md](02_research/SKILL.md) — brand, competitor, and category-trend notes.
3. [03_draft_and_score/SKILL.md](03_draft_and_score/SKILL.md) — draft, prune, tag, and score topics.
4. [04_write_sheet/SKILL.md](04_write_sheet/SKILL.md) — ensure `topicIdeas`, clear it, write header plus rows.

Wipe `{workspace_root}/tmp/generate_topic_ideas/` at the start of the run. Write step intermediates there. Wipe that folder again after step 04 succeeds.

The end state is a replaced `topicIdeas` tab with 30–45 `Topic | Tag | Rel` rows. No website pages are edited.

## Logging template

```text
[run-debug] workflow=_workflows/generate_topic_ideas | START | sheet={spreadsheet_id} brand="{brand_title}" domain={brand_domain}
[run-debug] workflow=_workflows/generate_topic_ideas | PREFLIGHT | ok sheet={spreadsheet_id}
[run-debug] workflow=_workflows/generate_topic_ideas | RESEARCH | brand_pages=N competitors=N trend_queries=N
[run-debug] workflow=_workflows/generate_topic_ideas | DRAFT | candidates=N kept=N tags=N
[run-debug] workflow=_workflows/generate_topic_ideas | SHEET | tab=topicIdeas created={true|false} rows=N
[run-debug] workflow=_workflows/generate_topic_ideas | DONE | rows=N sheet={spreadsheet_id}
```

## Checklist

```text
Task Progress:
- [ ] Sheet URL/ID confirmed from chat or wrapper
- [ ] brand_title and brand_domain confirmed
- [ ] Google access token refreshed
- [ ] [01_preflight/SKILL.md](01_preflight/SKILL.md) completed
- [ ] [02_research/SKILL.md](02_research/SKILL.md) completed
- [ ] [03_draft_and_score/SKILL.md](03_draft_and_score/SKILL.md) completed
- [ ] [04_write_sheet/SKILL.md](04_write_sheet/SKILL.md) completed
- [ ] Final summary includes row count, tag list, and sheet URL
```
