"""Resolve content-systems library root and workspace root."""

from __future__ import annotations

from pathlib import Path


def library_root(from_file: str) -> Path:
    cur = Path(from_file).resolve().parent
    for _ in range(10):
        if (cur / "setup/run_workflow" / "SKILL.md").is_file():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    raise SystemExit(
        "Could not locate content-systems root (setup/run_workflow/SKILL.md)"
    )


def workspace_root(from_file: str) -> Path:
    cur = Path(from_file).resolve().parent
    for _ in range(10):
        if (cur / "credentials.json").is_file():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    raise SystemExit(
        "credentials.json not found — run from a workspace with Google OAuth configured"
    )
