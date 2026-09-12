<!-- Reviewer return preserved VERBATIM by the orchestrator (report-preservation rule,
.claude/rules/project-control.md; transport entity-decoding applied: &amp; -> &, &lt; -> <, &gt; -> >).
Reviewer: independent qa-engineer subagent (G4 delta), returned 2026-09-12, reviewed HEAD e40c87c4. -->

All verification complete. Returning the delta gate report.

---

VERDICT: PASS

# G4 QA Delta Gate Report — M2-T022 (address-resolution API endpoint)

- **Task:** M2-T022 — GET /api/v1/address-resolution
- **Gate:** G4 (QA — coverage & executability of `services/api/tests/api/test_address_resolution_api.py`). DELTA round following the FAIL-on-B1 wave at `ec4b75dc`.
- **Reviewed HEAD:** `e40c87c4` (resubmit pointer at content `803d5606`; branch `candidate/D-024-mrl-option-b`). Confirmed `e40c87c4` vs `803d5606` is control-plane-only (`reports/M2-T022.json`, `state.json`, `tasks/M2-T022.json`) — no source/test drift, so content review at `803d5606` == review at `e40c87c4`.
- **Reviewer:** qa-engineer (independent). Read-only per ADR-005; no pytest/ruff executed. Static + read-only git + `python -c` probes (`PYTHONDONTWRITEBYTECODE=1`). Ruff outcome grounded in `origin/main` CI-green ground truth, not by executing ruff.
- **Recomputed collected count (AST at reviewed HEAD): 27** — 19 `def test_` functions; two parametrized (`test_s4_typed_failures_map_to_documented_pairs` ×6 via `_FAILURES` [6 items], `test_s4_hostile_retry_after_is_dropped_never_echoed` ×4 [4 items]); 17 + 6 + 4 = **27**. Matches the producer's claim and the revert-proof arithmetic (26 deselected + 1 selected = 27).

## B1 re-adjudication (explicit)

**I ACCEPT the correction of B1's ruff-outcome claim, and I formally REVERSE my prior round's "producer made a false evidence claim" assessment.**

- **Raw-length conformance restored (objective):** at HEAD, `address_resolution.py` (508 lines) and `test_address_resolution_api.py` (706 lines) have **zero lines > 100**. The 107-char line 361 is wrapped into a behavior-identical 3-key `detail={...}` dict. With the line now ≤ 100, ruff E501 cannot fire regardless of the exemption debate — the ambiguity class is removed outright.
- **Captured evidence credibility (`M2-T022-ruff-evidence.txt`):** version `ruff 0.13.0` matches the pin in `requirements-tools.lock` (`ruff==0.13.0`); cwd `services/api` and config (`pyproject.toml`, `line-length=100`, `select=["E","F","I","UP","B"]`, no `ignore`/`per-file-ignores`) match both the actual pyproject and the CI `api` job (`working-directory: services/api` → `ruff check .`). The stated exemption mechanism ("ruff E501 exempts lines whose overflow past the limit contains no whitespace — the URL token") is **independently corroborated from `origin/main` ground truth**, not merely accepted: `origin/main services/api/app/main.py:105` (104 chars, `...-> Response:  # type: ignore[no-untyped-def]`, unbreakable token straddling cols 82→103, no whitespace after col 100) is accepted, merged, and ruff-green under `ruff check .` — structurally identical to the disputed line 361 (URL token straddling cols 47→106, no whitespace after col 100). Two further origin/main lines pass at 114 and 106 chars (`transport.py:171`, `:453`) via the trailing-comment sub-case. Ruff 0.13.0 demonstrably tolerates this class.
- **Why my prior FAIL was wrong:** (a) my assertion "multi-chunk line, so ruff's single-word/URL exception does not apply" mis-stated ruff's rule — the exemption is not limited to whole-line single words; and (b) my "E501 enforced repo-wide / every accepted file conforms" corroboration scanned only `app/api` + `tests/api` and missed the accepted >100 lines in `app/main.py` and `app/resilience/transport.py` that reveal ruff's real tolerance. Consequently the documented command did **not** fail at `ec4b75dc` and the producer's "ruff … All checks passed" self-check was **TRUE**. B1's raw-length observation was a legitimate cleanup (the wrap is a strict improvement), but its impact claims (ruff fails / documented command fails / false producer claim / fails G1) do not hold.

