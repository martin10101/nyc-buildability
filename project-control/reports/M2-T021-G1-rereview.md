# M2-T021 — G1 independent code RE-REVIEW (rework at `eb6a15f8`)

**Reviewer:** code-reviewer (independent; did not write this code; same reviewer as the first-round G1 at `d4cdbe79`)
**Task:** M2-T021 — Geoclient v2 address-resolution connector
**Rework commit reviewed:** `eb6a15f8` (10 files, +1022 / −253), authored `2026-09-11T16:10:52-04:00`
**Preceding record commit:** `430773eb` (gate wave: G1 FAIL, G3 PASS, G4 FAIL, G5 PASS; task → rework)
**Branch:** candidate/D-024-mrl-option-b
**Date:** 2026-09-11
**Discipline:** read-only per ADR-005. No file edited, no test suite run, no ledger write. Every Python probe ran with `PYTHONDONTWRITEBYTECODE=1`; `git status --porcelain` is unchanged from before this review.

---

## VERDICT

**PASS with required corrections** (recorded as PASS per the gate-verdict semantics in `.claude/rules/project-control.md`; the three corrections in the NEW DEFECTS section are BLOCKING for the next gate and for acceptance).

All three first-round BLOCKING findings are genuinely closed, and I verified the hardest one — the fixture provenance — independently against artifacts outside the repository rather than taking the correction on trust. Eleven of the remaining findings are closed in code with non-vacuous tests; one is properly addressed by disclosure. The rework is a real repair, not a narrative.

Three new items keep it short of a clean pass: one newly added test assertion is vacuous and does not guard the fix it claims to guard, one silent schema-drift behavior is now codified by test without being disclosed anywhere a consumer would look, and the commit edits three paths the packet's `allowed_paths` does not cover.

---

## DISPOSITION OF THE 14 FIRST-ROUND FINDINGS

### 1. BLOCKING — fixture retrieval timestamps post-dating their own commit → **CLOSED (independently verified)**

The correction is real and I did not have to take it on faith. The orchestrator stated the true times come from the raw capture files' filesystem write times; those files exist in the session scratchpad, so I checked them directly:

| fixture | raw capture file | file mtime (UTC) | fixture `retrieval_timestamp_utc` | match |
|---|---|---|---|---|
| G01 | `geoclient_response.json` | 2026-09-11T18:46:43Z | 2026-09-11T18:46:43Z | yes |
| G02 | `geoclient_amb.json` | 2026-09-11T19:33:39Z | 2026-09-11T19:33:39Z | yes |
| G03 | `geoclient_rej.json` | 2026-09-11T19:33:39Z | 2026-09-11T19:33:39Z | yes |

Every corrected value equals its raw file's write time to the second. More important, the raw files are provably the *source* of the committed bodies, not an after-the-fact reconstruction: `sha256(raw file text)` equals `sha256(fixture["response_body_raw"])` equals the fixture's stored `response_sha256` for all three (`e7bffd4b…`, `6e7c6e35…`, `675d9bd9…`). No key material appears in any raw capture.

The ordering contradiction is gone: G01 at 18:46:43Z precedes its commit `ccf64f75` (18:48:07Z) by 1m24s; G02/G03 at 19:33:39Z precede their commit `dc227c0a` (19:41:40Z) by 8m01s and fall 1m10s after the task-claim commit `f8c118f9` (19:32:29Z) — exactly where a producer's first action belongs. The shared second for G02/G03 is now explained ("issued by one loop") and the raw files corroborate it with an identical mtime.

Each fixture also carries a new `retrieval_timestamp_basis` field naming the basis *and* disclosing the original error by name, which is the honest form of the correction rather than a silent overwrite. `project-control/blockers/B-004-geoclient-subscription-key.json` moves to `resolved` with `resolved_at: 2026-09-11T18:46:43Z` and states its basis ("resolved_at is the G01 capture's own timestamp"), matching the G01 capture I verified; it also records honestly that official rate limits remain unconfirmed.

