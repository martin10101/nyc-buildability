# M5-T112 — G3 delta re-review, rework round 2 (code-reviewer "cr-t112", read-only)

> Transmission history: pinned at cbafe211 (delta = 1b24fa94, identity 4b71b839), delivered as 1 SendMessage
> part(s) ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags
> removed only). Verdict PASS: B1 closed (the counter patches the
> consuming namespace; a positive control keeps it from going vacuous); production byte-unchanged.

---

M5-T112 G3 delta re-review — B1 CLOSED, VERDICT PASS. Read-only. HEAD pinned cbafe211c8dc07f9c17e56da7daf202010d72afd (matches expected).

Delta scope verified: commit 1b24fa94 touches ONLY services/api/tests/scenario/test_massing_model.py (+10/-2). `git log 1461966b..HEAD -- services/api/app/scenario/` is EMPTY, so the massing production code (model/guards/triangulation/mesh) is byte-unchanged since round 1 — all round-1 PASS findings (behaviour preservation, split quality, public triangulate_polygon, DB-079 b) still hold.

B1 fix (test_t098_as4) — correct and slightly stronger than my minimal suggestion:
- new top-level `from app.scenario import massing_triangulation as mt`;
- real_pit = mt._point_in_triangle and monkeypatch.setattr(mt, "_point_in_triangle", counting_pit) — patches the CONSUMING namespace, exactly the fix I recommended;
- positive control after the zero-call assertion: `mm._triangulate(ring, "t", mm._WorkBudget(mm.MAX_TRIANGULATION_WORK)); assert calls["n"] > 0`. This makes the guard self-validating — the test cannot pass unless the patch bites, so it cannot silently go vacuous again.

Independent verification this session:
- services/api `ruff check .` -> All checks passed!
- targeted test_t098_as4 -> PASSED. Because the positive control asserts calls>0, a green run PROVES the mt patch now bites.
- services/api `pytest tests/scenario -q` -> 817 passed (count unchanged; the edit modified one existing test body + added one import).
- repo root `modularity_check --check` -> failures 0 (no massing_* flagged; production unchanged).
- My round-1 probe already showed the consuming-namespace patch bites (mt counter=15) while the facade patch did not (counter=0); the fix moves the patch to mt, so mutant ME (m-3 charge after the scan) now increments the counter under budget n-3 and reddens `assert calls["n"]==0`.
Note: an in-process mutant-ME re-run was blocked by my session's read-only guard (a module-attr assignment); I did not retry. The positive control provides equivalent structural proof.

No new issue from the edit: the sole file is test-only and in allowed_paths; no new dependency; no production/route change. Advisories A1 (DB-079 b locator scope) and A2 (triangulate_polygon not on facade __all__) remain informational, unchanged.

M5-T112 G3 VERDICT: PASS

END-OF-REPORT
