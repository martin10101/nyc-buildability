"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { OutcomeAnnouncer } from "@/components/property/OutcomeAnnouncer";
import {
  announcementForMaxEnvelope,
  candidateIsAdoptable,
  envelopeAggregateIsComplete,
  envelopeHasConflictAdvisory,
  fetchMaxEnvelope,
  maxEnvelopeOutcomeIsRecoverable,
  type EnvelopeDimensionView,
  type EnvelopeView,
  type MaxEnvelopeOutcome,
  type MaxEnvelopeRequest,
} from "@/lib/architect/max-envelope-api";
import { draftFromCandidate, type ProposalDraft } from "@/lib/architect/proposal-draft";

/**
 * Preliminary-development-limits panel (task M5-T070, D-082-R003 + D-083). The
 * ANSWER-FIRST surface: the computed maximum-buildable envelope renders BEFORE any
 * designer input, from the architect surface's existing lot context alone. Each
 * dimension shows its binding rule (id + version + citation count), out-competed
 * rules, conflict advisories surfaced-never-resolved, and honest typed gaps; the
 * server disclosure renders VERBATIM.
 *
 * The D-083 CLAIM-CLASS VOCABULARY is binding here (D-083-R001/R002/R004): the
 * heading class is "Preliminary development limits"; the emitted candidate is a
 * "Generated building option" (the only building-shaped claim, labeled a checked
 * OPTION); no per-dimension ceiling is ever presented as one permitted building;
 * and while ANY gap or conflict advisory is present the aggregate stays VISIBLY
 * INCOMPLETE — there is no unrestricted green/complete aggregate state, and the
 * copy never asserts an unqualified maximum-allowed-building claim.
 *
 * One action adopts the Generated building option as the starting draft in the
 * accepted editor (through the ONE draft model, proposal-draft.ts); it is
 * disabled/absent unless the server FITTED a contained candidate. Manual entry
 * (numeric table + the accepted T066 drawing) stays fully available and unchanged
 * beside this — this panel composes ADDITIVELY and never blocks it.
 *
 * The route is UNMOUNTED: a null/loading/failed fetch degrades to a typed card,
 * never a dead surface and never a fabricated limit; the accepted experience
 * below it is untouched.
 */

function dimensionValueLabel(d: EnvelopeDimensionView): string {
  // The server value passes through verbatim (it is load-bearing; never rounded).
  return d.unit && d.unit !== "" ? `${d.bindingValue} ${d.unit}` : `${d.bindingValue}`;
}

// [ORCH-CORRECTED per T070 G3-F3/G4-F3] The server emits gap_reason as one of four
// machine tokens (EnvelopeGapReason, max_envelope.py:132-146); the analyst-facing
// headline maps each to plain copy. An unrecognized token renders verbatim
// (fail-honest — never invented copy); the server's human-prose `detail` stays
// rendered below unchanged.
const GAP_REASON_COPY: Record<string, string> = {
  no_applicable_rule: "no applicable rule was found for this dimension",
  allowance_unresolved: "the governing allowance could not be resolved",
  family_unsupported: "this rule family is not supported by the engine yet",
  non_commensurable_with_massing: "the rule does not translate to this massing dimension",
};

function gapReasonCopy(token: string | null): string {
  if (token === null || token === "") return "the reason was not stated";
  // [ORCH-CORRECTED per SEC F1] Own-property guard: a hostile/corrupt server token
  // like "__proto__" or "constructor" must render as its literal text (fail-honest),
  // never resolve through Object.prototype into a non-string React child that
  // crashes the whole property page through the route error boundary.
  return Object.prototype.hasOwnProperty.call(GAP_REASON_COPY, token)
    ? GAP_REASON_COPY[token]
    : token;
}

