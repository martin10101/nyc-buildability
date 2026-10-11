# M5-T163 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `adc36fc7231552635c6696e037f275d600dec685` (branch `task/wave24-report-v3`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R036, R037, R061, R079.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-11 21:03 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T163 (directive D-094, 4 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an independent read-only reproduction of evidence, not a human or professional zoning review. I produced none of this work. Everything below I re-derived from primary evidence (owner source files, git objects at the frozen head, the captures' own bytes, the registry, CI), treating the producer report, evidence map, reviews and gate records as claims.

(1) HEAD VERIFIED
 - I read the frozen head adc36fc7231552635c6696e037f275d600dec685 on task/wave24-report-v3 in /root/project/w-wave20, via git plumbing (the live worktree HEAD has moved on to 71a03977, a descendant).
 - Material commits b644f292 (cherry-pick of researcher a5419463) and bebcaeef (orchestrator [ORCH-CORRECTED] G1 entry) are both ancestors of adc36fc7; contract head fc96fd9c and claim head aac892fc are ancestors; base is main b4704161.
 - The 12 allowed-path files are byte-identical between adc36fc7 and the working HEAD 71a03977, and the working tree is clean for them, so the allowed check scripts run against the worktree reflect the frozen content.

(2) ROWS (D-094, numeric order; no D-090 rows bind this task)

