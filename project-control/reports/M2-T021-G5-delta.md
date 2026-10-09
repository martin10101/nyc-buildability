<!-- Reviewer return preserved VERBATIM by the orchestrator (report-preservation rule,
.claude/rules/project-control.md; transport entity-decoding applied: &amp; -> &).
Reviewer: independent security-reviewer subagent (G5 delta re-review), returned 2026-09-11,
reviewed HEAD 96c398aa. -->

I have completed all verification. Let me compose the delta-review report.

All checks are done. Here is my complete delta-review report.

---

# M2-T021 — G5 independent security DELTA re-review (corrections at 96c398aa)

## VERDICT: PASS

**Task:** M2-T021, Geoclient v2 address-resolution connector — delta review of the round-2 corrections.
**Reviewer:** independent G5 security reviewer (did not write this code; same reviewer as the prior `d4cdbe79` PASS and the `eb6a15f8` re-review that raised N1/N2/N3).
**Reviewed identity:** `96c398aa1e8d0a2bce3facfcbc932c4b247831e3` on `candidate/D-024-mrl-option-b`.
**Delta baseline:** `eb6a15f8` (my prior round). Correction commits: `01c01c5f` (producer material) + `7a43d2d0` (records), resubmitted at `96c398aa`.
**Prior verdict:** PASS with **N1 BLOCKING** for acceptance (uncaught `RecursionError` from `copy.deepcopy` on a hostile deep-nested 200 body) plus N2/N3 required scope corrections.
**Discipline (ADR-005):** read-only. No file edited, no test suite/ruff run, no ledger written, no network request. Read-only `git`/`grep` plus offline `python` probes fed via stdin (no file written to the repo) with `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=.`, injected in-memory transport only.

**Result:** N1 is **genuinely closed by execution**. N2 and N3 scope corrections landed exactly as required. The delta opens no leak surface, and no production code other than the connector changed. The one prior blocking condition is cleared; this delta carries no new blocking findings.

---

## 1. N1 — CLOSURE VERIFIED BY EXECUTION

The guard is at `geoclient_address.py:698-712`, structurally correct:
- It sits AFTER JSON parse (`:675`), AFTER shape validation (`:682-688`, `isinstance(parsed, dict)` and `isinstance(parsed["address"], dict)`), and AFTER `_classify` (`:696`).
- The `try` wraps **only** `raw_fields = copy.deepcopy(address)` and `response_digest = canonical_json_digest(parsed)` (`:703-705`); the `except RecursionError` (`:706`) raises `MalformedResponseError(...) from None` with `detail={"url": url, "body_chars": len(response.body)}` (`:707-712`). Nothing else is inside the block.
- `MalformedResponseError` subclasses `GeoclientConnectorError` (`:255`, `:193`).

**Probe 1 — hostile 600-deep body through public `resolve_address`, injected transport, no network** (body `{"address":{"geosupportReturnCode":"00","geosupportReturnCode2":"00","a":[[[…600 deep…]]]}}` with a body sentinel at the leaf and a fake key):
- `json.loads` accepted the 600-deep body: `True`; bare `copy.deepcopy(parsed)` on it raised `RecursionError` (hazard is real).
- `resolve_address(...)` raised **`MalformedResponseError`** (isinstance `GeoclientConnectorError` True), `error_type == "malformed_response"` — **never an untyped `RecursionError`**.
- `detail` keys exactly `['body_chars', 'url']`; `detail == {'url': 'https://api.nyc.gov/geoclient/v2/address?houseNumber=314&street=Fifth%20Avenue&borough=Manhattan', 'body_chars': 1314}` — `body_chars` is an `int` == `len(response.body)`, **no body content**.
- `url` is **key-free** (fake key, `Ocp-Apim`, `Subscription` all absent).
- No body sentinel and no key in `str(exc)`, `repr(exc)`, `exc.message`, or `to_payload()` JSON; no `[[[` fragment in any of them.
- **`from None` honored:** `exc.__cause__ is None` == True, `exc.__suppress_context__` == True (`__context__` is the RecursionError but suppressed; `__cause__` chain length 0 — the body-laden recursion frames do not ride the raised exception, and `to_payload()` carries no traceback/context at all).
- Transport called exactly once; the fake key was present only in the injected **headers** seam and absent from the URL.

