# M5-T163 producer report — NB-03 revision 2 and the ZR 12-10 street-definition captures

Producer: official-source-researcher. Documents only. Claim head
`aac892fcde5dc035848af9bf99f7cea0bc8edec2` on `task/wave24-report-v3`.
Research and verification (D-093) applied; primary sources opened, not the brief's summary.

## Files changed (all inside the packet's allowed paths)

- `docs/research/evidence-records/NB-03-rear-yard-short-block.json` — revision 1 → 2 (gaps a–h).
- `docs/research/zr-snapshots/v1/zr-12-10-street.snapshot.json` — new capture.
- `docs/research/zr-snapshots/v1/zr-12-10-street-setback-line.snapshot.json` — new capture.
- `docs/research/zr-snapshots/v1/zr-12-10-street-wide.snapshot.json` — new capture.
- `docs/research/zr-snapshots/v1/zr-12-10-street-narrow.snapshot.json` — new capture.
- `services/api/app/_zr_snapshots/v1/zr-12-10-street*.snapshot.json` (×4) — byte-identical bundled copies.
- `project-control/reports/M5-T163-producer-report.md` — this report.

README.md and RESEARCH_REQUESTS.md were **not** changed: NB-03's research_status is unchanged
(`interpretation_awaiting_review`), so per the packet both are left as-is.

## Captures (channel, retrieved, sha256)

