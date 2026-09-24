# M5-T083 — G4 re-review after the rework (qa-engineer "qa-drw", read-only)

> Transmission history: requested by SendMessage after the G5 FAIL rework (5467318e, cherry-pick of
> wt-m5t083 b07a4aaa); pinned at 10def4ef (the three review blobs verified byte-identical throughout);
> delivered as two SendMessage parts (1/2, 2/2) ending with END-OF-REPORT; no truncation. Joined verbatim
> by the orchestrator (transport wrapper tags removed only). A separate follow-up message from the same
> reviewer (agent-memory riders it could not write itself) is NOT part of this report. The first joint
> T083/T086 G4 (PASS) stays in M5-T083-G4.md unchanged.

---

M5-T083 G4 re-review (rework): PASS — with ONE ADVISORY test-vacuity finding (F6). Part 1/2. Read-only; git status --short services/ clean (in-memory mutation only, no repo/ledger/memory writes).

PIN & IDENTITY: pinned 10def4ef; HEAD churned during review (orchestrator integrating) but the 3 review blobs stayed byte-identical throughout — sheet_reader 63a992ca, sheet_primitives a3659c55, test_sheet_reader b60f7e1c (exactly the expected pin). Testing valid at the reviewed identity.

BASELINE: 37 passed via the 3.11 bare-package shim. CI authority: the latest COMPLETED CI run (head 33662211, which carries test blob b60f7e1c) shows `api (ruff + pytest)` = SUCCESS — the 3.12 job collects and passes all 37, ruff clean. (A newer re-record CI run was still in-flight at review time.)

F4 / F5 CLOSED (my prior advisories):
- F4 cubic_flat and->or: KILLED by the new test_asymmetric_bezier_respects_declared_tolerance (the symmetric quarter-circle AS-1 still can't distinguish it — as expected). Closed.
- F5 immediate-parent-only cycle: KILLED by the new test_multi_hop_form_cycle_is_refused (the self-reference test still passes under it — as expected). Closed.

NON-VACUITY MUTATION TABLE (each new guard mutated on the consuming namespace; target test in parens):
1 budget-threaded flatten (budget cutoff returns True) -> KILLED (test_flatten_cubic_stops_at_the_point_budget AND test_single_curve_refuses_within_bounded_memory).
2 per-page output reset (depth-0 reset neutralized) -> KILLED (test_each_page_has_only_its_own_primitives).
3 Form decode memoization (cache bypassed) -> KILLED (decode calls 11 not 2).
4 decoded-bytes budget (charge_decoded never refuses) -> KILLED (test_document_decoded_bytes_budget_is_refused).
5 top-level backstop (read_sheet except re-raises) -> KILLED (test_top_level_backstop...). NOTE: the test imports read_sheet BY VALUE, so a naive sheet_reader.read_sheet-only rebind was a FALSE survivor; rebinding the test module's read_sheet reached it -> RED(RuntimeError). Guard is real.
6 attacker-token truncation (_preview returns token) -> KILLED (test_unsupported_operator_detail_is_truncated).
7 finiteness gate in _map (skip is_finite check) -> KILLED (test_non_finite_coordinate_after_ctm_is_refused).
8 q/Q text-state restore (Q restores only CTM) -> KILLED (test_q_q_saves_and_restores_font_size).
8b form inherits caller text state (place_form font_size=None) -> KILLED (test_form_inherits_caller_text_state).

(continued part 2/2)

---

M5-T083 G4 re-review (rework) part 2/2 — remaining guards, F6, fuzz, verdict.

MUTATION TABLE (cont.):
9 new-subpath-after-close (_lineto refuses instead of _open_after_close) -> KILLED (test_segment_after_close_begins_new_subpath).
10 device-space current point (_curveto: p0 = _apply_matrix(self._ctm, *self._current) — the EXACT pre-rework revert) -> *** SURVIVED ***.

F6 (NEW, ADVISORY — test vacuity, production code CORRECT):
test_mid_path_cm_does_not_corrupt_curve_start does NOT guard its stated fix (item 9, G1 F6/G3 F3). It asserts points[0]==(10,10) and points[-1]==(40,40) — BOTH invariant under the bug: points[0] is the separately-stored moveto point and points[-1] uses map(*end). The pre-fix revert corrupts the curve's START, which is points[1]: measured REAL points[1]=(14.16,13.34) vs MUTANT (23.12,20.31) — a real discontinuity — and NO test among the 37 reddens (I ran the full fixture-free suite under the mutant: none caught it). The device-space fix IS correctly implemented (the real curve starts smoothly at (10,10)); only its regression-guard test is vacuous. The producer's own mutant record (report lines 278-283) self-verified only 5 of the 12 new guards and did NOT include this item. FIX (one line): assert the reopened curve's first interior point (points[1]) is continuous with the moveto point (~(10,10)), not points[0].

FUZZ: read_sheet over 12,238 inputs (prefix truncations, 4000 byte flips/deletes/inserts of a curves+CTM+text+XObject PDF, 2000 random blobs, 4000 content-stream operator streams incl. huge-cm chains / repeated Do / 300-char tokens / 1e39, truncated streams) -> 0 escapes / 0 bad returns. AS-4 holds; the new backstop is a second layer.

SCOPE: git status --short services/ clean; app/documents + requirements untouched (blobs unchanged); modules stdlib + already-admitted only.

ASSESSMENT: the BLOCKING G5 item (F1 memory/point budget) and every G5 security item (F2 memoization+decoded-bytes, F4 backstop, F5 truncation, F6 finiteness) are non-vacuously tested and correct; F4/F5 closed; 11 of 12 probed guards KILLED; all 37 green; CI 3.12 api SUCCESS at the exact test blob; fuzz clean. The single survivor (F6) is a test-only vacuity on a correctly-implemented, non-blocking correctness item — hence ADVISORY, not blocking. Recommend the one-line assertion strengthening (ideally folded into this task before final acceptance, but it does not compromise correctness, security, or the acceptance scenarios).

M5-T083 G4 VERDICT (rework): PASS

END-OF-REPORT
