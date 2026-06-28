#!/usr/bin/env python3
"""Flag numbered workflow step SKILL.md files missing a run_workflow pointer."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from workspace import library_root  # noqa: E402

REPO_ROOT = library_root(__file__)
SKIP_DIR_NAMES = {".git", ".claude", "node_modules"}
TRANSIENT_PREP_PREFIX = "_submodule_prep"
STEP_DIR_RE = re.compile(r"^[0-9]{2}_")
RUN_WORKFLOW = REPO_ROOT / "setup" / "run_workflow" / "SKILL.md"


def should_skip(path: Path) -> bool:
    return any(
        p in SKIP_DIR_NAMES or p.startswith(TRANSIENT_PREP_PREFIX) for p in path.parts
    )


def run_workflow_link_ok(skill_path: Path) -> bool:
    skill_dir = skill_path.parent
    depth = len(skill_dir.relative_to(REPO_ROOT).parts)
    expected = skill_dir / ("../" * depth) / "setup" / "run_workflow" / "SKILL.md"
    return expected.resolve().samefile(RUN_WORKFLOW)


def main() -> int:
    missing_ref: list[Path] = []
    depth_wrong: list[Path] = []
    checked = 0

    for sp in sorted(REPO_ROOT.rglob("SKILL.md")):
        if should_skip(sp):
            continue
        if not STEP_DIR_RE.match(sp.parent.name):
            continue
        checked += 1
        text = sp.read_text(encoding="utf-8")
        if "setup/run_workflow/SKILL.md" not in text:
            missing_ref.append(sp)
            continue
        if not run_workflow_link_ok(sp):
            depth_wrong.append(sp)

    print(f"Numbered-step SKILL.md files scanned: {checked}")
    print(f"Missing run_workflow reference in body: {len(missing_ref)}")
    for p in missing_ref:
        print(f"  {p.relative_to(REPO_ROOT)}")
    print(
        "Mention run_workflow but relative path does not resolve to "
        f"setup/run_workflow: {len(depth_wrong)}"
    )
    for p in depth_wrong[:80]:
        print(f"  {p.relative_to(REPO_ROOT)}")
    if len(depth_wrong) > 80:
        print(f"  ... and {len(depth_wrong) - 80} more")

    return 1 if missing_ref or depth_wrong else 0


if __name__ == "__main__":
    sys.exit(main())
