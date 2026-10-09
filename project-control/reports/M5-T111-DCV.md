# M5-T111 — directive-compliance verification (directive-compliance-verifier "dcv-t111", read-only)

> Transmission history: pinned at fc76a09f (HEAD moved to 16682c5c during the review through a disjoint peer commit;
> the nine T111 blobs and identity 3f87108f stayed byte-stable), delivered as five SendMessage parts (1/5..5/5)
> ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed
> only). Part 1 carries the blob-level restamp predicate with broad disjoint-peer tolerance. The orchestrator
> appended a `gitleaks:allow` HTML comment to the six predicate lines naming *_api.py blobs: the generic-api-key
> rule mistook those public git blob SHAs for keys (false positive); the report text is otherwise verbatim.

---

M5-T111 DCV — part 1/N: RESTAMP PRE-AUTHORIZATION (up front)

PINNED HEAD at start: fc76a09f. All 9 reviewed blobs verified byte-identical at HEAD and at material c3e3df15.

BLOB-LEVEL RESTAMP PREDICATE — my PASS holds at any HEAD >= fc76a09f for which `git ls-tree <HEAD>` yields these exact 9 blob SHAs:
- services/api/app/resilience/rate_limit.py = 637c1b6af64df8162c377516e0d7109a28bde0a2
- services/api/tests/resilience/test_rate_limit.py = 0f2b02783b9d0f1397d9c952969fb6c4a113e30b
- services/api/app/api/v1/scene_api.py = 9cdc8eb77b1c990417b5ef1a1b4bc3b2a88de054  <!-- gitleaks:allow (a public git blob SHA, not a secret) -->
- services/api/app/api/v1/dxf_import_api.py = 6a58ae1a56d11e73ac46b82c8324218e85c766d6  <!-- gitleaks:allow (a public git blob SHA, not a secret) -->
- services/api/app/api/v1/export_api.py = 4177ba0958dc48040457b822eda6f22c1121cfa8  <!-- gitleaks:allow (a public git blob SHA, not a secret) -->
- services/api/tests/scenario/test_scene_api.py = cd6232cf7bb19cd5b026ef3091bd80ee631e0179  <!-- gitleaks:allow (a public git blob SHA, not a secret) -->
- services/api/tests/drawings/test_dxf_import_api.py = 233878efceaf691b8d57afae9b91178e32550666  <!-- gitleaks:allow (a public git blob SHA, not a secret) -->
- services/api/tests/cad/test_export_api.py = ec9f9419e1e696c827643519634baa83b1a5fd11  <!-- gitleaks:allow (a public git blob SHA, not a secret) -->
- project-control/reports/M5-T111-producer-report.md = 70a7d045cba7973cf8e45375550a3da846208142
AND `_task_git_identity` still resolves to content_manifest_sha256 = 3f87108f AND evaluate_task_refs(M5-T111) stays exactly {D-066-R001, D-087-R001/R002/R003/R004/R006/R009}.

DISJOINT-PEER TOLERANCE (broad): I tolerate any commit at/after fc76a09f that touches ONLY files outside those 9 paths — other tasks' files/gates/material (M5-T112 rework+delta reviews, M5-T113, M5-T114/T115 harvests+reviews), other directives' registry binds, the orchestrator adding MY verification rows to D-066/D-087 verification.json with digest resyncs + audit entries, DISCOVERY_BACKLOG rows/sweep lines, and lifecycle-only edits to project-control/tasks/M5-T111.json or reports/M5-T111.json (status/progress/log) that leave the 9 blob SHAs and the 3f87108f identity unchanged. Any change to one of the 9 blob SHAs voids this and requires re-review.

Requirement rows + findings + final verdict follow in subsequent parts. (Part 1 end.)

---

M5-T111 DCV — part 2/5: IDENTITY, GATES, HARNESS

FROZEN IDENTITY (primary, reproduced): frozen_git_identity over the 9 allowed_paths at material c3e3df15 = 3f87108f625842f409b03efb12aefb0d5741c329c32d25e0448ebcc34cd0e49a. That EQUALS reports/M5-T111.json content_manifest_sha256 (line 8) AND the content_manifest_sha256 stamped by gates/M5-T111-{G2,G3,G4,G5}.json (all four = 3f87108f). Recomputed at live HEAD → same 3f87108f, so all 9 blobs are byte-stable at HEAD.

HEAD MOVED DURING REVIEW: started fc76a09f, now 16682c5c (one disjoint peer commit "seq 130: M5-T112 rework-round-2 deltas G3/G4 PASS + G5 identity carry"; fc76a09f is its ancestor). All 9 M5-T111 blob SHAs are byte-identical at 16682c5c — my part-1 restamp predicate holds at the current HEAD.

GATES (gates/M5-T111-*.json, primary): G0 PASS (reviewer=orchestrator, role=administrative, reviewed_sha=93b94019); G2 PASS (orchestrator, role=self_check); G3 PASS (code-reviewer, independent_review); G4 PASS (qa-engineer, independent_review); G5 PASS (security-reviewer, independent_review). All 5 required gates present; the three substantive reviews (G3/G4/G5) are by identities distinct from the producer backend-engineer (producer ≠ verifier holds).

