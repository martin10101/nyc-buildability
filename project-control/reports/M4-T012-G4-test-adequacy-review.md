# G4 GATE REPORT (ORIGINAL, verdict FAIL) — M4-T012 (R1/R2-series height/setback draft rule families, D-049 definitive scope)

> Orchestrator note: reviewer return saved VERBATIM from the agent-return channel
> (transport entity-decoding only). Reviewer: qa-engineer. This FAIL was discharged by
> the rework at 8538c272 and the same reviewer's delta attestation
> (project-control/reports/M4-T012-G4-delta-attestation.md). Recorded by the
> orchestrator per ADR-005.

I have everything I need. Here is my complete G4 gate report.

---

# Gate Report

- **Gate ID:** G4 (test adequacy / integration)
- **Task ID:** M4-T012 (D-045 A1 wave 1 — R1/R2-series height/setback draft rule families, D-049 definitive scope)
- **Reviewer:** qa-engineer (independent; NOT the producer)
- **Producer:** rules-engineer (claude-sonnet-5)
- **Result:** FAIL
- **Clean environment/worktree used:** Yes. Isolated worktree `agent-a67d76e626031a287`, `git fetch` + `git reset --hard 48aed9c093b0c33ae1f26438a09211466a982ecd` (the frozen reviewed SHA per the anchor). Verified `dd7c8b74` (material head) is an ancestor of HEAD. No repository files edited; no `project_control.py`/git-write/`gh` run. Only wrote under `.claude/agent-memory/qa-engineer/`.

## Acceptance criteria reviewed

S1 per-variant extraction + provenance; S2 typed min/max separation; S3 fail-closed gaps; S4 negative controls (wrong-district, cross-variant isolation, effective-date, mutation-style binding); S5 draft-posture + language; S6 regression + determinism + modularity + **api CI job green**. Plus the four packet `outputs` deliverables and the six G4 mandate items.

## Directive/requirement verification (test-adequacy view)

My G4 pass judges whether tests prove the packet's requirements; the formal per-requirement DCV verdict is the directive-compliance-verifier's separate pass. Mapping directive requirements to reproduced test evidence:

| Requirement ID | Reviewed identity | Verdict (test-coverage) | Reproduced evidence |
|---|---|---|---|
| D-045-R001 | dd7c8b74 | PASS | 4 rulesets + 4 snapshots; `test_as1_*` bind 25/35 & 35/35; digest-binding `test_as2_*` pass |
| D-045-R008 | dd7c8b74 | PASS | `test_nc8_setback_geometry_never_a_numeric_output` proves sloping-plane (a)-(f) stays a documented A2 gap, never a number; engine/schema untouched (diff-verified) |
| D-045-R009 | dd7c8b74 | PASS | `test_as5_*` (all needs_review; family coverage CONDITIONAL never VERIFIED; banned-language grep) |
| D-048-R001 | dd7c8b74 | PASS | bare R1/R2 express-encoded (`test_as1_bare_*`, distinct-provenance test) |
| D-048-R002 | dd7c8b74 | PASS (superseded) | five lettered variants encoded, not "not-assessed"; every value snapshot-cited or fail-closed |
| D-049-R001 | dd7c8b74 | PASS | `test_as1_suffix_variant_*` (11-25 suffix inheritance, owner-decision provenance), NC-1 isolation |
| D-049-R002 | dd7c8b74 | PASS | `test_as1_r2x_far_row_documented_as_floor_area_only` (R2X FAR note applied only to R2X, not R2A; height identical) |
| D-049-R003 | dd7c8b74 | PASS | `test_nc2_*` (letter-suffix + bare-R1 exclusion), `test_nc8_trigger_boundary_values`, `test_nc5_*` (missing-input → PRR) |
| D-049-R004 | dd7c8b74 | PASS | `test_nc3_*` modifier downgrades; `r1_r2_qrs_height` 23-424 + `test_nc7_*` same-family conflict |
| D-049-R005 | dd7c8b74 | PASS | owner-decision provenance + needs_review on every output; `test_as1_conditional_never_verified_for_every_rule` |
| D-049-R006 | dd7c8b74 | PASS | supersession honored: lettered variants moved to suffix-inheritance encoding; bare encoding unchanged |

Directive-requirement *test coverage* is sound. The FAIL below is a CI-gate (S6) defect, independent of directive coverage.

## Steps independently executed (verbatim commands + outputs)

All from the reset worktree at the frozen SHA.

