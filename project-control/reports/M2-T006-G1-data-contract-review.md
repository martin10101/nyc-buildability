# M2-T006 — G1 Independent Data-Contract Review

> Orchestrator preservation note: reviewer return saved VERBATIM from the agent-return channel (transport entity-decoding only, per the report-preservation rule in .claude/rules/project-control.md). Reviewer: data-contract-verifier. Received 2026-07-17, session 11. The reviewer's opening line before the report title was: "All verification is complete. Here is my gate report."

- **Reviewer:** data-contract-verifier (independent; not the producer)
- **Producer:** backend-engineer
- **Task:** M2-T006 — Property-profile contract 1.3.0 (additive): `reproducibility.staleness`, `correlation_id` description refresh, open-schema key documentation (amended packet A1)
- **Commit reviewed:** `cd0b385` on `task/M2-T006-contract-1-3-0` (implementation `e500ea5`; verified the delta `e500ea5..cd0b385` is exactly one file, `project-control/reports/M2-T006-G2-selfcheck.md`, orchestrator-recorded per the hardened-CLI convention)
- **Worktree:** `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T006`
- **Date:** 2026-07-17
- **Method:** started from the amended packet (`project-control/tasks/M2-T006.json`, S1–S7), my own prior findings D1/D2 in `project-control/reports/M1-T009-G1-data-contract-review.md`, and N3 in `project-control/reports/M2-T002-G3-human-journey-review.md` (UTF-16 file; read via PowerShell). Read the full diff `fb67d5a..cd0b385`, hand-traced the schema conditionals, executed all validation pipelines and the full api test suite myself, cross-checked PR #34 CI via read-only `gh`, and read the producer report and G2 self-check LAST.

## 1. Commands executed by this reviewer (all in the M2-T006 worktree)

| Command | Result |
|---|---|
| `python .github/scripts/validate_contracts.py` | 6 schemas, all valid fixtures OK, all invalid fixtures correctly rejected, 0 failures; engines = "stdlib mini-validator + jsonschema 4.26.0 (cross-checked)" |
| `python packages/contracts/scripts/generate_ts_types.py --check` | OK: generated TypeScript types are up to date (exit 0) |
| `python services/api/scripts/sync_contract_schemas.py --check` | OK: runtime-bundled schemas byte-identical to canonical source (exit 0) |
| `python -m pytest -q` (services/api) | **276 passed in 4.27s** (matches G2 claim: baseline 264 + 12 new) |
| `python -m pytest packages/contracts/scripts/tests -q` | 6 passed |
| 8-case conditional truth-table via `jsonschema.Draft202012Validator` (see §3) | all 8 cases behave as the schema descriptions claim |
| `gh pr view 34 --json state,headRefOid,statusCheckRollup` (read-only) | head = `cd0b385`; all 8 jobs × both events (push + pull_request) `COMPLETED/SUCCESS`, including `web-e2e`, `contracts-typegen`, `contracts-schema-bundle` |
| `git diff --stat fb67d5a..cd0b385`, per-file diffs, `git show --stat e500ea5 / cd0b385` | scope and commit-split verification (§7) |

## 2. D1 / D2 / N3 resolution assessment

**D2 (staleness object) — RESOLVED, exactly as asked.** My D2 asked for an additive `reproducibility.staleness` object with `served_from_cache`, `stale`, `upstream_error_type`, `original_retrieved_at`, `age_seconds`. The 1.3.0 schema adds precisely those five keys, no more, no fewer, and additionally fixes the second half of D2 (within-TTL cache serves previously had **no** explicit marker): the fetcher now stamps `{served_from_cache: true, stale: false, original_retrieved_at, age_seconds}` on every within-TTL cache hit (`services/api/app/resilience/fetcher.py:216-232`), asserted deterministically in `test_s3_cache_hit_emits_served_from_cache_with_monotonic_age`.