### 2. BLOCKING — `AttributeError` escaping the typed taxonomy on non-string input → **CLOSED**

`geoclient_address.py:417-447` adds `_validated_input`, applied to all four caller inputs at `:586-604`. Verified by direct call:

```
resolve_address(314, 'w 100 st', …)        -> InvalidInputError {'param':'house_number','received_type':'int'}
resolve_address('314', ['w'], …)           -> InvalidInputError {'param':'street','received_type':'list'}
resolve_address('x'*33, …)                 -> InvalidInputError {'param':'house_number','length':33,'max_chars':32}
resolve_address(…, borough='m'*33)         -> InvalidInputError {'param':'borough','length':33,'max_chars':32}
```

No value content is echoed into the error, only the type name and the length. `test_s5_non_string_input_is_typed_never_attribute_error` and `test_s5_oversized_input_fails_closed_before_network` guard both halves, and both assert `transport.calls == []`. See new finding N4 for the one input this does not cover.

### 3. BLOCKING — the `os.environ` branch never executed → **CLOSED**

`test_s6_key_is_read_from_the_real_environment_at_call_time` (test file `:734-753`) uses `monkeypatch.setenv(KEY_ENV_VAR, …)` and leaves `env` at its default, so the production `os.environ` path at `:614` actually runs. It goes further than I asked: it rotates the variable between two calls and asserts the second call's header carries the rotated value, which proves the read is at call time rather than captured at import. `test_s6_injected_env_mapping_is_honored` keeps the injected-mapping case separately, so the two are no longer conflated.

### 4. HIGH — `_extract_suggestions` trusting the declared count downward → **CLOSED**

`:375-395` drops the count entirely and walks every slot to `_MAX_SUGGESTIONS`. Verified: with `streetName1/3/4` populated and `streetName2` empty, the declared values `"00"`, `"-3"`, `"abc"`, `"999999"` and absent all return the same three suggestions; slot 32 is surfaced and slot 33 is not. The docstring now says the count is untrusted "in BOTH directions" and notes it stays verbatim in `raw_fields` — accurate to the code. `test_s3_declared_count_is_ignored_suggestions_come_from_slots` (5 cases) and `test_s3_multi_suggestion_walk_with_gaps_and_codeless_slots` are real tests: under the old code the `"00"` and `"-3"` cases returned `[]`.

### 5. HIGH — legacy no-jitter retry policy ignoring `Retry-After` → **CLOSED**

`:519-525` now uses `jittered_retry_after_delay` with `backoff_base`, `backoff_cap` (30.0), `retry_after_cap` (120.0), an injected `rng` and `wall_clock` — the same M1-T009 policy as the three M2-wave siblings. `test_s5_retry_after_is_honored_on_429` asserts the inter-attempt sleep is exactly `[7.0]` for a `retry-after: 7` header, which is the header value and not the exponential fallback; I confirmed `parse_retry_after("7")` returns `7.0` at `app/resilience/retry.py:55-56`. The `rng or Random()` default matches the sibling idiom (`ztldb_soda.py:791`, `zoning_features_arcgis.py:984`).

### 6. MEDIUM — no injectable clock → **CLOSED**

`clock: Callable[[], datetime] = _utc_now` at `:564`, stamped after the successful parse at `:678` with a comment explaining why. The same clock is threaded to the retry policy as `wall_clock`, matching `ztldb_soda.py:1189`. `test_s8_retrieved_at_comes_from_the_injected_clock` pins the actual value (`2026-09-11T12:34:56Z`), not just the shape.

### 7. MEDIUM — untested disagreement precedence and the populated-fields-on-non-resolved hazard → **CLOSED**

