# M5-T081 / M5-T086 — directive-compliance verification (directive-compliance-verifier "dcv-cad", read-only; joint DCV for M5-T081 and M5-T086)

> Transmission history: one joint verification pinned at 94182057 (live HEAD advanced through disjoint
> orchestrator seam commits to fa7e5fae during the review), delivered as SEVEN SendMessage parts: part 1
> (pinned head + blob-level restamp predicate + disjoint-peer tolerance, 09:07Z), parts 2-6 (identities,
> gates, every requirement row, prohibited-action check, findings F1-F6, 09:36Z-09:44Z) and a final part
> (validator run, predicate re-check at fa7e5fae, verdicts, 14:49Z) ending with END-OF-REPORT; no truncation.
> Joined verbatim in delivery order by the orchestrator (transport wrapper tags removed only); saved
> identically as M5-T081-DCV.md and M5-T086-DCV.md.
> Validator note: the verifier's single validator run overlapped an orchestrator seam commit (5e9dbd07)
> and reported two transient c14 digest mismatches (D-066, D-087) that the verifier traced to that
> overlap and showed consistent at every committed state since; the harness evidence is the CI
> control-plane job (SUCCESS at f6116a5c and 6c79cd88, both carrying all 8 predicate blobs).
> Orchestrator disposition of findings: F1-F6 are non-blocking for both task rows; all six are routed to
> docs/DISCOVERY_BACKLOG.md DB-057. The optional F3 evidence-map rewording was NOT applied (the map blob
> stays frozen at 6cce2a91); the F3 caveat is carried in the D-087-R007 verification row instead.

---

DCV M5-T081 + M5-T086, part 1: pinned head and restamp pre-authorization (verification still running).

PINNED = 94182057f9034a6c98c86ab9ef9aef97d01e6fb2 (primary checkout ctl24, branch candidate/D-024-mrl-option-b; task paths clean).

Identity at PINNED (reproduced with project_control._task_git_identity, read-only):
- M5-T081 = 9700b33befc8789a9f12963f8e9284f52ab602c21150c206f5ed28ad314040cf (matches reports/M5-T081.json, reviewed_sha 0ffe581c); packet material digest 7c5ef384aab464fac7e75e565c60e85751d4799e814767483aadb6ce2d329fcf.
- M5-T086 = f0c6963d13a7d72beca146eb1341f4eff7bc0981d23697abc2e805995b52caf2 (matches reports/M5-T086.json, reviewed_sha 5151c2e4); material digest fef3ec20ceceea4af0f2e9fc5a82f2419afb8fae259c757956cd519519ddc059.
- evaluate_task_refs ok for both; applicable == cited (T081: 7 IDs; T086: 6 IDs).

RESTAMP PREDICATE (blob level). My verdict for a task carries to any later head H if ALL of these hold at H:
1. Blobs are unchanged.
   T081: app/cad/dxf_writer.py 152f1f2e; tests/cad/test_dxf_writer.py 2aa45291; M5-T081-producer-report.md 9a4d06ef; M5-T081-evidence-map.json 6cce2a91.
   T086: app/drawings/dxf_reader.py 6dbc33b7; tests/drawings/test_dxf_reader.py 2503baae; M5-T086-producer-report.md b4675e48; M5-T086-evidence-map.json 3009c0f1.
2. _task_git_identity at H equals the identity above AND equals reports/<task>.json content_manifest_sha256.
3. The packet material digest is unchanged. Changes to status, progress or updated_at only are fine.
4. evaluate_task_refs(task) is ok, with applicable == cited == the same ID set.
5. The requirement text of every cited ID is byte-identical to its text at PINNED.
6. G0-G5 records for the task still say PASS at the same stamps; the task is not accepted or canceled; no open blocker names the task in affects or detail.

BROAD DISJOINT-PEER TOLERANCE (pre-authorized): any other task's files, packets, gates or material commits; any other directive's captures, amendments or binds; amendments to D-087 or D-066 that do not edit a cited requirement's text and leave both tasks' evaluate_task_refs ok (for example new IDs bound elsewhere, like R011/R012 on D-087-BOOTSTRAP); the orchestrator adding my verification rows to D-087/D-066 verification.json, plus the digest resyncs and audit_log entries that go with them; lifecycle-only packet changes. Anything outside this list needs a delta-attestation from me.