function DimensionRow({ dimension }: { dimension: EnvelopeDimensionView }) {
  const isGap = dimension.gapReason !== null;
  // The ACTUAL server-provided binding-rule citations (section references), not
  // only their count — load-bearing provenance the analyst reads directly.
  const citationSections = dimension.citations
    .map((citation) => citation.section)
    .filter((section): section is string => section !== null && section !== "");
  return (
    <li
      className={`envelope-dimension${isGap ? " envelope-dimension-gap" : ""}`}
      data-testid={`envelope-dimension-${dimension.dimensionId}`}
      data-gap={isGap ? "true" : "false"}
    >
      <div className="envelope-dimension-head">
        <span className="envelope-dimension-label">{dimension.label}</span>
        {isGap ? (
          <span className="envelope-dimension-gap-reason" data-testid={`envelope-gap-${dimension.dimensionId}`}>
            Could not check — {gapReasonCopy(dimension.gapReason)}
          </span>
        ) : (
          <span className="envelope-dimension-value" data-testid={`envelope-value-${dimension.dimensionId}`}>
            {dimensionValueLabel(dimension)}
          </span>
        )}
      </div>
      {isGap ? (
        <p className="envelope-dimension-detail">{dimension.detail}</p>
      ) : (
        <>
          <p className="envelope-dimension-provenance" data-testid={`envelope-binding-${dimension.dimensionId}`}>
            Binding rule {dimension.bindingRuleId ?? "unknown"}
            {dimension.bindingRuleVersion ? ` v${dimension.bindingRuleVersion}` : ""} ·{" "}
            {dimension.outCompetedRuleIds.length} rule
            {dimension.outCompetedRuleIds.length === 1 ? "" : "s"} out-competed · {dimension.citationCount}{" "}
            citation{dimension.citationCount === 1 ? "" : "s"}
          </p>
          {citationSections.length > 0 ? (
            <p
              className="envelope-dimension-citations"
              data-testid={`envelope-citations-${dimension.dimensionId}`}
            >
              Cited sections: {citationSections.join(", ")}
            </p>
          ) : null}
        </>
      )}
      {dimension.conflictAdvisory ? (
        <p
          className="envelope-conflict-advisory"
          role="note"
          data-testid={`envelope-advisory-${dimension.dimensionId}`}
        >
          Rule conflict surfaced for professional review, not resolved here: competing rules{" "}
          {dimension.conflictAdvisory.competingRuleIds.join(", ")}
          {dimension.conflictAdvisory.note ? ` — ${dimension.conflictAdvisory.note}` : ""}.
        </p>
      ) : null}
    </li>
  );
}

function EnvelopeBody({
  envelope,
  request,
  onAdopt,
  onAdopted,
}: {
  envelope: EnvelopeView;
  request: MaxEnvelopeRequest;
  onAdopt?: (draft: ProposalDraft) => void;
  onAdopted: (message: string) => void;
}) {
  const complete = envelopeAggregateIsComplete(envelope);
  const hasAdvisory = envelopeHasConflictAdvisory(envelope);
  const adoptable = candidateIsAdoptable(envelope);

  const adopt = useCallback(() => {
    if (!envelope.candidate || !onAdopt) return;
    const streetWidth = request.lot_rule_facts.street_width_class;
    const draft = draftFromCandidate(envelope.candidate, {
      label: "Generated building option",
      lot_area_sq_ft: request.lot.area_sq_ft,
      zoning_district: request.lot_rule_facts.zoning_district,
      street_width_class: streetWidth === "wide" || streetWidth === "narrow" ? streetWidth : "",
    });
    onAdopt(draft);
    onAdopted(
      "Adopted the Generated building option as a proposed starting draft in the editor below. " +
        "Every value stays labeled proposed — edit it, or keep entering your own.",
    );
  }, [envelope.candidate, onAdopt, request, onAdopted]);

  return (
    <div className="max-envelope-body">
      <p className="max-envelope-disclosure" data-testid="envelope-disclosure">
        {envelope.disclosure}
      </p>

      <p
        className={`max-envelope-aggregate ${complete ? "is-checked" : "is-incomplete"}`}
        data-testid="envelope-aggregate"
        data-complete={complete ? "true" : "false"}
        role="status"
      >
        {complete
          ? `All ${envelope.summary.total} preliminary development limits were checked — a rules-derived ` +
            `estimate requiring professional review.`
          : `Could not check ${envelope.summary.gap} of ${envelope.summary.total} development limits` +
            (hasAdvisory ? ", and a rule conflict needs professional review" : "") +
            `. This preliminary picture is incomplete.`}
      </p>

      <ul className="max-envelope-dimensions">
        {envelope.dimensions.map((dimension) => (
          <DimensionRow key={dimension.dimensionId} dimension={dimension} />
        ))}
      </ul>

      <section className="generated-building-option" data-testid="generated-building-option">
        <h3>Generated building option</h3>
        <p className="generated-building-option-honesty">
          A single checked building OPTION shaped from the limits above — a rules-derived estimate, not a
          permitted building and not a city record. The per-limit ceilings above are never combined into one
          building; only this checked option is building-shaped.
        </p>
        {adoptable ? (
          <button
            type="button"
            className="primary-button"
            data-testid="adopt-candidate"
            onClick={adopt}
          >
            Adopt as a proposed starting draft
          </button>
        ) : (
          <p className="generated-building-option-unavailable" data-testid="candidate-unavailable">
            No building option can be adopted for this lot: {envelope.placement.detail}
          </p>
        )}
      </section>
    </div>
  );
}

