# Lead for step P2: Article III sections for a residential building in a C1/C2 overlay

**Who wrote this:** an AI research helper (role: official-source-researcher). Not a lawyer, not a reviewer.
**Date:** 2026-10-07.
**A LEAD, NOT A CAPTURE:** every text below must be read again at the official source by the capture
task. Nothing here is a capture, a digest-pinned snapshot, or an interpretation of what any text means
for any lot. No number is derived.

**Source used:** only the official NYC DCP Zoning Resolution portal,
`zoningresolution.planning.nyc.gov`, HTML channel, one page at a time with a browser user-agent.

**What I could NOT read / did not do:**
- I did **not** fetch the print/PDF channel (`…/entityprint/pdf/node/<id>`) for any section. I only read
  the HTML page. Each node id below is taken from that page's own `shortlink` (and, where shown, the
  amendment-popup `data-content-nid`, which matched). The capture task must fetch and byte-pin the
  print/PDF itself and confirm the node id resolves.
- I did **not** open the further sections listed in list 6 (34-11, 35-62, 35-63, 36-64, 35-71, and the
  Article II / defined-term targets). They are pointers only, marked "not checked further."
- The paragraph lettering (a)/(b)/(c) is **rendered by the portal as ordered-list items**, not as literal
  "(a)" text in the body for 34-111 and 35-632; I confirmed the letters from the list structure plus the
  internal cross-references the text makes to its own paragraphs. The capture task should confirm the
  exact letter rendering at the source.

**Already-captured Article III sections:** none. The existing snapshot store
(`docs/research/zr-snapshots/v1/`) holds only Article I (11-23, 11-25, 12-10), Article II (23-xx) and
Article V (54-xx). No 34-xx or 35-xx snapshot exists, so none of the five below has been captured before.

---

## ZR 34-111

1. Address: `https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-111` (Article III,
   Chapter 4). Print node: **18311** (`…/entityprint/pdf/node/18311`, not fetched by me). HTML read:
   HTTP **200**, **74,800 bytes**, **2026-10-07T03:55Z**.
2. Title as shown: **"Residential bulk regulations in C1 or C2 Districts whose bulk is governed by
   surrounding Residence District"** (the page renders it "Cl or C2" — a font/glyph artifact for "C1").
   Stamp as shown: **"Last Amended 12/5/2024"**.
3. Shape: short (~800 characters), no table. An opening district list — **C1-1 C1-2 C1-3 C1-4 C1-5 C2-1
   C2-2 C2-3 C2-4 C2-5** — then a stem ("the bulk regulations for the Residence District within which
   such Commercial Districts are mapped apply, except that:"), then a 2-item ordered list ((a) qualifying
   residential sites in the Greater Transit Zone mapped in R1–R5 → R5 bulk; (b) non-qualifying
   residential sites mapped in R1 or R2 → R3-2 bulk), then a closing applicability sentence.
4. **Discrepancy with the rule file.** The rule file names "34-111 … (heights)". The live 34-111 is **not
   a height section**; it is the gateway/mapping rule that says which Residence District's bulk governs a
   residential building in a C1/C2 overlay. The two sub-items are not lettered in the body text; they are
   ordered-list items. The rule file cited no sub-paragraph of 34-111, so nothing named "(x)" is missing,
   but the "(heights)" label is wrong for this section.
5. Points to (all plain text, no hyperlinks in this body):
   - "…for the purposes of applying the provisions of **Article II, Chapter 3**, and the remaining
     provisions of this Chapter" — routes residential bulk to Article II Ch 3 (the R6B residence rules)
     and to the rest of Chapter 4. Article II Ch 3 parts are partly captured; "this Chapter" = Ch 4, **not
     captured** as an Article III unit.
   - Defined terms used: "Greater Transit Zone", "qualifying residential sites", "non-qualifying
     residential sites", "Residence District". **Not captured** (definitions live in Article I / 12-10).

---

## ZR 34-24

