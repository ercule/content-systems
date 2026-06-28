---
name: utilities_youtube_transcription_yt
description: >-
  Run the shared YouTube → Whisper script yt.py for local transcripts when
  captions APIs or timedtext are unavailable. Use when the user asks for
  yt-dlp/Whisper transcription or points at scripts/video_transcription/yt.py.
"last updated": 2026-05-24T00:00:00+00:00
"last run": 2026-06-14
---

# YouTube transcription (`yt.py`)

Local utility in this repository: `scripts/video_transcription/yt.py`.

Many workspace workflows use [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) with an HTTP-first contract (timedtext, vendor APIs, etc.). This skill is separate: it runs Python on the machine, downloads audio with yt-dlp, and transcribes with OpenAI Whisper. Use it only when that local stack is appropriate (developer machine, batch jobs, or when the user explicitly wants Whisper output).

## When to use

- User asks to transcribe a YouTube URL with the repo script or `yt.py`.
- HTTP caption fetches return empty or blocked and the user agrees to a local fallback.
- You need a plain-text transcript file on disk for downstream editing (not for skills that forbid local runners—check the active workflow).

## Prerequisites

A repo-local venv lives at `scripts/video_transcription/.venv` (created with `python3.13 -m venv .venv`). It already has `yt-dlp` and `openai-whisper` installed. Use it for every run; do not `pip install --user` against Homebrew Python (PEP 668 will block it).

If the venv is missing, recreate it once:

```bash
cd scripts/video_transcription
python3.13 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install yt-dlp openai-whisper
```

FFmpeg must be on `PATH` (yt-dlp uses it for audio extract; install with `brew install ffmpeg`). Whisper downloads model weights on first use (`WHISPER_MODEL` defaults to `base` in the script; edit `yt.py` to change).

## How to run

From the script directory (recommended so `downloads/` and `youtube_transcripts/` land next to the script unless you change paths in code), using the local venv:

```bash
cd scripts/video_transcription
.venv/bin/python yt.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

Multiple URLs in one invocation:

```bash
.venv/bin/python yt.py "https://youtu.be/AAAA" "https://youtu.be/BBBB"
```

From repo root without `cd` (still uses the venv interpreter, but outputs land in the current working directory — prefer `cd` for predictable paths):

```bash
scripts/video_transcription/.venv/bin/python scripts/video_transcription/yt.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Outputs

- `youtube_transcripts/<safe_title>_transcript.txt` — title line, separator, full transcript text.
- Temporary `downloads/` MP3s are removed after a successful run per video.

## Operational notes

- First run can take 30–60+ seconds loading Whisper; transcription time scales with audio length and model size.
- Respect copyright and site terms; use for internal / licensed content as appropriate.
- If installs fail, print the error and fix the environment (missing FFmpeg, CUDA drivers, etc.) before retrying.

## Related

- [Run a skill (shared context)](../../../setup/run_workflow/SKILL.md) — default patterns for credential-backed HTTP workflows.
- Script source: [`../../scripts/video_transcription/yt.py`](../../../scripts/video_transcription/yt.py)
