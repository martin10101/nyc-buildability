# ADR-005 — Agent Permission and Gate Workflow

- **Status:** Accepted (owner-directed process correction)
- **Date:** 2026-07-14
- **Decider:** Project owner + orchestrator

## Context

Two implementation waves stalled on the same failure class:

1. Producer subagents launched **in the background** cannot answer permission prompts, so every git write, `gh` call, and `python` invocation auto-denied (M0-T004 producer: files authored but uncommitted; M0-T006 producer: deliverables complete but ledger calls denied; M0-T002 G1 reviewer: verdict reached but gate CLI denied).
2. The hook-installed session `settings.json` used invalid permission-rule syntax (`"Bash:*"` instead of `Bash(...)` patterns), so its blanket allows were silently ignored and everything fell back to prompting.
3. Read-only reviewer agents were being asked to run ledger CLI commands, which their (correct) read-only posture forbids.

## Audit results (session of 2026-07-14)

- Session root: `...\Downloads\nyc zoning` — one level ABOVE the project folder. Native agent registration initially failed for this reason (repaired by copying agent definitions up; future sessions should start in the project folder).
- Main session: not in Plan Mode; full write capability.
- Producers (ai-pipeline, backend, cloud-architect, frontend, geospatial, legal-corpus, official-source-researcher, qa, rules, scenario-optimization, supabase): `permissionMode: default`, worktree isolation, RW+Bash tools — correct for implementation.
- Reviewers (code-reviewer, data-contract-verifier, security-reviewer, human-journey-reviewer, progress-auditor): `permissionMode: plan`, read-only toolsets — correct for review, incompatible with ledger writes.

## Decision

1. **Only the main-session orchestrator runs `tools/project_control.py`** (new-task, claim, progress, submit, gate, accept, checkpoint), git integration (add/commit/push/merge), and `gh`. It does so only after validating the producer/reviewer evidence.
2. **Producers** work inside their assigned scope/worktree, write their producer report, and RETURN files-changed + evidence + requested status. They never run the ledger CLI, push, or gh.
3. **Reviewers** stay read-only, produce their report content, and RETURN it with an explicit PASS/FAIL/BLOCKED verdict. The orchestrator saves the report and records the gate.
4. **Background agents** are given only work that needs no interactive permissions; anything requiring shell writes runs foreground or is executed by the orchestrator.
5. **Narrow permission allowlist** added to session `settings.local.json` (correct syntax): `python tools/project_control.py *`, `python tools/test_project_control.py`, `pytest tools/`, `git add/commit/push origin/log/diff/show/branch/rev-parse/worktree list`, `git merge --no-ff task/*`, `gh run/workflow/pr view/pr checks`. No destructive rules (no `rm`, `git reset/clean`, force-push, or unrestricted shell).
6. All 17 agent definitions (both the project copy and the session-registered copy) now embed these protocols; `.claude/rules/project-control.md` codifies them.

## Regression proof

`tools/test_project_control.py` (stdlib-only, runs against a disposable temp project, never the real ledger) proves: producer can claim/progress/submit; producer cannot set 100% or gate its own task; a reviewer report recorded by the orchestrator gates the task; non-orchestrator acceptance is rejected; orchestrator acceptance requires all required gates PASS. Runs locally in <5 s and in CI (`control-plane` job).

## Consequences

- Subagent prompts disappear from the critical path; the orchestrator becomes the single ledger writer, matching the authority rules in `docs/PROJECT_CONTROL_PROTOCOL.md`.
- Producer reports must carry real command outputs since reviewers and the orchestrator act on evidence, not claims.
- M0-T002 and M0-T004 resume from their existing evidence; no completed research or implementation is rerun.
