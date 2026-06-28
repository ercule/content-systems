#!/usr/bin/env python3
"""Insert `last updated` into SKILL.md YAML frontmatter when missing (Git commit date)."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from workspace import library_root  # noqa: E402

REPO_ROOT = library_root(__file__)
SKIP_DIR_NAMES = {".git", ".claude", "node_modules"}
SUBMODULE_PREP_PREFIX = "_submodule_prep"

HAS_DATE = re.compile(
    r"(?m)^(?:\"last updated\"|'last updated'|last updated|last_updated)\s*:",
)
FM_OPEN = re.compile(r"^---\s*\n", re.MULTILINE)


def should_skip(path: Path) -> bool:
    return any(
        p in SKIP_DIR_NAMES or p.startswith(SUBMODULE_PREP_PREFIX) for p in path.parts
    )


def git_toplevel_and_rel(skill_path: Path) -> tuple[Path, str] | None:
    cur = skill_path.resolve().parent
    while True:
        p = subprocess.run(
            ["git", "-C", str(cur), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
        )
        if p.returncode == 0:
            top = Path(p.stdout.strip())
            rel = str(skill_path.resolve().relative_to(top))
            return top, rel
        if cur == cur.parent:
            return None
        cur = cur.parent


def last_commit_date(toplevel: Path, rel: str) -> str:
    r = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", rel],
        cwd=toplevel,
        capture_output=True,
        text=True,
    )
    d = (r.stdout or "").strip()
    return d if d else "1970-01-01"


def split_frontmatter(text: str) -> tuple[str, str, str, str] | None:
    """Return (opening --- line(s), fm_inner, closing --- line, body after frontmatter) or None."""
    if not text.startswith("---"):
        return None
    m = re.match(r"^(---\s*\n)([\s\S]*?)(\n---\s*(?:\n|$))", text)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3), text[m.end() :]


def add_field(fm_inner: str, date: str) -> str:
    line = f'"last updated": {date}\n'
    return fm_inner.rstrip() + "\n" + line


def process_file(skill_path: Path) -> str:
    text = skill_path.read_text(encoding="utf-8")
    parts = split_frontmatter(text)
    if not parts:
        return "no_frontmatter"
    pre, fm_inner, sep, rest = parts
    if HAS_DATE.search(fm_inner):
        return "skip_has_date"
    info = git_toplevel_and_rel(skill_path)
    if not info:
        return "no_git"
    top, rel = info
    date = last_commit_date(top, rel)
    new_text = pre + add_field(fm_inner, date) + sep + rest
    skill_path.write_text(new_text, encoding="utf-8")
    return f"updated:{date}"


def repair_missing_frontmatter_close(text: str) -> tuple[str, int]:
    """If the closing --- after frontmatter was dropped after last updated, restore it."""
    total = 0
    new_text = text
    for pattern, repl in (
        (r'("last updated": \d{4}-\d{2}-\d{2})\n(#)', r"\1\n---\n\n\2"),
        (r'("last updated": \d{4}-\d{2}-\d{2})\n(Step 0:)', r"\1\n---\n\n\2"),
    ):
        new_text, n = re.subn(pattern, repl, new_text, count=1)
        total += n
    return new_text, total


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--repair-close",
        action="store_true",
        help="Only fix files where closing --- was missing after last updated (one-time repair).",
    )
    args = ap.parse_args()

    skills = sorted(
        p
        for p in REPO_ROOT.rglob("SKILL.md")
        if p.is_file() and not should_skip(p)
    )

    if args.repair_close:
        fixed = 0
        for sp in skills:
            text = sp.read_text(encoding="utf-8")
            new_text, n = repair_missing_frontmatter_close(text)
            if n:
                sp.write_text(new_text, encoding="utf-8")
                fixed += 1
        print(f"Repaired closing --- on {fixed} SKILL.md files")
        return 0

    counts: dict[str, int] = {}
    for sp in skills:
        status = process_file(sp)
        counts[status] = counts.get(status, 0) + 1

    print(f"SKILL.md files seen: {len(skills)}")
    for k in sorted(counts, key=lambda x: (-counts[x], x)):
        print(f"  {k}: {counts[k]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
