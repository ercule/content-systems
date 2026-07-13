---
name: find_faq_questions_04_gsc_questions
description: >-
  Step 04 for find_faq_questions: resolve the Google Search Console property,
  mine question candidates, and match them to Strategy topics.
"last updated": 2026-07-13T20:00:00+00:00
"last run": 2026-07-08
---

# Find FAQ questions — 04 GSC Questions

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

## Inputs

From [../02_sheet_and_topics/SKILL.md](../02_sheet_and_topics/SKILL.md):

- `strategy_topics` - the full Strategy topic list, used to regex-match GSC questions to topics.

Carried from [../03_source_collection/SKILL.md](../03_source_collection/SKILL.md), pass through unchanged:

- `source_bundles`
- `failed_sources_count`

From chat or caller:

- `workspace_slug` - optional. Short workspace identifier used to derive the GSC property and `main_domain_host`.
- `gsc_site_url` - optional. If omitted, derive from `workspace_slug`.
- `gsc_lookback_days` - optional, default `30`.
- `gsc_min_words` - optional, default `5`.
- `gsc_min_impressions` - optional, default `5`, meaning keep rows with impressions `>= 6`.

## Credentials

- Google OAuth for GSC: `{workspace_root}/credentials.json` at `google.oauth_token_unified`. The token must include `https://www.googleapis.com/auth/webmasters.readonly`.
- Optional fallback account: `{workspace_root}/credentials.json` at `google.oauth_token_unified_2`, if present. Used only when the primary token cannot read a matching property. Generate it with the standard Google OAuth installed-app flow (Desktop client in `google.oauth_installed_client`).

## 1. Resolve GSC Property

GSC always runs, so always resolve a property.

Resolve `gsc_site_url` in this order:

1. If the caller passed `gsc_site_url`, use it verbatim.
2. Else if `workspace_slug` is set, read `{workspace_root}/config.json` and collect candidate domains:
   - `gsc_site_url`, `site_url`, or `site` if present.
   - `webflow.domains[*]`.
   - Any `*_url` host.
3. Normalize each candidate to its apex host by dropping `www.`.
4. Verify against properties the token can read:

```http
GET https://searchconsole.googleapis.com/webmasters/v3/sites
Authorization: Bearer {access_token}
```

Each entry has a `permissionLevel`. Only `siteOwner`, `siteFullUser`, and `siteRestrictedUser` can read Search Analytics. `siteUnverifiedUser` is listed but has no data access and will return `403` on `searchAnalytics/query`. Treat only the first three levels as readable; ignore `siteUnverifiedUser` entries when matching a property.

Prefer a readable `sc-domain:{apex}`. Otherwise accept a readable URL-prefix property whose host matches the candidate host.

Set `main_domain_host` to the resolved apex host (e.g. `acme.com`) so the [generate_faq_responses](../../../generate/generate_faq_responses/SKILL.md) workflow can look up main-domain Response Pages. Derive it from the matched property, the passed `gsc_site_url`, or the first candidate domain from `{workspace_root}/config.json`. If no domain can be determined, set it to null.

If a candidate matches a property only at `siteUnverifiedUser`, skip GSC, log `gsc=skipped reason=insufficient_permission level=siteUnverifiedUser property={siteUrl}`, and report that the OAuth account must be granted Full or Restricted access to that property in Search Console (Settings -> Users and permissions). Do not attempt the query; it will `403`.

If the primary token finds no readable property (no match, or a match only at `siteUnverifiedUser`), and `google.oauth_token_unified_2` exists, refresh that fallback token and retry the sites lookup and property matching with it. Prefer the first account that yields a readable property. Log `gsc=fallback_token used=oauth_token_unified_2` when the fallback is what resolves the property.

If no readable property matches under any available token, skip GSC, log `gsc=skipped reason=no_property`, and report which domains and accounts were tried. Do not guess an unverified property.

## 2. Mine GSC Questions

Use the resolved GSC property.

Date window:

- `endDate`: today minus 3 days, unless the caller provided a known available end date.
- `startDate`: `endDate - gsc_lookback_days`.

### Build the topic regex query filter

Before querying, build one giant regex from the full `strategy_topics` list and pass it to GSC as a `query` dimension filter. This makes GSC return only queries that contain a topic's words in order.

Build it like this:

1. For each topic, lowercase it and replace every run of whitespace with `.*`.
2. Prepend `.*` to the start and append `.*` to the end of each topic term.
3. Concatenate all terms with `|`.

So `answer engine optimization` becomes `.*answer.*engine.*optimization.*`, and the full expression looks like:

```text
.*answer.*engine.*optimization.*|.*generative.*engine.*optimization.*|.*media.*outreach.*|...
```

GSC regex uses RE2. Lowercase the topic terms. The `.*` segments make each term a loose "contains these words in order" match.

Call Search Analytics with `query` and `page` dimensions, passing the regex as an `includingRegex` filter on `query`:

```http
POST https://searchconsole.googleapis.com/webmasters/v3/sites/{siteEncoded}/searchAnalytics/query
Authorization: Bearer {access_token}
Content-Type: application/json
```

