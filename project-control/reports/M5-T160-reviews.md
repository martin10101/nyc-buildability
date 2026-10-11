# M5-T160 reviews (every return kept unchanged)

- G1 round 1: data-contract-verifier at 2bbfed94, PASS with one required correction (conditions[0]) and two advisories.
- Revision 2 (researcher, integrated b544a4b3) applied all three.
- G1 delta: the same reviewer at b544a4b3, PASS (agrees, revision 2). Its review entry was copied into the record's review.agent_reviews by the orchestrator (the only change after b544a4b3 to the task's files).

## G1 delta return

<!-- saved unchanged by save_return.py from agent-acb58e6d8a06f1f70.jsonl, entry 2026-10-11T06:00:01.110Z, sha256 d46c754ff5dec581fa4598a7dee12701b455c7a9893af7df88920be850a3f55f -->
# G1 delta review — M5-T160 / NB-06 revision 2 at b544a4b3ec5132cbb70b448f15da4a93a3ae4e66

**Delta verdict: PASS.** All three findings resolved; nothing further remains. Read-only; captures opened directly (D-093).

## Findings re-verified (at b544a4b3, worktree /root/project/w-wave20, HEAD==b544a4b3)
- **F1(a) CONFIRMED.** conclusion.conditions[0] now reads that the 35-631(b) percentage rule governs unless its closing clause permits the **23-431(a)** line-up, and states "35-631(a) itself does not apply to this R6B Queens site." Matches the full zr-35-631 capture (closing clause of (b) points to 23-431(a); (a) is R8–R12 Manhattan Core only).
- **F1(b) CONFIRMED.** The gloss now follows the ZR 12-10 defined term and is cited as new **E16** (zr-12-10-prevailing-street-wall-frontage.snapshot.json): within 150 ft, at least half the aggregate street-wall width within 2 ft of the average distance, aggregate ≥100 ft, >50% of segments within 2 ft of that average. Saved copy exists; LF-normalized sha256 0bef4080835cc1535bc0c01fb6919056335fcb0d43bcd5816f88d458e108469f matches. Added to provisions_read. The 15 ft / 25 ft / >35 ft test is retained only as the 23-431(a) eligible-adjacent-building test.
- **F2 CONFIRMED.** E15 excerpt and the DCM observed_facts bullet relabelled as a selection of lot 70's frontages (Northern Boulevard, 215 Place); 215 Street (w 60) and 45 Road (w 50) noted as context only, not frontages; list stated non-exhaustive. Consistent with the 6-feature E15 data file.
- **F3 CONFIRMED.** exceptions_considered adds a 35-631(c) note (large-zoning-lot test quoted; inapplicable — lot 70 ≈ 10,075 sq ft, under 40,000 sq ft, not whole-block) and a 35-631(d) articulation-allowance note (12-inch general; up to 50% at up to 3 ft; no projection past the street line except per Admin Code), both quoting the capture. The "~10,075 sq ft" figure is correctly sourced: NB-04 records lot 70 area = 10075 sq ft (administrative_record); the gis tax-lot outline is 10,387.99 sq ft — both well under 40,000 sq ft.

## Scope / no-drift check
- Complete NB-06 removed-line set = exactly the four targeted lines (revision 1; old E15 excerpt; old provisions_read[0]; old conditions[0]) plus the old DCM observed_facts bullet; every other change is an addition. 26 json lines changed (+ producer-report appendix). Nothing else in the record changed beyond revision 1→2; last_changed stays 2026-10-11 (same day).
- All 16 evidence saved copies exist; all 16 LF-normalized sha256 match.
- `python3 tools/research_record_check.py --check` at b544a4b3 → **exit 0, PASS**. NB-06: status=interpretation_awaiting_review, code_current=True, review_state=none, requested_label=None. (NB-05 now shows review_state=current at this head.)
- review.agent_reviews left empty (orchestrator adds the review entry) — correct. Q1/Q2/Q3 substantive answers unchanged and remain correct and sourced (re-verified in revision 1).

The producer-report appendix accurately documents the three corrections and the integrated head.

## Review entry (reviewed_revision: 2)
{"reviewer": "data-contract-verifier", "date": "2026-10-11", "reviewed_revision": 2, "verdict": "agrees", "findings": ["F1(a) resolved: conditions[0] now names the 23-431(a) line-up as the 35-631(b) closing-clause fallback and states 35-631(a) does not apply to this R6B Queens site.", "F1(b) resolved: the 'prevailing street wall frontage' gloss now follows the ZR 12-10 definition cited as new E16 (saved copy present; LF sha256 0bef4080...469f matches), added to provisions_read; the 15/25/>35-ft test is kept only as the 23-431(a) eligibility test.", "F2 resolved: E15 excerpt and the DCM observed fact are relabelled a selection of lot 70's frontages (Northern Boulevard, 215 Place); 215 Street and 45 Road marked context-only, list non-exhaustive.", "F3 resolved: exceptions_considered adds 35-631(c) (inapplicable; lot 70 ~10,075 sq ft per NB-04, under 40,000 sq ft and not whole-block) and 35-631(d) articulation-allowance notes, both quoting the capture.", "No drift: only revision 1->2 and the four targeted fixes changed; all 16 evidence sha256 match; research_record_check.py --check exits 0; status interpretation_awaiting_review with no label requested."]}

