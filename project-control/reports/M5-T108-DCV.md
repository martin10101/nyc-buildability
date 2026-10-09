# M5-T108 — directive-compliance verification (directive-compliance-verifier "dcv-t108", read-only)

> Transmission history: pinned at 32b8aacb, delivered as seven SendMessage parts (the up-front restamp predicate, a path
> correction for the route file - app/api/v1/, blob unchanged - then 1/5..5/5) ending with END-OF-REPORT; no truncation.
> Joined verbatim (transport wrapper tags removed only). Validator EXIT 0 plus a hand-match of every cited digest. The task
> passed one FAIL -> rework -> three-reviewer delta cycle (round-1 G4 F1 and G5 MEDIUM 1).

---

M5-T108 DCV — restamp pre-authorization (UP FRONT). PINNED HEAD at start = 32b8aacb78a1d8826146040938898f64e372fd93 (branch candidate/D-024-mrl-option-b).

BLOB-LEVEL PREDICATE. My forthcoming verdict holds at any later HEAD H' WITHOUT re-review iff ALL of these blob identities are byte-stable (git rev-parse H':<path>):
- services/api/app/drawings/dxf_import.py == 124ad72b
- services/api/app/api/routes/dxf_import_api.py == eacb56b8
- services/api/tests/drawings/test_dxf_import.py == 8b64e4a9
- services/api/tests/drawings/test_dxf_import_api.py == 2d6edbbd
- project-control/reports/M5-T108-producer-report.md == 1f42b2f0
- AND project_control._task_git_identity(dr, task) for M5-T108 == reports/M5-T108.json content_manifest_sha256 == 2873d915 (the G2/G3/G4/G5 stamps).
(I will independently confirm each of these; if any differs from the values above my report will say so.)

DISJOINT-PEER TOLERANCE (broad). Any of the following landing between my freeze and the accept/record does NOT void the verdict, provided the blobs above stay byte-stable:
- other tasks' source files, gates, reports, material commits, and accepts;
- other directives' requirement binds, digest resyncs, and audit_log entries;
- the orchestrator writing MY v2 verification rows for M5-T108 (with the attendant directive_registry digest resyncs + audit entries);
- DISCOVERY_BACKLOG.md rows and contract-seam sweep lines;
- lifecycle-only packet changes to M5-T108.json / state.json (status transitions, reviewer lists, worktree fields) that do NOT alter the content_manifest_sha256 / _task_git_identity above.
Any change to the six identities in the predicate DOES void it and requires a delta re-review.

Full requirement rows, findings, and the final verdict line follow in subsequent parts.

---

M5-T108 DCV — CORRECTION to my restamp predicate (path only; the blob SHA is unchanged and confirmed).

The route file's path in my predicate should read services/api/app/api/v1/dxf_import_api.py (NOT app/api/routes/...). I verified at HEAD 32b8aacb: git ls-tree shows exactly one dxf_import_api.py in the tree, at app/api/v1/, blob eacb56b8101a112d68726c6819ab1a5d088e4107 — matching the packet's allowed_paths and the value you gave. So the predicate row is:
- services/api/app/api/v1/dxf_import_api.py == eacb56b8

All other four blobs confirmed byte-identical at HEAD:
- services/api/app/drawings/dxf_import.py == 124ad72b ✓
- services/api/tests/drawings/test_dxf_import.py == 8b64e4a9 ✓
- services/api/tests/drawings/test_dxf_import_api.py == 2d6edbbd ✓
- project-control/reports/M5-T108-producer-report.md == 1f42b2f0 ✓

Predicate and disjoint-peer tolerance otherwise stand as sent.

---

M5-T108 DCV REPORT — PART 1/5 (identity + applicability). PINNED HEAD 32b8aacb.

FROZEN IDENTITY — CONFIRMED (primary: git + project_control._task_git_identity).
- project_control._task_git_identity(dr, task) at live HEAD = 2873d915f97d352ce0683e9acbb7c14f320f3ab1457158a1ee5cf6d533c63fc1.
- Equals reports/M5-T108.json content_manifest_sha256 (2873d915) AND the G2/G3/G4/G5 gate stamps (each gates/M5-T108-G{2,3,4,5}.json content_manifest_sha256 = 2873d915). Match on all six.
- Frozen-head pattern verified: submit at 5bc472e9 (G2 there), G3/G4/G5 recorded at peer head 8273c688, live HEAD 32b8aacb — identity byte-stable across all three because the 5 allowed-path blobs are unchanged. _task_git_identity fails closed for a reviewed_sha != HEAD (by design); at HEAD it resolves to the frozen 2873d915.

