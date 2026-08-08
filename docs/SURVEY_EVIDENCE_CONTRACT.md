# Survey Evidence Contract (canonical)

**Status:** Canonical field-by-field contract for
`packages/contracts/schemas/v1/survey_evidence.schema.json` (survey_evidence contract **1.0.0**).
Produced by task **M2-T015** (owner directive 2026-07-20 section 3, survey workstream Packet B),
contract-first unit. The JSON Schema is the machine-enforced source of truth; this document explains
every field, the conditional integrity rules, and the boundaries the contract encodes. On any
conflict, the schema wins and this document has a defect.
**Companions:** `docs/SURVEY_DOCUMENT_FORMAT_POLICY.md` (M2-T014 supported-format decisions — hard
input); `docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md` (produced by a later M2-T015 unit: document
state machine, per-format pipeline, storage design under the B-001 hold).

## 1. Purpose and doctrine

One `survey_evidence` record is the complete provenance record of **ONE fact extracted from one
uploaded survey / official document** — a boundary dimension, a stated area, a scale statement, a
north-arrow orientation, an elevation, an address block. The owner directive requires every
extracted fact to preserve: original document digest; page number; bounding box or object
reference; original detected text/value; normalized value and units; extraction method; confidence;
validation results; correction history; professional-confirmation state. This contract is that
list, field for field.

Three permanent rules shape every field:

1. **Extraction doctrine.** The pipeline is never "OCR reads the survey". `extraction_method`
   records which per-format path actually produced the detection, and only paths the format policy
   approves exist in the enum. OCR and line/symbol detection on raster content are **advisory**,
   never authoritative.
2. **Fail-closed principle.** No value becomes canonical geometry or a material buildability input
   because a model expressed high confidence. Promotion requires deterministic validation plus
   qualified-human confirmation; a material value that cannot be independently validated surfaces
   as a **visible `unresolved` validation result**, never a silent pass (acceptance scenarios
   SB-S3, SB-S5).
3. **AI retrieves/classifies; deterministic code calculates; qualified humans approve.**
   `normalized_value` is produced by deterministic normalization code, validation checks are
   deterministic code, and only a qualified professional moves `professional_confirmation` out of
   `unconfirmed`.

## 2. What this record is — and is not

- **A sibling of `source_fact`, not a replacement.** API-retrieved facts (`source_fact`) carry
  dataset/request lineage (`dataset_version`, `request_url`, `observation_id`); document-extracted
  facts carry document/page/location lineage (`document_digest`, `page_number`, `location`). Both
  share `common.schema.json` definitions and the same PRD section 9 provenance discipline. Reusing
  `source_fact` was rejected because its required field set (dataset version, source field name)
  has no truthful meaning for an uploaded document — and this platform never fills required
  provenance fields with invented values.
- **Per-fact, not per-document.** Document-level provenance — original filename, uploader, upload
  timestamp, declared document class, server-sniffed MIME type, size, storage location, conversion
  lineage — lives on the document ingestion record (ingestion architecture doc) and is joined via
  `document_digest` (and `document_ref` once B-001 unblocks storage ids). It is deliberately not
  duplicated on every fact.
- **Evidence, not judgment.** The record states what was detected, how, where, with what
  validation outcomes and what human decisions. Evidentiary *weight* (survey vs tax map vs proposed
  plan) is governed by the document class taxonomy
  (`docs/research/survey-document-sources-2026-07.md` §9) and qualified humans — never by this
  record's format or confidence fields.
- **Closed from birth.** `additionalProperties: false` (following the M2-T017 `source_fact`
  hardening): an undocumented or mistyped key is rejected, never silently accepted into a
  mandatory evidence record.

## 3. Identity and joins