```json
{
  "startDate": "YYYY-MM-DD",
  "endDate": "YYYY-MM-DD",
  "dimensions": ["query", "page"],
  "dimensionFilterGroups": [
    {
      "filters": [
        { "dimension": "query", "operator": "includingRegex", "expression": "{topic_regex_filter}" }
      ]
    }
  ],
  "rowLimit": 25000,
  "type": "web",
  "startRow": 0
}
```

Paginate by increasing `startRow` by `rowLimit` until a chunk returns fewer than `rowLimit` rows.

If GSC rejects the regex (e.g. it exceeds RE2 limits), drop the `dimensionFilterGroups` and fall back to the unfiltered query plus client-side filtering.

Keep only rows where:

- `impressions > gsc_min_impressions`.
- Query word count is at least `gsc_min_words`.
- The query contains `?`, or its first token is a question word.

Question words:

```text
who, what, when, where, why, how, which, whom, whose, can, could, should, would, will, do, does, did, is, are, was, were, has, have, am
```

Do not turn keyword phrases into questions. If a query only contains a question word mid-string, drop it unless it also contains `?`.

Normalize kept queries by trimming, collapsing whitespace, sentence-casing the first letter, and appending `?` if missing.

Then apply the [Question Quality Rules](../SKILL.md#question-quality-rules):

- Drop junk queries (LLM-probe instructions, context injection, multiple `?`, compound `...?` fragments, unrelated third-party brand probes).
- Keep only fully-formed questions (proper interrogative form, single trailing `?`).

Keep the surviving rows as the GSC question candidate list, each carrying its `query` (normalized question), `page`, and `impressions`.

### Match questions to topics by regex

Map questions to topics by running a per-topic regex against the whole candidate list, not by token overlap against the new-topics queue. Use the full `strategy_topics` list from [../02_sheet_and_topics/SKILL.md](../02_sheet_and_topics/SKILL.md), so every Strategy topic gets relevant questions even when it is already present in `FAQ Coverage`.

For each topic:

1. Build a case-insensitive regex from the topic phrase:
   - Escape regex metacharacters, then split the topic into significant words (drop one-letter glue words but keep meaningful short tokens).
   - Join the words with `\s+` so spacing variants match.
   - Allow an optional trailing `s` on each word so singular/plural both match (e.g. `feature flag` matches `feature flags`).
   - Treat `/` loosely, e.g. `a/b testing` -> `a\s*/?\s*b\s+test\w*`.
   - Example: `trunk based development` -> `trunk\s+based\s+development?` ; `progressive delivery` -> `progressive\s+deliver\w*`.
2. Match the regex against each candidate question (case-insensitive).
3. From the matches, rank by `impressions` descending and keep the top 5 (the GSC per-topic cap). These become rows with `Topic = {topic}`.

A question may match more than one topic's regex; that is fine. Run-level question dedupe in [../05_extract_and_append/SKILL.md](../05_extract_and_append/SKILL.md) ensures it is written only once, under the first topic that claims it. Process topics in `strategy_topics` order so the assignment is deterministic.

### Significant-word fallback before GSC

A full-phrase regex misses common real queries. Before falling back to `GSC`, run a second pass over the still-unassigned candidates that matches on each topic's distinctive word(s):

1. For each topic, drop generic modifier words (e.g. `policy`, `management`, `based`, `expense`, `travel`, `booking`) and keep the remaining significant token(s): `expense policy` -> `expense`, `travel booking` -> `travel` / `booking`, `receipt capture` -> `receipt`, `per diem limits` -> `diem`.
2. Build a case-insensitive regex from those significant token(s), using the same singular/plural handling as the full-phrase regex, and test it against each unassigned candidate.
3. Assign each unassigned question to the topic whose significant token it contains. When several topics qualify, pick the one whose token is the most specific (longest / rarest across `strategy_topics`). Respect the per-topic GSC cap of 5.

## Outputs For Next Step

Carry these values to [../05_extract_and_append/SKILL.md](../05_extract_and_append/SKILL.md):

- `gsc_questions`: array of `{ topic, question, source }`.
- `main_domain_host`: resolved site apex host for the responder's Response Page lookups, or null.
- `source_bundles`: passed through unchanged from step 03.
- `failed_sources_count`: passed through unchanged from step 03.

## Logging

```text
[run-debug] workflow=_workflows/find_faq_questions | GSC | property={siteUrl} window={start}..{end} rows_fetched=N kept_questions=N
```

## Checks

- [ ] GSC property resolved by readable `permissionLevel` (`siteOwner`/`siteFullUser`/`siteRestrictedUser`), or skipped with a clear reason (`insufficient_permission` for `siteUnverifiedUser`, `no_property` otherwise).
- [ ] `main_domain_host` resolved from the GSC property, passed `gsc_site_url`, or workspace config when available.
- [ ] GSC questions filtered with 5+ words, more than 5 impressions, and question-only logic.
- [ ] Junk queries dropped and only fully-formed questions kept.
- [ ] GSC questions matched to topics by per-topic regex over the full Strategy list, ranked by impressions.
- [ ] No more than 5 GSC questions per topic.
- [ ] No temporary files left behind.
