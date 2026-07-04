---
name: accept_edits_google_doc
description: >-
  Accept or reject inline red-strikethrough / blue-addition editorial markup in a
  Google Doc after show_edits_in_google_doc. Trigger on "accept changes",
  "reject changes", "keep blue text", "remove red markup", or finalize editorial markup.
"last updated": 2026-06-28T23:30:00+00:00
"last run": never
---

# Accept edits in a Google Doc (inline markup)

Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) before running this step.

Log prefix: `[run-debug] workflow=accept_edits_google_doc | RESOLVE | <facts>`

Run after [show_edits_in_google_doc](../show_edits_in_google_doc/SKILL.md) has painted red/blue markup and the human has reviewed the Doc.

Typical pipeline: editorial workflow → plan JSON → [show_edits_in_google_doc](../show_edits_in_google_doc/SKILL.md) → human review → this skill.

## Modes

| Mode | Keep | Remove | Reset styling |
|------|------|--------|---------------|
| **accept** | Blue additions | Red strikethrough deletions | Blue → default body black |
| **reject** | Red original text | Blue additions | Red → default body black (strikethrough removed) |

## Markup detection

| Role | Strikethrough | RGB (approx) |
|------|---------------|--------------|
| Deletion | yes | 0.77, 0.13, 0.12 |
| Addition | no | 0.0, 0.4, 0.8 |

Tolerance ±0.08 per channel.

Before accept: confirm inserted sections use correct `namedStyleType`. See [show_edits_in_google_doc paragraph styles](../show_edits_in_google_doc/SKILL.md#paragraph-styles-required-second-pass).

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| `DOC_ID` | Yes | Same Doc that received inline markup |

## Run

Follow the Google Docs API steps above. Workspaces may provide a local runner; this public repo ships the skill procedure only.

```bash
# Preview counts (no mutation) — example workspace runner (optional):
python3 scripts/google_doc/resolve_doc_markup.py \
  "https://docs.google.com/document/d/{DOC_ID}/edit" accept --dry-run

# Accept all markup (keep blue, delete red)
python3 scripts/google_doc/resolve_doc_markup.py \
  "https://docs.google.com/document/d/{DOC_ID}/edit" accept

# Reject all markup (delete blue, restore red)
python3 scripts/google_doc/resolve_doc_markup.py \
  "https://docs.google.com/document/d/{DOC_ID}/edit" reject
```

## Credentials

Resolve from `{workspace_root}/credentials.json` per [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md):

```text
@credentials.json#google.oauth_token_unified
```

## Checks

- Missing `DOC_ID` → stop.
- Always run `--dry-run` first when the caller has not explicitly chosen accept vs reject.
- Zero matching markup on `--dry-run` or live run → stop with message.

## Output

- Mode, deletion/addition range counts, Doc URL.
- On live run: deleted range count and normalized (unstyled) range count.

## Related

- [show_edits_in_google_doc](../show_edits_in_google_doc/SKILL.md) — paint approved plan as inline markup
