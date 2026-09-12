<!-- Reviewer return preserved VERBATIM by the orchestrator (report-preservation rule,
.claude/rules/project-control.md; transport entity-decoding applied: &lt; -> <, &gt; -> >).
Reviewer: independent data-contract-verifier subagent (G3 delta), returned 2026-09-12,
reviewed HEAD e40c87c4. -->

I now have everything needed. Let me confirm my analysis of the reflected-surface audit and error-path value-freeness is complete by tracing the data path.

The verification is complete. Here is my findings summary before the report:

- **input_echo path**: `input_echo.{house_number,street,borough,zip}` in `_success_document` (lines 375-380) come from `outcome.house_number_in/street_in/...`, which the connector sets from `_validated_input(...)` = `value.strip()`. Hostile strings `<script>alert(1)</script>` / `7<b>7` have no surrounding whitespace, so strip is a no-op → byte-exact reflection. This assembly is byte-unchanged from ec4b75dc; the prior round already proved byte-exactness.
- **Test non-vacuity**: `install_resolver_for_body` drives the REAL `resolve_address` with the caller's actual args, so `test_s6_input_echo_is_a_named_reflected_surface` genuinely reproduces the hostile input through the connector.

---

VERDICT: PASS

# G3 Data-Contract Gate Report (DELTA) — M2-T022 (address-resolution API endpoint)

- Reviewed HEAD: **e40c87c4** (branch candidate/D-024-mrl-option-b); rework commit under review **803d5606**; prior FAIL at **ec4b75dc**.
- Reviewer: data-contract-verifier (independent; did not author). Read-only per ADR-005; PYTHONDONTWRITEBYTECODE=1; no pytest/ruff/project_control.py; nothing written.
- Method: diff-scoped delta review of 803d5606 vs ec4b75dc; source-level re-trace of the escape-contract data path through the real connector; helper non-vacuity check; scope confirmation via `git show --stat` and an empty `git diff -- 'packages/**'`.

## 1. Escape contract now complete — PASS
- `_REFLECTED_INPUT_WARNING["fields"]` now leads with `input_echo` and adds `source_facts[].original_value (street/borough facts)` and `source_facts[].normalized_value (street/borough facts)` (route lines 209-227).
- **input_echo reflects byte-exact:** `input_echo.*` (lines 375-380) = `outcome.{house_number_in,street_in,borough_in,zip_in}`, set by the connector's `_validated_input` (`value.strip()`). For `street="<script>alert(1)</script>"` / `house="7<b>7"` strip is a no-op → byte-exact. This assembly is byte-identical to ec4b75dc (my prior round proved byte-exactness there); the carry-forward is sound.
- **Reproduction is test-enforced and non-vacuous:** `test_s6_input_echo_is_a_named_reflected_surface` drives the hostile input through the REAL connector (via `install_resolver_for_body` → `resolve_address` with the caller's actual args), asserts `input_echo.street == hostile`, `input_echo.house_number == "7<b>7"`, `"input_echo" in fields`, and a `source_facts[]`-prefixed entry is present.
- **Full re-audit of every reflected surface in the response — nothing still missing.** Success-document surfaces carrying caller-reflected/unsanitized source text are all named: `input_echo`, `provenance.request_params` (the stripped caller params), `grc_message`, `grc2_message`, `suggestions`, `canonical.street_name_normalized`, `canonical.borough_name`, and the street/borough `source_facts[]` values. The connector's largest unsanitized surface, `raw_fields`, is deliberately NOT transported into the response document (verified in `_success_document`), so it needs no listing. `grc_reason`/`grc2_reason`/`provenance.reason_code(2)` are Geosupport structured reason codes (not free-text caller reflections), consistent with the connector's own documented caution set — not a blocking omission.
- **Error path confirmed value-free (as the packet directed).** The error body transports only `error.{error_type,message,connector_correlation_id,source_id,endpoint}` + a locally-bounded `retry_after`. Connector `InvalidInputError` messages/detail carry only param NAMES, type names, and integer lengths — no caller value; the connector `detail.url` (which does embed the query string) is NOT transported (route emits `payload.get("endpoint")` = the constant base URL, and never the wholesale `detail`). The 422 invalid_input payload is value-free. So the absence of a reflected-input warning on the error path is correct — there is nothing reflected there.

## 2. False universal retracted (not silently rewritten) and test-enforced — PASS
The original "names every reflected surface" sentence remains in place (report line 23-24); addendum item 2 (lines 95-104) explicitly RETRACTS it ("that was FALSE at review time … retracted, not rewritten, and the property is now enforced by test rather than claimed in prose"). The property is enforced by the new S6 test above. Correct retraction discipline.

## 3. Matrix/doc deltas introduce no new inaccuracy — PASS
`(503, "request_budget_exceeded")` added as a documented UNREACHABLE-BY-CONSTRUCTION pair; matrix exhaustiveness test updated to 10 pairs. **No budget at the production seam post-rework:** `_default_resolver` calls `resolve_address(house_number, street, borough=borough, zip_code=zip_code)` — no `budget=` (default None); `test_s1_production_wiring_default_resolver_reaches_the_connector` asserts `recorded["extra"] == {}`. The "would emit at the default 503 if a budget were introduced" claim is accurate (RequestBudgetExceededError → `except GeoclientConnectorError` → `_ERROR_STATUS.get(...)` miss → `_DEFAULT_ERROR_STATUS=503`); the prior comment crediting the generic 500 guard was indeed wrong and is corrected.

## 4. Prior PASS items stand (diff-scoped) — PASS
The route diff touches only four regions: two docstring passages, the matrix comment + one added pair, `_REFLECTED_INPUT_WARNING.fields`, and `_default_resolver`'s signature. `_FACT_FIELDS`, `_source_facts` (mapping, no-fact/withheld-with-reason rules, BBL-validation gate), `DATASET_VERSION`, and the verbatim `provenance` transport in `_success_document` are byte-untouched. My prior PASS findings on fact mapping, dataset_version honesty, no-fact rules, and provenance transport carry forward unchanged.

## 5. Scope — PASS
`git show --stat 803d5606` = exactly three files (producer report, route, test). `git diff ec4b75dc 803d5606 -- 'packages/**'` is EMPTY — `packages/contracts/**` byte-untouched. The new production-wiring test also stands as a genuine regression pin (reverting to the `**kwargs`-only default would make the route's positional call raise → generic 500 → the test's `status_code == 200` assertion fails).

## Conclusion
Every blocking finding from the ec4b75dc G3 FAIL is corrected: the escape contract now names `input_echo` and the street/borough `source_facts[]` values; byte-exact reflection is reproduced by a non-vacuous test; the false universal is retracted and property-enforced; the matrix delta is accurate and the budget pair genuinely unreachable at the production seam; prior PASS items and packages are untouched.

VERDICT: PASS (reviewed HEAD e40c87c4; rework commit 803d5606).

Relevant files:
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\app\api\v1\address_resolution.py
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\tests\api\test_address_resolution_api.py
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\app\connectors\geoclient_address.py
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M2-T022-producer-report.md
