# M2-T006 — G3 Independent Code Review (with G4 integration assessment)

> Orchestrator preservation note: reviewer return saved VERBATIM from the agent-return channel (transport entity-decoding only, per the report-preservation rule in .claude/rules/project-control.md). Reviewer: code-reviewer. Received 2026-07-17, session 11. This single report carries the G3 verdict and a separate explicit G4 integration/regression assessment; the orchestrator records the two gates separately, both citing this report.

- **Task:** M2-T006 — Property-profile contract 1.3.0 (additive): typed `reproducibility.staleness`, `correlation_id` description refresh, open-schema key documentation (amendment A1)
- **Gate:** G3 independent human-style walkthrough (this report also contains the G4 integration/regression assessment as a separate section)
- **Reviewer:** code-reviewer (independent; did not produce this work; read-only per ADR-005)
- **Producer:** backend-engineer
- **Branch/commit reviewed:** `task/M2-T006-contract-1-3-0` @ `cd0b385` (implementation `e500ea5`; verified the `e500ea5..cd0b385` delta is only `project-control/reports/M2-T006-G2-selfcheck.md`), reviewed in the checked-out worktree `.claude/worktrees/M2-T006`
- **Diff basis:** `git diff fb67d5a..cd0b385` (base = main containing amendment A1)
- **Date:** 2026-07-17
- **Method:** started from the AMENDED packet acceptance criteria (S1–S7) and the raw diff, not the producer's conclusions; walked every serve path in the code; re-executed all locally executable evidence; read the producer report and G2 self-check last and cross-checked their claims.

## Commands run and results (independent re-execution)

