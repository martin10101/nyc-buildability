# M2-T021 — G5 independent security RE-REVIEW (rework at eb6a15f8)

**Task:** M2-T021, Geoclient v2 address-resolution connector — re-review after rework.
**Reviewer:** independent G5 security reviewer (did not write this code; same reviewer as the d4cdbe79 G5 PASS).
**Reviewed identity:** `eb6a15f8` on `candidate/D-024-mrl-option-b` ("M2-T021 rework: every blocking finding from the four-gate wave, one bounded change").
**Prior G5:** PASS with blocking corrections C1–C4 at `d4cdbe79`.
**Discipline:** ADR-005 read-only. No file in the repository was edited, no test suite was run, no ledger was written, no network request was made. Read-only `git`/`grep` plus read-only offline `python -c` probes (including calling `resolve_address` with an injected in-memory transport, which performs no I/O).

---

## VERDICT: **PASS** — with one blocking correction (N1) and two scope corrections (N2, N3)

All four prior blocking corrections (C1–C4) are **genuinely closed**, verified by execution rather than by reading, and each is now pinned by a test that fails if the fix regresses. All four prior dispositions (findings 5, 6, 7, 8) are closed. The key-containment promise still holds on every surface, including the four surfaces the rework newly created.

The rework did, however, introduce one regression of its own: the new `copy.deepcopy` of the response body (the G3-10 fix) raises an **uncaught `RecursionError`** on a hostile 200 body, breaking the typed-taxonomy and fail-closed guarantees the packet states in S4/S5. I proved it end-to-end through the public API. It must be fixed before acceptance.

**Calibration note for the orchestrator.** I am recording PASS rather than FAIL for consistency with my own prior round: N1 is a MEDIUM of the same family as the four MEDIUMs I passed on at `d4cdbe79`, it cannot leak the key, and it is reachable only by an upstream that is already compromised or MITM'd. An orchestrator that weights *regressions introduced by a corrective rework* more heavily than first-pass findings could reasonably record FAIL instead; I flag the judgment explicitly rather than burying it. Either way N1 is blocking for acceptance.

---

## PRIOR BLOCKING CORRECTIONS — CLOSURE VERIFICATION

| ID | Correction | Status | How I verified |
|---|---|---|---|
| **C1** | `fullmatch` so a trailing newline cannot split a log record | **CLOSED** | `_SAFE_TEXT_RE` (`geoclient_address.py:169`) lost its `^…$` anchors and is now used via `.fullmatch()` (`:177`); `_GRC_SHAPE_RE` (`:155`) likewise via `.fullmatch()` in `_classify` (`:360`). Executed: `_safe_text("00 status=resolved bbl=1234567890\n")` now returns the `repr()` form, **no newline survives into the output**; `_GRC_SHAPE_RE.fullmatch("00\n")` is `False` and `_classify("00\n","00")` returns `unrecognized_status`. Test-pinned at `test_geoclient_address.py:879-893` — `"00\n"` is a named parametrize case (`trailing-newline`) run against **both** sub-call sides. |
| **C2** | Length-capped `repr()` fallback | **CLOSED** | `return repr(value)[:_SAFE_TEXT_MAX_CHARS]` (`:179`, cap 300 at `:168`). Executed: a 9 MB safe-charset string and a 1 M-newline string both return exactly 300 chars. |
| **C3** | Capped `top_level_keys` with a truncation marker | **CLOSED** | New `_malformed_shape_detail` (`:531-542`) caps at `_MAX_REPORTED_KEYS = 20` (`:173`), adds `top_level_keys_truncated` and `top_level_key_count`, and each key passes through the now-capped `_safe_text`. Executed against a constructed 61-key hostile body with 500-char key names and a nested body value: 20 keys reported, marker `True`, count `61`, max key length 300, **total payload 6 KB**, and the planted body value is absent. The non-dict branch returns `{"url", "body_shape"}` from `type().__name__` only. Test-pinned at `:607-620` (60 hostile keys, asserts `"SECRET-VALUE" not in json.dumps(to_payload())`). |
| **C4** | Typed input length caps, value never echoed | **CLOSED** | New `_validated_input` (`:417-447`) type-, presence- and length-checks all four inputs (`:586-601`) **before** key resolution (`:611`), URL construction (`:635`) and any transport call (`:643`). Caps at `:141-144` (house 32 / street 120 / borough 32 / zip 16). Executed end-to-end with 5000-char values for each of the four params: every one raises `InvalidInputError`, **the value appears in neither the message nor the payload**, and each payload is ~300 chars. A non-string `house_number=314` raises `InvalidInputError: house_number must be a string, got int` — detail carries `received_type` only, never the value. Test-pinned at `:634-662`. |

