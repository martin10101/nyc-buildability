_Verbatim independent qa-engineer return, ROUND 2 (post legal-semantics correction; transport entity-decoding only). Orchestrator-recorded; reviewer performed no git/ledger writes._

# GATE REPORT — M4-T006 (G4 Integration & Regression, re-review)

**Task:** M4-T006 — R5 height/setback ruleset (targeted legal-semantics correction re-review)
**Gate:** G4 (Integration & Regression)
**Reviewed SHA (frozen):** `5d605d4` on `task/M4-T006-r5-height-setback` (PR #88)
**Prior baseline (already G4 PASS):** `6509db3`
**Reviewer role:** Independent, read-only on production code
**Verdict: PASS** (final acceptance remains gated on G6)

## Reproduction environment
Clean detached worktree at `5d605d4`, Python 3.11.9, ruff 0.9.9, pytest 8.4.2. Worktree removed after review.

## Commands + outputs (all from `services/api` at 5d605d4)
| Check | Result |
|---|---|
| `python -m ruff check .` | `All checks passed!` (exit 0) |
| `python -m pytest tests/rules/test_r5_height_setback.py -q` | `47 passed in 1.73s` (was 45; +2) |
| `python -m pytest -q` (FULL API) | `928 passed in 19.53s` (was 926; +2) — no pre-existing test regressed |
| `python scripts/sync_zr_snapshots.py --check` | `OK: runtime-bundled ZR snapshots are byte-identical to the canonical source (6 file(s)).` |
| `python -m pytest tests/rules/test_zr_snapshot_bundle.py tests/rules/test_installed_deployability.py -q` | `8 passed in 0.41s` |

## Diff-scope confirmation (methodology note)
The packet's `git diff --name-only 6509db3 5d605d4` does **not** equal 2 files — it lists ~70 files because `5d605d4` merged origin/main (M0-T022 / PR #89, merge parent `8c53433`) in between. The correction commit itself is isolated correctly by diffing against its own parent:
- `git diff --name-only 8c53433 5d605d4` = exactly the 2 files: `services/api/app/rules/rulesets/r5_setback.rule.json` + `services/api/tests/rules/test_r5_height_setback.py`.
- Restricting `6509db3..5d605d4` to `services/api/app`, `packages/contracts` = only `r5_setback.rule.json` changed. R5A rule, `evaluator.py`, `registry.py`, all other rulesets, and all snapshot files are byte-identical to the reviewed baseline `6509db3`.

## Value invariance (confirmed via live evaluator + code diff)
- Rule param `setback_depth_by_street_class` unchanged: `{"wide": 10, "narrow": 15}`. Only descriptions/notes/limitations text plus one new `documented_limitation` exception (`condition: null`, `effect: documented_limitation`, no value effect) were added.
- Live `RuleRegistry().load()` evaluation of `r5-setback`:
  - `street_width_class=wide` → `required_setback_depth=10.0`, `coverage_status=conditional`, exception `section_23_423_modifications_unresolved` applied.
  - `street_width_class=narrow` → `required_setback_depth=15.0`, `coverage_status=conditional`, marker applied.
  - street width absent → `outputs={}` (no value), `coverage_status=professional_review_required` (fail-closed unchanged).
- The 2 new tests genuinely assert the marker exists, `effect == "documented_limitation"`, and its text contains "standard unmodified" / "never be presented as the final". Correction is labeling/marking only — no dimensional value or coverage class changed.

## Regression isolation
`git diff --name-only 6509db3 5d605d4` restricted to code/tests/contracts = only the 2 target files. Snapshots (6) byte-identical. No pre-existing test regressed (full suite 928 pass).

## CI observation (PR #88)
`gh pr checks 88` (read-only) — all checks **pass**, including `exact-production-install (Render pip install path + validate_profile + pip-audit)`, `api (ruff + pytest)`, `contracts (JSON Schema validation)`, `contracts-schema-bundle`, `contracts-typegen`, `api-lock-verify`, `control-plane`.
Reconciliation: PR #88 head is `0830454`, one commit **ahead** of the frozen review SHA `5d605d4`. `5d605d4` is a confirmed ancestor of `0830454`, and `git diff --name-only 5d605d4 0830454` = **project-control ledger only** (`gates/M4-T006-G2.json`, `reports/M4-T006-legal-semantics-proof.md`, `state.json`, `tasks/M4-T006.json`) — no code/test/contract delta. Therefore the green CI at `0830454` validly covers the reviewed code at `5d605d4`.

## Blocking gaps
None. The correction adds an always-on `documented_limitation` marker asserting the §23-423 10/15 ft depths are standard-unmodified starting setbacks (not the final applicable setback), with no dimensional/coverage change; integration, regression, deployability, and snapshot byte-identity all hold.

**Requested status for orchestrator to record: G4 PASS at `5d605d4`.** Not self-accepting; final acceptance stays gated on G6.
