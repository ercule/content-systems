---
name: utilities_youtube_transcription
description: >-
  Transcribe a YouTube URL or local audio file with Apple SpeechAnalyzer.
  Do not use Whisper or YouTube captions. Use when a workflow needs a transcript.
"last updated": 2026-10-18T23:50:00+00:00
"last run": never
---

# YouTube transcription

Do not use Whisper, mlx-whisper, openai-whisper, the Whisper API, or YouTube timedtext.

Follow [apple_speech_analyzer](../../../../../ercule-internal/workflows/apple_speech_analyzer/SKILL.md) (`$HOME/git/ercule-internal/workflows/apple_speech_analyzer/SKILL.md`). That skill is the procedure. Do not restate it here.

## Run

Outside the Cursor sandbox (`required_permissions: ["all"]`):

```bash
python3 {content_systems_public_root}/scripts/video_transcription/yt.py \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

`yt.py` forwards every argument to `scripts/transcribe.py`, including `--phrases` and `--output-dir`.

Read the path printed as `Transcript saved to:`. Drop the title line and the `====` separator. The body is the transcript. The script deletes the audio.
