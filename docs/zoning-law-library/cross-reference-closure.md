# Cross-reference closure — how the traversal ran

**Unreviewed draft (ADR-007).** This is the documents-only traversal that produced
`benchmark-r6b-sections.json`. It is not the cross-reference *closure engine* (that is the still-backlog
code task M3-T004); it is a bounded manual catalog for the R6B / C2-2 benchmark and the eleven options.

## Method

1. **Start set from the rules.** Read every R6B-applicable ruleset under
   `services/api/app/rules/rulesets/` and took the sections each formally cites in its `citations[]`
   array (the authoritative "what this rule rests on"). The R6B-applicable rulesets and their formal
   citations are:
   - `r6_r12_residential_far` (applicability `in_set` includes R6B) → 23-22
   - `r6b_qualifying_housing_far` → 23-22
   - `r6b_height` → **23-432 only** (see the correction below)
   - `r6b_lot_coverage` → 23-362, 11-25
   - `r6b_rear_yard_corner_waiver` → 23-344(a), 11-25
   - `r6b_dwelling_units` → 23-52, 23-52(b), 11-25
   - `r6_r7_r8_wide_street_conditional_far` applies to `[R6, R7-1, R7-2, R8]` — **not** R6B; its 23-22
     citation is reached through the R6B rules anyway, so 23-22 stays in the start set.
2. **Start set from the benchmark reading.** Added the sections the benchmark evidence records cite:
   NB-03 (rear yard, 23-342/23-344) and NB-06 (street wall / setback / side yard — 23-431, 23-432,
   23-433, 23-335, 34-11, 34-24, 34-232, 35-01, 35-63, 35-631, 35-632).
3. **Followed cross-references** from the captured verbatim text, tables, and footnotes of each in-scope
   section (as read in the snapshot files), level by level, until each branch was either captured and in
   scope, captured and out of scope (with a reason), or NOT CAPTURED (recorded, never silently dropped).
4. **Added the options frontier.** Added the sections the eleven development options need (from the H6
   return, re-checked against the snapshot folder): commercial use (32-131, 32-161), overlay/commercial
   FAR (33-12, 33-121, 35-30 to 35-33), parking + transit zone (25-xx, 66-11, Appendix I), community
   facility (24-11, 24-111 — NOT CAPTURED), UAP (23-154 — NOT CAPTURED), shared housing (sections
   unresolved), and the split-lot family (36-64 captured; 77-00 NOT CAPTURED).
5. **12-10 defined terms** the sections rely on are tracked in the `defined_terms` list, not as
   cross-reference edges, because they are definitions rather than numbered-section references.

## Correction to a helper summary (checked, not copied)

The H6 return said `r6b_height.rule.json` handles 23-431, 23-432 and 23-433. The producer read the rule
file directly: its `citations[]` names **23-432 only**, and its `computation` emits only the 23-432
height-table values (min/max base height, max building height). 23-431 (street-wall location) and 23-433
(setback depth) are mentioned in the rule's prose and `special_district_interactions` as context but are
**not** formally cited and **not** computed. They are therefore recorded as **NOT HANDLED** (coverage
`not_evaluated`), with a note that r6b_height references them. The benchmark three-storey / 30-ft option
sits at the minimum base height, so the 23-433 setback is not triggered there; the rule still does not
compute it.

## Confirmed discrepancy (recorded, not edited)

NB-06 revision 2 (search S3; evidence lines) records ZR 12-10 "street, wide" / "street, narrow" as **not
captured** in the repository snapshot set. The producer checked `zr-12-10.snapshot.json` directly: its
`section_title` is "Definitions - wide street and narrow street", it contains the "wide"/"narrow"/"75
feet" text and the 2026-03-26 "wide" amendment, digest
`23a9ccad31f1081fd15de94d796c22d540e7e8bcfe986e64c9ba302bf8fa4fde`, last amended 2026-03-26. **The text
IS captured.** NB-06's claim is stale at this commit (the likely cause: NB-06 searched for a
hyphenated-term filename, but the wide/narrow text sits in the plain `zr-12-10.snapshot.json`). NB-06 is
read-only for this task and is **not** edited here; the discrepancy is logged in `research-log.md` for the
orchestrator.

## What was followed vs out of scope

- **Followed** (captured, in scope): the R6-R12 FAR / height / setback / street-wall / rear-yard / lot-
  coverage chain (23-20, 23-22, 23-34, 23-341/342/343/344, 23-362/363, 23-41x, 23-43x, 23-52, 23-62,
  23-335), the C-overlay residential-bulk chain (34-11, 34-21/22/23/231/232/233, 34-24, 34-111), the
  Chapter-5 R6-R12-equivalency chain (35-01, 35-63, 35-631/632/633), and the options frontier above.
- **Terminal** (captured, no further in-scope numeric reference): 11-25, 23-22, 23-52, 23-34, 23-311,
  23-411, 23-434, 23-335, 34-111, 34-231, 34-233, 35-01.
- **Out of scope** (captured, but the district line or body excludes an R6B / C2-2 lot — reason recorded
  per entry): 23-42 (R1-R5 height), 23-435 (towers R9-R12), 34-112 (C1-6+/C2-6+/C3-C6), 34-113
  (previously-bonused lots), 35-62 (R1-R5 equivalency), 23-44 and 35-64 (special geographic areas —
  title-only capture; coverage stays `not_evaluated`, not `not_applicable`, because applicability to a
  mapped special area is not affirmatively resolved), 35-53 (pre-Dec-2024 mixed-building rear-yard
  numbering), 36-64 (district-boundary split — relevant to option 8 only under one reading).
- **NOT CAPTURED, out of scope** (referenced but not needed for an R6B / C2-2 lot): 23-361 (R1-R5 lot
  coverage), 23-425 (R1-R5 height), 25-621 / 25-622 / 25-85 (accessory parking/loading obstructions),
  26-50, 23-613 (planting-strip detail), 23-30 / 23-63 (balcony/yard cross-refs), 37-727 / 37-73 /
  74-761 (floor-area-bonus provisions). Also referenced only in rule prose (not captured): 23-38, 23-51,
  23-70, 23-72.
- **NOT CAPTURED, in scope / needed by an option** (recorded as `missing`): 24-11, 24-111 (community
  facility), 23-154 (UAP), 77-00 (split-lot alternative reading), and the shared-housing use/standards
  sections (section numbers unresolved).

## Reproduce

`benchmark-r6b-sections.json` is generated so that every capture claim is read straight from the snapshot
folder. The producer's capture-claim check (`verify_captures.py`, kept as a scratch tool, output in the
producer report) confirms every captured entry's snapshot id and digest equal the snapshot file's, and
every NOT CAPTURED entry has no snapshot file.
