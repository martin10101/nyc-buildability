# Survey fixture matrix (M2-T015)

Maps each of the 12 objective survey-document fixture categories to the committed
synthetic fixture(s), the deterministic check(s)/scenario(s) each exercises, and an honest
`extraction_status` (live in the shipped pipeline vs deferred to a later unit).

- **Pack location:** `services/api/tests/documents/fixtures/survey_documents/`
  (builder `build_fixture_pack.py`, committed fixtures, `MANIFEST.json`).
- **All fixtures are synthetic.** Surveys are private licensed documents with no live
  official source, so every fixture is deterministically synthesized — no real client
  survey, no captured official response, no private document. Each is labelled
  `classification: synthetic` in the MANIFEST with a `sha256` over its exact bytes.
- **Determinism:** the pack round-trips byte-identically through `build_fixture_pack.py`
  (no wall-clock in the MANIFEST). Verified by
  `services/api/tests/documents/test_survey_fixture_pack.py`.
- **Builders mirror the suite:** the PDF fixtures use the exact `_assemble_pdf` /
  `_one_page_pdf` byte assemblers from `test_survey_pipeline.py` and
  `test_vector_pdf_decoder.py`, so fixtures are the same shapes those tests exercise.
- This matrix is a DIFFERENT document from `docs/M2-T015-SB-COVERAGE-MATRIX.md` (which maps
  the SB-S1..S9 acceptance scenarios to test IDs); both are kept.

## The 12 categories

| # | Category | Fixture(s) | Deterministic check / scenario exercised | Extraction status |
|---|---|---|---|---|
| 1 | Digital PDFs | `SVY01_digital_scale_bbl.pdf` | Embedded-text decode → scale + BBL facts → all checks pass → `auto_extracted` (H5 gate). SB-S1, SB-S8. Test: `test_digital_fixture_promotes_to_auto_extracted`. | **live** — `embedded_text_extraction` |
| 2 | Vector PDFs | `SVY02_vector_segments_rect.pdf` | Straight segment (`m/l S`) + rectangle (`re f`) decode into `VectorSegment`/`VectorRect`; no curve → no refusal. SB-S1. Test: `test_vector_fixtures_decode_into_straight_line_primitives`. | **live** — `vector_object_extraction` |
| 3 | Clean scans | `SVY03_clean_scan.png` | S1 magic sniff + raster route → `DecoderUnavailable` (PNG supported, no concrete decoder yet). SB-S2. Test: `test_raster_scan_fixtures_route_but_defer_decoding`. | **deferred** → OCR/raster unit |
| 4 | Poor scans | `SVY04_poor_scan.png` | Same raster route as clean scan; distinct low-resolution bytes represent a degraded capture. SB-S2. | **deferred** → OCR/raster unit |
| 5 | Rotated pages | `SVY05_rotated_page.pdf` | `/Rotate 90` page: the content stream still decodes (`decode_refusal is None`), but mapping rotated device space to a normalized orientation is deferred. SB-S1/SB-S2. Test: `test_rotated_fixture_content_decodes_without_refusal`. | **deferred** → rotation-normalization unit |
| 6 | Mixed units | `SVY06_mixed_units.pdf` | Boundary courses stated in FEET and METERS. `units.py` refuses mixed/unsupported units (never coerces); assembling distance facts from free text is deferred. SB-S3. | **deferred** → distance/unit-normalization unit |
| 7 | Decimal ambiguities | `SVY07_decimal_ambiguity.pdf` | Ambiguous decimal/thousands separators (`1,234.5` vs `1.234,5`) that must never be silently disambiguated; numeric normalization is deferred (fail-closed on ambiguity). SB-S3. | **deferred** → distance/bearing-normalization unit |
| 8 | Conflicting dimensions | `SVY08_conflicting_scale.pdf` | Two scale statements (`1:240`, `1:480`) → two `scale_statement` facts → `scale_consistency` check FAILS → `needs_review`. SB-S3. Test: `test_conflicting_scale_fixture_fails_closed_to_needs_review`. | **live** — `embedded_text_extraction` |
| 9 | Incomplete boundaries | `SVY09_incomplete_boundary.pdf` | Open (non-closing) polyline of straight segments decodes as two `VectorSegment`s, never silently closed; boundary/area reconstruction (and the AREA cross-check that follows) is deferred. SB-S3. Test: `test_vector_fixtures_decode_into_straight_line_primitives`. | **deferred** → boundary-reconstruction unit |
| 10 | Multi-page surveys | `SVY10_multipage_survey.pdf` | Two pages (scale on p1, BBL on p2) decode in order; one fact per page → `auto_extracted`. SB-S1. Test: `test_multipage_fixture_decodes_both_pages_and_auto_extracts`. | **live** — `embedded_text_extraction` |
| 11 | Wrong-address files | `SVY11_wrong_bbl.pdf` | Stated BBL `3001230045` ≠ subject → `address_bbl_match` fails → `needs_review` with the typed wrong-address routing value. SB-S7. Test: `test_wrong_bbl_fixture_routes_to_needs_review`. | **live** — `embedded_text_extraction` |
| 12 | Malicious / oversized inputs | `SVY12_exe_renamed_as_pdf.pdf`, `SVY13_html_renamed_as_tiff.tiff`, `SVY14_oversize_sentinel.pdf` | T01 executable-renamed-`.pdf` and T02 HTML-renamed-`.tiff` → typed `ExtensionMismatchError` at the S1 gate (content decides, never the extension); T03 oversize → `UploadTooLargeError` at `MAX_UPLOAD_BYTES + 1` (proven in-memory; a >50 MiB file is intentionally not committed per the thin-client storage policy). SB-S2. Tests: `test_exe_renamed_fixture_is_rejected_by_the_s1_gate`, `test_html_renamed_fixture_is_rejected_by_the_s1_gate`, `test_oversize_sentinel_documents_the_cap_without_a_50mib_fixture`. | **live** — S1 gate (sniff + streaming cap) |

## Honest deferral notes

- **Deferred categories still ship a committed fixture.** Categories whose extraction path
  is not yet live (raster scans, rotated-page normalization, distance/unit and
  decimal normalization, boundary/area reconstruction) still carry a representative synthetic
  fixture with an honest `extraction_status`, so the matrix is complete even where extraction
  lands in a later unit. Where a deferred fixture's structure still decodes (rotated content,
  incomplete-boundary segments) the test asserts only the decode, not the deferred
  interpretation.
- **Live categories are proven end-to-end.** The digital, vector, conflicting-scale,
  multi-page, wrong-address, and malicious/oversize fixtures are run through the real
  pipeline / S1 gate in `test_survey_fixture_pack.py`, so the matrix's "live" claims are
  executable, not prose.
- **No area/boundary fact is fabricated.** The tax-lot AREA cross-check legitimately follows
  lot-area geometry reconstruction (deferred), so no lot-area fact is invented to force it —
  consistent with `docs/M2-T015-SB-COVERAGE-MATRIX.md`.
