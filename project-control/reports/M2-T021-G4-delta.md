<!-- Reviewer return preserved VERBATIM by the orchestrator (report-preservation rule,
.claude/rules/project-control.md). Reviewer: independent qa-engineer subagent
(G4 delta re-review), returned 2026-09-11, reviewed HEAD 96c398aa. -->

All six verification items are confirmed. I have everything needed. Here is my delta-review report.

---

VERDICT: PASS

# G4 Delta Re-Review — M2-T021 (Geoclient v2 address-resolution connector)

- Reviewed HEAD SHA: **96c398aa** (ancestors: `7a43d2d0` records ← `01c01c5f` producer ← `86c88ec1` eb6a15f8-based re-review collection). Both correction commits confirmed as ancestors of the reviewed HEAD.
- Prior round (eb6a15f8, `M2-T021-G4-rereview.md`): PASS, no blocking corrections. This is a delta review of the round-2 correction only.
- Independently recomputed collected-case count: **99** (was 98; +1 from `deepnest600`).
- Discipline: read-only (ADR-005). Static analysis, read-only git, `python -c` probes with `PYTHONDONTWRITEBYTECODE=1`. No pytest, no ruff, no repo writes — **CI is the execution authority**. Sandbox interpreter is CPython 3.11.9 (CI is 3.12); noted where relevant.

## 1. `deepnest600` case — PASS
- Body construction (`'{"address": {..."a": ' + "[" * 600 + "]" * 600 + "}}"`) reconstructed via probe: valid JSON, 2 balanced braces, 600 balanced brackets, top key `["address"]`, address keys `["a","geosupportReturnCode","geosupportReturnCode2"]`, **total nesting depth 602** (top dict → address dict → 600-deep list). This is ~600-deep nesting inside `{"address": {...}}`, and the `{"address": {...dict...}}` shape passes the line-682 shape gate, so control reaches the guard rather than the shape branch.
- The case is inside `test_s5_malformed_200_bodies_fail_closed`, which asserts `pytest.raises(MalformedResponseError)` — the **typed** error.
- Robustness across break-points independently verified against source: `json.loads` RecursionError is caught at connector L676→`MalformedResponseError`; `copy.deepcopy` and `canonical_json_digest` RecursionError are caught by the new guard at L706→`MalformedResponseError`. All three break-points map to the typed error. Probe at default limit (3.11.9) shows `json.loads` accepts depth 600 (C scanner), `deepcopy` raises RecursionError first, `json.dumps` accepts — so on this interpreter the guard's first statement (deepcopy) trips and is caught. Consistent with the "whichever layer breaks first" claim.
- Non-blocking note (not a finding): the case still relies on *some* layer exceeding the recursion budget at depth 600. On CPython (default limit 1000) pure-Python deepcopy consumes several frames/level, so depth 600 has a very wide margin; the producer red/green confirms it breaks on CI's 3.12. The comment "cannot rot if recursion limits differ" is robust to *which* layer breaks, and in practice robust to the limit given the margin.

## 2. Red/green record (report §3.1/§3.4) — PASS (cannot re-execute; stated)
- RED: connector reverted to eb6a15f8, `pytest ... -k deepnest600` → `FAILED ... RecursionError: maximum recursion depth exceeded` (1 failed, 98 deselected). GREEN: fix restored → module `99 passed`.
- Coherence verified against source I can read: eb6a15f8 lacks the deepcopy/canonicalization guard (its `raw_fields=copy.deepcopy(address)` / `canonical_json_digest(parsed)` run unguarded during outcome construction), and eb6a15f8 already catches RecursionError at `json.loads` — so a depth-600 body escapes as an untyped RecursionError from deepcopy, which is exactly what the RED records. My probe reproduces the deepcopy RecursionError at depth 600. The revert isolates only the production fix while keeping the new test — correct revert-proof methodology, specific in command, failure type, and counts.
- The RED counts independently corroborate the collected total: 1 selected (`deepnest600`) + 98 deselected = **99** collected, matching my AST recount.
- I could not and did not re-execute pytest (read-only; CI authority). The recorded pair is coherent and specific enough to serve as the revert-proof.