---

DCV M5-T081 + M5-T086, part 2: M5-T081 frozen identity, gates, and first requirement rows.

FROZEN IDENTITY (M5-T081):
- _task_git_identity at PINNED = 9700b33b.
- This equals reports/M5-T081.json content_manifest_sha256 (resubmitted 08:49:38Z at 0ffe581c).
- It also equals the stamp on every current G1-G5 record.
- The pre-rework identity 7394bcf0 (the submit at 5151c2e4) now appears only in superseded history entries: G2 1414e1a7, G3 FAIL 1d41daf8, G4 FAIL 71ab388a.
- G1 and G5 were first recorded after the rework, at 94182057.
- The packet material digest 7c5ef384 is identical in all 10 packet revisions (5e704eeb through 94182057). directive_refs are unchanged.

GATES (all PASS at 9700b33b; producer backend-engineer):
- G0: orchestrator, at 5e704eeb.
- G1: data-contract-verifier.
- G2: orchestrator self_check, at 0ffe581c.
- G3: code-reviewer (delta).
- G4: qa-engineer (delta).
- G5: security-reviewer (rework).
- Every independent reviewer is in reviewer_agents, and none is the producer.

D-066-R001: SATISFIED.
- tasks/M5-T081.json inputs[8] carries the navigation block. It records the graph regenerated (815 files/17025 nodes/7441 edges). It names consumers ("nothing imports it yet"), the forbidden sibling pdf_sheet_writer.py, the read-only mappluto ring source, and the `query.py --no-regen impact` instruction. It marks the graph advisory.
- My own recount of graph inputs over the 5e704eeb tree, using the include roots in graph.meta.json, gives exactly 815.

