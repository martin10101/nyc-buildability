# M5-T123 — directive-compliance verification (directive-compliance-verifier "dcv-t123", read-only)

> Transmission history: pinned at 4a0799b3 (HEAD advanced to 4c7437dd through a disjoint peer seam - the M5-T124
> contract - with the nine T123 blobs and identity 7bd23182 byte-stable; verified at both heads), delivered as four
> SendMessage parts (1/4 carries the up-front restamp pre-authorization) ending with END-OF-REPORT; no truncation.
> Joined verbatim by the orchestrator (transport wrapper tags removed only). Part 3 carries the evidence-honesty
> ruling F1 (the DXF memory figure) with its acceptance condition - satisfied in this accept seam's backlog row DB-093.

---

M5-T123 DCV report [1/4] — anchors, restamp predicate, and the validator c14 diagnosis. READ-ONLY.

PIN: I started at HEAD 4a0799b3 (expected). During review the branch advanced to 4c7437dd (your concurrent M5-T124 wave-9 work). I verified M5-T123 at BOTH heads.

RESTAMP PRE-AUTHORIZATION (up front):
Reviewed blobs (all 9 allowed paths; identical at 4a0799b3 AND 4c7437dd):
- scene_api.py 1f03ff7c
- export_api.py 0d5f2f07
- dxf_import_api.py 1329bc90
- rate_limit.py 0ff04d27
- test_rate_limit.py 4ee8baa2
- test_scene_api.py 027116e2
- test_export_api.py d6407d7d
- test_dxf_import_api.py 0e789d64
- M5-T123-producer-report.md ac510dcc
- identity 7bd23182
PREDICATE: this PASS holds while those 9 blobs and the frozen identity 7bd23182 are unchanged; restamp reviewed_sha to the accept-time HEAD. de92182d..4c7437dd touches NONE of the 9 paths (verified empty).
DISJOINT-PEER TOLERANCE (broad): other tasks' files/gates/material (M5-T120, M5-T122 in review; M5-T124 and any new packets); other directives' registry binds; you adding my verification rows to the D-066/D-087 verification.json with digest resyncs + audit entries; DISCOVERY_BACKLOG rows (incl. the DB-D4 corrected-memory row) + sweep lines; lifecycle-only packet changes. Any such peer that leaves the 9 blobs + 7bd23182 unchanged needs no re-review.

FROZEN IDENTITY — reproduced with project_control._task_git_identity(dr, task): 7bd23182b1a5998ae9b4911af60f7de3bf4f62cf45e0ca02c5d6b73bcea8baf3, err=None (clean). Equals reports/M5-T123.json content_manifest_sha256 AND the G2/G3/G4/G5 stamps (all 7bd23182). Holds at 4c7437dd (9 blobs byte-stable).

APPLICABILITY — reg.evaluate_task_refs(task): ok=True, applicable_ids == cited_ids == {D-066-R001, D-087-R001, R002, R003, R004, R006, R009}; missing=[], invalid=[], unresolved=[]. Matches the packet + reports/M5-T123.json. D-087 and D-066 both active, errors=[].

GATES: G0 orchestrator/admin@80e6274a PASS; G2 orchestrator/self-check@de92182d PASS; G3 code-reviewer PASS; G4 qa-engineer PASS; G5 security-reviewer PASS — G2-G5 all carry 7bd23182; none recorded by the producer (backend-engineer).

VALIDATOR c14 (important, diagnosed, NOT a defect): one `validate_directive_compliance.py --check` run returned INVALID with ONLY 3 errors — c14 requirements.json content-digest mismatch for D-066/D-083/D-087. Root cause: it read a TORN working tree during your 4a0799b3->4c7437dd branch advance. Proof via git-show on the COMMITTED blobs: at 4a0799b3 all three manifests MATCH their requirements.json (D-087 59de5ee4==59de5ee4), and at 4c7437dd all three MATCH (D-087 4ae20655==4ae20655). The validator compared manifest@4a0799b3 (59de5ee4) vs requirements@4c7437dd (4ae20655) — a mid-write snapshot. Registry is internally consistent at BOTH committed heads; no source-digest, locked-id, applicability or verification-row error anywhere. Transient, matches the known "requirements-lands-before-manifest" signature. Rows settled by direct computation; not re-run (budget). Continues in [2/4].

---

