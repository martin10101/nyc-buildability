# M1-T005 G3 — reviewer's return (verbatim preservation)

> Provenance: complete final return of the code-reviewer for M1-T005 G3, received 2026-07-16 via the agent-return channel; saved verbatim by the orchestrator (transport entity-decoding only) per the report-preservation rule in `.claude/rules/project-control.md`.

---

All evidence is gathered. Per ADR-005 and `.claude/rules/project-control.md`, I am read-only: I return the full gate report content here for the orchestrator to save as `project-control/reports/M1-T005-G3-review.md` and to record in the ledger. (The task prompt asked me to write the file; the standing process decision assigns file-saving to the orchestrator, so I am returning the content instead.)

---

# GATE REPORT — M1-T005 — G3 independent walkthrough

- **Task:** M1-T005 — Property-profile API v1: GET /api/v1/properties/{bbl}
- **Gate:** G3 (human-style walkthrough, downstream-consumer perspective: Priority 4 browser property screen)
- **Reviewer:** code-reviewer (independent; producer = backend-engineer)
- **Date:** 2026-07-16
- **Review location:** `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M1-T005`, branch `task/M1-T005-property-profile-api`, commit `555db54`
- **Order followed:** task packet S1–S8 → implementation (`properties.py`, `builder.py`, `pluto_soda.py` hardening diff, `main.py`, tests) → contracts (`property_profile.schema.json` + PRD §9/§12/§32.3) → producer report last. G2 evidence adjudication items ruled on below.

## VERDICT: **PASS** — 1 medium defect (D1) required as immediate one-line rework or bundled into the next task; 1 mandatory follow-up task (contract v1.1); remainder are carry-forwards for the Priority 4 screen.

## 1. Reproduction (all commands from the worktree)

| Step | Command | Expected | Actual |
|---|---|---|---|
| Full suite | `cd services/api && python -m pytest tests -q` | 140 passed | **140 passed in 1.57s** |
| Contracts validator | `python .github/scripts/validate_contracts.py` | 0 failures | **Checked 6 schema file(s); 0 failure(s)** |
| Contracts untouched | `git diff main -- packages/contracts` | empty | **empty** |
| Commit hygiene | `git show 555db54 --stat` | all inside allowed paths | **11 files, all within `allowed_paths`; no contracts, no large artifacts (+1609 source lines)** |