BLOB PREDICATE — all 5 confirmed byte-identical at HEAD (git rev-parse HEAD:<path>):
dxf_import.py 124ad72b; app/api/v1/dxf_import_api.py eacb56b8; test_dxf_import.py 8b64e4a9; test_dxf_import_api.py 2d6edbbd; M5-T108-producer-report.md 1f42b2f0. (Route path is app/api/v1/, per my earlier correction.)

APPLICABILITY == CITED — CONFIRMED (primary: directive_registry.load_registry().evaluate_task_refs(task)).
- ok=True; missing_ids=[]; invalid_refs=[]; unresolved=[]; reasons=[].
- applicable_ids == cited_ids == [D-066-R001, D-083-R001, D-083-R006, D-087-R001, D-087-R002, D-087-R006, D-087-R007, D-087-R009] (8).
- Cross-checked by hand against each requirements.json applicability.task_ids: D-087 {R001,R002,R006,R007,R009} (R003/R004/R005/R008/R010/R011/R012 correctly NOT applicable to M5-T108); D-083 {R001,R006}; D-066 {R001}. Exact match to tasks/M5-T108.json directive_refs and reports/M5-T108.json applicable_requirements.

Requirement rows follow in parts 2-3.

---

M5-T108 DCV REPORT — PART 2/5 (D-087 requirement rows; each judged on reproduced primary evidence).

D-087-R001 (obligation; capacity via contracted/claimed/gated packets) — SATISFIED. tasks/M5-T108.json is a full packet (required_gates G0,G2,G3,G4,G5; producer backend-engineer); progress_log: claimed 20% at seam 11089429 then in_progress; gates/M5-T108-G{0,2,3,4,5}.json all result=PASS. No state/gate skipped. M5-T108 is in D-087-R001 applicability.task_ids.

