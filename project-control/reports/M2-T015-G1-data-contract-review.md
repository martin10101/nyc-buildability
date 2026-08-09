# G1 Gate Report — M2-T015 (Secure survey-document ingestion / survey-evidence data contract)

**Reviewer:** data-contract-verifier (independent, read-only)
**Reviewed SHA:** `897e7df6c29753008a14fbb4c1457752e19ed2e0`
**Worktree:** `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m2t015`
**Scope:** G1 = the survey-evidence data contract, its fixtures, the assembler's conformance, and schema-drift discipline (NOT the connector/parser internals).

> Saved verbatim by the orchestrator (report-preservation). Reviewed at `897e7df`; a behavior-preserving
> ruff-0.13.0 lint fix followed, carrying a reviewer delta-attestation. Reviewer's "no `directive_refs`
> array" note reflects the stale branch copy of the task file; main's authoritative `M2-T015.json` carries
> `directive_refs: [{D-010, ALL}]` and the DCV pass covers the derived 97-requirement set.

## VERDICT: PASS

---

## What I reproduced (commands + outcomes)

| Check | Command | Result |
|---|---|---|
| Contract validator (authoritative captured evidence) | `python .github/scripts/validate_contracts.py` | `Checked 10 schema file(s); 0 failure(s).` exit 0 — **reproduced** |
| Engine mode | (banner) | `stdlib mini-validator + jsonschema 4.26.0 (cross-checked)` — stronger than CI's degraded runner; any mini/engine disagreement fails the build |
| Schema meta-validation | (same run) | `OK packages\contracts\schemas\v1\survey_evidence.schema.json (Survey Evidence Fact ...)` |
| TS drift discipline | `python packages/contracts/scripts/generate_ts_types.py --check` | survey_evidence up to date; property_profile / rule_evaluation / scenario all still byte-identical; exit 0 |
| Assembler conformance (SB-S8) + regression | `python -m pytest tests/documents/test_survey_pipeline.py -q` | `26 passed` |
| Full documents suite | `python -m pytest tests/documents -q` | `925 passed, 1 skipped` |

The SB-S8 test (`test_survey_pipeline.py:305`) drives the **actual pipeline** (`run_survey_extraction`) and validates every emitted `survey_evidence` record against the v1 schema using the real `jsonschema` `Draft202012Validator` with the cross-file `$ref` registry — so conformance of live assembler output is proven, not just of the hand-authored fixture.

## Contract field-by-field soundness

- **Required set (15 keys)** matches the owner-directive 2026-07-20 §3 evidence-record list: document digest, page, bounding-box/object locator, verbatim original value, normalized value + units, extraction method, confidence, validation results, correction history, professional-confirmation state. The assembler `services/api/app/documents/extraction/survey_pipeline.py::_build_fact` (lines 351–372) emits **all 15**; nothing required is omitted.
- **`document_digest`** correctly uses a dedicated `raw_bytes_digest_sha256` `$def` (`^sha256:[0-9a-f]{64}$`) with semantics distinct from `common.digest_sha256` (raw upload bytes, not canonical-JSON) — correct per the directive ("digest of the exact original uploaded bytes").
- **Closed enums are grounded, not improvised:** `extraction_method` = the 6 format-policy-authorized paths (native DWG deliberately excluded → rejected); `validation_results.check_id` = the 11 directive-named deterministic checks verbatim; `status` includes the fail-closed `unresolved`; `professional_confirmation.state` ∈ {unconfirmed, confirmed, rejected}; `corrected_by_role` ∈ {user, qualified_professional}; `coordinate_space` ∈ {pdf_user_space_points, raster_pixels} with documented origin/units.
- **`additionalProperties:false`** on the root and every nested object (location, bounding_box, validation item, correction entry, professional_confirmation, extraction_tool) — closed contract from birth.
- **Conditional integrity** encoded via `allOf`/`anyOf`+`const` (the documented keyword-subset workaround for absent `if/then`): locator kind ⇒ required locator; fail/unresolved ⇒ non-empty `detail`; confirmation state ⇔ null/non-null identity+timestamp.

## Units / null / unknown semantics

- **`units` required + explicitly `null` when unitless** — absence is a visible statement, never silent omission. Assembler sets `None` for the (unitless) scale-ratio and BBL facts — correct.
- **`detail` null ONLY on pass** — every fail/unresolved must say why (fail-closed reviewability).
- **`confirmed_by`/`confirmed_at` null exactly while unconfirmed** — enforced in **both** directions.
- **`original_value`/`normalized_value`** typed as any-JSON (→ `unknown` in TS) — appropriate for verbatim vs deterministically-normalized values; `original_value` immutable, corrections flow through append-only `correction_history`.
- **No fabrication where source is silent:** the assembler classifies only two EXACT canonical patterns (`SCALE_RATIO_PATTERN`, `BBL_PATTERN`, `_classify_text_run` lines 296–313); unmatched runs are left unassembled (never coerced). `confidence=1.0` is the schema's documented doctrine for deterministic embedded-text reads and never promotes a value; every fact is born `unconfirmed`.

