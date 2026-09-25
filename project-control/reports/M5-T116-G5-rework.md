# M5-T116 — G5 delta re-review, rework round 2 (security-reviewer "sec-t116", read-only)

> Transmission history: pinned at ab9001ea (delta = c903307e, identity 23fd4149), delivered as two SendMessage
> parts ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags
> removed only). Verdict PASS: GEOS sees only the prepared, bounded
> ring; the full shapely error family is typed; ADVISORY-1 closed.

---

M5-T116 G5 DELTA RE-CHECK (read-only, sec-reviewer) — PART 1/2

PIN: HEAD ab9001ea7ccdf3265d77303af115eb6438737533 (matches expected). Delta material c903307e (cherry-pick of wt e94deb0c); `git show --stat` = exactly the 3 allowed paths (export_service.py, test_export_service.py, producer-report.md). Read-only deps + main.py byte-unchanged vs my prior-reviewed 99c8457f (empty diff-stat). EVIDENCE (cwd services/api): `ruff check .` -> All checks passed; `pytest tests/cad -q` -> 464 passed (was 458; +6 tests). shapely already admitted (massing_guards.py:21 imports it; 2.0.7) -> ZERO new dependency; material = 3 files only, no requirements/lockfile change. UNMOUNTED (main.py unchanged, no `export` ref).

The delta inserts `_reject_non_simple_ring(ring)` (export_service.py:391-413) into `_build_prism_mesh`, run on the PREPARED ring AFTER `triangulate_polygon` returns and BEFORE the mesh build. Findings by your four questions:

1. GEOS INPUT SAFETY (PASS). The gate runs on the ring `triangulate_polygon` RETURNS, and that call runs FIRST — `_prepare_ring` enforces finiteness (triangulation.py:114), the 1e8 magnitude bound (:118) and the 1000-vertex cap (:102), and RAISES (caught by `_render_glb`) before it can return. So `LinearRing(ring).is_simple` only ever sees a <=1000-vertex, all-finite, |coord|<=1e8, quantized, distinct, non-collinear CCW ring. GEOS/shapely never sees non-finite or over-cap input on this path.

2. EXCEPTION TYPING / NO LEAK (PASS). `except (ShapelyError, ValueError)` — ShapelyError is shapely's BASE class, covering the whole GEOS family (GEOSException, TopologicalError, GeometryTypeError, DimensionError, EmptyPartError, ...), the same family massing_guards._wrap_geos_errors relies on; ValueError covers constructor-arity errors. Both re-raise `MassingModelError(reason="self_intersection")` with a FIXED message; the `if not is_simple` branch likewise. `_render_glb` catches MassingModelError and `_reconcile_triangulation` uses ONLY `exc.reason` (fixed code) — never `str(exc)` nor the chained `__cause__` — so no GEOS message and no caller coordinate reaches the one redacted refusal. Proven: `test_distinct_vertex_bowtie_is_a_reconciled_typed_refusal` asserts the detail is the fixed `(reject_code=self_intersection)` string with the bowtie coordinates ABSENT. No untyped escape is reachable: on the proven-clean prepared ring, `.is_simple` raises only ShapelyError/ValueError (a TypeError is unreachable — every coord is a float 2-tuple).

(continues 2/2)

---

M5-T116 G5 DELTA RE-CHECK — PART 2/2 — VERDICT

3. RESOURCE COST OF THE GATE (PASS). Per request: one `LinearRing` construction (O(n) copy) + one `is_simple` predicate on n<=1000 vertices. GEOS isSimple is ~O(n log n) (monotone-chain index); even a naive O(n^2)=1e6 at n=1000 is sub-millisecond, and negligible beside the ear-clipper's ~498,501 already-budgeted units at that cap. No amplification, no DoS; cost bounded by the same 1000-vertex cap proven in round 1.

4. ADVISORY-1 CLOSED (YES). The distinct-vertex crossed bowtie that in round 1 ear-clipped to completion and produced a valid-but-self-overlapping glTF is now REFUSED: `is_simple == False` -> typed `self_intersection` MassingModelError -> reconciled to the one redacted ExportRefusal (or, for a bowtie the ear-clipper stalls on, the triangulator's own self_intersection — both land on the same refusal). The gate runs on the PREPARED ring, i.e. the exact geometry that would be rendered (a uniform local-origin translation preserves simplicity), which is the correct surface — and a SIMPLE concave L/U footprint has `is_simple == True`, so it still exports (round-1 concave/L/U tests remain green in the 464-pass run). Mutation `test_simplicity_gate_dropped_lets_a_bowtie_through` proves the gate is load-bearing (dropping it lets the bowtie through as a valid ExportResult). The gate ONLY refuses — it never alters a produced mesh — so convex/concave GLB bytes are unchanged from round 1, and DXF/PDF + owner samples stay byte-identical. The G3 A1 change is a doc NOTE plus `test_glb_footprint_vertex_cap_1000_accepted_1001_refused` (1000 -> valid glTF, 1001 -> `over_cap_vertices`), no behavior change.

INFO (non-blocking): the `except` omits TypeError; it is unreachable on the proven-clean prepared ring, so no untyped-escape exposure exists today — revisit only if a future change ever feeds `_reject_non_simple_ring` a RAW (unprepared) ring. Prior deferred surfaces (tenant/auth, private storage, log redaction at the PKT-H mount — M5-T109 A3 / T112 INFO-2) are untouched.

SUMMARY: the round-2 delta closes ADVISORY-1 with an in-scope GEOS simplicity gate that sees only clean bounded input, catches the full shapely error family, leaks no caller text or GEOS message, costs O(n log n) at n<=1000, and refuses without mutating any mesh. Zero new deps; UNMOUNTED; ruff clean; tests/cad 464 passed; DXF/PDF byte-identity preserved. No CRITICAL/HIGH/MEDIUM.

M5-T116 G5 VERDICT: PASS

END-OF-REPORT