Hands-on TestClient walkthrough (fixture transports, real `fetch_by_bbl`, real route, real builder — not the producer's tests):

- **Normal (F01, `1000010100`)**: 200, `X-Correlation-ID` present. Body is legible cold to a frontend dev: `identity` (bbl/address/geometry Point in GeoJSON lon-lat order), `lot_facts`/`existing_building_facts` as `{value, units?, provenance_ref, coverage_status}`, `zoning` (districts `["R3-2"]`, special `["GI"]`, mapped_features with per-feature provenance), `provenance` (67 source_fact records), `missing_inputs`, `conflicts`, `data_completeness`, `reproducibility`. Coverage labels observed: `conditional` only — exactly PRD §12 vocabulary and inside the `coverage_status.schema.json` enum.
- **Decimal BBL** `1000010100.00000000`: 200; connector called with canonical `1000010100` only; raw serialization preserved in provenance `original_value`.
- **Malformed** `1-00001-0100`: 422, `state=validation_error`, typed `code=non_numeric`, repr-sanitized raw_value, zero connector calls.
- **No-match condo** (F02b, `1000041001`): 404, `state=no_match`, message contains the BILLING lot 7501–7599 explanation with README/research citation — genuinely actionable for a user.
- **Conflict** (synthetic borocode=3 on F01): 200; `conflicts[0]` shows both values verbatim (`1` BBL-derived, `"3"` record verbatim), `resolution=unresolved`; `lot_facts.borocode`/`bbl` = `data_conflict`; unaffected `lotarea` stays `conditional`; `identity.address` correctly refuses to assert Brooklyn (no borough/borough_code emitted).
- **Failures**: 429×3 → 503 `rate_limited`; timeout×3 → 504 `timeout`; network×3 → 503 `source_unavailable`; F13 drift → 502 `schema_drift` distinct status+state. Details carry only attempts/url/error_code — no token, no traceback, no header material (verified in bodies).
- **Determinism**: double fetch `json.dumps`-identical after removing exactly `generated_at` + `correlation_id`.

## 2. Defects

- **D1 (Medium)** — `services/api/app/api/v1/properties.py:231-253`: `_drift_monitor_hook()` and `build_property_profile()` run OUTSIDE the route's `try/except`. Any exception there (builder `RuntimeError`/`ValueError`, future builder bug) bypasses the documented 500 contract: I reproduced (monkeypatched builder raise, `TestClient(raise_server_exceptions=False)`) a plain-text `Internal Server Error` with **no `state=internal_error` body and no `X-Correlation-ID` header**, and Starlette's default handler logs the full traceback including `str(exc)` — which the route's own comment forbids because exception chains may embed untrusted upstream strings (F5 policy). No client-side leak observed (`secret-internal-path` canary absent from body). Currently unreachable by construction (integrity assert cannot fail for connector-built facts; route pre-checks `no_match`), hence Medium not High. **Fix sketch:** move steps 3 (hook + builder + 200 response) inside the existing `except Exception` scope, or wrap them in an equivalent handler. One-line-class change; the existing `test_s5_unexpected_exception_is_500...` pattern extends trivially to a builder-raise variant.
- **D2 (Low, contract debt — resolves via follow-up task, not rework)** — the three additive keys are undocumented in the canonical contract; see Adjudication #1. The Priority 4 frontend must not be built against undocumented keys.
- **D3 (Low)** — `missing_inputs` emits 42 boilerplate entries for every absent PLUTO column including non-feasibility admin columns (`firecomp`, `sanborn`, `policeprct`, `healtharea`…). Explicit-over-silent is correct, but this is UI noise; the Priority 4 screen needs either a builder-side relevance filter (documented policy) or a frontend filter. Carry-forward.
- **D4 (Info)** — `zoning.districts`/`commercial_overlays`/`special_districts` are plain strings with no direct `provenance_ref` (schema v1 shape); provenance is joinable only via `provenance[].original_field_name` (`zonedist1`…). The schema's own description says free strings here "must carry provenance". Fold into the contract v1.1 task (D2).
- **D5 (Info)** — S1 schema validation uses `pytest.importorskip("jsonschema")`: in an environment without jsonschema the contract-validation test silently skips. It ran here (140 passed, 0 skipped). Ensure CI keeps jsonschema in dev deps.
- **D6 (Info, environment)** — owner PC runs Python 3.11.9; `services/api/pyproject.toml` requires `>=3.12`. Suite passes on both; note only. (Redirect-handler completeness is unaffected: CPython ≥3.11 routes 301/302/303/307/308 through `redirect_request`; on the 3.12 floor, 308 is covered.)

## 3. The five G2 adjudications

1. **Additive contract keys — RULING: acceptable, WITH a mandatory contract minor-version follow-up task; NOT a needs_split violation and NOT rework.** Grounding: `property_profile.schema.json` sets `additionalProperties: false` nowhere (root, `$defs/fact_value`, identity — all open), so draft-2020-12 semantics admit the keys; the required v1 field set is emitted unchanged, and I confirmed the untouched schema validates the live response (S1 re-run + hands-on). The keys extend the ONE canonical document rather than creating a competing schema, so PRD §32.3's actual prohibition ("modules may not invent competing property schemas") is not violated; the emitted `coverage_status` values (`conditional`/`data_conflict`/`unsupported`) and `data_completeness` values sit exactly inside the existing `coverage_status.schema.json` enums, so no vocabulary was invented either. Precedent: M1-T002's additive `source_fact` provenance keys were approved at its G1. The packet's stop rule ("schema lacks a needed field → STOP") reads on missing capability; an open schema that already admits and enum-grounds these keys does not lack the capability. HOWEVER: leaving PRD §12-mandated statuses as undocumented extensions is exactly the §32.3 hazard for downstream consumers — **spawn a contract task (v1.1.0, additive): `$defs/fact_value.coverage_status` → `$ref coverage_status.schema.json`, top-level `data_completeness` → `$ref …#/$defs/data_completeness`, `reproducibility` object, and district provenance linkage (D4). This task must be accepted before the Priority 4 screen consumes those keys.**
2. **404-for-no_match; drift→502, timeout→504 — ACCEPT.** 404 with machine-readable `state=no_match` + condo explanation is conventional REST for a nonexistent resource, distinguishable from routing 404s, and honors the "result, not error" carry-forward (the body carries source/dataset ids, request_url, retrieved_at). 502 for schema drift correctly separates dataset-contract breakage from 503/504 transient classes; 424 was rightly rejected.
3. **Critical-columns policy (`lotarea`, `zonedist1`) — ACCEPT.** Clearly labeled platform completeness policy (builder.py:77-81 comment + producer report §7.5), not legal interpretation; the choice is sane (both are prerequisites to any FAR computation). Revisit when M2 formalizes completeness policy.
4. **No-auth INTERNAL/DEV condition — ACCEPT as tracked G5 condition.** Markers verified in `properties.py:3-6`, `main.py` docstring and OpenAPI description. This gate does not discharge it: G5/security-reviewer owns it, and public exposure stays blocked on M0-T007/T008 (B-001).
5. **Transport-test repointing — CONFIRMED, no assertion weakened.** `git show 555db54 -- services/api/tests/connectors/test_pluto_soda.py` shows exactly: monkeypatch target changed `urllib.request.urlopen` → `pluto_soda._OPENER` (`_FakeOpener`) in the 5 tests, plus `_FakeUrlopenResponse.read` gaining the `amt` parameter (required by the F1 bounded read; this *strengthens* fidelity to `HTTPResponse.read(amt)`). Every assertion is byte-identical to the 9e22839-lineage versions.

## 4. Test-quality audit

- **S1**: jsonschema validation is against the untouched schema (`REPO_ROOT/packages/contracts/schemas/v1` in the worktree; `git diff main -- packages/contracts` empty), resolved through a real registry with source_fact+common — not a copy, not a stub. Dangling-ref test computes the ref set independently of the builder. Good.
- **S5 token canary**: meaningful — `fetch_by_bbl` defaults `app_token` from `SOCRATA_APP_TOKEN` (pluto_soda.py:592-593) and the harness doesn't override it, so the monkeypatched canary genuinely flows into `X-App-Token` headers; leak-absence assertions are therefore live, not vacuous.
- **S4**: asserts both raw values verbatim (`{"1", '"3"'}` — type difference int/str preserved and visible) AND that unaffected `lotarea` stays `conditional`, AND identity non-derivation. Complete per packet.
- **S6**: strips exactly `generated_at` + `correlation_id`; `json.dumps` comparison covers key order. Good.
- **Coverage/confidence separation**: traced `_coverage_status()` (builder.py:117-131) — inputs are `conflict_status` and drift columns only; `confidence` appears nowhere in control flow; the S1 test proves confidence=1.0 facts stay `conditional`. `verified` is unreachable from this code. PASS.
- **Over-mocking**: low. Route tests run the real connector over fixture transports (integrative); transport tests mock only the `_OPENER` seam. No tautologies found. **Gap**: the 500-path test only covers fetcher-raised exceptions — the builder path is untested, which is how D1 slipped through.
- **F1–F4 quality**: bounded read cap 10 MiB is sane (per-BBL bodies ~1.5 KB; future 1000-record pages ~1.5 MB) and applied to both 200 and HTTPError bodies; redirect refusal is complete for 301/302/303/307/308 on the 3.12 floor and can never re-issue a request (verified single-call route test, 302 → 503 typed); sanitizer allowlist `^[A-Za-z0-9._-]{1,120}$` matches observed official dotted codes, blocks CRLF/control injection, repr-fallback verified hands-on.

## 5. Carry-forwards for the Priority 4 screen task

1. **Contract v1.1 task (from Adjudication #1/D2/D4) must land first** — frontend consumes documented keys only.
2. D1 fix (500-path wrapping) if not fixed as immediate rework.
3. D3 `missing_inputs` noise: decide filter policy (builder vs frontend), documented either way.
4. Frontend must tolerate absent `identity.address`/`geometry`/mapped-features (only present-column facts are emitted) and absent `borough` under conflict; must render 422 from `detail.code`+`message` (raw_value is repr-quoted); must treat `state` as the discriminator on non-200s (routing 404 vs `no_match`).
5. Endpoint remains INTERNAL/DEV until auth (B-001) — the screen task cannot deploy it publicly.
6. Drift monitor remains a logging stub; scheduled `check_columns_for_drift` job belongs to M2 connector-health.

## 6. Low-storage check

Source-only edits; all tests offline (fixture transports, zero network); no datasets, caches, or large artifacts written; commit adds ~1.6k source lines. Compliant.

---

**Final summary for the orchestrator**

- **Verdict: PASS** (140/140 reproduced; all S1–S8 walked hands-on; contracts untouched; hygiene clean).
- **Defects:** D1 Medium — builder/hook exceptions escape the documented 500 contract at `properties.py:231-253` (plain 500, no state/correlation header, Starlette logs full traceback contrary to F5 policy); reproducible, one-line-class fix. D2 Low — additive keys undocumented in contract (→ v1.1 task). D3 Low — 42-entry `missing_inputs` boilerplate noise. D4/D5/D6 Info — district strings lack direct provenance_ref; jsonschema importorskip; local Python 3.11 vs 3.12 floor.
- **Adjudications:** #1 additive keys ACCEPTABLE with mandatory contract-v1.1 follow-up task before Priority 4 consumption (schema is open, required set intact, enum-grounded values, M1-T002 precedent; needs_split not triggered); #2 404/502/504 mappings ACCEPT; #3 critical-columns policy ACCEPT as labeled platform policy; #4 no-auth condition ACCEPT as tracked G5 condition (B-001); #5 repointed transport tests CONFIRMED — no assertion weakened, only the monkeypatch seam moved.
- **Test quality:** strong and genuinely integrative; S1 validates against the untouched schema; S5 canary is live; one gap (builder-path 500) which is exactly defect D1.
- **Carry-forwards:** contract v1.1 task, D1 fix, missing_inputs filter policy, frontend tolerance rules, auth condition, M2 drift monitor.

Key files: `...\.claude\worktrees\M1-T005\services\api\app\api\v1\properties.py`, `...\services\api\app\profile\builder.py`, `...\services\api\tests\api\test_properties_v1.py`, `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\packages\contracts\schemas\v1\property_profile.schema.json`.
