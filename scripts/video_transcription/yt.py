#!/usr/bin/env python3
"""Forward YouTube / audio transcription to Apple SpeechAnalyzer.

Whisper is not used. The procedure is:
  ~/git/ercule-internal/workflows/apple_speech_analyzer/SKILL.md
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def transcribe_script() -> Path:
    candidates = []
    env_root = os.environ.get("ERCULE_INTERNAL")
    if env_root:
        candidates.append(Path(env_root) / "workflows/apple_speech_analyzer/scripts/transcribe.py")
    candidates.append(Path.home() / "git/ercule-internal/workflows/apple_speech_analyzer/scripts/transcribe.py")
    # This file: <workspace>/scripts/video_transcription/yt.py
    candidates.append(
        Path(__file__).resolve().parents[4]
        / "ercule-internal/workflows/apple_speech_analyzer/scripts/transcribe.py"
    )
    for path in candidates:
        if path.is_file():
            return path
    sys.stderr.write(
        "Apple Speech Analyzer script not found. Expected "
        "$HOME/git/ercule-internal/workflows/apple_speech_analyzer/scripts/transcribe.py\n"
    )
    raise SystemExit(1)


if __name__ == "__main__":
    script = transcribe_script()
    os.execv(sys.executable, [sys.executable, str(script), *sys.argv[1:]])