## 3. Removed S1 assertion — PASS (assertion-honesty, not weakening)
- Removed lines were exactly: `res.raw_fields["bbl"] = "MUTATED"` and `assert _fixture_address(G01)["bbl"] == addr["bbl"]`.
- Vacuity re-derived independently: `_fixture_address(name)` = `json.loads(_fixture_body(name))["address"]` — a **fresh** parse each call. `addr` (fixture A) and the re-read `_fixture_address(G01)` (fixture C) are both independent of `res.raw_fields` (deepcopy B). Mutating B cannot affect A or C; and even under aliasing (`raw_fields = address`) the mutation would hit only the connector's local, already-returned parse. The assertion `C["bbl"] == A["bbl"]` compares two independent reads of the same on-disk fixture — always equal, regardless of the copy behavior. It could not fail; vacuous with respect to its stated purpose.
- `assert res.raw_fields == addr` (L169) remains and is genuine coverage (fails if any field were dropped/altered). No coverage that was ever actually exercised is lost — honest deletion.

## 4. RecursionError guard — PASS (no legitimate path masked; no body leak)
- Guard wraps only `copy.deepcopy(address)` + `canonical_json_digest(parsed)`, catches **only `RecursionError`** (not broad `Exception`), and runs **after** the shape gate (L682). A well-formed Geoclient address (flat scalar dict) never approaches the recursion limit, so a legitimate success path can never raise RecursionError and can never be masked. Happy-path values are identical (deepcopy + digest computed once, then passed as `raw_fields`/`response_digest`).
- Detail payload = `{"url": url, "body_chars": len(response.body)}` — URL (already gate-established as key-free; key is header-only) plus an integer length; **no body content**. Message is a static string. `from None` drops body-laden recursion frames from the traceback. No content leak.

## 5. Regression surface — PASS
- `git show --name-only` under `services/api`: `01c01c5f` touched only `app/connectors/geoclient_address.py` (production) and `tests/connectors/test_geoclient_address.py` (test); `7a43d2d0` touched nothing under `services/api`. The sole production change is the guard plus non-behavioral docstrings/comments. Other files in the commits (`geoclient.json` registry, producer report, `MVP_AGENDA.md`, `B-004` blocker, evidence-map) are outside `services/api`.

## 6. Executability statics — PASS
- `ast.parse(..., feature_version=(3,12))` succeeds for both changed files; no 3.12-only grammar present (parsed cleanly on 3.11.9 with the 3.12 feature flag).
- Max line length: connector 89, test 87 — **no line exceeds 100 chars** (the concatenated deepnest body is split across two sub-100 string literals).
- Parametrize ids deterministic: `deepnest600` ids are 5 distinct string literals; `test_s8_provenance_is_complete_on_every_status` ids are the 6 distinct status strings from `_status_bodies()`; all other parametrize ids are literal string lists.

## Collected-case recount detail (AST-expanded, product of stacked parametrize)
- 49 module-level test functions, no test classes.
- 48 functions resolve statically to a running total of **93** (includes the cartesian `test_s8_invalid_shape_grc_fails_closed_on_either_side` = 2×6 = 12, and `test_s5_malformed_200_bodies_fail_closed` = **5** after the +1).
- 1 function uses computed argvalues `_status_bodies()` → its literal helper returns exactly **6** tuples (one per `RESOLUTION_STATUSES` member; ids match).
- Total = 93 + 6 = **99**. Cross-checked by the producer's `-k deepnest600` RED (1 selected + 98 deselected = 99).

## Verdict
All six delta-verification items pass. The delta's only production change is a fail-closed typed guard that preserves happy-path behavior and leaks no body content; the new test case genuinely exercises the defect (revert-proof recorded and mechanistically corroborated); the removed S1 assertion was provably vacuous and its deletion loses no real coverage; the collected-case count is independently **99**; and executability statics are clean.

**VERDICT: PASS** — reviewed HEAD `96c398aa`, collected cases `99`.

*Limitation:* I did not execute pytest/ruff (ADR-005 read-only; CI is the execution authority). My conclusions rest on static analysis, read-only git, and `python -c` probes on CPython 3.11.9; the producer's recorded `99 passed` / `438 passed` / ruff-clean / modularity-exit-0 self-checks must be confirmed green by CI at `96c398aa` before acceptance.

Relevant files (absolute):
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/services/api/app/connectors/geoclient_address.py`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/services/api/tests/connectors/test_geoclient_address.py`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/reports/M2-T021-producer-report.md`