1. Address: `https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-24` (Article III,
   Chapter 4). Print node: **18326** (`…/entityprint/pdf/node/18326`, not fetched by me). HTML read:
   HTTP **200**, **75,612 bytes**, **2026-10-07T03:57:34Z**.
2. Title as shown: **"Modification of Height and Setback Regulations"**. Stamp: **"Last Amended
   12/5/2024"**.
3. Shape: ~1,200 characters, no table. Opening district list **C1 C2 C3 C4 C5 C6**, a stem sentence, then
   two bold-titled subdivisions: "In Commercial Districts with R1 through R5 equivalency" and "In
   Commercial Districts with R6 through R12 equivalency" (the second has three run-in items).
4. **Discrepancy with the rule file.** The rule file names "**34-24(b)(1)**". The live 34-24 has **no
   lettered paragraphs at all** (no (a)/(b), no (b)(1)); it is organized by the two named "equivalency"
   subdivisions above. So "34-24(b)(1)" does **not exist as named**. 34-24 is a routing rule: it sends
   R6–R12 residential height/setback to 35-63 and R1–R5 to 35-62. (The street-wall 8-ft rule the rule
   file ties to "34-24(b)(1)" actually lives in 35-631(b) — see below.)
5. Points to (hyperlinked unless noted):
   - "…made applicable to such districts in Section **34-11** (General Provisions)" → `/article-iii/chapter-4#34-11`. Article III. **Not captured.**
   - R1–R5 branch: "the modifications to residential height and setback regulations set forth in Section
     **35-62** shall be applied" → `/article-iii/chapter-5#35-62`. **Not captured.**
   - R6–R12 branch (covers R6B): "the modifications … set forth in Section **35-63**, inclusive, shall be
     applied" → `/article-iii/chapter-5#35-63`. **Not captured** (contains 35-631 and 35-632 below).
   - "the special height and setback provisions for certain areas set forth in Section **36-64**" →
     `/article-iii/chapter-6#36-64`. Article III, Ch 6. **Not captured.**
   - "where the optional bulk regulations for sky exposure plane buildings are utilized … Section
     **35-71**, inclusive" → `/article-iii/chapter-5#35-71`. **Not captured.**
   - "the height and setback regulations set forth in **Article II, Chapter 3**" (plain text). Partly captured.

---

## ZR 35-53

1. Address: `https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-53` (Article III,
   Chapter 5). Print node: **18281** (`…/entityprint/pdf/node/18281`, not fetched by me). HTML read:
   HTTP **200**, **85,787 bytes**, **2026-10-07T03:58:29Z**.
2. Title as shown: **"Modification of Rear Yard Requirements"**. Stamp: **"Last Amended 12/5/2024"**.
3. Shape: short (~630 characters), no table, no lettered paragraphs. District list **C1 C2 C3 C4 C5 C6**,
   then one prose paragraph about where the residential rear yard is provided, then one sentence on
   permitted obstructions.
4. Exists as named. The rule file cites "35-53" with no sub-paragraph; none is needed. Its own scope words
   are "**for a residential portion of a mixed building**" — the capture task/reader must judge how it bears
   on an all-residential building (I do not interpret that here).
5. Points to:
   - "…decks, parapet walls, roof thickness … shall be permitted, pursuant to Section **23-41**
     (Permitted Obstructions), inclusive" → `/article-ii/chapter-3#23-41`. Article II. **Not captured**
     (23-42 is captured, but 23-41 itself is not).
   - Defined terms: "residential", "mixed building", "rear yard", "story", "dwelling units", "rooming
     units", "yard". **Not captured.**

---

## ZR 35-631

1. Address: `https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-631` (Article III,
   Chapter 5). Print node: **18291** (`…/entityprint/pdf/node/18291`, not fetched by me). HTML read:
   HTTP **200**, **91,638 bytes**, **2026-10-07T03:58:50Z**.
