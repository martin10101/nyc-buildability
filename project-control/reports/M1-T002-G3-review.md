# Gate Report

- Gate ID: G3 (independent human-style walkthrough)
- Task ID: M1-T002 — PLUTO SODA connector (64uk-42ks) with provenance and contract tests
- Reviewer: code-reviewer (independent; did not produce this work; not running G1)
- Producer: backend-engineer
- Result: **PASS** (7 findings, none blocking; carry-forwards listed for the property-profile API task)
- Clean environment/worktree used: yes — producer's committed worktree `.claude/worktrees/M1-T002`, branch `task/M1-T002-pluto-soda-connector`, commit `9e22839`, reviewed read-only; all commands re-executed by this reviewer first-hand. Review order per gate standard: task packet S1–S8 first, implementation/tests/fixtures second, research doc §4/§6 third, producer report last.

## Acceptance criteria reviewed

`project-control/tasks/M1-T002.json` scenarios S1–S8, cross-referenced against:
- `docs/research/pluto-mappluto-2026-07-16.md` §4 (dictionary semantics: NumFloors p.28, BBL p.38, units p.21/p.29/p.39-40, condo/billing §4.4) and §6 (fixture pack F1–F14)
- `packages/contracts/schemas/v1/source_fact.schema.json` + `common.schema.json` (M0-T009, untouched)
- M1-T001 G3 carry-forwards: (1) BBL decimal-serialization normalization, (2) `query.soql.no-such-column` drift signature, (3) OQ-4/OQ-10 out of scope, (6) app token = optional/human/env-only

## Steps independently executed

All from the worktree; exact commands reproducible.

1. `git show --stat 9e22839` — 26 files, 2156 insertions, every path inside `allowed_paths`; no `packages/contracts/**`, no `docs/**`, no workflow/tool files touched.
2. `cd services/api && python -m pytest tests -q` → **87 passed in 1.07s** (0 skipped — jsonschema contract validation ran, not skipped). Matches producer claim.
3. `python .github/scripts/validate_contracts.py` → **Checked 6 schema file(s); 0 failure(s)** (S8 re-verified independently).
4. Hands-on API exercise via injected fixture transport (downstream-consumer walkthrough):
   - **Normal (S1):** `fetch_by_bbl("1000010100")` vs F01 → `status=ok`, **67 facts**, `dataset_version=26v1`; `lotarea` fact carries all 12 required source_fact v1 keys + additive `dataset_id`/`request_url`/`input_vintages`; `provenance_id=pluto-64uk-42ks-26v1-1000010100-lotarea`; `units="square feet"`.
   - **Boundary (S2a/F12):** input `'1000010100.00000000'` → `result.bbl='1000010100'`, request URL uses the canonical form; the record's own `bbl` fact shows `original_value='1000010100.00000000'` → `normalized_value='1000010100'` (raw preserved verbatim). Verified on the actual objects.
   - **Missing/ambiguous (S3/S4):** malformed `'2000010100abc'` → `BBLValidationError` `non_numeric`, **zero transport calls**; F03b (`5999999999`) → explicit `no_match` result with explanation, `facts=[]`, `dataset_version=None`; borocode-conflict record (synthetic variant of F01, borocode="3") → one conflict dict with both values verbatim, `bbl` and `borocode` facts flagged `conflicting`, unrelated facts `none` — nothing silently resolved.
   - **Failure (S5):** F13 (400 + `query.soql.no-such-column`) → `SchemaDriftError`/`schema_drift`, single call, never retried; F13b (400 + `query.soql.type-mismatch`) → `SourceUnavailableError`/`source_unavailable` with the errorCode in detail — the two 400s are distinct, as required.
5. Edge probes beyond the suite (findings D1–D3 below): unparseable record-level `bbl`; `"NaN"`/`"Infinity"` strings in number columns; clock-call semantics (`retrieved_at` stamped once, pre-request); missing `version` → `SchemaDriftError`; `max_attempts=1` → immediate typed error, zero sleeps (retry bound holds at the degenerate boundary).
6. Fixture spot-checks (F01, F07, F13, F03, F03b): each embeds `request_url`, `retrieval_timestamp_utc`, `capture_method`, `http_status`, raw unmodified body. F07 is labeled `synthetic-from-official-doc` with `retrieval_timestamp_utc: null` and cites dev.socrata.com/docs/app-tokens; connector classifies 429 on status alone (body never asserted). Fixture pack sums to ~272.7 KB (F08 api/views snapshot is 228 KB of it) — KB-scale, no citywide data.
7. `pyproject.toml`: `jsonschema>=4.21,<5` added to the **dev extra only**; runtime dependencies unchanged (connector is stdlib-only, `urllib.request`).
8. Semantic cross-check against research §4: NumFloors p.28 rule quoted/applied verbatim (fires only when `numfloors` absent AND `numbldgs > 0` — F01 with numbldgs=0 correctly does NOT fire; F04 with numbldgs=10 does); condo ranges 1001–6999 / 7501–7599 match meta_mappluto; FIELD_UNITS match p.21/p.29/p.33-34/p.39-40 (EPSG:2263); FAR columns mapped as unitless informational facts, never rule outputs; `effective_date` explicitly null with per-input vintages carried verbatim (no guessed field→vintage mapping).

