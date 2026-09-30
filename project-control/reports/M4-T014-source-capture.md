# M4-T014 Source-Capture Report — R3/R4-series Height & Setback (post-City of Yes)

Role: rules-engineer (in-task capture). Purpose: capture the CURRENT-effective ZR
height & setback regulations for the R3 and R4 series districts so the draft
`needs_review` rule family can be built with byte-stable, hash-guarded snapshots.
AI captures/classifies; deterministic code calculates; a qualified human approves
at G6. This file is append-only source capture, not an encoded rule and NOT a
Verified legal determination.

## Access

- Retrieval date: **2026-09-13** (fresh, in-task).
- Portal: `zr.planning.nyc.gov` (NYC Dept. of City Planning official Zoning Resolution).
- Method: direct HTTPS GET via `curl -A "Mozilla/5.0"` (HTTP 200 for every URL below),
  legal text extracted from the `field--name-body` container; the district-list
  separators in the raw HTML are non-breaking spaces (U+00A0), normalized to plain
  spaces in the verbatim excerpts.
- Each section carries a machine-readable `<time datetime="2024-12-05T12:00:00Z">12/5/2024</time>`
  Last-Amended stamp = City of Yes for Housing Opportunity (effective **2024-12-05**).
- `raw_html_verified` is set **false** on every snapshot: the excerpt was tag-stripped
  from the fetched HTML but NOT re-verified byte-for-byte against the raw HTML bytes,
  and nothing here is G6-approved. `extraction_status = extracted_draft`.

## Structure / routing (§23-42, verbatim)

§23-42 (overview, districts "R1 R2 R3 R4 R5"): "the height and setback regulations …
shall be as set forth in Section 23-421 (Basic pitched-roof envelopes for certain
districts) and 23-422 (Basic flat-roof envelopes for certain districts). Where
applicable, standard setback provisions are set forth in Section 23-423. Such heights
may be increased on qualifying residential sites … qualifying senior housing, or …
certain large sites, pursuant to Sections 23-424 or 23-425 … The height of all
buildings or other structures shall be measured from the base plane."

Envelope selection is by **building type**, not district alone: §23-421 governs the
pitched-roof (detached / semi-detached / zero-lot-line) forms; §23-422 the flat-roof
forms. §23-424/§23-425 increases and §23-426/§23-44 modifications are conditional
(geography / lot-eligibility / overlay dependent) = **A2 gaps (D-045-R008)**, not
encoded as numeric values here.

## Authoritative variant enumeration (recorded with anchors)

### §23-421 pitched-roof envelope — opening district list (first line of the section body)
Verbatim list: **R1 R2 R3A R3X R3-1 R3-2 R4 R4-1 R4A R5A**.
- R3/R4-series members in M4-T014 scope: **R3A, R3X, R3-1, R3-2, R4, R4-1, R4A**.
- Uniform envelope for the whole list (no per-district override in the section):
  perimeter-wall height **max 25 ft** above the base plane; ridge/building height
  **max 35 ft** above the base plane.
- Setback above the perimeter wall = sloping-plane geometry (apex points; sloping
  planes rising to the 35 ft ridge; §23-421 paragraphs beyond this capture's readable
  excerpt) = **A2 gap**, surfaced as a documented limitation, never numeric. The
  "apex-point / ≤80°" detail and the "(a) through (g)" paragraph count are NOT read from
  THIS in-task HTML capture (see the completeness note below); they are carried from the
  preserved rules-engineer agent memory and the owner-verified record, named explicitly
  in the corrected snapshot notes.
- Out of scope from this same list: R1/R2 (bare group labels — **blocker B-023**,
  Section 20 / Tier D legal ruling pending) and R5A (accepted M4-T006 R5 pilot).
- §23-421 paragraph (g) — the R1/R2-without-a-letter-suffix reference-plane provision —
  is **NOT** content of this in-task capture. This HTML curl channel could NOT render it:
  the zr.planning.nyc.gov HTML render is documented to lose Section 23-421(g) in text
  extraction on both official mirrors across four attempts (`docs/ARCHITECT_REVIEW_QUESTIONS.md`
  lines 48-51, owner-verified 2026-09-13); the figures below appear NOWHERE in this
  capture's `verbatim_excerpt`. They are stated here only as a provenance-qualified
  description drawn from two NAMED sources outside this capture — the owner-verified
  record in `docs/ARCHITECT_REVIEW_QUESTIONS.md` (section A1/A3, approx. lines 40-56 and
  88-90) and the preserved rules-engineer agent memory
  (`.claude/agent-memory/rules-engineer/zr-r1-r2-height-setback-source-facts.md`,
  preserved in blocker B-023) — never as an in-task §23-421 quote. Per those
  owner-verified-elsewhere sources: for R1 and R2 Districts WITHOUT a letter suffix, the
  reference plane may be located up to 5 ft above the base plane where EITHER (a) the
  zoning lot has an area of at least 9,500 sq ft AND a width of at least 100 ft, OR (b)
  the lot has a slope (street-wall-line level to rear-wall-line level) of at least 5
  percent. This provision does NOT touch R3/R4 and remains out of M4-T014 scope
  (R1/R2 = blocker B-023).