END-OF-REPORT


## G1 round 1 return

<!-- saved unchanged by save_return.py from agent-acb58e6d8a06f1f70.jsonl, entry 2026-10-11T05:54:28.367Z, sha256 4e8b8435697b98f22fd18f3e5c99f64d0b8864d2bcb625be1500ae3ae14dbb0b -->
# G1 (data-contract-verifier) — M5-T160 / NB-06 (street wall, 23-433 setback trigger, R6B side yards)

**Verdict: PASS with required corrections.** Frozen head `2bbfed94311cd40ecb07f836590dd4413870099a` (worktree `/root/project/w-wave20`, HEAD == frozen head, tree clean). Read-only review; no writes/ledger/git.

## What I checked myself (primary sources, before reading the record's interpretation)

**SHA-256 / existence (LF-normalized):** all 15 evidence saved copies exist and every digest matches (E1–E14 ZR snapshots under `docs/research/zr-snapshots/v1/`; E15 DCM data file). Script-verified, ALL_OK.

**Structural check:** `python3 tools/research_record_check.py --check` at the frozen head → exit 0, PASS. NB-06 line: `status=interpretation_awaiting_review  code_current=True  review_state=none  requested_label=None`. No Verified label requested.

**Q1 street wall (worked from captures).** For a residential-only building: 34-11 (`zr-34-11`) sends residential buildings in C1–C6 to Art. II Ch. 3 bulk "except as modified by ... 34-24"; 34-24(b)(1) (`zr-34-24`) "shall" apply the 35-63 modifications for an R6–R12 equivalency; 35-63 (`zr-35-63`) "the street wall location ... shall be as set forth in Section 35-631." For a mixed building: 35-01 (`zr-35-01`) applies Ch. 5 bulk directly. Both reach 35-631. 35-631(a) (`zr-35-631`) is R8–R12 Manhattan Core only → does not apply to R6B Queens; 35-631(b) governs: ≥70% of aggregate street-wall width within **8 ft** of the street line on each frontage, extending to at least the 30 ft min base height or building height whichever is less; up to 30% recessed, recesses >10 ft (wide, Northern Blvd) or >15 ft (narrow, 215 Pl) in an outer court. I confirmed 35-631(b) uses 8 ft for BOTH frontages (unlike 23-431(b)'s 8/10) and the record uses 8 ft per frontage correctly. **Record's Q1 answer is correct and sourced.**

**Q2 setback (worked from captures).** 23-432 (`zr-23-432`) and 23-433 (`zr-23-433`) + overlay 35-632(a) (`zr-35-632`) all trigger a setback only "for portions of a building street wall that exceed the maximum base height," provided between min and max base height. I confirmed the structured 23-432 table R6B row = min 30 / standard max base 45 / standard max building 55 (qualifying 45/65), single row with no 100-ft-of-wide-street footnote. The 30 ft three-storey benchmark is at the min base and below 45 ft → no setback. Street-width class sets only the depth (10 ft wide / 15 ft narrow) of a setback above 45 ft. **Record's Q2 answer is correct and sourced.**

**Q3 side yards (worked from captures).** 23-335(b) (`zr-23-335`): no side yard required for residences other than single/two-family detached; 34-232 (`zr-34-232`): no side yard required for any residential building in C1–C6; any open area along a side lot line ≥5 ft. 23-335(a)'s two 5-ft yards apply only to single/two-family detached, and 34-232 removes even that in the overlay. **Record's Q3 answer is correct and sourced.**

**Supporting facts.** E15 DCM file confirms Northern Blvd width 100 (wide, ≥75 per D-052-R001) and 215 Place width 60 (narrow). D-052 requirements confirm "below 75 narrow, 75+ wide," exceptions checked first (the 3/26/2026 'street, wide' alternate-width amendment is inapplicable to R6B/C2-2), DRAFT posture — all consistent with the record. The 12-10 'street, narrow'/'street, wide' snapshots are genuinely absent from the set (only street-line, prevailing-street-wall-frontage, aggregate-width-of-street-walls exist). I independently re-fetched the live ZR 12-10 page: it **truncated before the street definitions**, reproducing the record's S3 claim. NB-03 keeps the same street-line-from-survey/approved-plan condition → consistent. Observed_facts are faithful source restatements, separate from the site-specific `interpretation`; conflicts [] is appropriate.

## Findings

**1. REQUIRED — `conclusion.conditions[0]` has two reading errors.** The text: *"Whether 35-631(a) line-up or 35-631(b) percentage governs ... depends on whether either frontage of the block has a #prevailing street wall frontage# further from the street line (eligible adjacent buildings within 15 ft of the street line, within 25 ft of the subject, height over 35 ft)..."*
  (a) It names **"35-631(a) line-up"** as the alternative, but the record itself (correctly, elsewhere) establishes 35-631(a) cannot apply to this R6B Queens site. The fallback in the closing clause of 35-631(b) is to **23-431(a)**, not 35-631(a) (verified in the full `zr-35-631` text and E9). Should read "the 23-431(a) line-up."
  (b) The parenthetical glosses **"prevailing street wall frontage"** with the **23-431(a) eligible-adjacent-building test** (15 ft / 25 ft / >35 ft). That is the line-up eligibility test, not the defined term. The actual ZR 12-10 definition (in repo snapshot `zr-12-10-prevailing-street-wall-frontage`, but NOT cited as evidence in NB-06) uses a 150-ft selection, street walls within 2 ft of the average distance from the street line, and aggregate width ≥100 ft. Correct the gloss, and ideally add the 12-10 definition as an evidence item since the reading leans on the concept. (Top-line Q1/Q2/Q3 answers are unaffected; `exceptions_considered[1]` and the regression cases state the fallback correctly — the error is isolated to this one condition.)

**2. ADVISORY — E15 excerpt is a non-flagged subset.** The envelope query returned 6 features; the excerpt (and observed_facts[12]) list only 3 ("Northern Boulevard 100; 215 Place 60; 215 Street 60"), omitting "45 Road" (w=50) and duplicate "215 Street" segments, while reading as exhaustive ("Features at the lot envelope:"). The two actual lot-70 frontages (Northern Blvd, 215 Place) are correct and correctly used; note that 215 Street is not a frontage of this lot. Recommend labelling the list as a selection of the relevant frontages.

**3. ADVISORY — street-wall reading omits 35-631(c)/(d).** 35-631(c) (large zoning lots ≥40,000 sq ft / whole block → 70% within 15 ft) and (d) (articulation allowances) are not mentioned. Almost certainly inapplicable to this small corner lot, but a one-line "considered; (c) inapplicable by lot size" would complete the reading.

## What I could not check
- The E15 HTTP `Last-Modified: 2025-12-01` header and the 2026-10-10 live DCM fetch (past events); verified the saved file content + SHA instead.
- Verbatim ZR 12-10 'street, narrow'/'street, wide' text (live page truncates, as the record states; not captured). The classification rests on DCM widths + owner-approved D-052, which is the record's documented posture — acceptable for a draft; residual correctly left unresolved with a print/PDF-capture next step.
- The adjacency "prevailing street wall frontage" fact and the operative street-line positions (correctly left unresolved with next steps).
- Legal correctness of the cross-reference chain is a professional (ADR-007/G6) matter, not this gate; the record ships as a labelled unreviewed draft.

Record is structurally sound, provenance-complete, answers correct, unresolved items honestly preserved. Acceptance should be conditioned on correcting Finding 1 (conditions[0]); Findings 2–3 are advisory.

## Review entry (for the orchestrator to add)
{"reviewer": "data-contract-verifier", "date": "2026-10-11", "reviewed_revision": 1, "verdict": "partly_agrees", "findings": ["REQUIRED: conclusion.conditions[0] names '35-631(a) line-up' as the fallback when the record establishes 35-631(a) is inapplicable to R6B Queens; the 35-631(b) closing-clause fallback is to 23-431(a). Same condition glosses 'prevailing street wall frontage' with the 23-431(a) eligible-adjacent-building test (15/25/35 ft) instead of its ZR 12-10 definition (150-ft selection, within 2 ft of average distance, aggregate >=100 ft); correct the gloss and/or cite zr-12-10-prevailing-street-wall-frontage.", "ADVISORY: E15 excerpt/observed_facts list 3 of 6 features the envelope query returned (omits '45 Road' w=50 and duplicate '215 Street' segments) while reading as exhaustive; label it a selection of the relevant frontages.", "ADVISORY: street-wall reading omits 35-631(c) large-zoning-lot and (d) articulation allowances; add a one-line note that (c) is inapplicable by lot size.", "Verified independently: all 15 evidence SHA-256 match (LF-normalized); research_record_check.py --check exits 0; R6B 23-432 row 30/45/55; Q1 35-631(b) 8-ft-each-frontage, Q2 no setback at/below 45-ft max base, Q3 no side yard required (23-335(b)/34-232) all correct and sourced; ZR 12-10 street-width definitions genuinely uncaptured and live page truncation reproduced; status interpretation_awaiting_review with no label requested."]}

END-OF-REPORT