2. Title as shown: **"Street wall location"**. Stamp: **"Last Amended 12/5/2024"**.
3. Shape: long (~4,400 characters), no table. District list **C1 C2 C4 C5 C6** (note: **no C3**), a stem
   sentence, then four bold-titled, ordered-list paragraphs: "Line-up rules", "Percentage-based rules",
   "Modifications for large zoning lots", "Articulation allowances". The first has a nested sub-list.
4. **Paragraph (b) exists as named.** The text's own internal references ("paragraph (a)(1) of this
   Section", "paragraph (a) of this Section", "paragraphs (a) or (b)", "paragraphs (a), (b) or (c)") letter
   the four subdivisions (a) Line-up, (b) Percentage-based, (c) Large zoning lots, (d) Articulation.
   Paragraph **(b)** is the "Percentage-based rules": "**At least 70 percent of the aggregate width of
   street walls shall be located within eight feet of the street line**" — this matches the rule file's
   "35-631(b) … within 8 ft of the street line". Paragraph (a) ("Line-up rules") is limited by its own
   words to "R8 through R12 Districts, when located within the Manhattan Core … along wide streets".
5. Points to (hyperlinked):
   - "…below the maximum base height and before the required setback as set forth in Section **23-432**
     (Height and setback requirements)" → `/article-ii/chapter-3#23-432`. **Already captured** (zr-23-432).
   - "the line-up provisions of paragraph (a) of Section **23-431** may be applied" (twice) →
     `/article-ii/chapter-3#23-431`. **Already captured** (zr-23-431).
   - Defined terms: "street wall", "Manhattan Core", "wide/narrow street", "street line", "zoning lot",
     "base plane", "aggregate width of street walls", "outer court", "corner lots", "block", "prevailing
     street wall frontage", "lot area". **Not captured.**

---

## ZR 35-632

1. Address: `https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-632` (Article III,
   Chapter 5). Print node: **18292** (`…/entityprint/pdf/node/18292`, not fetched by me). HTML read:
   HTTP **200**, **87,541 bytes**, **2026-10-07T03:59:25Z**.
2. Title as shown: **"Maximum height of buildings and setback regulations"**. Stamp: **"Last Amended
   12/5/2024"**.
3. Shape: ~1,700 characters, no table. District list **C1 C2 C4 C5 C6** (note: **no C3**), a stem sentence
   ("where mapped within, or with a residential equivalent of an R6 through R12 district, the height and
   setback regulations of Section 23-43 … shall be applied …"), then a 3-item ordered list: "Height and
   setback requirements", "Height and setback modifications on eligible sites", "Tower regulations".
4. **Paragraph (a) exists as named.** The three subdivisions are the one `<ol>`'s three items, so (a) =
   "Height and setback requirements", (b) = "…modifications on eligible sites", (c) = "Tower regulations".
   Paragraph **(a)** is the heights paragraph: "The minimum base height, maximum base height and maximum
   building height shall be as set forth in the table in Section 23-432 …" — matches the rule file's
   "35-632(a) (heights)". (The body does not print a literal "(a)"; the letter is the list position. The
   capture task should confirm the letter at the source.)
5. Points to:
   - stem: "the height and setback regulations of Section **23-43** (Height and Setback Requirements in R6
     Through R12 Districts), inclusive" → `/article-ii/chapter-3#23-43`. Umbrella; its children 23-431/432/433
     are captured, but 23-43 "inclusive" (and 23-434, 23-435) is **not captured** as a unit.
   - (a): "…as set forth in the table in Section **23-432** for the applicable Residence District" →
     `/article-ii/chapter-3#23-432`. **Already captured.** And "a setback shall be provided … in accordance
     with Section **23-433**" (plain text). **Already captured** (zr-23-433).
   - (b): "for zoning lots meeting the criteria of paragraph (a) of Section **23-434** … increased in
     accordance with the table in Section 23-434" → `/article-ii/chapter-3#23-434`. **Not captured.**
   - (c): "towers shall be permitted pursuant to the provisions of Section **23-435**" (plain text).
     **Not captured.** Applies to "R9 through R12 … other than R9A, R9X, R10A or R11A".
   - Defined terms: "residential equivalent", "Residence District", "qualifying affordable housing",
     "qualifying senior housing", "street wall", "building", "zoning lots". **Not captured.**

