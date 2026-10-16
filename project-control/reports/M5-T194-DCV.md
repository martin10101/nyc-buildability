# M5-T194 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `95e6f299cb008d79ef9c4017258ee9532b2a81a6` (branch `task/wave29-scenario-drawings`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R050, R095, R098, R198, R200, R203, R204, R205, R277, R278.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. No defect blocks this task's share; all 10 rows PASS for their share with the carry items named above. - Observation (not a correction): the G3 reviewer's ADVISORY 1 said 'illustrative_footprint' existed only in manifest.py (part B1 unbuilt at f9fee602). At the frozen head the kit style (kit/styles.py:178) and maps/placed_footprint.py (FOOTPRINT_KIND = "illustrative_footprint") already carry the exact literal (sibling parts landed after f9fee602), so the cross-part contract now matches and the chart can read a real footprint once wired; the wiring part's integration test should still pin this literal equal to the kit style kind (RISK 1).
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-16 01:44:03 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T194 (directive D-094, 10 rows)
VERDICT: PASS

(1) HEAD VERIFIED
 - I read the frozen head 95e6f299cb008d79ef9c4017258ee9532b2a81a6 on task/wave29-scenario-drawings in /root/project/w-wave29 via git plumbing (git show 95e6f299:<path>).
 - While I worked, the branch HEAD advanced to e016a59d (sibling M5-T173 G0/claim/progress, exactly as the brief warned); the frozen head 95e6f299 and the task's blobs were unchanged by it.
 - The task's 6 allowed-path files carry identical blob ids at the material commit 7f6dc46c, the submit/review head 8e1d5912 and the frozen head 95e6f299 (e.g. manifest.py ecdd629d, drawings_embed.py 3acb7fcc, page_option_comparison.py 70d9e7bb, page_evidence.py 967b66b4, test_report_drawn_manifest.py 67e358d0, producer-report.md 248eea28); the builder commit f9fee602 has blobs EQUAL to the cherry-pick 7f6dc46c, so the reviewed content identity carries unchanged to the frozen head.

(2) ROWS
ROW D-094-R050 — PASS
 - Source text confirmed verbatim at source-001.md line 147 ("Retain the existing six status meanings … Do not remove uncertainty to imitate the competitor's confidence"); requirements.json row text matches and lists M5-T194 in applicability.task_ids.
 - This task's share preserves uncertainty rather than removing it: the page-5 chart's placed-on-site status keeps three honest states ("Not demonstrated" / "Worked out; not drawn" / "Shown on the site plan") and the appendix clause never says "shown" without a drawn SVG (reproduced in test_s2/test_s3 and my own probe).
 - The six D-090 status-label chips themselves (label_chip(row["status_label"])) are untouched by this task — only the honest-state selection moved to rendered content, so no meaning was dropped.
 - Stays open: the whole-report "every output carries one status / promotion check" scope belongs to the other bound tasks (M0-T193, M5-T165); this task only touches the page-5 chart status and the page-10 appendix method clause.

ROW D-094-R095 — PASS
 - Source text confirmed verbatim at source-003-amendment.md lines 30/32 ("Keep the explanation to one short caption." "Put methodology in the appendix.").
 - This task's share keeps the area-illustration METHOD in the evidence appendix: page_evidence._area_illustration_method() emits one fixed sentence per manifest state ('zones'/'bar' name where it is drawn on the scenario sheet; otherwise "not yet drawn"), figures still read from the document block (verified by reading the diff and test_s3).
 - The method lives in page_evidence.py (the appendix page type), not on the scenario sheet, so the methodology placement is correct.
 - Stays open: the "one short caption beside the illustration" on the scenario sheet is page_scenario_sheet.py (a forbidden path here); it belongs to the scenario-sheet/wiring work (M5-T173).

