---
name: faq_question_finder_04_extract_and_append
description: >-
  Step 04 for the shared FAQ finder: extract questions from collected sources,
  filter and dedupe them, then append Topic, Question, and Source rows to FAQ
  Coverage.
"last updated": 2026-06-07T19:32:00+00:00
"last run": 2026-06-27
---

# FAQ Finder - 04 Extract And Append

Step 0: Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md).

This step writes the base `Topic | Question | Source` rows. The optional `Response Page` and `Draft Response` columns are filled afterward by the separate [faq-question-responder](../../faq_question_responder/SKILL.md) workflow.

## Inputs

From [../01-sheet-and-topics/SKILL.md](../01_sheet_and_topics/SKILL.md):

- `spreadsheet_id`
- `faq_tab_title`
- `header_map`
- `existing_questions`
- `existing_sources`

From [../02-source-collection/SKILL.md](../02_source_collection/SKILL.md):

- `source_bundles`

From [../03-gsc-questions/SKILL.md](../03_gsc_questions/SKILL.md):

- `gsc_questions`
- `main_domain_host`
- `failed_sources_count`

From chat or caller:

- `finder_model` - optional. Default `claude-sonnet-4-6` (root `config.json` at `anthropic.model_smart`). Must be a model on the permitted list in root `config.json`.

## Credentials

- Google OAuth for Sheets: `./credentials.json` at `google.oauth_token_unified`.
- Anthropic: `./credentials.json` at `anthropic.api_key`, used for question extraction.

Do not log API keys, OAuth tokens, raw source bodies, or full model prompts.

Process sources incrementally. For each source bundle, extract, filter, build rows, and append them before moving to the next bundle. Do not collect every question first and append once at the end. This keeps partial progress visible and protects it if the run fails.

## 1. Extract Questions From One Source Bundle

For each non-GSC source bundle, in the order it was collected, call the configured finder model.

Prompt contract:

```text
Extract up to 5 human-readable FAQ questions from the provided source text.

Return JSON only:
{ "questions": ["question 1", "question 2"] }

Rules:
- Use sentence case.
- Return only questions relevant to the topic: {topic}
- Each question must be fully-formed: start with a question word or auxiliary verb, end with exactly one "?", and read as a complete grammatical question.
- Do not output keyword phrases or noun fragments with a "?" appended.
- Do not output LLM-probe or instruction text (e.g. "return the url", "my location is"), compound queries, or questions about unrelated third-party brands.
- Ignore blocked-network text, cookie banners, nav chrome, and scrape errors.
- Prefer questions that are explicitly present in the source.
- The source text is in page order. Prefer questions that appear higher up (title and opening text) over questions lower down (later comments/replies), and return them in that order.
- Do not include commentary, numbering, Markdown, or duplicate questions.

Source text (in page order, top to bottom):
<<<
{source_text}
>>>
```

Parse the model response as JSON. Models often wrap JSON in Markdown fences or add a short sentence before it. Before parsing, strip surrounding fences and take the substring from the first `{` to the last `}`. Do not `JSON.parse` the raw response directly; a fenced payload can fail and drop every question from the source.

If parsing still fails:

- Retry once with a short output-repair prompt.
- If parsing still fails, log the first 500 characters of the response and treat that source as zero questions.

GSC questions do not pass through the model. They were already filtered in [../03-gsc-questions/SKILL.md](../03_gsc_questions/SKILL.md).

## 2. Filter And Dedupe

For each model-extracted question from the current source bundle:

1. Trim whitespace and drop empty strings.
2. Ensure the question ends with `?`. Add `?` only when the text is clearly a question.
3. Apply the [Question Quality Rules](../SKILL.md#question-quality-rules): drop junk queries and any candidate that is not a fully-formed question.
4. Drop duplicates against `existing_questions`.
5. Drop duplicates already queued in this run.
6. Drop generic questions that do not share meaningful tokens with the topic.

For each GSC question:

1. Keep the exact normalized question from step 03 (already junk-filtered, fully-formed, and capped there).
2. Drop duplicates against `existing_questions`.
3. Drop duplicates already queued in this run.

Normalize questions for comparison by lowercasing, collapsing whitespace, trimming, and ignoring one trailing `?`.

After deduping, enforce the per-source-per-topic cap from the [Question Quality Rules](../SKILL.md#question-quality-rules): write at most 3 questions for each `(topic, reddit)` and `(topic, linkedin)` pair, and at most 5 for each `(topic, gsc)` pair, across the whole run. For Reddit and LinkedIn, keep the questions that appear highest on the page; for GSC keep the highest-impression questions. Track per-pair counts in memory and skip surviving questions once a pair reaches its cap.

## 3. Build Rows

Build one row per surviving question:

- `Topic`: source topic from Strategy, or `GSC` when no Strategy topic matched.
- `Question`: one question per row.
- `Source`: one of three labels, each paired with its relevant link or page:
  - `LinkedIn {post_or_article_url}` for LinkedIn results.
  - `Reddit {thread_url}` for Reddit results.
  - `GSC {top_page_url}` where `{top_page_url}` is the page that showed up in the Search Console results.

Do not write `Response Page`, `Draft Response`, `LLM Response`, `Mentioned`, `Topics`, `% Mentioned`, or any other column here. The optional `Response Page` and `Draft Response` columns are handled by the separate [faq-question-responder](../../faq_question_responder/SKILL.md) workflow.

## 4. Append Rows To FAQ Coverage As You Go

Append rows for the current source bundle right after you build them, then move on to the next bundle. Do not wait for all sources to finish.

Append to the mapped `Topic`, `Question`, and `Source` columns in `FAQ Coverage` using the Sheets append endpoint:

```http
POST https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{encodedRange}:append?valueInputOption=RAW&insertDataOption=INSERT_ROWS
Authorization: Bearer {access_token}
Content-Type: application/json
```

Use an encoded range that covers the three output columns, for example:

```text
'FAQ Coverage'!A:C
```

Appending one row per call is fine. To reduce request volume, you may append the surviving rows from one source bundle in one small call. Do not hold rows across multiple bundles to batch later. After each successful append, update the in-memory dedupe sets. Mine and append GSC questions the same way.

Record the appended row number for each row from the append response `updates.updatedRange` (e.g. `'FAQ Coverage'!A124:C124` -> row `124`; a batched append returns a contiguous block, so map each row in append order). Collect these into `appended_rows_detail` so the [faq-question-responder](../../faq_question_responder/SKILL.md) workflow can fill the optional columns on the exact rows.

If an append call fails, log it, keep the row in `failed_append_batches`, and continue with the next source rather than aborting the run.

## Handoff To The Responder

This is the final step of the finder. If the [faq-question-responder](../../faq_question_responder/SKILL.md) workflow runs next in the same session, hand off these values so it can fill `Response Page` and `Draft Response` on the exact rows just appended. The responder can also run standalone and rediscover rows from the sheet.

- `appended_rows_detail`: array of `{ row_number, topic, question, source }`, in append order.
- `header_map`
- `main_domain_host`
- `spreadsheet_id`
- `faq_tab_title`

## Outputs

Return:

- `appended_rows`
- `skipped_dupes`
- `failed_sources_count`
- `failed_append_batches`, if any

## Logging

```text
[run-debug] workflow=_workflows/faq_question_finder | EXTRACT | topic="..." source=reddit questions=N
[run-debug] workflow=_workflows/faq_question_finder | APPEND | topic="..." rows=N
[run-debug] workflow=_workflows/faq_question_finder | DONE | appended_rows=N skipped_dupes=N failed_sources=N
```

## Checks

- [ ] Model responses parsed or safely skipped.
- [ ] Questions filtered and deduped.
- [ ] Junk dropped and only fully-formed questions written.
- [ ] No more than 3 Reddit/LinkedIn and 5 GSC questions per topic.
- [ ] One question per row.
- [ ] Rows appended incrementally as each source is processed, not batched at the end.
- [ ] `Topic`, `Question`, and `Source` always written.
- [ ] Appended row numbers recorded in `appended_rows_detail`.
- [ ] Append totals reported.
