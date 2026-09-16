import { boundedText } from "@/lib/bounded";
import { formatValue } from "@/lib/format";
import type { Scenario } from "@/lib/scenario-contract";
import { UNUSED_FLOOR_AREA_NOT_COMPUTABLE_REASONS } from "@/lib/scenario-contract";

/**
 * The C1 unused-draft-zoning-floor-area line for the Compare (Step 3) screen
 * (task M5-T018, directive D-041-R001).
 *
 * The scenario document carries a REQUIRED `unused_draft_zoning_floor_area`
 * section on EVERY branch (preliminary + no_scenario + unsupported), so this
 * block mounts once for every branch — directly beneath the cap line — exactly
 * like the other document-level blocks in ScenarioResult. Everything it shows is
 * transported VERBATIM from the validated document; nothing is computed,
 * clamped, or invented in the client.
 *
 * The three honest states follow astra-presentation-research.md 3.1/3.3:
 *
 *   - computed  → its OWN labeled line: the document's `label` verbatim, the
 *     exact value with a square-feet unit, the DRAFT discipline, and the
 *     document's `scope_note` directly beneath the number (3.1: the material
 *     assumption sits under the number). An honest exact-zero renders as 0.
 *   - over_built → the NEGATIVE remainder is shown honestly (never clamped to
 *     zero, never hidden, never restyled positive — formatValue renders the
 *     minus sign), the document's `over_built_statement` is rendered verbatim as
 *     its own explicit statement, and a needs-professional-review notice is
 *     surfaced as TEXT in a role="status" region (exposed to assistive tech, not
 *     colour-only).
 *   - not_computable → the standard "No supported estimate" treatment (3.3): no
 *     number, no invented zero, the typed reason surfaced in plain language
 *     derived from the document's enum.
 *
 * BOUNDING. `boundScenarioDocument` bounds the fields it surfaces, but it spreads
 * this section through unchanged (it predates the section). Consistent with the
 * module's own "bounded where it is read" doctrine (scenario-bounds.ts, for the
 * weakly-typed provenance the display readers walk), the free-text the section
 * newly surfaces — `label`, `scope_note`, `over_built_statement` — is length-
 * capped and control-stripped HERE via `boundedText` before it reaches the DOM.
 *
 * NAMING DISCIPLINE. Every human string on this line is the document's own
 * (`label` / `scope_note` / `over_built_statement`) or a fixed plain-language
 * gloss of a typed enum. The D-041 / research forbidden nouns (a buildable-area
 * claim, a development-rights claim, a remaining-capacity claim) and any
 * approval/attestation language are never introduced here; the section is a
 * FAR-derived floor-area difference only.
 */

type UnusedFloorAreaNotComputableReason =
  (typeof UNUSED_FLOOR_AREA_NOT_COMPUTABLE_REASONS)[number];

/**
 * Plain-language gloss of each typed `not_computable_reason`. This DERIVES the
 * sentence from the document's own enum value (the same way coverage.ts glosses
 * a coverage status); it never invents a number or a total. The `formula` /
 * inputs recorded on the document still say precisely which input was absent.
 */
const NOT_COMPUTABLE_PLAIN_LANGUAGE: Record<
  UnusedFloorAreaNotComputableReason,
  string
> = {
  missing_existing_building_area:
    "No existing building floor-area record was available for this lot, so no difference can be stated. An absent value is not zero.",
  existing_building_area_unusable:
    "The existing building floor-area record on file cannot be used for this calculation, so no difference can be stated. An unusable value is not zero.",
  no_draft_far_cap:
    "No draft residential zoning floor-area cap was surfaced for this lot, so no difference can be stated.",
};

function DraftDiscipline() {
  return (
    <span
      className="status-label"
      data-testid="scenario-unused-floor-area-draft-label"
    >
      (DRAFT — needs professional review, not Verified)
    </span>
  );
}

export function UnusedFloorAreaSection({ document }: { document: Scenario }) {
  const section = document.unused_draft_zoning_floor_area;
  // Free text surfaced here is bounded at the point it is read (see docstring).
  const label = boundedText(section.label, "(label not stated)");
  const scopeNote = boundedText(section.scope_note, "(scope note not stated)");

  return (
    <section
      className="card"
      data-testid="scenario-unused-floor-area"
      data-state={section.state}
    >
      <h2 className="section-title">Floor-area record comparison</h2>

      {/* The precise-noun label is the document's own — never relabelled here. */}
      <p className="section-note" data-testid="scenario-unused-floor-area-label">
        {label}
      </p>

      {section.state === "not_computable" ? (
        <NotComputableLine reason={section.not_computable_reason} />
      ) : (
        <ComputedLine section={section} />
      )}

      {/* Research 3.1: the material assumption sits directly beneath the number.
          It stays visible on every state so the reader always knows what this
          calculation did and did not assess. */}
      <p
        className="section-note"
        data-testid="scenario-unused-floor-area-scope-note"
      >
        {scopeNote}
      </p>
    </section>
  );
}

function ComputedLine({
  section,
}: {
  section: Scenario["unused_draft_zoning_floor_area"];
}) {
  const value = section.unused_draft_zoning_floor_area_sq_ft;
  const overBuilt = section.state === "over_built";
  return (
    <div data-testid="scenario-unused-floor-area-computed">
      <p>
        <span className="section-note">
          Draft cap minus recorded building area:
        </span>{" "}
        {/* The value is rendered EXACTLY as delivered. On over_built it is
            negative and the minus sign is shown — never clamped, hidden, or
            restyled into a positive. */}
        <strong
          className="fact-value"
          data-testid="scenario-unused-floor-area-value"
        >
          {formatValue(value)}
        </strong>{" "}
        {value !== null ? <span className="fact-units">square feet</span> : null}{" "}
        <DraftDiscipline />
      </p>

      {overBuilt ? <OverBuiltNotice section={section} /> : null}
    </div>
  );
}

function OverBuiltNotice({
  section,
}: {
  section: Scenario["unused_draft_zoning_floor_area"];
}) {
  const statement =
    typeof section.over_built_statement === "string"
      ? boundedText(section.over_built_statement, "")
      : "";
  return (
    <>
      {/* The document's own explicit statement, verbatim, as its own sentence. */}
      {statement !== "" ? (
        <p
          className="status-label"
          data-testid="scenario-unused-floor-area-over-built"
        >
          {statement}
        </p>
      ) : null}
      {/* Needs-professional-review, surfaced as TEXT in a role="status" region so
          assistive tech announces it — the escalation is never colour-only. */}
      <p
        className="status-label"
        role="status"
        data-testid="scenario-unused-floor-area-review"
      >
        This result exceeds the draft cap and is flagged for professional review
        before any reliance.
      </p>
    </>
  );
}

function NotComputableLine({
  reason,
}: {
  reason: Scenario["unused_draft_zoning_floor_area"]["not_computable_reason"];
}) {
  // The standard "No supported estimate" treatment (research 3.3): no number,
  // no invented zero, the typed reason surfaced in plain language.
  const plain =
    reason !== null
      ? NOT_COMPUTABLE_PLAIN_LANGUAGE[reason]
      : "No supported estimate is available for this calculation.";
  return (
    <div data-testid="scenario-unused-floor-area-not-computable">
      <p className="fact-value" data-testid="scenario-unused-floor-area-no-estimate">
        No supported estimate
      </p>
      <p className="section-note" data-testid="scenario-unused-floor-area-reason">
        {plain}
      </p>
    </div>
  );
}
