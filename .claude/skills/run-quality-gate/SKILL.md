---
description: Runs an independent evidence-based gate for a submitted task. Use only when the reviewer is not the producer.
---

Read the task packet and acceptance criteria first. Do not rely on the producer’s conclusion. Use a clean checkout or isolated worktree. Reproduce the feature, rerun the required scenarios, inspect provenance, and check regressions.

Write a gate report using `docs/templates/GATE_REPORT.md`, then record PASS, FAIL, or BLOCKED with `python tools/project_control.py gate`. A failed gate must list reproducible defects.