D-087-R001: SATISFIED (this task's share).
- The packet was contracted at 5e704eeb, with G0 PASS at that commit.
- It was claimed at f9bfd54d (wt-m5t081) and ran at the same time as T082-T085.
- All required gates G0-G5 are PASS.
- Lifecycle, all through the CLI: backlog -> claimed -> awaiting_gate -> rework -> in_progress -> awaiting_gate. No state or gate was skipped.
- B-026 affects only the loop-lane share of R001 and does not name this task.

D-087-R004: SATISFIED for this task's share: the DXF writer module plus its tests.
- dxf_writer.py writes $ACADVER AC1009 (L65, L465-466) and $INSUNITS 21 (L79, L467-468).
- It writes LOT, BUILDING_OUTLINE and MASSING_3D closed POLYLINEs (70=1), 3DFACE walls for each edge in each floor band, and ANNOTATION TEXT, followed by 0/EOF.
- My run: 24/24 passed. The golden 2d8988d6 reproduced.
- The [ORCH-CORRECTED] evidence-map row matches the code exactly: INSUNITS_US_SURVEY_FEET=21, and test L217 pins (70,"21").
- G1 checked every group code against the live Autodesk reference: all correct.
- The owner's confirmation of "DXF = the middleman" (R008) is still pending. I judged the DXF path as delivered, not as confirmed.
- One gap goes to directive level: see finding F1 in part 5.

---

DCV M5-T081 + M5-T086, part 3: the remaining M5-T081 requirement rows.

D-087-R002: SATISFIED.
- I compared T081's allowed_paths with every task packet (any status) at 5e704eeb, 86e2f98b, PINNED and live HEAD cfc3d22c. The only overlaps are broad globs in six ACCEPTED July tasks: M0-T004, M0-T024, M1-T005, M1-T009, M2-T003, M2-T006.
- No live or frozen neighbour overlaps, T086 included. This matches the G0 table (EMPTY overlap, 7 neighbours).
- Worktree wt-m5t081 (branch task/M5-T081-dxf-writer) was created at claim seam f9bfd54d and is clean now. Its only commits are a8e6c8ed and 778bf8ca, and each touches exactly the 3 allowed paths.
- The cherry-picks 4fd58a98 and 0ffe581c match those commits blob-for-blob on all 3 files.
- app/cad/__init__.py was changed only at the seam, by the orchestrator.

D-087-R006: SATISFIED for this task's share: writing and exporting through the open format.
- The DXF writer module and its tests are in place, and native DWG is not touched.
- I ran my own in-memory round trip (writer output fed into the T086 reader): ok=True, AC1009, units 21/us_survey_feet read from the header, 33 entities. The lot and building rings come back exactly and closed, and the honesty texts are present.
- The golden 2d8988d6 reproduced.
- One gap goes to directive level: see finding F2 in part 5.

D-087-R007: SATISFIED.
- At PINNED, git grep finds no DWG library in apps/web/package.json, package-lock.json, pyproject.toml, requirements.in, requirements.txt or requirements-tools.in. The only hit is "ZDWg" inside a base64 integrity hash, which is not a package.
- No .py/.ts/.tsx/.js file imports dwg, libredwg, realdwg, teigha, opendesign, ezdxf or aspose.
- dxf_writer.py imports only __future__, math, collections.abc and dataclasses (L51-55).
- The evidence-map wording overstates the test's power: see finding F3.

D-087-R009: SATISFIED.
- Material 4fd58a98 and 0ffe581c touch only the 3 allowed paths. There is no dependency, lockfile, route, main.py or web change.
- main.py at PINNED imports 11 routers, none of them max_envelope, and no app module imports max_envelope_api, so the route is still unmounted.
- Nothing imports dxf_writer except its own test. The seeded app/cad/__init__.py is docstring only.
- CI run 35980056704 at 33662211 (same blobs) is fully green, including api (ruff + pytest on 3.12), modularity, api-lock-verify, exact-production-install (pip-audit) and web-dependency-security.
- PR #241 is OPEN, mergedAt null, last updated 2026-08-20.
- No Tier D action. Refusals fail closed with no partial output (AS-3 tests).

My local runs (Python 3.11.9, no cache writes):
- pytest: 24 passed (writer) and 28 passed (reader).
- ruff check .: exit 0.
- modularity --check: exit 0, 0 failures, no warning on the DXF files.

---

DCV M5-T081 + M5-T086, part 4: M5-T086 frozen identity, gates, and all six requirement rows.

FROZEN IDENTITY (M5-T086):
- _task_git_identity at PINNED = f0c6963d.
- This equals reports/M5-T086.json content_manifest_sha256 (the single submit, 08:05:34Z, reviewed_sha 5151c2e4).
- It also equals the stamp on every G1-G5 record.
- The packet material digest fef3ec20 is identical in all 8 packet revisions (86e2f98b through 94182057).

GATES (all PASS; producer backend-engineer):
- G0: orchestrator, at 86e2f98b.
- G1: data-contract-verifier. The joint M5-T081-G1.md is fresh and self-contained, pinned at f2870507, and verified dxf_reader.py 6dbc33b7 byte-identical.
- G2: orchestrator.
- G3: code-reviewer (cr-drw).
- G4: qa-engineer (qa-drw).
- G5: security-reviewer (sec-parse).
- Every independent reviewer is in reviewer_agents, and none is the producer.

D-066-R001: SATISFIED.
- tasks/M5-T086.json inputs[7] carries the navigation block: the graph regenerated at the seam, "nothing imports dxf_reader yet", the forbidden sibling sheet_reader/sheet_primitives, the `query.py --no-regen impact` instruction, and the advisory note.
- The dependency set is empty: the seeded placeholder had no imports.
- My recount of graph inputs over the 86e2f98b tree is 817. That matches the seam commit message and the evidence map.
- The G0 report text states 815 instead: see finding F4.

D-087-R001: SATISFIED for this task's share.
- Contracted at 86e2f98b with G0 PASS there, and claimed at 46cc1e6a (wt-m5t086).
- It ran in wave 1.5 at the same time as T081-T085 and T087.
- G0-G5 are all PASS.
- Lifecycle, all through the CLI: backlog -> claimed -> awaiting_gate. Nothing was skipped.

D-087-R002: SATISFIED.
- The same all-packet overlap check at 86e2f98b, PINNED and HEAD finds overlaps only with the six accepted July broad-glob tasks. No live or frozen neighbour overlaps, T081 included.
- Worktree wt-m5t086 (branch task/M5-T086-dxf-reader) was created at claim seam 46cc1e6a and is clean now.
- Its single commit 496fd6f9 touches exactly the 3 allowed paths, and cherry-pick 719d96f8 matches it blob-for-blob.
- No sibling or __init__ file was touched.

D-087-R006: SATISFIED for this task's share: reading and importing through the open format.
- dxf_reader.py reads ASCII DXF: LINE, LWPOLYLINE, POLYLINE/VERTEX/SEQEND, 3DFACE and TEXT.
- Binary DXF is refused by its sentinel, and units are reported, never assumed.
- The writer round trip is proven (part 3). A committed round-trip test is still missing: see finding F2.

D-087-R007: SATISFIED.
- The reader imports only __future__, enum, math and dataclasses (L57-61).
- The DWG scan across the whole repo is clean (part 3).

D-087-R009: SATISFIED.
- 719d96f8 touches only the 3 allowed paths: no dependency, route, main.py or web change.
- Only the reader's own test imports it, so it is unwired, and the max-envelope route is still unmounted.
- CI is green at 33662211 with identical blobs. PR #241 is untouched.

---

DCV M5-T081 + M5-T086, part 5: prohibited-action check and findings F1-F5.

PROHIBITED-ACTION CHECK (at PINNED, re-checked at live HEAD f4b4ef28): clean.
- Not accepted. state.json accepted_tasks (262 entries) contains neither task, both are in active_tasks, and both packets are awaiting_gate.
- No verification rows exist for either task in D-087 or D-066 verification.json. The only new rows at HEAD are for M5-T082.
- Not on main. 4fd58a98, 0ffe581c, 719d96f8 and 94182057 are not ancestors of main or origin/main (both d8b3899f).
- No pull requests. gh returns [] for both task branches and for a search on either task ID. PR #241 is OPEN, not merged, not closed, last updated 2026-08-20.
- No open blocker names either task. I ran accept()'s own regex over affects and detail (and over the whole JSON) for B-001, B-002 (resolved_temporary), B-010, B-011 and B-026: zero hits. B-026 names only D-084-R001-R003 and "D-087-R001 (the loop-lane share)".
- Nothing installed, purchased or deployed. No dependency file changed, the modules are not wired in, and nothing is on main.

FINDINGS. None of these blocks either task's row.

- F1 (MEDIUM; open at directive level). Part of D-087-R004's required check is "a documented AutoCAD-open check the owner can perform". Nothing in T081 provides it, and G1 advisory A2 says no reviewer could run AutoCAD. The owner's confirmation under R008 is also still pending. Do not call D-087-R004 complete until the export/wiring packet (or a committed sample DXF plus a plain-English opening check) delivers this.

- F2 (LOW; open at directive level). D-087-R006's required check includes "round-trip tests where both directions exist". Both directions now exist, but the round trip is proven only ad hoc (G1's run and mine). The T086 packet deliberately deferred a committed test to a later packet; carry it there.

