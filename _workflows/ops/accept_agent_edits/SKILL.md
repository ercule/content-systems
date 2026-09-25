---
name: accept_agent_edits
description: >-
  Accept or reject inline red-strikethrough / blue-addition editorial markup in a
  Google Doc after agent_editor. Trigger on "accept agent edits", "accept changes",
  "reject changes", "keep blue text", "remove red markup", or finalize editorial markup.
"last updated": 2026-09-20T20:00:00+00:00
"last run": 2026-09-21
---

# Accept agent edits (inline markup)

Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) before running this step.

Log prefix: `[run-debug] workflow=accept_agent_edits | RESOLVE | <facts>`

Run after [agent_editor](../agent_editor/SKILL.md) has painted red/blue markup and the human has reviewed the Doc.

Typical pipeline: editorial workflow → plan JSON → [agent_editor](../agent_editor/SKILL.md) → human review → this skill.

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

Before accept: confirm inserted sections use correct `namedStyleType`. See [agent_editor paragraph styles](../agent_editor/SKILL.md#paragraph-styles-required-second-pass).

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| `DOC_ID` | Yes | Same Doc that received inline markup |

## Run

Follow the Google Docs API steps above. Workspaces may provide a local runner; this public repo ships the skill procedure only.

```bash
# Preview counts (no mutation) — example workspace runner (optional):
python3 scripts/google_doc/resolve_doc_markup.py \
  "https://docs.google.com/document/d/{DOC_ID}/edit" accept --dry-run \
  --workspace {workspace_root}

# Accept all markup (keep blue, delete red)
python3 scripts/google_doc/resolve_doc_markup.py \
  "https://docs.google.com/document/d/{DOC_ID}/edit" accept \
  --workspace {workspace_root}

# Reject all markup (delete blue, restore red)
python3 scripts/google_doc/resolve_doc_markup.py \
  "https://docs.google.com/document/d/{DOC_ID}/edit" reject \
  --workspace {workspace_root}
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

## Staging gate

Do not stage or publish a Doc that still has red strikethrough or blue-addition markup. Run `resolve_doc_markup.py … accept --dry-run` first. If counts are non-zero, stop and tell the user to run this skill (accept or reject) before `{workspace_root}/_workflows/stage_content`.

## Related

- [agent_editor](../agent_editor/SKILL.md) — paint approved plan as inline markup
- [update_agent](../../edit/update_agent/SKILL.md) — produce path that paints markup and must not auto-accept
