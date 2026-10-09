# M2-T021 — G4 QA RE-REVIEW (coverage and executability) of the rework

**Reviewer:** independent G4 QA reviewer (did not write this code).
**Re-reviewed commit:** `eb6a15f8` on `candidate/D-024-mrl-option-b`. Prior review: `d4cdbe79` / producer commit `dc227c0a`.
**Artifacts:** `services/api/app/connectors/geoclient_address.py` (727 lines), `services/api/tests/connectors/test_geoclient_address.py` (959 lines, 49 functions / **98 collected cases**), the three fixtures at `eb6a15f8`, `docs/MVP_AGENDA.md` C4, the producer-report rework addendum.
**Discipline:** read-only on the repository (ADR-005). Static analysis only — no pytest; CI at `eb6a15f8` is the execution authority. Files were extracted with `git show` into the session scratchpad; nothing in the repo was written.

---

## VERDICT: **PASS**

**No blocking corrections.** All five BLOCKING findings from my first review are CLOSED by tests that would actually fail under the specific mutants I described, and two of them were real defects (the `+` vs `%20` URL encoding and the `$`-anchored regex admitting a trailing newline), now genuinely fixed rather than merely tested around. The four HIGH and four MEDIUM findings are closed; the LOW items are closed or reduced to disclosed residue. What remains is six LOW observations — three of them newly introduced by the rework — none of which blocks acceptance.

Test count grew 36 → 98. I independently expanded the parametrizations and confirm **exactly 98 collected cases**, matching the producer's claim.

---

## DISPOSITION OF THE 18 PRIOR FINDINGS

| # | Prior severity | Disposition | Evidence |
|---|---|---|---|
| F1 sub-call swap-proofing | BLOCKING | **CLOSED** | `test_s2_sub_call_sides_are_never_swapped` :296 |
| F2 `os.environ` never read | BLOCKING | **CLOSED** | `test_s6_key_is_read_from_the_real_environment_at_call_time` :734 |
| F3 zip request form | BLOCKING | **CLOSED** | `test_s1_zip_form_request` :252, `test_s1_borough_and_zip_together_sends_both` :272 |
| F4 vacuous leak harvest | BLOCKING | **CLOSED** | `test_s6_sentinel_never_leaks_from_any_path` :668 |
| F5 URL ≠ recorded capture URL | BLOCKING | **CLOSED (defect fixed)** | conn :635, `test_s1_constructed_url_equals_the_recorded_capture_url` :221 |
| F6 single-suggestion only | HIGH | **CLOSED** | conn `_extract_suggestions` :375-395; tests :422, :444 |
| F7 warning message unproven | HIGH | **CLOSED** + disclosure | `test_s2_warning_outcome_surfaces_the_warning_message` :336; MVP_AGENDA C4 |
| F8 3xx/404/400 unexercised | HIGH | **CLOSED** | `test_s5_unexpected_statuses_including_refused_redirects_fail_typed` :543; conn :640-641 |
| F9 `TransportFailure` unexercised | HIGH | **CLOSED** | `test_s5_network_failure_is_source_unavailable_with_sanitized_reason` :514 |
| F10 tautological non-selection assert | MEDIUM | **CLOSED** | :418 states the fixture fact explicitly before :419 |
| F11 invalid shape only on side 1 | MEDIUM | **CLOSED (defect fixed)** | conn `fullmatch` :360; `test_s8_invalid_shape_grc_fails_closed_on_either_side` :882 (2×6) |
| F12 type-drift coercion | MEDIUM | **CLOSED** | :858, :869, :841, plus type assertions at :158-162 |
| F13 unbounded malformed detail / 429 count | MEDIUM | **CLOSED** | conn `_malformed_shape_detail` :531-542; tests :607, :562 |
| F14 S4 reason code | LOW | **CLOSED** | `test_s4_...` :480 (:492-493) |
| F15 echo fields / provenance reasons | LOW | **PARTIALLY CLOSED** | echo fields :170-173 closed; `provenance["reason_code"]`/`["reason_code2"]` still unasserted (→ N6) |
| F16 no mechanical network guard | LOW | **CLOSED (exceeded)** | `_no_network` autouse fixture :70-79 |
| F17 hygiene | LOW | **MOSTLY CLOSED** | explicit `ids=` throughout; `RecordingTransport` :110-111; `re` hoisted :22/:67 |
| F18 no source-fact mapping | MEDIUM | **ACCEPTABLE CARRY-FORWARD** | MVP_AGENDA C4:237-243 (assessment below) |