| Identity | Field | Lifetime / meaning |
| --- | --- | --- |
| Evidence record | `evidence_id` | Unique platform-wide; how downstream consumers cite the fact. |
| Original document | `document_digest` | Content identity of the exact original uploaded bytes; shared by all facts of one document; survives any storage migration. |
| Ingestion record | `document_ref` (optional) | Platform id of the document record; optional while B-001 blocks production storage ids. |
| Extraction run | `extraction_run_id` (optional) | One isolated processing job over one document, run only inside the verified, fail-closed parser isolation boundary (`docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md` §5) — never a plain, merely-separated child process; when the boundary cannot be verified, parsing is disabled (typed `isolation_unavailable`) and no run id is ever minted. Shared by all facts the run produced (analogous to the retrieval-event segment of `source_fact.observation_id`). |

Re-extraction of the same document mints a **new** run id and **new** evidence records; existing
records are never mutated. Corrections append to `correction_history`; `original_value` is
immutable forever.

## 4. Field-by-field reference

Requirement column: **R** = required key, **O** = optional key. "Nullable" means the key must be
present and may be explicitly `null` — visible absence, never silent omission.

### 4.1 Document lineage and target property

| Field | Req | Type | Meaning |
| --- | --- | --- | --- |
| `evidence_id` | R | non-empty string | Stable unique id of this evidence record. Construction is implementation-defined and documented by the ingestion module (suggested `sev:<digest-prefix>:p<page>:<sequence>`); synthetic/test records use a clearly non-official construction. |
| `bbl` | R | BBL (common pattern) | **Target** property the upload was submitted against — upload *intent*, never a verified association. The `address_bbl_match` check records whether the document actually pertains to it; a mismatch is flagged, never silently ingested (SB-S7). |
| `document_digest` | R | `sha256:` + 64 hex | Digest of the **exact original uploaded bytes** (raw-bytes semantics — local `$defs/raw_bytes_digest_sha256`, deliberately NOT the canonical-JSON `digest_sha256` of `common.schema.json`, because an uploaded document has no canonical JSON form; mirrors `legal_source_manifest.raw_capture.raw_sha256`). If extraction ran on a converted derivative (e.g. a future validated DXF→vector-PDF stage), this still digests the ORIGINAL upload; conversion lineage is document-level. |
| `document_ref` | O | non-empty string | Join key to the document ingestion record. Optional because production private-object storage and its ids are B-001-blocked; the digest, not the ref, is the content identity. |
| `page_number` | R | integer ≥ 1 | 1-based page of the original document the fact was detected on. Single-image uploads use 1; each multi-frame TIFF frame is one page. Lets a reviewer open the exact page of the immutable original. |

### 4.2 Location on the page

`location` (R, object) — the directive's "bounding box or object reference". `kind` selects the
mandatory locator:

| Field | Req | Type | Meaning |
| --- | --- | --- | --- |
| `location.kind` | R | enum `bounding_box` \| `vector_object` | `bounding_box` for raster paths, text runs, and AI-classified regions; `vector_object` for the vector-object extraction path of the open PDF container. |
| `location.bounding_box` | conditional | object | Required when `kind` = `bounding_box`; optional display-highlight extra when `kind` = `vector_object`. Fields: `x_min`, `y_min`, `x_max`, `y_max` (numbers) + `coordinate_space`. |
| `location.bounding_box.coordinate_space` | R (in box) | enum `pdf_user_space_points` \| `raster_pixels` | Never guessed. `pdf_user_space_points`: default PDF user space of the unrotated page, 1 unit = 1/72 inch (ISO 32000 default; a page-level `UserUnit` override is recorded on the document record), origin lower-left, y up. `raster_pixels`: decoded page/frame pixels, origin top-left, y down. Page coordinates are never survey/world coordinates. |
| `location.object_reference` | conditional | non-empty string | Required when `kind` = `vector_object`: stable implementation-documented reference to the vector content object (e.g. a content-stream object path), stable for the stored immutable original. |

`x_min ≤ x_max` / `y_min ≤ y_max` are enforced by deterministic validation code — cross-field
numeric comparison is outside the repository's contract keyword subset
(`.github/scripts/validate_contracts.py` allowlist), and the contract never pretends otherwise.

### 4.3 Value

