# M4-T012 G0 contract-readiness record (administrative; orchestrator)

Date: 2026-09-13 (UTC). First D-045 campaign task, contracted per D-045-R010 after master-plan
integration (commit 532fc221; checkpoint CP-2026-09-13-d045-integration).

- **Requirement identifiers**: D-045:D-045-R001 (A1 obligation), R008 (one-family-at-a-time
  sequencing — this wave deliberately excludes every A2 geometry-dependent mechanic), R009
  (preservation: DRAFT-until-G6, no compliance declarations). Applicability append committed
  (digest resync → 27bc7302); `evaluate_task_refs` ok — applicable == cited == [R001,R008,R009].
  `validate_directive_compliance.py --check` EXIT 0.
- **Wave choice (orchestrator replanning judgment per R008)**: R1+R2 series first — numeric
  per-district limits matching the accepted R5 pilot discipline with NO sky-exposure-plane /
  street-width dependency, so the campaign cadence is proven before A2/B2 enter.
- **Evidence files**: pinned by path (M4-T006 pilot packet + three reports, existing rulesets/DSL,
  the hash-guarded ZR snapshot mechanism, gap-list A1 rows, D-045 requirements).
- **Scopes**: allowed_paths resolve to tracked directories (rulesets/schemas/snapshots/tests) +
  two new reports; engine/evaluator and all cross-domain paths forbidden. Disjoint from every
  in-flight task (none are in flight — 196 accepted, queue empty).
- **Acceptance scenarios**: S1–S6 (per-variant provenance, typed min/max separation, fail-closed
  gaps, negative controls incl. cross-variant isolation, DRAFT posture + language grep, regression
  + determinism + modularity + CI).
- **Gates**: G0/G2/G3/G4/G5 with reviewers code-reviewer/qa-engineer/security-reviewer, all ≠
  producer rules-engineer (the M4-T006 roster).
- **Fail-closed source rule**: missing/uncapturable official text ⇒ BLOCKED submission naming the
  sections; never transcription from memory (permanent principle 3).

Verdict: **PASS** — packet claimable.
