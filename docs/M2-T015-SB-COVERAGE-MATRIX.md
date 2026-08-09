# M2-T015 SB-S1..SB-S9 coverage matrix (unit 3k — DecoderSeam wiring + fact assembly)

Maps each survey-ingestion acceptance scenario (`SB-S1..SB-S9`, task packet) to the
concrete executable evidence that covers it. This matrix satisfies R272 for unit 3k. It
is deliberately honest about scope: a row's **3k-local** column names the tests added by
this unit; **prior-unit** names already-committed tests that established the mechanism
this unit consumes; **orchestrator/CI** names evidence that only an authoritative run in
the orchestrator's environment produces (the producer sandbox varies per session).

Test IDs are under `services/api/tests/documents/`. All numbers below reflect the
local run recorded in the producer report (`python -m pytest services/api/tests/documents/`
→ **917 passed, 1 skipped**); the orchestrator re-runs to capture the authoritative banner.

| Scenario | What it asserts | 3k-local evidence (this unit) | Prior-unit / supporting evidence | Orchestrator/CI |
|---|---|---|---|---|
| **SB-S1** — digitally-authored path reaches `auto_extracted` | A vector/embedded-text PDF decodes deterministically and, when every fact validates and every check passes, promotes to `auto_extracted` through the H5 gate. | `test_survey_pipeline.py::TestAutoExtracted::*` (clean doc → `auto_extracted`, 2 facts, every fact `PromotionAllowed`, checks pass, gated edge record); `test_vector_pdf_decoder.py::TestSuccessfulDecode::*` (embedded text + vector segments/rects decoded). | PDF reader (`test_pdf_container.py`, `test_pdf_content.py`); promotion gate (`test_promotion.py`, `test_promotion_wiring.py`). | Full-suite pytest banner; CI `api` job. |
| **SB-S2** — closed format routing; unsupported → typed rejection, never improvised parsing | Only matrix formats route; anything else is a typed rejection naming the supported formats; the pipeline never parses an unrouted format. | `test_survey_pipeline.py::TestRoutingPassThrough::*` (unsupported `docx` → `ExtractionNotStarted` w/ `unsupported_format`; raster route → `DecoderUnavailable`, no decode). | `test_extraction_routing.py::TestFormatRoutingMatrix` (the CLOSED matrix, verbatim). | CI `api` job. |
| **SB-S3** — deterministic checks; failures visible, never silent | Every failing/unresolved check, a decode refusal, and an empty extraction route to `needs_review` and are recorded, never silently passed or dropped. | `test_survey_pipeline.py::TestFailClosedRouting::*` (decode-refusal → `needs_review`, no facts, refusal recorded; empty extraction → `needs_review`; payloads JSON-serializable); check outcomes recorded onto facts in `TestWrongAddressRouting::test_wrong_address_records_a_failed_check_on_the_bbl_fact`. | Check semantics: `test_checks_boundary.py`, `test_checks_area.py`, `test_checks_metadata.py`. | CI `api` job. |
| **SB-S4** — MapPLUTO cross-check never overrides a licensed survey | The tax-lot comparison is context-only; divergence routes to review and never mutates a survey value. | Not exercised by 3k (the pipeline does not yet consume the tax-lot reference — a deliberate later-unit wiring; noted in the producer report as a limitation). | `test_crosscheck.py` (cross-check is read-only, non-promotable, `overrides_survey = False`). | CI `api` job. |
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
- **SB-S4 is not wired into the pipeline yet** (see the matrix row); the cross-check mechanism exists
  and is tested at unit level. Wiring it into `run_survey_extraction` is a follow-up.
