# M5-T191 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `95e6f299cb008d79ef9c4017258ee9532b2a81a6` (branch `task/wave29-scenario-drawings`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R017, R043, R044, R053, R082, R197, R225, R226, R235.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. No row FAILs for this task's share; all bindings and gate records are in order. - Carry into W (M5-T173), advisory only, not blocking this acceptance: (a) page 4 and page 5 must read one drawn-content manifest so "footprint shown iff placed and drawn" and "'No building placed' only when none is drawn" hold end-to-end, including the placed-but-not-drawn edge (R197); (b) the page-4 caption must state both clearances (33.34 tax-map / 35.31 GIS) without mixing, and the kit fallback caption must not read the GIS footprint as the printed tax map (DB-269 residual) (R225/R235). qa-engineer ADVISORY 1 (the over_1000_vertices test case is actually rejected by the zero-area check, so the >1000 count bound has no distinct regression test) is a coverage gap only — the production bound is present and correct and no directive row depends on it.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-16 01:43:09 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T191 (directive D-094, 9 rows)
VERDICT: PASS

(1) HEAD VERIFIED
 - I read the frozen head 95e6f299cb008d79ef9c4017258ee9532b2a81a6 on task/wave29-scenario-drawings in /root/project/w-wave29 via git plumbing; base main is 065e3fb5.
 - The 8 allowed-path files are blob-identical across the material cherry-pick 9e5a2fe9, the submit head 8e1d5912, and the frozen head 95e6f299 (git rev-parse per file, all EQUAL).
 - Peer commits landed while I worked (HEAD advanced 95e6f299 -> e016a59d -> c4422294, the M5-T173 "W" contract/claim); I pinned every read to 95e6f299 and re-checked the predicate at the advanced head.
 - M5-T191 status is awaiting_gate (not accepted); its verification row is verifier="" with all 9 requirements pending; the branch is not merged to main — no prohibited accept/merge/deploy has occurred.

(2) ROWS
ROW D-094-R017 — PASS
 - Owner words (source-001.md L96, matrix L222): "Show applicable yard/setback areas only when their geometry and basis are established." This task's share is the footprint renderer.
 - draw_placed_footprint (placed_footprint.py) and kit _report_footprint draw ONLY the illustrative ring fill plus two edge dimensions; I read no yard/setback/constraint area derived from the footprint.
 - Yard/setback drawing (_yards/_setbacks in kit, the constraint overlay in maps) is untouched and governed elsewhere; G1/G3 reviews confirm no legal area is drawn from the footprint.
 - Stays open: yard/setback geometry under this row is owned by M5-T175/M5-T188/M5-T192, not this part.

ROW D-094-R043 — PASS
 - Owner words (source-001.md L137, matrix L248): finish one meaningful spatial example = footprint placed on the site + relevant constraints + section/massing + reconciled schedule; keep explicit incomplete state until those exist.
 - This part delivers one of the four pieces: the placed footprint on the page-4 close frame and the kit report frame (renderer level, opt-in).
 - The drawn ring is the document's floor_plates entry-0 outline-0, translated onto the map lot by overlay_offset only — a real placed footprint, not a stand-in.
 - Stays open: the other three pieces (constraints M5-T175, section M5-T192, reconciled schedule M5-T193) and wiring into the live report + the explicit-incomplete-state are the scenario/W (M5-T173) work.

ROW D-094-R044 — PASS
 - Owner words (source-001.md L137, matrix L249): "Do not invent geometry to fill a layout." This part draws only source-based geometry.
 - FOOTPRINT_SOURCE = "/geometry/floor_plates/entries/0/outline/0"; I computed the benchmark ring edges = [103.88, 64.66, 103.88, 64.66] ft, equal to reference case placement-building-b.json row gis-conflict-check (GIS frontage 103.88, GIS plan depth 64.66).
 - The tax-map rectangle (100.76 x 66.66, row footprint-tax-map) is never read or drawn; a degenerate or unplaceable ring draws NOTHING (no invented fallback; S4/S5, plan-then-commit returns None).
 - Stays open: nothing — this part's geometry is fully source-based and traceable.

