# M5-T107 — directive-compliance verification (directive-compliance-verifier "dcv-t107", read-only)

> Transmission history: pinned at 0c76b136, delivered as five SendMessage parts (1/5..5/5) ending with END-OF-REPORT;
> no truncation. Part 1 carries the blob-level restamp predicate (seven blobs + identity a367f548) with broad disjoint-peer
> tolerance, explicitly including the M5-T106 accept seam that must land first. Joined verbatim (transport wrapper tags
> removed only). Validator EXIT 0 (one direct run). The task passed one FAIL -> rework -> four-reviewer delta cycle.

---

M5-T107 (D-087 PKT-E) DCV — final review at PINNED HEAD 0c76b136 (git rev-parse HEAD, recorded at start). Part 1/5: restamp pre-authorization, up front.

RESTAMP PREDICATE (blob-level). This PASS holds at any HEAD ≥ 0c76b136 at which BOTH hold:
(1) the seven M5-T107 material blobs are byte-identical at these git object SHAs (verified at HEAD via `git rev-parse HEAD:<path>`):
- services/api/app/scenario/scene_assembler.py = 57a8afde
- services/api/app/api/v1/scene_api.py = b2c14483
- services/api/app/connectors/building_footprints_arcgis.py = be407e64
- services/api/tests/scenario/test_scene_assembler.py = fd5c5587
- services/api/tests/scenario/test_scene_api.py = 94403239
- services/api/tests/connectors/test_building_footprints_arcgis.py = b1be2943
- project-control/reports/M5-T107-producer-report.md = 2b22fedf
(2) the path-scoped identity `project_control._task_git_identity(dr, task)` == a367f5488b8ad520c25dc2c26fe7bad2f2f1065a9442bf9c077a70697b33501e — which I recomputed at HEAD (resolved_sha 0c76b136, error None) and which equals reports/M5-T107.json content_manifest_sha256 AND the G1/G2/G3/G4/G5 content_manifest_sha256 stamps.

DISJOINT-PEER TOLERANCE (broad). The verdict is unaffected by, and a restamp may proceed across, any commit landing between freeze and record that does NOT change those seven blobs or the identity, explicitly including:
- the M5-T106 accept seam (which MUST land first) and any other task's files/gates/material/accepts;
- other directives' binds (D-066/D-083/D-087 and others);
- the orchestrator writing MY v2 verification rows into the D-066/D-083/D-087 verification.json with digest resyncs + audit_log entries;
- DISCOVERY_BACKLOG rows and contract-seam sweep lines;
- lifecycle-only packet changes to M5-T107 (status/progress/worktree/updated_at transitions, incl. awaiting_gate→accepted) that leave allowed_paths and the seven material blobs unchanged.

Note the gate stamps carry reviewed_sha 1f4933e8 (the disjoint M0-T161 peer commit) but identity a367f548 — byte-stable task identity across that peer commit, which is exactly the tolerance above. Round-1 G5 FAIL (F-1) is superseded at identity a367f548.

Parts 2-5 follow (requirement rows, sweep, findings, verdict). No waiting between them.

---

M5-T107 DCV part 2/5 — applicability + requirement rows (1 of 2).

APPLICABILITY: reg.evaluate_task_refs(task) at HEAD → ok=True; applicable_ids == cited_ids == [D-066-R001, D-083-R001, D-083-R002, D-087-R001, D-087-R002, D-087-R003, D-087-R009]; missing=[], invalid=[], unresolved=[]. Applicability EQUALS citation. 7 applicable requirements, judged individually below on primary evidence I reproduced.

D-066-R001 (navigation block present) — SATISFIED. Primary: tasks/M5-T107.json input line "CODE-GRAPH NAVIGATION BLOCK (D-066-R001; graph REGENERATED …832 files/17984 nodes/7700 edges)" naming consumers (building_footprints_arcgis imported only by its test; massing_model by its test READ-ONLY; glb_writer by tests/cad), the forbidden neighbours, and the `query.py --no-regen impact` instruction. Corroborated by reports/M5-T107-G0.md lines 25-26.

D-083-R001 (never permitted/approved/maximum-allowed; proposal = "Proposed - not a city record") — SATISFIED. Primary: grep of the three produced source files for barred claim words returns ONE hit — scene_assembler.py:29, a NEGATIVE disclosure ("…never permitted, approved, or [a maximum-allowed building]"). Test test_scene_assembler.py:299-312 (`test_as2_the_assemblers_own_labels_carry_no_barred_claim_word`) asserts contains_claim_word(text) is None for every assembler-emitted label/disclosure incl. GROUND_DATUM_DECISION strings. test_scene_assembler.py:291 asserts disclosure == "Proposed - not a city record". 193 tests pass.

D-083-R002 (three claim classes distinct; no demonstrated maximum) — SATISFIED. Primary: test_scene_assembler.py:288-296 asserts proposed source="proposed"/disclosure="Proposed - not a city record" vs generated source="generated_option"/disclosure="Generated building option" — the two kept distinct. Label constants live in massing_model.py:140-141 (read-only, M5-T106). No class-c "demonstrated maximum" claim exists (screened by :299-312).

