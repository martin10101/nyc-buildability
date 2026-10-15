# M5-T183 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `3170556fea13b2176818bbd1878363d92572e563` (branch `task/wave26-envelope-constraints`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R024, R087, R088, R089, R090, R091, R092, R093, R094, R095, R098.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. No VIOLATED or UNVERIFIABLE row. All open items are out-of-scope successor work (M5-T173 Part B / M5-T174 / M0-T195) and all recorded findings are ADVISORY (G1 one advisory; G3 code three advisories; G3 visual three advisories; G5 one comment-wording advisory after F1–F3 were closed) — none blocks this task's share.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-15T08:25:11Z, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T183 (directive D-094, 11 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier), read-only. This is an automated reproduction of evidence, not a human or professional review. I produced none of this work. I judged THIS TASK'S SHARE of each row from primary evidence at the frozen head and relied on the producer's maps/reports only as claims to reproduce.

(1) HEAD VERIFIED
 - Frozen head read: 3170556fea13b2176818bbd1878363d92572e563 on task/wave26-envelope-constraints (base main 2bcdb05a). Its subject is the M5-T183 review-record/evidence-map commit.
 - Every row, packet, source, kernel, test, snapshot, gate and digest below was read with `git show 3170556f:<path>` (pinned), not from a drifting checkout.
 - Mid-session the branch HEAD advanced to 087670a9 (a parallel M3-T010 control-plane commit); `git diff 3170556f 087670a9` touches none of this task's files, and the on-disk kernel/test/two-snapshot files hash-match the 3170556f blobs exactly, so my focused test/ruff/modularity runs are valid for the frozen head.

(2) ROWS

