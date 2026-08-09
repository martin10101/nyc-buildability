# M2-T015 SB-S1..SB-S9 coverage matrix (units 3k + 3l — pipeline wiring incl. SB-S4 tax-lot cross-check)

Maps each survey-ingestion acceptance scenario (`SB-S1..SB-S9`, task packet) to the
concrete executable evidence that covers it. This matrix satisfies R272 for unit 3k. It
is deliberately honest about scope: a row's **3k-local** column names the tests added by
this unit; **prior-unit** names already-committed tests that established the mechanism
this unit consumes; **orchestrator/CI** names evidence that only an authoritative run in
the orchestrator's environment produces (the producer sandbox varies per session).

Test IDs are under `services/api/tests/documents/`. All numbers below reflect the
local run recorded in the producer report (`python -m pytest services/api/tests/documents/`
→ **925 passed, 1 skipped** after unit 3l adds the 8 SB-S4 pipeline tests to the 917 from
3k); the orchestrator re-runs to capture the authoritative banner.

| Scenario | What it asserts | 3k-local evidence (this unit) | Prior-unit / supporting evidence | Orchestrator/CI |
|---|---|---|---|---|
| **SB-S1** — digitally-authored path reaches `auto_extracted` | A vector/embedded-text PDF decodes deterministically and, when every fact validates and every check passes, promotes to `auto_extracted` through the H5 gate. | `test_survey_pipeline.py::TestAutoExtracted::*` (clean doc → `auto_extracted`, 2 facts, every fact `PromotionAllowed`, checks pass, gated edge record); `test_vector_pdf_decoder.py::TestSuccessfulDecode::*` (embedded text + vector segments/rects decoded). | PDF reader (`test_pdf_container.py`, `test_pdf_content.py`); promotion gate (`test_promotion.py`, `test_promotion_wiring.py`). | Full-suite pytest banner; CI `api` job. |
| **SB-S2** — closed format routing; unsupported → typed rejection, never improvised parsing | Only matrix formats route; anything else is a typed rejection naming the supported formats; the pipeline never parses an unrouted format. | `test_survey_pipeline.py::TestRoutingPassThrough::*` (unsupported `docx` → `ExtractionNotStarted` w/ `unsupported_format`; raster route → `DecoderUnavailable`, no decode). | `test_extraction_routing.py::TestFormatRoutingMatrix` (the CLOSED matrix, verbatim). | CI `api` job. |
| **SB-S3** — deterministic checks; failures visible, never silent | Every failing/unresolved check, a decode refusal, and an empty extraction route to `needs_review` and are recorded, never silently passed or dropped. | `test_survey_pipeline.py::TestFailClosedRouting::*` (decode-refusal → `needs_review`, no facts, refusal recorded; empty extraction → `needs_review`; payloads JSON-serializable); check outcomes recorded onto facts in `TestWrongAddressRouting::test_wrong_address_records_a_failed_check_on_the_bbl_fact`. | Check semantics: `test_checks_boundary.py`, `test_checks_area.py`, `test_checks_metadata.py`. | CI `api` job. |
| **SB-S4** — MapPLUTO cross-check never overrides a licensed survey | The tax-lot comparison is context-only; divergence routes to review and never mutates a survey value. | **BBL cross-check now wired end-to-end (unit 3l).** `test_survey_pipeline.py::TestTaxLotCrosscheckWiring::*` — an optional `tax_lot_reference` runs `tax_lot_bbl_crosscheck` over the assembled survey BBL fact and records the frozen typed result on `ExtractionCompleted.tax_lot_crosscheck`: matching BBL ⇒ typed PASS recorded, survey facts byte-for-byte unchanged, promotion preserved (`auto_extracted`); divergent BBL ⇒ typed FAIL recorded + `needs_review` (survey fact never mutated, cross-check the sole cause); no reference ⇒ payload/facts byte-for-byte identical to 3k; unevaluable (no BBL fact / malformed reference) ⇒ recorded + fail-safe `needs_review`, never dropped; the cross-check is non-promotable and kept out of `check_results` and off every fact's `validation_results`. The **AREA cross-check legitimately follows lot-area geometry reconstruction** (a later unit — 3k/3l reconstruct no boundary/area), so no lot-area fact is fabricated to force it. | `test_crosscheck.py` (cross-check mechanism is read-only, non-promotable, `overrides_survey = False`, imports no state/storage). | CI `api` job. |
| **SB-S5** — fail-closed AI/confidence boundary; confidence promotes nothing | A high-confidence value promotes only when deterministic validators resolve; confidence never substitutes. | `test_survey_pipeline.py::TestAutoExtracted::test_every_fact_promotes_and_checks_pass` (facts carry `confidence = 1.0` yet promotion rests solely on the resolved normalized-value + correction-history validators). | `test_promotion.py::TestAiOnlyEvidence`, `TestPromotionAllowed::test_confidence_has_no_influence_on_allowance`; `test_promotion_wiring.py::test_ai_values_cannot_stand_in_for_typed_verdicts`. | CI `api` job. |
| **SB-S6** — isolation boundary + resource bounds are fail-closed | Parsing runs ONLY behind a proven kernel boundary; when unproven, no byte is decoded. | `test_survey_pipeline.py::TestIsolationFailClosed::*` (isolation-disabled → `isolation_unavailable`, spy decoder proves `decode` is never called; permitted → decoder reached). | `test_isolation.py` (fail-closed capability probe both ways); reader stream/page/decode bounds in `test_pdf_container.py`, `test_pdf_content.py`. | CI `api` job (Linux is where the real Landlock/seccomp path runs, R274; applying the boundary is B-001-deployment-gated). |
| **SB-S7** — wrong-address document → `needs_review`, never silently ingested | A BBL/address mismatch fails `address_bbl_match` and routes to `needs_review` with the typed wrong-address routing value. | `test_survey_pipeline.py::TestWrongAddressRouting::*` (wrong-BBL PDF → `needs_review`, `NeedsReviewRouting` cause `failed`, failed check recorded on the BBL fact). | `test_extraction_routing.py::TestWrongAddressRouting`; `test_checks_metadata.py` (`address_bbl_match` exact-equality). | CI `api` job. |
| **SB-S8** — assembled facts validate against the v1 contract | Every assembled `survey_evidence` record validates against `survey_evidence.schema.json`. | `test_survey_pipeline.py::TestSchemaValidity::test_assembled_facts_validate_against_the_v1_contract` (jsonschema engine + contract `$ref` registry); durable fixture `packages/contracts/fixtures/valid/survey_evidence/assembled_embedded_text_scale_statement.json` (assembler output shape). | Contract + fixtures from units 1-2. | `python .github/scripts/validate_contracts.py` (authoritative; producer captured "Checked 10 schema file(s); 0 failure(s)." exit 0 locally, incl. the new fixture). |
| **SB-S9** — CI regression backstop keeps the pack green | The whole scenario pack stays green on the CI events; a screening control without a passing regression is not a control. | The 29 tests this unit adds (11 decoder + 18 pipeline) join the suite as permanent regressions. | Existing document-suite regressions. | CI `api` job on push/PR — the authoritative SB-S9 evidence (orchestrator-captured). |