Page: ZR 12-10, canonical HTML node 18523,
`https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10` (no `#`), retrieved
2026-10-11T19:58:08Z, HTTP 200, 1,287,409 bytes, raw_html_sha256
`8eb066d190f0270a20008973576a19e65f579e46d68b51e5fb361a07515bb33c`. The whole-page print/PDF
completeness channel `entityprint/pdf/node/18523` returned **HTTP 504** (41-byte "The application
did not respond in time."), retrieved 2026-10-11T19:58:51Z — the documented DB-167 fallback; each
capture discloses it and is extraction_status `extracted_draft`, raw_html_verified false. None of the
four definitions contains an ordered list (no `<ol>`); any parenthesised (a)/(b)/(1) is literal
source text.

| snapshot_id | defined_term / node | last amended | content_digest_sha256 (= sha256 of verbatim_excerpt) | file sha256 (LF) |
|---|---|---|---|---|
| zr-12-10-street | street / 21676 | 2/2/2011 | `7135283ce81d4d482a85086b466c709b53494d069ef4e4ede78f91b33685cce8` | `08966adc7880b61f268d17c4008ec50b1dd41307e179cf0ab76146f0545ceb5e` |
| zr-12-10-street-setback-line | street setback line / 21679 | 9/19/1985 | `ab543a997252eb04f958d0d65f6c588f0f23bf5daa958315637f00eb5e8ff4c3` | `56bffca7faf13e5a44fc440ae3ade7994b8b5bae7ae0e7aa069fa05853c548bc` |
| zr-12-10-street-wide | street, wide / 21683 | 3/26/2026 | `ddc28f49a391f11bd5646152c1ecaed649172edf6dbe7c7224759f3d3b43f1b3` | `f14bfee5eaade6f26fb41fa42923f42f16a6313ce31d8bad71a860438063ef24` |
| zr-12-10-street-narrow | street, narrow / 21678 | 12/15/1961 | `df578443effa365a572f2fb95f27dea590036d122a5d777b99230e716676a31a` | `881180c7b08169d30f6ae40724d9d8c079acc9de18067b6e1b7a9d019e600e16` |

Bundled copies under `services/api/app/_zr_snapshots/v1/` are byte-identical to the canonical copies
(same file sha256; verified by `sync_zr_snapshots.py --check` and the bundle test).

"street setback line" **is** a defined term (the packet flagged it might not be) — captured. The
"street, wide" text is the 2026-03-26 amendment (C5-3/C6-4/C6-6 alternate width; 70-ft connector;
Broadway W94–97 CD7 and Allen St Rivington–Delancey CD3).

## One-line answer per gap (each has a dated line + source + next step in NB-03 `conclusion.conditions`)

- (a) depth conflict: 100 ft (printed_tax_map label), 99.97 ft (gis, to the lot's own edge), ~101.06 ft
  (derived, to the mapped street line; hand-calc lines 97 and 92 assumption) — shown as a conflict, **no
  basis chosen**; settled by survey/ZD1. Sources E6, E7, `docs/reference-cases/R6B/provenance/return-independent-hand-calculation-11.md`.
- (b) the "short dimension of a block" is **one** measurement feeding both 23-344(b) (rear yard) and
  23-363(c) (100 % lot coverage) — measured once, never per street name. Sources E1, E2, E10, E11.
- (c) captured 12-10 "street" (E8) and "street setback line" (E9); a block is bounded only by the six
  12-10 "block" feature types (E10: streets, public parks, railroad ROW, airport boundaries,
  pierhead/shore lines, NYC corporate boundaries), so a tax-map **ALLEY** label is not a bounding feature
  for (b) unless the alley is a mapped #street#. Next step: confirm from the City Map.
- (d) irregular blocks: **searched, not found** — no official method beyond "the dimension between any two
  #streets# bounding the #block#"; 23-363(a)'s irregular-angle rule covers lot **depth** only, not block
  frontage. Next step: M5-T176 / a zoning professional.
- (e) neighbours are **R4B** (PLUTO); 23-344(c)(3)/(d)(3) as read key on the **subject** R6-R12 district and
  the neighbour's lot-line **type**, not the neighbour's district; a "Special Provisions Applying Along
  District Boundaries" section exists in the ZR but **no** residence-district provision changing this rear
  yard because the neighbours are R4B was confirmed from the primary source. Next step: M5-T176 opens it.
- (f) **recorded, not fixed**: the review-register entry `docs/zoning-rule-review/rules/r6b-rear-yard-corner-waiver.md`
  (revision 2, 2026-10-08) and the rule's own `limitations` field reflect only 23-344(a), not (b)/(c)(3)/(d)(3).
  Owed to M5-T167 / DB-230 (outside this task's allowed paths).
- (g) **no worked example** supplied here; M5-T176 supplies the independent one. The record's
  `worked_example` is a labelled law-text draft that leaves the depth basis unchosen.
- (h) PLUTO/MapPLUTO **LotFront** = the tax lot's frontage; on a corner lot it reports **one** side's
  frontage, often the PTS-building-address side (here 215-16 Northern Boulevard); **LotDepth** = the lot's
  depth. Both are DOF-maintained tax-lot attributes → nine-bases **administrative_record**, not a survey.
  Source: official PLUTO data dictionary (Open Data dataset 64uk-42ks column metadata), E14.

Every quantity in NB-03 carries one of the nine bases; no program output appears among expected values;
a tax lot is never equated with a zoning lot; index entries never stand for instruments.

## Coordinator note addressed (NB-06 contradiction)

The full-page capture `docs/research/zr-snapshots/v1/zr-12-10.snapshot.json` (title "Definitions - wide
street and narrow street") **already holds** the verbatim "street, wide" (with the 2026-03-26 amendment)
and "street, narrow" text. My per-definition captures `zr-12-10-street-wide` / `zr-12-10-street-narrow`
**agree word-for-word** with it (verified after normalizing the two transcription conventions: the
full-page capture uses single quotes and no `#term#` markers, mine use double quotes and `#term#` markers,
matching the existing per-definition files). **Apparent contradiction for the orchestrator to route to the
NB-06 owner (M5-T170):** NB-06 revision 2's search S3 records "street, wide"/"street, narrow" as *not
captured* and says a live 12-10 fetch on 2026-10-11 truncated before them — but the text was already in the
full-page capture, and dedicated captures now exist. I did **not** edit NB-06 (outside my scope).

## Checks (direct exit codes)

- `python3 tools/research_record_check.py --check` → **exit 0** (PASS; NB-03 status
  interpretation_awaiting_review, code_current True, review_state stale = revision 2 awaits a fresh review).
- `python services/api/scripts/sync_zr_snapshots.py --check` → **exit 0** (189 files byte-identical).
- `cd services/api && python -m pytest -q tests/rules/test_zr_snapshot_bundle.py tests/drawings/report/test_report_law_links.py`
  → **exit 0** (28 passed; lanes venv, PYTHONPATH=services/api).
- `cd services/api && python -m ruff check .` → **exit 0** (All checks passed).

## What I could not check / limitations

- No second-agent re-read of the raw HTML (raw_html_verified stays false; extracted_draft).
- The whole-page print/PDF completeness channel is unavailable (504) — list-marker glyphs could not be
  confirmed from the glyph-authoritative channel; none of the four definitions has an ordered list, so no
  list-position label is used.
- The 12-10 page bytes differ from the 2026-10-07 captures (1,316,758 → 1,287,409; sha
  3c719702… → 8eb066d1…) — a page-level change; each cited term's per-term Last Amended stamp is unchanged,
  so the operative definition text is the same. Disclosed in every new capture and in NB-03 freshness.
- gap (d) and (e) stay open (searched, not found / not confirmed from the primary source); the survey, ZD1,
  City Map, district-boundary provisions and the independent worked example (M5-T176) are owed.
- No professional review; a labelled unreviewed draft (ADR-007).
