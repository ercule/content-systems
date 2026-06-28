# Scripts

All Python runners for this repository live here. Skills in `_workflows/` link here; they do not co-locate `.py` files.

Run from the **repo root** (the directory that contains `config.json` and `credentials.json`).

## Layout

| Path | Purpose |
|------|---------|
| `lib/workspace.py` | Resolve workspace root (`credentials.json`) and library root (`setup/run_workflow/SKILL.md`) |
| `lib/browserbase_live.py` | Browserbase live-session URL banner for terminal + agent handoff |
| `google_doc/apply_inline_doc_markup.py` | Paint red/blue inline editorial markup ([show_edits_in_google_doc](../_workflows/edit/show_edits_in_google_doc/SKILL.md)) |
| `google_doc/resolve_doc_markup.py` | Accept or reject inline markup ([accept_edits_google_doc](../_workflows/edit/accept_edits_google_doc/SKILL.md)) |
| `video_transcription/yt.py` | YouTube → Whisper local transcription ([youtube_transcription_yt](../_workflows/ops/youtube_transcription_yt/SKILL.md)) |
| `maintain/scan_step_zero.py` | Audit numbered step skills for run_workflow Step 0 |
| `maintain/scan_skill_links.py` | Find broken relative links in SKILL.md files |
| `maintain/scan_reacts_to.py` | Audit workflow `reacts to` metadata |
| `maintain/add_last_updated_yaml.py` | Backfill `last updated` frontmatter from Git |

## Hygiene checks

From the repo root:

```bash
python3 scripts/maintain/scan_step_zero.py
python3 scripts/maintain/scan_skill_links.py
python3 scripts/maintain/scan_reacts_to.py
```

These scan skills under this repository only.
