# Gate Report — G4 (integration & regression), qa-engineer half

- **Gate ID:** G4 (integration & regression)
- **Task ID:** M4-T005
- **Reviewer:** qa-engineer (independent; read-only on production code)
- **Producer:** backend-engineer (+ frontend-engineer)
- **Reviewed SHA:** `84b50a722d518d0ae6c233ee38affedbdaaebea3` (`git reset --hard` in the assigned worktree; HEAD confirmed = frozen SHA)
- **Result:** **PASS**

## Steps independently executed (commands + actual outputs)
1. **Ruff** — `python -m ruff check .` (services/api) → `All checks passed!`
2. **Full backend suite** — `python -m pytest . -q` → **`855 passed in 49.69s`** (853 at Phase 2b + 2 installed-deployability pack).
3. **Five required new packs:** `test_rule_evaluation_api.py` → 29; `test_rules_fh4_temporal_parity.py` → 20; `test_zr_snapshot_bundle.py` → 6; `test_installed_deployability.py` → 2; `test_rule_evaluation_contract.py` → 28 (aggregate 85 passed).
4. **Contract drift (all four green):** `generate_ts_types.py --check` exit 0; `sync_contract_schemas.py --check` exit 0; `sync_zr_snapshots.py --check` exit 0 (byte-identical, 1 file); `validate_contracts.py` → `Checked 7 schema file(s); 0 failure(s)`.
5. **`property_profile` byte-identity to main** — `git diff --stat main -- packages/contracts/schemas/v1/property_profile.schema.json packages/contracts/generated/property_profile.ts` → **empty**. `contract_version` enum ends at `1.4.0`.
6. **Forbidden-path & no-fork audit** — `git diff --name-only main 84b50a72` filtered for every forbidden path → **NONE touched** (`properties.py`, `evaluator.py`, `app/profile/**`, `integration.py`, `coverage.py`, `rules/models.py`, canonical schemas, `sync_contract_schemas.py`, requirements/lockfiles, `package.json`, `.github/workflows/**`).
7. **CI on PR #84** — `gh pr checks 84`: **25/25 pass, 0 non-pass**, including `web-e2e`, `web`, `api`, `exact-production-install`, `contracts-typegen`, `contracts-schema-bundle`.

## Scenario → test coverage (AS-1..AS-14)
| AS | Behavior | Test(s) | Verified |
|---|---|---|---|
| AS-1 | schema validates real payload; TS/bundle byte-identical | contract test + validate_contracts + typegen/bundle --check | PASS |
| AS-2 | property_profile 1.4.0 + generated TS byte-identical to main | git diff main empty; validate_contracts 0 failures | PASS |
| AS-3 | flag ON → 200 draft; conditional, disclaimer, citations, spatial_uncertainty; input by-reference | `test_as3_*` | PASS |
| AS-4 | flag OFF/unknown → generic 404, no hint/cid; never in OpenAPI; refuses verified | `test_as4_*` (8 tokens) | PASS |
| AS-5 | unsupported family → normal 200 unsupported | `test_as5_*` | PASS |
| AS-6 | missing substrate/lot area → 200 professional_review_required, no fabricated value | `test_as6_*` | PASS |
| AS-7 | conflicting rules → typed rule_conflict/PRR, no value | `test_as7_*` (real evaluate over synthetic conflict registry) | PASS |
| AS-8 | split-lot RANGES preserved (0.55–0.65 / 0.35–0.45) | `test_as8_*` | PASS |
| AS-9 | FH-4 impossible date fails closed both paths; leap day evaluates | `test_rules_fh4_temporal_parity.py` (20) | PASS |
| AS-10 | safe typed errors, no leak; strict JSON | `test_as10_*` (canary + traceback absence) | PASS |
| AS-11 | UI network/5xx recoverable, profile usable, retry | `RuleEvaluationFailure.tsx` + e2e | via web-e2e CI green |
| AS-12 | keyboard, live-region, focus, provenance, no color-alone | component + e2e a11y | via web-e2e CI green |
| AS-13 | never Published/Verified; disclaimer end-to-end | backend verified-absent + serializer boundary; FE honesty | PASS (backend); UI via CI |
| AS-14 | full pytest+ruff green; property matrix unchanged; route absent from OpenAPI; no dup calc | `test_as14_*` + 855-pass suite + properties.py byte-identical | PASS |

## Regression / no-fork findings
- **No forked calculation path:** endpoint delegates all legal/numeric logic to accepted `app.rules.integration.evaluate_property`; `integration.py`/`evaluator.py`/`coverage.py` byte-identical to main. FH-4 is a single additive fail-closed guard reusing `evaluator._valid_iso_date`.
- **Existing consumers non-regressed:** `properties.py` and `app/profile/**` byte-identical to main; property-route + health regression tests green; internal route absent from `/openapi.json`.
- **Deployability backstop:** `test_installed_deployability.py` pins all runtime resources as package-data; installed-wheel proven by `web-e2e` + `exact-production-install`.

## Non-blocking observations (scope/process, not integration defects)
1. `apps/web/playwright.config.ts` (+7 lines) is the one changed file outside the enumerated `allowed_paths` — test-harness wiring (`env: { INTERNAL_RULE_EVAL_UI: "1" }` on the e2e webServer); producer-disclosed Phase-3 deviation #1. Benign for integration; flagged for scope adjudication.
2. PR #84 head is 2 commits ahead of the frozen SHA, but the diff touches only project-control report/ledger files — zero production-code change; CI validates the exact frozen tree.

## Defects / required rework
None for G4 (qa half). **Verdict: PASS.** Acceptance still requires the parallel human-journey-reviewer PASS per the gate map.
