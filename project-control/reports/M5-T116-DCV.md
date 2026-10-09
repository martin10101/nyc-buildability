# M5-T116 — directive-compliance verification (directive-compliance-verifier "dcv-t116", read-only)

> Transmission history: pinned at 2fdca967 (HEAD advanced to b1c43167 during the review through disjoint peer commits;
> the three T116 blobs and identity 23fd4149 stayed byte-stable), delivered as four SendMessage parts (1/4..4/4)
> ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed
> only). Part 1 carries the blob-level restamp predicate with broad disjoint-peer tolerance.

---

M5-T116 DCV — part 1/4: PIN, restamp pre-authorization, harness.

PIN: I started at HEAD 2fdca967 (as expected). During review the orchestrator advanced HEAD linearly to b1c43167 ("Accept seam: M5-T117 ACCEPTED") via 3be7c22f (M5-T118 review-record). 2fdca967 is an ancestor of b1c43167; M5-T116 material untouched (see F1).

RESTAMP PRE-AUTHORIZATION (blob-level predicate): my PASS holds at any accept-time HEAD where all three reviewed blobs are byte-identical AND the task identity is unchanged:
- export_service.py 25437d25822b3ad0c249261d9688b3cc5f87296b
- test_export_service.py fb1ea711eec6b6753c1352a43fcac2b69f34de4c
- M5-T116-producer-report.md bb2a479d005cd56a280a1d730e915099d0870900
- identity 23fd4149109076437121ae6282d9b09539a9a4e3d4641c1decfe53268e5d8e59

Broad disjoint-peer tolerance (all pre-authorized): commits touching other tasks' files/gates/material (M5-T117, M5-T118, M5-T119, any new packets); other directives' registry binds/digest-resyncs/audit entries; the orchestrator adding MY M5-T116 rows to D-066/D-083/D-087 verification.json with digest resyncs + audit entries; DISCOVERY_BACKLOG rows + sweep lines; lifecycle-only M5-T116 packet changes (status/gate-history/progress) that leave the 3 blobs unchanged. The already-observed advance 2fdca967 → 3be7c22f → b1c43167 is within tolerance (verified: 3 blobs unchanged, identity 23fd4149 holds, no M5-T116 verification row added).

HARNESS (reproduced by me, cwd services/api): `ruff check .` → All checks passed; `pytest tests/cad -q` → 464 passed. Mechanical (registry API): evaluate_task_refs ok=True, applicable_ids == cited_ids (7 IDs), missing/invalid/unresolved all empty; _task_git_identity == 23fd4149 (== reports/M5-T116.json content_manifest_sha256 == G2/G3/G4/G5 stamps). I did NOT run validate_directive_compliance.py --check: the load-bearing rows are settled by primary evidence (registry API reproduced directly, gate records, source + tests read); the full validator is CI's control-plane job at the pushed accept head. Round-2 head is NOT yet pushed (local-only); the earlier M5-T116 submit head pushed CI green; offline ruff+pytest is authoritative for this pure-geometry api module.

---

M5-T116 DCV — part 2/4: requirement rows (primary evidence).

D-087-R001 (obligation, capacity/gated packet) — SATISFIED. M5-T116 is a fully contracted/claimed/gated ledger packet: G0 PASS (gates/M5-T116-G0.json, reviewed_sha 07e028ce = "D-089 wave-3 contract seam"); claim seam c375457c ("G0 PASS... claimed... progress 20"); G0/G2/G3/G4/G5 all recorded; runs concurrently with disjoint D-087 packets. No state or gate skipped.

D-087-R002 (prohibition, no interference) — SATISFIED. G0 disjointness table (M5-T116-G0.md:31-54): 19 active neighbors, every row "none - EMPTY overlap". One worktree wt-m5t116 (packet.worktree). Both material commits touched EXACTLY the 3 allowed paths: 99c8457f (round-1) and c903307e (round-2), `git show --stat` = export_service.py + test_export_service.py + producer-report.md only. Forbidden paths (writers, claim_words, app/scenario, main.py, api, requirements) untouched.

D-066-R001 (obligation, navigation block) — SATISFIED. Packet M5-T116.json inputs carry the CODE-GRAPH NAVIGATION BLOCK (graph regenerated, 844 files/18356 nodes/7841 edges; names consumers export_api.py + tests as READ-ONLY, forbidden neighbors, and the `tools/code_graph/query.py --no-regen impact <path>` instruction before sweeps; graph advisory). G0 report:28-29 corroborates.

D-083-R001 (prohibition, claim-class / no caller text) — SATISFIED. export_service.py:320-337 `_reconcile`/`_reconcile_triangulation` build the detail SERVER-SIDE from the fixed reject code only — no caller value echoed; :110-114 `_SOURCE_LABELS` are only "Proposed - not a city record" / "Generated building option"; no "maximum allowed building" / permitted wording anywhere. Proven: test_reconciled_refusal_never_echoes_a_hostile_coordinate (:190) and test_distinct_vertex_bowtie_is_a_reconciled_typed_refusal asserts detail == exact server template "the glb footprint could not be triangulated (reject_code=self_intersection)" (:701). G4/G5 independently reproduced the no-leak.

