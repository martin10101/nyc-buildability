# M0-T073 producer report — permanent software-engineering modularity enforcement

Producer: orchestrator. Branch `task/M0-T073-modularity-enforcement`, base `57b80c2`
(D-017 capture head, PR #226). Governing rows: D-017-R105..R113 (source-002-amendment.md
items 1-7), bound to this task at claim.

## Deliverables (requirement → artifact)

| Rows | Artifact | Content |
|---|---|---|
| R105 | all of the below | permanence is written into each artifact and enforced by CI, not by session memory |
| R106 | `CLAUDE.md` | new permanent principle 16 (concise; context-budget guard PASS) with the seven mandated statements, routing to the policy and path rule |
| R107 | `AGENTS.md` | new "Modularity (permanent)" section; names the exact finding classes Codex must raise (responsibility mixing, module growth, giant functions, hidden coupling, generic utility modules) |
| R108 | `.claude/rules/code-architecture.md` | path frontmatter over `services/**/*.py`, `tools/**/*.py`, `packages/**/*.py`, `apps/web/src/**/*.ts(x)`; the ten mandated behaviors, compact; depth deferred to the policy |
| R109 | `docs/CODE_MODULARITY_POLICY.md` | 12 sections: cohesion rules; boundary examples (Python/TS/React/API/storage/rule-engine); soft+hard thresholds; function/class complexity; interface preservation; circular-dependency prevention; tests-before-extraction; exclusions; reviewed-exception process; safe large-file refactoring; anti-over-fragmentation; measurement+enforcement |
| R110 | `tools/modularity_check.py` (+ `tools/modularity_baseline.json`, `tools/modularity_exceptions.json`) | deterministic checker: handwritten-production-only selection from `git ls-files`; generated/vendored/lock/schema/migration/fixture/test exclusions; new-oversized fail; material-growth fail (`max(50, 10%)`); warning reporting; top-level symbol signal; versioned digest-locked baseline; approval-gated regeneration that never erases live debt; explicit expiring path-exact exceptions; deterministic sorted output; the two "line count is never proof / never an excuse" clauses in output and policy |
| R111 | `.claude/skills/start-controlled-task/SKILL.md`, `.claude/skills/run-quality-gate/SKILL.md` | the seven boundary questions at claim time; the reviewer instruction to check answers against the actual diff |
| R112 | `.github/workflows/ci.yml` | ADDITIVE `modularity` job (check + proof tests) on every PR/push; existing jobs untouched |
| R113 | `tools/test_modularity_check.py` | 24 tests incl. the seven mandated proofs plus malformed/duplicate/horizon/breadth/single-use-approval/TS-comment-counting regressions (see evidence) |

## Evidence

- `python tools/test_modularity_check.py` → **24 passed** (the seven
  D-017-R113 proofs map to: proof 1 `test_1_normal_focused_module_passes`; proof 2
  `test_2_new_unjustifiably_oversized_module_fails`; proof 3
  `test_3_growth_of_grandfathered_oversized_file_fails`; proof 4
  `test_4_excluded_generated_file_does_not_fail`; proof 5
  `test_5_valid_exception_is_narrow_and_temporary`; proof 6
  `test_6_expired_exception_fails` + `test_6b_broadened_exception_fails` +
  `test_6c_incorrectly_targeted_exception_fails`; proof 7
  `test_7_regeneration_cannot_silently_erase_debt` (+7b)).
- `python tools/modularity_check.py --check` on this branch → **0 failures**, 4
  symbol-ceiling warnings (review signals), 240 selected files (corrected from the
  originally recorded 239, which was captured before the checker itself was staged
  - G3-C3/G4-C1; re-measured after the G4-C2 comment-span-aware SLOC correction and
  the fresh baseline regeneration under the same reviewed approval).
- Initial baseline: version 1, **23 legacy-debt entries** (largest:
  `tools/agent_supervisor/cli.py`), generated under approval
  `M0-T073-initial-baseline` (expires 2026-08-25; reviewed in this PR), digest-locked.
- `python tools/context_budget_check.py` → **PASS** after the CLAUDE.md principle and
  the path rule were added (R106 conciseness obligation).
- Determinism: `test_output_is_deterministic` (byte-equal repeat runs, sorted output).

## Overlap disclosure (G0 check 4)

Open PR #64 touches `.github/workflows/ci.yml` (a hunk in the `web` region of a stale
base) and `CLAUDE.md` (a hunk near principle 12 of a stale base). This task's changes
are additive-only in different regions: a new self-contained `modularity` job appended
after `supervisor-bridge`, and principle 16 appended at the end of the permanent
principles. No existing job or principle text was edited. If a textual conflict
emerges at #64's eventual rebase, it resolves by keeping both additions.

## Boundary answers for this task itself (R111 discipline, self-applied)

1. Responsibility: policy definition (docs), rule delivery (.claude), machine
   enforcement (tools) — three modules, one per responsibility. 2. Placement: new
   files; no existing module owned these concerns. 3. Thresholds: `modularity_check.py`
   ≈ 380 SLOC (< 600); no touched file crossed a threshold. 4. Extraction: n/a (new).
5. Stable interfaces: none changed; skills/CLAUDE additions are additive.
6. Boundary tests: `tools/test_modularity_check.py`. 7. Modularity CI check: PASS.
