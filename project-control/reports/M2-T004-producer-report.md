# M2-T004 Producer Report — Data-semantics separation and snapshot lineage

- **Task:** M2-T004 (owner code-audit P1, 2026-07-17)
- **Producer agent:** backend-engineer
- **Status requested:** `awaiting_gate`
- **Date:** 2026-07-17
- **Execution location:** owner PC (thin-client-safe: no installs, no network, KB-scale text edits; all runs offline on the committed official fixtures)
- **Worktree note:** the harness enforced producer isolation into `.claude/worktrees/agent-ac7184be439daaba6` (branch `worktree-agent-ac7184be439daaba6`), whose tree was verified IDENTICAL to `task/M2-T004-data-semantics` at session start (`git diff --stat task/M2-T004-data-semantics HEAD` → empty). All edits and evidence below live in that worktree; the orchestrator integrates to the task branch per ADR-005. (One read-only baseline pytest run happened in the `.claude/worktrees/M2-T004` checkout before the isolation guard redirected work; only `__pycache__` side effects exist there.)

## 1. What was built (all four owner P1 bullets)

### P1.1 Independent status dimensions + 108-column defect fix
- New OPTIONAL top-level `status_dimensions` object (contract 1.2.0), all six subfields REQUIRED when present: `source_record_completeness` (`complete|partial|not_computed`), `analysis_readiness` (`ready|blocked_missing_critical|blocked_data_conflict|not_computed`), `rule_coverage` (`not_computed` — single-value enum BY DESIGN until M4 makes applicability computable), `geometry_validity` (`missing|not_computed` — validation values land with the M2 geometry pipeline), `financial_readiness` (`not_computed` until a financial engine exists), plus a verbatim `policy` string (coverage_policy self-description pattern). Not-yet-computable dimensions are DECLARED, never inferred (PRD s12; GDS s3.3).
- **Defect fix:** `data_completeness` and `source_record_completeness` are now derived ONLY from the documented 19-column `FEASIBILITY_COLUMNS` basis (`services/api/app/profile/builder.py`): critical `lotarea`, `zonedist1`; noncritical `lotfront, lotdepth, lottype, irrlotcode, splitzone, landuse, bldgclass, bldgarea, numbldgs, numfloors, unitsres, unitstotal, yearbuilt, builtfar, residfar, commfar, facilfar`. Every column is cited in the builder's basis comment against the official "PLUTO DATA DICTIONARY — May 2026 (26v1)" (`https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/pluto_datadictionary.pdf`, G1-verified direct read) via `docs/research/pluto-mappluto-2026-07-16.md` s4.1/s4.3 (LotArea p.21; LotFront/LotDepth p.29; NumFloors p.28 incl. the null+NumBldgs>0 rule; YearBuilt p.34-35 null/0=unknown; BldgArea p.22; ResidFAR/CommFAR/FacilFAR p.36-37; splitzone/zonedist1 = README minor-release zoning attributes, research s3.2; lottype/irrlotcode/landuse/bldgclass/unitsres/unitstotal = official 108-column inventory F08 + dictionary appendices, research s4.2/OQ-5). Documented exclusions: conditional-presence zoning/regulatory columns (SODA null-omission makes absence indistinguishable from "none" — counting them recreates the defect), geometry columns (owned by the independent `geometry_validity` dimension), identity/administrative columns. `missing_inputs[]` entries keep listing ALL absent columns (visibility unchanged) and gain `feasibility_relevant` (basis membership).
- `data_completeness` key/enum/placement unchanged for v1.1 consumers (M2-T001 web reads it as optional; `apps/web` untouched).

### P1.2 Fact identity
Every connector fact now carries stable `fact_key` (`fact:<source_id>:<dataset_id>:<bbl>:<field>` — survives re-observation AND dataset-version change) and immutable `observation_id` (`obs:<event-id>:<bbl>:<field>`; event id minted fresh per fetch, injectable for tests, deliberately separate from correlation_id so a multi-fetch correlation can never collide observation ids). `provenance_id` (version-scoped) is UNCHANGED — all `provenance_ref`s intact.