`test_s2_disagreement_matrix` covers nine mixed pairs; I ran `_classify` against the same inputs and every result matches the table (`00/EE`→ambiguous, `42/EE`→ambiguous, `00/11`→not_found, `11/01`→not_found, `00/42`→rejected, `77/77`→rejected). `test_s2_not_found_from_one_sub_call_still_transports_partial_fields` now asserts the exact hazard I raised — a `not_found` outcome carrying a populated `bbl` — and the `AddressResolution` docstring (`:300-306`) states it as a deliberate contract with "consumers must branch on `status`, never on field presence."

### 8. MEDIUM — `RESOLUTION_STATUSES` dead code → **CLOSED**

Now exported in `__all__` (`:112`) and imported by the tests. `test_s8_every_status_is_reachable_and_the_status_set_is_closed` produces all six statuses from six bodies and asserts `seen == set(RESOLUTION_STATUSES)`, and `test_s2_disagreement_matrix` additionally asserts every result is a member. The tuple is now pinned to the implementation in both directions. Residual: `status` is still annotated bare `str` (see N7).

### 9. MEDIUM — no `AnalysisBudget` threading → **CLOSED**

`budget: AnalysisBudget | None = None` at `:566`, passed through `_request` to `request_with_retry`, with `budget_error=RequestBudgetExceededError` wired into `standard_retry_hooks`. `test_s5_request_budget_is_consumed_per_attempt_and_typed_on_exhaustion` asserts one unit consumed, one transport call, and `detail["analysis_id"]`. I confirmed `AnalysisBudget(1, analysis_id=…)` matches the real signature at `app/resilience/budget.py:28`.

### 10. MEDIUM — documented GRC aliases never read → **ADDRESSED-BY-DISCLOSURE**

The module docstring (`:32-37`) now states the aliases are *deliberately* not consulted, gives the reason (every recorded response carries both forms identically; the primary names are canonical; an alias-only response fails closed rather than being half-guessed). Better than the disclosure I asked for: `test_s1_grc_fields_match_both_documented_forms` asserts `res.grc == geosupportReturnCode == returnCode1e` and `res.grc2 == geosupportReturnCode2 == returnCode1a` on all three recorded fixtures, so the assumption that the two forms agree is now evidence-backed and swap-proof rather than assumed.

### 11. MEDIUM — untested transport paths (network failure, 3xx, 404/400) → **CLOSED**

`test_s5_unexpected_statuses_including_refused_redirects_fail_typed` covers 302/400/404, asserting `SourceUnavailableError`, one call (never retried), the status in `detail`, and explicitly `not isinstance(…, AuthFailedError)`. `test_s5_network_failure_is_source_unavailable_with_sanitized_reason` drives `TransportFailure` through `sanitize_network_reason=_safe_text` and asserts `reason_kind == "network"` plus no `detail` value containing a literal newline — a real assertion of the G5 C1 property, not a restatement.

### 12. LOW — `$` instead of `\Z` in the two sanitizer regexes → **CLOSED**

Both regexes now use `fullmatch` (`:177` and `:360`). Verified: `_classify("00", "00\n")` returns `unrecognized_status` (it returned `rejected` before), `_safe_text("ok\n")` returns the repr form, a 301-character safe string falls to the capped repr, and a 5000-character repr is truncated to 300. `test_s8_invalid_shape_grc_fails_closed_on_either_side` covers 12 cases including the trailing-newline one on both sub-call sides. The pattern-wide sibling defect I noted (`mappluto_geometry_arcgis.py:314`, `zoning_features_arcgis.py:266`, `ztldb_soda.py:345`) is recorded as a follow-up packet in `docs/MVP_AGENDA.md` §C4 rather than silently left — the right disposition for out-of-scope wave damage.

### 13. LOW — `_OPENER` / local `urllib_transport` no-op indirection → **CLOSED**

Both removed; the module imports `urllib_transport` directly from `app.resilience.transport` like the three siblings. The default is resolved at call time (`:640-641`) with a comment explaining that the seam must stay monkeypatchable, and `test_s1_default_transport_is_resolved_at_call_time` exercises it.

### 14. LOW — assorted → **ALL CLOSED**