D-087-R002 (prohibition; pairwise-disjoint paths + own worktree) — SATISFIED. reports/M5-T108-G0.md disjointness table: EMPTY overlap vs all 20 active tasks. packet.worktree = ...\wt-m5t108 (one). git show --stat 2df81013 and 5bc472e9: BOTH material commits touch ONLY the 5 allowed paths, nothing else. Route tests placed in tests/drawings/ (not tests/api/**) to stay disjoint from the frozen M4-T005 glob services/api/tests/api/** (packet input line 16) — verified allowed_paths use tests/drawings/.

D-087-R006 (DXF in-path) — SATISFIED.
- candidates->roles->draft via validate_proposed_massing: dxf_import.py:315 list_candidates; :479 build_draft (roles from RoleAssignment only) calls validate_proposed_massing at :531.
- units vs known dimension: _resolve_scale dxf_import.py:391 (confirmed_units XOR known_length_ft+measured_length; ambiguous refuses, import.py:398).
- discrepancies shown not reconciled: dxf_import.py:423-434 units_mismatch; test_units_mismatch_is_shown_never_reconciled (test_dxf_import.py:194) — scale stays 1.0, discrepancy present.
- parse-time (b)-(e) at route dxf_import_api.py: (b) ceiling BEFORE materialize :266-279 via T053 _read_body_within_ceiling; (c) off-loop deadline+rate-limit :246-249 asyncio.wait_for(run_in_threadpool(read_dxf),10.0) + :260 30/60s; (d) sniff_dxf_media :281 + fixed _IMPORT_DXF_LIMITS :99 (never from input); (e) persists nothing (no storage call anywhere). Each AS-1 control has a test + reddening mutant (test_dxf_import_api.py:173-318). pytest: 57 passed.

D-087-R007 (ASCII-only; binary refused; no DWG lib) — SATISFIED. sniff_dxf_media refuses raw[:18]==b"AutoCAD Binary DXF" (dxf_import.py:254); tests api:214 + import:303. Imports are stdlib + fastapi/starlette + app.* only (dxf_import.py:35-51; dxf_import_api.py:42-72); requirements.txt/.in untouched by both commits — no DWG library.

D-087-R009 (unmounted; zero new deps; boundaries) — SATISFIED. main.py has no dxf_import ref at HEAD (git grep empty); both endpoints include_in_schema=False (:360,:401); dual-flag gate -> generic 404 (:257,:186-189); test_route_is_unmounted_in_the_real_app (api:141) asserts both paths absent from real_app.routes AND openapi().paths. config.py + dxf_reader.py + requirements untouched by both commits. DXF_IMPORT_ENABLED default-off (dxf_import_enabled False when absent, :126-135). Zero new deps.

D-083 + D-066 rows in part 3.

---

M5-T108 DCV REPORT — PART 3/5 (D-083 + D-066 rows; round-1 defect-fix independent reproduction).

D-083-R001 (prohibition; never present a permitted/"maximum allowed" building) — SATISFIED. Honesty vocab constants dxf_import.py:75-77 (DRAFT_SOURCE_LABEL="Proposed - not a city record"); candidates notice dxf_import_api.py:389-392 ("Nothing here is a city record or a permitted value"). test_draft_provenance_is_honest_and_not_upgraded (test_dxf_import.py:271-277) asserts NONE of {"permitted","approved","maximum allowed","as of right","demonstrated maximum"} appear in provenance+massing. No regulatory-ceiling surface exists here; no unqualified maximum-building claim. Observed absence reproduced by the passing test.

D-083-R006 (input-precision provenance; imported drawing, never upgraded) — SATISFIED. DRAFT_INPUT_PRECISION="imported drawing - not survey-confirmed" (dxf_import.py:76); provenance dict build_draft:541-556 carries precision/input_class/label; single constant, no code path upgrades it (scale conversion changes draft geometry only, not the precision label). Tests: test_dxf_import.py:273 asserts precision==DRAFT_INPUT_PRECISION; test_dxf_import_api.py:106 asserts response provenance.precision=="imported drawing - not survey-confirmed"; candidates notice also carries "not survey-confirmed" (api:390).

D-066-R001 (navigation block present + query.py --no-regen instruction) — SATISFIED. tasks/M5-T108.json inputs line 19 = the CODE-GRAPH NAVIGATION BLOCK (graph regenerated at seam, 832 files/17984 nodes/7700 edges; names dxf_reader.py consumers, validate_proposed_massing location in app/scenario/proposal.py, forbidden neighbors; instructs "python tools/code_graph/query.py --no-regen impact <path> before sweeps"). reports/M5-T108-G0.md corroborates the block names consumers/forbidden neighbors + the query.py --no-regen instruction.

ROUND-1 DEFECT FIXES — independently reproduced (red/green mutant proof read in source, not taken from reviewer claims):
- G4 F1 (user-assigned ring): _select_ring dxf_import.py:456. Live: test_dxf_import.py:183 + test_dxf_import_api.py:348 assert vertices[0]==[990000,200000] (ring B, index 1). Reddening mutants import.py:360 (always ring0) + :370 (largest ring) each assert [985000,195000] (ring A) — ring A deliberately larger (200x200 vs 80x100) so both wrong-selection modes are caught. Proper displaced-field proof. CLOSED.
- G5 MEDIUM 1 (non-finite measured dims -> untyped 500): service guard _measured_is_finite dxf_import.py:236 + refusal at :330; route pre-render guard _guard_finite_response dxf_import_api.py:192. Tests import.py:234/:386, api:367/:378. Mutant api:390 neuters BOTH guards and asserts a BARE untyped 500 with NO correlation id — proving the guards make it typed. CLOSED.

Findings + harness + verdict in parts 4-5.

---

M5-T108 DCV REPORT — PART 4/5 (findings, prohibited-action sweep, harness).

FINDINGS
- F1 (identity/applicability): stable and exact — see part 1. No frozen-evidence mismatch; accept will not fail-closed on identity at this HEAD.
- F2 (gate supersession): G4 and G5 histories show round-1 FAIL superseded by round-2 PASS, both round-2 records at content_manifest 2873d915 (the current frozen identity); G3 PASS both rounds. All 5 gate records present and PASS at the frozen identity.
- F3 (blobs): all 5 byte-identical to the predicate values.
- F4 (sweep clean): below.
- F5 (path note, NOT a defect): the route is app/api/v1/dxf_import_api.py (packet allowed_paths + tree agree; only one dxf_import_api.py in the tree). My first-message predicate said routes/ — corrected; blob eacb56b8 unchanged.

PROHIBITED-ACTION SWEEP — all clear (primary evidence):
- NOT accepted: state.json active_tasks contains M5-T108; accepted_tasks does NOT (it ends at M5-T105); tasks/M5-T108.json status=awaiting_gate.
- NO verification row yet: grep -c "M5-T108" = 0 in each of D-087/D-083/D-066 verification.json.
- NOT on main: git branch -a --contains 5bc472e9 -> not on main; git cat-file -e origin/main:services/api/app/drawings/dxf_import.py -> ABSENT on origin/main.
- PR #241 untouched: gh pr view 241 -> state OPEN, mergedAt null, headRefName task/M5-T002-scenario-endpoint (unrelated; "DO NOT MERGE" title). Not this task's branch.
- NO blocker names it: grep -rn "T108" across 26 blocker files -> zero references (affects + detail).
- Nothing merged/dispatched/deployed/installed/purchased/closed: route ships UNMOUNTED (absent from OpenAPI), zero new deps, feature flag default-off.

HARNESS (primary reproduction):
- pytest (cwd services/api): `python -m pytest tests/drawings/test_dxf_import.py tests/drawings/test_dxf_import_api.py -q` -> 57 passed in 4.70s. Matches the documented 57.
- CI at frozen HEAD: gh run list --branch candidate/D-024-mrl-option-b -> the top run is HEAD 32b8aacb ("Review-record seam seq 129 wave 19, M5-T106 correction deltas") with CI=success, context-budget=success, secret-scan=success. Control-plane CI green at the reviewed head.
- validate_directive_compliance.py --check: launched once (per instruction), running ~12 min; exit code reported in part 5. I did NOT run tools/test_directive_compliance.py (hard prohibition honored).

Verdict line follows in part 5 after the validator exit code lands.

---

M5-T108 DCV REPORT — PART 5/5 (harness close-out + verdict).

VALIDATOR: `python tools/validate_directive_compliance.py --check` completed with VALIDATOR_EXIT=0 (PASS). Run once, direct exit code. (tools/test_directive_compliance.py NOT run — hard prohibition honored.)

DIGEST HAND-VERIFICATION (independent of the validator; directive_registry.sha256_text_artifact vs manifest.json), all three cited directives:
- D-087: requirements.json ddec99c1 MATCH; source-001.md 34c3dd64 MATCH; source-002-amendment.md 4eea66c6 MATCH; locked_requirement_ids=12 (== requirement_count). Amendment (source-002 "Go" + rundown) reflected: R011/R012 anchor to it.
- D-083: requirements.json 1edb1a86 MATCH; source-001.md 7f11a99f MATCH; locked=13. No amendments (consistent).
- D-066: requirements.json e9b7ea9f MATCH; source-001.md 4cb05c94 MATCH; locked=4. No amendments (consistent).
- ALL_DIGESTS_MATCH: True.

REQUIREMENT TALLY (each judged on reproduced primary evidence; details in parts 2-3):
- D-087-R001 SATISFIED
- D-087-R002 SATISFIED
- D-087-R006 SATISFIED
- D-087-R007 SATISFIED
- D-087-R009 SATISFIED
- D-083-R001 SATISFIED
- D-083-R006 SATISFIED
- D-066-R001 SATISFIED
VIOLATED: 0. BLOCKED: 0. UNVERIFIABLE: 0.

RESTAMP PREDICATE (recap): PASS holds at any later HEAD H' iff blobs unchanged — dxf_import.py 124ad72b, app/api/v1/dxf_import_api.py eacb56b8, test_dxf_import.py 8b64e4a9, test_dxf_import_api.py 2d6edbbd, M5-T108-producer-report.md 1f42b2f0 — AND _task_git_identity==2873d915. Disjoint-peer tolerance as sent in my first message (other tasks' files/gates/accepts, other directives' binds, my v2 rows + digest resyncs + audit entries, DISCOVERY_BACKLOG rows/sweep lines, lifecycle-only packet changes). Any change to those six identities voids it.

Producer = backend-engineer; verifier = dcv-t108 (producer != verifier). Task NOT accepted; no verification row; not on main; PR #241 untouched; no blocker names it.

M5-T108 DCV VERDICT: PASS 8/8
END-OF-REPORT
