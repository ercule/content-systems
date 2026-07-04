---
name: utilities_youtube_transcription
description: >-
  Transcribe YouTube videos locally with yt-dlp and Whisper when caption APIs
  or timedtext are unavailable. Use when the user asks for a local transcript
  fallback.
"last updated": 2026-06-28T23:30:00+00:00
"last run": 2026-06-14
---

# YouTube transcription (local fallback)

Many workspace workflows use [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) with an HTTP-first contract (timedtext, vendor APIs, etc.). This skill is separate: it runs yt-dlp plus OpenAI Whisper on the machine. Use it only when that local stack is appropriate (developer machine, batch jobs, or when the user explicitly wants Whisper output).

## When to use

- User asks to transcribe a YouTube URL locally.
- HTTP caption fetches return empty or blocked and the user agrees to a local fallback.
- You need a plain-text transcript file on disk for downstream editing (not for skills that forbid local runners — check the active workflow).

## Prerequisites

- `yt-dlp` and `openai-whisper` installed in a workspace-local venv (not committed to this repo).
- FFmpeg on `PATH` (`brew install ffmpeg` on macOS).
- Whisper downloads model weights on first use (`base` is a reasonable default).

## How to run

From a workspace venv with yt-dlp and whisper installed:

```bash
yt-dlp -x --audio-format mp3 -o "downloads/%(title)s.%(ext)s" "https://www.youtube.com/watch?v=VIDEO_ID"
whisper downloads/*.mp3 --model base --output_dir youtube_transcripts --output_format txt
```

Write output to `{workspace_root}/tmp/` or another scratch directory gitignored by the workspace.

## Outputs

- Plain-text transcript file suitable for downstream editing.
- Remove temporary audio downloads after a successful run.

## Operational notes

- First run can take 30–60+ seconds loading Whisper; transcription time scales with audio length and model size.
- Respect copyright and site terms; use for internal / licensed content as appropriate.
- If installs fail, print the error and fix the environment (missing FFmpeg, etc.) before retrying.

## Related

- [Run a skill (shared context)](../../../setup/run_workflow/SKILL.md) — default patterns for credential-backed HTTP workflows.