1. `cd services/api && PYTHONPATH="." python -m pytest tests/rules/test_r1_r2_height_setback.py -q` → **`100 passed in 3.74s`**
2. `cd services/api && PYTHONPATH="." python -m pytest tests/rules -q` → **`558 passed in 13.99s`** (reproduces producer + orchestrator)
3. `python tools/modularity_check.py --check` → **exit 0** (16 warnings, all pre-existing in untouched `tools/*` and `apps/web`/`services/api` files this task did not touch)
4. `python services/api/scripts/sync_zr_snapshots.py --check` → **`OK: ... byte-identical ... (14 file(s))`, exit 0**
5. **Mutation-adequacy probe** (in-memory mutated rule docs, no repo writes): every mandate-named value is BOUND —
   - bare wall 25→99 (output tracks); bare ridge 35→88; suffix ridge 35→77; QRS base 35→66; (g) value 5→3 — all track the mutation, so each committed strict-equality assertion WOULD fail if the value were altered.
   - (g) area threshold: a `(9499,100,0)` lot is `not_applicable` at 9500 (as the committed boundary test expects) but flips to `conditional` when the threshold is lowered to 9000 — proving the boundary test binds the `9,500` figure. `test_nc8_trigger_boundary_values` parametrizes both sides of 9500/100/5 with off-by-epsilon negatives (9499, width 99, slope 4.99), so 100 ft and 5 % are bound identically.
6. **Source-fidelity spot check**: the `zr-23-421-g` snapshot verbatim contains "9,500 square feet … 100 feet … five percent … five feet above the base plane"; `zr-23-421-r1-r2` contains "maximum height above the base plane of 25 feet"; `zr-23-424-r1-r2` contains "R1-1 … R2X … | Maximum Base Height 35 | Maximum Height … 35". The passing digest-binding tests bind to genuine source text.
7. **Diff scope**: `git diff --name-status efa0f268 dd7c8b74` — only 4 rulesets, 4 canonical + 4 bundle snapshots, 1 test file, 2 reports (+ producer agent-memory). `git diff --name-only … -- 'engine*' 'evaluator*' 'schemas'` → **empty** (S6 engine/schema-untouched confirmed). `zr-23-21` and `zr-23-423` (cited by the suffix and QRS rules) are confirmed pre-existing, so no memory-transcribed values entered.
8. **PYTHONPATH disclosure check**: from repo root without `PYTHONPATH`, the *pre-existing* `test_rules_engine.py` fails collection with `ModuleNotFoundError: No module named 'app'` — identical to the new file. Confirms the note is a genuinely pre-existing environment characteristic (package not pip-installed in sandbox), not introduced by this task.
9. **CI-exact lint reproduction** (the defect): `cd services/api && python -m ruff check .` (ruff 0.13.0; the version CI uses) → **`Found 6 errors` (5× E501, 1× F841), exit 1.**

## Expected versus actual

| Item | Expected | Actual |
|---|---|---|
| New tests | pass | 100 passed ✓ |
| Full rules suite | 558 passed | 558 passed ✓ |
| modularity `--check` | exit 0 | exit 0 ✓ |
| snapshot sync `--check` | exit 0 | exit 0 (14 files) ✓ |
| Value/trigger binding | mutation-sensitive | all bound ✓ |
| **`ruff check .` (services/api) — S6 CI api step** | **exit 0 (clean)** | **exit 1, 6 errors — FAIL** |

## Evidence paths

- Tests: `services/api/tests/rules/test_r1_r2_height_setback.py` (100 tests, AS-1..AS-6 / NC-1..NC-8)
- Rulesets: `services/api/app/rules/rulesets/{r1_r2_bare_pitched_height,r1_r2_suffix_variants_pitched_height,r1_r2_reference_plane_23421g,r1_r2_qrs_height}.rule.json`
- Snapshots: `docs/research/zr-snapshots/v1/` + `services/api/app/_zr_snapshots/v1/` (`zr-11-25`, `zr-23-421-r1-r2`, `zr-23-421-g`, `zr-23-424-r1-r2`)
- CI config: `.github/workflows/ci.yml` job `api` (lines 186-213); `services/api/pyproject.toml` `[tool.ruff]` line-length=100, `select = ["E","F","I","UP","B"]`
- Reports: `project-control/reports/M4-T012-producer-report.md`, `M4-T012-source-capture.md`, `M4-T012-evidence-map.json`

## Human-style walkthrough findings

N/A — backend rule-data task, no UI surface.

## Regression/security/provenance findings

- Regression: full rules suite green (558), engine/evaluator/schemas provably untouched, snapshots byte-identical. No regression.
- Provenance: every numeric constraint cites a hash-guarded snapshot; tampered-snapshot and mismatched-citation-digest tests fail closed (`test_as2_*`). Non-value setback reference (`zr-23-423`) omits a citation digest but is hash-guarded at the snapshot level — acceptable (it is not a value-bearing citation).
- Fail-closed discipline: strong — omitted optional modifier flag → PRR (DF-6), missing district/building-type/any-single-(g)-geometry-input → PRR, invalid enum → PRR, same-family QRS-vs-envelope conflict surfaces `rule_conflict` with no silent value.

## Defects

### BLOCKING-1 — the new test file fails `ruff check`, so CI's `api` job (S6) will not be green