`body_bytes` → `body_chars` (`:665`). `latitude`/`longitude` annotated `float | int | None` (`:323-324`), with `test_s8_integer_coordinate_stays_int` proving no float coercion. `_string_or_none` now preserves an empty-string source value verbatim (`:398-403`), documented as "data, not absence" in the module docstring and the registry record, with `test_s8_empty_string_source_value_is_preserved_not_reinterpreted`. `import re` moved to the module top. The inert `caplog.set_level` on `app.resilience.transport` is removed and the producer report names it as an error it made. The weak `res.bbl is None` assertion is now labeled a fixture fact and sits beside real assertions. The bool-coordinate rejection is tested (`test_s8_type_drift_is_never_coerced[bool-latitude]`). The `key=""` precedence is tested (`test_s6_explicit_empty_key_never_falls_back_to_environment`).

---

## NEW DEFECTS INTRODUCED OR LEFT BY THE REWORK

### N1. BLOCKING (required correction) — `test_geoclient_address.py:160-163`: the deep-copy assertion cannot fail, so the `raw_fields` deep copy it claims to guard is untested.

```python
assert res.raw_fields == addr
res.raw_fields["bbl"] = "MUTATED"
assert _fixture_address(G01)["bbl"] == addr["bbl"]
```

`_fixture_address(G01)` re-reads and re-parses the fixture **from disk**, and `addr` came from an earlier independent disk read. The connector never writes that file, so this assertion compares two fresh parses of an untouched file and holds identically whether or not `copy.deepcopy` is present at `:704`. I confirmed it passes while `res.raw_fields` is mutated, and the comment above it ("as an independent copy: caller mutation cannot reach the connector's parsed state (G3 finding 10)") claims a property the code below it does not test.

The fix itself is correct — I verified independently that mutating `res.raw_fields` leaves `provenance["response_digest"]` unchanged — but nothing in the suite would catch a future regression that dropped the `deepcopy`. This is the exact anti-tautology failure mode the packet's S1 rule exists for, reintroduced in the rework. **Correction:** assert the property that actually depends on the copy — e.g. that `res.provenance["response_digest"]` still equals `canonical_json_digest(json.loads(body))` after mutating `res.raw_fields`, or that a second call on the same transport returns unmutated `raw_fields`.

### N2. BLOCKING (required correction) — `geoclient_address.py:398-414`: identifier type drift is swallowed silently, producing a clean `resolved` with a `None` BBL and no signal anywhere.

`_string_or_none` maps a non-string to `None` and `_number_or_none` maps a non-number to `None`. Verified end to end with a constructed numeric `bbl`:

```
status = resolved   bbl = None   raw_fields['bbl'] = 1018887502
provenance keys carrying any drift signal: NONE
```

A consumer sees a successful resolution whose BBL is missing, indistinguishable from Geoclient having omitted the field under the null-omission rule — for the one connector whose entire purpose is to produce a BBL. The value survives in `raw_fields`, so nothing is lost, but nothing surfaces it either: no `drift_signals`, no provenance flag, no log line. The three accepted sibling connectors all carry explicit drift signalling (`ztldb_soda.py:451`, `zoning_features_arcgis.py:356`), and `.claude/rules/backend-api.md` requires connectors to "handle pagination, rate limits, nulls, and schema drift explicitly."

The rework made this a *deliberate* behavior by codifying it in `test_s8_type_drift_is_never_coerced`, whose docstring calls it a "documented fail-safe" — but it is documented only in that test. It is absent from the `AddressResolution` docstring, the module docstring, and the registry record, all three of which do document the neighbouring null-omission and empty-string rules. **Correction:** either surface a drift signal (a provenance key or a `logger.warning`) when a canonical field is present but of the wrong type, or document the swallow in the result contract and the registry record alongside the other two honesty rules. Do not leave it discoverable only by reading a test.

### N3. BLOCKING (required correction, record-side) — `eb6a15f8` edits three paths outside the packet's `allowed_paths`, which was not amended.

