# M0-T076 — G0 readiness (2026-08-19)

Directive: **D-019** (context-pipeline-promotion-blocker-closure), active, owner-authorized.
Task: **M0-T076**, one branch `task/M0-T076-context-blocker-closure`, one PR (to open).
Producer: orchestrator. Adversarial reviewer + directive-compliance-verifier: independent agents.

## Live reconciliation (read-only, complete)
- origin/main = HEAD = `3c108944f6b1abf23866351c696e7f09562ea498` — EXACT handoff checkpoint (not newer).
- Worktree clean (`git status --short` empty).
- Ledger: 98 accepted; M0-T075 present; M0-T076 and D-019 were unused before this task.
- No overlapping branch/PR (only unrelated #64).
- `validate_directive_compliance.py` → exit 0 (19 directives with D-019).
- Baseline context-pipeline suites @ 3c10894 (clean clone): 229 passed, 1 skipped.

## Pre-change failure records (reproduced from a CLEAN clone @ 3c10894 — not trusting prior PASS)
- **A** lock publication/reclaim race → both writers report `promoted`, one node lost.
- **B** `--ci-summary` absolute read+included exit 0 (marker leaked); refused `--include` echoes the caller-supplied absolute path; refused include still sufficient/exit 0.
- **C** clean-main e2e benchmark exits 2 (`git_diff` baseline source missing on clean tree).
- **D** reviewer packet default `--diff-base HEAD` on a committed branch exits 3; frozen parent base exits 0.
- **E** routing emits `concurrency_or_performance=false` with `ambiguity=false`; alphabetical `MAX_SEEDS=5` drops the principal impl file; compiler never imports `repo_views`; advisory memory rows carry only id/outcome/agent.

Full detail: this task's producer report + counterexample matrix.

## Scope confirmation
Within D-019 hard limits: no `tools/agent_supervisor/**`, protected config, apps/services/packages/supabase, NYC logic, code-graph generators/fingerprint/baseline, limited-auto, history, or D-013-R060 promotion. R060 stays owner-gated.

## Readiness verdict: READY.
Acceptance scenarios AS-1..AS-10 and required proofs 1–12 are defined; the frozen base for this task's diff is its G0 parent `3c108944…`.