**Completeness note (owner directive, carried forward from the M4-T012 packet):** the
rules pipeline must prove ZR §23-421 section completeness from an artifact that provably
contains the full text (e.g. a print/PDF render) — never from HTML extraction alone,
because the HTML render on `zr.planning.nyc.gov` is documented to lose paragraph (g) on
both official mirrors across four attempts (`docs/ARCHITECT_REVIEW_QUESTIONS.md` lines
48-51). This in-task capture is an HTML curl channel and therefore does NOT constitute
that completeness proof. Full-text (print/PDF) verification of §23-421 is still owed
before any rule citing snapshot `zr-23-421-r3-r4` (or the accepted pilot's `zr-23-421`)
advances toward G6.

### §23-422 flat-roof envelope — opening district list + per-statement labels
Verbatim list: **R3-2 R4 R4B R5 R5B R5D**. R3/R4-series members in scope: **R3-2, R4, R4B**.
- **R3-2, R4** (grouped): "for residences not subject to the provisions of Section
  23-421, the maximum building height shall be **35 feet**." (single flat building-height
  cap; NO base-height/setback split stated).
- **R4B**: "In the district indicated, the maximum building height shall be **25 feet**."
  (single flat cap; no building-type condition; R4B has **no §23-421 counterpart** —
  the asymmetry is recorded, never symmetrized).
- R5/R5B/R5D statements of this same section belong to the accepted M4-T006 R5 pilot
  (snapshot `zr-23-422`) and are NOT duplicated here.

### Variant × section matrix (recorded asymmetry)

| Variant | §23-421 pitched (25/35) | §23-422 flat |
|---|---|---|
| R3A  | yes | — |
| R3X  | yes | — |
| R3-1 | yes | — |
| R3-2 | yes | 35 ft building height |
| R4   | yes | 35 ft building height |
| R4-1 | yes | — |
| R4A  | yes | — |
| R4B  | —   | 25 ft building height |

R3-2 and R4 are the only dual-section variants (building type selects the envelope);
R4B is flat-only; R3A/R3X/R3-1/R4-1/R4A are pitched-only. No membership was
symmetrized by assumption.

## Snapshots created (canonical `docs/research/zr-snapshots/v1/`, synced to bundle)

| snapshot_id | section | request_url | retrieved_at | content_digest_sha256 (sha256 of verbatim_excerpt) |
|---|---|---|---|---|
| zr-23-42 | 23-42 | https://zr.planning.nyc.gov/article-ii/chapter-3/23-42 | 2026-09-13 | `3fea4ca54cfee304698506e83f126949863b6a539b2e6de8731a58cfb494070d` |
| zr-23-421-r3-r4 | 23-421 | https://zr.planning.nyc.gov/article-ii/chapter-3/23-421 | 2026-09-13 | `68e4d147a351188ce0df06d8609b1c3766c76776e0a87482e04ac2cc9459e046` |
| zr-23-422-r3-r4 | 23-422 | https://zr.planning.nyc.gov/article-ii/chapter-3/23-422 | 2026-09-13 | `0268089074b51d7b2457fa280bb19f5a2ce1c49b708dbb6654f49df78ea61b18` |

Digests verified: `sync_zr_snapshots.py --check` EXIT 0 (bundle byte-identical, 10
files); `SnapshotStore().load()` loads all three with matching digests (tamper guard
active). Each rule's citation records the same digest and is fail-closed-bound at load
(`dsl._check_refs`; M4-T010).

## Ambiguity / gap assessment

- No group-label ambiguity touches R3/R4: §23-421 enumerates R3A/R3X/R3-1/R3-2/R4/R4-1/R4A
  and §23-422 lists R3-2/R4/R4B EXPLICITLY (confirms the M4-T012 finding / B-023 scope).
- Genuinely numeric caps became numeric constraints: 25 ft (pitched perimeter wall),
  35 ft (pitched ridge / R3-2+R4 flat building height), 25 ft (R4B flat building height).
- Typed A2 gaps (provenance-carrying, never numeric): §23-421 sloping-plane setback
  geometry; §23-424/§23-425 qualifying-site / large-site increases; §23-426/§23-44
  historic-district / special-district / commercial-overlay modifications; the base-plane
  determination. `building_type` is a required, fail-closed input with no canonical
  property_profile field (unavailable in practice ⇒ professional_review_required).
- No street-width-conditional provision bears on the R3/R4 height caps captured (the
  §23-423 10/15-ft setback is triggered only by a base-height/setback split, which
  R3-2/R4/R4B flat caps do NOT have; it remains an A2 gap for any future R5-style split).
