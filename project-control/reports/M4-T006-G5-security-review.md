_Verbatim independent security-reviewer return (transport entity-decoding only). Orchestrator-recorded; reviewer performed no git/ledger writes._

# G5 Security & Privacy Gate Report — M4-T006 (R5 height/setback draft rule family)

**Reviewer:** Independent G5 (security & privacy), read-only
**Reviewed SHA:** `6509db3` on `task/M4-T006-r5-height-setback` (PR #88)
**Base:** `main` @ `c5e8cd0`
**Verdict:** **PASS** (no blocking findings; one LOW informational carry-forward, non-blocking)

## Scope verification (focus #5) — PASS
`git diff --name-only 6509db3 c5e8cd0` returns only: 6 new `services/api/app/rules/rulesets/r5*.rule.json`, 5 packaged `services/api/app/_zr_snapshots/v1/*.snapshot.json`, 5 mirror `docs/research/zr-snapshots/v1/*.snapshot.json`, `services/api/tests/rules/test_r5_height_setback.py`, and `project-control/*` bookkeeping. The evaluator core (`dsl.py`, `registry.py`, `coverage.py`, `snapshots.py`), the FAR rule, API endpoints, web, and canonical contracts are **untouched**. Packaged vs. `docs/` snapshots are byte-identical (verified all 5). No engine or contract was silently modified.

## Commands run and actual outputs
- `python -m pytest tests/rules/test_r5_height_setback.py -q` → **`45 passed in 0.84s`**
- Independent digest recompute (sha256 of `verbatim_excerpt` per snapshot) → all **OK** (stored == computed) for zr-12-10, zr-23-421, zr-23-422, zr-23-423, zr-23-424; every snapshot `raw_html_verified=False`, `extraction_status=extracted_draft`.
- Computation-op enumeration of the 6 new rules → only `identity` (r5_setback also uses a static `param_select` map arg). No `eval`/`exec`/`multiply`/dynamic op. (`multiply`/`zr-23-21` seen in the glob are pre-existing out-of-scope files.)
- Secret/URL/path/dynamic-exec scan over all new files → **no matches** for http (non-official), password/secret/token/api-key/bearer, `.env`, `os.environ`, `subprocess`, `eval(`, `exec(`, or absolute filesystem paths. Only official public `zr.planning.nyc.gov` URLs present.

## Focus-area findings

1. **Draft-not-Verified integrity — PASS.** All six rules carry `status: "needs_review"`, `release.independent_review: "pending"`, `release.qualified_human_approval: "pending"`. `test_as1_conditional_never_verified_for_every_variant` asserts `coverage_status != VERIFIED` and `trace.rule_release["verified_eligible"] is False`; `test_as5_*` asserts `status == needs_review` and approval pending for all six. Because the (untouched) evaluator maps `needs_review → verified-ineligible`, no path can up-label these to Verified; G6 remains structurally required. Confident outputs surface as `conditional`, never `verified`.

2. **Fail-closed / no crash — PASS.** Missing street-width class (NC-2), out-of-enum street class (NC-2), unavailable building type (NC-4), unavailable qualifying-residential-site geography (NC-4), missing district (NC-5), contradictory district signals (NC-6 → `data_conflict`), uncertain geometry (NC-6 → `professional_review_required`), and simultaneously-applicable base vs. QRS envelopes (NC-7 → `rule_conflict`, `"value" not in conflict`) all yield typed downgrades with `outputs == {}`. No fabricated dimension, no non-finite value, no crash. All emitting steps are `identity` selections from static parameters. Street-width, building-type, and QRS geography are declared REQUIRED inputs with no canonical source and fail closed rather than being guessed.

3. **Provenance integrity / tamper-evidence — PASS.** The digest guard in `snapshots.py` (`_digest` = sha256 of `verbatim_excerpt`; `load_snapshot_file` raises `SnapshotError` on mismatch) is genuine and independently confirmed honest for all 5 snapshots. `test_as2_tampered_snapshot_fails_closed` proves a mutated excerpt with a stale digest raises `content_digest_sha256 mismatch`; `test_as2_absent_snapshot_fails_closed` proves an unknown id raises `unknown snapshot_id`. `test_as2_every_emitted_dimension_traces_to_snapshot_provenance` confirms every emitted value carries `snapshot_id` + `content_digest_sha256`. `raw_html_verified: false` and `extraction_status: extracted_draft` are truthful (not overclaiming), consistent with never-Verified.

4. **No injection / secret / PII leak, least privilege — PASS.** Rule JSON is declarative data over a fixed op vocabulary consumed by the untouched evaluator — no dynamic execution, no network/fs/env/DB reach, no format-string injection surface. No secrets, credentials, tokens, or internal paths in rule text, outputs, or error strings. Snapshot content is static official public ZR text (only `zr.planning.nyc.gov` URLs); no PII.

## Non-blocking finding

- **LOW / informational (carry-forward, out of scope):** The snapshot content digest covers only `verbatim_excerpt`, not the structured `table`/`notes` fields (`snapshots.py:129-139`). A tamper limited to a `table` row (e.g. zr-23-422/zr-23-424 numeric cells) would not be caught by the hash. This is not a defect of M4-T006: (a) `snapshots.py` is pre-existing M4-T001/T005 infrastructure outside this task's diff; (b) rule parameter values live in the rule JSON (independently reviewable), not sourced from the snapshot `table`; (c) every value is `needs_review`/verified-ineligible and gated on G6 raw-HTML byte-level verification before any Verified surface. Recommend the eventual verification/publication task extend the digest to cover structured fields. Does not block this draft rule-data gate.

## Conclusion
No way for a draft R5 height/setback value to surface as Verified or be up-labeled; no value can be fabricated without cited, hash-guarded provenance; every uncertain/unavailable/contradictory input fails closed to a typed status with no crash or leak; scope is confined to rule data, snapshots, tests, and bookkeeping. **Verdict: PASS.**
