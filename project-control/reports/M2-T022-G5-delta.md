<!-- Reviewer return preserved VERBATIM by the orchestrator (report-preservation rule,
.claude/rules/project-control.md; transport entity-decoding applied: &lt; -> <, &gt; -> >).
Reviewer: independent security-reviewer subagent (G5 delta), returned 2026-09-12,
reviewed HEAD e40c87c4. -->

All five delta items are verified. Summary of findings for the report.

- STATUS_STATE_MATRIX in `address_resolution.py` appears only in the docstring, `__all__`, and the frozenset definition — it is never consulted for status routing (routing uses `_ERROR_STATUS.get(state, _DEFAULT_ERROR_STATUS)`), so it is documentation-only.
- The delta touched no logging/except/provenance/error-body/success-document lines (O1/O2 structurally unchanged), confirmed empirically by the production-wiring probe's log line.

Here is my delta gate report to return to the orchestrator verbatim.

---

VERDICT: PASS

# G5 Security Gate Report (DELTA) — M2-T022 (address-resolution API endpoint)

- **Task:** M2-T022 — `GET /api/v1/address-resolution` over the internal flag-gated API in front of the M2-T021 Geoclient connector
- **Reviewed HEAD:** `e40c87c43e72a4f7e25611e7f83ffca562009259` (branch `candidate/D-024-mrl-option-b`)
- **Delta commit under review:** `803d5606` (rework); prior wave PASS at `ec4b75dc` (report `project-control/reports/M2-T022-G5.md`) stands
- **Scope of this review:** DELTA ONLY (`git diff ec4b75dc..e40c87c4`). Source changes limited to `services/api/app/api/v1/address_resolution.py` and `services/api/tests/api/test_address_resolution_api.py`; all other changed paths are `project-control/**`.
- **Reviewer:** independent security-reviewer (did not author). Read-only (ADR-005). `PYTHONDONTWRITEBYTECODE=1`; in-process probes only, no network (egress seams blocked); no pytest/ruff; nothing written; no `project_control.py`.

