# M5-T160 producer report — NB-06 street wall / setback trigger / side yard

**Producer:** official-source-researcher (Claude Code session 01TpXJN7)
**Date:** 2026-10-11
**Property:** 215-16 Northern Boulevard, Queens (borough 4, block 7334, lot 70; BBL 4073340070; R6B with a C2-2 overlay; corner of Northern Boulevard and 215 Place)
**Worktree:** /root/project/nyc-buildability/.claude/worktrees/agent-a1241e605bb34f895
**Contract head reset to:** c8215a33d0cd7e6c1ae60721843f39bfc4867126 (`Wave 23: G0 PASS for M5-T160 at its contract head`)

Research and verification (D-093) followed: `.claude/rules/research-and-verification.md` and
`docs/RESEARCH_AND_VERIFICATION.md` read in full; affected records NB-03 and NB-04 read; primary
sources (the repository ZR snapshots and the owner-research evidence pack) opened directly, not the
brief's summary. All unresolved inputs kept unresolved in the record.

## Files changed (allowed paths only)
- `docs/research/evidence-records/NB-06-street-wall-setback-side-yard.json` (new; `research_record/v1`)
- `docs/research/evidence-records/README.md` (one Records-table row for NB-06)
- `project-control/reports/M5-T160-producer-report.md` (this report)

Not touched: any other evidence record, `docs/RESEARCH_REQUESTS.md`, `docs/DISCOVERY_BACKLOG.md`,
or any code (all outside allowed paths).

## The three answers (plain words), status: interpretation_awaiting_review (labelled unreviewed draft, ADR-007)

