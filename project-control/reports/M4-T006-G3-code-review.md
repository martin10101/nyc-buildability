_Verbatim independent code-reviewer return (transport entity-decoding only). Orchestrator-recorded; reviewer performed no git/ledger writes._

# G3 Code-Review Gate Report — M4-T006 (R5 height/setback DRAFT rule family)

**Reviewer:** independent code-reviewer (read-only)
**Reviewed SHA:** `6509db3` on `task/M4-T006-r5-height-setback` (PR #88); base `main` `c5e8cd0`
**Verification of frozen SHA:** worktree `HEAD` == `6509db3b525f8c93bdf0af6d57828e44e1312319` (confirmed via `git rev-parse HEAD`); files read are the frozen tree.
**Verdict: PASS**

## Commands run + actual outputs (all from `services/api`)

```
$ python -m pytest tests/rules/test_r5_height_setback.py -q
45 passed in 0.95s

$ python -m pytest tests/rules -q
225 passed in 3.44s

$ python -m ruff check .
All checks passed!
```

Snapshot byte-identity (packaged bundle vs canonical `docs/research` copy), all 5 files: `IDENTICAL` for zr-12-10, zr-23-421, zr-23-422, zr-23-423, zr-23-424.

Scope / core-untouched:
```
$ git diff 6509db3 c5e8cd0 -- services/api/app/rules/evaluator.py services/api/app/rules/integration.py
(empty)
```
`git diff --name-status 6509db3 c5e8cd0` (excluding project-control) shows ONLY the 6 new `*.rule.json`, 5 snapshots × 2 dirs, and the test file. `r5_residential_far.rule.json`, evaluator/integration core, canonical contracts, `app/api`, `app/scenario`, `apps/web` are all untouched.

## Findings against the 8 review requirements

1. **Per-district, no defaults/inheritance — PASS.** R5/R5A/R5B/R5D are each a separate rule file with `in_set` applicability on the exact district string (no `R5*` wildcard). R5 (`r5_height`: base 35 / building 45 + §23-423 setback) and R5D (`r5d_height`: building 45, NO setback, no base split) are distinct rules with explicit "encoded SEPARATELY" limitations. `test_nc1_*` prove a foreign district → `not_applicable`, outputs `{}`, and that `R5X` is never nearest-mapped.

2. **Correct values, no invention — PASS.** Every emitted dimension traces to a verbatim snapshot excerpt I confirmed byte-for-byte: R5 35/45 and R5B 35 and R5D 45 (zr-23-422); R5A perimeter 25 / ridge 35 (zr-23-421); setback 10 wide / 15 narrow (zr-23-423); wide/narrow = 75 ft (zr-12-10); QRS 45/55 (zr-23-424). Each rule citation `quote` is an exact substring of the corresponding snapshot `verbatim_excerpt`. No value appears that is not in a snapshot.

3. **Separate typed constraints + min/max — PASS.** `max_base_height`, `max_building_height`, `max_perimeter_wall_height`, `required_setback_depth` are separate named outputs (never collapsed, never labeled "envelope/feasible/massing"). Max caps encoded; R5's absent minimum base height is an explicit `no_minimum_base_height` documented-limitation exception (asserted by `test_as1_...`), not a silent 0.

4. **Fail-closed inputs — PASS.** `street_width_class` (r5-setback), `building_type` (r5a-height), `qualifying_residential_site` (r5-qrs-height) are REQUIRED inputs with no canonical field; when absent the evaluator returns `professional_review_required` with `outputs == {}` and `missing_critical` (`test_nc2_missing_...`, `test_nc4_*`, `test_nc5_*`). Out-of-enum street class (`"unknown"`) is rejected by input validation before computation (`test_nc2_invalid_...`, `input_validation.valid is False`) — the `param_select` map is never reached with a guessed key. The readiness matrix maps every condition to an exact `property_profile` path and marks street-width/building-type/QRS/historic/large-site as `unavailable`.

5. **rule_conflict — PASS.** §23-424 competes with base rules via the registry's existing `detect_conflicts`/`detect_rule_conflicts` (evaluator/integration core diff empty, confirmed). Conflict is deterministic, order-independent (`test_nc7_conflict_is_order_independent`), sorted `["r5-height","r5-qrs-height"]`, with NO `value` key. No spurious conflict for ordinary R5.

6. **needs_review / never verified — PASS.** All 6 rules `status: needs_review`, `qualified_human_approval: pending`, `effective_from: 2024-12-05`. Evaluator makes `verified` unreachable without a published rule + matching G6 approval; `test_as5_*` assert `verified_eligible is False` and family coverage tops out at `conditional`. `as_of` before 2024-12-05 → `not_applicable`, outputs `{}` (`test_as3_*`).

7. **Determinism + provenance — PASS.** `test_as4` proves byte-identical export. Each snapshot carries `content_digest_sha256`; the loader recomputes and a tampered excerpt raises `content_digest_sha256 mismatch` (`test_as2_tampered_...`); an absent snapshot raises (`test_as2_absent_...`). Every emitted dimension carries section + verbatim quote + `last_amended 2024-12-05` + provenance digest.

8. **Scope — PASS.** See name-status diff above; only rulesets/snapshots/tests (+ ledger) changed.

**Disclosed-item assessment:** `raw_html_verified:false` + `extraction_status:extracted_draft` on all 5 snapshots, and the §23-42/426/44/425 modifier contexts implemented as `professional_review_required` exceptions with `citation_ref:null` (their verbatim text was not captured), are the CORRECT needs_review/G6 posture — no value is emitted from an uncaptured modifier; they fail closed. Not code defects.

## Non-blocking observations (for orchestrator / G6, not corrections)

- **N1 (informational).** For the *modifier* contexts (overlay/special-district/historic/large-site present), the numeric base value stays in `outputs` while `coverage_status` is downgraded to `professional_review_required` (the sanctioned "surface-but-flag" pattern from the accepted FAR rule; `test_nc3` asserts coverage=PRR but not empty outputs). This is not a guessed value and not an "absent governing input" case — but downstream M5 consumers must gate on `coverage_status`, not on outputs emptiness. Correct by design; flagged for consumer awareness.
- **N2 (doc nit).** The producer report §6 cites frozen candidate `edddbbf` and commits `3f9d6aa/efef508/edddbbf`; the branch was subsequently recommitted (`8a87cc8/e2ee125/6509db3`). Content verified equivalent at the actual frozen SHA `6509db3`; report commit hashes are stale only.
- **N3 (scope note).** `r5-setback` applies only to district `R5`; the §23-424 QRS envelope for R5A/R5B/R5D does not auto-emit a setback. Documented as a separate-constraint limitation in the QRS rule; acceptable for this draft slice.
- **N4 (interpretation).** Review item 5 groups overlay/special-district with `rule_conflict`; the implementation correctly routes modifier contexts → PRR (no competing same-family rule is encoded) and the §23-424 alternative → `rule_conflict`. Both fail closed with no final value. Acceptable.

## Reproducibility note
All commands above executed successfully in this environment (Python 3.11 local). Producer's `pip install --no-deps .` wheel test could not run locally (interpreter <3.12); deployability is instead covered green by `test_installed_deployability.py` + `test_zr_snapshot_bundle.py` (part of the 225-pass `tests/rules` run). Recommend the orchestrator capture the `pip install --no-deps ./services/api` log on the CI 3.12 `api` job for the record; the resolution mechanism is already exercised green.

**Final verdict: PASS.** No blocking defects. Final acceptance/publication remain gated on G6 qualified-human legal approval (unchanged, not weakened by this review).