M5-T123 DCV report [2/4] — requirement rows (primary evidence reproduced, not the producer's matrix).

D-066-R001 (obligation; navigation block) — SATISFIED. M5-T123.json inputs[] carries the CODE-GRAPH NAVIGATION BLOCK: "graph REGENERATED at the wave-1 seam, 844 files/18356 nodes/7841 edges: rate_limit.py imported by the three route modules + tests/resilience/test_rate_limit.py; the three route modules imported only by their own tests (UNMOUNTED); proposal_validation.py a MOUNTED READ-ONLY route" + the instruction "Run tools/code_graph/query.py --no-regen impact <path> before sweeps; graph ADVISORY." G0 report confirms it. Present in the packet.

D-087-R001 (obligation; use capacity, normal gated process) — SATISFIED. Bound via applicability.task_ids (evaluate_task_refs ok=true); contracted G0@80e6274a, claimed@8acf9c86 (producer report + evidence-map), gated G0/G2/G3/G4/G5, produced by an orchestrator-dispatched subagent (backend-engineer) concurrently with disjoint M5-T120/T121/T122; no state or gate skipped.

D-087-R002 (prohibition; no interference) — SATISFIED. G0 disjointness table: 19 active neighbors, every row "EMPTY overlap". One worktree (task.worktree = ...\wt-m5t123). de92182d `git show --name-only` = exactly the 9 allowed paths, no forbidden path; disjoint from M5-T120/T121/T122.

D-087-R003 (3D scene route ceiling+slots) — SATISFIED. scene_api.py (blob 1f03ff7c): SCENE_MAX_BODY_BYTES = 2*1024*1024 (2 MiB); enforced on the declared-Content-Length fast path AND the streamed _read_body_within_ceiling path (both in the diff); SCENE_MAX_IN_FLIGHT 16->8. Measured maximal body 811,225 B (report §1; G3 independently verified the proposal.py caps MAX_TOTAL_OUTLINE_POSITIONS=20000/MAX_LEVELS=500/MAX_EXTERIOR_WALLS=4000). Route stays UNMOUNTED.

D-087-R004 (DXF import ceiling + reader clamp raised) — SATISFIED (advisory F1 on the memory figure, below; non-blocking). dxf_import_api.py (blob 1329bc90): DXF_IMPORT_MAX_BODY_BYTES = 20*1024*1024 (20 MiB); `_IMPORT_DXF_LIMITS = DxfLimits(max_bytes=DXF_IMPORT_MAX_BODY_BYTES)` — the reader clamp is RAISED WITH the ceiling; enforced on both paths; DXF_IMPORT_MAX_IN_FLIGHT 16->4; under the reader's 64 MiB `_LIMIT_CEILINGS` hard clamp; dxf_reader.py untouched (READ-ONLY). Sized from the documented 1-20 MB range (DB-086 d). The max_lines-binds-first-on-a-dense-file limitation (~14.9 MB) is HONESTLY disclosed (DB-D4 discovery + OPEN QUESTION 3); TOO_MANY_LINES is a real typed refusal. Worst-case memory arithmetic declared (report §1 table).

D-087-R006 (CAD export ceiling + slots + principal) — SATISFIED. export_api.py (blob 0d5f2f07): EXPORT_MAX_BODY_BYTES = 1*1024*1024 (1 MiB), both paths; EXPORT_MAX_IN_FLIGHT 16->12; measured max 452,336 B. rate_limit.py (blob 0ff04d27): summed slots 8+12+4=24 < anyio 40-token pool (anyio 4.10.0; total_tokens==40 read LIVE in-test, reproduced by me and by G3); test_summed_job_slots_stay_under_the_anyio_thread_pool imports the REAL constants + LIVE limiter (non-vacuous; SUM==40 mutant -> RED). caller_key: `isinstance(principal, str) and principal.strip()` — whitespace-only -> host key (DB-088 b), mutation to `and principal` reddens. Continues in [3/4].

---

M5-T123 DCV report [3/4] — R009, harness, prohibited-action sweep, and the evidence-honesty ruling.

D-087-R009 (unchanged boundaries) — SATISFIED. app/main.py NOT in de92182d and has no reference to the three routers -> routes UNMOUNTED (G3/G5 grep). proposal_validation.py NOT touched; MAX_BODY_BYTES = 262144 (256 KiB) intact at HEAD (proposal_validation.py:76) — the three routes dropped the import and no longer borrow it. dxf_reader.py untouched. Zero new dependencies (no requirements.txt/.in in the diff; stdlib + already-admitted anyio/starlette only). 429 shape, per-window limits, deadlines, correlation ids, disabled-404 unchanged (full 199-suite green; G4 AS-5 invariance). PR #241 unaffected (de92182d not on main; no apps/ or PR change).

HARNESS (reproduced):
- pytest (cwd services/api) tests/resilience tests/scenario/test_scene_api.py tests/drawings/test_dxf_import_api.py tests/cad/test_export_api.py -q -p no:cacheprovider -> 199 passed in 6.41s (matches the report's 199; local Python 3.11).
- validate_directive_compliance.py --check -> 3 c14 torn-read errors only, diagnosed and disproven at both committed heads (part 1). Not re-run per the at-most-once budget; the rows are settled by the direct git-show digest computation (more precise than a re-run).
- I did NOT run tools/test_directive_compliance.py (prohibited; ~16h).

PROHIBITED-ACTION SWEEP — all clean:
- Not accepted: task status = awaiting_gate; 0 M5-T123 rows in D-087 and D-066 verification.json.
- Not on main: de92182d is not an ancestor of origin/main or local main; contained only by candidate/D-024-mrl-option-b.
- No open blocker names M5-T123 (grep of blockers/ empty; open B-001/B-010/B-011/B-026 do not reference it).
- PR #241 untouched; no material merged/dispatched/deployed by this packet.

F1 — EVIDENCE-HONESTY RULING (you asked explicitly). The producer report's DXF worst-case memory row (~1.2x raw, ~24 MiB/slot, ~312 MiB total) is optimistic; G5 measured ~17x input (the max_lines-governed _to_pairs list), so a DXF slot is ~65-150 MiB and the aggregate exceeds ~312 MiB. MY RULING: acceptable as a disclosed LOW advisory for UNMOUNTED code — the report need NOT be reworked before acceptance — PROVIDED you record the corrected measured figure in the DISCOVERY_BACKLOG DB-D4 row and preserve it as the PKT-H mount precondition (G5 mount-carry #1/#3). WHY: (a) the code is correct and HARD-bounded by max_lines (a real typed TOO_MANY_LINES clamp), so no shipped behavior is unsafe; (b) routes are UNMOUNTED, so the figure drives no live decision now; (c) the accurate number already lives on the independent VERIFIED record (G5) at the reviewed identity 7bd23182; (d) the producer disclosed the underlying MECHANISM (DB-D4 + OPEN QUESTION 3) — it under-counted one factor, it did not conceal it; (e) the number that governs the real gate (PKT-H instance sizing under a load test) is bound to PKT-H with the correct value. A rework->resubmit re-freeze for an advisory figure about non-runnable code, whose correct value is already on the verified record, adds churn without making any live code safer. All three independent reviewers returned PASS and rated it non-blocking. Continues in [4/4].

---

M5-T123 DCV report [4/4] — advisory sweep, review test notes, verdict.

REVIEWER-ADVISORY SWEEP (none undercuts a cited requirement):
- G3 A1 / G4-3 (comment nit): dxf_import_api.py:119 comment says `_MAX_LIMITS`; the real symbol is `_LIMIT_CEILINGS`. Comment-only — the code and tests use `_LIMIT_CEILINGS`; the producer report is correct. No functional impact on R004. (Cosmetic; fix on the next dxf_import_api.py touch.)
- G3 A2 / G4 CI note (web-e2e red): disjoint — de92182d has zero apps/ files, app/main.py loads none of the changed services/api modules; the apps/ diff d1970b06..b0eb29f7 is empty and the zero-delta rerun 36116139678 was fully green; signature = the known tabUntil `<body>` a11y flake. The covering api (ruff+pytest) job is green. Does not touch any requirement.
- G4-1/G4-2 (scene/export test depth): ceiling+1->413 is proven on the declared-length path; the streamed-path and exact-ceiling assertions are thinner than DXF, so a FULLY-defeated-guard mutant survives the scene/export suites (a LOWERED constant IS caught by the admission tests, which traverse the streamed path with the real constant). Inherited T111/T117 depth on UNMOUNTED routes; the binding AS-1/SAFETY bar (ceiling+1 refused + a maximal legit request admitted) is MET for all three routes. Advisory, does not undercut R003/R006.
- G5-2/G5-3 (principal raw value; pre-auth host-key collapse): safe while UNMOUNTED; mount-carry for PKT-H. The cited obligation (whitespace-only -> host, DB-088 b) IS correctly implemented. Does not undercut R006.

REVIEW TEST NOTES (AS-4) — both verified:
- DB-088(e): the AST no-local-limiter guard now catches module-level list/set/Counter (+ empty-list literal), leaving __all__/_ROUTE_METHODS/frozenset matrices unflagged; test_ast_guard_also_catches_list_set_counter_limiters reddens on reversion (producer M6; G4 Q1/Q2 independent -> RED).
- DB-088(g): the two post-start-timeout tests replaced the 50 ms window with an event handshake (started.wait(5.0)); the internal started flag is set before work() sets the test event, so no wall-clock race (G3/G4 Q12 confirm sound; the post-start slot semantics still redden under M7).

CONDITION ON ACCEPTANCE (non-blocking to this verdict): record the G5-measured DXF memory figure (~17x input; ~65-150 MiB/slot; aggregate > ~312 MiB) in the DISCOVERY_BACKLOG DB-D4 row and carry G5's five PKT-H mount preconditions. This is registry/backlog bookkeeping outside M5-T123's 9 blobs, so it moves no material identity.

Summary: 7/7 requirements SATISFIED on reproduced primary evidence; frozen identity 7bd23182 == reports manifest == all four material gate stamps; every required gate PASS by an independent reviewer (none the producer); exactly the 9 allowed paths, disjoint, UNMOUNTED, proposal_validation/dxf_reader/main.py untouched, zero new deps; pytest 199 passed reproduced; the validator's only errors are transient torn-read c14s disproven at both committed heads. No VIOLATED or UNVERIFIABLE result.

M5-T123 DCV VERDICT: PASS 7/7
END-OF-REPORT
