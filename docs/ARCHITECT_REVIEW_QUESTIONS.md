# Questions to check with the architect / zoning professional

**Owner's running list.** Started 2026-09-13 (owner directive D-048). This document collects every
question the platform deliberately refuses to answer itself — legal-text interpretations, professional
judgment calls, and product-validation questions. Take it to your architect or zoning consultant;
bring the answers back, and they get captured as directives / qualified rulings. The build never
guesses at any of these in the meantime — affected items show **"not assessed — needs professional
review"** on screen until answered.

How to use it: each question has (1) the plain-English question, (2) the exact citation for the
professional, and (3) what it unlocks in the product. Questions are append-only; answered ones get
marked with the answer and the directive that captured it.

---

## A. Legal-text interpretation questions (currently blocking coverage)

### A1. Do ZR 23-421's bare "R1" and "R2" labels include the lettered variants? — OWNER RESEARCH SAYS YES (via ZR §11-25); PENDING PROFESSIONAL CONFIRMATION

- **Plain English:** The zoning rule for single-family house heights (pitched-roof: 25 ft walls /
  35 ft ridge) lists the districts it applies to. For R3 and R4 it names variants explicitly
  (R3A, R3X, R3-1, R3-2, R4-1, R4A — though NOT R4B, which has its own flat-roof provision in
  §23-422; questionnaire correction 2026-09-13 from owner research). For R1 and R2 it says just
  "R1" and "R2." Do those bare labels legally sweep in R1-1, R1-2, R1-2A, R2A, and R2X — or do
  those variants have their own (or no) height rules?
- **Owner's researched reading (2026-09-13, current official text; NOT a qualified sign-off):**
  YES — ZR **§11-25** is the Resolution's own interpretation rule: "All regulations applicable to
  a district designation shall be applicable to such district designation appended with a suffix,"
  subject to express exceptions elsewhere, and it illustrates with R4-1/R4A/R4B. Applied to
  §23-421: R1 includes R1-1/R1-2/R1-2A; R2 includes R2/R2A/R2X — all within the basic 25/35
  envelope, subject to building-type scope and applicable modifications.
- **Text verified against zr.planning.nyc.gov (companion session, 2026-09-13):** §11-25 quote
  CONFIRMED VERBATIM ("…except as otherwise set forth in express provisions of this Resolution"),
  examples R4/R4-1/R4A/R4B + C4-6/C4-6A, last amended 6/29/1994 (predates City of Yes). §23-424
  CONFIRMED: "Height and setback requirements for qualifying residential sites" table lists
  R1-1, R1-2, R1-2A, R2, R2A, R2X at 35 ft base / 35 ft max (R4s 35/45, R5s 45/55). §23-21
  CONFIRMED in substance: R2X = FAR 1.00 (own row), R2/R2A = 0.75 (row shared with
  R3A/R3X/R3-1/R3-2), and R2/R2A rise to 1.00 on qualifying residential sites. What the
  professional still confirms: the APPLICATION of §11-25 here (the express-exceptions caveat).
- **§23-421(g) — OWNER-VERIFIED VERBATIM (2026-09-13, second research pass):** the full paragraph
  renders on the official mirror. Quoted sentence: "the reference plane for applying the
  regulations of this Section may be located up to five feet above the base plane." Conditions
  (either suffices), for R1/R2 districts WITHOUT a letter suffix: (1) zoning-lot area ≥9,500 sq ft
  AND width ≥100 ft; or (2) slope ≥5% measured between street-wall-line level and rear-wall-line
  level. Owner's suffix reading: numerical suffixes (-1, -2) are distinct from letter suffixes
  (A, X), so R1-1/R1-2/R2 are eligible; R1-2A/R2A/R2X are not. Reproduction recipe: open the
  official §23-421 page and search "9,500" — text extractors show paragraph (g) as item 7.
  TOOLING NOTE (for the professional and the build): the companion session's HTML extraction
  could NOT render this paragraph on two official mirrors across four attempts — the zr site's
  HTML render loses §23-421(g) in text extraction. The rules pipeline must prove section
  completeness from an artifact that provably contains the full text (e.g. the print/PDF render),
  never from HTML extraction alone. The architect can eyeball the paragraph in seconds via the
  link. CORROBORATION (2026-09-13): the original rules producer's preserved source-facts memory
  (.claude/agent-memory/rules-engineer/zr-r1-r2-height-setback-source-facts.md, captured live the
  same day via a different extraction path) records identical figures — "In R1 and R2 Districts
  without a letter suffix", ≥9,500 sq ft & ≥100 ft width OR ≥5% slope, reference plane up to 5 ft
  above base plane — so the owner's verbatim now has an independent in-repo witness.
- **Citation for the professional:** ZR §23-421 (City of Yes text, last amended 2024-12-05,
  verified live at zr.planning.nyc.gov on 2026-09-13). Applicability line reads:
  "R1 R2 R3A R3X R3-1 R3-2 R4 R4-1 R4A R5A". §23-422 (flat-roof alternative) excludes R1/R2.
  No captured governing height/setback section names R1-1, R1-2, R1-2A, R2A, or R2X.
- **Why we didn't assume:** the FAR table (ZR §23-21) treats R2X *differently* from R2/R2A —
  R2X is grouped with R4 at FAR 1.00 while R2/R2A sit at 0.75 — so "the variants inherit the
  group rule" is demonstrably not always true.