## Delta item 1 — `_default_resolver` signature (G1 HIGH-1 fix) — PASS
- Static: connector `resolve_address(house_number, street, *, borough=None, zip_code=None, key=None, transport=None, …, budget=None)` (services/api/app/connectors/geoclient_address.py:564) reads the subscription key from `key` or, when `None`, from `GEOCLIENT_SUBSCRIPTION_KEY` at call time. The new `_default_resolver(house_number, street, *, borough=None, zip_code=None)` forwards exactly `resolve_address(house_number, street, borough=borough, zip_code=zip_code)` — NO key, NO transport, NO budget. Straight-line body, no branching, no reference to the key/env var anywhere in the module (C4 duty 3 preserved at the production seam).
- Probe (production wiring, NO dependency override; `app.dependency_overrides.clear()`; module-global `resolve_address` monkeypatched to a recorder that drives the REAL connector over a fixture `RecordingTransport` with sentinel key `TEST-SENTINEL-KEY-OBVIOUSLY-FAKE`; module logger captured):
  - `STATUS_CODE: 200`, `BODY_STATUS_FIELD: resolved`, `TRANSPORT_CALLS: 1` → production route→`_default_resolver`→`resolve_address` genuinely reaches the connector (before the fix this 500'd on every real call).
  - `RECORDED_SEAM_ARGS: {house_number:'314', street:'w 100 st', borough:'manhattan', zip_code:None, extra:{}}` → seam forwards only the four route inputs; `SEAM_NO_BUDGET_NO_TRANSPORT: True`.
  - Positive control `sentinel_in_transport_headers: True` (connector used the key) yet `SENTINEL_IN_BODY/HEADERS/LOGS: False`; `GEOCLIENT_SUBSCRIPTION_KEY`/`Ocp-Apim` absent from body; logs non-empty and status/id/count-only (`address_resolution_v1 outcome status=resolved correlation_id=… connector_correlation_id=… source_facts=7`). No new branch touches the key.

## Delta item 2 — `_REFLECTED_INPUT_WARNING` extension — PASS
- Field list EXTENDED 6→9: all prior entries retained (`grc_message`, `grc2_message`, `suggestions`, `canonical.street_name_normalized`, `canonical.borough_name`, `provenance.request_params`); added `input_echo` and `source_facts[].original_value/normalized_value (street/borough facts)`. No previously-named surface dropped. The `warning` string is byte-identical to `ec4b75dc` (compared via `git show`) — unchanged in substance.
- Probe (hostile `<script>alert(1)</script>\r\nX-Injected: pwned` street, `7<b>7` house number): `input_echo.street`/`house_number` reflect the hostile input byte-exact; `fields` count 9 with all 6 prior fields + `input_echo` + 2 `source_facts[]` entries present; no `X-Injected` header materialized; hostile text absent from logs. This is a genuine over-disclosure fix (`input_echo` was reflected raw all along but previously unnamed), not a security regression.

## Delta item 3 — matrix documented-unreachable pair `(503, "request_budget_exceeded")` — PASS
- Grep of the module: every `budget`/`AnalysisBudget`/`analysis_id`/`request_budget` occurrence is docstring/comment/matrix text — NO `AnalysisBudget` construction and NO `budget=` argument passed anywhere. `request_budget_exceeded` is not in `_ERROR_STATUS`, so it would only ever fall to `_DEFAULT_ERROR_STATUS = 503`, consistent with the documented pair; it cannot arise because no budget is passed. `STATUS_STATE_MATRIX` is documentation-only (docstring + `__all__` + definition; routing uses `_ERROR_STATUS.get(...)`, never the frozenset). The pair documents, it does not enable.

## Delta item 4 — leak scan + sensitive-path integrity — PASS
- `git diff --name-only ec4b75dc..e40c87c4 -- app/connectors app/resilience app/config.py app/config` → **empty**. Nothing under `app/connectors`, `app/resilience`, `app/config` changed across the delta.
- Leak scan of `git show 803d5606` (and of added lines only) for key-shaped runs (`Ocp-Apim`, `GEOCLIENT_SUBSCRIPTION_KEY`, `os.environ/getenv`, `key=`, bearer/secret/token, 32–40+ char high-entropy runs): the only hits are the 40-char commit SHA (line 1) and two producer-report prose lines (a test name and the E501 URL-token discussion). No credential, no key-shaped literal introduced; the sole credential-like literal remains the words-only sentinel in tests.

## Delta item 5 — prior O1/O2 observations unaffected — PASS
- The delta touched NO logging, `except`, provenance-transport, error-body, `_success_document`, or `_internal_error` lines (confirmed by a diff filter returning no matches). O1 (connector-call generic guard logs correlation-id only, no `stage`/traceback) and O2 (success transports `outcome.provenance` wholesale; failure transports `payload["message"]`, only `retry_after` re-bounded locally) are structurally unchanged and remain accepted, non-blocking observations. The wiring probe empirically reconfirmed the O1 log format is key-free and reflected-text-free.

## Verdict
The rework is a strictly security-neutral-or-improving delta: the HIGH-1 signature fix makes production genuinely reach the connector while still passing no key/no transport/no budget; the reflected-input contract is extended (never narrowed) with the warning text unchanged; the new matrix pair documents an unreachable-by-construction state without introducing any budget path; and no connector/resilience/config surface changed and no secret was introduced. Prior PASS at `ec4b75dc` stands; the delta introduces no critical, high, medium, or low security defect.

**VERDICT: PASS** — reviewed HEAD `e40c87c4`.

**Probes executed:** (1) production-wiring success probe — no dependency override, module `resolve_address` monkeypatched to the real connector over a fixture transport with sentinel key (200/resolved, 1 transport call, seam extra `{}`, sentinel in transport header only, absent from body/headers/logs); (2) reflected-warning extension probe — hostile CRLF input, verified 9-field list superset, `input_echo` verbatim reflection, no header injection, nothing logged, warning text unchanged; (3) budget-construction grep (documentation-only, no `AnalysisBudget`/`budget=`); (4) delta leak scan + sensitive-path diff (`app/connectors|app/resilience|app/config` empty); (5) diff filter confirming logging/except/provenance/success-doc code untouched (O1/O2 intact).
