# M5-T170 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `b7f37c567450a4aeb5326d1045752f2f2341ca50` (branch `task/wave26-envelope-constraints`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R017, R043, R061, R082.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None that block any of the four rows. (Carried, non-blocking, outside the four rows: G1 advisory A1 — the NB-01/NB-05 dependency_assessment prose names a parenthetical revision one below the current field, text-only, carried; and DB-265 item 3 — a double street-window fetch when the live spatial provider is switched on, off by default, its file outside the packet, carried to a later task.)
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-15T09:37:44Z, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T170 (directive D-094, 4 rows)
VERDICT: PASS
I am an AI agent (directive-compliance-verifier). This is an automated read-only verification, not a human or professional legal review; the legal readings here are labelled unreviewed drafts (ADR-007).

(1) HEAD VERIFIED
 - I read the frozen head b7f37c567450a4aeb5326d1045752f2f2341ca50 on task/wave26-envelope-constraints (base main 2bcdb05a) via git plumbing in /root/project/w-wave20.
 - git diff a963266c..b7f37c56 touches ONLY project-control files (M5-T170 gates/reports/state/task), so every production/evidence file is byte-identical to the submit head a963266c.
 - CI run 38711384646 is at headSha a963266c, completed, conclusion success, 21/21 jobs success (no non-success job) — so CI green covers the frozen head's production content.
 - validate_directive_compliance.py --check exited 0 (direct exit code; git log -1 confirmed no concurrent commit, so not a transient c14).

(2) ROWS

ROW D-094-R017 — PASS
 - Source anchor source-001.md ("Show applicable yard/setback areas only when their geometry and basis are established.") is honored: envelope_constraints.py `_constraint_lines` emits street_wall_band/setback_line as state not_established with NO "geometry" key, and marks street_wall_band "established" only when an operative-street-line geometry is supplied.
 - Benchmark fixture recorded_215_16_northern_journey.json carries street_wall_band and setback_line both state "not_established", basis "derived", zr_sections set, and no geometry key — no area drawn without an established basis.
 - I reproduced the two pinning tests green at the frozen head: test_constraint_lines_not_established_without_an_operative_street_line and test_street_wall_band_established_when_a_geometry_is_supplied (full test_envelope_constraints.py = 40 passed).
 - Nothing of the prohibition stays open; drawing the band once an operative street line is recorded is future capability but the prohibition is fully kept now.

