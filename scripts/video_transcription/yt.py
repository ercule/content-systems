#!/usr/bin/env python3
"""
YouTube Video Transcription Tool
Downloads YouTube videos and transcribes them using Whisper.

Agent / team instructions for running this script live in the repo skill:
  _workflows/ops/youtube_transcription_yt/SKILL.md
(that file also explains when to prefer HTTP caption flows from run_workflow).

Usage:
    python yt.py <youtube_url> [youtube_url2] [youtube_url3] ...

Example:
    python yt.py https://youtu.be/PvDPYGnhGQU
    python yt.py https://youtu.be/PvDPYGnhGQU https://youtu.be/t-IfyNlWBD0

Requirements:
    pip install yt-dlp whisper openai-whisper
"""

import os
import sys
from pathlib import Path

print("Loading libraries... (this may take 30-60 seconds on first run)")

try:
    import yt_dlp
except ImportError:
    print("ERROR: yt-dlp is not installed")
    print("Install it with: pip install yt-dlp")
    sys.exit(1)

try:
    import whisper
except ImportError:
    print("ERROR: whisper is not installed")
    print("Install it with: pip install openai-whisper")
    sys.exit(1)


# Configuration
WHISPER_MODEL = "base"  # Options: tiny, base, small, medium, large
OUTPUT_DIR = "youtube_transcripts"


def download_youtube_video(url, output_dir="downloads"):
    """Download YouTube video using yt-dlp."""
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n{'=' * 80}")
    print(f"Downloading video from: {url}")
    print(f"{'=' * 80}")

    # Configure yt-dlp options
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "quiet": False,
        "no_warnings": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info first
            info = ydl.extract_info(url, download=False)
            video_title = info.get("title", "Unknown")
            print(f"Title: {video_title}")

            # Download
            print("\nDownloading...")
            info = ydl.extract_info(url, download=True)

            # Get the downloaded filename
            filename = ydl.prepare_filename(info)
            # Replace extension with mp3
            audio_file = os.path.splitext(filename)[0] + ".mp3"

            print(f"✓ Downloaded: {audio_file}")
            return audio_file, video_title

    except Exception as e:
        print(f"✗ Error downloading video: {str(e)}")
        return None, None


def transcribe_audio(audio_path, model):
    """Transcribe audio using Whisper."""
    print(f"\nTranscribing...")

    try:
        result = model.transcribe(audio_path)
        print(f"✓ Transcription complete")
        return result["text"]
    except Exception as e:
        print(f"✗ Error transcribing: {str(e)}")
        return None


def save_transcript(transcript_text, video_title, output_dir):
    """Save transcript to file."""
    os.makedirs(output_dir, exist_ok=True)

    # Clean filename
    safe_title = "".join(
        c for c in video_title if c.isalnum() or c in (" ", "-", "_")
    ).strip()
    safe_title = safe_title[:100]  # Limit length

    transcript_path = os.path.join(output_dir, f"{safe_title}_transcript.txt")

    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(f"Title: {video_title}\n")
        f.write("=" * 80 + "\n\n")
        f.write(transcript_text)

    print(f"✓ Transcript saved to: {transcript_path}")
    return transcript_path


def main():
    """Main function."""
    print("=" * 80)
    print("YouTube Video Transcription Tool")
    print("=" * 80)

    # Check command line arguments
    if len(sys.argv) < 2:
        print("\nUsage: python yt.py <youtube_url> [youtube_url2] ...")
        print("\nExample:")
        print("  python yt.py https://youtu.be/PvDPYGnhGQU")
        print(
            "  python yt.py https://youtu.be/PvDPYGnhGQU https://youtu.be/t-IfyNlWBD0"
        )
        sys.exit(1)

    urls = sys.argv[1:]
    print(f"\nProcessing {len(urls)} video(s)...")

    # Load Whisper model once
    print(f"\nLoading Whisper model ({WHISPER_MODEL})...")
    try:
        model = whisper.load_model(WHISPER_MODEL)
        print("✓ Model loaded")
    except Exception as e:
        print(f"✗ Error loading Whisper model: {str(e)}")
        sys.exit(1)

    # Process each URL
    results = []
    for i, url in enumerate(urls, 1):
        print(f"\n{'=' * 80}")
        print(f"Video {i}/{len(urls)}")
        print(f"{'=' * 80}")

        try:
            # Download video
            audio_path, video_title = download_youtube_video(url)
            if not audio_path or not video_title:
                results.append(
                    {"url": url, "status": "failed", "error": "Download failed"}
                )
                continue

            # Transcribe
            transcript = transcribe_audio(audio_path, model)
            if not transcript:
                results.append(
                    {"url": url, "status": "failed", "error": "Transcription failed"}
                )
                continue

            # Save transcript
            transcript_path = save_transcript(transcript, video_title, OUTPUT_DIR)

            # Clean up audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)
                print(f"✓ Cleaned up: {audio_path}")

            results.append(
                {
                    "url": url,
                    "status": "success",
                    "title": video_title,
                    "transcript_path": transcript_path,
                }
            )

        except Exception as e:
            print(f"✗ Error processing {url}: {str(e)}")
            results.append({"url": url, "status": "failed", "error": str(e)})

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "failed"]

    print(f"\n✓ Successful: {len(successful)}/{len(results)}")
    for result in successful:
        print(f"  • {result['title']}")
        print(f"    → {result['transcript_path']}")

    if failed:
        print(f"\n✗ Failed: {len(failed)}/{len(results)}")
        for result in failed:
            print(f"  • {result['url']}")
            print(f"    → Error: {result.get('error', 'Unknown error')}")

    print("\n" + "=" * 80)
    print(f"Transcripts saved to: {OUTPUT_DIR}/")
    print("=" * 80)


if __name__ == "__main__":
    main()