- F3 (LOW; evidence wording). The D-087-R007 row in T081's evidence map says stdlib-only is "asserted by test_as5_module_imports_stdlib_only". That test rejects only shapely, numpy, pydantic, fastapi, requests and httpx, so a DWG-library import would still pass it. The fact itself is true in the source. An optional [ORCH-CORRECTED per T081-DCV F3] rewording limited to that one row is pre-authorized inside my predicate (the file is outside allowed_paths, so the identity does not move).

- F4 (LOW; record accuracy). M5-T086-G0.md line 23 says "815 files/17025 nodes/7441 edges", copied from T081's G0. The 86e2f98b tree has 817 graph inputs, which the seam commit message and the evidence map both state. A correction note is optional; this file is outside every identity and my predicate.

- F5 (INFO). The original section of M5-T081-producer-report.md (L26, L46, L58) still shows $INSUNITS=2 and golden dbef79e1. The Rework section appended from L138 supersedes both. No action: editing it would move the frozen identity.

---

DCV M5-T081 + M5-T086, part 6: one more finding, F6 (LOW; it does not block either task).

The G0 neighbour tables are incomplete, though no overlap exists.
- At 5e704eeb and 86e2f98b, state.json active_tasks held 14 in-flight packets that the G0 tables do not list: M0-T021, M0-T034, M0-T080, M0-T109, M0-T133, M0-T145, M0-T153, M0-T155, and M4-T001-T006. Their states are awaiting_gate, in_progress, rework and claimed.
- The T081 G0 table lists 7 neighbours and the T086 G0 table lists 9.
- My all-packet overlap check at both seams, PINNED and HEAD found zero overlap with all 14, so D-087-R002's actual requirement (no shared writable files) holds.
- Only the G0 record is a subset.
- Suggestion for future G0 tables: list every active task, or state which filter was used.

