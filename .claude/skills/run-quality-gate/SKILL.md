---
description: Runs an independent evidence-based gate for a submitted task. Use only when the reviewer is not the producer.
---

Read the task packet and acceptance criteria first. Do not rely on the producer’s conclusion. Work from a clean checkout or the task's isolated worktree at the frozen reviewed SHA. Reproduce the feature, rerun the required scenarios, inspect provenance, and check regressions.

For any in-regime task (one carrying `directive_refs`), independently verify at the frozen SHA / content identity that **every** requirement AND **every** owner directive requirement named in the packet is actually satisfied — re-derive each from its source. Treat the producer's requirement-to-evidence map as claims to reproduce, not as evidence; any gap between a named directive requirement and reproducible evidence is a FAIL. Report every requirement ID individually (no "spot-checked"/"appears complete"). The independent `directive-compliance-verifier` agent performs this pass and its verdict is recorded in the directive's `verification.json` (producer ≠ verifier).

The reviewer is **read-only** (ADR-005 and `.claude/rules/project-control.md`): produce a gate report following `docs/templates/GATE_REPORT.md` and return its content plus a **PASS / FAIL / BLOCKED** verdict — with reproducible commands and outputs — to the orchestrator. Do **not** run `tools/project_control.py`, git, or `gh` (the read-only guard blocks these). The **orchestrator** saves the verbatim report and records the gate result with `python tools/project_control.py gate`. A FAIL must list reproducible defects; do not return BLOCKED solely because your sandbox cannot execute a command — request orchestrator-captured evidence and verify it.