**Probe 2 — guard masks no legitimate path:**
- Normal success body → `status == "resolved"`, `bbl == "1000010001"`, `provenance["response_digest"]` set, `raw_fields` populated (guard transparent).
- Shallow malformed body `{"notaddress":1}` → `MalformedResponseError` raised via the **shape-validation branch** (`:682-688`), which precedes the guard.
- Depth-300 body (survives both `json.loads` and `deepcopy`) → `status == "resolved"` (guard transparent on non-hostile depth).

**Probe 3 — regression pin:** the EXACT new `deepnest600` parametrize body (`"[" * 600 + "]" * 600`, `test_geoclient_address.py:597-616`) driven through `resolve_address` raised `MalformedResponseError` (detail keys `['body_chars','url']`). The case is a new id in `test_s5_malformed_200_bodies_fail_closed`, which asserts `pytest.raises(MalformedResponseError)` — so the regression is pinned. (The removed vacuous `raw_fields["bbl"]="MUTATED"` self-comparison at `:160` is a test-quality cleanup, not a security change; deep-copy relabeled defense-in-depth in the docstring.)

N1 is closed.

## 2. N2 — VERIFIED

`docs/MVP_AGENDA.md` C4 (records commit `7a43d2d0`, lines ~233-240) now names **`app/resilience/transport.py` `_RETRY_AFTER_SAFE_RE` + `sanitize_retry_after`** ("pass an in-charset value with a trailing newline through VERBATIM and have an uncapped `repr()` fallback — load-bearing for every connector on the jittered `Retry-After` path") as IN SCOPE for the wave-wide sanitizer packet, alongside the three sibling connectors, with remediation "fullmatch + length-cap all three connectors AND the shared engine, mirror tests."

## 3. N3 — VERIFIED

The C4 carry-forwards now warn: "`AnalysisBudget.analysis_id` is UNVALIDATED caller text echoed into the budget-exhaustion error payload (G5 re-review N3) — the consuming packet must never derive it from untrusted input."

## 4. Leak-surface delta — no surface opened

- **New error branch:** detail is `{url, body_chars}` only — key-free url (key lives only in `headers` built at `:651`), `body_chars` is an int length. Verified at runtime (Probe 1).
- **Changed docstrings/comments** (`geoclient_address.py` module docstring type-drift rule, `AddressResolution` docstring, deep-copy defense-in-depth comment, the deepnest guard comment): no key material.
- **Registry/record edits:** `docs/research/source-registry-drafts/geoclient.json` adds only an additive `type_drift_rule` doc entry; `evidence-map.json`, `B-004`, `MVP_AGENDA.md`, `M2-T021.json` are records — the only key-related token is the env-var NAME `GEOCLIENT_SUBSCRIPTION_KEY`, never a value.
- **32-hex scan:** `git show 01c01c5f 7a43d2d0 | grep -Eo '[0-9a-f]{32,}'` returns only the two delta commit SHAs (`01c01c5f…`, `7a43d2d0…`) referenced in the record files — commit hashes, not key material; no sha256 digests were even introduced in the changed lines. No 32-hex key-shaped run in any changed file.
- **`from None`** improves the prior posture: without it the RecursionError context would propagate un-suppressed; with it, the context is suppressed and `to_payload()` is clean. (Row-15 "fragile tomorrow" note — no Sentry/`exc_info`/`format_exc`/cgitb under `services/api/app/` — is pre-existing and unchanged by this delta.)

## 5. No other production code changed — CONFIRMED

Full delta `eb6a15f8..96c398aa`: the only production source file changed is `services/api/app/connectors/geoclient_address.py` (the N1 guard + docstring/comment relabeling). The remaining changed paths are the test (`test_geoclient_address.py`), docs (`MVP_AGENDA.md`, `SESSION_HANDOFF.md`, registry draft `geoclient.json`), and control-plane records (`B-004`, `M2-T021-evidence-map.json`, `M2-T021-producer-report.md`, `state.json`, `M2-T021.json`, the four `M2-T021-G{1,3,4,5}-rereview.md` from the prior wave). No change to `transport.py`, `retry.py`, `budget.py`, or any other connector.

---

## RECORDED RECOMMENDATION

**PASS.** The sole prior blocking condition (N1) is genuinely closed, proven end-to-end through the public API; N2 and N3 required scope corrections landed as specified; the delta opens no leak surface and touches no other production code. No new blocking or non-blocking security findings arise from this delta. The earlier N4–N6 items remain optional polish and are unaffected by these corrections.

**Files of record:** connector `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\app\connectors\geoclient_address.py` (guard `:698-712`); test `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\tests\connectors\test_geoclient_address.py` (`deepnest600` at `:597-616`); scope corrections `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\docs\MVP_AGENDA.md` (C4).
