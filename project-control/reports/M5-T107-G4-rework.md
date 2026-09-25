# M5-T107 — G4 DELTA re-review, rework round 2 (qa-engineer "qa-t107", read-only)

> Transmission history: pinned at bf504772 (delta = 2c52ac6d, identity a367f548), delivered as two SendMessage parts
> (1/2, 2/2) ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed
> only). Verdict PASS: the M18c vacuity probe now reddens; nine new-guard mutants all caught; no existing test weakened.

---

M5-T107 G4 DELTA re-review — Part 1/2 (qa-engineer, READ-ONLY, in-memory mutation).

PIN: HEAD bf504772 at start (frozen identity a367f548; delta = `git show 2c52ac6d`). Delta baseline: from services/api the three material suites = 193 passed in 8.81s (was 180 pre-delta; +13 new tests), fully offline.

No existing test weakened: `git show 2c52ac6d` touches the three test files with ZERO removed or changed lines — every test edit is purely additive (assembler +126, api +128, connector +7). The connector production file is untouched; only scene_assembler.py and scene_api.py changed. The golden building dict still matches (clean keys / empty gaps escape to themselves), consistent with the 193-green baseline.

Advisory 1 (not-wired AST vacuity) — CLOSED and re-verified. The delta adds a traversal FLOOR to test_pkte_connector_is_unwired...: `assert len(seen) > 1` and `assert "app.api.v1.proposal_validation" in seen`. My M18c re-probe (blind `_module_path` so the BFS from app.main resolves nothing) now REDDENS with exactly "the import walk resolved nothing beyond app.main (vacuous)". Pre-delta this probe passed vacuously; it no longer can. The two active halves (connector-reachable-from-main; assembler-unwired) still redden too.

Delta production changes verified present, each backed by a displaced-value test:
- _coerce_coordinate now guards float() with try/except OverflowError (G5 F-1).
- _escape_attributes → _escape_untrusted_mapping: escapes KEYS and values; gaps[].raw, drift_signals, geometry_findings now escaped (G5 F-2 / G3 A1).
- _rate_limit_allows evicts empty/expired keys and bounds distinct keys at SCENE_RATE_LIMIT_MAX_KEYS, fail-closed at the ceiling (G5 F-3 / G3 A2).
- non-dict `context` → typed 422 field=context; None stays not_requested (G3 A4).
- HEIGHT_PROVENANCE threaded into the context layer (G1 ADV-1); ground_status_is_authoritative disclosure added (G3 A5).
- route caplog no-leak test + (500, internal_error) pairs exercised (G4 adv 2/4).

Mutation results in Part 2.

---

M5-T107 G4 DELTA re-review — Part 2/2. New-guard mutation table (in-memory, consuming namespace; CAUGHT = a delta test reddens). All 9 CAUGHT.

Requested mutants:
- DROP OverflowError guard (assembler): _coerce_coordinate → unguarded pre-fix body → build_scene_massing leaks an untyped OverflowError (no typed refusal). test_as1_overflow_guard_is_load_bearing / test_as1_huge_int... redden → CAUGHT.
- DROP OverflowError guard (route e2e): POST 10**400 → (500, internal_error). test_422_huge_int_coordinate_is_typed_not_a_500 pins (422, validation_error) field=lot_ring[0] → CAUGHT.
- ESCAPE VALUES BUT NOT KEYS: _escape_untrusted_mapping escapes only values → hostile key "<img src=x onerror=alert(1)>" survives raw in attributes_escaped. test_as3_hostile_attribute_key... asserts the raw key absent → CAUGHT.
- NO EVICTION: _evict_empty_keys → no-op → after the window expires the key ceiling stays full of dead a/b/c → a new caller "d" is refused (False) and state stays {a,b,c}. test_rate_limit_evicts_expired_keys... asserts "d" admitted and state=={"d"} → CAUGHT.
- UNBOUNDED KEY COUNT: _rate_limit_allows without the ceiling check → the 4th distinct caller at the ceiling is admitted and state grows to 4. Same test asserts the 4th refused → CAUGHT.
- CONTEXT COERCION back to {}: current guard returns (422, validation_error) field=context and does NOT reach build_scene_payload (assembly_called=0); a revert to `else {}` would yield (200, not_requested). test_422_non_dict_context_is_refused_typed pins the 422+field → CAUGHT.

Extra new guards:
- HEIGHT caveats stripped from HEIGHT_PROVENANCE → test_as1_context_height_provenance... asserts "INFERENCE" + "not height above sea level" → CAUGHT.
- ground_status_is_authoritative disclosure dropped → test_as2_ground_status_authority... KeyErrors the code lookup → CAUGHT.

Determinism: the new rate-limit tests inject `_rate_limit_clock` (fake clock) and call `_evict_empty_keys` directly — no real sleep, no wall-clock flake; caplog + 500 tests deterministic; all offline, no socket.

Assessment: every reworked guard (G5 F-1/F-2/F-3, G3 A4/A5, G1 ADV-1) and all three prior G4 advisories (1 traversal floor now non-vacuous, 2 route caplog no-leak, 4 the 500 pairs) are backed by tests that assert the displaced value and redden under an in-memory mutation. Advisory 3 (mounted include_in_schema) was informational only. No blocking findings; no existing test weakened; delta baseline 193 passed.

M5-T107 G4 VERDICT: PASS

END-OF-REPORT
