# M4 footprint — R5 §11-25 applicability decision (owner correction, 2026-07-23)

**Purpose.** Records the per-variant applicability rule for the R5-series footprint tasks
(M4-T007..T010), correcting the earlier scoping report's flag E-1 ("generic R5 vs suffixed R5A/R5B/R5D
is inherently ambiguous"). Per owner directive, **that characterization is withdrawn**: ZR **§11-25**
supplies the governing rule, so the base→suffix relationship is *governed*, not ambiguous.

**Authority boundary.** This is the applicability rule the draft rules will ENCODE and CITE. It is
grounded in verbatim §11-25 text (raw-HTML-verified 2026-07-23) and directed by the owner. The
producer byte-verifies §11-25 and each substantive section at G-time; **G6 qualified-human legal
approval still governs** publication/verification/acceptance. The one residual paragraph-scope point
(§23-332, below) stays a professional-review note, not a mechanical resolution.

## The rule — ZR §11-25 "District Designations Appended with Suffixes"

Last Amended **6/29/1994** (a stable Article I interpretive rule, unchanged by City of Yes) ·
`https://zr.planning.nyc.gov/article-i/chapter-1/11-25`. Verbatim:

> "All regulations applicable to a district designation shall be applicable to such district
> designation appended with a suffix, except as otherwise set forth in express provisions of this
> Resolution. If a section lists an R4 District, therefore, the provisions of that section shall also
> apply to R4-1, R4A and R4B Districts, unless separate provisions for the districts with suffixes are
> listed within such section. Wherever a section lists only a district with a suffix, the provisions
> applicable to such district are different from the provisions of that district without a suffix. If
> a section lists only a C4-6A District, therefore, the provisions of that section are not applicable
> to a C4-6 District."

**Encoded consequence:**
1. A base-`R5` provision applies to **R5A/R5B/R5D** unless the SAME section lists separate provisions
   for the suffixed district.
2. Where a section lists a suffixed district separately, that separate provision governs it (and a
   suffix-only listing does not reach base R5).
3. **Each of R5/R5A/R5B/R5D is still represented EXPLICITLY** in the rules (owner control #1 — no
   silent family default). A value that a variant takes *through* §11-25 (rather than its own listing)
   **cites §11-25 + the controlling substantive section** (e.g. §11-25 + §23-361), with distinct
   `last_amended` provenance for each (§11-25 = 1994; the substantive section = 2024-12-05).

## Per-dimension resolution (raw-HTML-verified; values `[CANDIDATE]`, G6-gated)

| Dimension / section | §11-25 application (does the section list the suffix separately?) | Per-variant result |
|---|---|---|
| **Front yard §23-321** | YES — R5A listed in the 10-ft row; R5B, R5D in the 5-ft row | R5 = 10, R5A = 10, **R5B = 5, R5D = 5** ft [CANDIDATE] — each by its OWN listing (cite §23-321 alone) |
| **Rear yard §23-342 / RYE §23-343 / §23-344** | NO R5 suffix separately listed (header "R1…R12") | **Uniform** across R5/R5A/R5B/R5D via §11-25 (cite §11-25 + the section) |
| **Lot coverage §23-361 / §23-363** | NO R5 suffix separately listed (table lists R1/R2/R3/R4/R5; the R2X/R3A/R3X exception lists no R5 suffix) | **Uniform** across R5/R5A/R5B/R5D via §11-25 (cite §11-25 + §23-361) [CANDIDATE 60% interior/through, 80% corner, 1–2-family] |
| **Side yard §23-332 (+333/334)** | PARTIAL — §23-332 is building-type-**keyed**; R5B/R5D appear separately only in paragraph (c) "other residences"; (a) detached and (b) semi-detached/ZLL use bare "R5" | Bare "R5" in (a)/(b) extends to the suffixes via §11-25; (c) lists R5B/R5D separately — **residual nuance below** |

## Residual interpretive point (§23-332 paragraph scope) — professional-review note, NOT resolved

§11-25 keys the suffix override to separate provisions "listed **within such section**." In §23-332 the
suffixes R5B/R5D are listed separately only in paragraph (c). Whether that separate listing carves
R5B/R5D out of the bare-"R5" **detached (a)** and **semi-detached/ZLL (b)** paragraphs — or only out of
the "other residences (c)" case — is a purposive reading (a hyper-literal "within such section" reading
would leave R5B/R5D detached housing with no side-yard rule, an absurd result). **M4-T010 encodes both
the §11-25 base extension and this open scope question as a `documented_limitation` + professional-review
condition** (cite §11-25 + §23-332), rather than choosing an interpretation. This is a narrow
paragraph-scope question, not the withdrawn broad E-1 ambiguity.

## What changed vs. the initial scoping report
- **Withdrawn:** "generic R5 provisions are inherently ambiguous" (former E-1) and the
  `documented_limitation: generic-R5-ambiguous` it implied.
- **Adopted:** §11-25-governed per-variant resolution above; explicit per-variant representation with
  §11-25 + substantive-section citation for suffix-derived values; a single narrow §23-332
  paragraph-scope professional-review note.
- **Unchanged:** owner control #1 (variants represented separately, no silent default) — now satisfied
  by a *governed* derivation rather than by treating the base token as ambiguous.
