# M5-T112 — G5 delta re-review, rework round 2 (security-reviewer "sec-t112", read-only)

> Transmission history: pinned at cbafe211 (delta = 1b24fa94, identity 4b71b839), delivered as 1 SendMessage
> part(s) ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags
> removed only). Identity carry to 4b71b839: production
> byte-identical to the reviewed 7413ecf4; ADVISORY-1 closed; verdict PASS.

---

M5-T112 G5 IDENTITY-CARRY ATTESTATION (read-only, sec-t112)

PIN: HEAD cbafe211 (matches expected "cbafe211 or later").

VERIFIED:
- Production byte-identical: git diff 7413ecf4 (my reviewed material) -> HEAD over massing_model.py, massing_guards.py, massing_triangulation.py, massing_mesh.py is EMPTY. All four production blobs are unchanged from the content I PASSed; my security analysis carries to the re-frozen identity 4b71b839.
- Delta 1b24fa94 is TEST-ONLY: one file, services/api/tests/scenario/test_massing_model.py (+10/-2). No production/dependency/exception surface added; no security-relevant change.
- The correction closes ADVISORY-1 exactly as recommended: test_t098_as4 now binds real_pit = mt._point_in_triangle and monkeypatch.setattr(mt, "_point_in_triangle", counting_pit) — the CONSUMING namespace (massing_triangulation), which _triangulate actually resolves — so the counter now bites. It also adds a positive control: an ample-budget _triangulate run followed by assert calls["n"] > 0, which proves the overspend case's calls["n"] == 0 is a real "scan suppressed by the budget" observation, not a vacuous no-op. This re-arms the mutant-ME guard (charge m-3 AFTER the scan now reddens it) and prevents silent re-vacuation.
- Green at HEAD: pytest tests/scenario/test_massing_model.py::test_t098_as4_scan_units_charged_before_the_inner_scan = 1 passed. Matches the orchestrator self-check (baseline green, mutant ME red).

ADVISORY-1: CLOSED. ADVISORY-2 / INFO-1 / INFO-2 stand unchanged (defense-in-depth + carried-forward wiring-packet duties; none blocking). No CRITICAL/HIGH/MEDIUM. The monkeypatch-seam security question passes: production reads no mutable global that changes posture, and the DoS-guard test is now effective.

M5-T112 G5 VERDICT: PASS

END-OF-REPORT