CI job `api` (`.github/workflows/ci.yml`, `working-directory: services/api`) runs `ruff check .` **before** `pytest`. Under the repo's own config (`services/api/pyproject.toml`: `line-length = 100`, `select = ["E","F","I","UP","B"]`, no `per-file-ignores`/`exclude` for `tests/`), `tests/rules/` is linted. Reproduced exactly: `cd services/api && python -m ruff check .` → **exit 1, 6 errors, all in `test_r1_r2_height_setback.py`** (the rest of the `services/api` tree is ruff-clean, including the accepted discipline-bar file `test_r3_r4_height.py`):

- `E501` line-too-long: **line 40 (109>100)**, **line 45 (104>100)** (docstring coverage-map lines NC-3 / NC-8), **line 320 (105>100)** and **line 340 (105>100)** (the `full = _qrs_inputs(...) if ... else _envelope_inputs(...)` one-liners in `test_as3_*`), **line 585 (101>100)** (`def test_nc5_reference_plane_missing_any_single_geometry_input_fails_closed(registry, missing_field):`)
- `F841` unused variable: **line 190** — `rule = registry.rule("r1-r2-reference-plane-23421g")` assigned but never used in `test_as1_reference_plane_g_confident_when_area_and_width_satisfy` (that test passes a raw inputs dict, not `_envelope_inputs(rule, …)`).

Impact: S6 explicitly requires "the api CI job green at the frozen candidate." Because ruff is the api job's first step and exits 1 at dd7c8b74, the `api` job will FAIL on the Ruff step regardless of the passing pytest suite. Neither the producer's self-checks nor the orchestrator's pre-gate reproduction ran `ruff check .` (they ran pytest + modularity + sync only), so this was not caught. This is fully reproducible and attributable solely to this task's new file.

## Required rework (producer, not reviewer — ADR-005 read-only)

1. In `services/api/tests/rules/test_r1_r2_height_setback.py`: wrap the 5 long lines (40, 45, 320, 340, 585) to ≤100 chars, and remove the unused `rule` assignment at line 190 (or use it, e.g. keep the raw-dict call and drop the variable).
2. Re-run **exactly** `cd services/api && python -m ruff check .` → expect exit 0, plus `PYTHONPATH=. python -m pytest tests/rules -q` → expect 558 passed. These are behavior-neutral edits (whitespace/dead-var), so re-gate can be a delta-attestation. No test logic or assertion changes are required — the test *content* is adequate.

## Reviewer conclusion

On substance the test pack is strong and meets the discipline bar: all six acceptance scenarios have executable proof, all four `outputs` deliverables are exercised, and I **empirically confirmed mutation-binding** for every mandate-named value (25 ft wall, 35 ft ridge, 35/35 QRS, the 5 ft (g) allowance, and the 9,500/100/5 % triggers bound at exact boundaries with both-sided off-by-epsilon negatives). Isolation and fail-closed controls are thorough (cross-variant, letter-suffix exclusion from (g), DF-6 omitted-flag→PRR, missing-input→PRR, same-family conflict with no silent value), the conservative all-three-(g)-inputs behavior is explicitly pinned by NC-5 (a future relaxation is a visible change, satisfying mandate item 6), effective-date discipline is proven, and the S5 language guard is byte-identical to the accepted M4-T014 bar. The producer's PYTHONPATH disclosure is confirmed genuinely pre-existing.

However, acceptance scenario **S6 requires the api CI job to be green, and I reproduced a deterministic ruff failure (6 errors) in the new test file that will fail that job's first step.** A required acceptance scenario is not met by a reproducible defect, so the gate cannot pass as submitted. The rework is small and behavior-neutral.

**Advisory (non-blocking) items for the rework pass:**
- ADVISORY-1: AS-3 effective-date boundary tests cover 3 of the 4 rules; `r1-r2-reference-plane-23421g` is not in the `test_as3_*` parametrize list. The mechanism is shared and its `effective_from` is 2024-12-05, so risk is low — consider adding it.
- ADVISORY-2: wrong-district (far-foreign, e.g. R5/R3A) no-match is pinned only for the bare and suffix rules (NC-1). I verified the QRS and (g) rules DO return `not_applicable` for foreign districts, but no committed test locks this; a future broadening of their `in_set` would go uncaught. Consider extending NC-1 to those two rules.
- ADVISORY-3: the S5 banned-phrase list uses `"buildable envelope"` (space); the rulesets use the hyphenated `"buildable-envelope"` only in negations ("not a buildable-envelope result"), so there is no current violation, but a hyphenated positive claim would slip past the guard. This is inherited verbatim from the accepted M4-T014 bar, so it is a campaign-wide nit, not a M4-T012 regression.

Note for the orchestrator: CI on dd7c8b74 is orchestrator-captured evidence and was "in flight." Based on the unambiguous config, that captured conclusion should show the `api` job FAILING on the Ruff step; if it instead shows green, that contradicts the config and must be investigated before any accept. [Orchestrator capture: CONFIRMED — the CI run at dd7c8b74 concluded FAILURE with the api job failing on the Ruff step with exactly these 6 findings; all 17 other jobs green.]

VERDICT: FAIL