## Honest scope notes for the reviewer

- **Assembly is intentionally narrow and deterministic.** Unit 3k classifies an embedded-text
  run into a fact ONLY by an exact canonical pattern (`1:N` scale ratio, 10-digit NYC BBL). Distance/
  bearing/area normalization and free-text address labeling (architecture §§8.2-8.3, §10) are NOT
  fabricated here; they are a later deterministic-association / advisory-AI unit. The `auto_extracted`
  path is therefore demonstrated on scale + BBL facts — the full decode → assemble → check → promote
  loop — not on a reconstructed boundary polygon.
- **Isolation presence vs application.** `require_isolation` proves the boundary is PRESENT; applying
  the Landlock ruleset + seccomp filter before the first untrusted byte remains the deployed isolated
  parser path's duty (architecture §5, B-001-gated). Unit 3k guarantees only the structural invariant:
  a decoder is reachable exclusively through an `ExtractionJobAuthorized`, which `begin_extraction_job`
  returns only on a proven boundary.
- **SB-S4 BBL cross-check is now wired into the pipeline (unit 3l).** `run_survey_extraction` takes an
  OPTIONAL `tax_lot_reference: TaxLotReference | None = None`; when supplied it runs the read-only
  `tax_lot_bbl_crosscheck` over the assembled survey BBL fact and records the frozen typed result on
  `ExtractionCompleted.tax_lot_crosscheck`. The cross-check is context-only and enforced structurally: it
  never promotes (non-promotable result, deliberately kept out of `check_results` and off every fact's
  `validation_results`), never becomes a survey value, and never overwrites or mutates any assembled fact —
  the assembled facts are byte-for-byte identical across no-reference / matching / divergent references. It
  can only pull routing TOWARD review: a divergent (FAIL) or unevaluable comparison forces `needs_review`
  (fail-safe, recorded, never dropped); a PASS leaves the deterministic 3k promotion decision untouched;
  with no reference the outcome is byte-for-byte identical to the 3k path.
- **The tax-lot AREA cross-check is deliberately NOT wired yet.** It legitimately follows lot-area geometry
  reconstruction (boundary/area is not reconstructed by 3k or 3l — see the assembly scope note above), so no
  lot-area fact is fabricated to force `tax_lot_area_crosscheck`. Wiring the area cross-check onto a
  reconstructed lot-area fact is a later unit; the mechanism already exists and is unit-tested in
  `test_crosscheck.py`.
