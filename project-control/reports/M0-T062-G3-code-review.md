# M0-T062 — G3 code review (VERBATIM reviewer return)

Independent reviewer: `code-reviewer` (read-only; reviewer != producer orchestrator).
Returned via agent channel; saved verbatim (transport entity-decoding only).

---

All references to M0-T056 in `tools/` are now only in the explanatory comment; no test or code depends on its membership. Verification complete.

---

# G3 Independent Code Review — M0-T062

**Task:** Directive-compliance hygiene — (a) drain inert `M0-T056` from `_EMPTY_IDENTITY_GRANDFATHERED`; (b) add O1 `path_free_justification` fail-closed regression tests.
**Reviewed SHA:** `e2ab6dec97af2f973d5cc9294a681a4cd63c58f6` (confirmed `git rev-parse HEAD` in worktree == reviewed SHA).
**Diff scope:** `tools/validate_directive_compliance.py` (comment + frozenset, net −1 member), `tools/test_directive_compliance.py` (+3 tests), plus a new producer report. No production runtime code path changed; task-packet `additionalProperties` untouched.

## 1. Safety of the drain — VERIFIED SAFE
- `_validate_empty_identity` (worktree lines ~314–325): the sequence is `if entries or cp_entries or opted_in: continue` **then** `if tid in _EMPTY_IDENTITY_GRANDFATHERED: continue`. The membership test is reachable only when a task's paths resolve to zero tracked files. Confirmed by source.
- M0-T056's `allowed_paths` = 7 `tools/agent_supervisor/*.py` + `tools/test_agent_supervisor_model_turnover.py`, all `git cat-file -e e2ab6de:<path>` → TRACKED. Direct manifest resolution at e2ab6de: **non-cp entries = 7** (`e1=None`), so M0-T056 resolves **NON-EMPTY** and hits the `if entries…: continue` guard before the membership test. The drained entry was inert; removing it changes no behavior for M0-T056, and c17 now fails closed on it live if its paths were ever emptied.
- FYI (out of scope, pre-existing, non-blocking): M0-T056's 8th path `project-control/reports/M0-T056-producer-report.md` is NOT tracked at e2ab6de (cp entries = 0). This is a M0-T056 packet condition, not introduced by M0-T062, and is irrelevant to the drain — the 7 tracked `tools/` files already make the identity non-empty. No regression path found.

## 2. `sorted(...)[0]` stability — VERIFIED
Frozenset is now `['M0-T026','M0-T032','M0-T054','M3-T002..T005']`; `sorted(...)[0] == "M0-T026"`. `"M0-T056" > "M0-T026"`, so M0-T056 was never the minimum. `test_grandfathered_task_is_not_flagged` (uses `sorted(...)[0]` as fixture id) PASSES.

## 3. O1 tests exercise the real fail-closed branch — VERIFIED with teeth
- `path_free_opt_in` (directive_registry.py ~line 1252): with `path_free_governance: True`, the guard `if not isinstance(just, str) or not just.strip():` returns `(False, <err naming path_free_justification>)`. Empty-string (`"".strip()==""`), whitespace-only, and non-string (int/`0`/`True`/`False`/`None`/list/dict) all trip it; `isinstance(True, str) is False`, so bool is str-disjoint and refused. Confirmed by source and all 3 tests PASS.
- The new assertions (`assertFalse(opted)` + `assertIn(dr.PATH_FREE_JUSTIFICATION, err)`) are correct.
- Teeth confirmed by source: deleting the `if not isinstance(just, str) or not just.strip():` line makes execution fall through to `return True, None`, flipping `opted` to `True` and failing every `assertFalse(opted)`. Non-vacuous.

## 4. Reproduced runs
- `python -m pytest tools/test_directive_compliance.py -k "path_free or grandfather or optin or empty_identity or justification" -q` → **10 passed, 110 deselected** (includes all 3 new O1 tests + grandfather test).
- `EmptyIdentityGuardTests` + `ValidatorEmptyIdentityTests` → **18 passed**.
- `python tools/validate_directive_compliance.py --check` → **EXIT 0** (registry valid after the drain; M0-T056 not flagged).
- Full-file run timed out at 5 min (suite is slow, ~37s per 10 tests) — environment/perf only, not a defect; the required `control-plane` CI job runs the full file.

## Notes (non-blocking)
- Producer report's self-check labels "18 passed (was 15)" against the `-k` subset; the exact `-k` subset actually matches **10**, while **18** is the two affected classes' total. Minor labeling imprecision in the producer narrative; the underlying evidence reproduces and all relevant tests pass.

## Conclusion
The drain is provably behavior-preserving (M0-T056 resolves non-empty; entry never consulted), `sorted[0]` invariant holds, and the O1 tests are correct and non-vacuous. Validator exits 0; all directly-affected tests pass. No enforcement regression identified.

VERDICT: PASS
