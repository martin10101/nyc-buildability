# M5-T074 — [ORCH-HARVEST] G4 body-widening mutant capture (orchestrator, 2026-09-23)

Pre-captured for the G4 reviewer per the producer report's "For the gate" instruction and the
DB-046 precedent (reviewers are read-only; the orchestrator captures executable evidence —
`.claude/rules/project-control.md` evidence-capture division). cwd `services/api`, primary
checkout, tree clean at the reviewed head.

1. **Baseline:** `python -m pytest tests/api/test_outline_bridge.py -q` → **42 passed**.
2. **Mutant applied:** one field added to the production `_internal_error_500` body
   (`app/api/v1/outline_bridge.py` :605–614): `"detail": "MUTANT-widened-field"`.
3. **Mutant run:** `python -m pytest tests/api/test_outline_bridge.py -q -k "test_500_"` →
   **4 failed, 38 deselected** — ALL FOUR live-500 tests reddened:
   - `test_500_fetch_stage_internal_defect_is_bounded_generic` FAILED
   - `test_500_ring_crs_mismatch_display_side_is_bounded_generic` FAILED
   - `test_500_ring_crs_mismatch_authoritative_side_is_bounded_generic` FAILED
   - `test_500_serialization_unsafe_tail_guard_is_bounded_generic` FAILED
   Failure locus (observed verbatim in the fetch-stage test's traceback):
   `assert set(body) == _GENERIC_500_KEYS` →
   `AssertionError: assert {'correlation...age', 'state'} == frozenset({'c...ge', 'state'})`
   — the shared oracle's exact-shape check is the tripwire, as designed.
4. **Restore:** `git checkout -- app/api/v1/outline_bridge.py` (plain checkout restore);
   re-run `python -m pytest tests/api/test_outline_bridge.py -q` → **42 passed** (green
   candidate restored; production byte-identical to the reviewed head).

Conclusion for G4: the leak gate is LIVE — any widening of the generic-500 body is caught by
all four tests via the exact-shape oracle. The AS-2 leak-absence claim is mutation-backed,
not assertion-only.

END-OF-REPORT
