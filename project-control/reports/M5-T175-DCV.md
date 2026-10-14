# M5-T175 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `a5c5de22ebbc42b5f67cde084f39eccd65a83563` (branch `task/wave24-report-v3`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R015, R017, R036, R037, R038, R044, R052, R053, R060, R061, R079.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. Every applicable requirement is SATISFIED for this task's share; the five bindings and all five required gates reproduce; validator, research_record_check, modularity_check and ruff all pass; 51/51 focused tests pass. - Open items (not corrections, correctly disclosed): DB-262 (the committed synthetic 1.5.0 example is not self-consistent — its line runs ~60 ft past its lot and its input_facts differ from the calculated lot areas; the report now clips the line to the lot, S14) is QUEUED to M5-T167; DB-263 (four non-blocking review advisories: label box hides the short clipped line, string-based frame growth, title-strip word boundary, test-measurement approach) is OPEN for a later small polish task. Neither is M5-T175's responsibility to close.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-14 18:51 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T175 (directive D-094, 11 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an independent read-only re-derivation from primary evidence, not a human or professional review. I produced none of the work or records; I treated the producer report, evidence map, reviews and gate records as claims to reproduce.

(1) HEAD VERIFIED
 - git -C /root/project/w-wave20 rev-parse HEAD = a5c5de22ebbc42b5f67cde084f39eccd65a83563 on branch task/wave24-report-v3; this equals the frozen head in the brief.
 - I read all task files and product source through git plumbing at a5c5de22e; base is main b4704161 (not merged to main).
 - python3 tools/validate_directive_compliance.py --check returned exit 0 (quiet on success); git log -1 confirmed the settled head before reacting.
 - The gate-reviewed head 90f11548e is an ancestor of a5c5de22e and the product files (services, docs/research, packages) are byte-identical between them (empty diff), so reviewing at the frozen head equals the reviewed identity.

(2) ROWS

ROW D-094-R015 — PASS
 - Source text matches requirements.json verbatim (source-001.md Reading table, R015 obligation): dedicated constraints diagram, subject/neighbours dominant, dimensions anchored to edges.
 - This task's share, added to the dedicated close frame (base frame is M5-T166's): constraint_overlay.py draws each established line on the subject lot with its own label, and close_frame_dimensions.py draw_other_basis_dimensions draws the input_facts' other-basis lot dimensions beside the map-outline ones, one label per basis, nothing merged.
 - Reproduced: tests/drawings test_s5_other_basis_dimensions_draw_beside_the_outline and test_s5_each_input_fact_names_its_own_basis_nothing_merged pass (51/51 in the three task files).
 - Open: the benchmark's close frame does not change yet (its results carry no 1.5.0 constraint lines until M5-T167 emits them); the "subject/neighbours dominant" composition itself is M5-T166's prior share.

ROW D-094-R017 — PASS
 - Source matches verbatim (R017 prohibition): yard/setback areas drawn only when geometry and legal basis are established.
 - constraint_overlay.draw_constraint_overlay skips any item whose state != "established" (ESTABLISHED constant) and any item with no geometry; not_established/not_known carry and draw nothing and are omitted from the legend.
 - Reproduced: test_s4_only_established_lines_are_drawn and test_s4_a_not_established_line_draws_nothing pass; an established line is additionally clipped to the lot outline (test_s14_*).
 - Nothing stays open: the draw-only-when-established gate is fully implemented and tested in this task (the engine's act of establishing a line is M5-T167's, but the prohibition is enforced here regardless of what the document carries).

