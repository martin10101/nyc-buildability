<!--
PROVENANCE: This is the code-reviewer's G3 return for M1-T006, saved VERBATIM by the
orchestrator from the agent-return channel (transport entity-decoding only, per the
report-preservation rule in .claude/rules/project-control.md). Reviewer agent id
a7ade15845c009897; review executed read-only in .claude/worktrees/M1-T006 @ 82d43ef;
saved 2026-07-16 by the orchestrator.
-->
# Gate Report

- Gate ID: G3 (independent human-style walkthrough)
- Task ID: M1-T006 — Property-profile contract v1.1 (additive)
- Reviewer: code-reviewer (independent; did not produce this work)
- Producer: backend-engineer (commit `32f0159`); orchestrator pairing commit `82d43ef`
- Result: **PASS** — no blocking corrections
- Clean environment/worktree used: yes — review executed read-only inside `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M1-T006` (branch `task/M1-T006-contract-v1-1`, base `c6ad0e6`), local Python 3.11 + jsonschema 4.26.0 + pytest + ruff. Producer report read LAST, after all independent verification.

## Acceptance criteria reviewed

Binding packet: `project-control/tasks/M1-T006.json` (main checkout) — scenarios S1–S8, six outputs, three risks. Cross-referenced against PRD §9/§12/§19/§20-17/§25/§32.3, ground-truth `services/api/app/profile/builder.py`, and reviewer memory carry-forwards (M0-T009 residual 3: invariant hard-coding; M0-T005: legacy-path testing technique).

## Steps independently executed

All commands run from the worktree root unless noted; every result below is the actual output I observed.

1. **S1/S2/S3/S4/S5/S8 — full validator run.** `python .github/scripts/validate_contracts.py` → **EXIT=0**, `Checked 6 schema file(s); 0 failure(s)`, engines `stdlib mini-validator + jsonschema 4.26.0 (cross-checked)`. All 7 valid fixtures OK (incl. `builder_output_m1_t005.json`, `full_example.json`, `full_example_v1_1.json`); all 15 invalid fixtures + 3 invalid_schemas rejected.

2. **Intended-reason verification.** I read all six new invalid fixtures; each carries exactly one deliberate defect and is otherwise complete (resolving provenance, valid BBL, etc.). Rejection messages match intent:
   - `bad_coverage_status_enum.json` → `$.lot_facts.lot_area_sf.coverage_status: value 'approved' is not one of the allowed enum values ['verified', 'conditional', 'professional_review_required', 'data_conflict', 'unsupported', 'not_applicable']` (the 6-enum $ref)
   - `bad_data_completeness_enum.json` → `$.data_completeness: value 'partial' is not one of ... ['complete', 'missing_noncritical', 'missing_critical']` (the 3-enum $defs $ref)
   - `contract_version_unknown.json` → `'1.2.0' is not one of the allowed enum values ['1.0.0', '1.1.0']`
   - `reproducibility_missing_correlation_id.json` → `missing required property 'correlation_id'`
   - `district_provenance_dangling_ref.json` → `$.zoning.district_provenance['R6']: provenance_ref 'prov-does-not-exist' does not resolve ... (PRD s19)`
   - `district_provenance_orphan_value.json` → `key 'C1-9' is not a member of the sibling zoning.districts array`
   Masking check: `main()` builds `all_errors = mini_errors + invariant_errors` and reports the first — the two S5 fixtures reporting invariant messages therefore proves their schema layer passed. Independently double-proven by tests `test_dangling_district_linkage_is_schema_clean_but_fails_integrity` / `test_orphan_district_linkage_is_schema_clean_but_fails_membership`, which assert `schema_errors(instance) == []` directly.

3. **S2 backward compatibility.** `git diff c6ad0e6 -- packages/contracts/schemas/v1/property_profile.schema.json` reviewed line-by-line: nothing removed, retyped, or newly required. Only change to existing keys: `contract_version` `const "1.0.0"` → **closed** `enum ["1.0.0","1.1.0"]`. All other changes are new OPTIONAL properties (`fact_value.coverage_status`, top-level `data_completeness` + `reproducibility`, three zoning provenance maps) and two new `$defs`. `git diff c6ad0e6 --stat` on `full_example.json`, `coverage_status.schema.json`, `common.schema.json`, `source_fact.schema.json` → **empty (byte-identical)**. Every pre-existing valid fixture passes (run in step 1).

4. **S3 boundary.** Schema text confirmed: `coverage_status` is `{"$ref": "coverage_status.schema.json"}` and `data_completeness` is `{"$ref": "coverage_status.schema.json#/$defs/data_completeness"}` — enums referenced, never duplicated inline. Both bad-enum fixtures reject; 1.2.0 rejects on the closed enum.

