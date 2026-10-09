# M5-T109 — directive-compliance verification (directive-compliance-verifier "dcv-t109", read-only)

> Transmission history: pinned at 7f5c82fa, delivered as five SendMessage parts (1/5..5/5) ending with END-OF-REPORT;
> no truncation. Part 1 carries the blob-level restamp predicate (eight blobs + identity 802274bd) with broad
> disjoint-peer tolerance. Joined verbatim by the orchestrator (transport wrapper tags removed only). The harvest-time
> scope correction (test_glb_writer.py added at 6f9aff3c, G0 re-recorded, the edit tagged [ORCH-CORRECTED]) was judged
> properly tracked with its teeth kept.

---

M5-T109 DCV part 1/N — RESTAMP PRE-AUTHORIZATION (up front)

Live HEAD at start: 7f5c82faaf9ba46bc71b4a0151abb2240917abda. Verified: all 8 reviewed blobs are byte-identical at frozen head 419cdcee AND at live HEAD, and reports/M5-T109.json content_manifest_sha256 == 802274bd.

BLOB-LEVEL PREDICATE. If my final verdict is PASS, it restamps to any later head H provided that, at H:
- git rev-parse H:<path> equals the reviewed blob for each of the 8 files:
  services/api/app/cad/export_service.py = 2bf8963d
  services/api/app/api/v1/export_api.py = dec92648
  services/api/tests/cad/test_export_service.py = 2fbce1cb
  services/api/tests/cad/test_export_api.py = 9301f098
  services/api/app/cad/pdf_sheet_writer.py = 8064d845
  services/api/tests/cad/test_pdf_sheet_writer.py = 3935fa7c
  services/api/tests/cad/test_glb_writer.py = ca206312
  project-control/reports/M5-T109-producer-report.md = ccf4480e
- reports/M5-T109.json content_manifest_sha256 stays 802274bd and the task's frozen git identity (_task_git_identity) still equals it.

Any head satisfying that carries reviewed_sha = H for my v2 rows.

DISJOINT-PEER TOLERANCE (broad). None of these void the verdict, in any number/order:
- other tasks' files, gates, material, incl. M5-T106/T108 rework rounds, M5-T107 and M0-T161 reviews and harvests, and later accepts;
- other directives' registry binds, incl. D-088;
- the orchestrator adding MY verification rows to D-066/D-083/D-087 verification.json, with digest resyncs and audit_log entries;
- DISCOVERY_BACKLOG.md rows and contract-seam sweep lines;
- lifecycle-only changes to tasks/M5-T109.json (status/progress/progress_log) that leave content_manifest_sha256 == 802274bd.

Only a change to one of the 8 blob SHAs or to the frozen identity 802274bd voids it.

Full requirement rows, findings and final verdict line follow. END-OF-PART-1

---

M5-T109 DCV part 2/5 — applicability + requirement rows (1/2)

APPLICABILITY (reproduced): directive_registry.load_registry().evaluate_task_refs(task) → ok=True, applicable_ids == cited_ids == the 9 below, missing_ids=[], invalid_refs=[], reasons=[]. Applicable EQUALS cited. (D-087-R003/R007/R008/R010/R011/R012, D-083-R003..R013, D-066-R002/R003/R004 exclude M5-T109 in requirements.json — correctly not cited.)

D-087-R001 (capacity: contracted/claimed/gated packet, nothing skipped) — SATISFIED. tasks/M5-T109.json: status awaiting_gate, required_gates G0,G2,G3,G4,G5 all recorded+PASS; producer backend-engineer (orchestrator-dispatched subagent); progress_log claimed at 11089429, one worktree wt-m5t109; G0 at contract seam 06db6449 re-recorded 6f9aff3c. Ran with disjoint concurrent packets (G0 table lists M5-T106/T107/T108 contracting). No state/gate skipped.

