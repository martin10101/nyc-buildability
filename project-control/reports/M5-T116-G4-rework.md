# M5-T116 — G4 delta re-review, rework round 2 (qa-engineer "qa-t116", read-only)

> Transmission history: pinned at ab9001ea (delta = c903307e, identity 23fd4149), delivered as two SendMessage
> parts ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags
> removed only). Verdict PASS: the gate-removal and raw-ring mutants
> re-run RED; both round-1 advisories closed; nothing weakened.

---

M5-T116 G4 DELTA re-check (round 2, READ-ONLY) — part 1/2.

PIN: `git rev-parse HEAD` = ab9001ea7ccd at start (unchanged). Delta c903307e (cherry-pick of wt-m5t116 e94deb0c), 3 files. Harness re-run from services/api: `ruff check .` → All checks passed; `pytest tests/cad -q` → 464 passed (was 458, +6). All mutants re-run in-process via `python -c` (consuming namespace); no repo/scratchpad write (reviewer identity is read-only).

ADVISORY 1 (genuine bowtie) — NOW PROVEN REFUSED. The fix is an in-scope GEOS simplicity gate `_reject_non_simple_ring` (export_service.py:391), called inside `_build_prism_mesh` at :444 on the PREPARED ring `triangulate_polygon` returns; a non-simple ring raises the triangulator's own typed `self_intersection` MassingModelError, caught by the existing `_render_glb` handler and reconciled to the ONE redacted refusal. Uses `shapely.geometry.LinearRing(...).is_simple` (imports :69-70); any ShapelyError/ValueError also maps to self_intersection (fail closed).
- I re-verified GEOS truth in-process: is_simple → True for L, U, convex, and the CW+collinear fixture (NOT refused); False for the crossed bowtie and the figure-eight (refused). No false positive on valid concave/CW footprints.
- End-to-end: `build_export(glb, bowtie)` and `(glb, figure8)` → ExportRefusal, reject_code=self_intersection, payload keys exactly {reject_code, detail}, and detail is the fixed server template "the glb footprint could not be triangulated (reject_code=self_intersection)" — no caller coordinate echoed. Test: `test_distinct_vertex_bowtie_is_a_reconciled_typed_refusal` (3 params: origin/nyc-scale/figure-eight), test:691.
- MANDATORY gate-removal mutant RE-RUN BY ME: no-op'ing es._reject_non_simple_ring renders the bowtie as a valid glTF (ExportResult, body starts glTF) → the refusal test reddens; restored → refusal again. Load-bearing. Test: `test_simplicity_gate_dropped_lets_a_bowtie_through`, test:706.

Note: the gate runs AFTER triangulate_polygon, so preparation has already proven finiteness/magnitude/1000-cap before GEOS sees the ring; preparation (reverse/collinear-collapse/dedup) cannot turn a simple footprint non-simple, so no valid footprint is falsely refused — confirmed by L/U/convex/CW all rendering.

Part 2: advisory 2, cap edge, nothing-weakened, verdict.

---

M5-T116 G4 DELTA re-check — part 2/2.

ADVISORY 2 (prepared-vs-raw fixture sensitivity) — NOW CLOSED. New fixture `_CW_COLLINEAR_FOOTPRINT` (CW-ordered rectangle + a collinear midpoint) makes preparation both reverse to CCW and collapse the midpoint, so prepared != raw in BOTH order and count. Test `test_prism_positions_come_from_the_prepared_ring_not_the_raw_input` (test:751) asserts n_prep < len(raw), local_ring == localized PREPARED ring (not raw), the caps tile with correct count/area, and a raw-ring mutant reddens.
- I RE-RAN the raw-ring mutant in-process: real build n_prep=4 (raw=5), caps tile n-2=2; the raw-ring mutant (positions from raw order/count while caps index the prepared ring) → n=5 with 2 bottom-cap tris vs n-2=3 → cap-count oracle RED. Confirmed load-bearing. The positions-from-raw regression is now catchable (it was invisible in round 1).

G3 A1 cap edge — verified. `test_glb_footprint_vertex_cap_1000_accepted_1001_refused` (test:727): I re-ran in-process — 1000-vertex circle → ExportResult glTF; 1001 → ExportRefusal over_cap_vertices (refused inside the triangulator before the ear scan). In-code NOTE at `_FORMAT_RING_CAP` states the effective footprint cap is the triangulator's MAX_OUTLINE_VERTICES=1000 (raw 10_000 still bounds the never-rendered lot ring).

NOTHING WEAKENED — verified.
- 464 passed / ruff clean / (modularity exit 0 per producer report). The only change to an EXISTING test is the AS-2 docstring de-over-claiming; its assertions (dup-vertex → self_intersection) are unchanged.
- Zero new dependencies: shapely==2.0.7 is already pinned in requirements.txt (hashed) AND requirements.in, and used by five other app modules; the delta touches no requirements/lockfile (3 files only: export_service.py, test, report). AS-5 holds.
- The gate only REFUSES; it never alters a produced mesh — no new GLB byte change beyond round 1's disclosed convex cap-index change. Owner samples (test_cad_owner_samples.py) and DXF/PDF stay byte-identical (they bypass _build_prism_mesh) — green in the 464. UNMOUNTED (app/main.py untouched). Only the 3 allowed paths changed.
- My round-1 PASS coverage (AS-1 concave caps + winding, AS-3 fallback, AS-4 four-field/floor, AS-5 scope) is unaffected — the delta only ADDS the gate, tests, the NOTE, and the docstring fix.

No BLOCKING findings; no remaining advisories (both round-1 advisories closed).

M5-T116 G4 VERDICT: PASS
END-OF-REPORT
