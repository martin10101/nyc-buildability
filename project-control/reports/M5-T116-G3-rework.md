# M5-T116 — G3 delta re-review, rework round 2 (code-reviewer "cr-t116", read-only)

> Transmission history: pinned at ab9001ea (delta = c903307e, identity 23fd4149), delivered as two SendMessage
> parts ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags
> removed only). Verdict PASS: B1 closed (three bowties reproduced as the
> typed self_intersection refusal; L and convex still render); A1 and the G4 advisory addressed.

---

M5-T116 G3 DELTA re-review (cr-t116, READ-ONLY): B1 CLOSED — VERDICT PASS. [part 1/2]

PIN: HEAD = ab9001ea7ccdf3265d77303af115eb6438737533 (the re-frozen seam, as expected). Delta c903307e touches EXACTLY the 3 allowed files (export_service.py +48, test +130, report +80); the two code files at HEAD == c903307e (empty diff). No requirements/lockfile/pyproject touched; shapely==2.0.7 already pinned (requirements.txt:508, requirements.in:51) — zero new dependencies.

CHECKS (cwd services/api unless noted): ruff -> All checks passed; `pytest tests/cad -q` -> 464 passed (matches expected); `modularity_check --check` (root) -> exit 0.

B1 (round-1 BLOCKING) — CLOSED. New in-scope GEOS gate `_reject_non_simple_ring` (export_service.py:391-413): `LinearRing(ring).is_simple` on the PREPARED ring; not-simple -> typed MassingModelError(reason='self_intersection'); any ShapelyError/ValueError -> the SAME typed refusal (fail-closed). Called at export_service.py:444 in _build_prism_mesh on the prepared ring (already finite/bounded/<=1000/distinct/CCW, so GEOS never sees hostile input); caught by the existing _render_glb handler (:517-518), reconciled to the ONE redacted ExportRefusal (:329).

Reproduced IN-PROCESS against the new code (my three round-1 bowties):
- [[0,0],[60,60],[60,0],[0,60]] -> ExportRefusal self_intersection
- NYC-scale bowtie -> ExportRefusal self_intersection
- [[0,0],[40,0],[0,40],[40,40]] -> ExportRefusal self_intersection
detail = exactly "the glb footprint could not be triangulated (reject_code=self_intersection)" (no caller coordinate). Valid L (1828B) and convex (1680B) still render. New parametrized test test_distinct_vertex_bowtie_is_a_reconciled_typed_refusal + the gate-dropping mutant test_simplicity_gate_dropped_lets_a_bowtie_through prove it load-bearing. The old duplicate-vertex AS-2 test docstring no longer over-claims.

---

M5-T116 G3 DELTA (cont.): A1 + G4-adv addressed; placement/mapping/line-count answered; verdict. [part 2/2]

A1 (round-1 ADVISORY) — ADDRESSED. In-code NOTE at _FORMAT_RING_CAP (export_service.py:121-132): the effective GLB footprint cap is the triangulator's MAX_OUTLINE_VERTICES=1000, not the raw 10_000. New test test_glb_footprint_vertex_cap_1000_accepted_1001_refused; confirmed in-process: circle(1000) -> ExportResult, circle(1001) -> over_cap_vertices.

G4 advisory 2 — ADDRESSED: a CW + collinear-midpoint fixture + test_prism_positions_come_from_the_prepared_ring_not_the_raw_input with a raw-ring mutant pins positions from the PREPARED ring.

Team-lead's specific questions:
- Gate PLACEMENT: correct/safe. Runs on the prepared ring so GEOS gets clean input; a bowtie ear-clips to completion within the bounded work budget before the gate rejects (no DoS). Running after triangulate is a deliberate, defensible choice. Not an issue.
- EXCEPTION MAPPING: (ShapelyError, ValueError) and is_simple=False both -> MassingModelError('self_intersection') -> the one redacted refusal. Comprehensive, fail-closed. The gate only READS is_simple; it never mutates the mesh ring. Not an issue.
- export_service.py 612 raw lines vs the 600 line: the authoritative modularity checker is SLOC-based (policy: warn 600 / justify 750 SLOC). At 612 raw lines its SLOC is under warn, so --check does NOT flag it and exits 0 (same as round 1 at 572). Acceptable — not blocking, not even warn. The +48 lines are a required safety gate + docstring, cohesive with the file's single responsibility, not unrelated-domain growth.

Round-1 verified-correct items ((a) caps, (c), (f), (g), (h)) are untouched by the delta and still pass (part of the 464). No new issue found. UNMOUNTED (app/main.py untouched).

M5-T116 G3 VERDICT: PASS
END-OF-REPORT