ROW D-094-R036 — PASS
 - Source anchor reproduced: source-001.md attached brief, "Evaluate these pathways against the actual zoning-lot and boundary evidence." / "Update the diagram and conclusion together."; requirements.json text is faithful.
 - NB-03 rev 2 (blob acfd359f) evaluates BOTH pathways against boundary evidence: 23-344(b) short-dimension-of-a-block (Northern Blvd block frontage 200.01 ft printed_tax_map / 203.13 ft gis, both < 230) and 23-344(c)(3) R6-R12 adjoining side-lot-line (neighbours' north lines classified as side lot lines, E3/E4), against zoning_lot_unconfirmed and the actual boundary evidence (E6 tax map, E7 GIS, E10 "block").
 - The record's conclusion is updated to the conditional reading; it is a labelled draft, not a DOB determination.
 - Stays open: the "update the diagram" half and the engine that computes the single short-dimension measure are M5-T167's share (gap b / DB-230); the independent worked example is M5-T176's share.

ROW D-094-R037 — PASS
 - Source anchor reproduced: source-001.md, "Do not infer an unconditional zero rear yard from GIS, and do not continue explaining the issue as though the corner-radius test were the only applicable exception."
 - No unconditional zero rear yard from GIS: lot depth is kept a three-basis conflict (100 printed_tax_map / 99.97 gis / ~101.06 derived), "no basis chosen", conclusion "conditional", research_status interpretation_awaiting_review.
 - Corner test is not the only exception: exceptions_considered records 23-344(a) as a point test that "neither replaces nor defeats the street-line test of (b)"; (a), (b) and (c)(3) are each evaluated separately.
 - Stays open: the rendered-report wording of R037 is M5-T165's share (R037 is also bound to M5-T165).

ROW D-094-R061 — PASS
 - Source anchor reproduced: source-001.md, "Confirm that legal source facts are not marked unknown solely because a software feature is unfinished."
 - Legal source facts in scope are captured as facts, not left unknown: ZR 12-10 'street' (E8), 'street setback line' (E9), 'street, wide' (E12), 'street, narrow' (E13) captured sha256-pinned with byte-identical bundled copies; I verified content_digest_sha256 == sha256(verbatim_excerpt) for all four and sync_zr_snapshots --check exit 0 (189 files byte-identical).
 - Genuine site facts stay unresolved as recorded searches with the exact missing item + next step (depth conflict; survey/approved ZD1 access_blocked; whether the tax-map ALLEY is a mapped #street#; district-boundary provision not_found), not marked unknown because software is unfinished.
 - Stays open: the export-wide review of every "unknown" on rendered report pages is a report-regeneration check; this documents-only task does not touch the export, and R061 is bound here only to M5-T163, so its research-fact share is discharged.

ROW D-094-R079 — PASS
 - Source anchor reproduced: source-002-amendment.md, "...It still omits the separate short-block-frontage exception in ZR 23-344(b). That provision needs an explicit applicability check before the rear-yard analysis is complete; I am not saying the exemption is already established."
 - NB-03 rev 2 performs an explicit 23-344(b) applicability check beside the 100-ft point test: inputs recorded with bases (front lot line on the short-dimension street line; block frontage < 230 ft; reach within 100 ft of that street line), with 23-344(a) kept as a distinct point test.
 - The exemption is not presented as established: "a labelled draft reading, not a DOB determination", applies "conditional", interpretation_awaiting_review, depth conflict unresolved.
 - Stays open: the report's rear-yard item (23-344(b) check + result state) and the rule tests covering applicable/not-applicable/unknown are M5-T164/M5-T165/M5-T167's share (R079 is also bound to M5-T164 and M5-T165).

(3) BINDING B1-B5
 - B1 PASS: contract commit fc96fd9c appended "M5-T163" to EXACTLY R036/R037/R061/R079 in requirements.json (a Python before/after diff shows those four rows gained it and no others; zero rows had their 'text' changed); the material commits b644f292 and bebcaeef did not touch requirements.json.
 - B2 PASS: directive_registry.sha256_text_artifact(requirements.json) = b31b83ce333c7d90d7784e6a811ac520a5be36ad32876dcd6e7c27c771c108ef == manifest.requirements_content_digest_sha256; validator c14 corroborates.
 - B3 PASS: D-094 verification.json has exactly one M5-T163 row; applicable_requirement_ids = [R036,R037,R061,R079]; verifier "" (empty); all four requirement states "pending".
 - B4 PASS: evaluate_task_refs(M5-T163) via load_registry → ok=true, applicable == cited == the four ids; missing/invalid/unresolved all empty.
 - B5 PASS: missing_ids empty across all active directives → nothing else applies to this task uncited; invalid_refs empty → nothing invented.
 - Gates: G0 PASS (orchestrator, administrative, reviewed_sha fc96fd9c), G1 PASS (data-contract-verifier, independent_review), G2 PASS (orchestrator, self_check). G1 and G2 share one content identity content_manifest_sha256 = fef93aff3d7bd2114c690bee7d8b7d830aea9a78bb302a56eaaaeb5ca4233fb9, which I independently reproduced with git_tree_manifest over the packet's allowed_paths at adc36fc7. validate_directive_compliance --check exit 0; research_record_check --check exit 0 (NB-03 interpretation_awaiting_review, code_current True, review_state current); sync_zr_snapshots --check exit 0. Main CI workflow fully green 21/21 (incl. control-plane ADR-005 and api ruff+pytest) at 5a8228c1 (run 38172084908) and 209498e1 (run 38172918909), whose M5-T163 content is byte-identical to adc36fc7; the cancelled main-CI at the exact adc36fc7 is the known duplicate-push supersession, and the descendant head 71a03977 is also green. Task is awaiting_gate (not accepted); branch not merged to main; M5-T163 not in main's accepted set (389 accepted).

(4) CARRY-FORWARD CONDITION
 - Stamp this PASS at any later head that satisfies the blob-level predicate: the packet's 12 allowed-path files keep their blob ids — equivalently content_manifest_sha256 over allowed_paths == fef93aff3d7bd2114c690bee7d8b7d830aea9a78bb302a56eaaaeb5ca4233fb9 (NB-03 acfd359f; zr-12-10-street e65bb149; -street-setback-line b3f421f0; -street-wide aae77008; -street-narrow be914341; and byte-identical bundled copies) — AND the four rows' text plus their M5-T163 applicability binding in requirements.json are unchanged (requirements_content_digest b31b83ce...).
 - Broad disjoint-peer tolerance: later commits may touch any other file (other tasks' files under services/, apps/, packages/, docs/, .claude/, their packets/gates/reports/directive bindings, ledger state), plus this task's own acceptance records (verification.json M5-T163 row, gate records, state.json), plus a merge of the main line that changes none of the predicate's files; none of these requires a new review.

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The official ZR portal's glyph-authoritative print/PDF for §12-10 (504) and per-node print (403): the documented DB-167 fallback. I could not re-fetch the live primary source; I verified internal integrity (content_digest == sha256(verbatim), each capture file's LF-normalized sha256 == NB-03 evidence refs E8/E9/E12/E13, byte-identical canonical/bundled blobs) and that the wide/narrow/setback law text matches the project's authoritative domain knowledge. Captures correctly stay extraction_status extracted_draft, raw_html_verified false.
 - The DOB-approved ZD1 / Buckley 2017 survey (access_blocked) — a genuine unresolved site fact, correctly left open.
 - The block-dimension corner-to-corner span (lots 1+70 combined Northern Blvd frontage used as the block dimension) is an inference from parcel geometry, not a City-Map measurement; flagged as G1 advisory 1 and routed to M5-T176. I did not measure the City Map.
 - I did not run the focused S2/S3 pytest (test_zr_snapshot_bundle, test_report_law_links) locally; I relied on the green CI api job at content-identical heads plus my own reproduction of byte-identity and the digest/no-'#' request_url checks.
 - I did not run tools/test_directive_compliance.py (forbidden; hours) or the full api suite; the control-plane and api CI jobs cover them.

END-OF-REPORT
```