## Expected versus actual

| Scenario | Expected (packet) | Actual (reviewer-observed) | Verdict |
|---|---|---|---|
| S1 | 1 canonical record; facts validate v1; full provenance | ok/67 facts; jsonschema validation ran (not skipped); provenance value-asserted | PASS |
| S2 | F12 normalize w/ raw preserved; component padding; condo unit → no_match + explanation | all verified hands-on; `bbl_from_components` bounds tested (1/1/1, 5/99999/9999, string + decimal-tail components) | PASS |
| S3 | no_match not error; omitted keys = absent, never fabricated; p.28 rule | verified; `absent_columns == PLUTO_COLUMNS - emitted` asserted; real F04 record exhibits the p.28 case natively | PASS (S3a deviation adjudicated below) |
| S4 | typed rejection, no network; conflict flagged not resolved | 18-case parametrized typed codes; `transport.calls == []`; both conflict values verbatim | PASS |
| S5 | bounded retry/backoff; drift ≠ other 400; typed failures, no partial facts, no token/stack | exact call counts (3) and backoff `[0.5, 1.0]` asserted; drift single-call; token asserted in header AND absent from payload+caplog+URL | PASS |
| S6 | identical canonical output; deterministic keys; no dupes | exact fact-list equality across runs; sorted stable ordering verified in code (`sorted(record_keys & PLUTO_COLUMNS)`); unique deterministic provenance ids | PASS |
| S7 | no fact without provenance; version regex; vintages when present | required-key set per fact; malformed/missing version → SchemaDriftError (probed); vintage capture proven present (labeled synthetic) and absent (real F01v) | PASS |
| S8 | health + contracts validator pass; no contract files modified | 87 passed; validator 0 failures; git stat clean of `packages/contracts/**` | PASS |

## Evidence paths

- Worktree: `.claude/worktrees/M1-T002` @ `9e22839`
- Implementation: `services/api/app/connectors/bbl.py`, `services/api/app/connectors/pluto_soda.py`
- Tests: `services/api/tests/connectors/test_bbl.py` (38), `test_pluto_soda.py` (47)
- Fixtures: `services/api/tests/fixtures/pluto/` (18 files, ~273 KB)
- Producer report: `project-control/reports/M1-T002-producer-report.md`
- Reviewer commands: this report §Steps (all one-liners reproducible from `services/api/` in the worktree)

## Human-style walkthrough findings

As the future property-profile API implementer, the surface is directly consumable: `PlutoFetchResult` cleanly separates `status` (`ok`/`no_match`) from typed exceptions; `no_match_explanation` gives user-presentable condo text; `conflicts`/`drift_signals`/`absent_columns`/`notes` map naturally onto the PRD §9 conflict/missing-fact model. Error taxonomy is complete and distinct (`validation_error`, `rate_limited`, `schema_drift`, `timeout`, `source_unavailable`, plus `no_match` correctly a result, not an error). Injectable transport/sleep/clock make the connector fully testable downstream.

**Test-quality audit (special duty):** the suite is genuinely strong, not tautological.
- Concrete captured values asserted (lotarea `"23121"`→`23121`, appdate date-truncation, splitzone boolean, residfar 0.75 unitless).
- Negative assertions present and strong: zero network calls on validation failure (`transport.calls == []`); token asserted present in the header AND absent from serialized payload + `caplog.text` at DEBUG + URL; unknown column yields a drift signal AND no fact; unrelated facts stay `conflict_status="none"`; retry bound asserted by exact call count and exact backoff sequence.
- The 108-column duplication risk (module constant vs F08 fixture) is neutralized by `test_f8_embedded_inventory_matches_api_views_snapshot` asserting full dict equality plus count==108 — transcription drift fails the build. Live drift remains the (recommended) scheduled monitor's job via `check_columns_for_drift`.
- Synthetic variants are clearly labeled in-test and only exercise connector logic (never presented as official data).
- One structurally weak test noted (F2 below); one silent-skip hazard (F6 below); `urllib_transport` untested (F5 below).

**S3a adjudication (independent of G1):** the producer's deviation is **APPROVED**. The packet's S3(a) input `9999999999` has borough digit 9, which violates the accepted canonical pattern `^[1-5][0-9]{5}[0-9]{4}$` (M0-T009 `common.schema.json`) and would contradict the packet's own S4 requirement to reject borough 6. Client-side rejection as `invalid_borough` with zero network calls is the only reading consistent with the accepted contract. The packet's intent (syntactically valid, nonexistent → explicit `no_match`) is proven with live fixture F03b (`5999999999` → `[]`), while F03 preserves the raw API's `[]` behavior for `9999999999` as documentation. The decision is encoded in a dedicated test. Recommend the orchestrator annotate S3a in the task packet at acceptance.

## Regression/security/provenance findings