**Q1 — street wall.** The C2-2 overlay changes the street-wall rule. For a MIXED building
(residential + the overlay's commercial use) ZR 35-01 applies Article III Chapter 5 directly; for a
RESIDENTIAL-ONLY building ZR 34-11 applies Article II Chapter 3 "except as modified by ... 34-24",
and 34-24(b)(1) "shall" apply the Section 35-63 (inclusive) modifications for an R6–R12 equivalency
(35-01's closing cross-reference sentence contemplates this). Both pathways reach 35-63, under which
the street-wall location "shall be as set forth in Section 35-631". R6B is not an R8–R12 Manhattan
Core district, so 35-631(a) line-up does not apply and **35-631(b)** governs: at least 70% of the
aggregate street-wall width on each frontage within **8 ft** of that street line, extending to at
least the 30 ft minimum base height (or the building height, whichever is less); up to 30% may
recess, with recesses deeper than 10 ft on Northern Boulevard (wide) or 15 ft on 215 Place (narrow)
placed in an outer court. The exact position within (b) stays **conditional** on whether the block
has a "prevailing street wall frontage" further from the street line (then the 23-431(a) line-up may
be applied) and on the operative street-line position (a mapped width does not fix it). This directly
addresses backlog **DB-099**, whose premise "no Article III snapshot" is now outdated; the captures
support the overlay changing street-wall placement even for a residential-only building.

**Q2 — setback.** No setback is required for a building at or below the maximum base height. Both the
residence-district chain (23-432 → 23-433) and the overlay chain (35-632(a) → 23-433) require a
setback only for the portion of a building street wall that **exceeds the maximum base height
(45 ft for R6B standard residences)**. The benchmark three-storey **30 ft** option equals the
minimum base height and is below 45 ft, so none is triggered. The street-width class (D-052: Northern
Boulevard 100 ft = wide, 215 Place 60 ft = narrow) decides only the **depth** of a setback that would
apply above 45 ft (10 ft from a wide-street wall, 15 ft from a narrow-street wall) — it is not the
condition for whether a setback triggers at or below the max base height.

**Q3 — side yards.** Not required. Under ZR 23-335(b) a side yard is not required for any residence
other than a single/two-family detached; the overlay ZR 34-232 removes the side-yard requirement for
ANY residential building. A side yard is permitted (optional); any open area along a side lot line
must be at least 5 ft wide. Only a single/two-family detached residence would need two 5-ft side
yards under 23-335(a), and even that is removed by 34-232 in the overlay. A side yard is not
prohibited.

## Sources (all opened; snapshot sha256 = LF-normalized hash of the saved snapshot file)

| Evidence | Reference | saved_copy | sha256 | retrieved |
|---|---|---|---|---|
| E1 | ZR 12-10 street wall | zr-12-10-street-wall.snapshot.json | 9996f2941ad3aa7b… | 2026-10-07 |
| E2 | ZR 12-10 corner lot | zr-12-10-lot-corner.snapshot.json | 9f0d18ea0bf1064b… | 2026-10-07 |
| E3 | ZR 12-10 mixed building | zr-12-10-mixed-building.snapshot.json | 8f9e9381d4103307… | 2026-10-07 |
| E4 | ZR 23-431 street wall location | zr-23-431.snapshot.json | 2baef4dba3ada0bd… | 2026-10-04 |
| E5 | ZR 34-11 general provisions | zr-34-11.snapshot.json | 2e9d1b6a5b5c80de… | 2026-10-07 |
| E6 | ZR 34-24(b)(1) | zr-34-24.snapshot.json | ea58695d327b3f0f… | 2026-10-07 |
| E7 | ZR 35-01 applicability | zr-35-01.snapshot.json | 9554360d527ed838… | 2026-10-07 |
| E8 | ZR 35-63 | zr-35-63.snapshot.json | 3d3cde2757748 4bf… | 2026-10-07 |
| E9 | ZR 35-631 street wall (overlay) | zr-35-631.snapshot.json | 6d4f7c08487deaea… | 2026-10-07 |
| E10 | ZR 23-432 base-height table | zr-23-432.snapshot.json | 37c1414c2f1fb934… | 2026-09-30 |
| E11 | ZR 23-433 standard setback | zr-23-433.snapshot.json | 8dcd40b805399 2c0… | 2026-10-04 |
| E12 | ZR 35-632(a) overlay heights | zr-35-632.snapshot.json | b2f0bfc988073 5f8… | 2026-10-07 |
| E13 | ZR 23-335 side yards | zr-23-335.snapshot.json | 17698b050f9ee1b7… | 2026-10-07 |
| E14 | ZR 34-232 overlay side yard | zr-34-232.snapshot.json | 21c8c429183185da… | 2026-10-07 |
| E15 | DCM Street Center Line widths | owner-research/2026-10-10-…/data/dcm_street_centerline_lot_envelope_4073340070.json | 3fad815e5954fe77… | 2026-10-10 |

(Full 64-hex digests are in NB-06; the check verifies each against the saved file.) URLs: all on
`zoningresolution.planning.nyc.gov` for E1–E14; E15 is the `DCM_Street_Center_Line` ArcGIS
FeatureServer query. All ZR sections last amended 2024-12-05 except the 12-10 definitions (street
wall 1961-12-15, corner lot 1965-05-20, mixed building 2011-02-02). Street-width policy: D-052
(`project-control/directives/D-052-street-width-draft-classification/`): below 75 ft narrow, 75 ft or
above wide.

## What stays unresolved, and the exact next step for each
1. **ZR 12-10 "street, narrow"/"street, wide" verbatim text is not captured.** The live 12-10 fetch
   on 2026-10-11 truncated before the street definitions; a domain-scoped search returned only a
   paraphrase (narrow <75 ft, wide ≥75 ft) consistent with D-052. The classification (Northern
   100 ft = wide, 215 Place 60 ft = narrow) meanwhile rests on the DCM widths + D-052. **Next:**
   capture 12-10 'street, narrow'/'street, wide' via the print/PDF channel (browser UA, sha-pin) and
   add to the snapshot set. (Repository notes a 2026-03-26 amendment to 'street, wide'.)
2. **35-631(a) line-up vs 35-631(b) percentage** — depends on whether either frontage has a
   "prevailing street wall frontage" further from the street line. **Next:** an adjacency survey /
   field review in the placement step.
3. **Operative street-line position** — the 8-ft measure and any setback depth run from the street
   line, which the mapped width does not fix. **Next:** the approved plan or a certified survey.
4. **Residential-only vs mixed pathway** — both reach 35-631(b) here, but the record keeps the two
   pathways explicit for the G1 reviewer to check the 34-11 → 34-24(b)(1) → 35-63 chain.
5. **DB-099 backlog** — its "no Article III snapshot" premise is now outdated; the backlog edit is
   the orchestrator's (outside this task's allowed paths).

## Self-check (S4)
`python3 tools/research_record_check.py --check` → **PASS**, exit 0. NB-06 line:
`status=interpretation_awaiting_review  code_current=True  review_state=none  requested_label=None`.
All six records structurally valid; no Verified label requested.

## Limitations
A reading of the law is an unreviewed draft (ADR-007); this record certifies nothing and is not a
DOB determination. No independent review is recorded (`review.agent_reviews` empty — the G1 reviewer
adds it later through the orchestrator). No professional verification.

---

## Revision 2 (2026-10-11) — G1 review corrections

Applied on the integrated head 2bbfed94311cd40ecb07f836590dd4413870099a. NB-06 `revision` -> 2,
`last_changed` 2026-10-11; `review.agent_reviews` left empty (the orchestrator adds reviews).

1. **REQUIRED (conclusion.conditions[0]).** (a) The fallback named was wrong: 35-631(a) line-up does
   not apply to this R6B Queens site; the fallback in 35-631(b)'s closing clause is the **23-431(a)**
   line-up. Reworded the condition to say the 35-631(b) percentage rule governs unless its closing
   clause permits the 23-431(a) line-up. (b) Removed the gloss that defined "prevailing street wall
   frontage" with the 23-431(a) eligible-adjacent-building test (15 ft / 25 ft / over 35 ft).
   Replaced it with the ZR 12-10 defined term and added **E16** (`zr-12-10-prevailing-street-wall-frontage`
   .snapshot.json, LF sha256 `0bef4080835cc1535bc0c01fb6919056335fcb0d43bcd5816f88d458e108469f`,
   last amended 2024-12-05, retrieved 2026-10-07), also added to `provisions_read`. The 15/25/>35-ft
   test is now kept only where it is actually the 23-431(a) eligibility test.
2. **ADVISORY (E15 / observed facts).** The envelope query returned 6 features; relabelled the listed
   widths as a selection of this lot's frontages (Northern Boulevard, 215 Place), noted 215 Street
   (and 45 Road) are not frontages of this corner lot, and that the list is not exhaustive. Same
   wording carried into the DCM observed-facts bullet.
3. **ADVISORY (exceptions_considered).** Added one line for 35-631(c) (large zoning lots / whole
   block: inapplicable — lot 70 is about 10,075 sq ft, under the 40,000 sq ft test quoted, and does
   not occupy the block) and one for 35-631(d) (articulation allowances: 12-inch general, up to 50%
   of aggregate street-wall width at up to 3 ft, no projection past the street line except per the
   Admin Code).

Self-check: `python3 tools/research_record_check.py --check` -> PASS, exit 0. NB-06 line:
`status=interpretation_awaiting_review  code_current=True  review_state=none  requested_label=None`.
(Observed: NB-05 now reports `review_state=stale` — this derives from the orchestrator's integration
commit 2bbfed94, not from this edit; NB-05 is outside this task's allowed paths. Staleness is
reported, not failed; the check still passes.)

END-OF-REPORT