**D1 (correlation_id description) — RESOLVED, and the refreshed text is code-accurate.** Verified against the actual path: the serving endpoint generates its own id (`services/api/app/api/v1/properties.py:314`, `uuid.uuid4().hex`), always puts it in the `X-Correlation-ID` header (`:161`, `:406`), and passes it to the fetcher; on a fresh fetch the connector records it, so payload == header. On cache/LKG serves the fetcher returns a deepcopy of the **stored** result whose `correlation_id` is untouched (verified: cache-hit path sets only `staleness`; LKG path sets only `notes` + `staleness`), so the payload keeps the ORIGINAL fetch's id (`builder.py:627`) while the header identifies the serving exchange. The refreshed description states exactly this, including the J1 adjudication rationale ("rewriting it to the serving request's id would falsify reproducibility"). Sentence and code agree in both directions.

**N3 (open-schema keys) — RESOLVED, annotation-only, and accurate.** Three description-only additions, zero structural constraints added:
- `zoning.mapped_features` items: documented keys `feature`/`value`/`provenance_ref`/`coverage_status`/`units` match the builder exactly (`builder.py:367-373` emits `{"feature": column, **_fact_value(...)}`; `_fact_value` at `:292` emits value/provenance_ref/coverage_status and units only when present). The three example feature names (`splitzone`, `landmark`, `firm07_flag`) are all real members of `MAPPED_FEATURE_COLUMNS` (`builder.py:107-110`). Description correctly states the shape stays deliberately open.
- conflict item `reason`: builder emits `conflict.get("reason")` (`builder.py:501`) which can be `None` — the documented "string or null" is correct.
- conflict value `derivation`: builder emits exactly the two documented string forms (`builder.py:492`, `:497` — "derived from the canonical BBL digits" vs "record field '…' verbatim").

Behavior-neutrality confirmed by the clean full validate run, unchanged pre-existing fixtures, and 276/276 green.

## 3. Schema-conditional trace (hand-traced + engine-verified)

`packages/contracts/schemas/v1/property_profile.schema.json`, `reproducibility.staleness`:

- **Types/formats:** `served_from_cache`/`stale` boolean, both in object-level `required`; `upstream_error_type` → `common.schema.json#/$defs/non_empty_string`; `original_retrieved_at` → `common date_time` (RFC 3339, **pattern-enforced** plus `format: date-time`, so behavior is validator-independent); `age_seconds` `type: number, minimum: 0`. Number-not-integer is a deliberate, disclosed choice (monotonic-clock float subtraction; producer report §9) — correct, since forcing integer would truncate real ages.
- **Conditional 1 (`$comment`: cached ⇒ timestamp+age):** `anyOf[ {properties:{served_from_cache:{const:false}}}, {required:[original_retrieved_at, age_seconds]} ]`. Trace: `served_from_cache: true` fails branch 1 (const), so branch 2's `required` must hold. `false` satisfies branch 1 regardless. Absent `served_from_cache` would pass the anyOf vacuously but is caught by the object-level `required`.
- **Conditional 2 (stale ⇒ error-type + cached):** `anyOf[ {properties:{stale:{const:false}}}, allOf[{required:[upstream_error_type]}, {properties:{served_from_cache:{const:true}}}] ]`. Trace: `stale: true` forces the error type present AND `served_from_cache == true` — which then also triggers conditional 1, so a stale serve must carry all five keys. This encodes the correct real-world lattice: stale-but-not-cached is unrepresentable.
- **Engine equivalence:** confirmed the producer's claim — `if`/`then` is NOT in `validate_contracts.py`'s `KNOWN_KEYWORDS` (`.github/scripts/validate_contracts.py:81-90`), while `anyOf`/`allOf`/`const`/`$comment` are, and the stdlib mini-validator implements them (`const` at :323, applicator lists at :370-383, `properties` applying only to present keys at :348-351) — i.e. the chosen encoding is enforced in BOTH engines; my validate run confirmed "cross-checked" with jsonschema 4.26.0 present.
- **Truth-table (Draft202012Validator, ref-stripped subschema):** fresh marker `{false,false}` → valid; `{true,false}` without age/timestamp → invalid; complete cache hit → valid; stale without error type → invalid; **stale without cached → invalid**; full stale serve with `age_seconds: 0` boundary → valid; negative age → invalid; missing `served_from_cache` → invalid. All 8 as documented.
- **Committed invalid fixtures:** `staleness_cached_without_age.json` (`{true,false}` bare) and `staleness_stale_without_error_type.json` (`{true,true}` + timestamp + age, no error type) each violate exactly one conditional and nothing else; both rejected by the pipeline with `$.reproducibility.staleness: does not satisfy any schema in anyOf`. Additionally `test_s2_staleness_conditional_violations_are_schema_failures` proves the backend boundary (`validate_profile`) rejects both shapes with `schema_validation_failed`.