- **Product impact until answered:** lots mapped R1-1, R1-2, R1-2A, R2A, or R2X show height/setback
  as "not assessed — needs professional review." (Most real R1 lots are mapped R1-1/R1-2, so this
  affects most R1 lots.) Bare R1/R2 lots are covered.

### A2. Does R2X share the 25/35 ft pitched envelope, or does it have its own? — OWNER RESEARCH SAYS SHARED; PENDING PROFESSIONAL CONFIRMATION

- **Plain English:** If the answer to A1 is "yes, variants are included," R2X still needs its own
  confirmation — it's a higher-density district that the floor-area table already treats
  differently. Same envelope, or different?
- **Citation:** ZR §23-421 vs §23-21 (R2X grouped with R4 at FAR 1.00; R2/R2A at 0.75).
- **Owner's researched reading (2026-09-13; NOT a qualified sign-off):** R2X SHARES the 25/35
  envelope. §23-21's separate FAR row is an express exception concerning floor area only — it does
  not import R4's other regulations. Height remains determined through §§11-25 + 23-421.
- **Product impact:** R2X lots' height/setback stays "not assessed" until confirmed.

### A3. Does any other ZR section give R2A, R2X, or R1-2A a distinct height/setback envelope? — OPEN

- **Plain English:** A completeness check: we searched the captured governing sections (23-42,
  23-421, 23-422, 23-44/441/442, 21-11) and found none — but "we didn't find one" is not the same
  as "there isn't one." Please confirm.
- **Owner's research found REAL site-specific modifiers (2026-09-13; needs the qualified
  answer):** the basic envelope is shared, but these provisions can change it for particular
  sites — the professional should confirm this list is right and complete:
  - **§23-421(g)** — reference plane may rise up to 5 ft above the base plane in R1/R2 districts
    WITHOUT a letter suffix (per its wording: R1-1, R1-2, R2 eligible; R1-2A, R2A, R2X excluded),
    when the lot is ≥9,500 sq ft with ≥100 ft width, OR street-to-rear slope ≥5%.
  - **§23-424** — "qualifying residential site": expressly lists R1-1, R1-2, R1-2A, R2, R2A, R2X
    with 35 ft max base height / 35 ft max building height + referenced setbacks. NOTE: the
    ordinary transit-proximity qualifying route excludes R1/R2; other routes (e.g. the
    community-facility floor-space condition as of 2024-12-05) can include them — the §12-10
    "qualifying residential site" definition must be evaluated, never assumed.
  - **§23-425** — eligible large sites: applies §23-424 heights + conditional increase tied to
    existing roof heights / ornamental features.
  - **§23-426(a)** — LPC-designated Historic Districts: conditional base-height modification
    involving an adjacent building's height.
  - **§23-443(b)** — transportation-infrastructure-adjacent frontage: +10 ft maximum-height
    increase in R1–R6 for the described multiple dwellings.
  - **§119-212** — Special Hillsides Preservation District Tier II sites: separate control,
    R1/R2 at 36 ft, pitched roofs measured to midpoint.
  - **§113-523** — Special Ocean Parkway subdistrict: modifies §23-421's envelope geometry
    (apex points above perimeter walls).
  - Also noted: §23-421 permits setbacks within its sloping planes (a pitched-roof envelope is
    not a pitched-roof requirement), and rooftop obstructions carry their own limits (§23-413(a)).
- **Product impact:** closes the loop on A1/A2; on the ruling, the R1/R2 rule family is finished
  and every R1/R2-variant lot gets a real draft envelope — with the modifiers above encoded as
  conditions or review flags, never silently.

*Owner's research disposition note (2026-09-13): the researched reading above supports encoding
the shared basic envelope with precise applicability conditions while retaining review status
wherever eligibility, special-district rules, or another material modifier is unresolved. It is
explicitly NOT a qualified sign-off, NOT an owner decision, and does NOT clear G6.*

---

## B. Standing professional-review items (the G6 conversation)

1. **The big one — qualified legal review of the draft rule families (gate G6).** Every zoning
   number the platform produces is DRAFT until a qualified professional reviews the rule families
   (residential FAR R1–R12; R5-family height/setback; each new family the current build campaign
   adds). This is the single step that most changes what the product is worth. The A-section
   questions above are concrete openers for this same conversation.
2. **The tax-lot = zoning-lot assumption.** The platform treats the selected tax lot as the whole
   zoning lot (ZR §12-10 says they can differ when recorded agreements merge lots). Every result
   states this assumption. Question for the professional: is the on-screen wording the right
   professional framing, and what's the cleanest signal they'd want when a merger is suspected
   (today: an over-built-vs-own-FAR clue plus a review flag)?

---

## C. Product-validation questions (for the architect demo)

1. **Number-first vs map-first:** results currently lead with the headline number and its honest
   scope line; the map is subordinate. Watch a real architect on their own lot — do they look for
   the number or the map first?
2. **The honest labels:** does "not assessed — needs professional review" read as trustworthy
   or as unfinished? (Design rule: if a user calls a DRAFT result "approved," the design failed.)
3. **The report page:** page 1 is the decision summary (answer, formula, warnings). Is anything
   missing that they'd need before showing a client?

---

*Maintained under directive D-048. New interpretation questions from the build campaign are appended
here automatically instead of stopping the build each time; genuine contradictions still stop.*
