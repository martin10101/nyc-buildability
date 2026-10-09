# M5-T106 — G3 DELTA re-review, required-corrections round 2 (geospatial-engineer "geo-t106", read-only)

> Transmission history: pinned at 8273c688 (delta = 42526c66, identity 074a9f7b), delivered as two SendMessage parts
> (1/2, 2/2) ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed
> only). Verdict PASS: both residual echoes bounded, _preview never raises, huge-int typed on both paths, the second sibling
> pins the base-class catch, goldens byte-identical, public API unchanged. Forward note: 994/1000 lines.

---

M5-T106 G3 DELTA re-review (geospatial-engineer, READ-ONLY). PART 1/2 — setup + claims.

SETUP: PIN HEAD 8273c688 at start (past the pin). Delta = `git show 42526c66` (re-frozen to a102b537; frozen identity 074a9f7b). EXACTLY the 2 code files + report; proposal.py untouched (forbidden). [OBSERVED] services/api: ruff (two files + full tree) = All checks passed; pytest tests/scenario = 770 passed; test_massing_model.py = 81 passed (75 round-1 + 6 added, append-only, no existing test edited).

ALL FIVE CLAIMS VERIFIED (independent in-process probes):
- Both residual echoes now bounded. [OBSERVED] the B0 re-echo is `_preview(exc)` (massing_model.py:834): a 200k-char FOOTPRINT vertex → invalid_source, msg len 186, value elided, "chars>" marker. The no-candidate detail is `_preview(detail)` (:962): a 200k detail → no_generated_candidate, len 251, elided, marker; a short detail still surfaces. My round-1 ADVISORY-1 (A) and (B) both closed.
- `_preview` never raises (:227-236): [OBSERVED] a hostile `__repr__` (RuntimeError) and a self-recursive `__repr__` (RecursionError) both → "<unrepresentable value>"; a small value still verbatim.
- Huge-int coordinate typed non_finite on BOTH paths. [OBSERVED] lot 10**400 → non_finite/lot_ring[0] (len 181, bounded); footprint 10**400 → non_finite/proposed_massing.outline. Confirmed B0's `_is_real_number` uses bare `math.isfinite`, so `validate_proposed_massing` genuinely raises OverflowError → the new `except OverflowError` arm (:836) is load-bearing, not dead code. `_is_finite_number` now guards OverflowError (:249-258).
- Second ShapelyError sibling pins the base-class catch. [OBSERVED] GeometryTypeError (a ShapelyError, NOT GEOSException, NOT TopologicalError) → geometry_engine_error. Production wrap unchanged (already base-class); the new test reddens a narrowed `except (GEOSException, TopologicalError)`.
- Module docstring states the exact bounded set (:60-73): drops the round-1 "every" over-claim, enumerates the five bounded echoes + the never-raises property + the OverflowError→non_finite fix.

Round-2 mutation table re-checked: 6 mutants (medlot, medfoot, low1echo, detail, sibling, preview) each name a distinct reddening change; medlot/medfoot fail via "OverflowError: int too large to convert to float" escaping — a faithful discriminator.

PART 2 follows (confirmations + verdict).

---

M5-T106 G3 DELTA re-review. PART 2/2 — confirmations, notes, verdict.

CONFIRMATIONS (all pass):
- Geometry unchanged for valid input: [OBSERVED] both goldens byte-identical (recomputed b7fa9862 1-floor + e23b5cbc 5-floor with exact fixtures; test_t106_as6 green in the 770-pass run). Round-2 changes touch only refusal paths.
- Raw-vertex NYC check still runs before the collapse: [OBSERVED] the collinear x=2e6 spike still refuses lot_ring_out_of_nyc_bounds/lot_ring; `_require_raw_vertices_in_nyc_bounds` and `_prepare_ring` ordering are untouched by the delta.
- No public name/signature changed: `__all__`, `build_massing_model(lot_ring, proposed_massing, source=…, …)` and `build_from_generated_option(lot_ring, max_envelope, …)` unchanged; the delta touches only private/internal bodies (_preview, _is_finite_number, the B0 try/except, the no-candidate branch) + docstrings. M5-T107's dependency is safe.
- Docstrings now exactly true: the enumerated bounded set matches the code (pt/source/height/count via _preview; exc via _preview; detail via _preview). Every caller-input echo is either _preview-bounded or inherently bounded; no `!r}` remains. The producer also honestly scopes out level_index (independently bounded by B0's {0..N-1}, MAX_LEVELS=500).
- Modularity: [OBSERVED] 994 lines, review_signal WARNING, `modularity_check --check` exit 0, under the 1000 cap. The round-2 cohesion note is HONEST — it flags the file is ~6 lines from the hard cap and states the next packet adding a new responsibility (e.g. mesh export) must split along guards/builder/mesh with a facade rather than grow this module.

MINOR NOTES (non-blocking):
1. The NYC-bounds vertex echo (:308 `({x}, {y})`) is bounded by the finite/≤1e8 magnitude pre-checks, not _preview, and isn't in the docstring's _preview enumeration — immaterial: a huge/pasted vertex is caught as non_finite (via _preview) or coordinate_out_of_range BEFORE the NYC check, which only ever echoes finite ≤1e8 numbers, so "a huge pasted vertex cannot amplify" is exactly true.
2. FORWARD (M5-T107): the 994/1000 headroom means the wiring packet will likely breach the cap — plan the split up front, per the cohesion note.
3. proposal.py:250 `{vertex!r}` root stays D-OBS-2 for the wiring packet (correctly out of scope; the massing-layer re-echo is now bounded).

BLOCKING: none. My round-1 ADVISORY-1 is fully closed (both echoes bounded, docstring corrected to the exact set, plus a completed huge-int typed boundary and a second-sibling test). All five claims and every requested confirmation hold.

M5-T106 G3 VERDICT: PASS
END-OF-REPORT
