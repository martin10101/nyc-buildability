# Research evidence records

One concise record per research question that affects an official property fact, a legal
interpretation, a calculation input, a result or a certainty label (owner directive D-093). The
procedure that says when a record is needed and how it is reviewed is
[`docs/RESEARCH_AND_VERIFICATION.md`](../../RESEARCH_AND_VERIFICATION.md). The research request
queue stays [`docs/RESEARCH_REQUESTS.md`](../../RESEARCH_REQUESTS.md); a request links the records
that answer it.

These records are internal working evidence. They never appear in the architect's main screen or
the PDF summary; the report keeps its own labels and links to the law (ADR-007, the presentation
contract).

The check is `python3 tools/research_record_check.py --check` (run in CI). It checks structure,
references and status only. It cannot say whether a reading of the law is right, and nothing it
prints is a professional verification.

## Records

| Record | Question | Research status |
|---|---|---|
| [NB-01](NB-01-zoning-lot-instruments.json) | 215-16 Northern Boulevard: which recorded instruments establish the current zoning lot, and what is known only from index entries? | access_blocked |
| [NB-02](NB-02-proposed-zfa-scope.json) | Does the permitted 39,934 sq ft proposed zoning floor area already include the retained lot 1 building? | searched_not_found |
| [NB-03](NB-03-rear-yard-short-block.json) | Is the short-block rear-yard provision (ZR 23-344(b)) applicable, and how do the neighbouring line classifications affect the alternative (23-344(c)(3))? | interpretation_awaiting_review |
| [NB-04](NB-04-lot-dimensions-basis.json) | Which lot dimensions come from printed tax-map labels and which from GIS, and what must the named 2017 survey settle? | conflicting_evidence |
| [NB-05](NB-05-special-density-area.json) | Is the lot in a special density area, and what stays conditional in the dwelling-unit count? | answered_from_primary_source |

The status column is copied from each record's `conclusion.research_status`; the record wins.

## Format (`research_record/v1`)

A record is one JSON file named `<record_id>-<slug>.json`. Every key below is required; a list may
be empty only where this table says so. Vocabulary values are exact.

| Key | Content |
|---|---|
| `schema` | `"research_record/v1"` |
| `record_id` | Stable id, for example `NB-05`; the file name starts with it. |
| `title` | One line. |
| `revision`, `last_changed` | Integer from 1, raised on every change of meaning, evidence or linked code; ISO date. |
| `question` | `text`; `property` (address, borough/block/lot) or `"not property-specific"`; `lot_scope` one of `tax_lot`, `zoning_lot`, `zoning_lot_unconfirmed`, `not_lot_specific`; `site_scope` one of `building`, `whole_site`, `not_applicable`; `time_scope` one of `current_law`, `historical_approval`, `both`. |
| `evidence` | Non-empty list. Each: `id` (unique in the record, `E1`, `E2`, ...), `kind`, `authority`, `title`, `url` (http or https), `reference` (document, job, section or dataset id), `page` (or null), `document_date` (effective or last-amended date, as the source states it), `retrieved` (ISO date), `excerpt` (the relevant words or source field, quoted), `saved_copy` (repository path or null), `sha256` (64 hex of the saved copy with line endings normalized to LF, or null when `saved_copy` is null). |
| `evidence[].kind` | One of `law_text`, `dataset_record`, `index_entry`, `filing_record`, `tax_map`, `gis_geometry`, `recorded_instrument`, `approved_plan`, `survey`, `agency_guidance`, `map_document`. An `index_entry` or a `filing_record` never stands for the instrument or the approved plan it points to. |
| `meaning_and_applicability` | `provisions_read` (non-empty list: definitions, parent provisions, exceptions, overlays, field instructions actually opened); `exceptions_considered` (list, may be empty); `reading` (which provisions apply and why); `applies` one of `yes`, `no`, `conditional`, `not_determined`. |
| `measurement_basis` | `quantities` (list, may be empty): each `name`, `value`, `units`, `basis`, `scope`; `basis` one of `law`, `deed`, `survey`, `printed_tax_map`, `approved_plan`, `filing_attribute`, `administrative_record`, `gis`, `derived`; `scope` says existing or proposed and building or whole site. `double_count_risk` (string; `"none identified"` is allowed). |
| `conclusion` | `research_status` (below); `observed_facts` (non-empty list, facts read in a source, no reading of law); `interpretation` (string, may be `""` for a pure fact); `conflicts`, `conditions`, `settled_by` (lists, may be empty). |
| `conclusion.research_status` | One of `not_researched`, `searched_not_found`, `access_blocked`, `conflicting_evidence`, `interpretation_awaiting_review`, `answered_from_primary_source`. |
| `searches` | List. Each: `source`, `query`, `result` one of `found`, `not_found`, `access_blocked`, `conflicting`; `missing_item` (exact document or field, `""` when found); `affected_outputs` (list); `next_step` (`""` when found). Required non-empty when the status is `searched_not_found` or `access_blocked`, with at least one entry of that result naming its missing item and next step. |
| `implementation` | `affected_outputs` (non-empty list of output names, such as `dwelling_units.legal_limit`); `code_paths` (list of repository files, may be empty); `code_identity` (object: each code path to the sha256 of the file with LF line endings; keys equal `code_paths`); `worked_example` (`inputs`, `expected`, `basis`, `prepared_by`); `regression_cases` (list); `dependency_assessment` (list: other rules, scenarios or outputs that use the same reasoning, and what was found). |
| `review` | `producer`; `agent_reviews` (list): each `reviewer` (never the producer), `date`, `reviewed_revision`, `reviewed_code_identity` (as `code_identity`), `verdict` one of `agrees`, `partly_agrees`, `disagrees`, `findings` (list), `report` (repository path or null); `professional_review` null, or `reviewer_name`, `role`, `date`, `reviewed_revision`, `decision`, `comments` (only from a named human; never from an agent). |
| `freshness` | `checked_on` (ISO date); `method` one of `live_fetch`, `snapshot`; `snapshot_date` (ISO date or null); `limitation` (string). |
| `promotion` | `requested_label`: null or one of the six report labels (`Verified`, `Provisional`, `Illustrative`, `Conditional`, `Pending verification`, `Unresolved`). |

Conditional checks:

- `conflicting_evidence` needs a non-empty `conclusion.conflicts`.
- `interpretation_awaiting_review` needs a non-empty `conclusion.interpretation`.
- A `saved_copy` must exist; its `sha256` must match.
- Every `code_paths` file must exist.

Derived (printed by the check, never stored):

- `code_current`: the stored `code_identity` equals the current files. When it does not, the linked
  code changed after the record was written: the record must be rechecked and revised. This is
  reported, not failed, so ordinary code work is never stopped by a record.
- `review_state`: `none` (no agent review), `current` (the latest agent review's
  `reviewed_revision` equals `revision` and its `reviewed_code_identity` equals the current code),
  or `stale`. A stale review never carries over to the changed record.

Promotion to `Verified` (the check fails when a record asks for it and any condition is unmet; the
same function answers for any output name):

1. at least one record lists the output in `implementation.affected_outputs`;
2. every such record is structurally valid;
3. its research status is not `not_researched`, `searched_not_found`, `access_blocked` or
   `conflicting_evidence`, and it has no open `conflicts` or `conditions`;
4. its `review_state` is `current`;
5. a named professional review exists for the current revision;
6. the owner has answered question C1 (what must be true before a result is labelled Verified).
   Until then this condition always refuses, so nothing is Verified.

Every other label stays possible: draft and conditional work never waits for this check.
