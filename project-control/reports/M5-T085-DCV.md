# M5-T085 — directive-compliance verification (directive-compliance-verifier "dcv-w1", read-only; joint DCV for M5-T084 / M5-T085 / M5-T087)

> Transmission history: one joint verification pinned at 71ab388a (live HEAD advanced to 0ffe581c during
> the review through disjoint orchestrator commits; the verifier observed identity MATCH at every peer
> head), announced as five parts and delivered as FOUR SendMessage parts (PART 4 marked "final") ending
> with END-OF-REPORT; no truncation. Joined verbatim in delivery order by the orchestrator (transport
> wrapper tags removed only); saved identically as M5-T084-DCV.md, M5-T085-DCV.md and M5-T087-DCV.md.
> Identity note: commit 744154df (D-087 source-002 amendment, R011/R012 bound only to D-087-BOOTSTRAP)
> landed after the freeze; the predicate confirmation requested from the same verifier is appended below
> when received.

---

DCV REPORT (dcv-w1) — M5-T084 / M5-T085 / M5-T087 (D-087). PART 1 of 5.

Pinned HEAD at start: 71ab388a. Live HEAD now: 0ffe581c (moved 4x during review via disjoint orchestrator peer commits — 71ab388a→acb224b2→…→0ffe581c; NONE touch these three tasks' files). Method: I reproduced every stamp from primary evidence (registry helper, git objects, deterministic tests) — producer reports/evidence maps treated as claims only.

RESTAMP PRE-AUTHORIZATION (up front), blob-level, per task. This PASS stands at ANY head where each task's allowed_path blobs equal these SHAs (i.e. _task_git_identity(task,HEAD) == the frozen content_manifest_sha256), currently true at 0ffe581c:
- M5-T084 → identity f1d130ab… ; blobs: dxf-format-reference ffc1aaa8, architect-drawing-corpus f117b0ae, 3d-web-deps-prescreen dd35231b, reports/M5-T084-producer-report 771f175f.
- M5-T085 → identity e2581651… ; blobs: app/cad/pdf_sheet_writer.py 473ef5ea, tests/cad/test_pdf_sheet_writer.py 600c8f6f, reports/M5-T085-producer-report 229a7766.
- M5-T087 → identity 07cf9683… ; blobs: docs/research/building-footprints-source 9eec8134, reports/M5-T087-producer-report 051ab70e.

Disjoint-peer tolerance (broad, explicit): I tolerate ANY orchestrator commit between this freeze and the accept record PROVIDED it does not alter the nine blobs above — including other tasks' files (M5-T077..T086, apps/web, etc.), other material, your adding MY D-087/D-066 verification rows to verification.json, and other directives' registry edits that leave these three tasks' evaluate_task_refs == ok (applicable==cited). Any change to one of the nine blobs, or any registry change that makes evaluate_task_refs != ok for a task, voids that task's predicate and needs a re-freeze. I already OBSERVED identity MATCH=True across all four peer-commit heads.

---

PART 2 of 5 — CROSS-CUTTING (all three) + M5-T084 rows.

CROSS-CUTTING (reproduced):
- Registry integrity: `validate_directive_compliance.py --check` → EXIT 0 (single direct run). D-087 v1, 10 reqs, no amendments; requirements_content_digest 248e2b9e…, source-001 34c3dd64…; validator confirms source digests/locked-ids/vocab/digest — LF-normalized digests clean. D-087 + D-066 both `active` in index.json.
- Hold notice: .claude/rules/expansion-agent-dispatch-hold.md §2.3 records the D-087 scoped release (3D massing, CAD export DXF w/ native-DWG as owner decision, phase-C PDF read + blueprint write, CAD write/edit/export) citing D-087, plus the D-082 pointer — as the audit_log promised.
- Applicability: evaluate_task_refs ok=True, applicable==cited, missing/invalid/unresolved all empty for all three (reproduced via directive_registry). reports/<task>.json applicable_requirements == task.directive_refs.
- Frozen identity chain: for each task _task_git_identity@HEAD == reports/<task>.json content_manifest_sha256 == every post-submit gate's content_manifest_sha256 (G0 differs — it is pre-submit administrative, correct). Reviewed_sha varies per gate (peer commits) but path-scoped identity is byte-stable.
- Material commits touch EXACTLY allowed_paths: T084=075cc555 (4 files), T085=519bc360 (3 files; NO __init__/requirements/route), T087=a01d5fac (2 files).
- Prohibited-action sweep: all three status=awaiting_gate (NOT accepted); D-087 verification.json task_verifications=[] (no rows yet); on branch candidate/D-024 (not merged to main); nothing in the diffs touches PR #241; NO open blocker names any of the three (word-bounded). B-026 open but its affects = "D-087-R001 loop-lane share" — names no task id, does not gate them (see F1).
- No native-DWG library anywhere: repo scan of requirements*.in/.txt, apps/web/package.json, and source imports → zero ezdxf/libredwg/realdwg/oda/teigha tokens (R007).

M5-T084 (research; gates G0,G1[data-contract-verifier],G2[orch self],G3[security-reviewer] all PASS @ f1d130ab):
- D-066-R001 SATISFIED — CODE-GRAPH NAVIGATION BLOCK in M5-T084.json inputs (graph 815 files/17025 nodes; names consumers M5-T081/T083 + strict reader).
- D-087-R001 SATISFIED — contracted/claimed(07:25)/gated in-regime packet citing R001; wave-1 concurrent subagent producer (material 075cc555; G0 lists concurrent T081/82/83/85).
- D-087-R002 SATISFIED — G0 disjointness table EMPTY overlap all neighbors; worktree wt-m5t084; material touches only the 4 docs/report paths.
- D-087-R004 SATISFIED — docs/research/dxf-format-reference-2026-09.md grounds the AutoCAD-openable DXF middleman with OFFICIAL Autodesk facts: R12/AC1009 minimal file, $INSUNITS 21 = US Survey Feet (version-bracketed [HDR2016] absent/[HDR2017] present), LINE/LWPOLYLINE/3DFACE/TEXT group codes, retrieved_at + PDF sha256 6c56324c.
- D-087-R005 SATISFIED — docs/research/architect-drawing-corpus-2026-09.md: 6 REAL public-domain drawings (3 vector VA-CAD + 3 scanned HABS/HAER) w/ URL, publisher, reuse basis, bytes, sheet types, vector-vs-scanned, producing app, sha256; downloaded to scratch only (nothing in repo); real-file corpus precedes C1 reader widening.
- D-087-R006 SATISFIED — same note establishes DXF-out open interchange (R12 ASCII), aligned to SURVEY_DOCUMENT_FORMAT_POLICY; docs-only.
- D-087-R007 SATISFIED — note keeps native DWG out of scope (AutoCAD saves DWG from DXF); repo scan confirms no DWG lib adopted; ezdxf named only as a DXF (not DWG) option, not a dependency.
M5-T084 → PASS 7/7.

---

PART 3 of 5 — M5-T085 and M5-T087 rows.

M5-T085 (backend; gates G0,G2[orch self],G3[code-reviewer],G4[qa-engineer],G5[security-reviewer] all PASS @ e2581651):
- D-066-R001 SATISFIED — navigation block in M5-T085.json inputs (app/cad seam; forbidden sibling dxf_writer.py; reader read-only).
- D-087-R001 SATISFIED — contracted/claimed/gated in-regime packet citing R001; wave-1 subagent producer backend-engineer (material 519bc360).
- D-087-R002 SATISFIED — G0 EMPTY overlap; worktree wt-m5t085; material touches ONLY app/cad/pdf_sheet_writer.py + tests/cad/test_pdf_sheet_writer.py + report — NOT the forbidden __init__.py / dxf_writer.py / requirements / api route.
- D-087-R005 SATISFIED — services/api/app/cad/pdf_sheet_writer.py: deterministic PDF 1.4 site-plan from canonical EPSG:2263 rings; per-edge dimension strings computed server-side from 2263 coords, rounding declared (2 dp, _label_edges L266-269); choose_scale + scale bar; grid-north arrow "GRID N (EPSG:2263)" (never true north, L280); title block with "PROPOSED - NOT A CITY RECORD" + "Not for construction - professional review required" (L308-309); one escaper _escape_pdf_text (L329); typed SitePlanRefusal fail-closed. Primary OBSERVED (I ran them): ruff EXIT 0; pytest 19/19 pass in 0.33s incl. golden sha256 c38360f9, round-trip counts, dims 30/100/20/60, escaper-bypass mutant reddens round-trip, xref-offset corruption detected. Honesty/measurement rules bind and hold.
- D-087-R009 SATISFIED — writer imports only stdlib (math, dataclasses); material touches no requirements.txt/.in, no package.json/lockfile, no route/app/main.py/web; module is UNWIRED (max-envelope route stays unmounted); modularity clean (400 SLOC, no flag on this file). Zero new dependencies confirmed at code + lockfile level.
M5-T085 → PASS 5/5.

M5-T087 (research; gates G0,G1[data-contract-verifier],G2[orch self],G3[geospatial-engineer] all PASS @ 07cf9683):
- D-066-R001 SATISFIED — navigation block in M5-T087.json inputs (future connector beside mappluto_geometry_arcgis.py + massing model).
- D-087-R001 SATISFIED — contracted/claimed/gated in-regime packet citing R001; wave-1.5 subagent producer official-source-researcher (material a01d5fac).
- D-087-R002 SATISFIED — G0 EMPTY overlap vs all neighbors incl. the five wave-1 packets; worktree wt-m5t087; material touches only the 2 doc/report paths.
- D-087-R003 SATISFIED — docs/research/building-footprints-source-2026-09.md records the OFFICIAL OTI "BUILDING" dataset (NYC Open Data 5zhs-2jue / ArcGIS BUILDING_view/FeatureServer/0): field meanings HEIGHT_ROOF (above ground, not sea level), GROUND_ELEVATION (NAVD88), BIN, BASE_BBL, MAPPLUTO_BBL — each quoted from the City metadata dictionary w/ URL + retrieved_at; units feet (labelled well-supported INFERENCE, RQ-1); CRS source 2263, channels 3857/4326, outSR=2263 verified live; geometry type; access channels + limits (maxRecordCount 2000, deterministic paging); one-BBL+neighbours request shape; MapPLUTO condo/billing-lot join (7501-7599 empirically confirmed); cadence/licence/8 quality limits; inferences labelled, residuals RQ-1..6 listed; NO connector code (correct scope for recon feeding a later G1). Aligns with geospatial rule (official source first; provenance; no guessed schema/unit/datum).
M5-T087 → PASS 4/4.

---

PART 4 of 5 (final) — FINDINGS + VERDICTS.

FINDINGS (all advisory / non-blocking — none downgrades a SATISFIED):
- F1: B-026 is OPEN; its affects names "D-087-R001 (the loop-lane share of today's capacity ramp)" — the codex loop-lane launch REFUSED exit 11 (controller/cli manifest). It names NONE of M5-T084/T085/T087 (word-bounded) and does not gate them: R001 for THESE three is met via the orchestrator-dispatched-subagent channel, which delivered. B-026 concerns the separate loop-lane channel of the same requirement — a directive-level open item for you, not a task-level violation here.
- F2: T084 DXF note §6/§8 flags the R2000+ OBJECTS-section minimal root-dictionary as [NEEDS G1 RE-VERIFICATION] — honestly disclosed, non-blocking for the recommended R12 target; the future DXF-writer (M5-T081) G1 must close it only if it emits R2000+.
- F3: T087 height unit "feet" is a well-supported INFERENCE (no explicit per-field unit tag), flagged RQ-1 for the future connector's G1 — correct honesty posture; must be resolved before any measurement reliance (this packet is recon only, so fine).
- F4: Most-recent FULLY-completed main CI (success) is at the 08:23Z head; the T084/T085/T087 gate-record commits and the live HEAD show CI in_progress/cancelled (own-push cancellation is expected). context-budget + secret-scan pass on the latest; the authoritative registry evidence is my local `validate_directive_compliance.py --check` EXIT 0. Routine: confirm the control-plane CI job green at a settled head at/around accept.

Reviewer independence confirmed: producers are official-source-researcher (T084/T087) and backend-engineer (T085); none reviews its own task; every required gate has an independent reviewer present in reviewer_agents.

VERDICTS:
M5-T084 DCV VERDICT: PASS 7/7
M5-T085 DCV VERDICT: PASS 5/5
M5-T087 DCV VERDICT: PASS 4/4

Restamp predicate + broad disjoint-peer tolerance are in PART 1. No VIOLATED / UNVERIFIABLE / BLOCKED result for any requirement id. All three tasks are directive-compliant at the frozen identities and clear for acceptance under the PART-1 predicate.

END-OF-REPORT

---

## Predicate confirmation (same verifier, one SendMessage, END-OF-REPORT; requested after the D-087 source-002 amendment landed at 744154df)

DCV predicate check (dcv-w1) @ f2870507 — read-only.

(1) Nine blobs UNCHANGED at f2870507 — all nine `git rev-parse f2870507:<path>` equal my frozen SHAs (dxf-format ffc1aaa8, corpus f117b0ae, deps dd35231b, T084-report 771f175f, pdf_sheet_writer 473ef5ea, test 600c8f6f, T085-report 229a7766, footprints 9eec8134, T087-report 051ab70e).

(2) evaluate_task_refs still OK — M5-T084/T085/T087 each ok=True, applicable==cited, missing/invalid/unresolved all empty; _task_git_identity@f2870507 MATCH=True (f1d130ab / e2581651 / 07cf9683), err=None.

(3) Amendment is inert to these three — manifest.amendments=[source-002-amendment.md]; D-087-R011 and D-087-R012 both bind ONLY "D-087-BOOTSTRAP" (verified in requirements.json), so no existing text changed and the three tasks' applicable set is untouched; registry.errors=[] and D-087.errors=[] (digest resync valid).

RULING: This same-directive amendment sits INSIDE my PART-1 restamp predicate — it satisfies both conditions (nine blobs unchanged; evaluate_task_refs==ok, applicable==cited) and only adds sentinel-bound rows. The three PASS verdicts (M5-T084 7/7, M5-T085 5/5, M5-T087 4/4) CARRY to f2870507, and to any later head meeting the same two conditions.

END-OF-REPORT
