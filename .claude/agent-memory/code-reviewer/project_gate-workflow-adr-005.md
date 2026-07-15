---
name: gate-workflow-adr-005
description: ADR-005 gate workflow - reviewers are read-only, return verdicts in-message; only orchestrator writes ledger/git
metadata:
  type: project
---

Per docs/adr/ADR-005-agent-permission-and-gate-workflow.md (Accepted 2026-07-14): reviewers (code-reviewer included) run read-only, produce report content and RETURN it with an explicit PASS/FAIL/BLOCKED verdict; the orchestrator saves the report and records the gate via `python tools/project_control.py gate`. Producers never run ledger CLI/git-push/gh either.

**Why:** Background subagents cannot answer permission prompts, so ledger/git calls auto-denied and stalled two implementation waves; the fix centralizes all ledger/git writes in the main-session orchestrator.

**How to apply:** When invoked as G3 reviewer, ignore any skill instruction to write a gate report file or run `project_control.py gate` — return the full report as the final message instead. Do not modify any file under review. Expect producer reports to carry verbatim command outputs (evidence, not claims); flag when they don't. See [[vercel-dropped-frontend-on-render]] for a decision affecting review baselines.
