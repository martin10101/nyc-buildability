# M2-T021 — Producer report

**Task:** Geoclient v2 address-resolution connector. **Producer:** backend-engineer/orchestrator.
**Branch:** `task/M2-T021-geoclient-connector`, worktree `wt-m2t021`, base `5937b1f4` (the contract).
**Date:** 2026-09-11.

## What was built

1. **`services/api/app/connectors/geoclient_address.py`** — `resolve_address(house_number,
   street, *, borough|zip_code)` → typed `AddressResolution`. Statuses exhaustive:
   `resolved` (BOTH sub-call GRCs 00), `resolved_with_warnings` (both in {00,01}, ≥1 warning),
   `ambiguous` (EE — suggestions surfaced verbatim, never auto-picked), `not_found` (11),
   `rejected` (every other valid-shape code — the documented reject class), and
   `unrecognized_status` (invalid-shape/absent GRC, fail closed). Transport/auth/input failures
   RAISE the typed taxonomy (`KeyMissingError` before any network attempt, `AuthFailedError`
   401/403 never retried and never body-echoed, `RateLimitedError`, `SourceTimeoutError`,
   `SourceUnavailableError`, `MalformedResponseError`, `InvalidInputError`). Reuses the shared
   hardened transport (`app.resilience.transport`): bounded body read, NO redirect following
   (the subscription-key header can never be re-sent to a redirect target), bounded retry on
   429/5xx/timeout/network only via `standard_retry_hooks`. Provenance on every outcome:
   source_id, endpoint, key-free request params, retrieval timestamp, both GRC codes + reasons,
   canonical response digest (`canonical_json_digest`, the accepted M2-T004 spec), correlation id.
   Canonical fields verbatim (identifiers stay strings; coordinates stay source JSON numbers);
   the full response `address` object rides along in `raw_fields`; absent fields are `None`,
   never fabricated (null-omission rule).

2. **Two new RECORDED fixtures** (live captures from the owner machine per the packet path note,
   single KB-scale requests, key-absence machine-verified before commit):
   `G02_address_ambiguous_ee.json` (misspelled street → GRC EE, reason 1, suggestion
   `streetName1`/`streetCode1`, `numberOfStreetCodesAndNamesInList` — this capture is what pins
   the suggestion-list field names so nothing is guessed) and `G03_address_rejected_42.json`
   (house number 99999 → GRC 42 ADDRESS NUMBER OUT OF RANGE). G01 (happy path) was already
   committed at contract time.

3. **`docs/research/source-registry-drafts/geoclient.json`** — registry record: agency, base URL,
   endpoint contract, header-only auth + key storage policy, rate limits (officially UNKNOWN —
   recorded as such, with the connector's polite posture), the two-sub-call status model with
   GRC semantics, null-omission and identifier-type rules, the three fixtures, known limitations
   (including: `streetWidth` here is PAVED width — killed for ZR wide-street use by the
   street-width pilot; advisory only).

4. **`services/api/tests/connectors/test_geoclient_address.py`** — 36 tests, S1..S8 of the
   packet, all offline through the injected seam. Anti-tautology discipline throughout:
   expected values are loaded from the fixtures and compared, never restated as literals.
   Constructed variants are labeled CONSTRUCTED in code. S6 exercises success, ambiguity,
   rejection, 401, timeout and malformed paths with a sentinel key and asserts the sentinel
   appears in no outcome, exception, payload, or captured log record (connector and transport
   loggers both captured at DEBUG).

## Scenario coverage

S1 normal (3 tests: fixture-loaded field equality + provenance completeness/key-absence +
header-only auth with key-free URL); S2 both-sub-calls (constructed grc2 failure never a clean
success + 4-way parametrized pair table); S3 ambiguity (recorded EE with verbatim suggestions +
constructed 11 not-found); S4 rejection (recorded 42, partial data transported); S5 failures
(timeout budget, 401/403 immediate + key/body-free, 500, 429, 4 malformed bodies, invalid input
with zero network calls); S6 key hygiene (leak-absence harvest, env-read at call time, missing
key typed with zero network); S7 offline + integrity (3 fixture sha256 checks + default-transport
unreachable before the key check); S8 honesty (null omission → None, invalid-shape GRC 5-way
parametrized fail-closed, valid-shape unknown code → rejected, identifier types verbatim).

## Self-checks (executed by the producer, this worktree)

- `pytest tests/connectors/test_geoclient_address.py -q` → **36 passed**
- `pytest tests/connectors -q` → **375 passed** (no regression in the five existing connectors)
- `ruff check` on both new files → clean
- `python tools/modularity_check.py --check` → no findings on the new module (~500 lines incl.
  documentation; single responsibility: this one connector)
- `python .github/scripts/secret_scan.py` → PASS, no findings (fixtures verified key-free)

## Honest limits

- No live call is made by any test; live behavior is anchored by the three recorded captures.
- The `/v2/search` endpoint, BBL/BIN direct lookups, and the `/v2/version` health probe are OUT
  of scope (packet); so are the API endpoint and UI that will consume this connector.
- Warning-class fixtures (GRC 01) are covered by constructed variants only — no natural 01
  address was captured; the classification table is exercised, the exact 01 wire shape is not.
- CI has not run on this branch; the suite above ran locally on Python 3.11 (CI runs 3.12).