## Fixture behavior — both directions

- **5 valid** fixtures pass (incl. the new `assembled_embedded_text_scale_statement.json`, plus vector-object, OCR-unresolved, AI-classified-unresolved, and corrected+confirmed) — covering vector/raster locators, both coordinate spaces, unitless/feet/square_feet/degrees/feet_per_inch units, structured `original_value`, populated correction history, and confirmed state.
- **8 invalid** fixtures each rejected for the **intended** reason reported first: bad digest (pattern), confirmed-without-identity (anyOf), failed-check-without-detail (anyOf), vector-kind-missing-object_reference (anyOf), missing document_digest (required), missing units key (required), unapproved extraction_method (enum), undocumented field (additionalProperties).

## Independent adversarial cases (beyond committed fixtures, dual-engine cross-checked)

- **Reverse conditional not covered by any fixture** — `state:"unconfirmed"` with a non-null `confirmed_by` → correctly rejected (`$.professional_confirmation: does not satisfy any schema in anyOf`). This proves the conditional constrains the unconfirmed branch too, not just the confirmed branch.
- **Schema drift** — `check_id:"new_future_check"` → rejected with the closed-enum error.
- **Ambiguous/invalid** — `confirmed_at:"yesterday"` → pattern rejection; `location.kind:"bounding_box"` with no `bounding_box` → anyOf rejection.
All agreed between the stdlib mini-validator and jsonschema 4.26.

## Provenance completeness

Every assembled fact carries full lineage: immutable-original `document_digest`, `page_number`, page-space `location` (bbox with `coordinate_space`), verbatim `original_value`, deterministic `normalized_value`+`units`, `extraction_method`, `extraction_run_id`, `extracted_at`, `confidence`, per-fact `validation_results`, append-only `correction_history`, and born-`unconfirmed` `professional_confirmation`. Document-level provenance is deliberately joined via `document_digest` (not duplicated per fact), consistent with the ingestion-architecture doc. This is a coherent sibling to `source_fact` (API-lineage) provenance.

## Schema-drift discipline

`generate_ts_types.py` adds `survey_evidence` as an independent 4th artifact; `--check` byte-compares and the other three generated `.ts` files remain byte-identical. `generated/survey_evidence.ts` faithfully mirrors the schema (closed enums, `string | null` nullables, optional keys, no index signature since root is closed). `validate_contracts.py` is directory-driven so the new schema + fixtures are picked up automatically; both engines cross-check.

## Advisory notes (NOT defects; no action required for PASS)

1. **`_expected_failure` marker key in invalid fixtures** also trips `additionalProperties:false`, so each invalid fixture technically fails for two reasons. I verified the validator emits the *intended* reason first (required- and property-checks precede the additionalProperties check in `validate_instance`), so reason-correctness holds today. It is a latent fragility (if the intended defect were ever removed, the marker alone would keep the fixture red and mask the regression), but it is the established repo pattern (`source_fact` invalid fixtures do the same) — consistent, not a new problem.
2. **`fact_type` and `units` are open vocabularies in 1.0.0** — documented "OPEN-WITH-FLAG"; the closed `fact_type` taxonomy lands additively with the grounding implementation. Deliberate and documented; acceptable at G1.
3. **TS cannot express conditional required-ness** (`bounding_box`/`object_reference`/`confirmed_by`), so they surface as optional/nullable base types — correct structural mapping; the conditionals are runtime-enforced by the schema.
4. **Empty `validation_results` is schema-valid** (documented "no check has run yet"); material-influence gating is the backend state machine's job, not the contract's. Documented, intentional.

## Environment note

The session's read-only guard intermittently blocked multi-statement inline `python -c` probes and all shell file-writes/redirection. I worked around this with single-statement inline validations and the repo's own pytest suites (explicitly permitted test execution). All conclusions above were reproduced by commands that executed successfully; nothing is asserted on un-run evidence.

**G1 verdict: PASS.** The survey-evidence v1 contract is field-complete against the owner directive, sound in units/null/unknown/enum semantics, closed from birth, drift-guarded, and the deterministic assembler emits fully-provenanced records that conform to it with nothing fabricated where the source is silent. Both fixture directions and independent adversarial cases behave correctly.

---

## G1 Delta-Attestation — at merged main HEAD `1b3af35` (post-rework)

**G1 PASS (reviewed at `897e7df`) STANDS at `1b3af35`.** Verified by the same independent data-contract-verifier:
- `git diff --stat 897e7df 1b3af35 -- packages/contracts/` → **empty**; the exact G1 surface
  (`survey_evidence.schema.json`, `generated/survey_evidence.ts`, valid/invalid `survey_evidence` fixtures,
  `generate_ts_types.py`) is **byte-identical**.
- `python .github/scripts/validate_contracts.py` → `Checked 10 schema file(s); 0 failure(s).` exit 0 (14 OK lines).
- The rework (lint + the document fixture PACK + matrix + report) touched nothing in the G1 contract surface.

**Verdict: G1 PASS holds at `1b3af35`.**