## PRIOR NON-BLOCKING DISPOSITIONS

| ID | Disposition | Status |
|---|---|---|
| **5** — reflected source text | **CLOSED.** Module docstring now carries an explicit consumer caution (`geoclient_address.py:72-75`) naming `grc_message`/`grc2_message`, `suggestions` and `raw_fields` as unsanitized reflected input, citing G02's message as the proof; mirrored in the registry record (`geoclient.json:32` `reflected_input_warning`) and in `docs/MVP_AGENDA.md` C4 carry-forwards (`:237-241`). |
| **6** — test gaps / inert assertion | **CLOSED.** The inert `caplog.set_level(..., "app.resilience.transport")` line is gone. The leak harvest (`:668-732`) now covers **ten** paths (G01/G02/G03 success, 401, 403, 429, 500, timeout, network failure, malformed, plus two pre-network typed errors) and carries real **positive controls** (`:723-729`): every transport was actually called, every recorded call carried the sentinel in the auth header, every failure path actually raised (`pytest.fail` otherwise), and `caplog.records` is non-empty — so absence now means something. Refused 3xx is directly covered at `:544-554` (302/400/404 → `SourceUnavailableError`, never `AuthFailedError`, never retried). A module-wide autouse socket guard (`:70-79`) makes network I/O mechanically impossible. |
| **7** — absent second sub-call code | **CLOSED as a documented disposition.** The fail-closed choice and its evidentiary basis are stated in the module docstring (`:47-51`) and `_classify`'s docstring (`:355-357`), and tested on **both** sides including the absent case (`:879-893`). This was never a security defect; the disclosure is the right outcome. |
| **8** — transport seam receives the key | **CLOSED.** Module docstring `:24-27` now states that the injected `transport` receives the headers dict including the key and that any future instrumenting/caching wrapper is itself a key-handling surface requiring review. |

---

## NEW FINDINGS

**N1. [MEDIUM — BLOCKING] `copy.deepcopy(address)` raises an uncaught `RecursionError` on a hostile 200 body; an untyped exception escapes `resolve_address`.**
`geoclient_address.py:704` deep-copies the parsed response (the G3-10 fix, correct in intent — it protects `provenance["response_digest"]` from caller mutation). But `RecursionError` is caught **only** around `json.loads` (`:659-666`); nothing guards the deepcopy.

`json.loads` uses the C scanner and survives far deeper nesting than `copy.deepcopy`, which is pure Python and burns several stack frames per level. I measured the gap on this interpreter (`sys.getrecursionlimit() == 1000`): at nesting depth 300 both succeed; **at depth 500 and beyond `json.loads` succeeds and `copy.deepcopy` raises `RecursionError`** (the canonical `json.dumps` for the digest survives all tested depths, so deepcopy is the first thing to break — and it is evaluated before the `provenance` dict in the constructor call).

Proven end-to-end through the public API with an injected transport returning `{"address":{"geosupportReturnCode":"00","geosupportReturnCode2":"00","a":[[[…600 deep…]]]}}`:

> `UNTYPED ESCAPE >>> RecursionError -- not a GeoclientConnectorError`

This breaks two things the packet states explicitly: S4's "no exception escapes as an unhandled error" and S5's "every failure path is fail-closed". A consuming API would surface an untyped 500 instead of the typed `MalformedResponseError` the taxonomy promises, and the connector's own error-handling contract — the thing four gates just re-verified — would not hold on this path. It is also entirely untested: `grep` for `deepcopy|RecursionError|nest|recursion` across the 98-test module returns nothing relevant.