| Command | Result |
|---|---|
| `python -m pytest tests -q` (in `services/api`) | **276 passed in 4.08s** (matches producer's 276 = 264 baseline + 12 new) |
| `python .github/scripts/validate_contracts.py` | **Checked 6 schema file(s); 0 failure(s)**; both new invalid staleness fixtures rejected at exactly `$.reproducibility.staleness: does not satisfy any schema in anyOf`; `contract_version_unknown.json` rejected on the closed enum with 1.4.0 |
| `python packages/contracts/scripts/generate_ts_types.py --check` | OK: generated TypeScript types are up to date |
| sha256 compare `packages/contracts/schemas/v1/property_profile.schema.json` vs `services/api/app/_contract_schemas/v1/property_profile.schema.json` | **IDENTICAL** (`f4d6a156…43fa47` both sides) |
| `python -m ruff check services/api/app services/api/tests packages/contracts/scripts` | All checks passed |
| `git diff --quiet` (worktree) | Clean — no uncommitted or generated local artifacts |
| `gh pr view 34 --json statusCheckRollup` (read-only) | headRefOid = `cd0b385…`; **16 check entries = 8 jobs × 2 events (push + pull_request), all SUCCESS** — api, contracts, contracts-typegen (byte-identical), contracts-schema-bundle (byte-identical), web, web-e2e (vitest + Playwright), control-plane, credential scan |
| `grep datetime.now\|time.time\|utcnow` in `tests/resilience/test_staleness.py` | No matches — injected-clock discipline holds |

## Per-area findings

### 1. builder.py — staleness emission on every serve path (S2/S3/S4)
Walked all three paths end to end:

- **Fresh:** connector never sets `staleness` (`PlutoFetchResult.staleness: dict | None = None`, additive defaulted field, `pluto_soda.py:459`); builder emits exactly `{"served_from_cache": False, "stale": False}` (`builder.py:645-647`). Test `test_s3_fresh_profile_emits_the_fresh_marker_and_validates` asserts **exact dict equality**, so no invented age/error values can ride a fresh serve. Route-level assertion added too (`test_properties_v1.py:250`).
- **Cache hit:** `fetcher.py:216-233` stamps `{served_from_cache: True, stale: False, original_retrieved_at: <original retrieved_at>, age_seconds: <injected monotonic age>}` on a deep copy. Critically, **the stamp can never mask a prior stale serve**: the TTL cache is populated only at `fetcher.py:275` from fresh fetch results (staleness `None` at put time), and LKG serves are never re-inserted into the cache — so the overwrite is always fresh-origin. `test_s3_cache_hit_age_is_per_serve_and_cache_entry_is_not_mutated` proves per-serve ages (20.0 then 45.0) with a single upstream call and no entry mutation.
- **LKG:** `fetcher.py:444-450` stamps `{served_from_cache: True, stale: True, upstream_error_type: exc.error_type, original_retrieved_at, age_seconds}`; LKG entries come only from fresh `ok` results (`fetcher.py:277-278`). The circuit-open variant is covered (`test_s2_breaker_open_lkg_serve_…`).
- **Can a path emit nothing when it should?** No: the builder's ternary at `builder.py:645` guarantees emission on every 200; `no_match` cached results also get a truthful stamp but build no profile (route 404) — disclosed in producer report §9 and correct.
- **Wall-clock:** ages come from the injected `now` (monotonic) callable; no `datetime.now`/`time.time` in the new tests; production defaults (`time.monotonic`, `_utc_now`) are injection points only. The 4.08s full-suite runtime is itself evidence no real sleeps/clocks entered the tests.

### 2. cache.py — `get_with_age`
Correct and backward compatible. `get()` now delegates (`hit[0]`), so existing callers see identical semantics (expiry-on-observation, `cache_expired` metric, LRU `move_to_end`, same lock). Age is `now - entry.stored_at` — the same age the cache already computed for expiry, so no second clock source. Absence returns `None` in both methods.

### 3. fetcher.py — LKG stamping and taxonomy
- `original_retrieved_at` is `result.retrieved_at` of the **stored snapshot** (original retrieval), never serve time; `retrieved_at` itself is untouched (M1-T009 provenance rule preserved), and `test_s2_lkg_profile_…` asserts `staleness.original_retrieved_at == reproducibility.retrieved_at == fresh.retrieved_at`.
- `upstream_error_type` taxonomy verified against the actual connector classifiers: only retryable failures reach LKG (`_is_retryable`), so the possible values are exactly `source_unavailable` (incl. circuit-open, which subclasses `SourceUnavailableError` by design), `timeout`, `rate_limited` — matching the schema description's examples. `schema_drift` is non-retryable and can never appear; `budget_exceeded` is never masked by LKG (`fetcher.py:256-257`). No raw upstream strings.
- The human `served_from_last_known_good:` note is retained **verbatim unchanged** (`fetcher.py:429-438` — no diff to the note text); tests assert both channels coexist.

### 4. contract.py — dotted-path `VERSION_INTRODUCED`
Sound. `_dotted_path_present` degrades exactly to the previous `key in profile` behavior for single-segment keys (no behavior change for the 1.1.0/1.2.0 keys); intermediate segments must be dicts; there is no unknown-path acceptance surface because `VERSION_INTRODUCED` is a closed reviewed map, and the schema remains the structural authority. Version-gating direction preserved: declaring 1.2.0 while emitting `reproducibility.staleness` is rejected (`test_s6_declared_12_with_staleness_is_rejected_via_dotted_path`), and the no-false-positive companion test proves absence detection through the nested walk. `select_schema_version`/`unsupported_contract_version` code untouched; bounded behavior re-proven with the new 1.4.0 exemplar including the never-coerced assertion.

### 5. Schema encoding (disclosed deviation if/then → allOf/anyOf/const)
Verified the deviation's stated reason against the validator: `validate_contracts.py` enforces a keyword allowlist without `if`/`then` (its own broken-schema fixture output confirms the allowlist mechanism). The encoding is **logically correct**: both `anyOf` escape branches use `{"properties": {<flag>: {"const": false}}}`, which could vacuously pass if the flag were absent — but both flags are in the object's `required` list, so no vacuous bypass exists. `stale: true ⇒ upstream_error_type required AND served_from_cache const true` correctly forbids the stale-but-not-cached contradiction. Both invalid fixtures fail on both validation engines for exactly this condition. Readability: each `allOf` branch carries a `$comment` stating the human-readable rule, and the README documents the encoding and its reason — adequately maintainable.

### 6. Fixtures and exemplar move
`contract_version_unknown.json` 1.3.0→1.4.0 in the same commit — 1.4.0 is genuinely unpublished, the `_expected_failure` text was updated honestly, and the typegen leak-guard moved to `'"1.4.0"' not in ts`. The valid LKG fixture is labeled SYNTHETIC with a truthful note mirroring the real M1-T009 note format; the two invalid fixtures each violate exactly one conditional (cached-without-age carries `stale: false` so only the first conditional trips; stale-without-error-type carries age fields so only the second trips) — well-isolated boundary exemplars.

### 7. Tests — genuineness and honesty of updates
- The 7 new `test_staleness.py` tests are non-vacuous: exact-dict equality assertions, upstream-call counting, per-serve age arithmetic against the injected clock, boundary validation via the real `validate_profile`, and both-channels assertions.
- The 5 new `test_property_contract.py` tests cover the two conditional violations at the backend boundary, dotted-path rejection + no-false-positive, and 1.2.0-fixture + 1.3.0-LKG-fixture compatibility.
- The 4 updated test files change only for the honest version-advance reason; **no existing assertion was weakened** — several were strengthened (e.g. `test_s6_no_stale_version_hard_coded_in_builder_source` now also forbids a stale `"1.2.0"` pin; the route test gains the exact fresh-marker assertion; `test_data_semantics` pre-M2-T004-shape test also strips staleness so the 1.1-shape regression remains real).

### 8. A1 client edits and scope
`apps/web` diff contains **exactly** the two A1 files: `contract.ts` (+`"1.3.0"` in `SUPPORTED_CONTRACT_VERSIONS` plus the doc-comment describing that same pin — within the vocabulary-addition grant) and `validate-profile.test.ts` (published-version loop pin only). The `satisfies readonly ContractVersion[]` check plus the vitest loop plus green web-e2e against the real 1.3.0-declaring builder prove consistency with the generated union. Full diff file list contains only `packages/contracts/**`, `services/api/**`, the two A1 files, and the two reports — no workflow, docs, or other project-control changes. Grep confirms no other `apps/web` file references `1.3.0`.

### 9. Maintainability and honesty
README 1.3.0 section is high quality: serve-kind table, encoding deviation with reason, absence semantics, TS-conditional caveat, and the **R-NEW-1 systemic note stated honestly** ("publishing a contract version is always a coordinated schema + backend + client-vocabulary change… A future contracts-tooling task may generate the client's runtime version array"). Stale statements in the older README sections were corrected rather than left contradictory. The producer report's STOP→A1 history and the D-1 deviation are disclosed transparently.

## Findings table

| ID | Severity | File:line | Finding | Blocking? |
|---|---|---|---|---|
| D1 | LOW | `services/api/app/profile/contract.py:16-20` | Module-level docstring still states "the builder declares ``1.2.0`` because it emits keys through 1.2.0" — stale after this task's advance to 1.3.0. The producer updated the `VERSION_INTRODUCED` comment block and function docstrings but missed the module header. Doc-only; no behavioral effect (the real declaration is test-asserted and sourced live), but this module is the self-described "single backend source of truth" and stale descriptions are exactly the defect class this task fixes (G1 D1). Recommend a one-line fix at next touch of this file (or fold into acceptance hygiene). | No |
| OBS-1 | INFO | `packages/contracts/schemas/v1/property_profile.schema.json` (staleness `allOf`) | Conditionals are one-directional: a payload with `served_from_cache: false` **plus** `original_retrieved_at`/`age_seconds`/`upstream_error_type` present would still validate (the "never invented on fresh serves" rule is description-level). Production cannot emit this (builder tests pin exact fresh-marker equality), but future producers must keep test-level enforcement. Consistent with the contract's additive-optional philosophy; recorded for the next contract revision. | No |
| OBS-2 | INFO | `apps/web/src/lib/contract.ts:81-88` | `satisfies` prevents invalid members but not omission; completeness of the client version array is proven by the vitest loop and web-e2e only. The recommended R-NEW-1 follow-up (generate the array from the schema enum) should be tasked before any 1.4.0 publication. | No |
| OBS-3 | INFO | `services/api/app/connectors/pluto_soda.py:462` | `staleness: dict | None` is untyped; a `TypedDict` would give static shape safety. Cosmetic; the schema boundary enforces shape at runtime. | No |

No defects of MEDIUM or higher severity found. No guessed schemas, no hard-coded legal values, no hidden defaults (the fresh marker is an explicit, schema-documented, test-pinned emission — not a silent default), no silent uncertainty (STOP→A1 and D-1 both disclosed), no invented values on any serve path.

---

## G4 — Integration and regression assessment (separate verdict)

- **Full suite:** independently rerun — `python -m pytest tests -q` = **276 passed** (0 failures/skips), `ruff` clean across `services/api` and `packages/contracts/scripts`. CI PR #34 at exactly the reviewed commit `cd0b385`: **all 8 jobs green on both push and pull_request events** (verified via read-only `gh pr view 34 --json statusCheckRollup`, 16/16 SUCCESS), including web (tsc), web-e2e (vitest + 53 Playwright journeys against the real 1.3.0-declaring builder), and control-plane.
- **Contract compatibility:** 1.0.0/1.1.0/1.2.0 instances validate against the 1.3.0 schema — proven three ways: fixture CI (`validate_contracts.py`, 0 failures, both engines), backend boundary tests (`test_s7_valid_1_2_0_instance_still_validates`, existing 1.0.0/1.1.0 S7 tests unchanged and passing), and the strip-down regression in `test_data_semantics.py`. Nothing required, removed, or retyped.
- **No duplicate/contradictory implementations:** repo-wide grep for version lists found exactly the documented set — canonical schema enum (two byte-identical copies, sha256-verified locally and by the schema-bundle CI job), generated TS union (byte-identity typegen CI job + pinned test), backend `SUPPORTED_CONTRACT_VERSIONS` (derived live from the bundled schema, asserted by two tests), client array (type-`satisfies` + vitest + web-e2e). Every list is either derived or independently test-asserted; all agree on `1.0.0/1.1.0/1.2.0/1.3.0`.
- **Byte-identity jobs:** contracts-typegen and contracts-schema-bundle green in CI; both independently reproduced locally (`--check` OK; sha256 identical).
- **Migrations/RLS:** no database or storage changes in this diff — not applicable.
- **Performance:** negligible — `get_with_age` reuses the age the cache already computed under the same lock; one dict construction per cached/LKG serve; full suite runs in ~4s.
- **Low-storage/artifacts:** worktree clean after all runs; new committed files are small text fixtures/tests; no large or persistent local artifacts written.

**G4 verdict: PASS.**

---

## Final G3 verdict

**PASS.**

No blocking corrections. D1 (stale `contract.py` module docstring) is a non-blocking LOW recommended for the next touch of that file; OBS-2 (R-NEW-1 client version-array generation) should be converted to the recommended contracts-tooling micro-task before the next contract version publication.

Key evidence paths (all absolute):
- Worktree reviewed: `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T006`
- Packet: `...\M2-T006\project-control\tasks\M2-T006.json`
- Core code: `...\M2-T006\services\api\app\resilience\fetcher.py` (lines 216–233, 444–450), `...\services\api\app\resilience\cache.py`, `...\services\api\app\profile\builder.py` (line 645), `...\services\api\app\profile\contract.py` (D1 at lines 16–20)
- Schema: `...\M2-T006\packages\contracts\schemas\v1\property_profile.schema.json`
- New tests: `...\M2-T006\services\api\tests\resilience\test_staleness.py`
- Producer/G2 reports: `...\M2-T006\project-control\reports\M2-T006-producer-report.md`, `...\M2-T006-G2-selfcheck.md`
