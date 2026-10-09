---
description: Mandatory convergence method for REPEATED failures, commissioning failures, external CLI/provider incompatibilities, or conflicting evidence - freeze evidence, reproduce, trace the complete causal path, repair one bounded causal cluster, verify once at the frozen candidate, and finish with VERIFIED_CLOSED or one consolidated blocker report. Invoke BEFORE editing when a failure recurs, a live commissioning/supervised run fails, an external CLI or provider behaves incompatibly with expectations, or two pieces of evidence contradict each other. Do NOT invoke for an ordinary isolated failure with an already-proven cause. Manually invocable as /deficit-convergence.
---

# Deficit convergence — repeated-failure closure method (D-024 Amendment 51, R761–R766)

**Narrow trigger.** This skill governs REPEATED failures, commissioning failures, external
CLI/provider incompatibilities, and conflicting evidence. It does **not** apply to an ordinary
isolated failure whose cause is already proven — fix that directly under
`/engineering-reliability`. It **prohibits** turning every normal task into a repo-wide audit:
scope the closure to the failure surface actually observed, and stop expanding the moment the
causal cluster is bounded. Live reruns are never serial discovery; each rerun must be justified
by the closure matrix below.

## The 20 rules

1. Freeze and preserve canonical evidence before rerunning.
2. Reproduce the exact failure before editing.
3. Record live repo, worktree, branch, HEAD, status, origin, executable, version, model, and
   configuration identity.
4. Keep controller source, installed controller, control-plane checkout, and worker worktree
   identities separate.
5. Map the complete path from launch input through provider output, review, persistence, and
   external effects.
6. Locate all affected producers, consumers, validators, tests, documentation, and operator
   commands before changing code.
7. Probe real external CLI/provider boundaries early with the smallest safe test.
8. Compare behavior against an immutable known-good version or accepted candidate.
9. Group symptoms by root cause and distinguish primary, cascading, and NOT-RUN failures.
10. Repair the smallest complete causal cluster, not one symptom at a time.
11. Keep provider-facing schemas minimal; enforce unsupported constraints inside the controller.
12. Treat all model output as untrusted; factual identity must be observed and supplied by the
    controller.
13. Record raw argv, cwd, environment facts, timestamps, exit code, stdout/stderr digests, and
    process-tree settlement.
14. Capture PowerShell `$LASTEXITCODE` immediately; never let a pipe or later command replace it.
15. Use stable typed failure codes and preserve the original provider/runtime error.
16. Add positive, negative, and mutation tests that prove each important guard is load-bearing.
17. Run focused tests after each causal cluster and the complete affected suite once at the
    frozen final candidate.
18. Use immutable inputs and transactional backup, verification, and rollback for
    machine-changing operations.
19. Parallelize independent read-only tracing where useful, but use one writer for overlapping
    files and shared state.
20. Do not perform another live rerun until the closure matrix is complete; finish with
    VERIFIED_CLOSED or all remaining blockers together, measured by deficits and exit criteria
    rather than speculative time estimates.

## Boundaries

- **Not for isolated failures:** an ordinary single failure with an already-proven cause is
  handled directly (rules 1–2 alone would already exceed its needs); this skill's machinery is
  for recurrence, live-run failure classes, boundary incompatibilities, and evidence conflicts.
- **No repo-wide audits:** never convert a normal task into a repository-wide sweep on this
  skill's authority. The inventory in rules 5–6 covers the affected surface of the failure
  under closure, nothing more.
- **Authority unchanged:** this skill changes how failures are closed, not who decides —
  gates, holds, owner-only decisions, and `/directive-compliance` capture still apply.
- **Terminal outcomes:** every invocation ends in exactly one of: `VERIFIED_CLOSED` (closure
  matrix complete, affected suite green at the frozen candidate) or ONE consolidated blocker
  report listing every remaining deficit together — never a trickle of partial findings.