*Threat model, stated honestly:* the body must come from the upstream, so this needs a compromised or MITM'd `api.nyc.gov` (TLS is verified — see the leak table), not an ordinary user typing an address. No key exposure, no data corruption, no persistence. That is why it is MEDIUM rather than HIGH.

*Fix:* wrap the deepcopy (and, for symmetry, `canonical_json_digest`) in `except RecursionError` → `MalformedResponseError`, or reject excessive nesting during shape validation. Add the depth case to the S5 malformed-body parametrize list so it cannot regress.

**N2. [MEDIUM — not blocking this gate; BLOCKING the scope of the MVP_AGENDA C4 packet] The wave-wide sanitizer defect also exists in `app/resilience/transport.py`, and the rework put it on this connector's path. C4's recorded scope misses it.**
`docs/MVP_AGENDA.md:231-236` records the `$`-anchor defect for exactly three files — `mappluto_geometry_arcgis.py:314`, `zoning_features_arcgis.py:266`, `ztldb_soda.py:345`. It does **not** name `app/resilience/transport.py`, whose `sanitize_retry_after` (`:216-221`) uses the identical `$`-anchored `re.match` pattern (`_RETRY_AFTER_SAFE_RE`, `:69`) **and** an uncapped `repr()` fallback — both of the defects C1 and C2 just fixed in the connector.

Executed against the shared function: `sanitize_retry_after("7\n")`, `sanitize_retry_after("Fri, 17 Jul 2026 08:00:00 GMT\n")` and `sanitize_retry_after("120 \n")` all pass through **verbatim with the newline intact**, and a 200 KB header value returns a 200,002-character string.

This matters more now than it did at `d4cdbe79`: the rework switched this connector from `fixed_exponential_delay` to `jittered_retry_after_delay` (`:519-525`), making the Retry-After path load-bearing here for the first time.

*Bounding the actual risk, fairly:* the `retry_after` value never reaches a log line — `transport.py:485-488` logs only label/url/attempt/correlation_id — it reaches only `RateLimitedError.detail["retry_after"]` (`transport.py:482-484, 507`) and from there `to_payload()`, which is JSON-serialized, so a newline is escaped on the realistic consumer path. Production header size is additionally capped near 64 KB by `http.client`'s `_MAXLINE`. So this is a payload-hygiene and amplification defect, not a live log-forging one.

*Why it is not blocking THIS gate:* `services/api/app/resilience/**` is outside M2-T021's `allowed_paths`; the producer cannot fix it in this packet, and should not. *What is required:* add `app/resilience/transport.py` (`_RETRY_AFTER_SAFE_RE` and `sanitize_retry_after`) to the C4 packet's stated scope, so the follow-up does not ship a "wave-wide" fix that leaves the shared engine — used by all five connectors — still defective.

**N3. [LOW — scope/contract note] `AnalysisBudget.analysis_id` is unvalidated caller text echoed into an error payload.**
The rework threads an optional budget (`:517, 527, 566, 656`). On exhaustion the shared engine builds `detail = {"max_upstream_requests", "consumed", "analysis_id"}` (`transport.py:401-411`); `analysis_id` is accepted by `AnalysisBudget.__init__` (`budget.py:28-37`) with no type, length or charset validation, and flows into `RequestBudgetExceededError.to_payload()`. `max_upstream_requests` **is** validated; `analysis_id` is not. Pre-existing shared code, used identically by three accepted siblings, and the caller is our own code — so this is a contract note, not a defect in this packet: whoever constructs the budget in the consuming API packet must not derive `analysis_id` from untrusted input. Worth one line in the consumer carry-forwards beside the reflected-input warning.