ROW D-094-R024 — PASS
 - Owner source (source-001.md#attached-brief line 99/229): "Do not silently equate gross floor area, zoning floor area, and apartment area."
 - The kernel prints the block's measure tag "Residential floor area" and the exact conversion statement "plate = zoning floor area per storey; no gross-up, exclusions or wall-thickness conversion worked", so the basis is disclosed, never silently equated (both snapshots carry both lines; test_s6 asserts "zoning floor area" absent from the measure tag).
 - An apartment/other split that does not reconcile to total, or whose apartment/total disagrees with share, returns Unavailable (test_s3_inconsistent_split_is_unavailable, reproduced: 37/37 tests pass).
 - Stays open: R024's wider report-schedule obligations (displayed rounding/totals reconcile, accounting in the appendix) belong to the schedule/report tasks, not this drawing kernel.

ROW D-094-R087 — PASS
 - Owner source (source-003-amendment): the remaining 25–40% must not all be called "core and corridors".
 - The second zone is labelled from token area_zone_other = "Other building area: core, circulation, walls and services" — never "core and corridors" (verified in presentation_tokens.py and in both snapshot <text data-role="area_label_other">).
 - test_s2_labels_and_caption_are_the_tokens_verbatim pins this string; 37/37 pass.
 - Nothing stays open: the decision is fully honoured in this kernel.

ROW D-094-R088 — PASS (this task's share)
 - Owner source authorizes a simple two-zone illustration under R089–R098.
 - The illustration exists as a leaf kernel services/api/app/drawings/kit/area_allocation.py in both states (bar when unfitted, two zones when fitted+placed), with two byte-stable snapshots; scenarios S1–S9 reproduce.
 - Stays open: placing the illustration on the worked scenario (PDF) and website is M5-T173 Part B and M5-T174; this task does no report/website wiring (forbidden_paths bar it, evidence map "what_did_not_change").

ROW D-094-R089 — PASS
 - Owner source: zones labelled exactly "Apartment area" and "Other building area: core, circulation, walls and services".
 - The drawing renders both labels byte-equal to the committed WORDING tokens (snapshots + test_s2; token values confirmed "Apartment area" and "Other building area: core, circulation, walls and services").
 - Observation: the token (and thus the drawing) omits the trailing period present in the owner's quoted sentence; the canonical WORDING string is owned by M5-T165 (presentation_tokens.py is in this task's forbidden_paths), so the period decision is not this kernel's to set — this kernel correctly consumes the approved token verbatim.
 - Nothing stays open in this kernel's share (labels are the approved tokens, verbatim).

ROW D-094-R090 — PASS
 - Owner source: caption "Illustrative area allocation—not a floor plan."
 - The drawing prints token area_illustration_caption = "Illustrative area allocation—not a floor plan" with an em dash, exactly one caption element, same trailing-period note as R089 (test_s2 asserts no trailing period and count==1; both snapshots carry one caption).
 - caption=False can omit it for the report frame (test_s2_caption_can_be_omitted_for_the_report_frame).
 - Nothing stays open in this kernel's share.

ROW D-094-R091 — PASS
 - Owner source: one explicitly stated percentage from the 60–75% assumption; drawing and calculation consistent; percentage shown beside it.
 - The kernel prints round(share*100) as "65%/70% apartment area" (never hardcoded: test_s4) and enforces share in 0.60–0.75 (out-of-range → Unavailable, test_s8); the drawn proportion equals share within 0.5% in both states (bar 189.80/292.00=0.65; zones 137.20/196.00=0.70; test_s3).
 - On the fixtures the drawn ratio also equals apartment/total (rear_yard 12025/18500=0.65; placed 13300/19000=0.70 — read directly from the fixtures).
 - Stays open: the real-report 60% figure is emitted upstream by the engine (M5-T164/M5-T177), outside this data-driven kernel; it does not contradict the settled placement-building-b.json 60% reading because the fixtures are synthetic.

ROW D-094-R092 — PASS
 - Owner source: estimate and drawing use compatible area measures; zoning floor area not automatically treated as physical floorplate.
 - The drawing carries the block's measure and the exact conversion statement disclosing plate = zoning floor area per storey with no conversion worked; a garbled block (wrong label/measure/conversion) returns Unavailable (test_s6, test_s8), so ZFA is never silently taken as floorplate.
 - test_s6 asserts "zoning floor area" is absent from the measure label; both fixtures carry measure "residential_floor_area".
 - Stays open: the live estimate↔drawing measure compatibility across the engine/report is M5-T164/M5-T177/M5-T182's share; here it is a defensive refusal only.

ROW D-094-R093 — PASS
 - Owner source: no rooms, unit walls, apartment counts, or invented stair/elevator locations.
 - The rendered group contains only the expected six texts and exactly one number (the percentage), and the fitted state has exactly one line inside the footprint (the single proportional division): test_s5_only_the_expected_texts_and_one_number and test_s5_fitted_has_exactly_one_line_inside_the_footprint; both snapshots confirm (one area_division path, no other interior line).
 - The two zones share one fill and differ only by hatch; no count, room or core/stair/elevator mark is drawn.
 - Nothing stays open in this kernel's share.

ROW D-094-R094 — PASS
 - Owner source: zones inside the footprint only when fitted to the site; until then a proportional bar beside the building diagram.
 - Unfitted fixture (fitted=false, placement withheld, no outline) → a proportional bar with no zone/division/footprint; fitted fixture (fitted=true, status placed, 82×82 outline) → two zones inside outline[0] with one division and no bar (test_s1, both snapshots).
 - Fitted-without-outline (None/withheld) returns Unavailable reason_kind "not_placed" — never a bar mislabelled fitted (test_s1_fitted_without_outline_is_unavailable_never_a_bar).
 - Stays open: the bar-beside-the-actual-building-diagram pairing is composed on the scenario sheet (M5-T173 Part B); the kernel emits the bar alone, as scoped.

ROW D-094-R095 — PASS (caption share)
 - Owner source: keep the explanation to one short caption; put methodology in the appendix.
 - The drawing emits exactly one caption and carries no methodology prose (test_s5 pins the full text set; only the one caption plus labels/measure/conversion/percentage appear).
 - Stays open: "methodology goes in the appendix" is report-wiring and belongs to M5-T173 Part B; not drawn by this kernel.

ROW D-094-R098 — PASS (this task's share)
 - Owner source (harness): verify the rendered result for readability and consistency before marking complete.
 - This kernel's two SVGs were independently checked: every <text> font-size is 9.50 pt (≥8.5), zones are told apart by two distinct hatch patterns at the same fill #EEF4F7 (test_s7, both snapshots); the G3 visual-quality-reviewer rasterised both and returned PASS with only placement-stage advisories.
 - I reproduced the measurable facts from the SVG text; I did not rasterise pixels myself (see section 6).
 - Stays open: readability/consistency of the illustration once placed on the report page and website (and under any down-scaling below ~0.89×) is verified by M5-T173 Part B / M5-T174 / M0-T195 — three advisories are recorded for them.

(3) BINDING B1–B5
 - B1 PASS: contract commit 6f80bd76 appended "M5-T183" to applicability.task_ids of all 11 rows; the requirements.json diff shows only the updated_at timestamp and the 11 appends — no row text, classification or binding changed.
 - B2 PASS: I computed directive_registry.sha256_text_artifact(requirements.json) = ee63ca8f516de341209eee44eabb7d99c4143fc3d86ab65050b9206a5d39f7b7, which equals manifest.requirements_content_digest_sha256 at the frozen head.
 - B3 PASS: verification.json carries exactly one M5-T183 row with the 11 applicable_requirement_ids (R024, R087–R095, R098), producer backend-engineer, verifier "" (empty), schema directive_verification/v2, and all 11 requirement entries state=pending with empty evidence — the provisional row awaiting this verdict.
 - B4 PASS: reg.evaluate_task_refs(packet) returns ok:true with applicable_ids == cited_ids == the 11 ids, and missing_ids/invalid_refs/unresolved all empty.
 - B5 PASS: no other active-directive requirement is applicable-but-uncited (missing_ids empty); tools/validate_directive_compliance.py --check exits 0; gates G0 (orchestrator, head 6f80bd76), G1 (data-contract-verifier), G2 (orchestrator), G3 (code-reviewer), G4 (qa-engineer), G5 (security-reviewer) all record PASS, with G1–G5 all at one content identity 48d6587b; the four product blobs are byte-identical between 48d6587b, round-2 bed48258 and the frozen head 3170556f (F1–F3 closed in round 2 and reproduced by test_f1/f2/f3); CI run 38703438698 at 48d6587b is completed/success, 21/21 jobs.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review while the following blob-level predicate holds: the five allowed-path files keep these exact blob ids — area_allocation.py 1c7586057afe78e45f753765774a20bc94586039; test_area_allocation_drawing.py e0fd5d6cc5e64f5a0f6b06458caa7d4901074dcf; snapshot synthetic_placed_building_contract_1_5_0.area_allocation.svg 09c444d7ed336663d3106188bd14c2ecda3a6ec9; snapshot synthetic_rear_yard_constraints_contract_1_5_0.area_allocation.svg 4cd31fddd2a35174dd0017b4e16d4188dede80b0; project-control/reports/M5-T183-producer-report.md e58737f91cc20dede059271d0b9be18ee5744fed — AND the 11 rows' text plus their M5-T183 applicability binding are unchanged.
 - BROAD DISJOINT-PEER TOLERANCE: later commits may touch any other file (other wave-26 tasks' files under services/, apps/, packages/, docs/, .claude/; other packets, gates, reports, directive bindings of other tasks; new rows appended to D-094; ledger state), plus this task's own acceptance records, and may merge the main line, provided none of the predicate's files/blobs or the 11 rows' text/binding change. The HEAD advance I observed (3170556f → 087670a9, M3-T010 control-plane, touching none of this task's files) is exactly such a tolerated disjoint peer.

(5) REQUIRED CORRECTIONS
 - None. No VIOLATED or UNVERIFIABLE row. All open items are out-of-scope successor work (M5-T173 Part B / M5-T174 / M0-T195) and all recorded findings are ADVISORY (G1 one advisory; G3 code three advisories; G3 visual three advisories; G5 one comment-wording advisory after F1–F3 were closed) — none blocks this task's share.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - Pixel-level visual legibility: I did not start the Chromium rasteriser or any server/port; I verified the measurable SVG facts (9.5 pt font-size, two distinct hatch transforms, shared fill, geometry, one division line) and relied on the G3 visual-quality-reviewer's PASS for the rendered look (its remit).
 - The full services/api pytest suite and tools/test_directive_compliance.py were forbidden by my brief; I ran the focused kernel test (37/37 passed), ruff (clean), modularity_check --check (exit 0, area_allocation.py no finding), the directive validator (exit 0), and confirmed CI run 38703438698 green via read-only gh — but I did not re-run the full regression myself (it is CI's job; green at 48d6587b).
 - The placed-on-report and website behavior (the remainder of R088/R094/R095/R098, and R096/R097/R099 which are correctly not bound to this task): out of this kernel's scope and owned by M5-T173 Part B / M5-T174 / M0-T195 / design-contract+questionnaire tasks; I confirmed only that this task's share is met and said what stays open per row.
 - The owner-vs-token trailing-period question on R089/R090: I confirmed the drawing matches the committed token byte-for-byte; whether the canonical token should carry the owner's sentence-final period is M5-T165's decision (presentation_tokens.py is outside this task's writable scope), so I could not resolve it from this task's files alone and do not treat it as a defect of this kernel.
END-OF-REPORT
```