- Regression: `test_health.py` passes inside the 87; contracts validator 0 failures; no contract schema touched.
- Security (G5 is separate, but nothing adverse observed): token env-only, header-only, absent from URLs/logs/payloads (asserted); error payloads carry no stack traces; fixtures contain only public data; no new runtime dependency.
- Provenance: the only fact-emission path constructs the full source_fact v1 record — no normalized value exists outside a provenance-bearing fact; failures raise before any fact is built (no partial facts, structurally guaranteed).
- Low-storage: 273 KB fixtures; nothing large written; producer disclosed a leftover OS-temp capture dir (`%TEMP%\pluto_cap`, ~0.5 MB, outside repo) for orchestrator/owner cleanup.
- Hygiene: `git show --stat 9e22839` — all 26 files inside allowed paths.

## Defects

None blocking. Numbered findings with severity, location, reproduction, fix sketch:

1. **D1 (Medium, carry-forward or quick patch)** — `services/api/app/connectors/pluto_soda.py:614`: a source record whose own `bbl` field fails normalization escapes `fetch_by_bbl` as `BBLValidationError` (`error_type=validation_error`), contradicting the documented taxonomy ("malformed BBL **input**; NO network call is made"). A downstream consumer following the contract would misclassify corrupted/drifted source data as caller error. Repro: replay F01 with `record["bbl"]="0000000000.00000000"` → `BBLValidationError invalid_borough` escapes. Fix: wrap `normalize_bbl(record["bbl"])` in `try/except BBLValidationError` → raise `SchemaDriftError` (record-level contract violation). Still fails safely today (typed, no facts, no fabrication), and no acceptance scenario covers this path — hence non-blocking.
2. **D2 (Low)** — `pluto_soda.py:447-462` (`_normalize_value`, number path): `float("NaN")`/`float("Infinity")` are accepted, emitting `nan`/`inf` normalized values with NO drift signal, despite the docstring's "unparseable values are surfaced as drift signals". `json.dumps` then produces non-RFC-8259 output (`NaN`) that strict downstream parsers reject. Repro: replay F01 with `record["lotarea"]="NaN"` → `normalized_value=nan`, `drift_signals=[]`. Fix: `if not math.isfinite(number): drift_signals.append(...); return raw`.
3. **D3 (Low)** — `pluto_soda.py:526`: `retrieved_at` is stamped BEFORE the request; with retries the timestamp can precede actual retrieval by up to ~31.5 s (defaults: 3×10 s timeouts + 1.5 s backoff). Verified: clock called exactly once, pre-request. Fix: stamp after the successful response (or record both request/response times). Provenance-semantics nit only.
4. **D4 (Trivial)** — `project-control/reports/M1-T002-producer-report.md` §5: "66 facts from F1" — the F1 record has **67** keys and 67 facts are emitted (reviewer-verified). No test asserts 66; documentation typo only.
5. **F5 (Low, test gap)** — `pluto_soda.py:259-277`: `urllib_transport`'s error translation (HTTPError body pass-through, `TimeoutError`→`TransportTimeout`, `URLError.reason` mapping) is entirely untested. Offline-testable by monkeypatching `urllib.request.urlopen`. Producer disclosed the missing live smoke honestly (report §7.1); the translation layer itself deserves unit tests before production traffic.
6. **F6 (Low, CI hazard)** — `test_pluto_soda.py:94`: `pytest.importorskip("jsonschema")` means the S1 contract-validation test silently SKIPS if the dev extra is missing; a misconfigured CI would go green without validating facts against source_fact v1. Confirmed NOT skipped in this run (87 passed, 0 skipped). Fix: make jsonschema unconditionally required in CI (fail loudly) or assert non-skip in the CI job.
7. **F7 (Info, downstream guidance)** — every fact carries hard-coded `confidence: 1.0`. Justified and disclosed (deterministic official retrieval, per the schema's own description) — not a hidden default — but the property-profile/conflict engine must not read `confidence=1.0` as a coverage/legal status; coverage labels remain a separate axis (PRD §12).

## Required rework

None required for G3. D1 and D2 are small, contained patches; the orchestrator may fold them into this task pre-merge or track them as defects against the property-profile API task. F5/F6 should be tracked as test-hardening items before the connector serves production traffic.

## Reviewer conclusion

**PASS.** All eight packet scenarios reproduce first-hand from the committed worktree; the suite (87 tests) is substantive with strong negative assertions and no over-mocking; dictionary semantics (p.28/p.38, condo billing, units, never-guess) are faithfully implemented and traceable to the accepted research; both M1-T001 carry-forward hazards (decimal BBL, drift signature) are correctly handled; hygiene, storage, and dependency constraints are met. The S3a deviation is approved as the only contract-consistent reading. Seven non-blocking findings recorded above; D1/D2 recommended as immediate small patches, the rest as tracked carry-forwards.

Carry-forwards for the property-profile API task (Priority 3): consume `PlutoFetchResult` taxonomy exactly (after D1 fix, `validation_error` = caller error only); treat `no_match` as a result; persist `conflicts`/`drift_signals`/`absent_columns`/`notes` into the PRD §9 model; do not map `confidence=1.0` to any coverage label; wire `check_columns_for_drift` into the scheduled drift monitor; `build_page_url` is for the M2 bulk task only (OQ-4/OQ-10 still open, nyc.gov-403-bound).
