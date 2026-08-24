---
name: find_faq_questions_02_sheet_and_topics
description: >-
  Step 02 for find_faq_questions: resolve the Google Sheet, validate Strategy
  and FAQ Coverage tabs, map headers, and build the topic queue plus dedupe sets.
"last updated": 2026-08-06T12:00:00+00:00
"last run": 2026-08-23
---

# Find FAQ questions — 02 Sheet And Topics

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

## Inputs

- `sheet_url_or_id` - required. Google Sheet URL or bare spreadsheet ID.
- `topics` - optional. Comma-separated Strategy topic names to scope this run (case-insensitive).

## Credentials

- Google OAuth: `{workspace_root}/credentials.json` at `google.oauth_token_unified`.

Refresh the Google access token once at the start of the workflow. Use it for every Sheets API call. Do not log tokens.

## 1. Resolve Spreadsheet And Tabs

1. Extract `spreadsheet_id` from `sheet_url_or_id`.
2. Call:

```http
GET https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}?fields=properties(title),sheets(properties(sheetId,title))
Authorization: Bearer {access_token}
```

3. Resolve tabs by title, not by gid:
   - Strategy tab: exact `🎯 Strategy`; fallback to any title containing `Strategy`.
   - FAQ tab: exact `FAQ Coverage`; fallback to any title containing `FAQ Coverage`.
4. If either tab is missing, stop and report the available tab titles.

Log:

```text
[run-debug] workflow=_workflows/find_faq_questions | SHEET | title="..." strategy="..." faq="..."
```

## 2. Map Or Create FAQ Coverage Headers

Read row 1 from `FAQ Coverage`.

Required header names:

- `Topic`
- `Question`
- `Source`

Preferred full header row:

```text
Topic | Question | Source | LLM Response | Draft Response | Response Page | Mentioned | Topics | % Mentioned
```

If row 1 is empty, write the preferred header row.

If row 1 exists but any required header is missing, add the missing header at the end of the row. Do not rename existing headers unless the match is obvious and case-only.

Only this workflow's append step writes data. It writes `Topic`, `Question`, and `Source`. It must not write `Response Page` or `Draft Response`; those columns belong to the [generate_faq_responses](../../../generate/generate_faq_responses/SKILL.md) workflow.

## 3. Build Dedupe Sets

Read existing `FAQ Coverage` rows across the mapped columns.

Build:

- `existing_topics` from non-empty `Topic` cells.
- `existing_questions` from non-empty `Question` cells.
- `existing_sources` from URL-like `Source` cells.

Normalize questions by trimming, lowercasing, collapsing whitespace, and dropping a trailing `?` only for comparison.

Normalize source URLs by lowercasing scheme and host, dropping fragments, dropping common `utm_*` parameters, and trimming a trailing slash.

Log:

```text
[run-debug] workflow=_workflows/find_faq_questions | DEDUPE | existing_topics=N existing_questions=N existing_sources=N
```

## 4. Read Strategy Topics

Read `🎯 Strategy!A2:A`. Trim empty values and dedupe case-insensitively while preserving sheet order.

Build `strategy_topics_all`: the full deduped topic list after dropping empty and header-like values (`Topic`).

### Optional `topics` scope

When the caller passed `topics` (comma-separated names):

1. Split on commas, trim, and lowercase for matching.
2. Keep only Strategy rows whose normalized name equals one of the requested names (case-insensitive exact match on the topic cell).
3. If any requested name is missing from Strategy, stop and report the missing names plus the available Strategy topics.
4. Set `strategy_topics` to that filtered list (preserve Strategy sheet order). Both GSC regex matching and SERP use this scoped list.
5. Log: `[run-debug] workflow=_workflows/find_faq_questions | TOPICS_FILTER | requested=N matched=N names=...`

When `topics` is omitted, set `strategy_topics` = `strategy_topics_all` (unchanged behavior).

`strategy_topics` is used to regex-match GSC questions to topics in step 04, so when unscoped it still includes topics already present in `FAQ Coverage`.

Then build the SERP `topic_queue` from `strategy_topics` by skipping:

- Header-like values such as `Topic`.
- Topics already present in `existing_topics` — **except** when `topics` was passed explicitly; in that case re-run Reddit/LinkedIn for the requested topics even if they already appear in `FAQ Coverage` (still dedupe individual questions later).
- Exact normalized duplicate topics.

Cap the queue at `max_new_topics` unless `topics` already names a shorter explicit list (then use that list length as the effective cap).

If no topics remain, continue anyway: GSC always runs and mines questions on its own (scoped to `strategy_topics` when set). Tell the user there were no new Strategy topics, then proceed with GSC-only mining.

Log:

```text
[run-debug] workflow=_workflows/find_faq_questions | QUEUE | topics=N max={max_new_topics} scoped={yes|no}
```

## Outputs For Next Step

Carry these values to [../03_source_collection/SKILL.md](../03_source_collection/SKILL.md):

- `spreadsheet_id`
- `strategy_tab_title`
- `faq_tab_title`
- `header_map`
- `strategy_topics`
- `topic_queue`
- `existing_topics`
- `existing_questions`
- `existing_sources`

## Checks

- [ ] Google access token refreshed.
- [ ] Strategy and FAQ Coverage tabs resolved by title.
- [ ] Required FAQ Coverage headers exist.
- [ ] Existing topics, questions, and source URLs loaded.
- [ ] Full `strategy_topics` list built for GSC regex matching.
- [ ] Topic queue built and capped.

Next: [../03_source_collection/SKILL.md](../03_source_collection/SKILL.md)