---

## List 6 — are these five the sections a reader needs for a residential building where a C1 or C2 overlay is mapped in an R6B district?

Following only what the texts above say (not interpreting their meaning): the five are the Article III
entry points, but they are **not self-contained**, and two of them sit inside a third:

- **34-111** is the gateway: the surrounding Residence District's bulk applies, routed to **Article II,
  Chapter 3** (the R6B residence rules) "and the remaining provisions of this Chapter" (Ch 4).
- **34-24** then routes R6–R12 height/setback to "**35-63**, inclusive" — which **contains 35-631 and
  35-632**. So 35-631 and 35-632 are reached through 34-24/35-63, not independently.
- **35-631** (street wall) and **35-632** (heights/setback) each point back into Article II (23-431,
  23-432, 23-433 — captured; 23-434, 23-435 — not).
- **35-53** (rear yard) points to 23-41 (not captured).

Further **Article III** sections the texts point to as governing such a building (bulk/height/yards),
each **pointed to by the text; not checked further**:

- **34-11** (General Provisions) — pointing words: "made applicable to such districts in Section 34-11
  (General Provisions)" (34-24). `…/article-iii/chapter-4#34-11`.
- **35-63, inclusive** — pointing words: "the modifications to residential height and setback regulations
  set forth in Section 35-63, inclusive" (34-24). This is the R6–R12 parent of 35-631/35-632.
  `…/article-iii/chapter-5#35-63`. May contain further children (e.g. 35-633+) the capture task should enumerate.
- **35-62** — pointing words: "the modifications … set forth in Section 35-62" (34-24); its own scope is
  "R1 through R5 equivalency", i.e. not the R6B branch. `…/article-iii/chapter-5#35-62`.
- **36-64** — pointing words: "the special height and setback provisions for certain areas set forth in
  Section 36-64" (34-24). Article III, Ch 6. `…/article-iii/chapter-6#36-64`.
- **35-71, inclusive** — pointing words: "where the optional bulk regulations for sky exposure plane
  buildings are utilized … Section 35-71, inclusive" (34-24). `…/article-iii/chapter-5#35-71`.

Note (fact, not ranking): none of the five points to an Article III floor-area, lot-coverage or density
section for the overlay. 34-111's text routes those to the surrounding Residence District (Article II,
Chapter 3). I do not say what that means for any lot.

---

## Doubts

1. **Rule-file labels are partly stale.** The rule file ties "34-111 (heights)" and "34-24(b)(1)" to
   these sections, but live 34-111 is a bulk-mapping gateway (not heights) and live 34-24 has no (b)(1).
   The street-wall 8-ft rule is in 35-631(b), and the heights paragraph is 35-632(a). Likely the labels
   predate the City of Yes restructuring. The capture task should re-key its citations to the live text.
2. **All five show "Last Amended 12/5/2024."** This came from each page's per-section amendment popup
   (data-content-nid / data-section-number matched the section), not a page banner — but the 12-10
   snapshot warns that a "12/5/2024" value was once a City-of-Yes banner elsewhere. The capture task must
   confirm each per-section stamp at the source.
3. **Print/PDF channel untested by me.** Node ids are from each page's own shortlink; I did not fetch any
   `entityprint/pdf/node/<id>`. Big ZR pages have 504'd before (12-10, node 18523). The capture task must
   fetch, pin, and fall back per the documented method.
4. **Paragraph letters are list positions**, not literal "(a)" text, for 34-111 and 35-632; confirmed for
   35-631 by its internal cross-references. Confirm the exact rendering when capturing.
5. **"35-63, inclusive" not enumerated.** I did not open 35-63, so I cannot list all its children; 35-631
   and 35-632 are two of them. The capture task should enumerate the rest.
6. The "36-64" reference in 34-24 is in Article III **Chapter 6** (confirmed by its href), not Chapter 5.