The packet at `project-control/tasks/M2-T021.json:21-30` still lists exactly eight entries, and `430773eb` changed only `status`, `progress_percent`, `updated_at` and `progress_log` — not `allowed_paths`. The rework commit touches:

- `docs/MVP_AGENDA.md` (+33/−6)
- `project-control/blockers/B-004-geoclient-subscription-key.json` (+4/−2)
- `project-control/reports/M2-T021-evidence-map.json` (+15/−?) — only `M2-T021-producer-report.md` is allowed under `project-control/reports/`

None is under `forbidden_paths`, the orchestrator pre-announced all three in the `430773eb` progress_log, and ADR-005 gives the orchestrator authority over ledger and blocker records — so I am not calling the edits themselves improper. The defect is that the packet's declared scope and the commit disagree, and a scope declaration that the producing commit silently exceeds is worth exactly as much as a provenance field that misstates its basis. **Correction:** amend `allowed_paths` (or record the widening in the packet) so the contract matches what was committed. The ruling on whether an orchestrator ledger edit needs a packet amendment is the orchestrator's, not mine; the mismatch itself is the finding.

### N4. LOW — `geoclient_address.py:611-612`: `key=` is the one caller input the new typed validation does not cover.

`if key is not None: resolved_key = key.strip() if isinstance(key, str) else None`. A non-string key (e.g. `key=12345`) therefore becomes `None` and raises `KeyMissingError` — "no key available" — rather than the `InvalidInputError` every other mistyped parameter now raises. Verified. Fail-closed and no leak, but it contradicts the discipline finding 2's fix established, and it is untested.

### N5. LOW — `geoclient_address.py:531-542`: `_malformed_shape_detail` sanitizes and sorts every key before capping at 20.