### Detail on the five BLOCKING closures

**F1 — CLOSED.** `test_s2_sub_call_sides_are_never_swapped` (:296) builds an asymmetric CONSTRUCTED variant with distinct code, reason and message on each side (`"00"/""/side-1` vs `"EE"/"1"/side-2`) and asserts each triple lands on its own side of the outcome. A connector that swapped the sub-calls would put `"EE"` in `res.grc` and fail immediately — this is the mutant-killing test that was missing. `test_s1_grc_fields_match_both_documented_forms` (:177) adds `res.grc == geosupportReturnCode == returnCode1e` and `res.grc2 == geosupportReturnCode2 == returnCode1a` on all three recorded fixtures.
*Honest note:* the alias test alone is **not** swap-proof — all three fixtures remain symmetric (`00/00`, `EE/EE`, `42/42`), so alias equality holds either way. The asymmetric variant is what does the work; the alias test pins that the primary and alias forms agree on real captures. Together they close the finding. The connector additionally *discloses* (conn :32-37) that the alias fields are deliberately not consulted and that a hypothetical alias-only response fails closed as `unrecognized_status` — an acceptable ADDRESSED-BY-DISCLOSURE for the alias-reading half, since no fixture pins such a response.

**F2 — CLOSED.** `test_s6_key_is_read_from_the_real_environment_at_call_time` (:734) uses `monkeypatch.setenv(KEY_ENV_VAR, ...)` with `env=None`, calls twice with a rotated value, and asserts each call's `Ocp-Apim-Subscription-Key` header separately. This defeats both mutants I named: an import-time snapshot (second call would carry the stale key) and a wrong-variable lookup (neither call would carry a key). The connector was restructured at :611-616 so `key is not None` short-circuits cleanly and `env=None` genuinely reaches `os.environ`.

**F3 — CLOSED.** `test_s1_zip_form_request` (:252) asserts `zip=10025` present and `borough=` absent in the URL, `res.zip_in == "10025"`, `res.borough_in is None`, and the exact `provenance["request_params"]`. `test_s1_borough_and_zip_together_sends_both` (:272) covers the both-present path. Connector line :629-630 is now executed.

**F4 — CLOSED.** The harvest (:668) now carries every positive control I asked for: `else: pytest.fail(...)` on both the transport-failure loop (:705) and the pre-network loop (:720); `assert transports and all(t.calls for t in transports)` (:724); a per-call `headers[KEY_HEADER] == SENTINEL_KEY` assertion across all ten transports (:725-727); `assert caplog.records` (:728); and `caplog.text` — which includes logger names, levels and `exc_text` — harvested instead of bare `record.getMessage()` (:730). Coverage expanded from six paths to twelve (3 success + 401/403/429/500/timeout/network/malformed + KeyMissing + InvalidInput). The inert `caplog.set_level(..., logger="app.resilience.transport")` is removed, and the producer report's addendum explicitly corrects that original claim.

**F5 — CLOSED, and the underlying defect fixed.** The connector now uses `urlencode(params, quote_via=quote)` (conn :635) with a comment naming the reason, and `test_s1_constructed_url_equals_the_recorded_capture_url` (:221) asserts byte-identity against each fixture's own `request_url`. **I recomputed this independently** for all three fixtures at `eb6a15f8` using stdlib `urlencode(..., quote_via=quote)` — all three are byte-equal to the recorded capture URLs, including parameter order. The production risk I flagged (a live call sending `street=w+100+st`) is eliminated.

---

## NEW OBSERVATIONS FROM THE REWORK (all LOW, none blocking)

**N1 — `key=` type handling is inconsistent with the new input discipline.** `geoclient_address.py:612`: a non-string `key` (e.g. `key=123`) degrades through `isinstance(key, str)` to `resolved_key = None` and surfaces as `KeyMissingError`, while `house_number`/`street`/`borough`/`zip_code` all get a typed `InvalidInputError` naming `received_type` via `_validated_input` (:417-447). Neither behavior is tested. A caller passing a mistyped key gets "no key available" instead of "key must be a string".

