_Verbatim independent qa-engineer return (transport entity-decoding only). Orchestrator-recorded; reviewer performed no git/ledger writes._

# G4 GATE REPORT — M4-T006 (R5 height & setback draft rule family)

**Verdict: PASS**

**Reviewer:** independent G4 (integration & regression), read-only. No `project_control.py`, git writes, or `gh` writes performed.
**Reviewed SHA:** `6509db3` on `task/M4-T006-r5-height-setback` (PR #88), base `main` @ `c5e8cd0`.
**Checkout:** verified in isolated worktree, detached HEAD confirmed `6509db3b525f8c93bdf0af6d57828e44e1312319`.

## SHA-advance equivalence (resolved, non-blocking)
PR #88 head has advanced to `bf82564`. I verified `git diff --name-status 6509db3 bf82564`: the delta is **ledger-only** — `project-control/gates/M4-T006-G2.json`, `reports/M4-T006-G2-selfcheck.md`, `state.json`, `tasks/M4-T006.json`. **Zero code/test/snapshot/contract change.** The frozen code is byte-identical at both SHAs.

## 1. Independently executed (exact outputs, from `services/api`, Python 3.11.9)
| Command | Result |
|---|---|
| `python -m ruff check .` | `All checks passed!` |
| `python -m pytest tests/rules/test_r5_height_setback.py -q` | `45 passed in 1.21s` |
| `python -m pytest -q` (FULL API) | `926 passed in 13.13s` — = 881 baseline + 45 new; no failures/skips, so no pre-existing test regressed |
| `python scripts/sync_zr_snapshots.py --check` | `OK: runtime-bundled ZR snapshots are byte-identical to the canonical source (6 file(s)).` exit 0 |
| `python -m pytest tests/rules/test_zr_snapshot_bundle.py tests/rules/test_installed_deployability.py -q` | `8 passed in 0.28s` |

The 45-test contribution and the 926 total are internally consistent (926 − 45 = 881 baseline), confirming no silent regression.

## 2. AS/NC → proving-test map (all genuinely assert the stated behavior)
File: `services/api/tests/rules/test_r5_height_setback.py`
- **AS-1** (per-district min/max preserved, separate typed constraints, never verified): L68, L83, L91, L99, L105, L113. Max encoded as separate `max_base_height`/`max_building_height`; absent minimum is documented via `no_minimum_base_height` exception (L76-77) — **not fabricated as 0**. Coverage `conditional`, never `verified`.
- **AS-2** (provenance + tampered/absent fail closed): L131 (section+quote+`last_amended`+`content_digest_sha256`+snapshot_id match), L144 (3 citations), **L152 tampered digest raises `SnapshotError content_digest_sha256 mismatch`**, **L167 absent id raises `unknown snapshot_id`**. Verified genuine.
- **AS-3** (effective-date boundary): L189 before `2024-12-04`→`not_applicable`, empty outputs, `in_effect False` (5 variants); L205 on `2024-12-05`→`conditional`, `in_effect True` (4 variants).
- **AS-4** (determinism): L216 byte-identical export.
- **AS-5** (never-verified lifecycle): L227, L236 — every family rule `needs_review`, `verified_eligible False`, `qualified_human_approval: pending`, family coverage `conditional`.
- **AS-6** (installed-wheel deployability): L246, L258 + external `test_zr_snapshot_bundle`/`test_installed_deployability` (8 passed) + **CI `exact-production-install` success at the frozen SHA** (see §3).
- **NC-1** (variant non-inheritance): L280 (6 cross-variant combos → `not_applicable`, empty), L289 (unknown `R5X` not mapped to nearest).
- **NC-2** (wide/narrow/**unknown** street): L303 missing→`professional_review_required`+`missing_critical`; L310 `"unknown"`→`professional_review_required`, `input_validation.valid False`, no value.
- **NC-3** (special-district/overlay/historic): L326 (`overlay_present`/`special_district_present`→`professional_review_required` with overlay/special exception applied), L333 (`historic_district`).
- **NC-4** (building-type / QRS geography unavailable): L342, L349 → `professional_review_required`, empty.
- **NC-5** (missing input): L361 empty district → `professional_review_required`+`missing_critical`.
- **NC-6** (contradictory input): L372 `data_conflict` coverage + uncertainty trace; L386 multi-district-split → `professional_review_required`.
- **NC-7** (mutually-exclusive rules → rule_conflict): L403 competing `r5-height`/`r5-qrs-height`, sorted deterministic, `"value" not in conflict`; L414 order-independent; L422 no spurious conflict for ordinary R5.

Provenance mechanism spot-checked directly: `r5_height.rule.json` carries `status needs_review`, `effective_from 2024-12-05`, real ZR §23-422 citation with verbatim quote + `last_amended`; snapshots carry `content_digest_sha256`; setback rule carries 3 citations (`zr-23-423`, `zr-12-10`, `zr-23-422`) and a single typed `required_setback_depth`.

## 3. Installed-wheel deployability (CI observed)
CI ran **directly at the frozen SHA `6509db3`** (`gh api .../commits/6509db3/check-runs`). Conclusions:
`exact-production-install (Render pip install path + validate_profile + pip-audit)` → **success**; `api (ruff + pytest)` → success; `contracts` / `contracts-schema-bundle` (byte-identical) / `contracts-typegen` (byte-identical) → success; `api-lock-verify`, `api-tooling-lock-verify`, `control-plane`, `web`, `context-budget`, credential scan → success. `web-e2e` → `cancelled` (superseded; diff has no `apps/web` change — expected, non-blocking). The literal Python-3.12 install path the producer could not run locally is thus confirmed green in CI at the reviewed SHA.

## 4. Regression isolation
`git diff --name-status c5e8cd0 6509db3` = **17 files, all `A` (added)**: 5 `docs/research` snapshots, 5 packaged `_zr_snapshots`, 6 `*.rule.json` rulesets, 1 test file (plus project-control reports). Explicit forbidden-path diff returned **empty** for `evaluator.py`, `r5_residential_far.rule.json`, `app/profile`, `app/spatial`, `app/scenario`, `app/api`, `apps/web`, `packages/contracts`, and `app/rules/schemas`. No engine core, FAR rule, contract, or DSL-schema modification. Additive + fail-closed only, as scoped.

## Non-blocking observations (suggestions, not gate conditions)
1. AS-3 `on-amendment-date` parametrize (L196-204) omits `r5a-height`; its `2024-12-05` effective point is only covered implicitly (AS-1 at post-amendment default `as_of` + AS-3 before-date at L189). Consider adding `r5a` to the on-date list for symmetry.
2. G4 scope is integration/regression only — **legal correctness of the dimensional values (35/45 ft, 10/15 ft setback, §23-42x mapping) is explicitly a G6 qualified-human determination and was NOT assessed here.** The rule family remains `needs_review`/verified-ineligible, correctly deferring that.

**Verdict: PASS** — required corrections: none. Final acceptance remains gated on G6 qualified-human legal approval per the packet (not this gate's scope).
