# UI inspiration mockups (owner-supplied, 2026-09-12)

Six AI-generated LAYOUT STUDIES produced by the owner with ChatGPT's image model (GPT Image
2 class), from prompts built on `docs/design/competitor-report-presentation-research.md`.
**Status: inspiration/reference ONLY — not specifications.** Every number, address, citation,
and label in these images is INVENTED mockup content; nothing here asserts a real zoning value.
The real UI is designed through the normal design-spec → review → gated-implementation process.

| File | Screen |
|---|---|
| 01-search-front-door.png | Landing: "What can you build?" + address search + trust markers |
| 02-verdict-screen.png | The verdict: lot map left; hero "unused development rights" number, three stat cards, "What could change this" checklist |
| 03-fact-cards-detail.png | Detail level: section rail + four-line fact cards (rule → value → plain sentence → citation chip) + expanded law-text quote |
| 04-report-page-one.png | Printable report page 1: verdict box, parameter table, checklist, verify-before-filing footer + reference code |
| 05-phone-verdict.png | Mobile verdict, single calm column |
| 06-lot-compare-strip.png | Four-lot screening strip with identical card structure + status strips |

## Known wording corrections REQUIRED before any of this becomes a spec

1. **"text verified" chip (03) must be reworded** — house law forbids "verified" vocabulary on
   user surfaces; the digest match should read e.g. "law text matched · Jun 2024" (mechanism,
   not vouching).
2. **"Looks buildable (draft)" status (06) is too close to a compliance verdict** — reword to a
   non-adjudicating form (e.g. "Draft rights computed · no blockers found in checked items").
3. **Checklist icon semantics (02/04/05):** green check currently means "found" for an overlay —
   but a found overlay is a *modifier*, not good news. Icons must encode
   found / not-found / unknown / needs-review, never good/bad.
4. **Report table rows (04) lack per-row citations** — the ZD1/BSA convention (and our own law)
   is a citation on every value; page 1 must carry them or point to the citation appendix.
5. **Missing on all screens:** the data-vintage line (dataset release dates per source) and the
   correlation/reference id on the interactive screens (the report already shows one).
6. Mock numbers are internally consistent (61,250 − 20,000 = 41,250) — keep that discipline in
   future mockups so nobody screenshot-quotes an impossible example.
