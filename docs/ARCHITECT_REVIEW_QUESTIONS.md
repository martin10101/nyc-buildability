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

### A1. Do ZR 23-421's bare "R1" and "R2" labels include the lettered variants? — OPEN

- **Plain English:** The zoning rule for single-family house heights (pitched-roof: 25 ft walls /
  35 ft ridge) lists the districts it applies to. For R3 and R4 it names every lettered variant
  explicitly (R3A, R3X, R3-1, R3-2, R4-1, R4A). For R1 and R2 it says just "R1" and "R2." Do those
  bare labels legally sweep in R1-1, R1-2, R1-2A, R2A, and R2X — or do those variants have their own
  (or no) height rules?
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

### A2. Does R2X share the 25/35 ft pitched envelope, or does it have its own? — OPEN

- **Plain English:** If the answer to A1 is "yes, variants are included," R2X still needs its own
  confirmation — it's a higher-density district that the floor-area table already treats
  differently. Same envelope, or different?
- **Citation:** ZR §23-421 vs §23-21 (R2X grouped with R4 at FAR 1.00; R2/R2A at 0.75).
- **Product impact:** R2X lots' height/setback stays "not assessed" until confirmed.

### A3. Does any other ZR section give R2A, R2X, or R1-2A a distinct height/setback envelope? — OPEN

- **Plain English:** A completeness check: we searched the captured governing sections (23-42,
  23-421, 23-422, 23-44/441/442, 21-11) and found none — but "we didn't find one" is not the same
  as "there isn't one." Please confirm.
- **Product impact:** closes the loop on A1/A2; on the ruling, the R1/R2 rule family is finished
  and every R1/R2-variant lot gets a real draft envelope.

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