**N2 — Suggestion-list truncation at the bound is silent.** `_extract_suggestions` (:386) walks slots 1..`_MAX_SUGGESTIONS` (32) and stops; a response carrying 33+ populated slots silently loses the remainder with no marker on the outcome. This is inconsistent with the rework's own new discipline in `_malformed_shape_detail` (:539-541), which sets `top_level_keys_truncated` and `top_level_key_count`. The boundary (32 vs 33 slots) has no test. Low practical risk — no documented EE response approaches 32 — but the honesty asymmetry is worth a `suggestions_truncated` flag in the consuming packet.

**N3 — The `retry_after_cap` stop-early branch is untested for this connector.** The rework newly wires in the shared `jittered_retry_after_delay` policy, whose documented behavior includes returning `None` (stop retrying, raise now) when `Retry-After` exceeds `retry_after_cap`. `test_s5_retry_after_is_honored_on_429` (:569) covers only the honored-within-cap path (`sleeps == [7.0]`). The over-cap branch is covered by the shared engine's own M1-T009 tests, not by this pack.

**N4 — Three of the four new length caps are untested.** `test_s5_oversized_input_fails_closed_before_network` (:651) exercises `MAX_STREET_CHARS` only; `MAX_HOUSE_NUMBER_CHARS` (32), `MAX_BOROUGH_CHARS` (32) and `MAX_ZIP_CHARS` (16) at conn :141-144 have no test.

**N5 — Two hardened sanitizer branches are never exercised.** `_safe_text`'s 300-character `repr` truncation (conn :179) is never reached — every test value's repr is short. `_malformed_shape_detail`'s non-dict branch (conn :536) is reached by the `"[]"` parametrization but its `body_shape` value is never asserted.

**N6 — `provenance["reason_code"]` / `["reason_code2"]` values are still unasserted.** `test_s8_provenance_is_complete_on_every_status` (:932) requires the other eight provenance keys plus both GRC keys, but not these two, and no test checks their values on any status (the reason codes *are* asserted on the outcome fields `grc_reason`/`grc2_reason` at :409-410 and :313-315). Residue of F15.

**N7 — `app/connectors/__init__.py:3-5` is now stale.** The package docstring still states that every connector maps to facts validating against `packages/contracts/schemas/v1/source_fact.schema.json`; this connector emits an `AddressResolution` instead. That file is inside this packet's `allowed_paths` (`services/api/app/connectors/**`) and was not amended. A one-line qualification there would keep the package contract honest. Related to F18.

---

## F18 DISPOSITION ASSESSMENT — is the carry-forward acceptable for THIS packet?

**Yes, acceptable.** Four reasons, and one caveat:

1. **Scope.** The packet objective states verbatim: "NO API endpoint and NO UI in this packet — follow-up packets consume the connector." The `outputs` list contains no source-fact mapping.
2. **The packet's actual provenance clause is fully met.** It enumerates source id, endpoint, request params without the key, retrieval timestamp, and both GRC codes. `test_s8_provenance_is_complete_on_every_status` (:932) now asserts all of those on **all six** statuses, plus `response_digest`, `digest_canonicalization`, `correlation_id`, and key-absence.
3. **The obligation is recorded where the consuming packet will meet it**, with a named duty rather than a vague note — `docs/MVP_AGENDA.md` C4:241-243: "the connector emits an `AddressResolution`, not `source_fact`-shaped facts — the endpoint packet that consumes it must map to the contract and prove consumability." The same entry also discloses the GRC 50/75 narrowing, the unsanitized reflected-input caution, and the two missing natural captures (GRC 01, multi-suggestion).
4. **Deferring is the more honest engineering call.** Mapping to `source_fact` now, with no consumer and no endpoint, would mean inventing a field-to-fact mapping ahead of the requirement — precisely the guessing this project's rules forbid.

*Caveat (N7):* the carry-forward is recorded in the agenda but the `app/connectors/__init__.py` package docstring still asserts the opposite. Worth a one-line amendment in the consuming packet if not here.

---

## REBUILT COVERAGE TABLE (98 collected cases)

