# Three NYC zoning questions: R6B lot with a C2-2 overlay

> **For the owner:** paste this whole file into the other AI, then paste its answer back to Claude.
> Another AI's answer is a second opinion, not a licensed sign-off. The app keeps showing
> these numbers as "Draft — not reviewed" until a qualified professional confirms them.

---

## Instructions for the AI answering

You are checking three readings of the **New York City Zoning Resolution (ZR)**, as amended through
12/5/2024 ("City of Yes for Housing Opportunity"). For each question:

1. Answer **Yes / No / Depends**, then explain in a few sentences.
2. **Quote the exact ZR text** you rely on, with the section number. If you can read the official
   text at https://zr.planning.nyc.gov, quote it from there. If you cannot check the current text,
   say so. Do not quote from memory as if it were verbatim.
3. Say **what is uncertain** and what a licensed architect or zoning attorney should confirm.
4. Do not guess numbers. If a value depends on facts not given here, say which facts.

The quoted ZR text below comes from snapshots the app captured in September 2026. Snapshots are
missing for some sections; those are marked **(no snapshot)**.

## The lot

- **Address:** 215-16 Northern Boulevard, Queens (BBL 4073340070, tax lot 70), about 100.8 × 100 ft.
  It is a corner lot, on Northern Blvd and 215th Place.
- **Zoning:** an **R6B** residence district with a **C2-2** commercial overlay.
- **Zoning lot:** the Department of Buildings records this lot as one zoning lot together with tax
  lot 1 (DOB job 421803891). The numbers below are for tax lot 70 alone; combining the two lots is
  handled separately.
- **The app's current draft results** for this lot:
  - maximum residential floor area 20,150 sq ft, or 24,180 sq ft with qualifying affordable housing;
  - height limits 30 / 45 / 55 ft, or 45 / 65 ft with the qualifying option;
  - lot coverage 100% (corner lot);
  - no rear yard required (corner-lot waiver);
  - 29 dwelling units.

---

## Question 1: Do R6–R12 rules reach R6B through ZR 11-25?

Three rules the app applies to R6B come from sections whose district list says "R6 … R12" and does
not name R6B. The app assumes they reach R6B only through ZR 11-25.

**ZR 11-25** (snapshot; last amended 6/29/1994):
> "All regulations applicable to a district designation shall be applicable to such district
> designation appended with a suffix, except as otherwise set forth in express provisions of this
> Resolution. If a section lists an R4 District, therefore, the provisions of that section shall also
> apply to R4-1, R4A and R4B Districts, unless separate provisions for the districts with suffixes
> are listed within such section."

The three rules that depend on it:

| App rule | ZR section (district line in the snapshot) | Quoted text (snapshot, last amended 12/5/2024) | What the app does for this lot |
|---|---|---|---|
| Lot coverage | **23-362** ("R6 R7 R8 R9 R10 R11 R12") | "(a) … the maximum #residential# #lot coverage# for #interior lots# or #through lots# shall be 80 percent and the maximum #residential# #lot coverage# for #corner lots# shall be 100 percent." | 100% coverage (corner lot) |
| Corner rear-yard waiver | **23-344** ("R1 … R12") | "(a) … no #rear yard# shall be required within 100 feet of the point of intersection of two #street lines# intersecting at an angle of 135 degrees or less." | No rear yard |
| Dwelling units | **23-52** | "(b) … the applicable #dwelling unit# factor shall be 680. Fractions equal to or greater than three-quarters resulting from this calculation shall be considered to be one #dwelling unit#." | 29 units |

**Snapshots missing:** 23-342, 23-343 and 23-363. Any of these could hold separate R6B provisions.

**Questions:**
- **1a.** Does 23-362's 80% / 100% coverage apply to R6B through 11-25? Or does another section,
  such as 23-363, set separate coverage for R6B? Quote it.
- **1b.** Does 23-344(a)'s corner-lot rear-yard waiver apply in R6B? The line names R1…R12, so
  the question is whether any R6B-specific provision overrides it.
- **1c.** Does the 23-52 dwelling-unit factor of 680 apply to R6B? If R6B has a different factor,
  quote it.
