---
name: g5-gate-recording-protocol
description: How to resolve the run-quality-gate skill vs ADR-005 conflict - reviewers never run the ledger CLI; return the report, orchestrator records the gate
metadata:
  type: feedback
---

When acting as G5 security reviewer, do NOT run `python tools/project_control.py gate` or write gate/report files, even though the run-quality-gate skill text says to. ADR-005 (docs/adr/ADR-005-agent-permission-and-gate-workflow.md) supersedes it: reviewers stay read-only, RETURN the report content with an explicit PASS/FAIL/BLOCKED verdict, and the orchestrator saves the report and records the gate.

**Why:** Reviewer agents run with a read-only posture; earlier waves stalled when reviewers attempted ledger CLI writes and got permission-denied (documented in ADR-005 audit). Only the main-session orchestrator is the ledger writer.

**How to apply:** In any run-quality-gate invocation for this project, do all evidence gathering with read-only commands (git log/diff/show, git grep, gh run list/view work for the reviewer session as of 2026-07-14), then return the full report as the final message. Note explicitly in the report that gate recording is delegated to the orchestrator per ADR-005.