D-087-R001 (capacity: contracted/claimed/gated packet run concurrently, no state/gate skipped) — SATISFIED. Primary: packet M5-T107.json cites D-087-R001; gates/M5-T107-G0.json PASS at 06db6449; progress_log shows claim at 11089429 with the full worktree path C:\…\wt-m5t107; orchestrator-dispatched subagent producer (backend-engineer); ran concurrently with M5-T106/T108/T109 (G0 disjointness table). Full gate chain G0→G1→G2→G3→G4→G5 all recorded — nothing skipped.

D-087-R002 (no interference: pairwise-disjoint allowed_paths + isolated worktree) — SATISFIED. Primary: I independently recomputed the intersection of M5-T107's 8 allowed_paths against every non-accepted task packet → NONE overlap. reports/M5-T107-G0.md:28-52 disjointness table = EMPTY overlap vs all active tasks. Both material commits (d3c47a85, 2c52ac6d) `git show --stat` touch ONLY allowed paths; one worktree wt-m5t107; route tests placed in tests/scenario to avoid the frozen M4-T005 tests/api/** glob.

Part 3 (D-087-R003, D-087-R009) next.

---

M5-T107 DCV part 3/5 — requirement rows (2 of 2).

D-087-R003 (3D massing in its real neighbourhood; all sub-items) — SATISFIED. Primary, all reproduced in source + tests (193 pass):
- section 2.1 payload: scene_assembler.assemble_scene (:521-551) returns MassingModel.as_dict() + scene_version/vertical_unit/context_buildings/provenance.
- ONE declared ground datum, both official defs disclosed, NAVD88→dictionary only: GROUND_DATUM_DECISION (:105-138, definitions_disclosed.city_dictionary + fgdc_metadata; navd88_attribution "stated ONLY by the City dictionary … Neither definition is reconciled"); test :131-134.
- zero/unverified grounds disclosed (never sea level): unverified_ground_policy (:133-137), _ground_status (:400-408); test :323-334.
- HEIGHT_ROOF above ground + height provenance threaded: HEIGHT_PROVENANCE (:145-149, height_reference/height_unit_basis) on the layer (:494); docstring :142-144 (G1 ADV-1).
- untrusted text escaped — values, KEYS, diagnostics: _escape_untrusted / _escape_untrusted_mapping (:370-392) applied to attributes keys+values, gaps[].raw, drift_signals, geometry_findings, geom_source, last_status_type (:435-456,:506-507); tests :378-410 incl. hostile-key/gap.raw/drift-name test + load-bearing mutation (:397-405).
- courtyard holes disclosed, never dropped: parts exterior+holes (:437-442), disclosure (:172-181); test :337-346 (mutation reddens on drop).
- typed refusals only: SceneAssemblyError (:221-229); the G5 F-1 OverflowError guard (:244-252); tests service-level :203-225 + reddening OverflowError mutation :228-252, route-level test_scene_api.py:244-247.
- UNMOUNTED route, off-loop deadline, bounded per-caller rate limit: scene_api.py include_in_schema=False (:265), flag-gated generic 404 (:271-272,:187-190), asyncio.wait_for(run_in_threadpool, timeout=SCENE_MAX_SECONDS=15) → 504 (:356,:90), rate limit _rate_limit_allows MAX=30/window=60/MAX_KEYS=4096 bounded+evicting fail-closed (:150-173) run before body/work (:277); tests OpenAPI-absent :189, 504+mutation :344-360, 429+mutation :271-283, key-bound eviction :292-331; connector called interactive+deadline test :424-435.
- connector riders DB-073 (a)-(g): building_footprints_arcgis.py diff d3c47a85 — (a) U+2028/2029 strip, (b) length-bound cid at source, (c) _sleep_within_deadline + pre-metadata _check_deadline, (d) _validate_deadline tz-naive→disallowed_request. Tests test_building_footprints_arcgis.py: (a):1224 (b):1242 (c):1253/1264 (d):1292 (reason tz_naive_deadline) (e):825 AST import-graph replaces grep (f):1304 advancing-clock trips on 2nd page (g):1333 ceiling between one/two-page sums — each with a reddening mutation.

D-087-R009 (unchanged boundaries) — SATISFIED. Primary:
- zero new dependencies: new modules import only stdlib (html, math, asyncio, functools, json, logging, time, uuid, datetime, typing) + already-admitted fastapi/starlette/shapely; requirements.txt/.in untouched (material-commit stat; also forbidden_paths).
- route UNMOUNTED: include_in_schema=False (:265); app/main.py in NEITHER material commit; test asserts URL absent from real_app.openapi().paths (:189).
- massing_model.py, proposal.py, app/cad, app/resilience untouched: absent from both `git show --stat` (d3c47a85, 2c52ac6d).
- no network in tests: fetch seam monkeypatched (test_scene_api.py:117,155); connector tests synthetic transport; 193 tests pass offline.

