# M5-T192 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `95e6f299cb008d79ef9c4017258ee9532b2a81a6` (branch `task/wave29-scenario-drawings`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R017, R021, R043, R076, R208.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. All open items are legitimately downstream (M5-T173 wiring / M5-T193 sheet) and are already recorded as known limits in the evidence map and reviews; none is a defect in M5-T192's share.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-16 01:42:49 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T192 (directive D-094, 5 rows)
VERDICT: PASS

(1) HEAD VERIFIED
 - I read the frozen head 95e6f299cb008d79ef9c4017258ee9532b2a81a6 on branch task/wave29-scenario-drawings; every task artifact was read via `git -C /root/project/w-wave29 show 95e6f299:<path>`.
 - The four allowed-path source/test files carry identical blob ids at the reviewed head 8e1d5912 and at the frozen head 95e6f299 (section_legal_lines.py 15c1233b, section.py 771f6a44, __init__.py 512a73f9, test file 503493de), so the reviewed content identity is what sits on the frozen head.
 - Those blobs also equal the round-2 builder commit 0bd9d747; section.py and the test differ from round-1 2c91fe92 (the F1 fix), while the reader and facade are round-1==round-2, matching the review record.
 - The working-tree disk head had already advanced to e016a59d while I worked (expected disjoint-peer wave-29 activity); I stayed on the frozen head by reading git objects, not disk.

(2) ROWS

ROW D-094-R017 — PASS
 - The renderer draws only horizontal dashed HEIGHT-LIMIT reference lines plus schedule bands; it draws no yard, setback, or street-wall AREA at all (read section.py at 95e6f299).
 - section_legal_lines.py reads only answers.permitted_envelope and never envelope_rows; tests test_s4_envelope_rows_never_become_a_line and test_s4_envelope_rows_alone_draw_no_line confirm the 40/60 ft setback/street-wall values never become a line.
 - The three lines it does draw are established: each has status "available" and ZR 23-432 provenance (benchmark min/max_base/max_building = 30/45/55 ft), so nothing is drawn on an unestablished basis; the prohibition is respected by omission.
 - Nothing of this task's share stays open; actual yard/setback area rendering (constraints/site plan) belongs to the row's other tasks (M5-T191, M5-T175).

ROW D-094-R021 — PASS
 - The section stays a compact schematic: height <=260 pt and width <=515.9 pt (code _LEGAL_STACK_TOP 24 + _LEGAL_STACK_H 200; test_s2 asserts the caps), and it adds no footprint/placement (caption "Drawn from the floor schedule; no placement on the lot.").
 - It is the "section" output the owner wants filling the main drawing area, drawn only when results are given; legal_lines=None / no-results output is byte-identical to today (test_s1_* and the 88 report-frame tests unedited).
 - The explicit "schematic / not to scale" sheet label is NOT supplied by this renderer (report frame uses caption=False; its own caption is a no-placement note); the evidence map and G3-visual finding F3 assign that label to the scenario-sheet/wiring parts.
 - Stays open: the "schematic / not to scale" sheet label and replacement of the generic three-box stack on the live scenario sheet (M5-T193 / M5-T173).

ROW D-094-R043 — PASS
 - R043 is a four-piece spatial-example obligation (footprint, constraints, section/massing, reconciled schedule); M5-T192 supplies the SECTION piece only — a vertically to-scale floor stack carrying the document's height limits.
 - The piece is delivered and exercised at the frozen head (reader + renderer, with the focused test file), so this task's share is met.
 - The task adds nothing that completes or falsely closes the scenario; the "explicit incomplete state until those exist" is enforced by the sheet/report, not this renderer.
 - Stays open: the placed footprint (M5-T191), the reconciled schedule and the explicit incomplete-state (M5-T193), and the wiring onto the sheet (M5-T173); R043 does not complete until those land.

ROW D-094-R076 — PASS
 - R076 asks the page-5 building diagram to show more than stacked floors; this task's share adds the legal height context (30/45/55 ft) beside the storey bands, so the diagram is more than a bare three-box stack.
 - The core of R076 — a footprint, its placement on the lot, and labelled circulation/apartment zones — is NOT drawn here (no footprint/placement/zone geometry in section.py), consistent with the evidence map assigning those to M5-T191/M5-T193/M5-T173.
 - No detailed apartment layout is produced (only schedule bands and reference lines are drawn), so the owner's "no detailed apartment layouts" bound is respected.
 - Stays open: footprint + placement (M5-T191), circulation/apartment zones labelled by status (M5-T193), and their arrival on the page (M5-T173) — the bulk of R076.

