---
name: show_edits_in_google_doc
description: >-
  Paint an approved edit plan into a Google Doc as red-strikethrough / blue-addition
  inline markup so changes are visible in place. Requires inline-markup-plan.json
  from the caller or another workflow. Trigger on "show edits in the doc",
  "red blue markup", or apply editorial plan to Google Doc.
"last updated": 2026-06-28T23:30:00+00:00
"last run": never
---

# Show edits in a Google Doc (inline markup)

Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) before running this step.

Log prefix: `[run-debug] workflow=show_edits_in_google_doc | APPLY_INLINE | <facts>`

Does not read the Doc or invent edits. Another workflow or the caller supplies an approved markup plan; this skill paints it into the source Doc. After apply, the human reviews; run [accept_edits_google_doc](../accept_edits_google_doc/SKILL.md) to finalize.

Google Docs Suggest mode cannot be created via the Docs API. Red/blue inline markup is the substitute.

Typical pipeline: editorial workflow → plan JSON → this skill → human review → [accept_edits_google_doc](../accept_edits_google_doc/SKILL.md).

## Inputs

| Input | Required | Source |
|-------|----------|--------|
| `DOC_ID` | Yes | Target Google Doc |
| Plan JSON | Yes | Caller path or default `{workspace_root}/tmp/inline-markup-plan.json` |

If the plan file is missing, stop and ask the caller to supply one from their editorial workflow.

### Plan JSON schema

```json
{
  "replaces": [["old text verbatim", "new text"]],
  "styled_replaces": [
    {"old": "Old heading\n", "new": "New heading\n", "style": "HEADING_2"}
  ],
  "insert_after": [["anchor substring", " text to insert"]],
  "strike_only": ["text to strike without replacement"],
  "insert_section": {
    "insert_before": "anchor heading or phrase",
    "paragraph_style_anchor": "first line of inserted section for style pass",
    "blocks": [
      {"style": "HEADING_2", "text": "Section title\n"},
      {"style": "NORMAL_TEXT", "text": "Body paragraph.\n"}
    ]
  },
  "insert_sections": [],
  "trim_replacements": [["\n\n\nHeading", "\n\nHeading"]]
}
```

At least one of `replaces`, `styled_replaces`, `insert_after`, `strike_only`, `insert_section`, or `insert_sections` is required.

## Inline markup palette

| Role | Style |
|------|--------|
| Deletion | Red (~197, 34, 31) + strikethrough |
| Addition | Blue (~0, 102, 204), no strikethrough |

Pass order: color markup → insert section → paragraph styles → trim empty paragraphs.

### Paragraph styles (required second pass)

`insertText` at a heading boundary inherits that heading's style. After color markup, run a separate `updateParagraphStyle` pass per paragraph. Use single `\n` between paragraphs — never `\n\n`.

## Run

Follow the Google Docs API steps above. Workspaces may provide a local runner; this public repo ships the skill procedure only.

```bash
# Example workspace runner (optional):
python3 scripts/google_doc/apply_inline_doc_markup.py \
  "https://docs.google.com/document/d/{DOC_ID}/edit" \
  --plan {workspace_root}/tmp/inline-markup-plan.json
```

## Credentials

Resolve from `{workspace_root}/credentials.json` per [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md):

```text
@credentials.json#google.oauth_token_unified
```

| Scope | Use |
|-------|-----|
| `https://www.googleapis.com/auth/documents` | `documents.get`, `batchUpdate` |

Token refresh: [google_doc_to_markdown](../../ops/google_doc_to_markdown/SKILL.md). Do not log tokens.

## Checks

- Missing `DOC_ID` or plan file → stop.
- Empty plan → stop.
- Any `old text` substring not found → stop with the failing snippet (do not partial-apply).

## Output

- Doc URL with red/blue markup applied.
- Remind the user to review in the Doc, then run [accept_edits_google_doc](../accept_edits_google_doc/SKILL.md).

## Cleanup

Delete `{workspace_root}/tmp/inline-markup-plan.json` after a successful apply unless the caller asked to keep it.

## Related

- [accept_edits_google_doc](../accept_edits_google_doc/SKILL.md) — accept or reject inline markup after human review