| S | Implementing tests (line → cases) | Remaining unasserted elements |
|---|---|---|
| **S1** normal — 10 cases | `resolved_fields_are_loaded_from_the_fixture_never_literals` :143→1; `grc_fields_match_both_documented_forms` :177→3; `provenance_is_complete_and_key_free` :187→1; `transport_receives_header_only_auth_and_key_free_url` :210→1; `constructed_url_equals_the_recorded_capture_url` :221→1; `default_transport_is_resolved_at_call_time` :237→1; `zip_form_request` :252→1; `borough_and_zip_together_sends_both` :272→1 | None material. Coordinate and identifier **types** now asserted against the fixture's own types (:158-162); URL byte-equality to all three capture URLs; echo fields; deep-copy independence (:167-168). `provenance["reason_code"]`/`["reason_code2"]` values unasserted (N6). |
| **S2** both sub-calls — 17 | `second_sub_call_failure_is_never_a_clean_success` :284→1; `sub_call_sides_are_never_swapped` :296→1; `clean_success_requires_both_codes_00` :328→4; `warning_outcome_surfaces_the_warning_message` :336→1; `disagreement_matrix` :368→9; `not_found_from_one_sub_call_still_transports_partial_fields` :378→1 | Both codes AND both messages now asserted (:291-293, :310-315, :346-347). Mixed-code precedence covered 9 ways incl. `00-EE`, `EE-00`, `42-EE`, `00-11`, `11-00`, `11-01`, `00-42`, `42-00`. Residue: the GRC `01` **wire shape** is constructed-only (no natural capture) — disclosed in MVP_AGENDA C4; the asymmetric variant leaves `returnCode1e`/`1a` at `00/00`, an internally inconsistent body (harmless — aliases are deliberately unconsulted). |
| **S3** ambiguity — 8 | `recorded_ee_response_is_ambiguous_with_verbatim_suggestions` :394→1; `multi_suggestion_walk_with_gaps_and_codeless_slots` :422→1; `declared_count_is_ignored_suggestions_come_from_slots` :448→5; `constructed_grc_11_is_not_found_with_no_suggestions` :465→1 | Multi-slot walk, blank middle slot, name-without-code slot, and hostile declared counts (zero/negative/nonnumeric/huge/absent) all covered; `street_code` type and the declared count's verbatim presence in `raw_fields` asserted; non-selection now rests on an explicit fixture-fact statement (:418). Residue: the 32-slot bound truncates silently and is untested (N2); GRC `50`/`75` still classify as plain `rejected` — **disclosed** in the connector docstring, the registry record and MVP_AGENDA C4, pending a recorded fixture. |
| **S4** rejection — 1 | `recorded_rejection_is_typed_and_transports_partial_data` :480→1 | Complete: both codes, both messages, `grc_reason is None` justified by an explicit `"reasonCode" not in addr` fixture-fact assertion, partial `street_name_normalized` + `borough_name` transported, `bbl is None`. |
| **S5** transport/auth — 20 | `timeout_persists_through_bounded_retry_budget` :507→1; `network_failure_is_source_unavailable_with_sanitized_reason` :514→1; `auth_failure_is_typed_immediate_and_key_free` :531→2; `unexpected_statuses_including_refused_redirects_fail_typed` :544→3 (302/400/404); `persistent_500_is_source_unavailable_after_budget` :555→1; `persistent_429_is_rate_limited_with_bounded_attempts` :562→1; `retry_after_is_honored_on_429` :569→1; `request_budget_is_consumed_per_attempt_and_typed_on_exhaustion` :585→1; `malformed_200_bodies_fail_closed` :602→4; `malformed_detail_is_bounded_and_body_value_free` :607→1; `invalid_input_raises_before_any_network_call` :621→1; `non_string_input_is_typed_never_attribute_error` :640→2; `oversized_input_fails_closed_before_network` :651→1 | Bounded-attempt counts now asserted on timeout, network, auth, 429, 500, 3xx/4xx and budget paths. Malformed detail proven to carry key **names** only, capped at 20 with truncation marker and count, with body values absent from the payload. "No partial facts emitted" remains satisfied structurally (every failure raises) rather than by a dedicated assertion — the checkable half (payload content) is now proven. Residue: `retry_after_cap` over-cap stop-early branch (N3); three of four length caps (N4); `_safe_text` 300-char truncation and `body_shape` value (N5). |
| **S6** key hygiene — 5 | `sentinel_never_leaks_from_any_path` :668→1 (12 paths, full positive controls); `key_is_read_from_the_real_environment_at_call_time` :734→1; `injected_env_mapping_is_honored` :755→1; `missing_key_is_typed_and_attempts_no_network` :765→1; `explicit_empty_key_never_falls_back_to_environment` :775→1 | Complete for the packet clause. Real `os.environ` read + at-call-time rotation proven; harvest cannot pass vacuously; `key=" "` proven not to fall back to a populated env. Residue: non-string `key` type handling (N1). |
| **S7** offline/integrity — 7 | `fixture_digest_matches_stored_sha256` :792→3; `fixture_request_urls_are_key_free` :799→3; `key_check_precedes_any_transport_use` :805→1 | "No network I/O" is now **mechanical**, not merely unexercised: the `_no_network` autouse fixture (:70-79) blocks `socket.socket` and `socket.create_connection` for every test in the module. Fixture `request_url` key-absence newly asserted. Note: the module performs fixture **file** I/O at collection time (`_status_bodies()` is evaluated twice by the :928 decorator, for params and for ids) — harmless, but a missing fixture would surface as a collection error rather than a test failure. |
| **S8** transport honesty — 30 | `absent_fields_are_none_never_fabricated` :827→4; `empty_string_source_value_is_preserved_not_reinterpreted` :841→1; `type_drift_is_never_coerced` :858→3; `integer_coordinate_stays_int` :869→1; `invalid_shape_grc_fails_closed_on_either_side` :882→12; `identifiers_stay_verbatim_strings` :895→1; `every_status_is_reachable_and_the_status_set_is_closed` :916→1; `provenance_is_complete_on_every_status` :932→6; `retrieved_at_comes_from_the_injected_clock` :951→1 | Absence covered for four canonical field classes; empty-string-is-data pinned; the PLUTO-lesson type-drift cases (numeric bbl, string latitude, bool latitude) each assert the canonical field is `None` **and** that `raw_fields` preserves the drifted value; int coordinates stay `int`; invalid shape now parametrized over **both** sides including the `"00\n"` case the old `$`-anchored regex admitted; `RESOLUTION_STATUSES` proven exhaustive and closed; provenance asserted on all six statuses. Residue: N6. |