ROW D-094-R036 — PASS (this task's share)
 - Source matches verbatim (R036 obligation): evaluate 23-344(b) and (c)(3) against actual zoning-lot/boundary evidence; update diagram and conclusion together.
 - This task's share: constraint_text.rear_yard_checks/rear_yard_combined read the engine's state/way/text/conditions/zr_sections, and both page 3 (page_site_context) and page 1 (page_decision_summary) read the one combined row, so diagram and conclusion move together.
 - Reproduced: test_s2_conditional_rear_yard_shows_combined_text_labelled_conditional, test_s12_*, test_s16_* pass.
 - Open: the actual engine evaluation of 23-344(b)/(c)(3) against the lot and the appendix open item are M5-T167's (the report here reads whatever the engine emits).

ROW D-094-R037 — PASS
 - Source matches verbatim (R037 prohibition): no unconditional zero rear yard inferred from GIS; corner-radius test not the only applicable exception.
 - constraint_text.REAR_YARD_OPEN_CHECK states no conclusion and names both ZR 23-344(b) and 23-344(c)(3) as "not yet applied"; the earlier "not known beyond the corner area" wording is removed; the 1.5.0 path prints the combined row labelled by its way (Conditional), never an unconditional "no rear yard", and carries no measurement number.
 - Reproduced: test_s2_* and test_s16_not_known_rear_yard_check_prints_no_number pass; page_decision_summary rear-yard branch and page_site_context rear-yard row read the combined row.
 - Nothing stays open for the report wording: the prohibition is met in both the 1.5.0 and the 1.4.0 fall-back paths.

ROW D-094-R038 — PASS (this task's share)
 - Source matches verbatim (R038 obligation): find why older statements persist and fix the data path, not just the wording.
 - Data path fixed: the hard-coded page-3 state dict ({"rear_yard": "Not known", "setback": "Not worked out yet"}.get(..., "Not shown")) is removed from page_site_context.py and replaced by constraint_text reads; has_results_rows routes a 1.5.0 document to the engine's own rows; page_location forwards the document's constraint_lines/input_facts into the live report.
 - Reproduced: the removal is visible in git diff 654ea3fad..a5c5de22e; test_fallback_state_strings_live_in_constraint_text, test_s1_*, test_s7_*, test_s12_* pass (1.4.0 byte-identical fall-back preserved).
 - Open: regenerating the benchmark from the corrected engine output is M5-T167's (the engine must emit 1.5.0 blocks for the real lot).

ROW D-094-R044 — PASS
 - Source matches verbatim (R044 prohibition): never invent geometry to fill a layout; geometry is calculated/source-based.
 - Lines are drawn only from the document's established geometry via a pure translation (overlay_offset = subject outline minimum, never a reprojection) and clipped to the lot polygon; _clip_line_to_polygon uses shapely intersection so clipped ends rest on the outline and interior vertices are preserved; a line wholly outside draws nothing; DrawnConstraint.source_points keep the document's own vertices.
 - Reproduced: test_s5_drawn_endpoints_lie_on_the_document_vertices, test_offset_places_results_geometry_on_the_map_lot, test_s14_a_line_wholly_outside_the_lot_draws_nothing pass.
 - Nothing stays open: no geometry is invented; all drawn geometry traces to the document.

ROW D-094-R052 — PASS (this task's share)
 - Source matches verbatim (R052 obligation): every map has a distinct job; a diagram that only repeats "three floors" does not displace a useful site drawing.
 - This task's share keeps the constraints close frame's single job: it adds only the established constraint lines plus other-basis dimensions; the legend lists only what is drawn and expand_frame_for_overlay grows the frame so no legend row is clipped (S13); an overlay failure keeps the map with a short note rather than dropping it (drawings_embed._OVERLAY_DROPPED_NOTE, S15).
 - Reproduced: test_s13_overlay_legend_fits_and_the_plain_frame_is_unchanged, test_s15_overlay_failure_keeps_the_map_with_a_note, test_s15_report_keeps_the_site_map_when_overlay_geometry_is_malformed pass; a document without 1.5.0 blocks is byte-identical (S1 tests).
 - Open: the report-wide map-job rationalisation (page 2/3 map selection and the three-box scenario diagram) is other tasks' (M0-T193, M5-T166); this task touched neither.

ROW D-094-R053 — PASS (this task's share)
 - Source matches verbatim (R053 obligation): source-based geometry, useful line weights, anchored dimensions, readable labels, north arrow, scale; illustrative geometry marked distinctly.
 - kit/styles.py adds three distinct constraint styles (rear_yard_100ft_line dashed line; corner_area and street_wall_band each a unique black-and-white hatch) beside the existing setback_line, additive only so existing outputs stay byte-identical; each drawn label carries name+state+ZR section at >= 8.5 pt, and other-basis dimensions name their own basis.
 - Reproduced: test_style_table.py (test_constraint_kinds_have_their_own_legend_entries, test_black_and_white_every_area_kind_has_a_unique_hatch, test_uses_match_the_results_contract_vocabulary) and test_s6_* pass.
 - Open: north arrow, scale and the base street/lot labels are the base close frame's (prior tasks); this task did not remove them.

ROW D-094-R060 — PASS (this task's share)
 - Source matches verbatim (R060 harness): open PDF evidence links and check destinations; internal references like "item 3" get a precise page/anchor destination.
 - This task's share: the former plain "see item N" span is now <a href="#issue-<n>">see item N</a>, and the page-3 rear-yard row links its numbered open item; I confirmed the target anchors exist — page_assumptions.py emits id="issue-{item['number']}" (line 65, a peer M5-T179 file, pre-existing behaviour).
 - Reproduced: test_s9_every_issue_href_resolves_to_an_anchor and test_s9_page_three_rear_yard_links_its_numbered_open_item pass.
 - Open: the full click-through audit of the exported PDF's law links across the report is a review harness step (the evidence map cites the visual reviewer's renders); I verified the internal anchor resolution deterministically, not by rendering a PDF.

ROW D-094-R061 — PASS (this task's share)
 - Source matches verbatim (R061 harness): legal source facts are not marked unknown solely because a software feature is unfinished; genuinely unresolved facts stay unresolved.
 - A 1.5.0 row prints its own state and no number; the 1.4.0 fall-back REAR_YARD_OPEN_CHECK says the checks "have not been applied to this lot" (software work owed, M5-T167), not that the law is unknown; _envelope_label maps not_known to "Pending verification", not an absent legal fact.
 - Reproduced: test_s3_not_known_envelope_row_shows_text_no_number and test_s16_not_known_rear_yard_check_prints_no_number pass.
 - Open: the engine actually resolving the checks is M5-T167's; the genuinely unresolved site facts stay unresolved, which is correct per this row.

ROW D-094-R079 — PASS (this task's share)
 - Source matches verbatim (source-002-amendment.md, R079 obligation): the rear-yard analysis needs an explicit 23-344(b) applicability check beside the 100-ft point test before complete; the exemption is not presented as established.
 - Page 1 (page_decision_summary) and page 3 (page_site_context) show the engine's combined 23-344(b) reading when the document carries it, labelled Conditional and linked to ZR 23-344; the exemption is never shown as established (way=conditional, no number); page 1 strips a leading title so it does not repeat "Rear yard Rear yard:".
 - Reproduced: test_s12_page_one_uncertainty_reads_the_1_5_0_conditional_rear_yard and test_s16_page_one_rear_yard_uncertainty_does_not_repeat_its_title pass.
 - Open: the explicit engine applicability check of 23-344(b) itself is M5-T167's; until then the report names it as not-yet-checked (owed), which satisfies this row's "not presented as established".

(3) BINDING B1–B5
 - B1 PASS: contract commit 231dcf948 ("M5-T175 contracted") appended "M5-T175" to exactly 11 applicability.task_ids arrays (11 "+ \"M5-T175\"" lines, plus the top-level updated_at); no requirement text/classification/source_ref changed in that commit, and git diff 231dcf948..a5c5de22e shows later commits only added new rows (R125+) and other tasks' ids — the 11 rows' text is unchanged.
 - B2 PASS: directive_registry.sha256_text_artifact(requirements.json) = ac5261694f186ca7999d8d373ff9eebb2f4ef702e962e5f20ebc7892111a29d3, equal to the manifest's requirements_content_digest_sha256.
 - B3 PASS: verification.json has one M5-T175 task_verifications row with producer backgroundengineer, verifier "" (empty), reviewed_sha null, and 11 requirement rows all state="pending", evidence empty.
 - B4 PASS: DirectiveRegistry.evaluate_task_refs on the packet returns ok=True; applicable_ids == cited_ids == the 11 rows; missing_ids [], invalid_refs [], unresolved [].
 - B5 PASS: derive_applicable scans all active directives; the only applicable rows are these 11 D-094 rows and all are cited (missing_ids empty) — nothing else applies uncited. Gates: G0 (orchestrator, administrative) PASS at reviewed_sha 63bb2720; G1 (data-contract-verifier), G2 (orchestrator self_check), G3 (visual-quality-reviewer with code-reviewer in history), G4 (qa-engineer) all PASS at reviewed_sha 90f11548 with one identical content_manifest_sha256 42cc7100eb0259a0162226779caa5375b56f8555aa05b0cc0996327447672441 — G1–G4 at one content identity. Only G0–G4 gate files exist (no accept/G5/G6/G7); the task is awaiting_gate, not accepted; nothing merged/deployed/dispatched.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review while the blob-level predicate holds: the packet's allowed-path files keep these blob ids at the stamping head — constraint_text.py 753ffd1bca67, page_site_context.py 3036c6a78b48, close_frame_dimensions.py 80f91cbd79de, constraint_overlay.py 32cdead43df7, site_context_plan.py c2da95950133, maps/__init__.py 91bf1f7dde68, drawings_embed.py 2ba4cd4ccbf9, page_location.py 856104cf5908, page_decision_summary.py 18fac37d6958, kit/styles.py acb0314de66e, test_constraint_rows.py 8a722dbc7000, test_constraint_overlay.py 6097e1e37cdf, test_style_table.py 33e16839bcfc, NB-04 990d0af64c4f — AND the 11 rows' text and their M5-T175 applicability binding stay unchanged.
 - BROAD DISJOINT-PEER TOLERANCE: later commits may touch any other file (other wave tasks under services/, apps/, packages/, docs/, .claude/, their packets/gates/reports, other tasks' directive bindings, new rows appended to D-094, ledger state), plus this task's own acceptance records (verification.json M5-T175 row, gate records, state.json), plus a merge of the main line that changes none of the predicate files, without voiding this verdict.

(5) REQUIRED CORRECTIONS
 - None. Every applicable requirement is SATISFIED for this task's share; the five bindings and all five required gates reproduce; validator, research_record_check, modularity_check and ruff all pass; 51/51 focused tests pass.
 - Open items (not corrections, correctly disclosed): DB-262 (the committed synthetic 1.5.0 example is not self-consistent — its line runs ~60 ft past its lot and its input_facts differ from the calculated lot areas; the report now clips the line to the lot, S14) is QUEUED to M5-T167; DB-263 (four non-blocking review advisories: label box hides the short clipped line, string-based frame growth, title-strip word boundary, test-measurement approach) is OPEN for a later small polish task. Neither is M5-T175's responsibility to close.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I did not render the PDF or any SVG to pixels and did not click exported PDF links (ports 3000/3001/8000 forbidden; no browser). R060's "open the PDF links and check destinations" and the visual qualities (8.5 pt legibility, no collision, legend fit, hatch distinguishability) I verified only through the deterministic tests (S6/S9/S13) and the code; the visual-quality-reviewer's rendered-image PASS is a claim I reproduced only at the deterministic-test level.
 - I did not run tools/test_directive_compliance.py or the full api pytest suite (both forbidden by the brief); I relied on validate_directive_compliance.py --check (exit 0), the three task test files (51 passed), research_record_check.py --check (exit 0), modularity_check.py --check (0 failures), ruff (clean), and CI run 38615796574 as claimed in the evidence map (I did not re-run CI).
 - The engine's actual ZR 23-344(b)/(c)(3) evaluation and the benchmark regeneration are M5-T167's and outside this task; I verified only that the report reads whatever 1.5.0 blocks the document carries, not that a real lot's blocks are correct.
 - The docs/reference-cases/R6B settled readings do not bear on this task's share (it reads engine output rather than deriving zoning figures); I did not re-derive them, per the brief.
END-OF-REPORT
```
