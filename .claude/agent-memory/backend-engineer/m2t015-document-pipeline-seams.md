---
name: m2t015-document-pipeline-seams
description: Non-obvious wiring seams in the M2-T015 survey document-ingestion pipeline (services/api/app/documents) — promotion-gate evidence contract, isolation gating, two distinct "validation_results"
metadata:
  type: project
---

Stable architectural facts about the M2-T015 survey ingestion pipeline
(`services/api/app/documents/**`), learned wiring the concrete DecoderSeam + fact
assembly (unit 3k). Verify against source before relying — these are mechanism notes,
not status.

**Two different things are both called "validation_results".** (1) The wire
`survey_evidence.validation_results` array records deterministic CHECK outcomes
(`check_id` enum: `scale_consistency`, `address_bbl_match`, …). (2) `evaluate_promotion(validation_results=…)`
takes a mapping `{ValidationKind: (results,)}` where `ValidationKind ∈ {normalized_value, location, correction_history}`
— the VALIDATOR families, NOT the checks. The promotion gate never consumes the checks;
checks feed the `auto_extracted`-vs-`needs_review` document decision.

**Promotion evidence contract requires per-kind `fact_type` identity.** `promotion._result_refusal`
demands every submitted result expose `resolved is True`, NO `reject_code`, AND a
`fact_type` matching the member. `units.Validated*` carry `fact_type` (good), but
`correction_history.ValidatedCorrectionHistory` and the `geometry_validation.Validated*Location`
results do NOT. So the wiring layer must adapt them: wrap a resolved history/location
result in a tiny frozen adapter exposing `resolved=True` + `fact_type=member`, and pass
refusals through unchanged so the gate still fails closed. `test_promotion.py`'s module
note ("real validators' typed results are bound in the state-machine wiring unit, not
here") is pointing at exactly this seam. See `survey_pipeline._FactScopedHistory`.

**Decode is fail-closed by construction, not by convention.** A decoder is reachable
ONLY via `ExtractionJobAuthorized.decoder`, and `routing.begin_extraction_job` returns
that only after `isolation.require_isolation()` yields `ParsingPermitted`. On Windows/any
non-Linux host the probe returns `ParsingDisabled` → `IsolationUnavailable`, so tests must
monkeypatch `routing_module.require_isolation` (module attribute, a test seam) to run the
decode path. `require_isolation` proves boundary PRESENCE only; applying Landlock+seccomp
is the deployed parser's duty (B-001-gated).

**Gated vs raw transition.** `processing → auto_extracted` and both professional-confirmation
edges MUST go through `state.promotion_gated_transition` with `material_fact_verdicts`
(a `{fact_id: PromotionAllowed}` map). Every other edge (e.g. `processing → needs_review`)
uses raw `state.transition`. `DocumentIngestionRecord.apply_transition` delegates to raw
`transition`, so it must NOT be used to drive a gated edge — build the record evolution
from the gated transition's returned `TransitionRecord` instead.

**Reader refusal-as-value.** The in-repo `pdf_*` reader and `interpret_content` never raise;
they return frozen `PdfSyntaxError` / `UnsupportedPdfFeature` values (`.expected` exists on
PdfSyntaxError but NOT on UnsupportedPdfFeature, which has `.feature`/`.detail`). The
concrete `VectorPdfDecoder.decode` preserves this: on refusal it returns the one-element
sequence `(refusal,)`; use `pdf_decode_refusal(seq)` (element-TYPE check, since a valid
single page is also length-1).

**Contract fixtures are validated in-repo by jsonschema 4.26** (importable in the api test
env) via a `referencing.Registry` built from every `packages/contracts/schemas/v1/*.schema.json`
by `$id`; relative `$ref: common.schema.json#/…` resolves against the survey_evidence `$id`.
`python .github/scripts/validate_contracts.py` is the authoritative check.