---

## EXECUTABILITY RE-CHECK (static)

- **Python 3.12 parse:** `ast.parse(..., feature_version=(3,12))` clean on both files (connector 727 lines, tests 959). No line exceeds the 100-character limit in either file.
- **Ruff:** run as CI runs it (`cwd=services/api`, repo config, via `--stdin-filename` so `src`/isort first-party resolution matches `ruff check .`) — **All checks passed** on both files. Local ruff 0.13.0 is byte-identical to the hash-pinned `requirements-tools.lock:379`. The `# noqa: S101` at conn :602 targets an unselected rule (`select = ["E","F","I","UP","B"]`), and `RUF100` is not selected either, so it is inert rather than an error.
- **Collected-case count:** statically expanded all 14 parametrizations across 49 test functions → **exactly 98**, matching the claim. Every parametrize carries an explicit `ids=` except :928, which derives ids from `_status_bodies()`; all ids are deterministic strings.
- **Collection determinism:** tooling lock contains only `pytest==9.0.3`, `pluggy`, `anyio` — no `pytest-randomly`, no `xdist`. No `filterwarnings = error`. Fixture path `parents[1]/"fixtures"/"geoclient"` unchanged and correct. `tests/__init__.py` and `tests/connectors/__init__.py` both present; no `conftest.py` anywhere under `services/api`.
- **New imports all verified to exist:** `MAX_STREET_CHARS` (conn :142), `RESOLUTION_STATUSES` (conn :280), `RequestBudgetExceededError` (conn :256), `CANONICALIZATION_SPEC` (`pluto_soda.py:229`, exported at :79), `AnalysisBudget(1, analysis_id=...)` with `.consumed` (`app/resilience/budget.py`), `jittered_retry_after_delay` (`transport.py:252`), `TransportFailure` (`transport.py:100`).
- **Retry-After arithmetic traced end to end:** header `{"retry-after": "7"}` → `get_retry_after` (lowercase match) → `sanitize_retry_after("7")` passes the RFC-9110 allowlist verbatim → `last_detail["retry_after"]="7"` → `parse_retry_after("7", wall_now=clock)` → `7.0` → `7.0 ≤ retry_after_cap 120` → `sleep(7.0)`. `sleeps == [7.0]` holds, and the second queued outcome (200) ends the loop.
- **Budget arithmetic traced:** `AnalysisBudget(1)`; attempt 1 consumes the unit then gets 500; attempt 2's `try_consume()` returns `False` → `raise_budget_exceeded` → `RequestBudgetExceededError` with `detail["analysis_id"]`. `len(calls)==1` and `consumed==1` both hold.
- **No real sleep anywhere:** `_resolve` injects `_no_sleep` by default; the Retry-After test injects `sleeps.append`. No wall-clock dependence beyond an RFC-3339 shape regex, and `test_s8_retrieved_at_comes_from_the_injected_clock` (:951) pins the value through the new `clock` seam.
- **Socket guard is safe:** `_no_network` is function-scoped, autouse, and monkeypatch-restored; nothing in the suite (caplog, json, pathlib, hashlib) needs a socket, and it blocks both `socket.socket` and `socket.create_connection`, the two entry points `urllib`/`http.client` use.
- **Fixtures at `eb6a15f8`:** recomputed `sha256(response_body_raw)` for all three — all match `response_sha256`. The fixture edits added `retrieval_timestamp_basis` and revised `retrieval_timestamp_utc`; **response bodies are unchanged**, so the S7 digest tests still pass. I also recomputed the three capture URLs against `urlencode(..., quote_via=quote)` — all byte-equal.
- **Modularity:** connector 574 SLOC (was 443) — below the 600 warn threshold, so not even a warning. Test files are excluded from selection (`tools/modularity_check.py:82-103`, `_is_test_file`), so the 761-SLOC test module is not measured. The baseline (`M0-T073-initial-baseline`) contains **no** entry for `geoclient_address.py`, so the material-growth rule (which the +131-line growth would otherwise have tripped at a 493 limit) does not apply; the new-file rule is `HARD_SLOC` 1000. Clean — and note `tools/**` is a forbidden path for this packet, so a baseline entry would have been a real problem.
- **Secret scan:** imported `.github/scripts/secret_scan.py` and ran its own `scan_line` over every line of both reworked files → **0 findings**. Neither the sentinel nor the `"SECRET-VALUE"` literal in the hostile-body test (:611) matches any pattern, so no `secretscan:allow` pragma is needed.

