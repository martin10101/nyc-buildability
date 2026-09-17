# M5-T034 orchestrator seam evidence

Captured by: orchestrator · Date: 2026-09-17 (~20:5x UTC)
Material commit: ae478563 on `task/M5-T034-wide-street-far-wiring` (integration 54e1da7a).

## CI (executable authority)

- Head **ae478563**: workflows **CI -> success, context-budget -> success, secret-scan ->
  success** (GitHub Actions; api job = ruff + pytest on the clean 3.12 runner).
- Orchestrator pre-capture verification in the task worktree: `python -m ruff check
  services/api` → "All checks passed!"; suites from the CORRECT cwd — connectors 49 passed,
  api 35 passed, rules **599 passed** (includes the new wiring suite). The "rules exit 2 /
  16 collection errors" seen from repo-root invocation is the documented
  `No module named 'app'` artifact (now a CODING_RULES line), NOT a defect — reproduced and
  cleared by cwd change at capture.

## Run 38/39 provenance (attribution + breaker record)

- Produced by the loop worker (claude-opus-4-8) across runs persistent-local-38 (2 cycles;
  killed mid-unit by the machine-sleep crash, recovered per the Tier 2 drill) and
  persistent-local-39 (4 cycles; `consecutive_revision_loops` breaker at seq 845). Codex
  REVISEs this time drove BUILD SUBSTANCE (rule-consumption design, concrete provider
  typing, endpoint/evaluator regressions) — each answered with a rework pass; the final
  run-39 worker wrote the §0 provenance-reconciliation report distinguishing inherited vs
  authored work, per the packet's honesty bar.
- The worker's staged commit was unconsumed at breaker time; the orchestrator captured the
  tree as ae478563 mirroring its intent (9 files, +1940/-19).

## Packet-deviation flag for the review wave (producer report §3.3)

`r6_r7_r8_wide_street_conditional_far.rule.json` is byte-UNCHANGED: the determination is
consumed at the evaluator seam (`integration.py select_conditional_far_row` +
`evaluate_property(wide_street_determination=...)`), reading the rule's own byte-checked
`standard_far_by_district` / `wide_street_far_by_district` parameters as the single source
of FAR values. This deviates from the packet output line "rule.json updated to consume the
real determination". Producer rationale: the DSL has no wide-street-determination input
primitive and the Codex reviewer prohibited inventing one; server-side evaluator
consumption preserves needs_review + provenance and byte-identity when no determination is
supplied. The producer flagged this for reviewer judgment rather than asserting
satisfaction. The review wave must rule on it explicitly.

## AS-7 orchestrator items

- api CI green at the seam (above). D-066-R001 navigation block was in the packet; the
  producer report §3.1 records own-module consumption exactly as the block described.
