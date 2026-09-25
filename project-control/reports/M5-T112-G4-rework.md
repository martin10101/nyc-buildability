# M5-T112 — G4 delta re-review, rework round 2 (qa-engineer "qa-t112", read-only)

> Transmission history: pinned at cbafe211 (delta = 1b24fa94, identity 4b71b839), delivered as 1 SendMessage
> part(s) ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags
> removed only). Verdict PASS: mutant ME re-run in-process is
> detected again (5 scan calls under the tight budget); baseline green; 817 scenario tests.

---

M5-T112 G4 delta re-review — BLOCKING finding resolved; verdict PASS.

PIN: HEAD `cbafe211` at start (matches expected).

DELTA SCOPE (clean): commit 1b24fa94 touches ONLY `services/api/tests/scenario/test_massing_model.py`. The massing production modules (`app/scenario/massing_*.py`) and both new test files (`test_massing_split_equivalence.py`, `test_massing_triangulation.py`) are BYTE-UNCHANGED vs my prior-reviewed head 1461966b (scoped `git diff` empty), so my Part 1/2 findings (AS-1 modularity, AS-2 byte-perfect equivalence incl. DB-079b, AS-3 public triangulator, AS-4, AS-5) all still stand. The other files in the wider 1461966b..HEAD diff (scene_api, dxf_import, export_api, drawings, rate_limit, M5-T111/T113/T115) are disjoint peer lanes, not T112 material.

THE FIX (test_t098_as4, correct form): adds `from app.scenario import massing_triangulation as mt`; `real_pit = mt._point_in_triangle`; `monkeypatch.setattr(mt, "_point_in_triangle", counting_pit)` — the CONSUMING namespace, which the inner scan actually resolves. Plus a positive control after the zero-call assertion: an ample-budget `mm._triangulate(...)` then `assert calls["n"] > 0`, so the guard can't silently go vacuous again.

BASELINE GREEN: the corrected test passes under pytest; full `tests/scenario` = 817 passed; `ruff check .` clean.

MUTANT ME (re-run myself, in-process): I built the charge-after-scan variant with consuming-namespace lookups, bound it on the facade (`mm._triangulate`), and ran the corrected test's exact logic:
- Baseline (real code): budget refused, scan calls under the tight WorkBudget(n-3) = 0 (m-3 charged BEFORE the scan), positive control calls>0 → PASS.
- Variant (m-3 charged AFTER the scan): still refuses, but scan calls under the tight budget = 5 → `assert calls["n"] == 0` is now FALSE → the test FAILS. Mutant ME is DETECTED again.

So the mutant-ME (charge-order) guard is RESTORED: the counter now bites the real consumer (5 calls observed), the positive control confirms it bites on the happy path, and the assertion discriminates charge order. Production behaviour remains byte-identical and correct.

ADVISORY (unchanged, non-blocking): OPEN-Q1 huge-int `floor_to_floor_ft` label; `triangulate_polygon` not re-exported from the facade. Both fine.

M5-T112 G4 VERDICT: PASS

END-OF-REPORT