ROW D-094-R098 — PASS
 - Source text confirmed verbatim at source-003-amendment.md line 32 ("Verify the rendered result for readability and consistency before marking it complete.").
 - This task renders no new page: every new keyword defaults to byte-identical legacy output (test_s1; producer/reviewers report the full tests/drawings/report folder = 235 passed unedited; I reproduced the 8-test manifest file, exit 0), so the only rendered-consistency obligation in this task's share (do not disturb existing output) is met by proven byte-identity.
 - The manifest this part adds is the record that lets the wiring part check readability against actually-drawn content (evidence map R098).
 - Stays open: the substantive rendered-readability check WITH screenshots/export record is not produced by this task (nothing new renders) and is entirely owed by the wiring part M5-T173 — the orchestrator should bind R098 (and R198/R200/R203/R204/R205/R277/R278) to M5-T173 at its contract.

ROW D-094-R198 — PASS
 - Source text confirmed verbatim at source-028-amendment.md section 3 ("Page 5 said the building was 'Shown on the site plan.'"; handoff: page 5 reads "Worked out; not drawn" at e026a391).
 - This task's share makes the chart's "Shown on the site plan" selected by the manifest's footprint flag read from the rendered site plan (drawings_embed.allowance_bar_chart_svg footprint_drawn; manifest.site_plan_draws_footprint = site_plan.is_drawing and 'illustrative_footprint' in kinds_drawn); my probe: footprint kind among other kinds -> "Shown"; absent -> "Worked out; not drawn".
 - In the still-unwired live report the kept legacy predicate site_plan_draws_placed_footprint() returns a hard-coded False (drawings_embed.py), so page 5 reads "Worked out; not drawn" today — honest and matching the handoff.
 - Stays open: passing footprint_drawn=manifest.site_plan_draws_footprint from builder.py and the real-print page re-check are the wiring part M5-T173's.

ROW D-094-R200 — PASS
 - Source text confirmed verbatim at source-028-amendment.md section 3 ("Page 10 said the allocation was shown as zones inside the placed footprint, but no such zones appeared anywhere.").
 - This task's share makes the appendix name the scenario sheet only when the manifest state is 'zones' or 'bar' (derived from the kernel's own area_zone_*/area_bar_* SVG data-roles), else "not yet drawn"; reproduced in test_s3 and my probe (state 'zones' -> "shown as zones inside the placed building footprint on the scenario sheet"; None/'not_drawn' -> "not yet drawn").
 - The manifest reads the data-roles that kit/area_allocation.py actually emits (roles at lines 427/429 bar, 459/461 zones), confirmed by reading the kit source.
 - Stays open: actually drawing the zones inside the fitted footprint (R094) and wiring the manifest into the live page-10 appendix are the wiring/B parts.

ROW D-094-R203 — PASS
 - Source text confirmed verbatim at source-028-amendment.md section 3 ("A data field such as 'placement.status = placed' … or 'area_allocation.fitted = true' is not proof that a drawing was rendered.").
 - manifest.py reads ONLY rendered Embedded values (Embedded.is_drawing, Embedded.kinds_drawn, Embedded.svg data-roles) — no results field, no placement.status, no floor_plates, no area_allocation.fitted, no arithmetic (verified by reading the full file); my probe fed data-only (non-drawing) Embeddeds and got site_plan_draws_footprint=False and area_illustration_state=None.
 - The chart's drawn/shown status and the appendix drawn clause now read the manifest; the kept legacy fallbacks are conservative hard-coded False (never a data field), so no visible DRAWN claim in this task's code rests on a data field.
 - Stays open: the full removal of the legacy predicates and routing EVERY drawing claim through the manifest is the wiring part M5-T173's.

ROW D-094-R204 — PASS
 - Source text confirmed verbatim at source-028-amendment.md section 3 ("Inspect the report readers and conditions … 'building_not_placed()' could return false based on available geometry …").
 - I reproduced the inventory claim at the frozen head: readers.building_not_placed() (readers.py:588) keys on geometry.floor_plates.status only, a data field, never on whether a drawing was rendered.
 - This task's share records the predicates (packet business_reason: drawings_embed.py:212-221, page_evidence.py:140-146 hard-coded False; page_option_comparison.py:32-35 data-field read) and adds the DrawnManifest rendered-content basis, moving the chart's "Shown on the site plan" status onto it.
 - Stays open: the complete claim-by-claim inventory and making every claim read the manifest (and keeping building_not_placed as a placement-DATA signal, never a drawing claim) are the wiring part M5-T173's.

