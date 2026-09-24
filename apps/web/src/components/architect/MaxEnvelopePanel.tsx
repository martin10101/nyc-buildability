"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { OutcomeAnnouncer } from "@/components/property/OutcomeAnnouncer";
import {
  announcementForMaxEnvelope,
  candidateIsAdoptable,
  classifyDimensionRow,
  envelopeAggregateIsComplete,
  envelopeAggregateMessage,
  fetchMaxEnvelope,
  maxEnvelopeOutcomeIsRecoverable,
  type ContractViolationShape,
  type EnvelopeDimensionView,
  type EnvelopeGapReason,
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
 * and while ANY gap, withheld row, or conflict advisory is present the aggregate
 * stays VISIBLY INCOMPLETE — there is no unrestricted green/complete aggregate
 * state, and the copy never asserts an unqualified maximum-allowed-building claim.
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

// [ORCH-CORRECTED per T070 G3-F3/G4-F3; DB-050(m)] The server emits gap_reason as
// one of the four EnvelopeGapReason machine tokens (max_envelope.py:132-146); the
// analyst-facing headline maps each to plain copy. Typed as an EXHAUSTIVE
// `Record<EnvelopeGapReason, string>`, so if the server enum ever grows a token,
// this literal fails to compile until its analyst copy is added — the map can never
// silently drift out of the server vocabulary. An unrecognized RUNTIME token (a
// malformed/hostile server) renders verbatim (fail-honest — never invented copy);
// the server's human-prose `detail` stays rendered below unchanged.
export const GAP_REASON_COPY: Record<EnvelopeGapReason, string> = {
  no_applicable_rule: "no applicable rule was found for this dimension",
  allowance_unresolved: "the governing allowance could not be resolved",
  family_unsupported: "this rule family is not supported by the engine yet",
  non_commensurable_with_massing: "the rule does not translate to this massing dimension",
};

// [ORCH-CORRECTED per SEC F1] Own-property guard: a hostile/corrupt server token
// like "__proto__" or "constructor" must render as its literal text (fail-honest),
// never resolve through Object.prototype into a non-string React child that crashes
// the whole property page through the route error boundary. hasOwnProperty is false
// for prototype keys, so the guard narrows to a REAL EnvelopeGapReason key.
function isKnownGapReason(token: string): token is EnvelopeGapReason {
  return Object.prototype.hasOwnProperty.call(GAP_REASON_COPY, token);
}

export function gapReasonCopy(token: string | null): string {
  if (token === null || token === "") return "the reason was not stated";
  return isKnownGapReason(token) ? GAP_REASON_COPY[token] : token;
}

// [HJ-3/HJ-5] Plain-words copy for a withheld row: what the service actually returned.
// "unreadable" (one field sent, in a form this page cannot use) is never called
// "neither" — the service DID send something.
export const CONTRACT_VIOLATION_HEADLINE =
  "the service's answer for this limit was inconsistent or unreadable, so no value is shown.";
export const CONTRACT_VIOLATION_RETURNED: Record<ContractViolationShape, string> = {
  both: "both a value and a reason",
  neither: "neither a value nor a reason",
  unreadable: "no usable value or reason",
};

function DimensionRow({ dimension }: { dimension: EnvelopeDimensionView }) {
  // D-083-R004 XOR: a row is a clean value, an honest gap, or — if the server
  // response carries BOTH or NEITHER of binding_value/gap_reason, or its one field
  // is unusable — a typed contract violation that NEVER renders a value (DB-050(d)).
  const row = classifyDimensionRow(dimension);
  // The ACTUAL server-provided binding-rule citations (section references), not
  // only their count — load-bearing provenance the analyst reads directly.
  const citationSections = dimension.citations
    .map((citation) => citation.section)
    .filter((section): section is string => section !== null && section !== "");
  return (
    <li
      className={`envelope-dimension${row.kind === "value" ? "" : " envelope-dimension-gap"}`}
      data-testid={`envelope-dimension-${dimension.dimensionId}`}
      data-gap={row.kind === "gap" ? "true" : "false"}
      data-row-kind={row.kind}
    >
      <div className="envelope-dimension-head">
        <span className="envelope-dimension-label">{dimension.label}</span>
        {row.kind === "value" ? (
          <span className="envelope-dimension-value" data-testid={`envelope-value-${dimension.dimensionId}`}>
            {dimensionValueLabel(dimension)}
          </span>
        ) : row.kind === "gap" ? (
          <span className="envelope-dimension-gap-reason" data-testid={`envelope-gap-${dimension.dimensionId}`}>
            Could not check — {gapReasonCopy(dimension.gapReason)}
          </span>
        ) : (
          <span
            className="envelope-dimension-contract-failure"
            data-testid={`envelope-contract-violation-${dimension.dimensionId}`}
          >
            Could not check — {CONTRACT_VIOLATION_HEADLINE}
          </span>
        )}
      </div>
      {row.kind === "value" ? (
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
      ) : row.kind === "gap" ? (
        <p className="envelope-dimension-detail">{dimension.detail}</p>
      ) : (
        <p className="envelope-dimension-detail" data-testid={`envelope-contract-detail-${dimension.dimensionId}`}>
          {`The service should send either a value or the reason it could not check this limit. It returned ${
            CONTRACT_VIOLATION_RETURNED[row.returned]
          }, so nothing is shown for this limit and this preliminary picture stays incomplete.`}
        </p>
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
  const adoptable = candidateIsAdoptable(envelope);

  const adopt = useCallback(() => {
    if (!envelope.candidate || !onAdopt) return;
    const draft = draftFromCandidate(envelope.candidate, {
      label: "Generated building option",
      lot_area_sq_ft: request.lot.area_sq_ft,
      zoning_district: request.lot_rule_facts.zoning_district,
      // DB-050(j): street width is SERVER-determined and never inferred in the
      // client (the answer-first request sends no street width), so the adoption
      // seed records "not provided" — an unconditional "" here, byte-identical to
      // the prior always-"" value now that the dead lot_rule_facts read is gone.
      street_width_class: "",
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
        {/* HJ-1/HJ-2: the SAME line the announcer speaks; screen-row counts only. */}
        {envelopeAggregateMessage(envelope)}
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
      if (activeRef.current !== token) return; // superseded by a newer request
      // DB-050(c): an `aborted` outcome means this request was cancelled, never a
      // real result. The path that reaches here with the token still active is a
      // request CLEARED to null (the null branch does not bump the token): stored,
      // it would make a later re-set commit a reasonless failure card (aborted
      // announces "") before loading starts. Pinned by the MutationObserver spec in
      // max-envelope-panel.test.tsx ("cleared and re-set").
      if (result.kind === "aborted") return;
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