D-087-R002 (no interference: disjoint paths, worktree isolation) — SATISFIED. G0 report disjointness table = EMPTY overlap vs EVERY active task (incl. M4-T005 awaiting_gate, whose tests/api/** glob forced the route tests into tests/cad). git show --stat 154f3abe = exactly the 7 allowed files. The 8th file (test_glb_writer.py) and pdf_sheet_writer.py are shared ONLY with ACCEPTED/frozen packets — I verified statuses: T092/T096/T102/T105 = accepted; T081/T085/T091 = accepted. Under R002 ("waits until that one is accepted") frozen-only overlap is permitted; the test edit is an orchestrator serial [ORCH-CORRECTED], added to allowed_paths at 6f9aff3c, G0 re-recorded + re-checked vs every active task. No concurrent writer shared a writable file.

D-087-R004 (AutoCAD import via DXF) — SATISFIED. export_service.py:378-388 _render_dxf → dxf_writer.render_site_plan_dxf; DXF_MEDIA_TYPE="image/vnd.dxf" (:76); served as a file download (export_api _file_response). Tests: test_each_format_dispatches_to_its_writer[dxf], test_200_returns_a_file_per_format[dxf]. DXF writer byte-frozen (forbidden_paths; golden green in the 429 run). UNMOUNTED until PKT-H (correct staged release).

D-087-R005 (PDF blueprints + DB-075(a)) — SATISFIED. export_service.py:391-403 _render_pdf; caller text capped+claim-screened before the writer (build_export order :448-467). DB-075(a): pdf_sheet_writer.py diff = docstring + `except (ValueError, TypeError): return SitePlanRefusal("non_numeric_coordinate", ...)` (purely additive). Golden+owner samples byte-identical (test_cad_owner_samples green in the 429 run). Red/green teeth: test_hostile_float_vertex_is_a_typed_refusal_never_raises + test_narrow_overflow_only_catch_reddens_on_a_hostile_float (reverts to pre-fix body, proves escape). Route DB-075(b): test_422_typed_refusal_through_the_real_route.

Part 3 (R006/R009/D-083/D-066) follows. END-OF-PART-2

---

M5-T109 DCV part 3/5 — requirement rows (2/2)

D-087-R006 (CAD export via open formats DXF/PDF/GLB, with the safety guarantees) — SATISFIED. All three dispatch (_DISPATCH :420). One reconciled redacted refusal: _reconcile (:277-283) discards the writer's own message, emits server-built detail "the <fmt> export was refused by its writer (reject_code=<code>)". Caps BEFORE any writer: _screen_caller_text → _raw_ring_length (raw len() before normalization, DB-057 d, :245-256) → _raw_floor_count(<=2000) all precede _DISPATCH. Filename safety: build_filename_token allowlist [A-Za-z0-9._-] cap 80 (:190-202) + content_disposition RFC 6266/5987 (:205-214). GLB dedupe by single-prism construction (_build_prism_mesh, DB-054 m). Route: off-loop asyncio.wait_for+run_in_threadpool deadline (15s) + per-caller sliding-window rate limit. Open formats only; no DWG library.

D-087-R009 (unchanged boundaries; zero deps; UNMOUNTED; main.py untouched) — SATISFIED. Zero new deps: imports stdlib + admitted fastapi/starlette; requirements.txt/.in last changed by M0-T018/M0-T020, NOT any T109 commit; limiter is stdlib OrderedDict/deque. UNMOUNTED: git log shows main.py untouched by the T109 range; grep at HEAD → no export reference in main.py; include_in_schema=False (:221); flag-gated internal_rule_eval_enabled(); generic 404 (:155-158). test_route_is_unmounted_in_the_real_app asserts OpenAPI-absent. Other writers/claim_words/samples untouched (cherry-pick = 7 files only). [ORCH-CORRECTED] test_glb_writer.py properly tracked, teeth preserved. PR #241 untouched.

D-083-R001 (no permitted/approved/maximum-allowed; claim-word screen before writers) — SATISFIED. _SOURCE_LABELS = only the two honest labels (:90-93); grep: the sole "permitted/approved/maximum allowed" hit is the negation in the docstring (:43). _screen_caller_text → claim_words.contains_claim_word before any writer. Tests: test_source_labels_are_honest, test_claim_word_in_caller_text_refuses_before_the_writer. (G4 A1 advisory: bbl/generated_at/generator_version screens untested — code screens all 4 fields via _TEXT_FIELDS; non-blocking test gap, does not undercut the requirement as built.)

D-083-R002 (three claim classes; demonstrated maximum unavailable) — SATISFIED. Vocabulary distinguishes "Proposed - not a city record" (a) from "Generated building option" (b); no demonstrated-maximum (class c) claim; no per-dimension ceiling presented as one permitted building. Consistent with R009.

D-066-R001 (navigation block in packet + query.py --no-regen instruction) — SATISFIED. Packet inputs[20]: CODE-GRAPH NAVIGATION BLOCK (graph regen at seam, 832 files/17984 nodes/7700 edges; names writers' consumers, forbidden neighbors; "Run python tools/code_graph/query.py --no-regen impact <path> before sweeps; graph ADVISORY - verify in actual source"). G0 report confirms present. Graph stayed advisory (harvest sweep found the one real consumer, test_glb_writer AS-5, handled in scope).

Part 4 (gates, frozen identity, prohibited-action sweep, findings) follows. END-OF-PART-3

---

M5-T109 DCV part 4/5 — gates, frozen identity, prohibited-action sweep, findings

GATES (all required PASS; G3/G4/G5 independent, none = producer backend-engineer):
- G0 PASS (orchestrator, administrative) reviewed_sha 6f9aff3c.
- G2 PASS (self_check, recorded by orchestrator — CLI rejects the producer's own name) manifest 802274bd.
- G3 PASS (code-reviewer) / G4 PASS (qa-engineer) / G5 PASS (security-reviewer), each independent_review, each content_manifest_sha256 = 802274bd, reviewed_sha 52594a03.

FROZEN IDENTITY — reproduced: project_control._task_git_identity(reg_mod, task) at live HEAD 7f5c82fa = 802274bdc19be7cfa8fbb3d417ce6921f95fdc130c39343d7b0b8a5893ec6775, err=None (scope clean). == reports/M5-T109.json content_manifest_sha256 == the G2/G3/G4/G5 stamps. The 8 reviewed blobs are byte-identical at 419cdcee and HEAD (the report's reviewed_sha 419cdcee resolves to that same identity; the CLI stamps identity at HEAD by design).

HARVEST SCOPE CORRECTION — properly tracked, teeth kept. test_glb_writer.py added to allowed_paths at 6f9aff3c, G0 re-recorded (manifest d8bd8eab), disjointness re-checked vs every active task, edit tagged "[ORCH-CORRECTED per M5-T109 harvest]" (419cdcee, 5+/1-). Corrected test asserts importers == ["app/cad/export_service.py"] AND main.py contains neither "export_service" nor "export_api" → reddens on a 2nd importer or a mount. G3/G4/G5 each independently re-verified teeth.

PROHIBITED-ACTION SWEEP — all clean:
- NOT accepted: status awaiting_gate; absent from master_plan accepted; present in state.json active_tasks; 0 verification rows in D-087/D-083/D-066 verification.json.
- NOT on main: git branch -a --contains 154f3abe → not on main/origin-main.
- PR #241: OPEN, mergedAt null, headRefName task/M5-T002-scenario-endpoint, updatedAt 2026-08-20 — untouched/unmerged.
- No open blocker references M5-T109.
- Nothing merged/accepted/dispatched/deployed/installed/purchased/closed.

FINDINGS (advisory; none blocking, none undercuts a cited requirement):
- F1 (= G3 A1): GLB cap triangulation is a fan from footprint vertex 0 (export_service.py:356-359) — geometrically wrong for concave footprints, NOT refused (fail-open). Does NOT undercut D-087-R006: GLB is UNMOUNTED, a "Proposed/Generated" visual massing, no zoning value derives, output is still valid glTF; the format/refusal/cap/filename guarantees hold. RECOMMEND recording as a DISCOVERY so PKT-H cannot mount GLB export for concave footprints without a fail-closed refusal or a robust triangulator.
- F2 (= G4 A1): claim-word/length screens for bbl/generated_at/generator_version have no reddening test (only address). Code screens all 4 via _TEXT_FIELDS; latent only if a future refactor narrows the tuple. Does NOT undercut D-083-R001 as built. RECOMMEND parametrizing the screen tests across all 4 fields.
- F3 (reconciliation, not a defect): gate reviewed_sha 52594a03 ≠ report reviewed_sha 419cdcee, but all four content gates carry manifest 802274bd = the frozen identity, so reviews are of the frozen content (byte-stable-identity gate-at-head pattern). G5 A1-A4 also non-blocking (PKT-H items).

Part 5 (harness evidence + predicate recap + final verdict) follows once the validator returns. END-OF-PART-4

---

M5-T109 DCV part 5/5 — harness evidence + digest verification + VERDICT

HARNESS (authoritative):
- python tools/validate_directive_compliance.py --check → VALIDATOR_EXIT=0 (direct exit code, no pipe; ran ONCE, completed). Registry integrity PASS (enforces source digests, requirements digests, locked_requirement_ids, schema).
- pytest tests/cad (cwd services/api) → 429 passed, exit 0 (incl. test_export_service 36, test_export_api 20, test_pdf_sheet_writer DB-075 hostile-__float__, corrected test_glb_writer AS-5, test_cad_owner_samples owner samples byte-identical, DXF/PDF/GLB goldens).
- CI at 52594a03 (contains the M5-T109 material blobs): CI success (5m39s), secret-scan success, context-budget success (gh run list, read-only).

DIGEST HAND-VERIFICATION (team-lead request; sha256_text_artifact = LF-normalized sha256, reproduced via tr -d '\r' | sha256sum) — ALL MATCH manifest.json:
- D-087 requirements.json ddec99c1 ✓; source-001.md 34c3dd64 ✓; source-002-amendment.md 4eea66c6 ✓
- D-083 requirements.json 1edb1a86 ✓; source-001.md 7f11a99f ✓
- D-066 requirements.json e9b7ea9f ✓; source-001.md 4cb05c94 ✓

AMENDMENTS reflected: D-087 source-002 added R011+R012 (manifest audit_log 2026-09-24T08:50; requirements.json carries both) — in the matrix; D-083/D-066 have no amendments. Every cited requirement's source digest intact.

WRITER BYTE-IDENTITY: git diff 6f9aff3c~1..HEAD over dxf_writer.py, glb_writer.py, claim_words.py, cad/__init__.py, test_cad_owner_samples.py, test_dxf_writer.py, test_claim_words.py, docs/samples/ = EMPTY. Only 154f3abe + 419cdcee touched any allowed path.

SUMMARY: 9/9 applicable requirements SATISFIED on primary evidence (D-066-R001; D-083-R001,R002; D-087-R001,R002,R004,R005,R006,R009). All 5 gates PASS (G3/G4/G5 independent, none = producer backend-engineer). Frozen identity 802274bd reproduced at live HEAD 7f5c82fa == report content_manifest == every content gate. Prohibited-action sweep clean: not accepted, 0 verification rows, not on main, PR #241 OPEN/unmerged/untouched, no blocker names it. Advisories F1 (GLB concave-footprint cap fan, fail-open, UNMOUNTED) and F2 (bbl/generated_at/generator_version screens untested) are non-blocking; neither undercuts a cited requirement. RECOMMEND recording F1 as a DISCOVERY before PKT-H mounts GLB export.

RESTAMP PREDICATE (recap): PASS restamps to any head where the 8 reviewed blob SHAs (part 1) and content_manifest 802274bd hold; broad disjoint-peer tolerance per part 1.

M5-T109 DCV VERDICT: PASS 9/9
END-OF-REPORT