Also checked while waiting on the validator:
- Your in-flight, uncommitted seam binds M0-T160 and M5-T088-T092 onto D-087 R001/R002/R003/R005/R006/R009/R011, plus the D-066 manifest/requirements edits.
- These change only applicability. No cited requirement text changed, and nothing was removed from T081 or T086.
- evaluate_task_refs is still ok for both tasks against that working-tree registry.
- This falls inside my stated tolerance.
- The D-087 and D-066 source digests and requirements digests match their manifests. I recomputed them myself with sha256_text_artifact.

---

DCV M5-T081 + M5-T086, final part: harness result, predicate re-check, and verdicts.

VALIDATOR (my single run): VALIDATOR_EXIT=1.
- It ran 09:24:37Z to 09:54:48Z. HEAD moved from cfc3d22c to 114e5e56 during the run.
- It reported two c14 errors:
  - D-066: manifest 627ccb48, actual ec04025b.
  - D-087: manifest d2f15086, actual 87b20e4b.
- Cause: the run overlapped your seam writes; this is not a registry defect.
  - 627ccb48 and d2f15086 are the manifest digests at PINNED, read when the run started.
  - ec04025b and 87b20e4b are exactly the requirements digests you committed at 5e9dbd07 (09:45:20Z), and the manifests in that same commit record the same values.
  - Recomputing in memory, manifest == actual for both directives at every committed state since: 5e9dbd07, a14fb775 and fa7e5fae.
- Neither error concerns T081 or T086. I did not re-run, per the once-only rule.

HARNESS EVIDENCE is therefore the CI control-plane job, which runs validate --check, test_project_control.py, test_directive_compliance.py and test_directive_reminder.py:
- SUCCESS at f6116a5c (run 36014033941).
- SUCCESS at 6c79cd88 (run 35989704760).
- Both heads carry all 8 predicate blobs unchanged.
- The fa7e5fae run (36014737739) was still in progress when I checked.
- I did not run test_directive_compliance.py.

PREDICATE RE-CHECK at live HEAD fa7e5fae: HOLDS on every condition.
1. All 8 blobs are unchanged: 152f1f2e, 2aa45291, 9a4d06ef, 6cce2a91, 6dbc33b7, 2503baae, b4675e48, 3009c0f1.
2. _task_git_identity reproduces 9700b33b (T081) and f0c6963d (T086) with no error, and both equal the reports/*.json stamps.
3. The packet material digests 7c5ef384 and fef3ec20 are unchanged. Status is awaiting_gate and neither task is accepted.
4. evaluate_task_refs is ok, with applicable == cited (7 IDs for T081, 6 for T086).
5. The cited requirement texts are byte-identical to PINNED, both in the commit and in the working tree. The new seam binds change only applicability, and both tasks are still bound.
6. G0-G5 are PASS at the same stamps. No verification rows exist yet. The five open blockers name neither task.
7. PR #241 is still OPEN and not merged. Remote main is d8b3899f and contains neither 0ffe581c nor 719d96f8. There are no task PRs.

VERDICTS. Every applicable requirement is SATISFIED on primary evidence. F1-F6 are non-blocking for these task rows. D-087-R004 and D-087-R006 stay open at directive level because of F1 and F2, and R008 is still pending.

M5-T081 DCV VERDICT: PASS 7/7 (D-066-R001, D-087-R001, R002, R004, R006, R007, R009)
M5-T086 DCV VERDICT: PASS 6/6 (D-066-R001, D-087-R001, R002, R006, R007, R009)

Lesson for you to store if useful: run the single DCV validator only when no seam edit is in flight. It reads the manifests when it starts and re-reads requirements.json later, so a bind made during the run produces a transient pair of c14 errors.

END-OF-REPORT