ROW D-094-R205 — PASS
 - Source text confirmed verbatim at source-028-amendment.md section 3 ("Make claims about visible content depend on the content actually included in the output. Correct page references, legends, comparison-table statuses, and methodology together.").
 - This task's share makes the chart status and the appendix clause depend on what the output includes (the manifest from Embedded values); the row's unit harness ("data without the drawing makes claims say not drawn; with it, they name the page") is proven by test_s2 (footprint True->"Shown", False->"Worked out; not drawn") and test_s3 (zones/bar->names the sheet; not drawn->"not yet drawn").
 - The behavior defaults keep unwired callers byte-identical (test_s1), so no existing claim regressed.
 - Stays open: correcting page references, legends and comparison-table statuses together across the LIVE report in one change is the wiring part M5-T173's.

ROW D-094-R277 — PASS
 - Source text confirmed verbatim at source-028-amendment.md line 305 ("Cover meaningful cases: placement data with a rendered drawing …").
 - This task's share covers the "placement data WITH the drawing rendered -> claims say shown" case: manifest footprint flag True -> chart "Shown on the site plan" (test_s2); zones/bar drawn -> appendix names the scenario sheet (test_s3).
 - The named test test_report_drawn_manifest.py (8 tests) is green in CI at the candidate head: CI run 38834850070 at 8e1d5912 = 21/21 jobs success (I confirmed via gh), and I reproduced the 8 tests myself (exit 0, under the heavy-run lock).
 - Stays open: the printed page-reference "with the page" on the REAL integrated print is the wiring part M5-T173's (its S2/S8); this task renders no page.

ROW D-094-R278 — PASS
 - Source text confirmed verbatim at source-028-amendment.md line 305 (same "Cover meaningful cases" sentence; this row is the "placement data WITHOUT a rendered drawing" case).
 - This task's share covers it: footprint flag False -> chart "Worked out; not drawn" (test_s2); an explicit not-drawn illustration state -> "not yet drawn" WITHOUT reading the legacy predicate (test_s3_explicit_not_drawn_state_ignores_the_legacy_predicate, proven with a monkeypatch that forces the legacy predicate True and shows only the None/legacy path moves); a failing map footprint keeps the map with a note (test_s6).
 - Named test green in CI (run 38834850070, 21/21 at 8e1d5912) and reproduced locally (8 passed, exit 0).
 - Stays open: the degenerate-footprint state on the real print is the wiring part M5-T173's (its S4).

