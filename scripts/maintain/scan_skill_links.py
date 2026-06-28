#!/usr/bin/env python3
"""Scan SKILL.md files for unresolved relative Markdown links."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from workspace import library_root  # noqa: E402

REPO_ROOT = library_root(__file__)
SKIP_DIR_NAMES = {".git", ".claude", "node_modules"}
# Transient setup dirs (any name beginning with this prefix) — skip during audits.
SUBMODULE_PREP_PREFIX = "_submodule_prep"
# Only real Markdown links `[label](target)` — avoids false positives in prose/code.
LINK_RE = re.compile(r"\[[^\]\n]*\]\(([^)]+)\)")


def should_skip(path: Path) -> bool:
    parts = path.parts
    return any(
        p in SKIP_DIR_NAMES or p.startswith(SUBMODULE_PREP_PREFIX) for p in parts
    )


def normalize_link(link: str) -> str | None:
    link = link.strip()
    if not link or link.startswith(("#", "http://", "https://", "mailto:", "vscode:", "tel:")):
        return None
    if link.startswith("//"):
        return None
    # Drop anchor/query for existence check
    base = link.split("#", 1)[0].split("?", 1)[0].strip()
    if not base or base in {"(url)", "url"}:
        return None
    return base


def check_file(skill_path: Path) -> list[tuple[str, str]]:
    """Return list of (link_text, issue)."""
    text = skill_path.read_text(encoding="utf-8")
    cwd = skill_path.parent
    issues: list[tuple[str, str]] = []
    for m in LINK_RE.finditer(text):
        raw = m.group(1)
        target = normalize_link(raw)
        if target is None:
            continue
        resolved = (cwd / target).resolve()
        try:
            resolved.relative_to(REPO_ROOT)
        except ValueError:
            issues.append((raw, "resolves outside repo"))
            continue
        if resolved.is_symlink():
            # symlinks uncommon; resolve for check
            if not resolved.exists():
                issues.append((raw, "missing (symlink broken)"))
        elif not resolved.exists():
            issues.append((raw, "missing"))
    return issues


def main() -> int:
    skills = sorted(
        p
        for p in REPO_ROOT.rglob("SKILL.md")
        if not should_skip(p)
    )
    bad: list[tuple[Path, list[tuple[str, str]]]] = []
    for sp in skills:
        iss = check_file(sp)
        if iss:
            bad.append((sp, iss))

    print(f"Scanned {len(skills)} SKILL.md files under {REPO_ROOT}")
    print(f"Files with unresolved relative links: {len(bad)}")
    for sp, iss in bad:
        rel = sp.relative_to(REPO_ROOT)
        print(f"\n{rel}")
        for raw, msg in iss:
            print(f"  {msg}: ({raw})")

    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
