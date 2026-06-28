---
name: evaluate_content
description: >-
  Scores editorial content for publication risk and outputs a structured review card.
  Uses criteria.md, brand.md, and optional examples.md over HTTP when calibrating.
"last updated": 2026-06-01T00:58:13+00:00
"last run": 2026-06-01T00:58:13+00:00
---

# Evaluate content for publication (shared)

Step 0: Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) (workflow standards: runtime HTTP, logging, ephemeral rules).

Resolve `workspace_root` (directory with `config.json`) before running. Read workspace rubric files from `{workspace_root}/_context/evaluate_content/` (criteria.md, brand.md, examples.md, output-card-template.md). If that folder is missing, ask the user for the rubric location.

Scores content on the workspace four-dimension rubric, assigns Priority, checks escalation overrides, and outputs a structured card for a human publishing decision.

Quick reference:

- Scoring and overrides: [{workspace_root}/_context/evaluate_content/criteria.md]
- Voice: [{workspace_root}/_context/evaluate_content/brand.md]
- Calibration examples: [{workspace_root}/_context/evaluate_content/examples.md]
- Output card template: [{workspace_root}/_context/evaluate_content/output-card-template.md]

## Workflow

1. Score dimensions 1 to 3 per the rubric in [{workspace_root}/_context/evaluate_content/criteria.md] with one short justification each. Dimensions are Factual Risk, Verification Feasibility, Topic Sensitivity, and Editorial Alignment (1 low risk, 3 high risk per criteria).
2. Assign Priority High, Medium, or Low from the Priority table in [{workspace_root}/_context/evaluate_content/criteria.md]. Priority is separate from the numeric risk total.
3. Check all five escalation overrides in [{workspace_root}/_context/evaluate_content/criteria.md]. Flag any that apply.
4. If a score is borderline, read [{workspace_root}/_context/evaluate_content/examples.md] and HTTP GET a relevant example URL from that file. Skip heavy fetching on routine runs. If the URL fails, fall back to the Scores and Notes in [{workspace_root}/_context/evaluate_content/examples.md] and continue.
5. Render the card using [{workspace_root}/_context/evaluate_content/output-card-template.md]. Populate Specific Review Items only for concrete, high-confidence findings.

## Cleanup

This skill writes nothing to disk. Deliver the rendered card in chat. Do not save scratch files.