---

M5-T116 DCV — part 3/4: requirement rows (cont.).

D-087-R003 (authorization, 3D released / concave GLB caps) — SATISFIED. export_service.py:442-461 builds bottom+top caps from the public concave-safe `triangulate_polygon` (NOT a vertex-0 fan): bottom `[a,c,b]` faces -z, top `[n+a,n+b,n+c]` faces +z, side walls share the same prepared ring; :391-414 `_reject_non_simple_ring` adds the GEOS simplicity gate (LinearRing.is_simple; ShapelyError/ValueError → typed self_intersection), called at :444. Tests: test_glb_caps_lie_inside_the_footprint_and_sum_to_its_area[L|U|convex] (:442) with area-sum + containment + winding oracles computed IN-test (not imported); vertex-0-fan mutation (:483); distinct-vertex-bowtie refusal x3 (:691) + gate-drop mutant (:706). Reproduced: 464 passed. UNMOUNTED, under full gates; round-1 G3 FAIL (bowtie) → round-2 PASS.

D-087-R006 (authorization, CAD files / DXF path) — SATISFIED. This packet hardens the pure export SERVICE (DXF/PDF/GLB). DXF & PDF outputs stay byte-identical (they bypass `_build_prism_mesh`; owner-samples golden green within the 464; G4/G5 confirmed byte-identity). Native DWG stays refused (test_unsupported_format_is_refused for "dwg", :310) — R007 hold intact. Zero new deps.

D-087-R009 (prohibition, unchanged boundaries) — SATISFIED. Zero new dependencies: shapely==2.0.7 already pinned (requirements.txt:508, requirements.in:51); material commits touch no requirements/lockfile (3 allowed paths only). UNMOUNTED: app/main.py untouched (forbidden; reviewers confirmed byte-unchanged, no `export` ref). Writers/claim_words/app/scenario untouched (forbidden paths; material scope = 3 files). PR #241 OPEN + mergedAt null ("DO NOT MERGE until owner authorizes"). All gates G0–G5 present. Material (99c8457f, c903307e) NOT on main.

---

M5-T116 DCV — part 4/4: gates, sweep, findings, verdict.

GATES (all PASS; producer = backend-engineer, none reviewed own work):
- G0 orchestrator/administrative PASS; G2 orchestrator/self_check PASS; G3 code-reviewer PASS (history: round-1 FAIL recorded); G4 qa-engineer PASS; G5 security-reviewer PASS. All four G2/G3/G4/G5 content_manifest_sha256 = 23fd4149 = frozen identity. Rework cycle tracked: SAME reviewers re-ruled at the re-frozen head ab9001ea (delta c903307e).

FROZEN IDENTITY: _task_git_identity = 23fd4149 == reports/M5-T116.json content_manifest_sha256 == G2/G3/G4/G5 stamps. The 3 reviewed blobs are byte-stable across c903307e → ab9001ea → 2fdca967 → HEAD b1c43167.

PROHIBITED-ACTION SWEEP (clean): not accepted (status awaiting_gate; accepted_tasks holds only the unrelated old M0-T116); zero M5-T116 verification rows in D-087/D-083/D-066 verification.json; material not on main; PR #241 untouched/unmerged; no open blocker names M5-T116 (grep over blockers/ empty; open blockers B-001/010/011/026 unrelated).

REVIEWER ADVISORIES: none undercuts a cited requirement. Round-1 G4/G5 advisories (bowtie gap; prepared-vs-raw fixture) CLOSED in round 2; round-2 G5 leaves one benign INFO (the `_reject_non_simple_ring` except omits an unreachable TypeError on the proven-clean prepared ring) — non-blocking, future-change note only.

FINDINGS:
- F1 (informational): HEAD advanced 2fdca967 → b1c43167 (disjoint M5-T117 accept + M5-T118 review-record) during review; M5-T116's 3 blobs byte-stable, identity 23fd4149 holds. Within my restamp tolerance.
- F2 (for accept): reports/M5-T116.json reviewed_sha is c903307e while G3/G4/G5 were recorded at ab9001ea — identical content_manifest 23fd4149, so identity-consistent; orchestrator restamps reviewed_sha to live HEAD at accept, v2 reviewed_manifest_sha256 from the gate records (23fd4149).
- F3 (benign INFO): the round-2 head is not yet pushed — CI control-plane/full-validator runs at the pushed accept head; offline ruff+pytest (464) reproduced locally is authoritative for this api module.

No requirement VIOLATED or UNVERIFIABLE. 7/7 SATISFIED.

M5-T116 DCV VERDICT: PASS 7/7
END-OF-REPORT