ROW D-094-R053 — PASS
 - Owner words (source-001.md L150, matrix L258): real source-based geometry, anchored dimensions, illustrative geometry marked distinctly.
 - The footprint carries two anchored figure-only edge dimensions (103.88 ft back/width, 64.66 ft depth) sourced to edge:/geometry/floor_plates/entries/0/outline/0#i, each at >= 8.5 pt (DIMENSION_MIN_PT=8.5; kit dimension_pt+0.5=8.5); tests assert font-size>=8.5 and no collisions.
 - It is marked distinctly illustrative: new ShapeStyle "illustrative_footprint" (slate wash #E8EEF2, crossed-diagonal hatch, dashed #5B7083 outline, legend "Illustrative building footprint", CAD layer A-BLDG-ILLUS); the visual reviewer confirmed it reads as an illustration, not a legal line.
 - Stays open: street/lot labels, north arrow and scale are the frame's existing furniture (other tasks); verification on the printed page is W (M5-T173).

ROW D-094-R082 — PASS
 - Owner words (source-002-amendment.md L48, matrix L72): finish one meaningful scenario = a dimensioned footprint on the site, a section, a reconciled floor schedule; name every untested constraint.
 - This part draws the dimensioned footprint on the site (the renderer for the close frame and the kit report frame), with its two anchored dimensions.
 - Stays open: the section (M5-T192), the reconciled schedule (M5-T193), naming untested constraints, and wiring into the live report (M5-T173) complete the row.

ROW D-094-R197 — PASS
 - Owner words (source-028-amendment.md L93, matrix L388): page 4 wrongly said "No building placed" and showed no footprint; fix = show the illustrative footprint whenever one is placed and drawn, keep "No building placed" only when none is drawn.
 - site_context_plan.py sets not_placed_legend = (placed_footprint is None): passing a valid footprint draws it and drops "No building placed" (test S2); passing None keeps the row byte-identically (test S1); a degenerate but non-None ring (building placed, ring undrawable) draws nothing yet still drops the row (test_s4_...shows_no_no_building_placed).
 - Reproduced via the tests and the diff; the renderer mechanism delivers the owner's fix for the real (valid-ring) case.
 - Stays open: W (M5-T173) wires this into the live page 4 and must make page 4 and page 5 read ONE drawn-content manifest so "shows the footprint whenever placed AND drawn" and "'No building placed' only when none is drawn" hold end-to-end, including the placed-but-not-drawn edge (the renderer currently keys the row on placed, not drawn — code-reviewer ADVISORY 2 / known_limit).

ROW D-094-R225 — PASS
 - Owner words (source-028-amendment.md L149, matrix L416): 33.34 ft is the tax-map basis, 35.31 ft the GIS basis; do not mix, average, or conceal; each drawing names its basis.
 - The footprint and its two dimensions are GIS/city-map basis only (103.88/64.66 = GIS plate edges); the close frame carries exactly one basis note "All dimensions: city map outline, not surveyed." (GIS_BASIS_NOTE); test S2 asserts none of 33.34/35.31/35.32/100.76/66.66 appears in the SVG, and three reviewers grepped the real SVG = 0 each.
 - No clearance figure is drawn, averaged, or concealed by this part; I confirmed the footprint adds only GIS edge lengths consistent with the already-present GIS lot dims on the maps close frame.
 - Stays open: W (M5-T173) states the two clearances (both bases) in the page-4 caption; the kit fallback's held caption "Lot outline: Approximate — tax map" sitting over GIS figures is a pre-existing residual (DB-269, forbidden-path schema const) that W's caption must reconcile — this part introduces no new figure-level basis mix.

ROW D-094-R226 — PASS
 - Owner words (source-028-amendment.md L151, matrix L417): draw legal constraint lines only where supported; an illustrative footprint does not establish a legal setback or yard.
 - The footprint's edges are drawn only in the illustrative_footprint style (hatch/dashed outline/legend/CAD layer A-BLDG-ILLUS), translated by the existing overlay_offset; I read no yard/setback/legal line produced from them, and the visual reviewer confirmed nothing reads as a legal line.
 - Mutation C (kit kind -> plate.use) reddens S3/S1/S5, proving the edges are genuinely the illustrative kind, not a use/legal colour.
 - Stays open: nothing — the illustrative marking is complete at the renderer level and carries into W's live report.

ROW D-094-R235 — PASS
 - Owner words (source-028-amendment.md L181, matrix L426): Site plan — show the proposed footprint when supported, with dimensions, source basis, and relevant constraints.
 - The site plan (close frame and kit report frame) now shows the proposed footprint with its two dimensions and a named source basis (GIS/city-map via the single basis note); delivered at renderer level, opt-in.
 - "Relevant constraints" on the same page and the printed-page delivery are not this part.
 - Stays open: relevant constraints (M5-T175/M5-T192) and putting the footprint into the live print (W, M5-T173) complete the row; the printed page 4 changes there.

(3) BINDING B1-B5
 - B1 PASS: all 9 rows have M5-T191 in applicability.task_ids at the frozen head; for every row text, classification and source_ref are byte-identical to base main 065e3fb5 (this task only appended its binding — some rows also carry sibling appends M5-T192/M5-T193, which are allowed disjoint peers).
 - B2 PASS: I recomputed the manifest digests from the frozen-head requirements.json (315 rows) — content digest 9ed95b17.. and id digest 36f3b1e3.. both equal the manifest's declared values; validate_directive_compliance.py --check returned exit 0.
 - B3 PASS: verification.json has exactly one M5-T191 task_verifications row listing these 9 ids, producer backend-engineer, verifier "", reviewed_sha null, all 9 requirement states pending.
 - B4 PASS: scanning the frozen-head requirements.json, the set of requirements binding M5-T191 == the 9 cited ids exactly (no extra applicable-uncited, no cited-not-applicable).
 - B5 PASS: scanning EVERY active directive at the frozen head, only D-094's 9 rows bind M5-T191 (nothing else applies uncited). Required gates G0,G1,G2,G3,G4 are all recorded PASS; G0 is administrative at contract head 4eadaf00; G1 (data-contract-verifier), G2 (orchestrator self_check), G3 (code-reviewer), G4 (qa-engineer) all share one content identity reviewed_sha 8e1d5912 / content_manifest 615eeac6. CI run 38834850070 at headSha 8e1d5912 is completed/success, 21/21 jobs, zero non-success (independently read via gh).

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review while the following blob-level predicate holds, under broad disjoint-peer tolerance.
 - Predicate (the 8 allowed-path files keep these exact blob ids at the stamping head):
     placed_footprint.py = f109aea8c14344e31e933a52d75ae3fa16396e59
     maps/site_context_plan.py = deae0bc85708be3638eaf32e73b99412807687f0
     maps/__init__.py = f6bdf77872b7501f179d9ce8bdbd0ea9dce0eeaf
     kit/styles.py = ea69a7565fab6986d2c2a00e23dab1320fb46037
     kit/site_plan.py = dbce271c90ee5ae0db11802d6cd724bfed312a74
     tests/drawings/maps/test_placed_footprint.py = 0a6c281df6e31c1b21729fcb9542c2715acb4b20
     tests/drawings/kit/test_site_plan_footprint.py = c0b05d04d0a66ad8fa7b4440b735e97e1c924dc5
     reports/M5-T191-producer-report.md = 3c47bd910cf263d1903cfd6daf71456e30ecdb90
   AND the 9 rows' text + classification + source_ref unchanged and M5-T191 still bound to all 9.
 - Broad disjoint-peer tolerance: later commits MAY touch any other file (other tasks' files under services/, apps/, packages/, docs/, .claude/, their packets/gates/reports; OTHER TASKS appended to the applicability of these same 9 rows — e.g. the wiring part W / M5-T173 at its contract, with the digest resync and provisional verification rows it brings; new rows appended to the directive; ledger/state), plus this task's own acceptance records (its verification.json row filled, gate/accept records), plus a merge of the main line that changes none of the 8 predicate files. The registry-wide requirements_content/id digests WILL shift when peers resync — that is expected and NOT a predicate breach; the predicate is the 8 blob ids plus the row-level text/binding, not the whole-registry digest.
 - Demonstrated live: after I froze, HEAD advanced through the real M5-T173 contract (e016a59d) and a further peer (c4422294); I re-verified all 8 blob ids stable and all 9 rows' text/classification/binding unchanged at the advanced head.

(5) REQUIRED CORRECTIONS
 - None. No row FAILs for this task's share; all bindings and gate records are in order.
 - Carry into W (M5-T173), advisory only, not blocking this acceptance: (a) page 4 and page 5 must read one drawn-content manifest so "footprint shown iff placed and drawn" and "'No building placed' only when none is drawn" hold end-to-end, including the placed-but-not-drawn edge (R197); (b) the page-4 caption must state both clearances (33.34 tax-map / 35.31 GIS) without mixing, and the kit fallback caption must not read the GIS footprint as the printed tax map (DB-269 residual) (R225/R235). qa-engineer ADVISORY 1 (the over_1000_vertices test case is actually rejected by the zero-area check, so the >1000 count bound has no distinct regression test) is a coverage gap only — the production bound is present and correct and no directive row depends on it.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I did not run the full services/api pytest or tools/test_directive_compliance.py (both forbidden by brief); I relied on CI run 38834850070 (success, 21/21 at 8e1d5912) and the recorded gate reports for suite-level and byte-identity (tests/drawings+tests/cad 1958 passed) evidence rather than re-running the heavy suite.
 - I did not re-rasterize the SVGs or re-run the focused/heavy drawing tests myself (visual and heavy-lock lanes); I read the code, the two new test files, the reference case and the benchmark fixture, and reproduced the figures (103.88/64.66) and the ring provenance directly from source.
 - I did not independently recompute the SLOC/modularity numbers (placed_footprint.py 216<300; site_context_plan.py +9 within +15; modularity_check exit 0) — that is G3/G4's lane; both reviewers reproduced them on isolated extractions.
 - overlay_offset's own correctness (M5-T175, import-only / forbidden path here) is assumed, not re-derived; test_s2 confirms each map vertex = document vertex + offset within 0.01 ft, which is this part's use of it.
END-OF-REPORT
```