`keys = sorted(map(_safe_text, parsed.keys()))` runs over the whole key set; only the slice afterwards is bounded. The docstring says "never an amplification surface," which overstates it: a hostile 10 MB body (the transport's `MAX_RESPONSE_BYTES`) of minimal keys forces a repr-and-sort pass over on the order of a million strings. Bounded overall by the body cap and roughly a constant factor on top of the `json.loads` that already happened, so the impact is modest — but the cap belongs before the `map`/`sorted`, and the docstring should match.

### N6. LOW — `MAX_HOUSE_NUMBER_CHARS` / `MAX_STREET_CHARS` / `MAX_BOROUGH_CHARS` / `MAX_ZIP_CHARS` are absent from `__all__` while the test module imports `MAX_STREET_CHARS`.

The import works, but the module's declared public surface and its actual consumed surface disagree. Either export the caps or have the test derive the bound another way.

### N7. LOW — `AddressResolution.status` is still annotated bare `str` (`:309`) now that `RESOLUTION_STATUSES` is exported.

The natural completion of finding 8 is `Literal["resolved", …]` or an enum, so a consumer's type checker can see the closed set the runtime test now pins.

---

## WHAT I VERIFIED

**Read in full:** `services/api/app/connectors/geoclient_address.py` (all 727 lines), `services/api/tests/connectors/test_geoclient_address.py` (all 959 lines), all three fixtures' diffs and current contents, the `eb6a15f8` diffs for `docs/research/source-registry-drafts/geoclient.json`, `docs/MVP_AGENDA.md`, `project-control/blockers/B-004-geoclient-subscription-key.json`, `project-control/reports/M2-T021-producer-report.md` (rework addendum), the rewritten `project-control/reports/M2-T021-evidence-map.json`, and the `430773eb` diff of `project-control/tasks/M2-T021.json`.

**Re-read for comparison:** `app/resilience/transport.py` (retry engine, hooks contract, `NoRedirectHandler`), `app/resilience/budget.py`, `app/resilience/retry.py` (`parse_retry_after`), `tools/modularity_check.py` (thresholds and the `source_lines` SLOC definition), and the `rng` / `clock` / `drift_signals` idioms in `ztldb_soda.py` and `zoning_features_arcgis.py`.

**Commands run — all read-only**, `PYTHONDONTWRITEBYTECODE=1` on every Python invocation, and `git status --porcelain` unchanged before and after:

- `git log`, `git show --stat eb6a15f8 / 430773eb`, `git show` per path, `git log -1 --format='%aI %cI'` on the relevant commits
- filesystem `stat` + sha256 of the three raw capture files in the session scratchpad, compared against the fixtures' `retrieval_timestamp_utc`, `response_body_raw` and `response_sha256`
- direct calls into `_classify` (12 pairs), `_extract_suggestions` (5 declared counts + slot-32/33 bound), `_safe_text` (newline, 301-char, 5000-char repr), `_validated_input` via `resolve_address` (5 rejection cases)
- full `resolve_address` runs against all three fixtures asserting the emitted URL is byte-identical to each fixture's recorded `request_url`, the key is header-only, `raw_fields` mutation leaves the digest stable, and a special-character street encodes safely (`a&b=c?d#e/f` → `a%26b%3Dc%3Fd%23e%2Ff`, no query injection)
- an AST-based count of the test module's collected cases
- a direct demonstration that the N1 assertion holds while `raw_fields` is mutated

**Not run, deliberately:** pytest (ADR-005 and the standing precedent — CI is the authority), `ruff`, and `tools/modularity_check.py`; the latter two would write cache or output artifacts into the tree.

---

## CLAIMS CHECKED

### Verified true

- **"98 collected (was 36)"** — my AST count of the test module, expanding every `parametrize` including the dynamic `_status_bodies()` one, gives exactly 98.
- **"URL percent-encoding aligned to the recorded capture URLs, asserted byte-identical per fixture"** — I ran all three and each emitted URL equals the fixture's `request_url` exactly.
- **"fixture retrieval timestamps corrected to the raw capture files' write times with the basis stated and the original hand-estimate error disclosed inside each fixture"** — verified against the actual files, to the second, with body-hash provenance linking raw file to committed fixture.
- **"suggestion extraction untrusting of the declared count in both directions"** — verified across five declared values.
- **"shared jittered Retry-After-honoring retry policy and optional AnalysisBudget threading like every M2-wave sibling"** — verified in code and against the sibling implementations.
- **"injectable clock stamped after parse"**, **"RESOLUTION_STATUSES exported and pinned"**, **"call-time transport resolution, indirection removed"**, **"deep-copied raw_fields"** (the code, not its test — see N1), **"digest_canonicalization carried beside the digest"** (`CANONICALIZATION_SPEC` confirmed to exist at `pluto_soda.py:229` and to be exported) — all verified in the tree.
- **"modularity clean"** — the connector is 574 SLOC by the tool's own non-blank/non-comment definition (raw 727), under `WARN_SLOC` 600, with 21 top-level symbols against a ceiling of 40, and as a new file it is nowhere near the `HARD_SLOC` 1000 that would fail CI.
- **"secret-scan PASS"** — I found no key material in the fixtures or in the three raw capture files; the only long hex runs are the `response_sha256` values.
- **The producer report's rework addendum** genuinely corrects its own four overstated claims, including the two I flagged ("~500 lines" and "every failure path"), and preserves the original text rather than rewriting history.

### Unverified by me

- **"437 connectors tests pass (98 new + 339 existing, zero regressions)"** and **"ruff clean"** — these require running the tooling, which read-only discipline forbids. The arithmetic is at least self-consistent with the first round's "375 = 36 + 339." CI remains the authority.
- The **live-capture claim** itself. I verified that the raw capture files exist, that their write times match the committed timestamps, and that their contents hash to the committed bodies — which establishes the timestamps' stated basis and rules out the first-round contradiction. It does not, by itself, prove the bodies came from a live GET rather than another source; nothing in the tree can prove that, and the fixtures now state their basis plainly, which is the appropriate standard.