HARNESS (independently reproduced, cwd services/api unless noted):
- `python -m ruff check .` → All checks passed! (exit 0).
- `python -m pytest tests/resilience tests/scenario/test_scene_api.py tests/drawings/test_dxf_import_api.py tests/cad/test_export_api.py -q` → 183 passed (exit 0).
- `python tools/test_directive_reminder.py` → 12 tests OK (exit 0).
- `python tools/test_project_control.py` → all 23 groups passed (exit 0).
- CI: run 36100151633 (workflow CI) at 0c24a8b5 = success; latest CI at fc76a09f (36101618977) + secret-scan + context-budget = success. The control-plane validator runs inside the green CI job.
- `tools/test_directive_compliance.py`: NOT run (your ~16h hard prohibition honored).
- `validate_directive_compliance.py --check`: SKIPPED under your "may skip if other checks settle the rows" allowance — see part 5 for why registry integrity is settled.

(Part 2 end; requirement rows follow.)

---

M5-T111 DCV — part 3/5: APPLICABILITY + R001/R002/R003 (primary evidence)

APPLICABILITY (reproduced): load_registry().evaluate_task_refs(task) → ok=True; applicable_ids == cited_ids == ['D-066-R001','D-087-R001','D-087-R002','D-087-R003','D-087-R004','D-087-R006','D-087-R009']; missing=[], invalid_refs=[], reasons=[]. I also scanned every uncited requirement: none lists M5-T111 in applicability.task_ids (D-087-R005/R007/R008/R010/R011/R012 and D-066-R002/R003/R004 all exclude it). Applicable == cited, exactly 7.

D-087-R001 (capacity; obligation) — SATISFIED. M5-T111 is a contracted, claimed, gated ledger packet: G0 recorded at 93b94019 (gate JSON), claimed at 275ef85f (parent of producer commit d3e303eb, per G2 report), 5 gates recorded, produced by an orchestrator-dispatched subagent concurrently with disjoint M5-T112/T113/T114; no state or gate skipped. Evidence: gates/M5-T111-*.json + tasks/M5-T111.json progress_log.