**N4. [LOW] Transient allocations before the new caps apply.**
Both C2 and C3 bound what reaches the *payload*, correctly. They do not bound the intermediate work: `repr(value)` is built in full before `[:300]` (`:179`), and `sorted(map(_safe_text, parsed.keys()))` materializes and sorts **every** key before slicing 20 (`:537-538`). On a 10 MB hostile body that is a transient multi-MB allocation and an O(n log n) sort of ~500k strings. The parsed body already occupies comparable memory, so this is not a new amplification class and I am not treating it as a finding against the fix — but `heapq.nsmallest(_MAX_REPORTED_KEYS, …)` and slicing before `repr` are close to free if touched anyway.

**N5. [LOW] The `clock` seam has the same trust property as the `transport` seam, without the same warning.**
`clock` (`:564`) feeds both the retry policy's `wall_clock` (`:654`) and `provenance["retrieved_at"]` (`:678`). An injected clock therefore stamps provenance. That is a legitimate and well-used test seam (`test_s8_retrieved_at_comes_from_the_injected_clock`), and it is caller-controlled rather than attacker-controlled — but the docstring now warns about exactly this property for `transport` (`:24-27`) and says nothing for `clock`. One sentence would make the seam contract consistent.

**N6. [LOW] No test exercises a hostile `Retry-After` value.**
`test_s5_retry_after_is_honored_on_429` (`:569-584`) covers the well-formed `"7"` case and proves the jittered policy honors it (`sleeps == [7.0]`). Nothing covers a malformed, oversized, or newline-bearing header on the path the rework just activated. Given N2 lives in shared code, a connector-level test asserting no `detail` value carries a newline (the pattern already used at `:514-529` for the network-reason path) would be the cheap local guard.

---

## LEAK-SURFACE TABLE (re-traced at eb6a15f8)

