/**
 * SUCCESS-PATH bounding for a validated scenario document (task M5-T004
 * rework; the G5 "Required spec" table).
 *
 * scenario-api.ts has always documented that "All reflected server text is
 * length-capped and control-stripped" — which was true only of the FAILURE
 * path. This module makes it true of the success path too, which matters far
 * more after the rework, because the rework surfaces ~19 previously-dropped
 * server-controlled fields (every `constraints[].note`, every
 * `assumptions[].rationale`, the full citation block) onto the screen.
 *
 * THE THREE RULES, AND WHY THEY DIFFER
 *
 *   ARRAYS      reject (scenario-contract.ts, MAX_DOCUMENT_ARRAY_LENGTH = 64).
 *   FREE TEXT   truncate, VISIBLY (here, MAX_REFLECTED_TEXT_LENGTH = 600 and
 *               TRUNCATION_MARKER, both already established by bounded.ts).
 *   IDENTIFIERS reject (scenario-contract.ts `checkTokenRepresentable`).
 *
 * Truncating an array would SILENTLY DROP contract content — exactly the defect
 * class this packet was failed for — so an over-long array is rejected as a
 * contract problem instead.
 *
 * Free text truncates because that truncation ANNOUNCES ITSELF: bounded.ts:16-17
 * establishes that a shortened string carries "… [truncated]". That guarantee
 * is a property of `boundedText` ALONE, and an earlier revision of this file
 * over-claimed it for the whole module. `boundedToken` shortens and strips
 * SILENTLY — no marker, and a fully-stripped value becomes empty — so it can
 * never be the last word on an identifier. It is now preceded by a validator
 * check that rejects any value it would alter, which makes every `identifier()`
 * call below a proven no-op rather than a quiet rewrite of a pointer to legal
 * authority.
 *
 * WHAT IS DELIBERATELY *NOT* BOUNDED, and why. Everything excluded below is a
 * MATERIAL value, and the frontend never transforms a material value:
 *
 *   - `draft_zoning_floor_area_cap_sq_ft` and every other number: bounding a
 *     number is arithmetic on a legal value. Never.
 *   - `constraints[].value` / `assumptions[].value`: the constraint values
 *     themselves ("R5", 10000). Truncating one would corrupt a legal value.
 *     They are instead made safe by TYPE: the validator now pins them to
 *     number | string | boolean | null, which closes the object-into-the-DOM
 *     path G5 finding 2 identified (format.ts JSON.stringify) at the source.
 *   - `evaluated_input.bbl`: the document's own identity, compared against the
 *     requested BBL to surface a mismatch. Sanitizing it could turn a real
 *     mismatch into an apparent match — the opposite of the honesty this
 *     rework restores. It is bounded at RENDER instead (ScenarioProvenance).
 *   - `evaluated_input.input_fingerprint`: already pinned by the validator to
 *     `^sha256:[0-9a-f]{64}$`, a strictly tighter bound than 64 chars.
 *   - `cap_provenance.rule_status`: bounded by ENUMERATION to 4 exact values,
 *     which is strictly stronger than a 64-character truncation, and applying
 *     `boundedToken` would force an unsafe cast back to the union.
 *   - `constraints[].provenance` (schema type `unknown`): bounded where it is
 *     read, by the display readers in scenario-display.ts, since nothing here
 *     may assume its shape.
 */

import {
  MAX_REFLECTED_TEXT_LENGTH,
  MAX_TOKEN_LENGTH,
  boundedText,
  boundedToken,
} from "./bounded";
import type { Scenario, ScenarioCitation } from "./scenario-contract";

/**
 * Maximum accepted `Content-Length` for a scenario response, checked BEFORE
 * `.json()` so a hostile or misbehaving upstream cannot make the tab parse
 * megabytes. 256 KiB is ~40x the largest committed fixture. A larger (or
 * differently-shaped) response is REJECTED into the already-tested
 * `unexpected_response` state — never partially read.
 */
export const MAX_RESPONSE_BYTES = 256 * 1024;

/**
 * Free-text bound: control-stripped and truncated at 600 with the explicit
 * marker. The fallback is the EMPTY STRING deliberately — `boundedText`'s
 * fallback fires only when the value is not a string (impossible here: the
 * validator ran first) or when it cleans to empty, and substituting invented
 * copy for a string the server actually sent would be a silent default. An
 * empty result means the server sent only whitespace or control characters,
 * and that is what renders.
 */
function freeText(value: string): string {
  return boundedText(value, "", MAX_REFLECTED_TEXT_LENGTH);
}