ROW D-094-R208 — PASS
 - This is the row M5-T192 most directly satisfies: a compact floor-stack section showing the relevant levels (storey tops 10/20/30 ft from the schedule) and heights (30/45/55 ft from answers.permitted_envelope).
 - Every drawn number is the document's own value: test_s2_every_line_number_is_the_document_value_at_its_source resolves each label's RFC-6901 pointer to the printed number, and 30/45/55 match the settled reading real-lot.json row L3 and ZR 23-432 (I read both at the frozen head) — never a program run; the qualifying 65 ft key is excluded by STANDARD_HEIGHT_KEYS.
 - The drawing is compact (<=260 pt tall), satisfying the "compact section" wording.
 - Stays open: R208's "on the candidate print" harness — the section is renderer-level only and not yet placed on the live report (wiring M5-T173 not yet contracted); the overall-scenario conditional flag (fixture building_alternatives[0] way=conditional; standard heights carry no per-value way) must reach the printed sheet (a recorded known-limit); R208 also depends on R082.

(3) BINDING B1–B5
 - B1 PASS: contract commit 1c84ec40 appended exactly "M5-T192" to the task_ids of all five rows and changed only updated_at; the reproduced requirements.json diff shows no requirement text/classification/binding change.
 - B2 PASS: LF-normalized sha256 of the frozen requirements.json = 9ed95b1792e22ed1ee627872e56f184145662f86624c434df557d093de140ad5 = manifest.requirements_content_digest_sha256 (I recomputed it with the registry's normalize-then-sha256).
 - B3 PASS: verification.json holds exactly one M5-T192 task_verifications row; applicable_requirement_ids = the five; every requirement state "pending"; verifier "" (empty); reviewed_sha null; producer backend-engineer.
 - B4 PASS: reg.evaluate_task_refs(frozen packet) → ok=True, applicable_ids == cited_ids == the five, missing_ids [], invalid_refs [], unresolved []; an independent frozen-head scan of all 315 D-094 rows derived the same five and no unresolved applicability.
 - B5 PASS: evaluate_task_refs ran over ALL active directives (D-001..D-094) and returned no additional applicable id — nothing else across active directives applies to M5-T192 uncited.
 - Gates: G0 PASS (orchestrator, contract head 1c84ec40); G1 (data-contract-verifier), G2 (orchestrator), G3 (visual-quality-reviewer), G4 (code-reviewer) all PASS at one content identity (reviewed_sha 8e1d5912, content_manifest_sha256 fa60ef30928447f673e41006f5c637c40e109a462cff9deb67cde8bfee680984). reviews.md shows the G3 record carrying the visual round-1 REQUIRED-F1 and the round-2 delta PASS, and the G4 record carrying the code-reviewer round-2 code/test delta plus the qa-engineer round-1 PASS. CI run 38834850070 at 8e1d5912 = 21/21 jobs success. validate_directive_compliance.py --check exited 0 (at the live head, corroborating registry integrity).

(4) CARRY-FORWARD CONDITION
 - Stamp this PASS at a later accept head WITHOUT a new review iff (blob predicate) at that head the four allowed-path files keep the exact blob ids section_legal_lines.py 15c1233b, section.py 771f6a44, __init__.py 512a73f9, test_section_legal_lines.py 503493de and the producer report stays within the task's allowed paths, AND the five rows' text plus their M5-T192 task_ids binding are unchanged (the requirements digest may move only through a resync that leaves those five rows' text + binding intact).
 - BROAD DISJOINT-PEER TOLERANCE: later commits may touch any other file (other wave-29 tasks' sources under services/apps/packages/docs/.claude, their packets/gates/reports; OTHER tasks appended to these same rows' applicability, e.g. the wiring part M5-T173 at its contract with the digest resync and provisional rows that brings; new rows appended to D-094; ledger/state), plus M5-T192's own acceptance records (verification.json verifier fill, accept-time task/state edits) and a main-line merge that changes none of the predicate files.

(5) REQUIRED CORRECTIONS
 - None. All open items are legitimately downstream (M5-T173 wiring / M5-T193 sheet) and are already recorded as known limits in the evidence map and reviews; none is a defect in M5-T192's share.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The rendered pixel output / real report print: no rasterizer or server available and ports 3000/3001/8000 forbidden; I verified SVG geometry, provenance pointers and numbers from the code and tests, not a printed page. The candidate-print appearance (R208 harness) awaits the not-yet-contracted M5-T173.
 - The full api pytest and vitest/e2e and the 507/511 kit-folder counts: forbidden to run the full suite; I relied on CI run 38834850070 (21/21 success at 8e1d5912) and the source I read. I did not re-execute the focused kit tests (I preferred reading); the mutation/overlap claims are the producers'/reviewers', reproduced structurally from the code, not by my own test run.
 - The 8.0-vs-8.5 pt printed label size and the conditional-"way" labeling reaching the page: explicitly downstream (M5-T173 / M5-T193), UNKNOWN at this renderer level, recorded as known limits.
 - Live port behavior and any sibling commit landing after my read: I verified identity only at 95e6f299 (disk head had advanced to e016a59d); the carry-forward predicate in (4) governs a later stamp.
END-OF-REPORT
```
