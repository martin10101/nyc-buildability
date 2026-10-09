# M5-T104 — directive-compliance verification (directive-compliance-verifier "dcv-t104", read-only)

> Transmission history: pinned at 2bd37434, delivered as three SendMessage parts (1/3..3/3) ending with END-OF-REPORT; no
> truncation. Part 1 carries the blob-level restamp predicate with broad disjoint-peer tolerance (incl. the M5-T103 harvest).
> Joined verbatim by the orchestrator (transport wrapper tags removed only). Validator EXIT 0 (one direct run); CI at
> cde8fc0e 18/18 green incl. the 46 sheet tests on Linux 3.12.

---

M5-T104 (D-087 PKT-K2) DCV — Part 1/3: pinned head, restamp pre-authorization, harness. Read-only; no writes outside my agent-memory dir; no CLI/git write verbs.

PINNED HEAD at start = 2bd374340bb3f029a11a9c487b4371999e061844 (expected). Material c0ce1ae3, cherry-pick of producer wt-m5t104 42a3995a. Producer backend-engineer.

RESTAMP PRE-AUTHORIZATION (blob-level predicate + broad disjoint-peer tolerance):
My PASS holds at ANY later orchestrator HEAD at accept time PROVIDED all three reviewed blobs stay byte-identical AND the frozen identity is unchanged:
- project-control/reports/M5-T104-producer-report.md = baa2cf45458299c55c3f081e242a85d3b37075fc
- services/api/app/drawings/sheet_primitives.py = eb4205a24491e8201dfa7c74413ebaae80d30c94
- services/api/tests/drawings/test_sheet_reader.py = 613bcd20a1ecd1eef10540bff7f444878249dd30
- _task_git_identity(dr,task)@HEAD == 38a708668c98f80b46273ab40579506c745e5af564ad6b10802ca5353211c839 (== reports/M5-T104.json content_manifest == the G2/G3/G4 stamps).
Broad disjoint-peer tolerance — the verdict is UNAFFECTED by, and the restamp is pre-authorized across, any commit that does not alter those 3 blobs, specifically: other tasks' files/gates/material incl. the M5-T103 harvest (disjoint files) and other contract/accept seams; other directives' registry binds (applicability appends + same-commit requirements-digest resyncs + audit entries); the orchestrator adding M5-T104's verification rows to D-066/D-087 verification.json with matching digest resyncs and audit_log entries; DISCOVERY_BACKLOG rows and sweep lines; lifecycle-only packet changes to M5-T104.json (awaiting_gate -> accepted, progress/updated_at). Proven safe: identity held at 38a70866 across cde8fc0e..2bd37434 while gate records and state.json changed — the task JSON is not in allowed_paths, so accept-lifecycle writes move neither the 3 blobs nor the identity.
FAIL the restamp if: any of the 3 blob SHAs change, allowed_paths change, identity != 38a70866, a new blocker references M5-T104, PR #241 is touched, or M5-T104 reaches main outside the normal accept seam.

HARNESS (reproduced myself):
- python tools/validate_directive_compliance.py --check -> exit 0 (direct exit code, no pipe; ran once, ~7 min).
- CI at material head cde8fc0e (run 36067795214): ALL 18 jobs success, incl. `api (ruff + pytest)` (the 46 sheet tests on 3.12), `control-plane (ADR-005)`, `exact-production-install (pip-audit)`, `api-lock-verify`, `modularity`, `contracts`.
- python tools/test_directive_reminder.py -> Ran 12 tests, OK (exit 0).
- python tools/test_project_control.py -> exceeded 300s (slow suite post verification-row growth); covered by the green control-plane CI job. Did NOT run test_directive_compliance.py (hard-prohibited).
Continues 2/3.

---

M5-T104 DCV — Part 2/3: applicability + requirement rows (each judged on primary evidence I reproduced).

APPLICABILITY: dr.load_registry().evaluate_task_refs(task) -> ok=true; applicable_ids == cited_ids == {D-066-R001, D-087-R001, D-087-R002, D-087-R005, D-087-R009}; missing_ids=[], invalid_refs=[], unresolved=[]. Hand-confirmed no other active D-087/D-066 requirement lists M5-T104 (R003/R004/R006/R007 exclude it; D-066 R002/R003/R004 are BOOTSTRAP/M5-T033 only). No missing/invented ref.

REGISTRY INTEGRITY: source + requirements digests recomputed with dr.sha256_text_artifact — ALL MATCH: D-087 source-001 34c3dd64, source-002-amendment 4eea66c6, requirements 17cc4854; D-066 source-001 4cb05c94, requirements ae18d0fb. Both amendment requirements (R011,R012) present in the D-087 matrix. Wave-8 bind recorded with same-commit resync in both manifests (D-087 audit 2026-09-24T22:05Z: R001/R002/R005/R009 <- M5-T104; D-066 audit: R001 <- M5-T104).