D-087-R002 (no interference; prohibition) — SATISFIED. G0 report (reports/M5-T111-G0.md) disjointness table lists "none - EMPTY overlap" against all 19 active tasks (M0/M4/M5 incl. M5-T110/T112/T113/T114). One isolated worktree: tasks/M5-T111.json "worktree": ...\wt-m5t111. Material c3e3df15 `git show --stat` = exactly the 9 allowed_paths (0 forbidden). Route tests sit beside their services because the frozen M4-T005 packet globs tests/api/** — no overlap.

D-087-R003 (3D released; authorization) — SATISFIED. services/api/app/api/v1/scene_api.py (blob 9cdc8eb7) is the UNMOUNTED 3D scene route, orchestrator-designed under full gates. Primary source: include_in_schema=False at api_route (:279); fail-safe disable checked FIRST — `if not internal_rule_eval_enabled(): return _not_found()` for every method in _ROUTE_METHODS=[GET,HEAD,POST,PUT,PATCH,DELETE,OPTIONS] (:98,:286-289); per-caller rate limit BEFORE body read/parse (:295 precedes :300/:304 stream + :312 json.loads); bounded job slots via run_in_job_slot→SlotsExhausted→503 (:375-378). Uses the shared app.resilience.rate_limit primitives (:67-73); no route-local limiter remains.

(Part 3 end; R004/R006/R009 + D-066-R001 follow.)

---

M5-T111 DCV — part 4/5: R004/R006/R009 + D-066-R001 (primary evidence)

D-087-R004 (AutoCAD/DXF import; authorization) — SATISFIED. services/api/app/api/v1/dxf_import_api.py (blob 6a58ae1a) = the UNMOUNTED ASCII-DXF interchange import route (/candidates,/draft). Source: dual flag gate checked FIRST (`if not _import_enabled()` → _not_found, :399-400/:450-451; adds a dedicated DXF_IMPORT_ENABLED write flag :177-179); _gate_and_limit (rate limit) runs BEFORE _parse_assignment — :458 precedes :462 on /draft (DB-081(b) explicit at :456-457); job slots in _read_dxf_with_deadline→run_in_job_slot→503 (:266-276); include_in_schema=False (:395,:444); shared limiter import (:76-82); _guard_finite_response aligns the utf-8 encode step with the sibling (DB-081(e), :213-231).

D-087-R006 (CAD files; authorization) — SATISFIED. services/api/app/api/v1/export_api.py (blob 4177ba09) exports {dxf,pdf,glb}; DXF-out is the open CAD interchange. Source: flag gate first (:230-231), all-methods 404; rate limit BEFORE body read/parse (:239 precedes :244/:262); run_in_job_slot→503 (:289-293); include_in_schema=False (:223); shared app.resilience.rate_limit primitives (:61-67).

D-087-R009 (unchanged boundaries; prohibition) — SATISFIED (four sub-claims on primary evidence):
- Zero new deps: rate_limit.py imports only asyncio/threading/time/collections(.abc)/typing + starlette.concurrency.run_in_threadpool (starlette already admitted via fastapi); requirements.txt/.in NOT in the c3e3df15 diff.
- app/main.py untouched: not among the 9 files; `grep scene_api|dxf_import_api|export_api services/api/app/main.py` = NONE → routes stay UNMOUNTED.
- Absent from OpenAPI: include_in_schema=False on all 4 endpoints + throwaway-app OpenAPI-absence tests (test_scene/dxf/export).
- Existing app/resilience modules untouched: only NEW rate_limit.py in the diff; breaker/budget/cache/config/fetcher/metrics/retry/transport/__init__ are forbidden_paths and absent from the diff (docstring :9-13 states it does not import/extend them). Max-envelope route not in the 9 files (untouched).

D-066-R001 (code-graph nav block; obligation) — SATISFIED. tasks/M5-T111.json inputs[] carries the "CODE-GRAPH NAVIGATION BLOCK (D-066-R001; graph REGENERATED at this contract seam, 844 files / 18356 nodes / 7841 edges)" naming each route's sole importer (its own test), that app/main.py imports none, the READ-ONLY neighbours, and "Run `python tools/code_graph/query.py --no-regen impact <path>` before sweeps"; reports/M5-T111-G0.md (:28-29) corroborates. Graph advisory; I verified the consumer claims directly in source (main.py + route imports above).

(Part 4 end; reviewer findings + prohibited sweep + verdict follow.)

---

M5-T111 DCV — part 5/5: REVIEWER FINDINGS, PROHIBITED SWEEP, VERDICT

REVIEWER ADVISORIES (none undercuts a cited requirement; none blocks this UNMOUNTED packet):
- G3 (code-reviewer) A1-A5: HEAD/OPTIONS unasserted (behaviour verified correct); AS-1 dict-form scan gap (isinstance + behavioural 429 tests are primary); cosmetic docstring path in scene_api; the 256 KiB body ceiling deferred to PKT-H (kept fail-closed, routed DB-D1/DB-D2); a 3.12 real-runner deadline test. All non-blocking; reviewer re-ran ruff/183-pytest/modularity and confirmed 9 paths, zero deps, main.py untouched, byte-stability.
- G4 (qa-engineer) gaps 1-5: lock-contention untested; XFF-not-trusted prose-only; HEAD/OPTIONS unasserted (verified 404 byte-parity incl. HEAD/OPTIONS); AS-1 substring scan; route-level slot-hold not e2e. All advisory; each AS keeps a reddening test — G4 re-ran 4 named mutants + 1 own IN-PROCESS, all RED for the right reason, baselines GREEN; confirmed only 2 route-local-limiter tests removed (properties migrated to the shared pack), nothing else weakened (git diff 275ef85f..c3e3df15).
- G5 (security-reviewer) F1 (MEDIUM, MUST-FIX-BEFORE-ENABLE): pre-thread-start cancel-window job-slot leak (Σ48>anyio-40 pool). NOT reachable while UNMOUNTED, fails CLOSED (availability only — no bypass, no data exposure), recorded as a PKT-H mount precondition. This is CONSISTENT with D-087-R009 ("the unmounted route and its mount preconditions stand"), not a violation of this packet. F2-F4 LOW, fail-closed PKT-H carry-forwards (F4 = the same 256 KiB ceiling, already routed). No blocking finding.

PROHIBITED-ACTION SWEEP (all clear): NOT accepted — state.json /active_tasks, packet status awaiting_gate, and NO task_verifications row keyed to M5-T111 in D-087 (36 rows) or D-066 (76 rows); the only "M5-T111" string in D-087 verification.json is inside M5-T114's DCV evidence (a disjointness note). NOT on main — c3e3df15 not on main; rate_limit.py absent on origin/main. PR #241 OPEN, mergedAt=null, title "…DO NOT MERGE until owner authorizes". No open blocker (4 open) references M5-T111 in affects or detail. Nothing merged/accepted/dispatched/deployed/installed/purchased/closed.

VALIDATOR NOTE: validate_directive_compliance.py --check SKIPPED per your allowance. Registry integrity is settled by: (1) evaluate_task_refs loaded D-087+D-066 with invalid_refs=[] (the loader fails closed on directive integrity errors); (2) the source-002 amendment IS reflected — requirements.json R011/R012 anchor to source-002-amendment.md; (3) green control-plane CI at 0c24a8b5 and fc76a09f. No missing/weakened/combined/invented requirement bearing on M5-T111.

RESULT PER REQUIREMENT: D-066-R001 SATISFIED; D-087-R001 SATISFIED; R002 SATISFIED; R003 SATISFIED; R004 SATISFIED; R006 SATISFIED; R009 SATISFIED. Zero VIOLATED/UNVERIFIABLE.

M5-T111 DCV VERDICT: PASS 7/7
END-OF-REPORT
