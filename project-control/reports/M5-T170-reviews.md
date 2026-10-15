# M5-T170 reviews (every return kept unchanged)

- Three build rounds (backend-engineer, worktrees): round 1 e85ace52 integrated as 281e23b7 (after scope correction 1: the rule-file fan-out); round 2 5b30c0e8 integrated as bec421b3 (the G1 and G4 required findings and the advisories); scope correction 2 (320d615b: NB-03 and the rear-yard register page join the packet because round 2 changed rear_yard_checks.py, a code path of NB-03); round 3 b5c11d59 integrated as 0dbe27b2 (NB-03 revision 4; DB-265 item 2, the register code link). Every builder commit inside the allowed paths; LF sha256 equal to each return.
- Independent pre-integration check of round 1 (return-M5-T170-precheck.json and its skeptic, session 2026-10-15a). Round 2: the builder ran the whole api suite (9951 passed, 8 skipped) and the whole web unit suite (2704 passed); the CI run on the pushed head runs both again. Round 3: records and register only (tests/rules 1194 passed under the lock).
- Real-preview prints (the owner's report printed from the branch through the preview): round 1 print-b067e9db (session 2026-10-15a: 11 pages; pages 3, 6 and 8 agree; DB-266 fixed); round 2 print-9ac5ad4a (session 2026-10-15b) diffed page by page against round 1: only page 3 changed (the side-yard row's "(see item 9)").
- G2 orchestrator self-check at the submit head: the task's files equal the integrated rounds; nothing outside the allowed paths; lane coverage PASS; research_record_check and render_review_register --check exit 0; the CI run at the submit head read green before submission.
- G1 data-contract-verifier at 281e23b7: PASS with REQUIRED F1 (width facts cited MapPLUTO) and advisories F2, F3; its skeptic upheld F1. All three closed in round 2. G1 delta check of rounds 2 and 3: below.
- G3 code-reviewer at 281e23b7: PASS. G5 security-reviewer at 281e23b7: PASS.
- G4 qa-engineer at 281e23b7: PASS with REQUIRED S17 (DB-265's six advisories not done) and advisories 3, 4; its skeptic upheld S17. Round 2 fixed items 1, 4, 5, 6 and advisories 3, 4; round 3 closed item 2; item 3 (a double fetch with the live spatial provider switched on, off by default; its file is outside the packet) is carried with its reason. G4 delta check of round 2: below.
- Delta checks: G4 (qa-engineer) at 640076ee PASS (S17 satisfied; two mutations reproduced red; 811 passed). G1 (data-contract-verifier) at a963266c PASS (F1 fixed and tested; F2/F3 correct against the captures; DB-265 texts, records and register honest; pages agree) with one advisory A1 (two dependency_assessment entries name the previous revision number in a parenthesis; text only, carried, not applied).

Every reviewer is an AI agent; none is a human or professional review.

## G1 (data-contract-verifier)

I have completed my G1 verification. Let me compose the report.

Key findings confirmed:
- Benchmark envelope data, constraint lines, and setback-depth-as-numbers all match both sealed readings and the captures.
- NB-06 rev 3 condition 3 closed with the 12-10 captures (E17/E18) quoted; 23-433(a)-(d) carried in NB-06 + the rule file; `research_record_check --check` PASS; code identity matches.
- Rule files have source linkage, no human verdict; `render_review_register --check` PASS.
- Pages 3/6/7-9 agree; DB-266 fixed (page 3 no longer drops rows the appendix lists).
- One REQUIRED defect: width input_facts carry MapPLUTO provenance instead of DCM Street Center Line.

---

I am an AI agent (G1 data-contract-verifier), read-only. This is a labelled AI review, not a human or professional determination.

# G1 GATE REPORT — M5-T170 (envelope constraints from NB-06)

VERDICT: PASS with required corrections

Reviewed at pinned SHA 281e23b7 (extracted via `git archive` to scratch). Checked against the two sealed readings (A, B), the mixed-side-yard research return, NB-06 captures (E1–E18), overlay-reading.json / real-lot.json, and the real branch print (print-b067e9db, standard_residence, BBL 4073340070).

## Law conformance (engine vs BOTH readings + captures)
- STREET WALL (`envelope_constraints.py` `_street_wall_check` L169-213): overlay → 8 ft flat on each frontage (`STREET_WALL_OFFSET_FT`), ZR 35-631 + 35-01(mixed)/34-24(res); no overlay → 8 wide / 10 narrow (`_no_overlay_offset` L216), D-051 asymmetry preserved, withheld (never narrow) for unresolved/unknown; not-read → no distance + overlay condition. Always `applies`, conditional on prevailing-frontage + operative-street-line. Matches A and B exactly.
- SETBACK (`_setback_triggered` L277, `_setback_check` L289): trigger strictly `> 45.00` (30/44.99/45.00 not triggered; 45.01/50 triggered); depths 10 wide / 15 narrow, withheld on unresolved/unknown width. Matches A and B and S2's 45.00 boundary. Benchmark 30-ft option `not_applicable` (RISK-3 G1 decision) — both readers say "not triggered"; concur.
- SIDE YARD (`_side_yard_check` L331): multi/mixed/residential → none required; detached+overlay → none (34-232); detached no-overlay → two 5-ft yards (23-335(a)); 5-ft open-area note. Matches A and (via the research resolver) B.

## Benchmark (recorded_215_16_northern_journey.json)
envelope_rows: street_wall applies (8/8 ft, prevailing-frontage + operative-street-line conditions, ZR 35-631+34-24); setback not_applicable with 15/10 ft numeric values + "above the 45 ft maximum base height" condition (ZR 23-433+35-632); side_yard not_applicable + 5-ft open-area condition. constraint_lines: street_wall_band + setback_line both `not_established`, basis derived, NO geometry (D-094-R017). input_facts: widths 100/60 numeric, basis gis, one basis each. Nothing called compliant/optimal/feasible. All agree with overlay-reading.json and both readings.

## Records / register (run in my copy)
- `research_record_check.py --check` → PASS, exit 0 (NB-01/05/06 code_current=True, no Verified claim; NB-06 stays `interpretation_awaiting_review`).
- `render_review_register.py --check` → PASS, exit 0. Three new rule files are DRAFT (needs_review), carry snapshot citations + digests, `automated_tests`="Not run", NO human/agent verdict entered.
- NB-06 rev 3: E17 "wide street … 75 feet or more", E18 "narrow street … less than 75 feet" captured and quoted, confirming D-052; condition-3 limitation resolved; 23-433(a)-(d) added to exceptions_considered. Code identity fb32d6…/fe6e7b…/064fb6… match the actual files (LF-sha256 verified). NB-05 rev 5 + NB-01 rev 7 code-identity rows match unchanged result_ways.py (ac0747…) / result_way_bridge.py (4e4d20…).

## Report pages 3 / 6 / 7-9 (real branch print)
All three constraints render on page 3 with a Conditional chip, the draft reading, and a working law link (35-631 street wall; 23-433 setback; 23-335/34-232 side yard). Appendix items 7/8/9 carry the same applied readings. Page 6 "What was not checked" lists only plan-placement + parking — the street wall is gated out. DB-266 confirmed fixed: on main (print-main-2bcdb05a) setback/street wall appear only as "not worked out"/"not checked" with page 3 dropping them; on the branch page 3 no longer drops a constraint the appendix lists, and side yard (absent on main) now appears.

## Findings

F1 — REQUIRED (provenance). `result_way_engine_bridge.py:352` `_envelope_analysis_for` passes `_mappluto_source(profile)` as the source for the width input_facts; `envelope_constraints.py:434` `_input_facts` stamps them basis "gis". Benchmark emits `mapped_street_width:Northern Boulevard 100` / `215 Place 60` with source "NYC Department of City Planning MapPLUTO, version 26v2" / "2026-09-30". But NB-06 E15 + measurement_basis state these widths come from the DCM Street Center Line feature service (document_date Last-Modified 2025-12-01, retrieved 2026-10-10), and `_input_facts`'s own docstring calls them "the DCM mapped width." MapPLUTO publishes no street-width field, so both source_title and source_date are the wrong dataset (value 100/60 and basis gis are correct). The correct provenance is already threaded in `street_data` (used by `_street_segments` to build `SegmentSource`, L260-268). Correction: source the width input_facts from the DCM Street Center Line provenance in `street_data`, not MapPLUTO; regenerate the benchmark and width-fact consumer pins. (Principle 2 provenance; S14 "its source title and date".)

F2 — ADVISORY (mixed-building citation). `_side_yard_check` L351-354: for any `_RESIDENCE_MULTI` type incl. `BUILDING_MIXED`, with overlay, the headline text reads "no side yard is required under ZR 34-232." The research return (the resolver of the A/B disagreement) holds 34-232 by its words reaches a "residential building" only, and a mixed building reaches the same answer via Chapter 5 → 23-335(b). State (not_applicable), result, and the 5-ft condition are correct, zr_sections already includes 23-335, and the shipped benchmark is residential_only so the print is unaffected. Correction: for `BUILDING_MIXED`, lead the citation with ZR 23-335(b).

F3 — ADVISORY (23-433(a)-(d) in the engine row). The (a)-(d) modifications are carried in NB-06 rev 3 and r6b_setback.rule.json ("ZR 23-433(a) to (d) may reduce the depths"), but a triggered-setback row (`_setback_check`, S1 >45 ft) emits flat 10/15 ft with only the above-base condition; it does not note (a) (1-ft/1-ft, 7-ft floor) or (c) (optional beyond 50 ft / ≤65°) can reduce/waive them. Benchmark triggers no setback, so unaffected. Correction: note the 10/15 ft are minimums subject to 23-433(a)-(d).

## What I could not check
- Live-route emission beyond the benchmark (read-only; no server). The benchmark/print is the evidence.
- The genuinely unresolved site facts (operative street line, prevailing-frontage/adjacency, zoning-lot extent) — correctly carried as named conditions, not resolved; I confirmed they stay unresolved.
- I did not re-run the full api/web suites (CI's job); the independent pre-check (return-M5-T170-precheck.json) reports whole api 9814 / web 2704 green at this content — not re-verified by me.
- 35-633(b) corner-lot one-street-line modification (raised by Reader A only, not both) — not an engine/both-readings divergence; no action required.

The three legal readings, the benchmark contract blocks, NB-06 rev 3, the rule files/register, and pages 3/6/7-9 are correct and internally consistent. F1 (width-fact source dataset) must be corrected before the data-provenance claim is clean; F2/F3 are precision improvements.

END-OF-REPORT

## G1 (skeptic of the G1 review)

I have enough to adjudicate. The data path, NB-06's stated source, the benchmark's emitted provenance, and the governing acceptance scenario (S14) are all confirmed.

Key confirmations:
- Width VALUES (100/60 ft) come from `street_data.centerlines` via `_frontage_widths` → `derive_frontage_street_widths(..., _street_segments(street_data,...))`; the profile is used only for `_lot_borough` and `_mappluto_source`.
- NB-06 E15 + `measurement_basis` record the widths' source as the "DCM Street Center Line feature service" (Last-Modified 2025-12-01, retrieved 2026-10-10).
- The benchmark input_facts stamp `source_title: "NYC Department of City Planning MapPLUTO, version 26v2"`, `source_date: "2026-09-30"` (a different dataset/date).
- Acceptance scenario S14 governs input_facts: "each uses one of the nine closed bases with its source title and date; the frontage widths are administrative_record/gis as recorded."
- The test (`test_envelope_constraints.py:273`) only asserts `f["source_title"] and f["source_date"]` are truthy — it does NOT check the dataset, so the wrong MapPLUTO source passes.
- Correct provenance is already threaded in `street_data.source` + `.provenance` (used to build `SegmentSource`, L260-268), all inside this task's allowed_paths.

SKEPTIC RETURN — M5-T170 G1 REQUIRED-finding adjudication (read-only, pinned 281e23b7)

F1 (width input_facts carry MapPLUTO provenance, not DCM Street Center Line) — UPHELD. Real: `_envelope_analysis_for` (result_way_engine_bridge.py:352) feeds `_mappluto_source(profile)` → "NYC...MapPLUTO, version 26v2"/"2026-09-30" into `build_envelope_analysis` → `_input_facts` (envelope_constraints.py:434, basis "gis"); benchmark emits exactly that for `mapped_street_width:Northern Boulevard`/`215 Place`. But the width VALUES originate from `street_data.centerlines` via `derive_frontage_street_widths(..., _street_segments(street_data,...))`, and NB-06 E15 + `measurement_basis` record their source as the "DCM Street Center Line feature service" (Last-Modified 2025-12-01, retrieved 2026-10-10) — a different dataset and date; MapPLUTO carries no street-width field. In scope: acceptance scenario S14 explicitly requires each input_fact carry "its source title and date … as recorded," and the width facts are a new 1.5.0 emission of this task. Correction belongs here: the right provenance is already threaded in `street_data.source`/`.provenance` (consumed by `SegmentSource`, L260-268); fix sits in result_way_engine_bridge.py + envelope_constraints.py + the regenerated benchmark, all in allowed_paths. Violates Principle 2/4 (provenance; official source). The pinning test (`test_envelope_constraints.py:273`) only asserts the fields are non-empty, so it passes the wrong source — the correction must also strengthen that assertion to the DCM dataset/date, else the defect stays untested.

F2 (mixed-building side-yard citation should lead with 23-335(b)) — correctly ADVISORY, not elevated. Real but non-shipping: `_side_yard_check` headline cites 34-232 for `BUILDING_MIXED`; the shipped benchmark is residential_only, `zr_sections` already lists 23-335, state/result/5-ft condition correct, so no output is wrong today. A citation-order precision fix, not a REQUIRED gate defect.

F3 (triggered-setback row should note 10/15 ft are minimums subject to 23-433(a)-(d)) — correctly ADVISORY, not elevated. The (a)-(d) modifications are carried in NB-06 rev 3 and r6b_setback.rule.json; the benchmark triggers no setback (30-ft option, not_applicable), so no shipped value is affected. Precision improvement to the triggered-row condition text, not a REQUIRED defect.

Net: the sole REQUIRED finding (F1) stands — real, in scope via S14, fixable within this task's files; it is a genuine provenance mislabel plus a too-weak test. F2/F3 are legitimately advisory and should not be promoted to REQUIRED. The G1 verdict "PASS with required corrections" is supportable, with F1 as the blocking correction before acceptance.

END-OF-REPORT

## G1 (data-contract-verifier, delta check of rounds 2 and 3)

I am an AI agent (data-contract-verifier), read-only. This is a labelled AI review, not a human or professional determination. G1 DELTA review of M5-T170 rounds 2+3, pinned a963266c (confirmed current branch head; extracted via `git archive` to scratch).

VERDICT: PASS (G1 delta). The round-1 REQUIRED F1 is fixed and now properly tested; the F2/F3 advisories are correctly implemented; the DB-265 texts, records and register are correct and honest; pages 3/6/8 agree. One cosmetic ADVISORY (A1) that does not block acceptance.

Content identity: LF-sha256 of all 12 pinned files equals the round-2/round-3 builder returns exactly (envelope_constraints 2f7d6146; rear_yard_checks 24b7f2c8; result_way_engine_bridge 267ac390; benchmark 8dab823c; NB-01 4edc98bd; NB-03 a6be4ab0; NB-05 3ba8faa2; NB-06 68d23686; register 37ce0213; REGISTER.md/HISTORY.md/rules md match).

1. F1 (REQUIRED, resolved). Benchmark `recorded_215_16_northern_journey.json` input_facts: `mapped_street_width:215 Place` = 60.0 ft / basis gis and `:Northern Boulevard` = 100.0 ft / basis gis, both source_title "DCP Digital City Map street center lines" (the production adapter's DCM label, adapters.py:158) — not MapPLUTO. `recorded_lot_area`/`lot_outline_area` keep MapPLUTO 26v2. Code: `_street_width_source` (bridge L177-189) reads title from `street_data.source` and date from `street_data.provenance.retrieved_at` — the SAME provenance `_street_segments` stamps on SegmentSource (L257-273), not `_mappluto_source`. `_input_facts` (envelope_constraints L457-477) emits nothing without both title+date (no borrowed source). The pinning test (test_result_way_engine_bridge.py:424) now asserts source_title==streets.source, "MapPLUTO" absent, source_date==streets.provenance.retrieved_at[0][:10], basis=="gis" — closing the round-1 skeptic's truthiness gap; round-2 mutation proof confirmed RED. Note: benchmark date 2026-09-30 is the synthetic fixture window's own retrieved_at (coincides with MapPLUTO's date but is read from street_data, not borrowed); it differs from NB-06 E15's real DCM retrieval 2026-10-10 because the benchmark is a synthetic pack — expected, not a defect.

2. F2/F3 vs captures (correct). F2: for BUILDING_MIXED (L365-371) the headline is "no side yard...ZR 23-335(b)", zr=[23-335, 35-01]; 34-232 and 35-24 are NOT cited. Verified against captures: 35-01 applies Ch.5 bulk to a mixed building; 35-21/35-22 bring in Article II Ch.3; 23-335(b) "all other buildings...no side yards." No zr-35-24 capture exists, so its non-citation is correct. Residential-in-overlay correctly keeps 34-232. F3: `_setback_depth_minimum_condition` (L322-331), added only when the setback is triggered, says the 10/15 ft depths "are the least...ZR 23-433(a) to (d) may reduce or waive them (for example where part of the wall is far enough from the street line)" — matches the 23-433 capture ((a) 1-ft/1-ft min 7 ft; (c) optional beyond 50 ft/≤65°). Plain words, correct. Minor: 35-21/35-22 are not in the mixed zr_sections (code anchors on 35-01) — defensible, not a defect.

3. DB-265 in rear_yard_checks.py (correct, no reading changed). `_check_c3` not_known text and `_combined` condition both name the (c)(1) alternative beside (c)(3): "meeting a side lot line calls for none under 23-344(c)(3), while meeting a rear lot line requires one under 23-344(c)(1)" — exactly the 23-344 capture and the settled reading in docs/reference-cases/R6B/cases/short-block-rear-yard.json (rows 9/20/31: branch on the adjoining lot's lot-line KIND; R6B-within-R6-R12 flagged for confirmation). `_check_b` appends the (b) waiver consequence only when state=="applies"; a not_applicable reading omits it. Combined row stays not_known/Conditional. NB-03 rev 4 states no state/value/quantity/interpretation/conclusion changed — honest.

4. Records (honest; tool PASS). Revisions NB-01 rev8, NB-03 rev4, NB-05 rev6, NB-06 rev4 (git-confirmed M5-T170 bumped each +1 from 281e23b7). code_identity for the changed files equals the pinned LF-sha256 (NB-03→24b7f2c8; NB-06→2f7d6146/267ac390). `research_record_check.py --check` exit 0, all six records code_current=True, requested_label=None; statuses interpretation_awaiting_review/access_blocked/answered_from_primary_source — nothing Verified. dependency_assessment prose accurately describes the edits and defers G1 confirmation to the reviewer.

5. Register (PASS; GUIDE-compliant; no human verdict). `render_review_register.py --check` exit 0. rear_yard_checks.py is added to the r6b-rear-yard-corner-waiver code_links; rule_file_sha256 ee909d7e unchanged. HISTORY seq 31 is one implementation_changed event (rev 4, 2026-10-15), AI-agent-attributed "backend-engineer (M5-T170)", honestly stating no rule-file/interpretation/test/reading change and pinning the LF-sha256 via NB-03 — no human/agent verdict entered.

6. Pages (agree). Real-preview print print-9ac5ad4a (round-2 head; round-3 touched only records/register wrappers): diff vs round-1 shows ONLY page 3 changed (side-yard row gained "(see item 9)"); pages 2/4/5/6/7/8/9/10/11 byte-identical. Page-3 constraints table + appendix items 7/8/9 match the engine rows: rear yard "conditional...ZR 23-344/12-10"; setback "no setback above the base required (23-433/35-632)"; street wall "35-631/34-24"; side yard "no side yard under 34-232 (23-335/34-232)" for the residential-overlay benchmark. Pages 6 and 8 unchanged from the round-1-confirmed agreement.

A1 (ADVISORY, non-blocking). The M5-T170 dependency_assessment entries name a parenthetical revision one below the record's current field: NB-01 rev 8 says "refreshed here (revision 7)"; NB-05 rev 6 says "(revision 5)". Content is honest and research_record_check passes; the label is ambiguous/possibly off-by-one. Suggest the orchestrator have it read "revision 8"/"revision 6" (or clarify it names the prior identity).

Could not check: live-route emission beyond the benchmark (no server, read-only); full api/web suites (CI's job — round-2 return reports 9951 api / 2704 web green, not re-run here); genuinely unresolved site facts (operative street line, prevailing frontage, zoning-lot extent) stay correctly carried as named conditions.

END-OF-REPORT

## G3 (code-reviewer)

I have completed my review. Here is my gate report.

---

**M5-T170 — G3 code-review gate report (code-reviewer share). I am an AI agent, not a human or professional reviewer. Read-only; nothing written, no servers touched.**

Pinned SHA `281e23b7` (task/wave26-envelope-constraints); the two JUSTIFY-watched files are byte-identical at worktree HEAD `b067e9db` (= the print folder). Scope: correctness/maintainability of `envelope_constraints.py` + the attach points, the no-default rule, the borough reconstruction, the setback reconcile, modularity, texts, 1.4.0 parity, ruff.

**VERDICT: PASS (code-review share), with advisory findings. No REQUIRED correctness defect in my area.**

**What I reproduced**
- `cd services/api && ruff check .` (lanes venv) → **All checks passed**.
- `tools/modularity_check.py --check` (worktree) → **failures 0**; `three_way_document.py` and `result_ways.py` are in the WARN band only, **below JUSTIFY (750)** — the brief's requirement holds.
- Real print `print-b067e9db/` pages 3/6/8: page 3 lists setback / street wall / side yard as applied Conditional readings; page 6 drops "The street wall" from "What was not checked"; page 8 items 7/8/9 show the applied readings — **pages agree**. `print-main-2bcdb05a/page-03` confirms DB-266 (main drops both rows) and that the branch fixes it.
- Benchmark fixture: `setback_above_base` value-state `reason`/`zr_sections` equal the envelope setback row — the reconcile agrees by construction.
- No `not_known` state is emitted; emitted user strings are clean (forbidden tokens appear only in docstrings).

**Could not check myself (relied on evidence):** full `pytest` and whole web `vitest` — I used the independent `return-M5-T170-precheck.json` (whole api 9814 passed; web 2704 passed on rerun after one unrelated timeout flake in `dashboard/engine.test.ts`). I did not re-derive the NB-06 law chain (directive-compliance-verifier / qa share).

**Findings**

1. **ADVISORY — truthiness test on the optional `overlay_present` for ZR citation.** `envelope_constraints.py:299` (`zr = _ZR_SETBACK_OVERLAY if overlay_present else _ZR_SETBACK_PLAIN`) and `:341`/`:352` (side yard). When the overlay is *not read* (`None`), these treat it as "no overlay" and drop the overlay section (ZR 35-632 / 34-232) from the citation. The result (depth, trigger, state) is unaffected — citation completeness only — and the benchmark has `overlay_present=True`, so it never hits this. But it contradicts the producer report's blanket claim "No truthiness test reads an optional fact as a value." Correction: use `overlay_present is True` for the citation too (or cite both sections when `None`).

2. **ADVISORY — S9 has no *dedicated* mutation test.** The packet/S9 requires "a mutation to one [setback emitter] that disagrees with the other fails a dedicated test." The 6 producer mutation proofs do not include it, and no focused test asserts `value_states.setback_above_base.reason/zr_sections == envelope setback row`. The agreement is pinned only *indirectly* by the regenerated journey fixture (removing `_reconcile_setback_value_state` would change the committed fixture → `test_215_16_northern_journey` fails), so sensitivity exists but is coarse. Design note: it is **not** a true second source of truth — the depths live only in the envelope row; the value-state stays `way:"withheld"` with a derived reason, so the two cannot numerically diverge in the normal path. Latent coupling: `_reconcile_setback_value_state` (three_way_document.py) only fires when the value-state `way == "withheld"`; if `result_ways._setback_way` ever emits a non-withheld way, the reconcile silently skips and page-3/value-state could diverge. Correction: add a focused test (value-state reason/zr == envelope row, plus a divergence mutation) and/or a comment/guard documenting the withheld precondition. (G4/qa should confirm test adequacy.)

3. **ADVISORY — page-3 side-yard row carries no "(see item N)" link while page 8 numbers it item 9.** `page_site_context.py:84` `_ENVELOPE_CATEGORY = {"setback": "setback", "street_wall": "street_wall"}` omits `side_yard`, so `_issue_link(None, …)` yields no cross-link, whereas `readers._apply_envelope_open_items` adds a numbered side-yard item (item 9). Both pages still *name* side yard, so constraint parity holds; only the convenience link is missing. Correction: add `"side_yard": "side_yard"` to `_ENVELOPE_CATEGORY` (the fallback row is `None` for side yard, so no other path changes).

4. **ADVISORY (minor) — borough reconstruction is sound and fail-closed.** `result_way_engine_bridge._lot_borough` reads `profile.identity.address.borough`; missing → `None`. In `exceptions.named_street` a `None`/blank borough returns "not checked" → `derive._segment_reasons` adds a reason → `street_class = NEEDS_STREET_WIDTH` → the envelope maps it to `WIDTH_UNKNOWN` → depth **withheld, never narrow** (D-051). Verified end-to-end by the benchmark (Queens; 215 Place narrow / Northern Blvd wide). Minor residual: `_lot_borough` emits `str(borough)`; if a profile stored a borough *code* rather than a name, a ZR 12-10 *named* wide street could be mis-matched (matcher returns not-matched → treated `not_applicable` → width-only class). Narrow edge; the benchmark uses the name. Worth a one-line note that the name form is assumed.

**Maintainability** — Good. `envelope_constraints.py` is a focused new module (one responsibility: NB-06 readings → additive 1.5.0 blocks), reuses the accepted D-052 classifier rather than re-deriving width, and keeps every number as a named constant cited to its section. The attach helpers (`_apply_envelope`, `_reconcile_setback_value_state`, `_street_wall_applied`, `_envelope_fallback_row`, `_apply_envelope_open_items`) are thin and opt-in; 1.4.0 documents never reach them, so behavior is byte-identical (confirmed by code path and the precheck's true-1.4.0 render). `_NOT_CHECKED_BASE` is now a 2-tuple referenced only at `[0]`/`[1]` in the same file — no stale index.

**Scenario-test sensitivity (per the brief):** S1 depths, S2 strict `>45` boundary (parametrized 45.00/45.01; mutation `>`→`>=` fails), S3 overlay/no-overlay 8/10 asymmetry, S4 side-yard table, S5 width→depth (through the *real* classifier + "never narrow" assert), S6 constraint lines (established/not_established), S8 "never not_known", S14 input facts, S18 page-3 fallback (mutation: restore `continue` → fails), and S10 page-8 benchmark — each would fail on its defect. The one gap is S9's *dedicated* test (finding 2).

END-OF-REPORT

## G4 (qa-engineer)

All heavy runs are green. I have complete evidence. Here is my gate report.

---

# G4 QA GATE REPORT — M5-T170 (envelope constraints from NB-06), reviewed at 281e23b7

I am an AI agent performing an independent, read-only G4 review. This is not a human or professional verification. I worked from a `git archive` copy of `281e23b7` under `/tmp/claude-0/t170-review-g4/`, wrote nothing in any repo, and started no servers.

## Verdict: PASS with required corrections

The envelope feature (street wall, setback-above-base, side yard) is built correctly, provenance-backed, byte-identical on 1.4.0, with pages 3/6/8 agreeing and DB-266 fixed. One acceptance scenario (S17) is entirely unaddressed; three advisories follow.

## Checks (all reproduced in my copy; direct exit codes)
- `ruff check .` → exit 0 (All checks passed).
- `pytest tests/rules` (flock) → **1160 passed**, exit 0 (incl. the three new goldens + lane-A rule-set pins).
- WHOLE `pytest` (flock) → **9897 passed, 8 skipped**, exit 0 (493s).
- web `npm run lint` → 0 errors, 2 pre-existing warnings (untouched test files); `typecheck` → exit 0; WHOLE `vitest run` (flock) → **129 files, 2704 passed**, exit 0 (engine.test.ts did NOT time out; jsdom getContext lines are MapLibre noise, no FAILs).
- `render_review_register --check` PASS; `research_record_check --check` PASS (NB-01/05/06 code_current=True); `validate_contracts` 23 schemas 0 failures; `modularity_check --check` exit 0, failures 0 (three_way_document.py / result_ways.py in WARN not JUSTIFY — S15 holds).
- CI at `task/wave26-envelope-constraints` for 281e23b7: CI, context-budget, secret-scan all **success** (the newest in_progress run is a disjoint handoff commit, not this task).

## Scenario table S1–S18
S1 setback 10 wide/15 narrow cited 23-433 — test_setback_depths… + my probe: PASS. S2 trigger table 30/44.99/45.00 not-triggered, 45.01/50 triggered — test_setback_trigger_table + mutation M1: PASS. S3 overlay 8ft both / no-overlay 8 wide 10 narrow never collapsed — test_street_wall_* + M3: PASS. S4 side-yard table — test_side_yard_* (multi/mixed/detached±overlay/open-area): outcomes PASS (citation caveat, Finding 2). S5 width→depth via the REUSED D-052 classifier — test_per_frontage_width_class (real classifier) + M2: PASS. S6 constraint lines established/not_established — test_constraint_lines_* : PASS. S7 benchmark rows — fixture + print page 3: PASS. S8 none not_known — test_no_envelope_row_is_ever_not_known + my R061 probe: PASS. S9 two setback emitters agree; a disagreement fails a test — mutation M6 reddens the journey golden (test_215_16_northern_journey): PASS. S10 1.4.0 byte-identical; 1.5.0 pages 3/6/8 agree on the REAL print — print-b067e9db pages 3/6/8 verified (see below): PASS. S11 register/record checks, 3 entries no human verdict, NB-06 rev3 — verified (verdict "Not reviewed", law+code+test links present, 26=23+3 entries): PASS. S12 condition-3 closure, 12-10 captures confirm D-052 (<75 narrow, ≥75 wide), 23-433(a)-(d) added — NB-06 diff verified: PASS. S13 benchmark regenerated, consumers updated — fixture diff + green suites: PASS. S14 input_facts gis with provenance, no invented fact — test_input_facts_* : PASS. S15 goldens text-only, modularity, no JUSTIFY cross — PASS. S16 NB-05 rev5 / NB-01 rev7 fire — present in diff: PASS (G1/DCV confirm). S18 page-3 fallback never silently omits — test_m5t170_s18 + mutation M5: PASS.

## Real-print cross-check (branch vs main)
Branch print page 3 lists all three readings (Setback "no setback above the base is required" ZR 23-433/35-632 →item 7; Street wall ZR 35-631/34-24 →item 8; Side yard ZR 34-232/23-335 Conditional). Page 6 "What was not checked" drops "The street wall" (agrees). Page 8 items 7/8/9 show the applied Conditional readings — no "not checked". main 2bcdb05a page 3 drops setback+street-wall while its page 8 keeps them as items 7/8 — DB-266 confirmed and fixed here.

## Mutation probes (applied in copy, restored)
M1 `>`→`>=` (envelope_constraints.py:286) → RED. M2 unknown width→narrow depth (_setback_depth) → RED (4 failed). M3 no-overlay narrow 10→8 (_no_overlay_offset) → RED. M4 not-stated side-yard drops detached condition → RED. M5 remove page-3 fallback (page_site_context.py) → RED (S18 test). M6 reconcile reason mismatch → RED on the journey golden (GREEN on report_benchmark/contract, as designed — they strip setback for the 1.4.0-core compare). All six caught.

## Findings
**1 — REQUIRED. S17 (DB-265, the six M5-T167 advisories) is unaddressed.** `project-control/reports/M5-T170-producer-report.md` contains no S17/DB-265 section, and `rear_yard_checks.py`, `study_inputs.py`, `test_rear_yard_short_block.py`, `test_study_live_geometry.py` (added to allowed_paths precisely for this) are unchanged at 281e23b7. Spot-check: no 503-coercion added, rear-yard register code-link advisory not applied. S17 requires each advisory "resolved or carried with a reason in the producer report." Correction: address the six advisories, OR the orchestrator records a decision to split DB-265 to a follow-up task — not silently drop it. (Not a D-094 requirement; scope decision is the orchestrator's.)

**2 — ADVISORY (G1 cross-ref, RISK 10). Mixed-building side-yard citation.** `envelope_constraints.py:352` emits `ZR 34-232` for a mixed building in the overlay. The research return (return-research-mixed-side-yard.md) concludes 34-232 governs a "residential building" only; a mixed building reaches "not required" via 35-01→35-21→35-22→23-335(b). The result (not required) is correct; the cited section is imprecise for the mixed case, and `test_side_yard_mixed_none_required` (test_envelope_constraints.py:211) asserts only the state, not the citation. The benchmark is all-residential, where 34-232 is correct, so the print is unaffected. G1 rules per the packet; if confirmed, cite 23-335(b) (optionally 35-24) for mixed.

**3 — ADVISORY. Page-8 side-yard effect is state-invariant.** `readers._envelope_open_effect` returns a fixed "No side yard is required…" for side_yard regardless of row state, unlike the setback branch. A detached-no-overlay row (state=applies, two 5-ft yards) would make page 8 contradict page 3. Unreachable via the live route today (`_building_type` yields only residential_only/mixed), so latent. Recommend making side_yard vary with state.

**4 — ADVISORY. Page-3 side-yard carries no "see item" link.** `_ENVELOPE_CATEGORY` (page_site_context.py) omits side_yard, so page 3 shows no cross-reference while page 8 numbers it item 9; setback/street_wall both link. Add `"side_yard": "side_yard"`.

Note (not a finding): result_ways.py was not edited; the two-emitter agreement (objective item 4 / S9) is achieved by a document-level reconcile in three_way_document.py + envelope_constraints.py. Defensible, test-proven (M6), avoids a calc-page fan-out; code-reviewer/DCV may weigh in.

## What I could not check
I did not run `.github/scripts/tests` (outside my share; validate_contracts passed). I did not re-derive the full ZR legal chain (34-11→34-24(b)(1)→35-63→35-631(b); the 70%-of-aggregate street-wall nuance in overlay-reading.json street-wall-location) — that independent legal reading is G1's. Directive-requirement (D-094 R017/R043/R061/R082) completeness is the directive-compliance-verifier's pass.

END-OF-REPORT

## G4 (skeptic of the G4 review)

I have complete evidence. Here is my skeptic adjudication.

SKEPTIC ADJUDICATION — M5-T170 @ 281e23b7 (w-wave20)

Finding 1 (S17 / DB-265, six M5-T167 advisories unaddressed) — **UPHELD**. The reviewer's facts reproduce exactly: (a) S17 is a genuine acceptance scenario in `project-control/tasks/M5-T170.json` requiring each of the six advisories be "resolved OR carried with a reason in the producer report"; (b) the producer report `project-control/reports/M5-T170-producer-report.md` (228 lines, ends END-OF-REPORT) has NO S17/DB-265 section — grep for s17|db-265|503|operative.reach|coerc|waiver returns nothing, and the "Assumptions/limitations" + "Plan claims" tails carry no carry-reason for DB-265; (c) all four fix-carrying files are present but byte-unchanged across the entire task span (`git diff --name-only 0b9a6415 281e23b7` lists none of `rear_yard_checks.py`, `api/v1/study_inputs.py`, `test_rear_yard_short_block.py`, `test_study_live_geometry.py`), so advisory 6 (503 coercion in the live route) is not added; (d) advisory 2 is independently confirmed unapplied — register entry `r6b-rear-yard-corner-waiver` `code_links` = [rule.json, evaluator.py, registry.py], i.e. `rear_yard_checks.py` is absent. In scope: yes — those four files were added to this packet's `allowed_paths` precisely to carry S17, so the obligation is inside this task's contract, not a follow-up invention. Belongs here: yes — "carried with a reason in the producer report" requires an explicit report reason; silent omission is neither a resolution nor a carry, so the scenario is unsatisfied as written. The reviewer's remedy (address the six OR the orchestrator records a decision to split DB-265 — not drop silently) correctly locates the split-vs-fix choice with the orchestrator. The sealed readings (`return-sealed-T170-A/-B.md`) and `docs/reference-cases/R6B/cases/` concern the NB-06 envelope law (street-wall/setback/side-yard), not the rear-yard DB-265 advisories, so they cannot moot S17. No refutation available.

Findings 2, 3, 4 — marked ADVISORY by the G4 reviewer, not REQUIRED; outside this skeptic pass's refutation mandate. Noted, not adjudicated.

Net: the sole REQUIRED finding stands. M5-T170 at 281e23b7 does not satisfy its own S17; the gate's "PASS with required corrections" is well-founded and acceptance is correctly blocked until the orchestrator either lands the six DB-265 advisory fixes within the packet's allowed_paths or records an explicit split decision.

Relevant paths (all absolute):
- /root/project/w-wave20 → `git show 281e23b7:project-control/tasks/M5-T170.json` (S17 text; allowed_paths)
- /root/project/w-wave20 → `git show 281e23b7:project-control/reports/M5-T170-producer-report.md` (no S17 section)
- /root/project/w-wave20 → `git show 281e23b7:services/api/app/rules/review_register/register.json` (rear-yard code_links lack rear_yard_checks.py)

END-OF-REPORT

## G4 (qa-engineer, delta check of round 2)

# G4 QA GATE REPORT (DELTA, round 2) — M5-T170, reviewed at 640076ee

I am an AI agent performing an independent, read-only G4 delta review. Not a human or professional verification. I worked from a `git archive` copy of `640076ee` under `/tmp/claude-0/t170-g4-delta/` (round-1 `281e23b7` extracted to `/tmp/claude-0/t170-r1/` for diffs); wrote nothing in any repo, started no server, ran heavy pytest under the flock lock.

## Verdict: PASS (G4 delta)

Both round-1 REQUIRED findings (G1 F1 width provenance; G4 F1 = S17) are resolved; the three advisories and G4 adv 3/4 applied; no new defect. Content identity confirmed: the 10 key changed files' LF sha256 at 640076ee all match the builder's return exactly.

## 1. S17 / the six DB-265 advisories (my primary share)
- (1) (c)(1) alternative — **FIXED**. `rear_yard_checks` `_check_c3`/combined now name 23-344(c)(1) besides (c)(3); state stays `not_known`. I checked the wording against the ZR 23-344 snapshot verbatim: (c)(1) "a rear yard shall be provided... where such rear lot line coincides with a rear lot line of an adjoining zoning lot"; (c)(3) "no rear yard... where [it] coincides with a side lot line". The paraphrase is faithful. Test `test_c3_and_combined_texts_name_the_c1_alternative_besides_c3` passes.
- (2) register code_link — **CARRIED with reason** (rendered rule page outside allowed_paths; `--check` fails closed on a stale page). Scope-correction 2 adds the files for round 3. Legitimate carry, not a drop.
- (3) double street-window fetch — **CARRIED with reason** (in `study_live_geometry.py`, outside allowed_paths; flag off by default). Legitimate carry.
- (4) operative-reach arg — **FIXED**. I confirmed the round-1 `_rear_yard_constraint_lines` body never read `operative_reach_ft` (always returns both lines `not_known`), so the drop is behaviour-identical; propagated through `build_rear_yard_analysis`, the bridge, and the `_analysis` test helper. grep: zero residual `operative_reach`/`street_reaches`.
- (5) `_check_b` not_applicable text — **FIXED**. The "(b) waiver consequence" is appended only when state==applies. Tests `..._omits_the_waiver_consequence` / `..._keeps...` pass.
- (6) 503 coercion — **FIXED**. `study_inputs.py` re-raises `StudyInputsUnavailableError`, coerces any other `Exception` to it (reason `street_data_unavailable`); typed errors untouched. `except Exception` does not catch KeyboardInterrupt/SystemExit. Test passes.
All six are each fixed-with-a-test or carried-with-a-written-reason in the producer report — S17 satisfied.

## 2. Mutation proofs (reproduced two in my copy)
- #3 page-8 side-yard made state-invariant → `test_m5t170_page_8_side_yard_effect_follows_the_row_state` **FAILED** (RED).
- #4 503 coercion replaced by re-raise → `test_unexpected_street_data_provider_exception_becomes_a_503` **FAILED** (RED).
Both files restored byte-identical (sha256 re-verified: readers.py 4aed375d…, study_inputs.py 8f70a61c…).

## 3. G4 adv 3 & 4 + the moved pin
- adv 3 FIXED: `readers._envelope_open_effect` side-yard now returns the two-5ft-yards text (ZR 23-335(a)) when state==applies, else "No side yard is required" — follows row state like setback. Test passes.
- adv 4 FIXED: `page_site_context._ENVELOPE_CATEGORY` gains `side_yard`; page-3 row carries the "(see item N)" link. Test passes.
- The only moved consumer pin is `test_constraints_page` baseline 216→220; justified by the single "(see item 9)" link. Every other test change is additive (new tests) or the dead-arg helper cleanup. Confirmed no other golden/pin moved.

## 4. Checks (my copy, lanes venv, under flock)
- `ruff check .` → **exit 0** (All checks passed).
- `pytest tests/scenario/three_answers tests/drawings/report tests/api/test_study_live_geometry.py` → **811 passed, 2 skipped, exit 0** (123.9s). The 9 named pinning tests also run green individually.
- F1 provenance: new `source_title` "DCP Digital City Map street center lines" is faithful to NB-06 E15/measurement_basis (DCM Street Center Line); width values 60/100, date, basis `gis` unchanged; fixture diff is exactly 2 rear-yard-text + 2 provenance-title lines (no value drift). `_input_facts` emits no width fact when title or date is missing ("no provenance, no fact", D-093) — sound null handling.

## 5. CI
The CI run at **640076ee** (38709881151) was **cancelled** by the next push (own-push cancellation). The later head **9ac5ad4a** differs from 640076ee only in control-plane files (`M5-T170-G0.json`, `M5-T170-G0.md`, `state.json`, `tasks/M5-T170.json`) — I verified `git diff --name-only 640076ee 9ac5ad4a` lists no code/test file. Its CI run **38709959569 is fully green: 21/21 jobs success** (api ruff+pytest, web-e2e, modularity, control-plane, contracts, dependency-security, etc.; conclusion=success). So the green CI covers the exact code/test content under review.

## What I could not check
- The orchestrator's real-preview print folder `session-2026-10-15b/print-9ac5ad4a/` is **empty** (not yet landed), so I could not run the per-page pdftotext comparison of pages 3/6/8. The builder's TestClient print reports only page 3 changed (+" (see item 9)"), pages 3/6/8 agree; I corroborated this via the readers/page_site_context code and the two page tests, not by re-rendering (I must not start a server).
- The full ZR legal chain and NB-03 round-3 code-identity revision are G1's domain; the directive-requirement completeness pass is the directive-compliance-verifier's.

END-OF-REPORT

## G5 (security-reviewer)

I have completed all G5 security checks. Every item in my brief is verified. Here is my gate report.

---

# G5 Security Gate Report — M5-T170 (envelope constraints from NB-06)

**Reviewer:** security-reviewer (G5), independent, read-only. **I am an AI agent; this is not a human or professional security review.**
**Reviewed identity:** `281e23b7` on `task/wave26-envelope-constraints`. I confirmed this task's files are byte-identical at the current branch head `b067e9db` (`git diff 281e23b7 b067e9db` over `scenario/three_answers/*`, `drawings/report/*`, `rules/*` = 0 lines), so the print folder `print-b067e9db/` matches the reviewed code.
**Scope:** 37 files; production Python = `envelope_constraints.py` (new), `result_way_engine_bridge.py`, `three_way_document.py`, `first_option_results.py`, `drawings/report/readers.py`, `drawings/report/page_site_context.py`; plus 3 rule JSONs, the review register, evidence records, benchmark fixture, tests.

## Verdict: PASS (no required or advisory security findings)

## Checks performed and evidence

**1. New/changed external request (expected none).** CONFIRMED none. The envelope analysis is built from data already in the request flow: `_envelope_analysis_for` takes `street_data`/`geometry`/`profile` as parameters (bridge lines ~232–378). `_lot_borough` reads `profile["identity"]["address"]["borough"]` from the in-memory profile and `str()`-casts it — no fetch, no host/path. `_street_segments` builds `SegmentSource.request_url` from the *already-fetched* `street_data.provenance`, not a new call. `derive_frontage_street_widths` is the accepted D-052 classifier operating on in-memory segments. Grep of the production diff for `requests|httpx|urlopen|socket|subprocess|os.system` = none.

**2. New route input / deserialization (expected none).** CONFIRMED none. No `@router`/`@app`/`APIRouter`/`Depends`/SQL/`execute(` added anywhere in the diff. The route change (`run_engine_and_result_ways_from_evidence`) only threads one additional opt-in in-memory analysis; it parses no new user input. Emission is opt-in on a DCM street window being supplied (same gate as the accepted rear-yard emission), so with no window the document stays 1.4.0.

**3. Text/link emission into report HTML/PDF and website (escaping; links only to official law site; no markup from data fields).** CONFIRMED safe.
- All new page-3/page-8 cells use `el(...)`/`label_chip(...)` with static constant strings (`_ENVELOPE_TITLES`, `_ENVELOPE_FALLBACK_STATE`, `_ENVELOPE_RESOLVES`, effect strings). `el` escapes every text child via `html.escape` (`drawings/report/html.py:55-67`).
- The only external-data field this task introduces is the street name, carried in `values[].name` and in the `input_facts` key `mapped_street_width:<street_name>`. Page 3 renders neither — it renders title/state/label only. On the location drawing the input-fact *rendered text* is figure + basis word (`other_basis_label`, `close_frame_dimensions.py:258-264`), never the key. The street name reaches rendered output only as the `data-source` SVG attribute (`svg.py:text_element`), which is XML-escaped by `svg.attrs`/`svg.escape` (`&<>"` escaped, control chars refused, attributes double-quoted) — no markup/attribute breakout.
- All law links go through `law_links.section_url` → the pre-existing hardened allowlist (`law_links.py`: fixed `_HOST=zoningresolution.planning.nyc.gov`, https only, no creds/port/query, path+anchor regex, canonical rebuild, snapshot-index lookup returning an official URL or `None`), then `href="{escape_attr(url)}"`. `law_links.py` is not modified by this task. The task's `zr_sections` are hardcoded constants (`_ZR_STREET_WALL_OVERLAY=["ZR 35-631"]` etc.), not data-derived — no injection/SSRF vector into link hosts.
- Every URL introduced in the diff resolves to the official NYC ZR site (`zoningresolution.planning.nyc.gov/...` and the ZR print channel `zr.planning.nyc.gov/entityprint/pdf/node/18433`). No third-party or user-controlled host.

**4. Secrets/credentials in code, fixtures, records, tests.** CONFIRMED none. Full-diff scan for `password|secret|api[_-]?key|token|bearer|authorization|private key|aws_|service_role|supabase|postgres://|-----BEGIN|AKIA…|ghp_|sk-…` = no matches.

**5. Dependency changes (expected none).** CONFIRMED none. No `lock|requirements|pyproject|package.json|.env` file in the 37-file list.

**6. Production switch / environment setting / deployment file (expected none; `LIVE_SPATIAL_PROVIDER_ENABLED` default off).** CONFIRMED none. No deployment/YAML/env/config file changed. The only `LIVE_SPATIAL_PROVIDER_ENABLED` occurrence in the diff is descriptive prose inside the NB-05 revision-history record (carried from M5-T167), not a code change; the flag's default-off behavior is untouched. The test-only `_ON={"LANE_A_ENABLED":"1"}` is in a rule-register test file, not a production toggle.

**ruff:** `ruff check .` on my extracted copy of `services/api` → "All checks passed!" (exit 0; project venv `/root/project/lanes-runtime/venv/bin/ruff`).

## Cross-cutting security posture (per mandate)
- **Cross-tenant isolation:** no new data access; logic operates only on the single request's in-memory document. No concern introduced.
- **Service-role secrecy / private storage:** no secret use, no storage/bucket access added. N/A.
- **SSRF:** no new outbound request; report link host is a fixed allowlist. No vector.
- **Injection:** no SQL; HTML text and SVG attributes escaped; `zr_sections` hardcoded. Rule JSONs are declarative (standard schema keys; no `eval/exec/lambda/subprocess/<script>/javascript:`).
- **Upload controls / prompt-injection:** no upload path; no runtime AI/prompt handling — the readings are deterministic static constants, not model output. N/A for this change.
- **Least privilege:** no new external surface or privilege.
- **Log redaction:** no logging/`print`/file-write added; no PII emitted to logs.

## What I could not check (and why)
- I did not run the full api pytest or any web vitest/e2e (brief forbids the full api suite; heavy web runs are the content/precheck reviewers' and CI's job). The independent pre-integration check (`return-M5-T170-precheck.json`) reports whole-api 9814 passed and whole-web 2704 passed; CI at the accepted head is the authoritative gate. My G5 scope is the security slice above, verified statically plus ruff.
- I verified correctness only where it bears on security (escaping, hardcoded sections, opt-in gating); zoning-accuracy and page-agreement correctness are other reviewers' roles.

No security defect found. Nothing blocks acceptance on security grounds.

END-OF-REPORT