### P1.3 Canonical digests
`canonical_json_digest()` + verbatim `CANONICALIZATION_SPEC` ("canonical-json-1": SHA-256 over UTF-8 of the parsed value serialized with sorted keys, `,`/`:` separators, no whitespace, non-ASCII preserved, no Unicode normalization, json.dumps number defaults). Per-fact `value_digest` (verbatim original_value) + per-retrieval `response_digest` (ENTIRE parsed body; also on no_match results — the empty array that proves absence is itself evidence). Recorded per response (`reproducibility.response_digest` + `digest_canonicalization`) and per fact.

### P1.4 Snapshot lineage
Gap-free chain on every fact: `observation_id`+`retrieved_at` (observation) → `dataset_version`/`dataset_id`/`source_id` (source version) → `request_url` (request) → `response_digest` (exact content). Builder now REFUSES a result without `response_digest` (fail-loud, mirrors `_assert_provenance_integrity`).

### Contract versioning (input to M2-T003 — deliberately not preempted)
Schema enum now `["1.0.0","1.1.0","1.2.0"]` (closed; rejected-exemplar fixture advanced to `1.3.0`). The builder still DECLARES `"1.0.0"` while emitting the additive keys (M1-T005/M1-T006 precedent). What M2-T003 owns, recorded in the enum description and README: which version producers declare, and whether declaration and emitted key set are validated against each other.

## 2. Files changed

