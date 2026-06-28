---
name: faq_question_responder
description: >-
  Shared FAQ question responder. Fills the Response Page and Draft Response
  columns on FAQ Coverage rows that already have Topic, Question, and Source
  (typically produced by the faq_question_finder workflow). Use when the user
  asks to draft responses, fill Response Page / Draft Response, or run the FAQ
  responder for a workspace sheet. Runs standalone against a sheet or as a
  follow-on to faq_question_finder.
"last updated": 2026-06-07
"last run": 2026-06-07
---

# FAQ Question Responder

Step 0: Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) (runtime HTTP, logging, ephemeral runs). Build calls at request time.

This workflow is a second pass over `FAQ Coverage` rows that already have `Topic | Question | Source` (the output of the [faq_question_finder](../faq_question_finder/SKILL.md) workflow). It fills two optional columns per row, and only when those columns already exist on the sheet (it never creates them):

- `Response Page` - the top main-domain page on the workspace site that ranks for the question's keyword. For `GSC` rows this is the page already captured in `Source`; for `Reddit`/`LinkedIn` rows it is found with a site-restricted SerpAPI lookup against the workspace's primary domain. Left blank when no main-domain page is found.
- `Draft Response` - a ~50-word answer that recapitulates whatever is on the `Response Page`, adding minimal new content. Left blank when there is no `Response Page` or the page cannot be fetched.

It never edits website pages and never writes `Topic`, `Question`, `Source`, `LLM Response`, `Mentioned`, `Topics`, or `% Mentioned`.

Log line prefix:

```text
[run-debug] workflow=_workflows/faq_question_responder | <PHASE> | <facts>
```

## Inputs

- `sheet_url_or_id` - required. Google Sheet URL or bare spreadsheet ID.
- `workspace_root` - optional. Repo root, used to derive `main_domain_host` and to merge ``{workspace_root}/credentials.json``.
- `gsc_site_url` - optional. Used to derive `main_domain_host` when workspace config does not supply a domain.
- `main_domain_host` - optional. The site apex host (e.g. `acme.com`) for Reddit/LinkedIn Response Page lookups. When omitted, derive it from `gsc_site_url`, then ``{workspace_root}/config.json`` candidate domains; if none can be determined, set it to null and skip Reddit/LinkedIn page lookups.
- `finder_model` - optional. Default `claude-sonnet-4-6` (root `config.json` at `anthropic.model_smart`). Must be a model on the permitted list in root `config.json`.
- `appended_rows_detail` - optional. When handed off directly from [faq_question_finder](../faq_question_finder/SKILL.md) in the same session, an array of `{ row_number, topic, question, source }` to fill. When absent, discover the rows from the sheet (see section 1).

## Credentials

Read credentials from `./credentials.json`; if a workspace wrapper calls this skill, merge ``{workspace_root}/credentials.json`` over the root values only for that run.

- Google OAuth for Sheets: `google.oauth_token_unified`. Refresh the access token once at the start of the run and reuse it for every Sheets call.
- SerpAPI: `serpapi.api_key`, used for main-domain page lookups on Reddit/LinkedIn rows.
- Anthropic: `anthropic.api_key`, used for `Draft Response` drafting.

Do not log API keys, OAuth tokens, raw page bodies, or full model prompts.

## 1. Resolve Sheet And Target Rows

Resolve the spreadsheet and the `FAQ Coverage` tab by title via the Sheets API (exact `FAQ Coverage`, fallback to any title containing `FAQ Coverage`). Read row 1 and build a `header_map` of `{ header -> { index, column_letter } }`.

Check each optional column independently in `header_map`:

- If neither `Response Page` nor `Draft Response` is present, stop now and report that there is nothing to fill.
- `Draft Response` depends on a resolved `Response Page`. If `Draft Response` is present but `Response Page` is not, still resolve the page in memory to draft from it, but do not write the page anywhere.

Then build the list of rows to process:

- If `appended_rows_detail` was handed off, use it directly.
- Otherwise read the data rows of `FAQ Coverage`, and select rows that have a non-empty `Topic`, `Question`, and `Source` but are missing at least one present optional column (`Response Page` blank, or `Draft Response` blank). Capture each as `{ row_number, topic, question, source }`. Skip rows already fully filled.

For each row, parse the source type and URL from its `source` value (`Reddit {url}`, `LinkedIn {url}`, or `GSC {page_url}`).

Log:

```text
[run-debug] workflow=_workflows/faq_question_responder | TARGETS | rows=N response_page={present|absent} draft_response={present|absent}
```

## 2. Resolve The Response Page

The target keyword is the question text itself.

- For `GSC` rows, reuse the page already captured in `source` (`GSC {page_url}`). That page already ranks on the main domain for the query, so it is the Response Page.
- For `Reddit` and `LinkedIn` rows, when `main_domain_host` is set, call SerpAPI with query `{question} site:{main_domain_host}` and take the top organic result URL whose host is on `main_domain_host`. If no organic result is on the main domain, leave `Response Page` blank.
- When `main_domain_host` is null, skip the lookup and leave `Response Page` blank.

## 3. Draft The Response

When a `Response Page` URL is resolved and the `Draft Response` column is present:

1. Fetch the page (it is the workspace's own main-domain page and should not be blocked). On fetch failure, leave `Draft Response` blank and continue.
2. Call the finder model to write a ~50-word recap.

Prompt contract:

```text
Write a single answer of about 50 words (45-55) to the question below, using only what the page says. Recapitulate the page's relevant content and add minimal new content of your own. No preamble, no markdown, no citations.

Question: {question}

Page text:
<<<
{page_text}
>>>
```

Trim the result to a single paragraph. If it is wildly off length (under 30 or over 70 words), retry once; otherwise keep it.

## 4. Write The Optional Cells

`Response Page` and `Draft Response` usually do not sit adjacent to `Topic | Question | Source` (the default header has `LLM Response` between `Source` and `Draft Response`), so write each optional value to its own cell rather than widening any range.

For each present optional column with a non-blank value, write it to the row's cell using the column letter mapped in `header_map` and the `row_number`:

```http
PUT https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{encodedCell}?valueInputOption=RAW
Authorization: Bearer {access_token}
Content-Type: application/json
```

where `{encodedCell}` is e.g. `'FAQ Coverage'!F124` for `Response Page` and `'FAQ Coverage'!E124` for `Draft Response`. Skip the write for a blank value. Never write to `LLM Response` or any unmapped column.

If a cell write fails, log it, keep the row in `failed_response_writes`, and continue with the next row rather than aborting the run.

## Outputs

Return:

- `response_pages_written`
- `draft_responses_written`
- `failed_response_writes`, if any

## Logging

```text
[run-debug] workflow=_workflows/faq_question_responder | RESPONSE | topic="..." response_page={url_or_none} draft_words=N
[run-debug] workflow=_workflows/faq_question_responder | DONE | response_pages_written=N draft_responses_written=N failed_response_writes=N
```

## Checks

- [ ] Sheet and `FAQ Coverage` tab resolved by title; `header_map` built.
- [ ] Skipped entirely when neither optional column exists.
- [ ] Target rows taken from `appended_rows_detail` handoff, or discovered from the sheet when running standalone.
- [ ] `Response Page` resolved per row (GSC page reused; Reddit/LinkedIn via site-restricted SerpAPI), or left blank.
- [ ] `Draft Response` is a ~50-word recap of the `Response Page` with minimal added content, or left blank.
- [ ] Optional values written to the exact row by mapped column letter.
- [ ] `LLM Response` and other non-responder columns left untouched.
- [ ] No temporary files left behind.