| Field | Req | Type | Meaning |
| --- | --- | --- | --- |
| `fact_type` | R | non-empty string | What the fact IS (`boundary_segment_distance`, `stated_lot_area`, `scale_statement`, `north_arrow_orientation`, `elevation_value`, `address_text`, …). **OPEN-WITH-FLAG** in 1.0.0: the closed taxonomy is produced by the implementation unit together with the deterministic checks that ground it, and lands as an additive enum then (same precedent as v1's deliberately-unenumerated zoning district codes). |
| `original_value` | R | any JSON type | Verbatim detection, before any cleanup: raw OCR text, exact embedded text-run content, raw vector object data (may be structured), or the schema-constrained AI output verbatim. **Immutable** — corrections never touch it. |
| `normalized_value` | R | any JSON type | Deterministically normalized current value (post-correction when corrections exist). Produced by normalization code, never AI. Never silently blanked or coerced — an unvalidatable material value fails closed via an `unresolved` validation result instead. |
| `units` | R, nullable | string \| null | Units of `normalized_value`; explicitly `null` when unitless, so absent units are always a visible statement. Open vocabulary in 1.0.0 (mirrors `source_fact.units`; examples `feet`, `square_feet`, `degrees`, `feet_per_inch`). A unit-ambiguous detection (mixed units, decimal ambiguity — core task fixture classes) surfaces as a failing/unresolved `units_consistency` check, never as a silently guessed unit. |

### 4.4 Extraction provenance

| Field | Req | Type | Meaning |
| --- | --- | --- | --- |
| `extraction_method` | R | closed enum | Which approved per-format path produced the detection: `vector_object_extraction` (vector PDF), `embedded_text_extraction` (born-digital PDF text layer), `ocr_text` (scanned text — advisory only), `line_symbol_detection` (scanned geometry — advisory), `ai_assisted_classification` (bounded, schema-constrained; never canonical without independent validation), `deterministic_geometry_reconstruction` (derived fact built deterministically from extracted primitives). Grounded verbatim in the M2-T015 extraction doctrine + format policy. Unapproved paths (e.g. native DWG parsing — format policy row 7, DEFERRED) cannot appear; new paths are added additively only after the format policy approves them. |
| `extraction_tool` | O | object `{name, version}` | Tool provenance of the detection (both keys required when present — a tool without a version is not reproducible). Mirrors the format policy's conversion rule "records the tool + version". |
| `extraction_run_id` | O | non-empty string | See §3. |
| `extracted_at` | R | RFC 3339 timestamp | When the extraction run produced the detection (extraction time; upload time is document-level). |
| `confidence` | R | number 0–1 | Extraction-path confidence in the **detection**: deterministic reads of digitally-authored content use 1; OCR/line-detection/AI report model confidence. Confidence **never** promotes a value (PRD section 12; fail-closed principle) — see §6. |

### 4.5 Validation results

`validation_results` (R, array; may be empty) — outcomes of the deterministic checks run against
this fact. An empty array is the visible statement "no deterministic check has run yet"; the
backend state machine (not this contract) forbids a fact with material influence from resting
there. Each item:

| Field | Req | Type | Meaning |
| --- | --- | --- | --- |
| `check_id` | R | closed enum | Exactly the M2-T015 required deterministic checks: `address_bbl_match`, `units_consistency`, `scale_consistency`, `north_orientation`, `boundary_closure`, `area_vs_stated`, `segment_sum`, `contradictory_dimensions`, `geometry_validity`, `elevation_consistency`, `tax_lot_geometry_comparison`. Only the checks actually run against THIS fact appear. `tax_lot_geometry_comparison` records divergence from accepted MapPLUTO/tax-lot geometry as a **typed comparison result** — the cross-check never silently overrides a licensed survey (SB-S4). Additive extension with the implementation that grounds new checks. |
| `status` | R | enum `pass` \| `fail` \| `unresolved` | `pass`: check confirmed the value. `fail`: check ran and found a contradiction. `unresolved`: check **could not** independently validate the value — the fail-closed visible unresolved condition; never omitted, never coerced to `pass`. |
| `detail` | R, nullable | string \| null | Why. May be `null` only on `pass` (schema-enforced conditional): every `fail`/`unresolved` must state its reason, because an unexplained unresolved condition is not reviewable. |
| `expected_value` | O | any | Comparison basis (e.g. stated area for `area_vs_stated`), carried so the outcome is reproducible from the record. |
| `observed_value` | O | any | What the check computed/observed (e.g. calculated polygon area, closure gap). |

### 4.6 Correction history

`correction_history` (R, array; may be empty) — **append-only**, oldest first; empty = "never
corrected". Entries are never edited or deleted; `original_value` is never touched; each entry
preserves both sides of the change so every historical state is reconstructable. Each entry:

| Field | Req | Type | Meaning |
| --- | --- | --- | --- |
| `corrected_at` | R | RFC 3339 timestamp | When the correction was made. |
| `corrected_by_role` | R | enum `user` \| `qualified_professional` | Who (by role) corrected — grounded in the PRD section 5 confirm/correct flow and the qualified-human boundary. Deterministic code never "corrects" (re-extraction makes new records); AI may never write a correction. |
| `corrected_by` | O | non-empty string | Actor id; optional in 1.0.0 because the identity scheme is owned by the B-001-blocked auth/storage design. The role is always required. |
| `previous_normalized_value` | R | any | Value before the correction, verbatim. |
| `corrected_normalized_value` | R | any | Value after the correction (equals current `normalized_value` on the latest entry — code-enforced invariant, §5). |
| `previous_units` / `corrected_units` | R, nullable | string \| null | Units on each side, so a unit change (decimal/unit-ambiguity fix) is always visible. |
| `reason` | R | non-empty string | Human-readable reason; a correction with no stated reason is rejected. |

### 4.7 Professional confirmation

`professional_confirmation` (R, object) — the per-fact qualified-human approval boundary, distinct
from the document-level state machine
(`uploaded/processing/auto_extracted/needs_review/rejected/professionally_confirmed`, ingestion
architecture doc).

| Field | Req | Type | Meaning |
| --- | --- | --- | --- |
| `state` | R | enum `unconfirmed` \| `confirmed` \| `rejected` | Every extracted fact is born `unconfirmed` regardless of method, confidence, or passing checks — nothing is born confirmed. Only a qualified human moves a fact out of `unconfirmed`; never AI, never a score, never a passing check alone. `rejected` = the professional rejected the detection (a correction + re-confirmation, or a re-extraction, produces the usable value). |
| `confirmed_by` | R, nullable | string \| null | Professional's platform id; `null` exactly while `unconfirmed` (schema-enforced conditional). Licensure/qualification records are an auth-design concern referenced by this id, not embedded. |
| `confirmed_at` | R, nullable | RFC 3339 \| null | Timestamp of the confirmation/rejection; `null` exactly while `unconfirmed`. |
| `note` | O, nullable | string \| null | Free-text note from the professional; never a substitute for a required field. |

## 5. Integrity rules

**Schema-enforced conditionals** (encoded with `allOf`/`anyOf`/`const` because `if`/`then` is
outside the `validate_contracts.py` keyword subset — same pattern as
`property_profile.reproducibility.staleness`):

1. `location.kind = "bounding_box"` ⇒ `bounding_box` present; `kind = "vector_object"` ⇒
   `object_reference` present (a vector-object location may also carry a display bounding box).
2. Validation `status` ∈ {`fail`, `unresolved`} ⇒ `detail` is a non-empty string.
3. `professional_confirmation.state = "unconfirmed"` ⇒ `confirmed_by`/`confirmed_at` are `null`;
   `state` ∈ {`confirmed`, `rejected`} ⇒ both are non-null and well-formed.

**Code-enforced invariants** (deterministic ingestion/validation code — outside the contract's
keyword subset, and the contract says so rather than pretending):

- `x_min ≤ x_max`, `y_min ≤ y_max` within a bounding box.
- `evidence_id` uniqueness; `document_digest` equals the stored original's digest.
- The latest `correction_history` entry's `corrected_normalized_value`/`corrected_units` equal the
  record's current `normalized_value`/`units`; entries are chronologically ordered and append-only.
- A fact with material buildability influence may not rest with empty `validation_results` or in a
  promoted state without confirmation — owned by the backend state machine.

## 6. Fail-closed and AI boundary (what this contract makes impossible to hide)

- A high-`confidence` AI or OCR value with no independent validation shows exactly that: its
  `validation_results` carry `unresolved` with a stated reason, and `professional_confirmation`
  stays `unconfirmed`. Nothing in the record lets confidence stand in for validation (SB-S5).
- Survey-vs-tax-lot divergence is a typed `tax_lot_geometry_comparison` result; the record has no
  mechanism for replacing a survey value with the cross-check value (SB-S4).
- A wrong-address document shows a failing `address_bbl_match` on facts extracted under the target
  `bbl` — the mismatch is visible, never silently absorbed (SB-S7).
- Every human intervention is an append-only, reasoned, role-attributed `correction_history` entry;
  the original detection remains verbatim forever.

## 7. Fixtures (SB-S8)

Under `packages/contracts/fixtures/{valid,invalid}/survey_evidence/`; CI validates both directions
(an "invalid" fixture that passes fails the build). All fixtures are synthetic
(`test-fixture-synthetic` ids, obviously-synthetic digests); no client documents.

**Valid** — representative lifecycle coverage:

| Fixture | Demonstrates |
| --- | --- |
| `vector_pdf_boundary_segment.json` | Vector-object path (not OCR) on a vector PDF; object reference + display box; deterministic confidence 1; passing checks; born `unconfirmed`. |
| `ocr_stated_area_unresolved.json` | Advisory OCR on a scan; `area_vs_stated` **unresolved** with stated reason — high confidence fails closed. |
| `corrected_confirmed_scale_fact.json` | OCR misread → append-only professional correction (value 20→30, verbatim `original_value` untouched) → passing re-validation → `confirmed`. |
| `ai_classified_orientation_unresolved.json` | Bounded AI classification (structured `original_value`) with 0.98 confidence that still fails closed: `north_orientation` unresolved, `unconfirmed`. |

**Invalid** — each targets one mechanism (`_expected_failure` states the defect):

| Fixture | Rejected because |
| --- | --- |
| `missing_document_digest.json` | Required document lineage key absent. |
| `bad_document_digest_format.json` | `md5:abc` violates the SHA-256 digest pattern. |
| `undocumented_field_rejected.json` | Closed contract rejects an undocumented key. |
| `unapproved_extraction_method.json` | `native_dwg_parse` — format policy row 7 defers DWG; not in the closed enum. |
| `location_missing_object_reference.json` | `kind=vector_object` without its mandatory locator (conditional 1). |
| `failed_check_without_detail.json` | `fail` with `detail: null` (conditional 2). |
| `confirmed_without_professional_identity.json` | `confirmed` with null identity/timestamp (conditional 3). |
| `missing_units_key.json` | `units` key omitted — absence must be visible, not silent. |

## 8. Versioning and scope

- Versioned by the `/v1/` `$id` directory; within v1 all changes are **additive** (new optional
  keys, additive enum extensions; required keys never removed/renamed, patterns never tightened).
  Breaking changes require `/v2/` + a migration note (package versioning rules,
  `packages/contracts/README.md`).
- **Not yet a TypeScript typegen target:** the first cross-tier TS consumer is the Packet C upload
  UI (M2-T016); adding `survey_evidence` to `packages/contracts/scripts` `SCHEMA_FILES` is an
  additive follow-up decided with that task. Fixture validation is active immediately — the CI
  `contracts` job discovers the schema and both fixture directories automatically by name.
- Storage honesty: nothing in this contract requires production storage; `document_ref` is optional
  precisely because B-001 blocks storage provisioning, and the contract stays complete without it.
