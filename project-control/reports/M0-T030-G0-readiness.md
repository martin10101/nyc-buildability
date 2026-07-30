# M0-T030 — G0 definition-of-ready (administrative)

**Task:** M0-T030 — in-house code-navigation index: deterministic generator, targeted query CLI,
CI determinism check, A/B navigation benchmark.
**Reviewer:** orchestrator (administrative G0). **Result:** PASS (ready to claim).

## Readiness checklist (per `/start-controlled-task`)
- **Requirement identifiers named:** D-005-R066..R089 (owner GO + ten clarifications,
  `project-control/directives/D-005-codebase-knowledge-graph-pilot/source-002-amendment.md`),
  plus the standing D-005 rows binding all task work (R008/R009, R014, R017, R019, R022, R024,
  R029, R039–R041, R044, R047, R050, R053, R058, R061, R064, R065). Task is in-regime
  (`directive_refs` D-005:ALL, regime v1.0). ✓
- **Exact evidence files named:** inputs list the two directive sources, the four house-pattern
  precedents (generate_ts_types.py, sync_contract_schemas.py, validate_product_map.py,
  validate_contracts.py), and read-only source trees (services/api, apps/web/src,
  packages/contracts, tools). ✓
- **Non-overlapping write scope:** allowed `tools/code_graph/{generate.py,query.py,README.md}`,
  `tools/test_code_graph.py`, ONE additive `ci.yml` job, own reports, own packet (CLI only).
  No active task shares these paths (checked open packets: M0-T019 apps/web + lockfile,
  M0-T021 lock tooling under services/api/scripts, M0-T027/T028 pilot governance/hooks,
  M2-T014..16 HELD survey planning, M3/M4/M5 product trees — all disjoint). Forbidden paths
  restate the owner prohibitions (.claude/**, git hooks, product trees, dependency manifests,
  Graphify, global config, husk deletion). ✓
- **Acceptance scenarios:** AS-1..AS-10 (generation, determinism byte-identity, non-self-referential
  fingerprint, pollution exclusion with planted sentinels, honesty labels with no caller/callee in V1,
  bounded/stale-safe querying, stdlib-only fixture tests, additive CI job, load-bearing A/B benchmark
  with independent correctness verification, isolation proof). All executable or evidence-defined. ✓
- **Required gates + independent reviewers:** G0 (admin, this record); G3 code-reviewer;
  G4 qa-engineer; G5 security-reviewer; plus directive-compliance-verifier for the D-005 rows at the
  frozen reviewed identity — all distinct from producer `backend-engineer`. ✓
- **Dependencies:** none (infrastructure task; no product dependency permitted). D-004 blockers
  (B-015 open) untouched: no hooks, no teammate-confinement surface, Task-tool producer in an
  isolated worktree. ✓
- **Design decision recorded before implementation (owner clarification 2):** NO committed graph
  artifact. Artifacts are generated into a per-checkout cache directory outside the repository,
  keyed by a deterministic source fingerprint computed ONLY over canonical input file paths+bytes
  (CRLF/LF-normalized, sorted; generated artifacts and excluded trees never hashed). Freshness =
  recompute fingerprint (subsecond) and compare; query CLI refuses/regenerates on mismatch, so a
  stale graph can never be presented as current. CI proves determinism (regenerate twice →
  byte-identical) and runs the fixture suite on every push, satisfying "independently regenerable
  and CI-verifiable" without making any product PR fail on a stale committed artifact
  (owner clarification 9) and without any self-referential SHA (owner clarification 2). ✓
- **Thin-client check:** generator is stdlib-only, runs in seconds on ~220 source files; cache
  artifacts are a few MB outside the repo; heavy verification runs in CI. ✓

Reviewed at main = 613c4b1 (post-PR #113: D-005 amendment 1 + M0-T030 contract).