ROW D-094-R043 — PASS (this task's share)
 - Source anchor source-001.md item 5 asks for one meaningful spatial example (footprint placed, relevant constraints, section/massing, reconciled schedule) with an explicit incomplete state until those exist; this task delivers the "relevant constraints" share.
 - Street wall, setback-above-base and side yard are now engine-checked with states/conditions and shown on page 3 (with "see item" links), page 6 and page 8; the real print print-9ac5ad4a shows pages 3/6/8 agree (only page-3 side-yard "(see item 9)" changed vs round 1).
 - The scenario keeps an explicit incomplete state: page 6 "What was not checked / Pending verification" lists "Where the plan sits on the lot", "Parking, loading and bicycle", and "Floor schedule" — nothing is falsely claimed complete.
 - STAYS OPEN: the dimensioned footprint placed on the site, the section/massing, and the reconciled floor schedule are NOT delivered here; they are owed to M5-T172 part B and M5-T173 part B (per the evidence map).

ROW D-094-R061 — PASS (this task's share)
 - Source anchor source-001.md ("legal source facts are not marked unknown solely because a software feature is unfinished; genuinely unresolved site facts stay unresolved") is honored: envelope_constraints.py has only "applies"/"not_applicable" row builders and no "not_known" path for the three checks; the law is captured in three DRAFT rule files and NB-06, not left unknown.
 - Genuinely unresolved site facts stay NAMED conditions or withheld distances, never defaulted to narrow (D-051): unknown/unresolved width shows no distance, overlay-not-read and building-type-not-stated are named conditions.
 - I reproduced green: test_no_envelope_row_is_ever_not_known, test_setback_trigger_table_strict_above_the_maximum_base_height (strict >45.00: 30/44.99/45.00 not triggered, 45.01/50 triggered), and test_street_wall_no_overlay_unknown_width_shows_no_distance_never_narrow; research_record_check.py --check exited 0 (6 records, code_current=True, none claims Verified).
 - Nothing of the harness stays open for this task's three envelope checks.

ROW D-094-R082 — PASS (this task's share)
 - Source anchor source-002-amendment.md item 2 ("Finish one meaningful scenario: a dimensioned footprint on the site, a section, and a reconciled floor schedule. Clearly identify every constraint still untested."); this task delivers the "clearly identify every constraint still untested" share plus the three now-checked constraints.
 - Real print print-9ac5ad4a: page 6's "What was not checked" no longer lists the street wall (now checked, Conditional) and keeps plan placement, parking and floor schedule; page 8 open items 7/8/9 show the applied conditional setback/street-wall/side-yard readings and page 3 agrees.
 - The DB-266 silent-drop bug (page 3 dropping setback/street-wall rows while page 8 kept them) is fixed and tested: I reproduced test_constraint_rows.py green (S18 fallback), so no constraint is silently omitted.
 - STAYS OPEN: the dimensioned footprint, the section, and the reconciled floor schedule are NOT delivered here; they are owed to M5-T172 part B and M5-T173 part B.

(3) BINDING B1–B5
 - B1 PASS: contract commit 2e095e50 appended only "M5-T170" to the four rows' applicability.task_ids (after M5-T167 for R017/R061, after M5-T177 for R043/R082); no row text changed, and each row's quoted text matches its source anchor verbatim.
 - B2 PASS: directive_registry.sha256_text_artifact(requirements.json) = ee63ca8f516de341209eee44eabb7d99c4143fc3d86ab65050b9206a5d39f7b7 equals manifest.requirements_content_digest_sha256; the validator's exit 0 independently confirms digests and source anchors.
 - B3 PASS: verification.json has exactly one M5-T170 entry, applicable_requirement_ids = [R017,R043,R061,R082], producer "backend-engineer", verifier "" (empty), all four requirement states "pending", reviewed_sha null.
 - B4 PASS: reg.evaluate_task_refs(packet) returned ok=True, applicable_ids == cited_ids == the four rows, missing_ids/invalid_refs/unresolved all empty.
 - B5 PASS: the same evaluate_task_refs run (which scans active directives) reports no additional applicable, uncited requirement for M5-T170 (missing_ids empty).
 - GATES PASS: G0 (orchestrator, re-recorded at scope-correction-2 head), G1 (data-contract-verifier), G2 (orchestrator), G3 (code-reviewer), G4 (qa-engineer), G5 (security-reviewer) all recorded PASS; G1–G5 are at one content identity a963266c, the submit head whose CI run is green and whose production files are byte-identical to the frozen head. Round-1 required findings (G1 F1 provenance; G4 S17/DB-265) were applied in rounds 2/3 and re-verified by delta checks at a963266c (confirmed in M5-T170-reviews.md, and I reproduced the benchmark now carrying "DCP Digital City Map street center lines", not MapPLUTO, for the width facts).

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review provided the blob-level predicate holds: the task's material/allowed-path files that carry the verified behavior (the evidence-map files_changed set — envelope_constraints.py, three_way_document.py, result_way_engine_bridge.py, first_option_results.py, readers.py, page_site_context.py, rear_yard_checks.py, study_inputs.py, the three r6b_*.rule.json, register.json and its rendered register pages, NB-01/03/05/06, recorded_215_16_northern_journey.json, and the listed test files) keep their exact blob ids; AND requirements.json rows R017/R043/R061/R082 keep their text unchanged with M5-T170 still in each applicability.task_ids; AND manifest.requirements_content_digest_sha256 is unchanged.
 - BROAD DISJOINT-PEER TOLERANCE: later commits MAY touch any other file — other tasks' files under services/, apps/, packages/, docs/, .claude/; other tasks' packets, gates, reports and directive bindings; new rows appended to D-094 or any directive; ledger state.json; this task's own acceptance records (M5-T170 gates/reports/state/task/verification.json); and a merge of the main line that changes none of the predicate files — none of these voids this verdict.

(5) REQUIRED CORRECTIONS
 - None that block any of the four rows. (Carried, non-blocking, outside the four rows: G1 advisory A1 — the NB-01/NB-05 dependency_assessment prose names a parenthetical revision one below the current field, text-only, carried; and DB-265 item 3 — a double street-window fetch when the live spatial provider is switched on, off by default, its file outside the packet, carried to a later task.)

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I did not run the full api pytest suite, the whole web vitest suite, or the real-preview print (brief forbids the first; no server/ports allowed) — I relied on CI run 38711384646 (green, 21 jobs) plus the fact that production files are byte-identical at the frozen head, and on the recorded print artifacts print-9ac5ad4a / diff-vs-b067e9db.txt, which I treated as evidence but could not regenerate here.
 - I did not fully re-derive the NB-06 ZR law chain (35-631(b)/23-431(b), 23-432/23-433, 35-632(a), 23-335(b)/34-232) from the primary statute; I checked the engine against the captured ZR snapshots, the settled reference-case readings in docs/reference-cases/R6B/cases/, and the sealed/research returns, and against research_record_check + render_review_register (both exit 0). These readings are labelled unreviewed DRAFTs (needs_review, 0.1.0-draft, "not a Verified determination"); no human verdict is entered, consistent with ADR-007.
 - I could not exercise the "established" street-wall-band geometry path on a real recorded site because none exists yet (the benchmark supplies no operative street line); I verified that path only via the unit test that supplies a geometry.
END-OF-REPORT
```