**Absence semantics:** unambiguous. The staleness description states in caps: "when this object is ABSENT the payload came from a pre-1.3.0 producer — consumers MUST NOT infer freshness from absence and must fall back to the connector-note convention plus the truthful retrieved_at," and that a 1.3.0 builder emits the object on EVERY serve with the fresh serve being exactly `{served_from_cache: false, stale: false}`. A consumer following the description cannot misread absence as fresh. The TS-consumer caveat (generated types carry no cross-field conditionals) is stated in both the schema description and the README — matches the generated `staleness?: {…}` block I diffed.

## 4. Emission truthfulness

- **Fresh path:** connector never sets `staleness` (additive dataclass default `None`, `pluto_soda.py:459`); builder emits exactly `{"served_from_cache": False, "stale": False}` when `None` (`builder.py:641-649`). Test asserts **exact** dict equality (no invented age/error values) both at the fetcher-direct path and the route path.
- **Cache-hit path:** `TTLCache.get_with_age` exposes the age the cache already computes for expiry from the **injected monotonic clock** (`cache.py`); fetcher stamps `original_retrieved_at` from the cached result's own `retrieved_at` and the per-serve age onto a deepcopy — `test_s3_cache_hit_age_is_per_serve_and_cache_entry_is_not_mutated` proves the stored entry never accumulates staleness state.
- **LKG path:** `upstream_error_type` is the **actual** typed failure (`exc.error_type` of the exception that triggered the fallback, including the circuit-open case which correctly classifies outward as `source_unavailable`); `original_retrieved_at` is the stored snapshot's `retrieved_at`; `age_seconds` is the same monotonic-clock age already computed for the LKG-max-age check (`fetcher.py:413`, `:444-450`). Nothing invented. The human-readable `served_from_last_known_good:` STALE note is **retained** unchanged alongside (`fetcher.py:429-438`; asserted in `test_s2_lkg_serve_emits_typed_staleness_and_retains_the_note`).
- **No relabeling hazard:** the TTL cache and LKG store are populated ONLY from fresh results (`fetcher.py:275-278`; LKG additionally only for `status == "ok"`), so a later cache hit can never overwrite a stale marker with `stale: false`.
- **Self-consistency:** `staleness.original_retrieved_at == reproducibility.retrieved_at` (never rewritten to serve time) is documented in the schema and asserted in `test_s2_lkg_profile_carries_staleness_and_passes_boundary_validation`.

## 5. Version discipline and compatibility (S1/S4/S5 results)

- Enum advanced to `["1.0.0","1.1.0","1.2.0","1.3.0"]`; builder `PROFILE_CONTRACT_VERSION = "1.3.0"`; declared-vs-emitted check extended via dotted-path resolution (`contract.py` `VERSION_INTRODUCED["reproducibility.staleness"] = "1.3.0"`, `_dotted_path_present`) with both a rejection test (declared 1.2.0 + staleness → `declared_version_below_emitted_keys`) and a false-positive-absence test. All four legs moved atomically in `e500ea5`: schema enum, builder constant, client vocabulary, exemplar fixture.
- Bounded unsupported-version behavior unchanged: `contract_version_unknown.json` advanced 1.3.0 → 1.4.0 in the same commit (validator run shows 1.4.0 rejected); test asserts the typed 500 with `declared_version == "1.4.0"`.
- **Backward compatibility executed, not assumed:** 1.0.0 (`full_example.json`, `builder_output_m1_t005.json`), 1.1.0 (`full_example_v1_1.json`), and 1.2.0 (`status_dimensions_lineage_m2_t004.json`) fixtures all carry **no** staleness object and all validate in my run. `test_s7_valid_1_2_0_instance_still_validates` and the strip-keys data-semantics test cover it at the backend boundary too.
- **A1 conformance:** the apps/web diff is exactly the two amendment-named files with exactly the amendment-named changes — one `"1.3.0"` array member in `SUPPORTED_CONTRACT_VERSIONS` (plus a comment refresh) in `contract.ts`, and one loop-vector update in `validate-profile.test.ts`. The `satisfies readonly ContractVersion[]` + generated union `"1.0.0" | "1.1.0" | "1.2.0" | "1.3.0"` keep the two vocabularies compile-time locked; typegen script tests assert the union and the enum.
- **Generated-artifact integrity:** both byte-identity checks pass in my environment and in CI (both events); the generated TS diff is machine-consistent with the schema change (union member + optional staleness block, no hand-edit artifacts, no competing handwritten representation anywhere in the diff).