| # | Surface | Status | Evidence at the new code |
|---|---|---|---|
| 1 | Key in the URL / query string | **CLOSED** | `params` still only ever receives `houseNumber`/`street`/`borough`/`zip` (`:626-630`); key goes only to `headers` (`:636`). The header-only decision is restated at `:18-27`. |
| 2 | Key at rest / in module state | **CLOSED** | `:611-616` — read at call time into a local. The rework additionally removes the env fallback for an explicitly-passed empty key (`:611`), so a caller bug cannot silently pick up the process key; tested at `:775-785`. A non-string `key` yields `None` → typed `KeyMissingError`, never a crash and never an echo. |
| 3 | `headers` dict captured by the transport | **CLOSED in production, now documented** | `:640-641` resolves the default at call time; the seam's key-handling property is disclosed at `:24-27` (prior finding 8). |
| 4 | `TransportResponse` | **CLOSED** | Unchanged — `transport.py:79-93` carries status, body and *response* headers only. |
| 5 | Exceptions from the shared engine | **CLOSED for the key** | Terminal detail (`transport.py:507`) is `{attempts, reason?, http_status?, retry_after?, url, max_attempts, reason_kind}`; `url` is key-free per row 1. The `retry_after` member's own hygiene is N2 — a size/newline issue, never a key issue. |
| 6 | Retry-loop logging in the shared engine | **CLOSED** | `transport.py` still has no module logger and no DEBUG statements; the four `warning` calls (`:459, 469, 485, 492`) never take headers or `retry_after` as arguments. |
| 7 | Connector logging | **CLOSED, and hardened** | `:720-726` logs correlation_id/status/sanitized GRCs. The C1/C2 fixes mean a hostile GRC can no longer split or inflate this record — the exact defect I raised last round, now closed at its only reachable site. |
| 8 | Redirects re-sending the key cross-host | **CLOSED — re-verified after the import change** | The rework deleted the connector-local `urllib_transport` wrapper and `_OPENER` and imports the shared function directly (`:102`). Executed: `geoclient_address.urllib_transport is app.resilience.transport.urllib_transport` → `True`; the local `_OPENER` global is gone; `DEFAULT_OPENER` carries `NoRedirectHandler` and **no** stock `HTTPRedirectHandler`. The shared function defaults `opener=None` → `DEFAULT_OPENER` (`transport.py:168`), so redirect refusal survives the refactor. Behaviour test at `:544-554`. |
| 9 | Auth-failure (401/403) body echo | **CLOSED** | `:473-481` — detail is `{http_status, url}`; the body is never read into the error and 401/403 never retry. Asserted at `:531-542`, including `"gateway says no" not in combined`. |
| 10 | Provenance | **CLOSED** | `:705-718` — `request_params` is `dict(params)`; the two additions (`digest_canonicalization`, from the `CANONICALIZATION_SPEC` constant) are static. No header field exists on the record. |
| 11 | `AddressResolution` repr / `asdict` | **CLOSED** | No field holds the key; harvested across ten paths at `:668-732` with positive controls. |
| 12 | Repo artifacts (fixtures, docs, tests) | **CLOSED** | Re-scanned at HEAD: no 32-hex key-shaped run in the connector, tests, any fixture, or the registry record. All three fixture `response_sha256` values still verify against their bodies, and no fixture body contains the auth header name. The three `request_url` fields carry only `houseNumber`/`street`/`borough`. The rework touched fixture **metadata only** (retrieval timestamps corrected with a stated basis and a disclosed prior error) — bodies and digests unchanged. Sentinel unchanged and still obviously fake. |
| 13 | SSRF / injection via caller input | **CLOSED — re-verified under the new encoder** | `urlencode(params, quote_via=quote)` (`:635`) is a behaviour change, so I re-probed it. urlencode passes its default `safe=''` through to `quote`, so `/` is encoded too: `houseNumber='314\r\nX-Injected: 1'` → `314%0D%0AX-Injected%3A%201`; `street='a&zip=99999#frag/..'` → `a%26zip%3D99999%23frag%2F..`; `borough='m?x=1'` → `m%3Fx%3D1`. Spaces now emit `%20`, matching the recorded capture URLs. No header injection, parameter smuggling, path traversal or fragment truncation. Host and scheme remain a hardcoded `https://` constant (`:128`). |
| 14 | TLS weakening | **CLOSED** | Still no `_create_unverified_context`, `CERT_NONE`, `verify=False` or `check_hostname=False` under `services/api/app/`. |
| 15 | Frame locals in a traceback | **CLOSED today, fragile tomorrow** | Unchanged from round 1: no Sentry, `exc_info=True`, `format_exc` or cgitb under `services/api/app/`. N1 makes this marginally more relevant — an uncaught `RecursionError` propagating out of `resolve_address` carries frames whose locals include `headers` — which is a further reason to type that failure rather than let it escape. |
| 16 | Response-body size | **CLOSED** | `MAX_RESPONSE_BYTES` = 10,485,760 still applies via `_bounded_read` on both the success and `HTTPError` branches, and still sits on this connector's production path (verified through the new import). |
| 17 | Retry multiplication | **CLOSED — re-traced under the new jittered policy** | Still one bounded `for attempt in range(1, max_attempts + 1)` (`transport.py:451`). The new policy cannot extend the budget: a parseable `Retry-After` above `retry_after_cap` (default 120 s, `:136`) returns `None`, which **stops** retrying rather than sleeping (`transport.py:499-504`); otherwise full-jitter backoff bounded by `backoff_cap` (30 s, `:135`). `parse_retry_after` (`retry.py:36-66`) bounds delay-seconds to 10 digits, wraps HTTP-date parsing in `try/except (TypeError, ValueError)`, clamps at `max(0.0, …)` so no negative sleep is possible, and strips before matching so its own `$`-anchored `_DELAY_SECONDS_RE` (`retry.py:33`) cannot be fooled by a trailing newline. Bounded attempts asserted for timeout, 429, 500 and the budget path (`:507-601`). |
| 18 | **NEW** — AnalysisBudget path | **CLOSED for the key** | Budget units are consumed **before** I/O (`transport.py:452-454`); `RequestBudgetExceededError` takes the standard signature and its detail is `{max_upstream_requests, consumed, analysis_id}` — no key, no headers, no URL. `analysis_id` hygiene is N3. Tested at `:585-601`: one unit per attempt, second attempt never paid for, typed on exhaustion. |
| 19 | **NEW** — jittered Retry-After path | **CLOSED for the key; see N2** | The `retry_after` value is response-header data, never request-header data; it reaches `RateLimitedError.detail` and never a log line. Its own sanitizer is defective in shared code (N2), but no path carries the subscription key. |
| 20 | **NEW** — call-time transport resolution | **CLOSED** | `:640-641`. Verified the monkeypatch seam still resolves through the module global (relied on by `:237-250` and `:805-816`) and that the no-redirect opener survives the indirection removal (row 8). |
| 21 | Hostile suggestion count | **CLOSED, and now count-independent** | `_extract_suggestions` (`:375-395`) no longer parses `numberOfStreetCodesAndNamesInList` at all — it walks a fixed `_MAX_SUGGESTIONS = 32` slots and surfaces populated ones. This removes the `int(str(declared))` parse entirely, so the hostile-count surface I probed last round no longer exists. Declared count remains verbatim in `raw_fields`. |
| 22 | Non-string / absent GRC types | **CLOSED, stricter** | `_classify` (`:354-372`) requires `isinstance(c, str)` **and** `fullmatch` on both codes. Executed: `"00\n"`, `"0"`, `"000"`, `"ee"` all → `unrecognized_status`. |
| 23 | **NEW** — deep-nesting handling | **OPEN → N1** | `copy.deepcopy` at `:704` is unguarded; `RecursionError` escapes untyped. Proven end-to-end. |