## REGRESSION RE-CHECK

`eb6a15f8` touches 10 files; the only two under `services/api` are the connector and its own test module. No sibling connector, no shared transport, no conftest, no schema, no CI config. The connector **deleted** its own `urllib_transport` wrapper and module-level `_OPENER` and now imports the shared `app.resilience.transport.urllib_transport` (conn :102, :640-641), which removes rather than adds cross-module coupling — `pluto_soda._OPENER`'s accepted monkeypatch seam is untouched. The new imports (`AnalysisBudget`, `jittered_retry_after_delay`, `CANONICALIZATION_SPEC`) are pure reads of existing public API with no mutation of shared state. **Regression surface for the 339 existing connector tests: none.** The producer's claim of 437 passing (98 + 339, zero regressions) is consistent with everything I can verify statically; CI at `eb6a15f8` remains the authority.

## RECOMMENDED (NON-BLOCKING) FOLLOW-UPS

1. N1 — give `key=` the same typed `InvalidInputError` treatment as the other inputs, or document the degradation.
2. N2 — add a `suggestions_truncated` marker at the 32-slot bound, mirroring `top_level_keys_truncated`, and test the boundary.
3. N7 — amend `app/connectors/__init__.py:3-5` so the package docstring matches this connector's actual contract.
4. N3/N4/N5/N6 — small coverage top-ups: the over-cap `Retry-After` stop-early branch, the three untested length caps, `_safe_text`'s repr truncation, `body_shape`, and the two provenance reason-code values.