5. **S4 missing/null.** `full_example.json` (fact_values with no coverage_status) passes → key optional. `full_example_v1_1.json` has `"dataset_version": null` and passes both engines (`type: ["string","null"]` + `minLength: 1`, which correctly ignores null); `builder_output_m1_t005.json` exercises the string branch (`"26v1"`). Missing `correlation_id` rejected.

6. **S5 + validator diff.** `git diff c6ad0e6 -- .github/scripts/validate_contracts.py` reviewed in full: `profile_provenance_invariant` extended to `zoning.mapped_features[*].provenance_ref` and the three maps (`ZONING_PROVENANCE_MAPS`), plus the map-key membership rule. **No existing check weakened** — the fact-section loop is untouched, exit-code semantics unchanged, and the M0-T005-R1 fail-closed `_LocalOnlyRefResolver.resolve_remote` guard is intact. The M0-T009 carry-forward (any new provenance_ref site must extend the invariant in the same commit) is honored. Non-string refs inside lists still error (fail-closed); only list/dict shape errors defer to the schema layer (unit-tested not to crash).

7. **S6 ground-truth — strongest check: full independent regeneration.** I ran the real accepted code path — `fetch_by_bbl("1000010010", transport=FakeTransport([TransportResponse(200, <committed record>)]), clock=2026-07-16T12:00:00Z, correlation_id="m1t006-s6-ground-truth")` → `build_property_profile(result, clock=FIXED)` — and deep-diffed against the committed fixture: **`EXACT MATCH: regenerated builder output == committed contract fixture`** (all 1964 lines: 84 provenance records, 24 missing_inputs, all coverage_status values `conditional`, 10 reproducibility keys, `contract_version "1.0.0"`, no token in `request_url`). Note: the producer generated from F05, I regenerated from the matching F06a record; I verified `F05 vs F06a record identical: True` (same BBL 1000010010 record, zonedist1/2 = R3-2/C4-1, spdist1 = GI), so this is the same ground truth reached by an independent route — determinism confirmed.

8. **S7 legacy path + validator tests.** `python -m pytest .github/scripts/tests -q` → **24 passed**. Forced-legacy inspection: `monkeypatch.setitem(sys.modules, "referencing", None)` is applied AFTER jsonschema is fully imported, so `from referencing import ...` inside `make_validator` raises ImportError and execution genuinely lands on the RefResolver branch (this avoids the known pre-import-poisoning pitfall that kills jsonschema entirely). Tests prove all three property_profile valid fixtures resolve with zero errors on that branch, enum rejection fires, and an unknown remote `$ref` raises `remote $ref fetch blocked` (fail-closed). Honest caveat (producer disclosed): this exercises the script's branch on 4.26 internals, not literal 4.10.3 — mitigated because v1.1 introduces **zero new $ref patterns** (whole-document cross-file, cross-file into `$defs`, and internal `#/$defs/` all pre-exist since M0-T009 and pass on the real 4.10.3 CI runner), and G4 CI will provide the authoritative 4.10.3 evidence.

9. **Regression.** `cd services/api; python -m pytest tests -q` → **142 passed in 1.64s**. `git diff c6ad0e6 --stat -- services/` → exactly `services/api/tests/api/test_properties_v1.py | 1 +`.

10. **Pairing commit 82d43ef review.** One line: adds `"coverage_status.schema.json"` to the `profile_validator` registry tuple. **Correct and minimal**: v1.1's legitimate `$ref` into `coverage_status.schema.json` made the test's hardcoded 3-document registry incomplete; it failed closed (unresolved-reference error, 141/142 before pairing per producer evidence; 142/142 after — reproduced by me at head). The README's new "load all four referenced documents" consumer guidance documents the rule. No implementation code touched.

11. **Adversarial probes (my own, beyond the packet):**
    - A — district `R6` annotated under `commercial_overlay_provenance` (cross-map confusion): invariant rejects (`key 'R6' is not a member of the sibling zoning.commercial_overlays array`). Fail-closed.
    - B — `coverage_status: "verified"` on an unreviewed fact: **schema-legal** (enum must include it per PRD §12); non-emission is a documented builder/coverage_policy obligation (schema description + `_COVERAGE_POLICY` + G3 F7 comment in builder). Documented, not hidden. Info only.
    - C — empty `provenance_ref_list` `{"R6": []}`: schema rejects (`minItems 1`). Fail-closed.
    - D — map present, sibling `districts` array absent: invariant rejects (empty member set). Fail-closed.
    - E — duplicate refs in one list: accepted (no `uniqueItems`). Harmless noise; Info.
    - F — `contract_version "1.0.0"` instance carrying additive keys: valid — deliberate and correct, because the accepted M1-T005 builder emits exactly that (proven by the S6 fixture).

