# M5-T096 — directive-compliance verification (directive-compliance-verifier "dcv-t096", read-only)

> Transmission history: pinned at 481e51ff (HEAD advanced through a disjoint orchestrator seam; the nine reviewed blobs and
> identity 8db12f2a were reproduced), delivered as an up-front restamp pre-authorization message followed by five report
> parts (1/5..5/5) ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags
> removed only). The local validator exceeded its budget; control-plane integrity was hand-verified (digests MATCH) and
> CI run 36056296954 is green. Findings F1-F4 are non-blocking.

---

M5-T096 DCV — RESTAMP PRE-AUTHORIZATION (up front). Verification in progress; verdict follows.

BLOB-LEVEL PREDICATE. My verification, once issued PASS, remains valid at any later HEAD provided ALL of the following hold byte-for-byte:
1. Frozen identity unchanged: reports/M5-T096.json content_manifest_sha256 == 8db12f2a8140c74ae17a823ae8bd22c6eabdca8378bcf2a0068e7342930c0f83.
2. The 9 reviewed blobs at material d59cbfca4210b9470896493963c666681eb1e4df are byte-identical:
- docs/samples/cad/.gitattributes ab95c38bfc9bb6ea15a4388dc91f7354ae395e05
- docs/samples/cad/README.md c3e98f73ef1d9de53e29f4886a70f37d25ea3562
- docs/samples/cad/example-massing.glb 21c1e3065d4124a91c003dc0bce11d6841a5ab17
- docs/samples/cad/example-site-plan.dxf 2c80881b3d2bee368daf7b5abce2bc63f0aafc92
- docs/samples/cad/example-site-plan.pdf d7220466c13cd401a491b2fdf8ba0e8123b9ce8d
- project-control/reports/M5-T096-producer-report.md e2efa4dfff4e613ee823905a285e4c0910f208ee
- services/api/app/cad/dxf_writer.py 6f57cdc4892073e81623bc842fa43cbe38fe2afa
- services/api/tests/cad/test_cad_owner_samples.py c0383c49d49d73cc940d9c00cfa370a7d60419e7
- services/api/tests/cad/test_dxf_writer.py 79ad39af108260da24cdec10cdc0446cb41851a5

DISJOINT-PEER TOLERANCE (broad, explicit). The verdict is NOT voided by any peer change that leaves the above byte-stable, specifically: (a) other tasks' files, gates, material commits, and packets; (b) other directives' registry binds and requirement edits; (c) the orchestrator appending MY M5-T096 verification rows to D-087 and D-066 verification.json with the matching sha256_text_artifact digest resyncs and audit_log entries; (d) docs/DISCOVERY_BACKLOG.md rows and contract-seam sweep lines; (e) lifecycle-only packet changes to project-control/tasks/M5-T096.json (status/progress/updated_at) that do not alter the frozen content_manifest_sha256. Any change to a byte in the 9 blobs or to the manifest sha voids the verdict and requires a fresh review.

---

M5-T096 DCV report 1/5 — D-087 CAD-2. Read-only, producer=backend-engineer (I am not the producer).