Part 4 (identity/gates/harness + prohibited-action sweep) next.

---

M5-T107 DCV part 4/5 — frozen identity, gates, harness, prohibited-action sweep, dependency.

FROZEN IDENTITY. _task_git_identity(dr, task) at HEAD = a367f5488b8ad520c25dc2c26fe7bad2f2f1065a9442bf9c077a70697b33501e (resolved_sha 0c76b136, error None). Equals: reports/M5-T107.json content_manifest_sha256 (a367f548); and the content_manifest_sha256 on G1, G2, G3, G4, G5 gate records. The seven material blobs at HEAD match the pre-auth list exactly (part 1). Confirmed a manifest digest, not a git object.

GATES (project-control/gates/M5-T107-*.json).
- G0 PASS (orchestrator, administrative) reviewed_sha 06db6449, identity 67bda6e4 (contract-time, pre-production — correct).
- G1 PASS data-contract-verifier; G3 PASS code-reviewer; G4 PASS qa-engineer; G5 PASS security-reviewer — all four at identity a367f548, reviewed_sha 1f4933e8, report_file *-rework.md. Each history[] shows the prior round entry; G5 history = FAIL (round 1) then PASS — the round-1 F-1 is superseded at a367f548.
- G2 PASS orchestrator self_check at a367f548. All six required gates (G0-G5) recorded PASS.

HARNESS (independently run at HEAD).
- `python tools/validate_directive_compliance.py --check` → exit 0 (direct exit code, no pipe). Run once.
- `cd services/api && python -m pytest tests/scenario/test_scene_assembler.py tests/scenario/test_scene_api.py tests/connectors/test_building_footprints_arcgis.py -q` → 193 passed, exit 0.
- Per the DCV standing instruction I did NOT run tools/test_directive_compliance.py (full-suite = CI's job; ~16h against the grown registry).
- The producer's [ORCH-HARVEST] full-suite numbers (1823/1842 passed, Python 3.11 local) are the producer's CLAIM; I reproduced the authoritative subset + validator instead — no discrepancy.

PROHIBITED-ACTION SWEEP — all clear.
- Not accepted: tasks/M5-T107.json status = awaiting_gate; no accepted/done marker in state.json or master_plan.json.
- No verification row: grep of every project-control/directives/*/verification.json for M5-T107 → none.
- Not on main: HEAD contained only in candidate/D-024-mrl-option-b; scene_assembler.py ABSENT on origin/main; 2c52ac6d NOT an ancestor of origin/main.
- PR #241 untouched: gh pr view → state OPEN, branch task/M5-T002-scenario-endpoint, updatedAt 2026-08-20 (unrelated, pre-dates this task).
- No open blocker references M5-T107 (word-bounded grep of project-control/blockers/).

DEPENDENCY M5-T106. Recorded: tasks/M5-T107.json dependencies = [M5-T101, M5-T106]; G0 report line 55 states the ledger refuses M5-T107 accept until M5-T106 is accepted. M5-T106 current status = awaiting_gate (NOT yet accepted) — so acceptance of M5-T107 remains correctly blocked. This is sequencing working as designed, not a defect in M5-T107; the orchestrator must accept M5-T106 first.

Part 5 (findings + verdict) next.

---

M5-T107 DCV part 5/5 — findings and verdict.

FINDINGS.
- F-1 (informational, not blocking): the evidence-map harness lines are labelled [ORCH-HARVEST] at Python 3.11 local (1823 then 1842 passed). I treated those as a producer claim and reproduced the authoritative evidence myself at HEAD (validator --check exit 0; the three documented test files = 193 passed; blob SHAs; identity). No discrepancy found.
- F-2 (informational, not blocking): services/api/app/connectors/building_footprints_geometry.py is listed in allowed_paths but was touched by neither material commit. allowed_paths is a ceiling, not a floor — no violation; the connector production+geometry files being unchanged in round 2 matches the evidence-map claim (round-2 commit 2c52ac6d does not list the connector).
- F-3 (sequencing reminder, not a defect of this task): M5-T106 (declared dependency) is still awaiting_gate. M5-T107 must NOT be accepted until M5-T106 is accepted (enforced by the ledger; G0 report line 55). Acceptance is otherwise unblocked once M5-T106 lands.

No requirement is VIOLATED, BLOCKED, or UNVERIFIABLE. All 7 applicable requirements SATISFIED on reproduced primary evidence:
- D-066-R001 SATISFIED
- D-083-R001 SATISFIED
- D-083-R002 SATISFIED
- D-087-R001 SATISFIED
- D-087-R002 SATISFIED
- D-087-R003 SATISFIED
- D-087-R009 SATISFIED

Producer = backend-engineer; verifier = directive-compliance-verifier (me) ≠ producer. Read-only throughout: no project_control write verbs, no git/gh writes, no file writes outside my own agent-memory scope (none written). Restamp predicate + disjoint-peer tolerance are in part 1; apply to the M5-T106 accept seam and my v2 rows.

M5-T107 DCV VERDICT: PASS 7/7
END-OF-REPORT
