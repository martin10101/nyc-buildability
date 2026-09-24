# M5-T083 — directive-compliance verification (directive-compliance-verifier "dcv-t083", read-only)

> Transmission history: pinned at f4b4ef28, delivered as eight SendMessage parts (1..8, part 8 marked
> final) ending with END-OF-REPORT; no truncation. Part 2 REPLACES part 1's P4 wording (the verifier's
> own correction, requested by the orchestrator because the first P4 was already false at the pin).
> Joined verbatim in delivery order by the orchestrator (transport wrapper tags removed only).
> Orchestrator predicate re-check at the accept head: the four blobs (63a992ca / a3659c55 / b60f7e1c /
> f13fc136) unchanged; identity 86661a1a with error None; services/api/app/documents tree c14c65ff;
> app/main.py has no max_envelope reference; evaluate_task_refs ok. The D-087-R005 row is recorded
> SCOPE-LIMITED exactly as the verifier requires (synthetic tests only; the real-file harness is not
> discharged).

---

M5-T083 DCV part 1 (up-front restamp pre-authorization; the verdict follows in later parts).

PINNED HEAD = f4b4ef285b2f32df0ab6472cd9c63d28a775748d (read at start).

RESTAMP PREDICATE (applies only if my final verdict is PASS; void on FAIL/BLOCKED). The verdict carries to any later head H if ALL of these hold at H:
(P1) The blobs are byte-identical to the pinned ones (`git rev-parse H:<path>`):
- services/api/app/drawings/sheet_reader.py = 63a992ca60dc02d0b95d5bbb12a7c530b79bc3a1
- services/api/app/drawings/sheet_primitives.py = a3659c55c6a5364bcc57e91c85200f2f794f23fc
- services/api/tests/drawings/test_sheet_reader.py = b60f7e1ccc89b75b3a665d5c92423b293f00a6da
- project-control/reports/M5-T083-producer-report.md = f13fc13620d8de999f6275406e4806d3d612d99a
(P2) project_control._task_git_identity(directive_registry, task) at H == 86661a1ac1114f4463b2d3ce21d71d1660cea6d8788adfa0dd9250fc6a68607e, and reports/M5-T083.json content_manifest_sha256 still says that value.
(P3) At H, directive_registry.load_registry().evaluate_task_refs(M5-T083) is still ok, and applicable == cited == {D-066-R001, D-087-R001, D-087-R002, D-087-R005, D-087-R009}.
(P4) Every app/documents/** path and services/api/app/main.py, services/api/app/routes/**, apps/web/**, and the dependency manifests/lockfiles are still byte-identical to f9bfd54d (the rule for R005/R009). A disjoint peer changing one of these is the ONLY peer change this predicate does not tolerate.
(P5) The gate records G0-G5 for M5-T083 are unchanged, except for rows the orchestrator appends.
(P6) M5-T083 is still not accepted and not merged to main at the moment of restamp, other than through the accept this DCV feeds.

DISJOINT-PEER TOLERANCE (explicitly allowed, no re-ruling needed):
- Any other task's files, material commits, gates, reports, packets, and state.json changes that touch no P1/P4 path.
- Registry binds by other directives, and same-directive (D-087/D-066) amendments or binds that leave P3 true.
- The orchestrator adding MY verification rows to D-087 and D-066 verification.json, plus the matching audit_log/digest resync in the same commit.
- DISCOVERY_BACKLOG, CODING_RULES, PROGRAM_KNOWLEDGE, handoff docs, and agent-memory changes.
If P1-P6 hold, restamp reviewed_sha to H without asking me again. If any of them fails, send me the delta.

---

M5-T083 DCV part 2: a correction to P4 in part 1. Use this version; the part-1 wording is void.

The part-1 P4 was wrong. Between f9bfd54d and the pinned head f4b4ef28, other tasks already changed apps/web/** (11 files) and services/api/app/api/v1/max_envelope_api.py. Also, "services/api/app/routes/**" does not exist. As written, P4 would fail even at the pinned head.

REPLACEMENT P4 (checked at restamp head H):
(P4a) `git rev-parse H:services/api/app/documents` == c14c65ff952b253b44089dd32117e4149eff9e57. That is the same tree as at f9bfd54d and at the pinned head. T083 imports pdf_lexer, pdf_objects and pdf_xref from there, so if this tree changes the runtime basis for R005 changes too, and I must re-rule.
(P4b) services/api/app/main.py at H still does not import or mount the max_envelope_api router.
(P4c) No tracked file at H imports app.drawings.sheet_reader or app.drawings.sheet_primitives, other than the three T083 code/test files themselves. The module stays unwired. The docstring-only app/drawings/__init__.py blob is 44250803.

TOLERATED, in addition to the part-1 list: disjoint peer changes to apps/web/**, services/api/app/api/**, services/api/tests/documents/**, and any peer's own dependency admission under its own gates. T083's own imports are fixed by the P1 blobs: stdlib math/zlib, app.documents.extraction.*, and app.drawings.sheet_primitives.

P1, P2, P3, P5 and P6 are unchanged.

---

M5-T083 DCV part 3: frozen identity and gates.

PIN: f4b4ef28, the HEAD when I started. HEAD has since moved to 114e5e56 (D-087 wave-2 seams) and then a57bb8de (T077 accepted; T078-T080 gates). Both moves are disjoint from T083. The four T083 blobs are identical at both heads.

IDENTITY (reproduced with project_control._task_git_identity and directive_registry.frozen_git_identity):
- Live HEAD f4b4ef28: 86661a1ac1114f4463b2d3ce21d71d1660cea6d8788adfa0dd9250fc6a68607e. The clean live stamp at 114e5e56 is the same.
- reports/M5-T083.json has the same content_manifest_sha256 (86661a1a), with reviewed_sha 5467318e and submitted 09:10:45Z. MATCH.
- History: 5f05969d at 5e704eeb and f9bfd54d (placeholders); e550d721 from 7acb3359 through 5c5f7e1b (first pass); 86661a1a at 5467318e, 10def4ef, 33662211, 4de4f5ec and f4b4ef28 (rework).

POST-RESUBMIT GATE RECORDS (gates/M5-T083-Gn.json). All five stamp the REWORK identity 86661a1a. None stamps e550d721.
- G2: orchestrator self_check, PASS, 09:10:54, sha 5467318e.
- G3: code-reviewer, PASS, 09:20:01, sha 33662211, report -G3-rework.md.
- G1: data-contract-verifier, PASS, 09:20:07, sha 33662211, report -G1-rework.md.
- G5: security-reviewer, PASS, 09:20:24, sha 33662211, report -G5-rework.md. The history keeps the earlier FAIL (-G5.md).
- G4: qa-engineer, PASS, 09:31:25, sha 4de4f5ec, report -G4-rework.md.
- G0: orchestrator, administrative, PASS, stamped 5f05969d at 5e704eeb. This is the contract-seam readiness gate. accept() checks each gate's result, role and reviewer, not its stamp (project_control.py:1200-1222). The identity it does check is the one in reports/M5-T083.json (:563).

INDEPENDENCE: the required gates are G0-G5. Each independent gate (G1, G3, G4, G5) was recorded by a reviewer listed in reviewer_agents, and none of them is the producer (backend-engineer). Each re-ruling came from the same reviewer as the first ruling (dc-pdf, cr-drw, qa-drw, sec-parse). Every -rework report pins 10def4ef, verifies code blobs 63a992ca and a3659c55 (G3, G4 and G5 also the test blob b60f7e1c), and ends in PASS.

MATERIAL: 7acb3359 is the cherry-pick of wt-m5t083 commit 641f097c (parent f9bfd54d). 5467318e is the cherry-pick of b07a4aaa (parent 641f097c). Each of the four commits changes exactly the four allowed paths (git diff-tree --raw), and each pick is blob-identical to its source. wt-m5t083 is clean at b07a4aaa, and no other packet names it.

---

M5-T083 DCV part 4: requirement rows, 1 of 2.

APPLICABILITY: evaluate_task_refs(M5-T083) returns ok=true at both f4b4ef28 and 114e5e56. Applicable == cited == {D-066-R001, D-087-R001, D-087-R002, D-087-R005, D-087-R009}. Missing and invalid are both empty. The source-002 rows do not apply here: R011 binds only [D-087-BOOTSTRAP, M5-T090], and R012 binds only [D-087-BOOTSTRAP]. Every source digest matches its manifest (D-087 source-001 34c3dd64, source-002 4eea66c6; D-066 source-001 4cb05c94), and so do both requirements digests. Locked ids equal the requirement ids (12/12 and 4/4).

D-066-R001 - SATISFIED.
- tasks/M5-T083.json inputs[8] (file line 17) holds the CODE-GRAPH NAVIGATION BLOCK. It says the graph was regenerated at this seam (815 files / 17025 nodes / 7441 edges) and that app/drawings is a new package whose __init__ belongs to the orchestrator. It lists the strict modules, which are consumed by vector_pdf_decoder, survey_pipeline and routing, all FORBIDDEN. It gives the instruction `query.py --no-regen impact <path>` before sweeps, and says the graph is ADVISORY and must be verified in source.
- I checked the consumer claim in source: vector_pdf_decoder.py:43-46 imports the strict modules, and routing.py:48 and survey_pipeline.py:78,86 import the decoder.
- Applying generate.py's own include rules to the 5e704eeb tree gives 815 input files, which supports the regeneration count.
- The producer stayed in scope: both diffs touch only the 4 allowed paths.

D-087-R001 - SATISFIED.
- Packet status at each seam commit: backlog at 5e704eeb (G0 PASS); claimed at f9bfd54d; awaiting_gate at 9979cfb6 (submit from claimed is allowed, project_control.py:181); rework at d5f81997 after the G5 FAIL; in_progress at 5c5f7e1b; awaiting_gate at 10def4ef (resubmit); 95% at f4b4ef28.
- No state was skipped, and all six required gates are PASS.
- It was claimed at f9bfd54d as an orchestrator-dispatched subagent packet, at the same time as T081, T082, T084 and T085.
- B-026's affects list names only D-084 lanes and "D-087-R001 (the loop-lane share...)". It does not cover this packet.

D-087-R002 - SATISFIED.
- I recomputed the overlap between the 4 allowed paths and every non-terminal packet (project_control._path_touches). It is EMPTY at 5e704eeb (40 live packets), f9bfd54d (40), 5467318e (42) and f4b4ef28 (41), and in the current tree, which includes M5-T088 to T092.
- The only overlap ever found is M0-T024 ('project-control/'), which was accepted on 2026-07-24.
- There is one isolated worktree, wt-m5t083.
- The shared __init__ files (44250803 and e69de29b) are unchanged since 5e704eeb.
- The sibling T086 lists sheet_reader.py and sheet_primitives.py in its forbidden_paths.

---

M5-T083 DCV part 5: requirement rows, 2 of 2.

D-087-R005 - SATISFIED for this packet's scope (see F1 and F2).
- The release was in force before the work. Hold notice section 2.3 (committed at b8ed927c, before the 5e704eeb contract) releases phase-C PDF blueprint reading.
- It is a separate profile, and it reuses the strict reader read-only. sheet_reader.py:51-62 imports only from pdf_lexer, pdf_objects and pdf_xref (read_object_table).
  - It does not use pdf_content, which refuses curves, XObjects and rotated/sheared matrices (pdf_content.py:12-16, 48-49, 580).
  - It does not import pdf_container either: that page API does not expose /Resources, and its decode helpers are private. The profile applies the same limits itself: 512 pages, 8 MiB per stream, 32 reference hops, and a single FlateDecode filter only.
- app/documents is byte-untouched. Its tree is c14c65ff at f9bfd54d, f4b4ef28, 114e5e56 and a57bb8de. All 8 strict modules and isolation.py have identical blobs, and the git diff since f9bfd54d is empty. tests/documents (970ac277) is also unchanged.
- Output stays in PDF user space.
  - user_unit is recorded but never applied (sheet_reader.py:435-443).
  - Every page carries media_box, user_unit and flatten_tolerance (sheet_primitives.py:189-200).
  - Nothing converts to feet or world coordinates, classifies lines, or feeds the proposal contract.
- Behavior checked in the code: the declared tolerance is recorded; the CTM handles rotation and shear; q/Q nesting is capped at 128; forms are capped at depth 8 and cycles are refused; images are counted and never decoded; every refusal is a returned value, with a top-level catch-all (:350-353).
- Tests: 37 pass locally under a no-write 3.11 shim. The CI api job (ruff + pytest) passed at f4b4ef28 (run 35981978444) and at 114e5e56 (run 35983442690).

D-087-R009 - SATISFIED.
- Imports are only the standard library (math, zlib, dataclasses, typing) plus app.* (sheet_reader.py:46-76, sheet_primitives.py:17-21). The tests add only pytest and tracemalloc.
- The two T083 commits change no dependency manifest, lockfile, route, main.py or web file.
- main.py mounts no max-envelope router: the include_router calls at :126-218 don't include it, and a grep for max_envelope finds nothing.
- The module is unwired. Nothing imports app.drawings.sheet_reader or sheet_primitives except T083's own three files, and the package __init__ is a docstring only.
- PR #241 is still OPEN (mergedAt and closedAt are null, last updated 2026-08-20).
- 7acb3359 and 5467318e are not ancestors of main (d8b3899f).
- Gates G0-G5 are all PASS.
- At f4b4ef28 these CI jobs succeeded: modularity, api-lock-verify, api-tooling-lock-verify, web-dependency-security.
- No Tier D action, and nothing touches the D-086 surface.

---

M5-T083 DCV part 6: findings F1 and F2. Neither blocks this acceptance.

F1 (MEDIUM; rider that must bind the next reader packet): T083 does not discharge R005's real-file obligation.

Facts:
- All 37 tests use synthetic PDFs built in the test file (test docstring, lines 3-5).
- R005's required_harness is "Offline reader tests on a real-file fixture corpus". R005 also says "supported drawing classes defined from REAL files (a fixture-corpus capture precedes the C1 reader widening)". docs/PROPOSAL_EDITOR_PHASED_PLAN.md:69-71 says real files become the corpus BEFORE C1 is contracted.
- T083 was contracted in the same commit (5e704eeb) as T084, the corpus capture, with dependencies []. T083's producer commit (04:01:33) landed 2 minutes after T084's (03:59:32) and used no corpus file.
- The corpus note §5 (docs/research/architect-drawing-corpus-2026-09.md:110-122) is written "for M5-T083 / phase C". It recommends items 1-2 as positive vector fixtures and items 4-6 as scan-only fixtures, referenced by digest. T083 uses none of them.

Ruling: this is NOT a T083 violation, for three reasons:
1. In the plan, C1 is the extraction SERVICE SEAM (pick a page or sheet, refuse scan-only files).
2. T083 is an unwired module and claims no supported drawing class.
3. The accepted corpus (T084, f2870507) already comes before any C1 contract.

What this means:
- The T083 R005 verification row must say it is limited to scope. It must not be cited as meeting R005's real-file harness.
- Rider: the next reader packet (C1 or wiring) must run corpus items 1-2 and 4-6 through read_sheet, by sha256, before wiring.
- Until that is done, do not tell the owner that real architect PDFs can now be read.

F2 (MEDIUM; a discovery that was never routed; not a cited requirement):
- The producer report lists two discoveries that are not in docs/DISCOVERY_BACKLOG.md: "Cross-reference streams (PDF 1.5+) are refused" (report lines 171-175) and the `sh` (shading) refusal (lines 182-184). I grepped the backlog at 5d8b16b6: no entry. DB-055 (d) covers only inline images.
- The packet's D-069 input says the orchestrator records discoveries at the seam.
- This matters for F1. Corpus vector items 1-2 were made by "Acrobat PDFMaker 9.0 for AutoCAD". Whether they use xref streams is UNVERIFIED, because the files exist only in scratch. If they do, the reused strict reader (read_object_table) refuses them, and T083 reads neither positive fixture.
- Recommend adding this as DB-055 (g) at the accept seam and making it a precondition of the F1 rider.

---

M5-T083 DCV part 7: the DB-055 (a) ruling and findings F3-F5.

DB-055 (a) RULING (G4-rework F6, the vacuous test)
- Reproduced in memory with content `10 10 m 2 0 0 2 0 0 cm 10 10 20 10 20 20 c S`.
  - Real code: points[1] = (14.16, 13.34).
  - Exact pre-fix revert (p0 = _apply_matrix(self._ctm, *self._current)): points[1] = (23.12, 20.31).
  - points[0] = (10,10) and points[-1] = (40,40) are the same in both. All 37 tests still pass under the mutant.
- So the test is vacuous and the production code is correct.
- The disposition leaves NO cited requirement unsatisfied:
  - The fix this test was meant to guard answers an ADVISORY/NIT finding (G1 F6, G3 F3). It is not one of AS-1..AS-5.
  - G4 marked F6 ADVISORY, not a required correction, so the blocking rule for required corrections does not apply.
  - G1-rework separately confirmed the behavior against ISO 32000-1 Table 59.
- Note: producer report lines 244-246 claim this test proves the curve start. That claim is false. Do not edit the report, because it is inside the frozen identity. The G4-rework report is the record that corrects it.

F3 (LOW; tests vs the packet's input)
- The packet's binding TESTS input asks for "a 30-degree rotated rectangle via cm". The AS-2 test rotates a line instead (test lines 162-172).
- I counted operators in memory across all 37 tests. These are never executed: re, v, y, s, f, F, f*, B*, b, b*, n, W, W*, TL, Td, TD, T*, TJ, ', ".
- G1 checked what these operators do by reading the code. AS-2's own wording is met, and G4 passed twice. No cited requirement fails.
- Recommend adding this to DB-055 (a).

F4 (LOW; evidence-map wording)
- The R005 rework row says "attacker tokens in refusal details are truncated". Only the unsupported-operator token is truncated (_preview, sheet_reader.py:818).
- XObject /name echoes are not truncated (:989, :997, :1003, :1009, :1040). The lexer bounds their length. This is the G5-rework residual, already recorded as DB-055 (f).
- The evidence map is outside the frozen identity, so an [ORCH-CORRECTED] note is optional.

F5 (INFO)
- The G0 disjointness table names 7 neighbours, but 40 packets were live at 5e704eeb.
- My full recomputation (part 4) finds EMPTY overlap with every one of them. No real gap.

---

M5-T083 DCV part 8 (final): sweep, harness, predicate, verdict.

PROHIBITED-ACTION SWEEP (at 5d8b16b6)
- Not accepted: status is awaiting_gate; accepted_at and post_accept_verification are null.
- No M5-T083 row exists in D-087 verification.json (5 rows) or D-066 verification.json (44 rows).
- Not on main: 7acb3359 and 5467318e are not ancestors of main d8b3899f (gh api agrees). There is no PR and no remote task branch for T083.
- PR #241 is still OPEN, unmerged and not closed.
- Open blockers: B-001, B-010, B-011, B-026. None matches M5-T083 under accept()'s word-bounded matcher, and B-026 does not name it.
- T083's commits install, deploy, dispatch or purchase nothing: they touch only the 4 allowed paths and change no manifest.

HARNESS (tools/test_directive_compliance.py was not run locally, per your prohibition)
- CI control-plane job: SUCCESS at f4b4ef28 (run 35981978444), 114e5e56 (35983442690), a57bb8de (35984669232) and 5d8b16b6 (35985746149). At the first two I checked each step: project-control regression, validate --check, the full directive-compliance suite and the reminder tests all succeeded.
- CI api job (ruff + pytest on Python 3.12): SUCCESS at the same heads. At f4b4ef28, ruff reported "All checks passed!" and pytest "4627 passed".
- Local: test_directive_reminder.py EXIT=0; modularity --check shows failures 0 (sheet_reader.py is a warning only); the T083 suite passed 37/37 under a shim that writes nothing.
- Still running when I sent this: local validate --check (one run, started 09:59:42Z) and test_project_control.py (started 10:05:37Z). I will send both exit codes in one short addendum. CI already covers both, so the verdict does not depend on them.

PREDICATE STATUS
- P1-P6 hold at 114e5e56, a57bb8de and 5d8b16b6, with P4 as corrected in part 2.
- The newer commits 80f17a86 (M5-T090 three.js admission) and 2e444920 (web lockfile) touch only apps/web/package*.json and the T090 report. That falls in the tolerated set. The T083 blobs and the app/documents tree are unchanged at those commits.

VERIFICATION ROWS
- PASS for all five, citing report M5-T083-DCV.md.
- The D-087-R005 row must also say: "scope-limited: synthetic tests only; R005's real-file reader harness NOT discharged - F1/F2 riders bind the next reader packet".

FINDINGS: F1 and F2 are MEDIUM riders, F3 and F4 are LOW, F5 is INFO. None blocks this acceptance.

M5-T083 DCV VERDICT: PASS 5/5
END-OF-REPORT