(3) BINDING B1–B5
 - B1 PASS: the contract commit ed30635d appended ONLY "M5-T194" to the task_ids of all 10 rows (R050 after M5-T165; R095 after M5-T193; R098 after M0-T197; R198/R200/R203/R204/R205/R277/R278 after D-094-BOOTSTRAP) plus the updated_at timestamp; no row "text" field was removed or changed (verified from the full requirements.json diff). All 10 rows carry M5-T194 at the frozen head.
 - B2 PASS: I recomputed directive_registry.sha256_text_artifact over requirements.json at the frozen head = 9ed95b1792e22ed1ee627872e56f184145662f86624c434df557d093de140ad5, which equals manifest.requirements_content_digest_sha256 at the frozen head.
 - B3 PASS: verification.json holds exactly one M5-T194 task row with applicable_requirement_ids = the 10 ids, verifier = "" (empty), reviewed_sha null, every requirement state "pending" (producer = backend-engineer, the task's material producer; producer != verifier).
 - B4 PASS: reg.evaluate_task_refs(M5-T194) returns ok=True, applicable_ids == cited_ids == the 10 ids, missing_ids=[], invalid_refs=[], unresolved=[] (registry loaded with no errors).
 - B5 PASS: applicable == cited with empty missing across all 93 active directives in index.json, so nothing else applies to M5-T194 uncited; tools/validate_directive_compliance.py --check exited 0. GATES: G0 PASS (orchestrator, administrative, reviewed_sha ed30635d), G2 PASS (orchestrator self_check), G3 PASS (code-reviewer), G4 PASS (qa-engineer); G2/G3/G4 all at one content identity reviewed_sha 8e1d5912 + content_manifest_sha256 0ba7d7bd2aad582ff05c001ddbedf3f0f2e79591273824f1f8bd898a00de6293. (B2/B4/B5 were evaluated against the working tree at e016a59d, whose M5-T194 bindings and the 10 row texts are blob-identical to the frozen head; validator exit 0 corroborates registry integrity.)

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review while BOTH hold:
 - Blob predicate: the 6 allowed-path files keep their frozen-head blob ids — manifest.py ecdd629dd68eec8d54f5809ae48543eaf733617d, drawings_embed.py 3acb7fcc5ac8b99322ac69831adc14cea0e67396, page_option_comparison.py 70d9e7bb3bde20792479777cc857d95ce9c993bb, page_evidence.py 967b66b4158393abd0ea083619227bc4d858ff13, test_report_drawn_manifest.py 67e358d0940125ac72371f73c407bbbce766f7d2, project-control/reports/M5-T194-producer-report.md 248eea288dfc8deb161cf441b8dd7e050490d91d; AND the 10 rows' text and their M5-T194 applicability binding are unchanged.
 - Broad disjoint-peer tolerance: later commits MAY touch any other file (other wave-29 tasks' sources under services/, apps/, packages/, docs/, .claude/, their packets/gates/reports; OTHER tasks appended to the applicability of these same 10 rows, e.g. the wiring part M5-T173 at its contract with the resulting digest resync and provisional verification rows; new rows appended to D-094; ledger state), plus this task's own acceptance records and a merge of the main line that changes none of the predicate's files. Note: a digest resync by a peer/binding append changes manifest.requirements_content_digest_sha256 — that is tolerated provided the 10 rows' text is byte-unchanged (verify with the recorded 95e6f299 row-text/blob if challenged).

(5) REQUIRED CORRECTIONS
 - None. No defect blocks this task's share; all 10 rows PASS for their share with the carry items named above.
 - Observation (not a correction): the G3 reviewer's ADVISORY 1 said 'illustrative_footprint' existed only in manifest.py (part B1 unbuilt at f9fee602). At the frozen head the kit style (kit/styles.py:178) and maps/placed_footprint.py (FOOTPRINT_KIND = "illustrative_footprint") already carry the exact literal (sibling parts landed after f9fee602), so the cross-part contract now matches and the chart can read a real footprint once wired; the wiring part's integration test should still pin this literal equal to the kit style kind (RISK 1).

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - No rendered PDF / live-report behavior: this part changes no rendered page (byte-identical), so the integrated page references, legends and the R098 screenshot/export readability record are the wiring part M5-T173's; I rendered nothing.
 - I did not re-run the full tests/drawings/report folder (235 tests), the full api suite, or tools/test_directive_compliance.py (forbidden/heavy); for the 235-folder pass and the whole-api G2 (10179 passed) I relied on the producer/reviewer reports and CI run 38834850070 (21/21 success at 8e1d5912), and reproduced only the focused 8-test manifest file myself (exit 0) plus my own direct probe.
 - I did not open the H4 input return-H4-claims-manifest.md (outside the repo); I verified the inventory claims directly against readers.py:588 and the edited modules instead.
 - B1 kit emission of the footprint kind at render time and the kernel's live SVG data-role serialization I confirmed by reading kit source + the passing test (which builds real drawings), not by rendering a full report.
 - Reference-case cross-check (docs/reference-cases/R6B/cases/) was N/A: none of these 10 rows turns on a zoning figure the reference cases settle (they govern honest drawn/shown/placed claims and status, not legal figures).
 - B2/B4/B5 were computed against the w-wave29 working tree at e016a59d; the frozen head 95e6f299 differs only by sibling-task bindings, and M5-T194's rows/blobs are identical between the two, so the results hold at the frozen head.
END-OF-REPORT
```