HEADS: verification started at 481e51ff; a disjoint peer commit landed mid-review (59737e43 "Review-record seam wave 6", other tasks' gate records) — T096's 9 blobs are byte-identical at 59737e43 (git diff 481e51ff..HEAD on the T096 paths = NONE), so the review binds unchanged. Material commit d59cbfca (9 files); reviewed_sha in reports/M5-T096.json.

FROZEN IDENTITY — VERIFIED. reports/M5-T096.json content_manifest_sha256 = 8db12f2a8140c74ae17a823ae8bd22c6eabdca8378bcf2a0068e7342930c0f83. I reproduced it two ways via directive_registry/project_control: (a) at reviewed commit d59cbfca (git-canonical, require_clean off) → 8db12f2a MATCH; (b) live clean stamp at HEAD via project_control._task_git_identity → 8db12f2a MATCH (allowed_paths clean). It equals the G1/G2/G3/G4/G5 gate content_manifest_sha256 (all 8db12f2a). G0 carries e88c827c because G0 is the administrative contract-seam gate at 64fce622 (pre-material) — expected.

GATES — all PASS, independent reviewers ≠ producer (project-control/gates/M5-T096-*.json):
- G0 orchestrator/administrative PASS (64fce622)
- G1 data-contract-verifier PASS
- G2 orchestrator/self_check PASS
- G3 code-reviewer PASS
- G4 qa-engineer PASS
- G5 security-reviewer PASS
Producer backend-engineer is none of the reviewers. G1 report (reports/M5-T096-G1.md L34-47) independently VERIFIED both producer "[recalled - verify]" items — VPORT R12 group codes 40 (view height)/41 (aspect) and the TABLES order — against the primary AutoCAD Release 12 DXF Reference (not merely recalled), and recomputed all three sample raw-blob sha256 == README.

APPLICABILITY — applicable == cited. directive_registry.evaluate_task_refs(M5-T096): ok=True, applicable_ids == cited_ids == [D-066-R001, D-087-R001, D-087-R002, D-087-R004, D-087-R006, D-087-R007, D-087-R009]; missing_ids=[], invalid_refs=[], unresolved=[]. D-087 requirements.json applicability.task_ids listing M5-T096 == the cited D-087 set exactly; wave-5 audit_log bind (manifest.json 2026-09-24T15:40) matches. Rows in 2/5–4/5.

---

M5-T096 DCV report 2/5 — requirement rows (each judged on primary evidence I reproduced).

D-066-R001 (obligation, code-graph navigation block) — SATISFIED. Primary: project-control/tasks/M5-T096.json inputs[8] carries the "CODE-GRAPH NAVIGATION BLOCK (D-066-R001; graph REGENERATED at this contract seam, 825 files / 17656 nodes / 7589 edges)" naming key consumers (pdf_sheet_writer.py CLAIM_CLASS_WORDS L54; the two writer tests), forbidden neighbors, dependencies, and the `tools/code_graph/query.py --no-regen impact` instruction — matching the R001 text (regenerate + embed consumers/deps/impact + query.py instruction, graph advisory). G0 report L25-26 records the regeneration at the seam. Compatibility held: git diff d59cbfca^..d59cbfca shows NO change to CLAIM_CLASS_WORDS or any public name; G3 confirmed pdf_sheet_writer imports CLAIM_CLASS_WORDS byte-unchanged; CI api job green with test_pdf_sheet_writer/test_glb_writer passing (consumer sweep clean).

D-087-R001 (obligation, use today's capacity via gated packets — never skip a state/gate) — SATISFIED. Primary: M5-T096 is a fully contracted→claimed→gated ledger packet: G0 at contract seam 64fce622 (commit "D-087 wave-5 contract seam"), claimed at 2e0b2351 ("G0 PASS at the contract seam 64fce622, claimed (full worktree paths), progress 20"), produced by an orchestrator-dispatched subagent concurrently with M5-T097/T098/T099/T100 + M0-T160 (G0 disjointness table lists them). All six gates recorded PASS — no state or gate skipped. Capacity is added by an additional disjoint gated packet, exactly as R001 requires.

D-087-R002 (prohibition, no interference — pairwise-disjoint allowed_paths, isolated worktree) — SATISFIED. Primary: reports/M5-T096-G0.md disjointness table — all 21 active neighbors (incl. M5-T094/T095/T097/T098/M0-T160) "none - EMPTY overlap". One isolated worktree: tasks/M5-T096.json worktree = C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t096. The cherry-pick d59cbfca touches exactly 9 files, every one inside allowed_paths (services/api/app/cad/dxf_writer.py; tests/cad/test_dxf_writer.py; tests/cad/test_cad_owner_samples.py; docs/samples/cad/{.gitattributes,README.md,example-site-plan.dxf,example-site-plan.pdf,example-massing.glb}; project-control/reports/M5-T096-producer-report.md) — zero forbidden paths touched.

---

M5-T096 DCV report 3/5 — requirement rows.

D-087-R004 (authorization, AutoCAD-openable export + a documented owner-runnable AutoCAD-open check) — SATISFIED. Primary: committed owner-openable samples docs/samples/cad/example-site-plan.dxf (7936 B), example-site-plan.pdf (1839 B), example-massing.glb (2460 B) + README.md plain-English open checklist per file (AutoCAD: Open → DXF file type → expected 4 layers LOT/BUILDING_OUTLINE/MASSING_3D/ANNOTATION, US survey feet; PDF in any viewer; GLB in Windows 3D Viewer). The DXF gained STYLE (STANDARD) + VPORT (*ACTIVE) tables (dxf_writer.py diff: _write_style_table/_write_vport_table/_vport_frame added; $ACADVER AC1009 and $INSUNITS 21 UNCHANGED per git diff). I independently confirmed the honesty stamps in the actual bytes: DXF contains "PROPOSED - NOT A CITY RECORD", "Example lot - not a real property", "EPSG:2263"; PDF contains those two labels + placeholder BBL "EXAMPLE-0000000000" (invalid borough digit 0); GLB node names carry "Example lot" + "Proposed - not a city record".
OWNER-CHECK HONESTY confirmed (this is the R004 gap the packet closes, not a claim AutoCAD opened): README says "Opening the files only proves that the export works. It does not mean any building is permitted or legal" and asks "Did each file open? (yes / no…)"; producer report L47 marks AutoCAD-open [BLOCKED] ("I cannot run AutoCAD here"); L166 records the R008 "DXF = the middleman" confirmation "still awaits the owner". So the AutoCAD open remains the OWNER's to perform and R008 stays an OPEN owner confirmation — correctly deferred, not asserted. G1 group-code-walked the committed DXF (correct R12 structure, every TEXT resolves to STANDARD, VPORT frames the extents) and PASSED.

D-087-R006 (authorization, CAD write/export through open formats first) — SATISFIED. Primary: export is DXF R12 (AC1009), PDF, and glTF 2.0 GLB — all open interchange formats, no proprietary path. dxf_writer.py serializes R12; evidence map + G1 confirm the sample DXF reads back through the accepted DXF reader (AC1009, units 21). G5 confirmed the DXF has no external refs/xdata/xref, the GLB is self-contained (embedded buffer, no uri), the PDF has no active content. Zero new dependencies (CI api-lock-verify green). Native DWG untouched (see R007).

---

M5-T096 DCV report 4/5 — requirement rows.

D-087-R007 (hold, native DWG library = owner licensing decision; DXF meanwhile) — SATISFIED (hold honored). Primary: no DWG library and no licensing decision taken. git diff d59cbfca^..d59cbfca on dxf_writer.py shows ZERO new import statements. The import test is now a genuine AST allowlist (test_dxf_writer.py: IMPORT_ALLOWLIST = {__future__, math, collections.abc, dataclasses}; test_as4_module_import_allowlist asserts imports − allowlist == {} AND allowlist − imports == {}; test_as4_allowlist_is_load_bearing proves `import json` prepended → rejected) — a DWG-lib import cannot land without reddening. No requirements.txt/in change; CI api-lock-verify + exact-production-install green. G5 confirmed native DWG untouched. See finding F1 (non-blocking allowlist gap).

D-087-R009 (prohibition, unchanged boundaries: gates, dep-security, Tier D, PR #241, unmounted max-envelope route, D-086, thin-client, D-051) — SATISFIED. Primary, each reproduced:
- Zero new dependencies: no requirements.txt/in in the 9-file diff; CI api-lock-verify (fresh hash-pinned uv lock), web-dependency-security, exact-production-install (pip-audit) ALL green at HEAD.
- No route/main.py/web change: the 9 files touch none of services/api/app/api, main.py, apps/, packages/; CI web (lint+typecheck+build) and web-e2e green.
- Max-envelope route stays UNMOUNTED: no app/api or main.py change (nothing wires it).
- .gitattributes scoped to docs/samples/cad only: patterns *.dxf/*.pdf/*.glb, file located at docs/samples/cad/.gitattributes (applies to that subtree; nothing broader) — G5 confirmed.
- PR #241 untouched: gh pr view 241 → state OPEN, mergedAt null, headRefName task/M5-T002-scenario-endpoint, updatedAt 2026-08-20 (long before this 2026-09-24 work).
- All gates G0-G5 recorded; modularity CI gate green (dxf_writer.py 671 SLOC WARN band, cohesion justification recorded — G3/F4). D-051/Tier D not implicated (no legal rule, no production/merge/deploy action).

---

M5-T096 DCV report 5/5 — harness, prohibited-action sweep, findings, verdict.

HARNESS EVIDENCE. Control-plane integrity verified by-hand (the exact validator c14/source/locked-id checks) + CI:
- D-087: requirements_content_digest MATCH (ca5ba8eb); source-001.md + source-002-amendment.md LF-normalized digests MATCH manifest; locked_requirement_ids == requirements ids (12).
- D-066: requirements_content_digest MATCH (bbfa25a4); source-001.md MATCH.
- CI control-plane job (validator wired in, ADR-005) = success at HEAD; api (ruff+pytest) success on Linux 3.12 — runs tests/cad/test_cad_owner_samples.py, the byte-identity proof for the three samples; all 18 CI jobs green (run 36056296954, headSha 481e51ff, contained in 59737e43). a612652b CI workflow (the G1-cited head) also success.
- My one authorized `validate_directive_compliance.py --check` (launched at 59737e43, no pipe) exceeded the ~15-min budget without emitting its buffered result; NOT re-run. Resolved via the dispatch-blessed fallback above (see F2).

PROHIBITED-ACTION SWEEP — clean:
- Not accepted: tasks/M5-T096.json status = awaiting_gate.
- No verification row: grep "M5-T096" in D-087 and D-066 verification.json = 0.
- Not on main: d59cbfca not in main/origin/main (candidate-branch ancestor only).
- PR #241 untouched (OPEN, unmerged).
- No open blocker names M5-T096.

FINDINGS (all NON-BLOCKING):
- F1: G4 advisory A1 — the AST import allowlist is blind to the `__import__("name")` builtin (dynamic import produces no Import node); beyond the stated AS-4 mutation, mitigated by the dependency-security lockfile/age gate (a DWG lib still cannot install) + code review. Does not weaken the R007 hold.
- F2: local validator --check exceeded the time budget with no buffered output; verified control-plane integrity by hand + green control-plane CI instead (dispatch-sanctioned). No re-run.
- F3: HEAD advanced 481e51ff→59737e43 during review (disjoint peer seam, other tasks' gates); T096 blobs byte-identical — within the restamp predicate I gave up front.
- F4 (informational, routed at accept per G3/G4/G5): modularity 671-SLOC WARN band w/ recorded cohesion justification + future facade split; GLB title-case honesty label vs DXF/PDF upper-case (DSC-1); README optional third-party web glTF viewer wording (harmless for synthetic); README-sha test hashes checkout bytes but fails safe via .gitattributes binary marking (G1 verified raw-blob==README).

RESTAMP PREDICATE: as sent up front — the 9 named blobs at d59cbfca + manifest identity 8db12f2a byte-stable; broad disjoint-peer tolerance (other tasks/directives, my verification-row appends with digest resyncs+audit entries, DISCOVERY_BACKLOG/sweep lines, lifecycle-only packet changes). Confirmed still satisfied at 59737e43.

Every applicable requirement is SATISFIED on reproduced primary evidence; no VIOLATED/UNVERIFIABLE/BLOCKED.

M5-T096 DCV VERDICT: PASS 7/7

END-OF-REPORT