## 6. Provenance and connector mapping (S7)

`pluto_soda.py` change is exactly an additive `staleness: dict | None = None` dataclass field plus docstring — no field mapping, normalization, unit, or provenance change (the G1-verified S9 mapping stands). `retrieved_at` semantics untouched everywhere (LKG serves keep the ORIGINAL retrieval moment — re-verified in code and tests). Existing provenance structures, digests, and connector_notes unchanged except the retained-note interplay documented above.

## 7. Scope and CI evidence

- Full diff `fb67d5a..cd0b385` contains ONLY: `packages/contracts/**` (schema, README, 3 fixtures, generated TS, script tests), `services/api/**` (bundled schema copy, connector dataclass, builder, contract, cache, fetcher, 5 test files), the two A1 files, and the two reports (`M2-T006-producer-report.md` in the producer commit; `M2-T006-G2-selfcheck.md` alone in the orchestrator-recorded G2 commit). No `docs/**`, `.github/**`, `.claude/**`, or other `project-control/**` files. Forbidden paths respected.
- CI cross-checked directly via read-only `gh`: PR #34 head is `cd0b385`; all 8 jobs SUCCESS on **both** push and pull_request events, including `web-e2e` (the executable proof that the real-builder harness declaring 1.3.0 passes the A1-updated client) and both byte-identity jobs. This matches the committed G2 report.

## 8. Findings

| ID | Severity | Blocking? | Location | Finding |
|---|---|---|---|---|
| O1 | Info | No | `M2-T006-G2-selfcheck.md` ("53 Playwright journeys") vs `M2-T006-producer-report.md` §10 ("43 Playwright web-e2e journeys") | Playwright journey count differs between the two evidence documents; one is a typo. CI green on both events regardless; suggest the orchestrator normalize the number when recording the gate. |
| O2 | Info | No | schema, staleness description | The staleness object description cites "M1-T009 G1 findings D1/D2" though the object itself resolves D2 (D1 is the correlation_id sentence, correctly cited at its own site). Defensible as a bundle citation since the refreshed D1 text cross-references the sibling staleness object; cosmetic only. |
| O3 | Info | No | `fetcher.py:413` | LKG `age_seconds` is measured from LKG **store** time (`entry.stored_at`), which coincides with retrieval within the same request under the injected clock; the emitted value is truthful for "age of the served snapshot at serve time". No action. |
| O4 | Info | No | `fetcher.py` cache-hit path | `no_match` cached results also receive the cache-hit staleness stamp (disclosed, producer report §9); truthful, and the route's 404 branch builds no profile so it never reaches a payload. No action. |

No blocking defects. No corrections required.

## 9. Verdict

Every packet scenario S1–S7 verified by direct execution or direct code/diff inspection; my prior D1/D2 findings are resolved exactly as specified; N3 is documented accurately and annotation-only; the conditional encoding is enforced identically in both validation engines and proven by hand-trace, truth-table, fixtures, and boundary tests; emission is truthful on all three serve kinds with no invented values and the human note retained; the 1.3.0 publication moved atomically across all four coordinated legs; backward compatibility is executed proof, not assertion; scope is exact; CI is green on both events at the reviewed head.

**PASS**

> Orchestrator note on O1 (recorded at gate time): the correct count is 53 Playwright journeys — verified directly from the PR #34 web-e2e CI log ("Running 53 tests using 1 worker … 53 passed"); the producer report's "43" is the stale pre-M2-T005 count and is the typo.