---

## WHAT I VERIFIED

- **Read in full:** the reworked connector (728 lines), the reworked test module's structure plus every cited test body, `app/resilience/transport.py`, `app/resilience/retry.py`, `app/resilience/budget.py`, the three fixtures, the registry record, and `docs/MVP_AGENDA.md` C4.
- **Executed C1 closure:** eight `_safe_text` inputs including the exact trailing-newline payload from my prior report — now `repr()`-escaped, no newline in output; plus `_GRC_SHAPE_RE.fullmatch` and `_classify` across six malformed codes.
- **Executed C2 closure:** 9 MB and 1 M-newline inputs — both return exactly 300 characters.
- **Executed C3 closure:** constructed 61-key hostile object with 500-char keys and a planted body value — 20 keys, truncation marker, true count, 6 KB payload, planted value absent; plus the non-dict branch.
- **Executed C4 closure end-to-end** through `resolve_address` with an injected transport: 5000-char values for all four params and a non-string `house_number` — every one typed, pre-I/O, value never echoed, payloads ~300 chars.
- **Proved N1 end-to-end** through `resolve_address`: a 600-deep hostile body that `json.loads` accepts escapes as an untyped `RecursionError`; measured the `json.loads` / `deepcopy` / `json.dumps` divergence across depths 100–990.
- **Probed N2** against the shared `sanitize_retry_after`: three in-charset values with trailing newlines pass through verbatim; a 200 KB value returns 200,002 characters.
- **Re-verified the redirect chain after the import refactor:** identity of the connector's `urllib_transport` with the shared function, absence of the local `_OPENER`, `NoRedirectHandler` present and stock `HTTPRedirectHandler` absent in `DEFAULT_OPENER`.
- **Re-probed URL construction** under the new `quote_via=quote` encoder with CRLF, `&`, `=`, `#`, `?` and `/..` payloads.
- **Re-verified fixture integrity at HEAD:** all three sha256 digests recomputed and matching; confirmed the rework changed metadata only; re-scanned all changed files for 32-hex key-shaped runs (none) and checked all three `request_url` fields.
- **Confirmed the disposition artifacts exist** where claimed: docstring `:24-27` (seam), `:42-51` (50/75 narrowing, sub-call asymmetry), `:72-75` (reflected input); registry `reflected_input_warning` and `empty_string_rule`; MVP_AGENDA C4 `:227-241`.
- **Did not** run the test suite, edit any file, write the ledger, or make any network request.

**Recommended recording:** PASS, with **N1 blocking for acceptance**, and **N2 + N3 recorded as required scope corrections** to the MVP_AGENDA C4 packet and the consumer carry-forwards respectively. N4–N6 are optional polish. If the orchestrator weights a regression introduced by a corrective rework above a first-pass finding of equal severity, recording FAIL instead is defensible on the same evidence — the remediation required is identical either way.