/** Rendered in place of an identifier this client cannot display faithfully.
 * Unreachable while the validator runs first — kept because a silent blank is
 * the one outcome an identifier field must never produce, and a defence that
 * only works when nothing upstream is broken is not a defence. */
export const UNREPRESENTABLE_IDENTIFIER = "(identifier not representable)";

/**
 * Machine-identifier bound: allowlisted charset, capped at 64.
 *
 * This is now a BACKSTOP, not the control. `checkTokenRepresentable` rejects
 * the whole document during validation if this call would change anything, so
 * by the time it runs it is a proven no-op — which is what lets an identifier
 * be trusted as a pointer to the record it names.
 *
 * If it ever does fire, it says so: a value with no surviving character
 * renders as an explicit "not representable" rather than a blank, because a
 * blank reads as "the document did not state one" and would un-do the
 * non-empty guarantee the validator established for it.
 */
function identifier(value: string): string {
  // An EMPTY identifier is representable — it is empty. `cap_provenance.rule_id`
  // and `.rule_version` are propagated from the trace and may legitimately
  // arrive empty (the validator deliberately permits it rather than turning a
  // defective rule record into a total outage), so emptiness must survive as
  // emptiness and be labelled by the renderer, not relabelled here.
  if (value === "") return "";
  return boundedToken(value, MAX_TOKEN_LENGTH) ?? UNREPRESENTABLE_IDENTIFIER;
}

/**
 * Unit-label bound: control-stripped and capped at the same 64 characters as a
 * machine identifier, but through `boundedText` rather than `boundedToken`.
 *
 * A unit renders raw beside a legal value, so it needed a bound — but it is NOT
 * safe to put through the token allowlist. `boundedToken` keeps only
 * [A-Za-z0-9._-] and drops the rest SILENTLY, so `"sq ft"` would render as
 * `"sqft"` and `"m³"` as `"m"` — a quietly rewritten unit attached to a number,
 * which is the same defect class as a quietly dropped field. `boundedText`
 * delivers the identical 64-character cap and the same control-character
 * stripping, and when it does shorten, it says so with TRUNCATION_MARKER.
 *
 * `null` stays `null`: "no unit recorded" and "a unit that bounded to empty"
 * are different statements, and the renderers distinguish them.
 */
function unitLabel(value: string | null): string | null {
  return value === null ? null : boundedText(value, "", MAX_TOKEN_LENGTH);
}

function boundCitation(citation: ScenarioCitation): ScenarioCitation {
  return {
    ...citation,
    snapshot_id: identifier(citation.snapshot_id),
    section: freeText(citation.section),
    quote: freeText(citation.quote),
    last_amended:
      typeof citation.last_amended === "string"
        ? freeText(citation.last_amended)
        : citation.last_amended,
  };
}

/**
 * Return a bounded COPY of an already-validated scenario document. Pure: the
 * input is never mutated, so a caller holding the raw body still holds the raw
 * body.
 */
export function boundScenarioDocument(document: Scenario): Scenario {
  return {
    ...document,
    not_verified_disclaimer: freeText(document.not_verified_disclaimer),
    evaluated_input: {
      ...document.evaluated_input,
      profile_contract_version: identifier(
        document.evaluated_input.profile_contract_version,
      ),
      rule_evaluation_contract_version: identifier(
        document.evaluated_input.rule_evaluation_contract_version,
      ),
    },
    constraints: document.constraints.map((constraint) => ({
      ...constraint,
      key: identifier(constraint.key),
      unit: unitLabel(constraint.unit),
      note: freeText(constraint.note),
    })),
    cap_label: document.cap_label === null ? null : freeText(document.cap_label),
    cap_provenance:
      document.cap_provenance === null
        ? null
        : {
            ...document.cap_provenance,
            rule_id: identifier(document.cap_provenance.rule_id),
            rule_version: identifier(document.cap_provenance.rule_version),
            output_name: identifier(document.cap_provenance.output_name),
            note: freeText(document.cap_provenance.note),
            citations: document.cap_provenance.citations.map(boundCitation),
          },
    assumptions: document.assumptions.map((assumption) => ({
      ...assumption,
      key: identifier(assumption.key),
      assumption_type: freeText(assumption.assumption_type),
      unit: unitLabel(assumption.unit),
      rationale: freeText(assumption.rationale),
    })),
    reasons: document.reasons.map(freeText),
    coverage_matrix: document.coverage_matrix.map((row) => ({
      ...row,
      constraint_family: identifier(row.constraint_family),
      governs: freeText(row.governs),
    })),
    integrity_check: {
      ...document.integrity_check,
      method: freeText(document.integrity_check.method),
      note: freeText(document.integrity_check.note),
    },
  };
}