## Delta verification (all PASS)

1. **New test `test_s1_production_wiring_default_resolver_reaches_the_connector` (G1 HIGH-1 pin):** calls `app.dependency_overrides.clear()` so `Depends(get_address_resolver)` resolves to the REAL `_default_resolver` (confirmed `get_address_resolver()` returns `_default_resolver`); monkeypatches module-global `resolve_address` with a recorder; asserts the production path forwards `(house_number, street, borough, zip_code)` faithfully with `extra == {}` (no budget/transport — C4 duty 3) and one transport call. **Revert-proof coherent:** the route calls `resolver(house_number, street, borough=…, zip_code=…)` positionally; the old `_default_resolver(**kwargs)` raises TypeError → non-200, so the single selected test fails while 26 of 27 are deselected — arithmetically and mechanically consistent with the recorded `[1 failed / 26 deselected]`.
2. **New test `test_s6_input_echo_is_a_named_reflected_surface` (G3 pin):** hostile `<script>alert(1)</script>` street + `7<b>7` house number asserted byte-exact in `input_echo` (route emits `outcome.street_in`/`house_number_in` verbatim at route line 375-379 — non-vacuous), plus `"input_echo" ∈ unsanitized_reflected_input.fields` and a `source_facts[]`-prefixed field present. The route's `_REFLECTED_INPUT_WARNING.fields` now leads with `input_echo` and names the two `source_facts[]` values — matching the assertions.
3. **Matrix set-equality (10 pairs):** the test's `emitted` set is exactly 10 pairs including the documented-unreachable `(503, "request_budget_exceeded")`; the route's `STATUS_STATE_MATRIX` is also exactly 10 pairs including that member; `assert emitted == set(STATUS_STATE_MATRIX)` pins both directions. Coherent; the unreachable pair is intentionally undriven (S8 — no budget is ever passed), consistent with the prior non-blocking observation 2.
4. **No weakening / no writes / statics clean:** 0 test functions removed, exactly 2 added (the only other test-file change is the behavior-identical line wrap); no repo-write patterns (`open('w')`/`write_text`/`write_bytes`/`mkdir`/`shutil`) in the test; both changed files `ast.parse` OK on Python 3.11 (no 3.12-only syntax); zero lines > 100; parametrize ids deterministic.
5. **Scope:** `803d5606` touches exactly route + test module + producer report (3 files); `e40c87c4` adds only the 3 control-plane files. In scope.

## Non-blocking notes (not gating)

- The route grew to 508 lines; the rework's route delta is small (resolver signature + docstring/comment corrections + one matrix line). Modularity is G1's remit, not G4 — flagged only for awareness.
- The G4 non-blocking observations 1-3 from the prior round remain accurate and are unchanged by this rework (deliberately, per the producer report).

---

Return to orchestrator: **G4 = PASS**, reviewed HEAD `e40c87c4`, recomputed collected count **27**. B1 disposition: raw line wrapped (zero lines > 100 in both files), and B1's ruff-outcome claim is corrected — I accept the correction and reverse my prior "false producer claim" assessment, corroborated independently from `origin/main` CI-green >100-char lines (notably `main.py:105`). All delta items (two new tests, 10-pair matrix, no weakening/writes, statics, scope) verified sound.

Relevant files (absolute):
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/services/api/app/api/v1/address_resolution.py`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/services/api/tests/api/test_address_resolution_api.py`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/services/api/pyproject.toml`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/services/api/requirements-tools.lock`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/.github/workflows/ci.yml`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/reports/M2-T022-ruff-evidence.txt`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/reports/M2-T022-G4.md` (prior round)
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/reports/M2-T022-producer-report.md`