- **1d.** Does 11-25's "except as otherwise set forth in express provisions" clause, or its
  "unless separate provisions for the districts with suffixes are listed within such section" clause,
  defeat any of 1a–1c?

**If the reading is wrong:** the 100% coverage, the rear-yard waiver and the 29 units would all be
unsupported. The 80% interior coverage rests on the same sentence.

---

## Question 2: Does the C2-2 overlay change R6B's height, coverage or yards?

**What the app assumes:** the R6B residence rules apply unchanged under the C2-2 overlay. It uses
the plan's rule "the R district's rules apply" and gives height 55 / 65 ft plus the coverage and
rear-yard results above.

**Why that is doubtful:**
- The app's own R5 height rule says the opposite: "A commercial overlay may modify residence-district
  height (section 23-44) … Professional review required."
- An earlier review flagged that ZR **34-111** and the Article III mixed-building rules were never
  checked.

**ZR text: no snapshot.** The app has no captured text for Article III (34-xx, 35-xx) or for 23-44.

**Questions:**
- **2a.** For a residential or mixed building on an R6B lot with a C2-2 overlay, which sections
  govern height and setback? Is it 23-432 (the residence-district table), or Article III
  (e.g. 35-xx for mixed buildings)? Quote the governing text.
- **2b.** Do the overlay rules change residential **lot coverage** (23-362) or **rear yards**
  (23-344) for this lot? Quote the text.
- **2c.** Is there any floor-area change for residential or mixed use under the C2-2 overlay in R6B
  compared with plain R6B? A competitor tool showed "+2.00 FAR" for the overlay; the app rejects
  that as an add-on.
- **2d.** Is ground-floor commercial use permitted here, and does it count against the residential
  floor area?

**If the reading is wrong:** the heights 30/45/55 and 45/65 would become "needs professional review",
and coverage and yard results could change.

---

## Question 3: How are "portions thereof" apportioned?

Several ZR sections apply rules to "#zoning lots#, or portions thereof, located within 100 feet of a
#wide street#". The app does not split lots by distance: if any part of the lot is within 100 ft,
it applies the wide-street row to the whole lot.

**ZR 23-22** (snapshot, last amended 12/5/2024), footnote 1:
> "For #zoning lots#, or portions thereof, located within 100 feet of a #wide street#"

The R6B row reads 2.00 / 2.40 with **no footnote**.

**ZR 23-432** (snapshot, last amended 12/5/2024):
> Footnote 1: "For #zoning lots# or portions thereof within 100 feet of a #wide street#"
> Footnote 2: "…or, for #zoning lots# with only #wide street# frontage, portions of such
> #zoning lot# beyond 100 feet of the #street line#"

The R6B row reads 30/45/55/45/65 with **no footnote**.

**ZR 23-344(c)** (snapshot; the app does not implement it yet):
> "for #interior# or #through lot# portions of #corner lots# … the portion of a #side lot line#
> beyond 100 feet of the #street line# … shall be considered a #rear lot line#"

**Snapshots missing:** 23-433 and 23-62x.

**Questions:**
- **3a.** Since the R6B rows in 23-22 and 23-432 carry no wide-street footnote, confirm that
  **street width does not change R6B floor area or height at all**. That is the app's current
  position.
- **3b.** For this corner lot, about 100.8 × 100 ft, part of the lot may lie beyond 100 ft of the
  street intersection. How does 23-344 treat that part? Does it need a rear yard, and does 23-344(c)
  turn part of a side lot line into a rear lot line?
- **3c.** For districts where the wide-street footnote does apply (e.g. R6, R7), should floor area
  be split in proportion to the lot area within 100 ft? The app currently applies the higher row to
  the whole lot. Quote the rule that says how.

---

## Answer format (please fill in)

| # | Answer (Yes / No / Depends) | Governing ZR section(s) | Exact quote | Confidence | What a licensed professional must confirm |
|---|---|---|---|---|---|
| 1a | | | | | |
| 1b | | | | | |
| 1c | | | | | |
| 1d | | | | | |
| 2a | | | | | |
| 2b | | | | | |
| 2c | | | | | |
| 2d | | | | | |
| 3a | | | | | |
| 3b | | | | | |
| 3c | | | | | |