Modified:
- `packages/contracts/schemas/v1/property_profile.schema.json` — 1.2.0: enum append, `status_dimensions`, `missing_inputs[].feasibility_relevant`, `reproducibility.response_digest`/`digest_canonicalization`, description updates (all additive; required sets untouched)
- `packages/contracts/schemas/v1/source_fact.schema.json` — 4 optional identity/lineage keys
- `packages/contracts/schemas/v1/common.schema.json` — `$defs/digest_sha256`
- `packages/contracts/README.md` — full 1.2.0 documentation (dimensions, basis + citations, identity table, digest spec, M2-T003 input)
- `packages/contracts/fixtures/invalid/property_profile/contract_version_unknown.json` — rejected exemplar `1.2.0`→`1.3.0` (publishing 1.2.0 legalized the old exemplar; caught by validator, fixed)
- `packages/contracts/fixtures/valid/property_profile/builder_output_m1_t005.json` — regenerated byte-exact from the NEW builder (same recipe: F05 capture, fixed clock, correlation_id `m1t006-s6-ground-truth`, pinned `observation_event_id=m2t004-s6-ground-truth-event`). Verified old==new **modulo additive keys** except exactly one intended change: `data_completeness` `missing_noncritical`→`complete` — the defect fix itself on a real official capture (F05's absences are all non-basis columns)
- `services/api/app/connectors/pluto_soda.py` — digest/identity emission, `observation_event_id` param, `response_digest` on results
- `services/api/app/profile/builder.py` — FEASIBILITY_COLUMNS basis (documented, cited), fixed `data_completeness` derivation, `_status_dimensions`, reproducibility lineage keys
- `services/api/tests/api/test_properties_v1.py` — S6 volatile set: `observation_id` added (volatile BY DESIGN per P1.2) + NEW disjointness assertion; fact_key/digests stay in the exact comparison (test is now STRICTER on content)
- `services/api/tests/connectors/test_pluto_soda.py` — same volatile-set update in the two S6 idempotency tests + stability/uniqueness/digest assertions added

New:
- `services/api/tests/profile/__init__.py`, `services/api/tests/profile/test_data_semantics.py` — 22-test S1–S6 acceptance pack (below)
- `packages/contracts/fixtures/valid/property_profile/status_dimensions_lineage_m2_t004.json` — synthetic 1.2.0 exemplar modeling S2 (complete record + missing geometry simultaneously); digests are REAL canonical-json-1 values recomputable from the shown content
- `packages/contracts/fixtures/invalid/property_profile/status_dimensions_unknown_value.json` — invented dimension label rejected
- `packages/contracts/fixtures/invalid/property_profile/status_dimensions_missing_dimension.json` — collapsed/omitted dimension rejected
- `packages/contracts/fixtures/invalid/source_fact/bad_value_digest_format.json` — non-sha256 digest rejected

NOT touched (forbidden/reserved): `services/api/requirements.txt`, `services/api/app/main.py`, `apps/web/**`, `render.yaml`, `docs/**`, `.claude/**`, `.github/workflows/ci.yml` (no CI change needed — existing jobs cover everything).

## 3. Acceptance scenarios and evidence

New pack `services/api/tests/profile/test_data_semantics.py` (22 tests):
- **S1** (5): basis ⊆ official 108-column inventory, |basis|=19, geometry excluded; synthetic all-basis-usable record with ~38 non-basis absences → `complete`/`complete` (108-denominator gone) while non-basis absences stay visible; official F01 gaps are exactly `{numfloors, yearbuilt}` (both dictionary-grounded unknowns) → `partial`/`missing_noncritical`; dropping `lotfront` degrades; every `missing_inputs` entry's flag equals basis membership.
- **S2** (4): complete record + no coordinates → `source_record_completeness=complete` AND `geometry_validity=missing` simultaneously; inverse (geometry present, `lotarea` dropped) → `not_computed`+`partial`+`blocked_missing_critical`+`missing_critical`; borocode conflict → `blocked_data_conflict` while completeness stays `complete`; `rule_coverage`/`financial_readiness` always declared `not_computed`, all six keys present.
- **S3** (3): re-observation preserves `fact_key`, issues fresh unique `observation_id`s; `fact_key` stable across a synthetic `26v1`→`26v2` version change while `provenance_id` changes; both identities persist in profile provenance.
- **S4** (4): digest key-order independence; byte-different but semantically identical bodies (reserialized with indent/sorted keys) digest EQUAL; one value change flips response digest and exactly that fact's value_digest; digests recorded per response (reproducibility) and per fact, each value_digest independently recomputable.
- **S5** (3): every fact carries all 9 lineage keys non-empty with retrieved_at/dataset_version/request_url matching the fetch (no gaps); no_match carries the digest of `[]`; builder refuses a digest-less result.
- **S6** (3): new profile validates against the evolved schema; profile STRIPPED of every M2-T004 key still validates (pre-1.2.0 shape remains valid); builder still declares `1.0.0`.
- **S6 fixtures side:** existing valid fixtures unmodified except the regenerated builder ground truth; `geosearch_bbl_fact.json`, `full_example.json`, `full_example_v1_1.json` untouched and passing = old shapes remain valid. Web e2e (M2-T001 journeys) not run locally — `apps/web` untouched and additive-only API changes; the CI `web-e2e` job is the regression harness per the task packet.
- **S7** is the data-contract-verifier's G1 re-verification of the documented column set/semantics — pending, reviewer-owned. Verification aids: the builder basis comment cites research-doc sections + dictionary pages per column; the synthetic fixture's digests are recomputable; `test_s1_basis_is_explicit_and_inside_the_official_inventory` pins the set against the official F08 inventory constant.

## 4. Commands run (exact) and results

Baseline before changes (green start), run in the task worktree:
```
$ cd .claude/worktrees/M2-T004/services/api && python -m pytest -q
142 passed in 1.70s            (exit 0)
$ python .github/scripts/validate_contracts.py
Checked 6 schema file(s); 0 failure(s).   (exit 0)
```

Mid-implementation (expected failures, both fixed):
```
$ python .github/scripts/validate_contracts.py     # after enum append
FAIL ...contract_version_unknown.json: fixture in 'invalid/' unexpectedly PASSED validation
-> fixed by advancing the rejected exemplar to 1.3.0
$ python -m pytest -q                              # after connector/builder changes
3 failed, 139 passed  (the three S6 idempotency tests: facts differ only by
observation_id, which is volatile BY DESIGN per owner P1.2)
-> volatile sets updated + disjointness assertions ADDED (tests now stricter on content)
```

Final verification (agent worktree, 2026-07-17):
```
$ python .github/scripts/validate_contracts.py
meta-schema engines : stdlib-structural + jsonschema 4.26.0
instance engines    : stdlib mini-validator + jsonschema 4.26.0 (cross-checked)
OK   [all 6 schemas, all valid fixtures incl. builder_output_m1_t005.json and
      status_dimensions_lineage_m2_t004.json; all invalid fixtures correctly
      rejected, e.g.:]
OK   ...contract_version_unknown.json (rejected: value '1.3.0' is not one of ['1.0.0','1.1.0','1.2.0'])
OK   ...status_dimensions_missing_dimension.json (rejected: missing required property 'financial_readiness')
OK   ...status_dimensions_unknown_value.json (rejected: value 'excellent' is not one of ['complete','partial','not_computed'])
OK   ...bad_value_digest_format.json (rejected: 'md5:abc' does not match pattern '^sha256:[0-9a-f]{64}$')
Checked 6 schema file(s); 0 failure(s).   exit=0

$ python -m pytest .github/scripts/tests -q
24 passed, 5 warnings in 0.59s            (exit 0)

$ cd services/api && python -m ruff check .
All checks passed!                        (exit 0)

$ python -m pytest -q
164 passed in 1.30s                       (exit 0; 142 baseline + 22 new S1-S6 tests)
```

Deterministic smoke (recorded during development, offline F01 replay): dimensions `{source_record_completeness: partial, analysis_readiness: ready, rule_coverage: not_computed, geometry_validity: not_computed, financial_readiness: not_computed}`; feasibility-missing exactly `['numfloors','yearbuilt']`; 40 non-basis absences no longer affect the label; `fact_key` stable / `observation_id` fresh across two fetches; response digest identical across identical bodies.

## 5. Expected vs actual

| Scenario | Expected | Actual |
| --- | --- | --- |
| S1 108-denominator gone | complete reachable; basis-only derivation | PASS (incl. real-capture proof: regenerated F05 ground truth flips to `complete`) |
| S2 independence | complete + missing simultaneously | PASS (3 directions) |
| S3 identity | fact_key stable, observation_id fresh, both persisted | PASS (incl. cross-version stability) |
| S4 digests | deterministic, sensitive, per response + per fact | PASS |
| S5 lineage | no gaps observation→version→request | PASS (+ no_match digest, fail-loud builder guard) |
| S6 additive | old shapes/fixtures valid; suite green; web untouched | PASS locally; web side proven by CI e2e job |
| S7 | reviewer G1 re-verification | PENDING (reviewer-owned) |

## 6. Assumptions, defaults, limitations

1. **Basis membership is a PLATFORM completeness policy** (like the pre-existing CRITICAL_COLUMNS), not a legal interpretation; every inclusion cites official grounding, and exclusions are argued from the verified null-omission semantics rather than invented per-column null meanings.
2. **Vacant-lot limitation (disclosed in the builder comment):** zero-vs-null serving is officially verified only for numfloors and yearbuilt; a genuinely vacant lot may read `partial`/`missing_noncritical` on building columns until verified research or the M2 confirmation workflow refines the policy. Completeness never blocks analysis — only CRITICAL gaps gate `analysis_readiness`.
3. **`analysis_readiness=ready` is a data statement**, not the PRD s32.1 workflow state; documented in schema + policy string so the future state machine cannot be bypassed by it.
4. **Digest canonicalization** uses Python json.dumps float defaults; SODA serves numeric raw values as strings, so float-representation variance is not exercised by real data. Spec is versioned (`canonical-json-1`) and stored verbatim per profile for future evolution.
5. **Idempotency tests' volatile set** now includes `observation_id` — a semantic consequence of P1.2, not a weakening: content comparison is stricter than before (fact_key + both digests compared exactly), and disjointness of observation ids is newly ASSERTED.
6. Builder still declares contract_version `1.0.0`; declaration/validation semantics are M2-T003's decision (documented in schema enum description + README).

## 7. Security / provenance impact

- Provenance strengthened: content-addressed snapshots (digests) + immutable observation identity + gap-free lineage; builder fails loudly on lineage gaps. No secrets touched; digests/ids contain no token material; observation event ids are uuid4 hex. No new dependencies (stdlib hashlib), no network in tests, no schema loosening (only additive optional keys + one enum value append per the version rules).

## 8. New risks / recommended next tasks

- M2-T003 must resolve declaration semantics (declare 1.2.0? bind declared version to emitted keys?) — inputs recorded in the schema and README.
- When the M2 geometry/rules/financial capabilities land, their tasks must extend the dimension enums ADDITIVELY via accepted contract tasks (single-value enums for rule_coverage/financial_readiness are deliberate).
- Reviewer attention: the regenerated `builder_output_m1_t005.json` (`data_completeness` flip is the intended defect fix; everything else additive), and the S7 column-set verification.

## 9. Report path

`project-control/reports/M2-T004-producer-report.md` (this file, in the agent worktree for orchestrator integration).
