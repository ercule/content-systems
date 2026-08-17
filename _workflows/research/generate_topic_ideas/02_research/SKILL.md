---
name: generate_topic_ideas_02_research
description: >-
  Step 02 for generate_topic_ideas: research the brand, competitors, and
  category trends, then write structured notes for draft and score.
"last updated": 2026-08-16T00:00:00+00:00
"last run": 2026-08-16
---

# Generate topic ideas — 02 Research

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

You are an SEO / AEO / generative-overview strategist. Starting from a brand, gather the notes that later become 30–45 short, unbranded, brand-adjacent topics. Write notes only in this step. Final topics wait for [../03_draft_and_score/SKILL.md](../03_draft_and_score/SKILL.md).

## Inputs

From [../01_preflight/SKILL.md](../01_preflight/SKILL.md):

- `brand_title`
- `brand_domain`
- `spreadsheet_id`
- `workspace_root`

## Credentials

- SerpAPI: `{workspace_root}/credentials.json` at `serpapi.api_key`.

## Fetch helper

Use [fetch_url](../../../ops/fetch_url/SKILL.md) for brand and competitor pages. Cap each page at the fetch_url limit. On a non-2xx fetch, log status and continue with the pages that succeeded.

## SerpAPI helper

```http
GET https://serpapi.com/search
```

Params: `engine=google`, `q={query}`, `api_key` from credentials. Read `organic_results` (`link`, `title`, `snippet`). Ignore ads, people-also-ask, and knowledge graph. One page of results is enough for each query in this step.

## STEP 1 — Brand/product research

Research `brand_title` using `https://{brand_domain}` and the web.

1. Fetch the homepage with fetch_url.
2. Fetch up to two linked product, platform, solutions, or use-case pages from that homepage.
3. Determine the brand's primary business category (1–4 words). Use this category wherever later steps say "the category".

Summarize:

- 3–7 core product pillars
- 3–7 core customer use cases or outcomes
- 5–10 recurring concepts or phrases in their messaging

Output a short structured summary. Leave topics for step 03.

## STEP 2 — Competitor research

Identify 3–7 direct or close competitors in the same category.

1. SerpAPI query: `{brand_title} competitors`
2. SerpAPI query: `{category} software` or `{category} platform` when that is a better category query
3. Fetch the homepage (and one product/solutions page when linked) for up to five competitors

Output:

- Competitor names with 1-sentence descriptions
- 10–20 recurring topic themes across competitors (short labels, 1–4 words, unbranded)
- Gaps or angles `brand_title` could own

Leave final topics for step 03.

## STEP 3 — Industry trends

For the category, research industry trends, best practices, and common challenges.

SerpAPI queries:

- `{category} trends`
- `{category} best practices`
- `{category} challenges`
- `{category} analytics`
- `{category} AI`

Run at least the first three. Use titles and snippets; fetch a page only when a snippet is too thin to name a theme.

Output 10–20 short, unbranded, conceptual topics (1–4 words) that appear frequently in neutral, analyst, or industry content. Leave the final list for step 03.

## Write notes

Save the STEP 1–3 notes to `{workspace_root}/tmp/generate_topic_ideas/research_notes.md`. Include the resolved category string at the top.

Log: `[run-debug] workflow=_workflows/generate_topic_ideas | RESEARCH | brand_pages=N competitors=N trend_queries=N category="{category}"`

Next: [../03_draft_and_score/SKILL.md](../03_draft_and_score/SKILL.md)