export interface MaxEnvelopePanelProps {
  /** The lot context to send, built from the architect surface's profile. When
   * null the panel shows a typed "cannot compute" card (never a fabricated limit). */
  request: MaxEnvelopeRequest | null;
  fetchImpl?: typeof fetch;
  /** Adopt the Generated building option into the editor's ONE draft model. */
  onAdopt?: (draft: ProposalDraft) => void;
}

export function MaxEnvelopePanel({ request, fetchImpl, onAdopt }: MaxEnvelopePanelProps) {
  const [outcome, setOutcome] = useState<MaxEnvelopeOutcome | null>(null);
  const [loading, setLoading] = useState(false);
  const [announcement, setAnnouncement] = useState("");
  const [reloadNonce, setReloadNonce] = useState(0);
  // Guard against a resolved fetch from a superseded request updating state.
  const activeRef = useRef(0);

  useEffect(() => {
    if (!request) {
      setOutcome(null);
      setLoading(false);
      return;
    }
    const token = activeRef.current + 1;
    activeRef.current = token;
    const controller = new AbortController();
    setLoading(true);
    setAnnouncement("");
    fetchMaxEnvelope(request, { fetchImpl, signal: controller.signal }).then((result) => {
      if (activeRef.current !== token) return; // superseded
      setOutcome(result);
      setLoading(false);
      setAnnouncement(announcementForMaxEnvelope(result));
    });
    return () => {
      controller.abort();
    };
  }, [request, fetchImpl, reloadNonce]);

  return (
    <section className="card max-envelope-panel" data-testid="max-envelope-panel" aria-labelledby="max-envelope-heading">
      <OutcomeAnnouncer testId="max-envelope-announcer" message={announcement} />
      <header className="max-envelope-head">
        <h2 id="max-envelope-heading">Preliminary development limits</h2>
        <p className="max-envelope-lead">
          The computed limits for this lot, shown first — a rules-derived estimate that requires professional
          review, not a maximum permitted building. Test a design below whenever you are ready.
        </p>
      </header>

      {!request ? (
        <p className="max-envelope-unavailable" data-testid="envelope-no-context" role="status">
          Preliminary development limits cannot be computed for this property: no usable lot area is recorded.
          Enter a proposal below to check a design directly.
        </p>
      ) : loading ? (
        <p className="max-envelope-loading" data-testid="envelope-loading" role="status" aria-busy="true">
          Computing the preliminary development limits…
        </p>
      ) : outcome?.kind === "envelope" ? (
        <EnvelopeBody
          envelope={outcome.envelope}
          request={request}
          onAdopt={onAdopt}
          onAdopted={setAnnouncement}
        />
      ) : outcome ? (
        <div className="max-envelope-failure card failure-state" data-testid="envelope-failure" role="alert">
          <strong>Preliminary development limits are unavailable right now</strong>
          <p>{announcementForMaxEnvelope(outcome)}</p>
          <p className="max-envelope-failure-note">
            Nothing was fabricated. The proposal editor below is unaffected — enter a design and check it
            directly.
          </p>
          {maxEnvelopeOutcomeIsRecoverable(outcome) ? (
            <button
              type="button"
              className="secondary-button"
              data-testid="envelope-retry"
              onClick={() => setReloadNonce((n) => n + 1)}
            >
              Try again
            </button>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
