# M0-T031 — G0 definition-of-ready (administrative)

**Task:** M0-T031 — code-graph hardening + selective navigation routing guidance (D-005 amendment 2).
**Reviewer:** orchestrator (administrative G0). **Result:** PASS (ready to claim).

## Readiness checklist (per `/start-controlled-task`)
- **Requirement identifiers named:** D-005-R090..R110 (owner GO WITH CONDITIONS + eight
  clarifications, source-003-amendment.md), binding via `directive_refs` D-005:ALL (regime 1.0);
  the resolver derives exactly these 21 rows as M0-T031-applicable. ✓
- **Exact evidence files named:** the amendment source, the accepted decision packet (section H =
  the only authorized routing surfaces), the G5/G3/G4 advisory findings being hardened, the current
  tools/code_graph implementation (generator 1.0.1), and tools/context_budget_check.py. ✓
- **Non-overlapping write scope:** tools/code_graph/** + tools/test_code_graph.py (owned by this
  lane; M0-T030 is accepted/immutable), ONE additive CLAUDE.md routing row, ONE additive
  .claude/skills/start-controlled-task/SKILL.md paragraph, own producer report, own packet via CLI.
  No open task shares these paths. Forbidden paths restate every amendment-2 prohibition
  (no hooks/watchers, no reserved surfaces, no product/dependency/CI changes, no universal
  graph-first wording). ✓
- **Acceptance scenarios:** AS-1..AS-9 (tamper detection; meta-corruption safety; cache identity;
  --limit both positions; all prior invariants green; --check + context-budget PASS; single-row/
  single-paragraph guidance diffs encoding the SELECTIVE decision model; no savings claims;
  allowed-paths-only diff). Executable or evidence-defined. ✓
- **Gates + independent reviewers:** G0 (this record); G3 code-reviewer; G4 qa-engineer;
  G5 security-reviewer (single-paragraph SKILL.md diff scrutiny explicitly assigned);
  directive-compliance-verifier for rows R090-R110 at the frozen reviewed identity — all distinct
  from producer backend-engineer. ✓
- **Dependencies:** M0-T030 accepted (48th); no product dependency; D-004 blockers untouched
  (Task-tool producer in an isolated worktree; no teammate runtime, no hooks). ✓
- **Design decisions recorded before implementation:** hash-bind = sha256(graph.json bytes) stored
  in graph.meta.json, verified on every load, mismatch => regenerate (or refuse under --no-regen);
  cache key = sha256(absolute repo root)[:12] + basename; read errors treated as stale, never a
  raw traceback; generator_version bump; CLAUDE.md row must keep tools/context_budget_check.py
  PASS or the producer STOPS and reports (no compensating trims without owner approval). ✓

Reviewed at main = cc273b5 (post-PR #116: D-005 amendment 2 + M0-T031 contract).