D-066-R001 (obligation; graph regen + navigation block + query.py --no-regen; advisory) — SATISFIED.
Evidence: packet M5-T104.json inputs[9] carries the CODE-GRAPH NAVIGATION BLOCK (graph regenerated 830 files/17842 nodes/7656 edges), names the reader modules' consumers, fences M5-T103's files FORBIDDEN, and instructs `python tools/code_graph/query.py --no-regen impact <path>` with "graph ADVISORY - verify in actual source." G0 report lines 25-26 corroborate. Bind + digest resync verified above.

D-087-R001 (obligation; use capacity, normal gated process unchanged) — SATISFIED.
Evidence: full gated lifecycle present, no state/gate skipped — G0 at 8e20acf2, claim at e9a268a5 (progress_log: orchestrator-dispatched subagent, worktree created at claim-seam), G2/G3/G4 recorded; required_gates [G0,G2,G3,G4] all PASS; ran concurrently with the file-disjoint M5-T103 (both wave-8). Manifest wave-8 bind confirms.

D-087-R002 (prohibition; pairwise-disjoint allowed_paths, isolated worktree) — SATISFIED.
Evidence: I read both packets. M5-T104 allowed_paths {tests/drawings/test_sheet_reader.py, app/drawings/sheet_primitives.py, reports/M5-T104-producer-report.md} are FULLY DISJOINT from M5-T103 {pdf_object_streams.py, sheet_reader.py, sheet_objects.py, sheet_interpreter.py, test_pdf_object_streams.py, its report}. forbidden_paths explicitly fence all of M5-T103's files. G0 disjointness table = EMPTY overlap vs every active task incl. M5-T103. Worktree wt-m5t104 isolated. git diff-tree c0ce1ae3 = exactly the 3 allowed paths, all Modified.
Continues 3/3.

---

M5-T104 DCV — Part 3/3: R005/R009, identity, gates, prohibited-action sweep, verdict.

D-087-R005 (authorization + C-track honesty; here = regression tests only, no new reading capability) — SATISFIED.
Evidence I reproduced: git diff c0ce1ae3^..c0ce1ae3 on sheet_primitives.py is ONLY the apply_matrix docstring "§8.3.3"->"§8.3.4" (one line; no code). No reader module touched (all M5-T103-owned reader files are in forbidden_paths). All 10 named DB-055/DB-064 tests exist in the committed file (git show grep, each count=1). DB-055(a) test now pins points[1]==(14.160156,13.339844) — the interior point the bug displaces (points[0]/points[-1] preserved); the field the bug moves is asserted, not a vacuous invariant. Honest, not overclaimed: report states "without changing production behaviour"; G4 killed 12/12 producer mutants + 5/5 reviewer weakenings, 20/20 operators executed; G3 independently reran the pre-fix revert (points[1]->(23.125,20.3125)). CI api pytest green at 3.12 (46 tests). Mutation runs are recorded-not-committed (report M1-M10) to avoid coupling to M5-T103-owned internals — matches packet input "record each mutant and its red run"; both reviewers accepted and reproduced.

D-087-R009 (boundaries stand; zero new deps) — SATISFIED.
Evidence: material commit touches only 3 files; requirements.txt/requirements.in are forbidden and absent from the diff; CI api-lock-verify + exact-production-install (pip-audit) green. Unwired (app/api/, app/main.py forbidden; max-envelope route stays unmounted). split-equivalence golden untouched (forbidden; 9/9 green per G3/G4). PR #241 OPEN/unmerged/untouched since 2026-08-20. No gate skipped. Production unchanged except the citation line.

FROZEN IDENTITY: _task_git_identity(dr,task)@HEAD = 38a708668c98f80b46273ab40579506c745e5af564ad6b10802ca5353211c839, error=None == reports/M5-T104.json content_manifest == G2 == G3 == G4 stamps. Blobs byte-identical c0ce1ae3->HEAD and c0ce1ae3==producer 42a3995a (report baa2cf45, primitives eb4205a2, tests 613bcd20).

GATES: G0 PASS (orchestrator/administrative), G2 PASS (orchestrator/self_check), G3 PASS (code-reviewer/independent), G4 PASS (qa-engineer/independent). Producer backend-engineer is none of the reviewers (producer != verifier). Test count 37->46 (baseline c0ce1ae3^ = 37, HEAD = 46).

PROHIBITED-ACTION SWEEP (all clean): task status awaiting_gate (NOT accepted); ZERO verification rows for M5-T104 in D-066/D-087 verification.json (no 38a70866/c0ce1ae3 anywhere); NOT on main; PR #241 untouched; no open blocker references M5-T104.

FINDINGS: no BLOCKING defects. Reviewer advisories (flattener-derived interior literals; the untouched §8.3.3 type-alias comment) are non-blocking and correctly routed. All 5 applicable requirements SATISFIED on primary evidence.

M5-T104 DCV VERDICT: PASS 5/5
END-OF-REPORT