12. **Hygiene.** All new fixtures KB-scale (largest = 68 KB S6 ground truth — justified: it is the executable S6 proof, re-run on every CI validator pass; total new disk ≈ 90 KB, no installs/datasets, nothing written outside the worktree). `python -m ruff check` on the three touched Python files → clean; with the producer's `--config services/api/pyproject.toml`, `validate_contracts.py` shows 28 findings at head AND at base `c6ad0e6` (reproduced by me) → **zero new findings**, matching the producer's parity claim. No secrets in fixtures; no `.github/workflows` or other forbidden-path changes; producer stayed in scope (report file is the allowed exception; the one `services/**` line is the orchestrator's pairing commit, not the producer's).

## Expected versus actual

Every packet expectation met; no divergence found between producer claims and independent reproduction. The only claim I could not fully reproduce locally is real-4.10.3 behavior (my environment has 4.26); covered by the forced-branch tests plus the pending G4 CI run, consistent with how M1-T005 was gated.

## Evidence paths

- Worktree: `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M1-T006` @ `82d43ef`
- Schema: `packages/contracts/schemas/v1/property_profile.schema.json`; validator: `.github/scripts/validate_contracts.py`; tests: `.github/scripts/tests/test_validate_contracts.py`
- Fixtures: `packages/contracts/fixtures/valid/property_profile/{full_example_v1_1,builder_output_m1_t005}.json` + 6 new invalid fixtures under `packages/contracts/fixtures/invalid/property_profile/`
- Ground truth: `services/api/app/profile/builder.py` (lines 94–145, 341–396); regeneration inputs `services/api/tests/fixtures/pluto/F05_split_zone_lot.json` / `F06a_pagination_page1.json`
- Producer report: `project-control/reports/M1-T006-producer-report.md` (worktree)

## Human-style walkthrough findings

As a downstream consumer (the Priority 4 property screen), the contract is usable exactly as adjudicated in M1-T005 G3: a district string from `zoning.districts` joins O(1) to its evidence via the value-keyed map; partial/absent linkage degrades to the documented 1.0.0 `original_field_name` join, visibly rather than silently. README documents the versioning rule, all four additive keys, both integrity rules, and the four-document registry requirement accurately (I verified each claim against the code).

## Regression/security/provenance findings

Provenance strictly strengthened (referential integrity at every provenance_ref site + anti-fabrication key-membership rule); nothing weakened. Fail-closed remote-$ref guard regression-tested for the first time. No secrets, no network calls, no large local artifacts, no new dependencies.

## Defects

None blocking. Numbered findings:

1. **D1 (Low, carry-forward):** the 24-test validator pytest suite (including the fail-closed legacy-path regression tests) is not wired into any CI job (contracts job is stdlib-only by design; `.github/workflows/**` was forbidden to the producer). Producer disclosed (§5.2, §8.4). Orchestrator decision owed; recommend wiring at the next workflows touch.
2. **D2 (Info):** `provenance_ref_list` permits duplicate entries (probe E). Consider `uniqueItems: true` at the next contract minor.
3. **D3 (Info, documented by design):** `coverage_status: "verified"` is schema-legal on any fact (probe B); enforcement lives in the builder policy and future G6, as documented in the schema description. No action for this task.
4. **D4 (Info, carry-forward to the M2 builder task):** the builder still labels output `contract_version "1.0.0"` while emitting the three additive keys (legal, fixture-proven). When the M2 task adds district-map emission (producer §8.3), it must also bump `PROFILE_CONTRACT_VERSION` to `"1.1.0"` and extend `_assert_provenance_integrity` with both map rules.
5. **D5 (Info):** partial district linkage is a deliberate, documented permissive default (producer assumption 2); tightening later requires a major bump. The frontend must not assume full map coverage.

## Required rework

None. No correction blocks acceptance.

## Reviewer conclusion

**PASS.** All eight acceptance scenarios independently reproduced, including a full byte-exact regeneration of the S6 ground-truth fixture through the real connector + builder code path, line-by-line additive-compatibility verification of the schema diff, confirmation that the validator invariant was extended (not weakened) to every new provenance_ref site in the same commit, and six adversarial probes that all fail closed or are documented. The orchestrator pairing commit is correct and minimal. G4 CI (jsonschema 4.10.3 runner) remains the authoritative legacy-path evidence, per the packet's execution-location contract. Carry-forwards D1–D5 recorded in reviewer memory (`.claude/agent-memory/code-reviewer/project_m1-t006-g3-carryforward.md`) — none block acceptance.
