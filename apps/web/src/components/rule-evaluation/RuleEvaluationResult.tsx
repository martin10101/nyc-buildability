import { CoverageBadge } from "@/components/property/CoverageBadge";
import { formatValue, urlHost } from "@/lib/format";
import {
  classifyRuleEvaluation,
  type RuleEvalPresentation,
} from "@/lib/rule-evaluation";
import type {
  BaseDistrictCandidate,
  EvaluationTrace,
  RuleEvaluation,
} from "@/lib/rule-evaluation-contract";

/**
 * Draft rule-evaluation RESULT surface (task M4-T005 phase 3): the five
 * document-derived UI states (applicable draft, unsupported / not applicable,
 * missing evidence, conflicting rules, spatial uncertainty). The sixth
 * required state — network / server failure — is a non-200 outcome rendered by
 * RuleEvaluationFailure, never here.
 *
 * Every value shown is delivered by the deterministic backend and displayed
 * verbatim; this component performs NO legal or numeric computation
 * (docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md). The presentation template is chosen
 * by classifyRuleEvaluation from server discriminators only.
 *
 * NEVER-VERIFIED discipline: the prominent framing states DRAFT / not-final /
 * professional-review-required WITHOUT ever presenting the result as Published,
 * Verified, legally final, or guaranteed buildable, and without encoding
 * certainty by color alone (the coverage badge always carries its exact enum
 * value + a non-color symbol + a screen-reader gloss). The exact server
 * disclaimer string is surfaced in a reachable, labeled disclosure.
 */

const HEADINGS: Record<RuleEvalPresentation, string> = {
  applicable_draft: "Draft determination — requires professional review",
  unsupported: "No applicable draft rule for this property",
  missing_evidence: "Professional review required — evidence missing",
  rule_conflict: "Conflicting draft rules — professional review required",
  spatial_uncertainty: "Spatial uncertainty — the lot spans districts",
};

const INTROS: Record<RuleEvalPresentation, string> = {
  applicable_draft:
    "A draft rule produced the values below. They are unreviewed and not a final " +
    "determination — a qualified New York professional must review them before any reliance.",
  unsupported:
    "The platform has no draft rule that applies to this property, so no draft value is produced. " +
    "This is shown explicitly rather than left silent.",
  missing_evidence:
    "The platform could not confidently establish the inputs a draft determination needs, so it " +
    "produced no value and made no guess. The gap is shown, not hidden.",
  rule_conflict:
    "More than one draft rule is simultaneously in effect and applies to the same inputs. Which " +
    "rule governs is a legal determination, so the platform produced no value and picked no winner.",
  spatial_uncertainty:
    "This lot spans more than one base-zoning district. The share of each district is preserved as a " +
    "range and never collapsed into a single value, so no single district is asserted.",
};

function DisclaimerDisclosure({ document }: { document: RuleEvaluation }) {
  // The exact server disclaimer string is surfaced here in a REACHABLE,
  // labeled native disclosure. It is intentionally inside a collapsed
  // <details> (mirroring the accepted property-profile coverage-policy quote):
  // the prominent framing above already carries the plain-language DRAFT /
  // not-final / professional-review message, and the verbatim legal string is
  // one keystroke away for anyone who wants the canonical wording.
  return (
    <details className="provenance-details" data-testid="rule-eval-disclaimer">
      <summary>Draft-result disclaimer (exact wording)</summary>
      <div className="provenance-body">
        <p style={{ margin: 0 }}>{document.not_verified_disclaimer}</p>
      </div>
    </details>
  );
}

function InputAndProvenance({ document }: { document: RuleEvaluation }) {
  const input = document.evaluated_input;
  const citationBlocks = document.evaluations.flatMap((evaluation) =>
    evaluation.citations.map((citation) => ({ evaluation, citation })),
  );
  return (
    <details className="provenance-details" data-testid="rule-eval-provenance">
      <summary>Evaluated input and source provenance</summary>
      <div className="provenance-body">
        <dl>
          <dt>Evaluated BBL</dt>
          <dd>{input.bbl ?? "not stated"}</dd>
          <dt>Property-profile contract version</dt>
          <dd>{input.profile_contract_version}</dd>
          <dt>Input fingerprint</dt>
          <dd>
            <code>{input.input_fingerprint}</code>
          </dd>
          <dt>Zoning-district input provenance</dt>
          <dd>
            {input.input_provenance.zoning_district.length > 0
              ? input.input_provenance.zoning_district.join(", ")
              : "none linked (shown explicitly, not omitted)"}
          </dd>
          <dt>Lot-area input provenance</dt>
          <dd>
            {input.input_provenance.lot_area_sq_ft.length > 0
              ? input.input_provenance.lot_area_sq_ft.join(", ")
              : "none linked (shown explicitly, not omitted)"}
          </dd>
        </dl>
        {citationBlocks.length > 0 ? (
          <div data-testid="rule-eval-citations">
            <p className="section-note">
              Legal-source citations backing the draft rule (unverified draft
              extraction; not a Verified reading of the source):
            </p>
            {citationBlocks.map(({ evaluation, citation }) => {
              const provenance = (citation.provenance ?? {}) as Record<string, unknown>;
              const requestUrl = provenance.request_url;
              return (
                <dl key={`${evaluation.rule_id}-${citation.snapshot_id}-${citation.section}`}>
                  <dt>Rule</dt>
                  <dd>
                    <code>{evaluation.rule_id}</code> ({evaluation.rule_version},{" "}
                    {evaluation.rule_status})
                  </dd>
                  <dt>Section</dt>
                  <dd>{citation.section}</dd>
                  <dt>Quote</dt>
                  <dd>{citation.quote}</dd>
                  {typeof provenance.source_id === "string" ? (
                    <>
                      <dt>Source</dt>
                      <dd>{provenance.source_id}</dd>
                    </>
                  ) : null}
                  {typeof requestUrl === "string" ? (
                    <>
                      <dt>Retrieved from</dt>
                      <dd>{urlHost(requestUrl)}</dd>
                    </>
                  ) : null}
                  {typeof provenance.retrieved_at === "string" ? (
                    <>
                      <dt>Retrieved at</dt>
                      <dd>{provenance.retrieved_at}</dd>
                    </>
                  ) : null}
                </dl>
              );
            })}
          </div>
        ) : (
          <p className="section-note">
            No legal-source citations accompany this result (there is no computed
            value to cite).
          </p>
        )}
      </div>
    </details>
  );
}

function ReasonsList({ reasons }: { reasons: string[] }) {
  if (reasons.length === 0) return null;
  return (
    <ul className="missing-list" data-testid="rule-eval-reasons">
      {reasons.map((reason) => (
        <li key={reason}>{reason}</li>
      ))}
    </ul>
  );
}

function DraftOutputs({ evaluations }: { evaluations: EvaluationTrace[] }) {
  const withOutputs = evaluations.filter(
    (evaluation) => Object.keys(evaluation.outputs as Record<string, unknown>).length > 0,
  );
  if (withOutputs.length === 0) return null;
  return (
    <div data-testid="rule-eval-outputs">
      {withOutputs.map((evaluation) => (
        <div key={`${evaluation.rule_id}-${evaluation.rule_version}`} className="provenance-body">
          <p className="section-note">
            Draft outputs from rule <code>{evaluation.rule_id}</code> (
            {evaluation.rule_status}) — draft values, not a final determination:
          </p>
          <dl>
            {Object.entries(evaluation.outputs as Record<string, unknown>).map(
              ([name, value]) => (
                <div key={name}>
                  <dt>{name}</dt>
                  <dd>{formatValue(value)}</dd>
                </div>
              ),
            )}
          </dl>
        </div>
      ))}
    </div>
  );
}

function CandidateShare({ candidate }: { candidate: BaseDistrictCandidate }) {
  // Ranges are NEVER collapsed: show the full [min, max] with the point share.
  const range =
    candidate.share_min !== null && candidate.share_max !== null
      ? `${formatValue(candidate.share_min)}–${formatValue(candidate.share_max)}`
      : "range not stated";
  const point =
    candidate.share_point !== null ? ` (point estimate ${formatValue(candidate.share_point)})` : "";
  return (
    <li>
      <strong>{candidate.district_label ?? "district not stated"}</strong>: share{" "}
      {range}
      {point}
      {candidate.minor_portion ? " — minor portion" : ""}
    </li>
  );
}

function SpatialCandidates({ document }: { document: RuleEvaluation }) {
  const candidates = document.spatial_uncertainty.base_district_candidates;
  if (candidates.length === 0) return null;
  return (
    <div>
      <p className="section-note">
        Base-zoning districts the lot intersects (shares preserved as ranges):
      </p>
      <ul className="missing-list" data-testid="rule-eval-candidates">
        {candidates.map((candidate, index) => (
          <CandidateShare key={candidate.district_label ?? index} candidate={candidate} />
        ))}
      </ul>
    </div>
  );
}

function ConflictDetails({ document }: { document: RuleEvaluation }) {
  const conflict = document.rule_conflict;
  if (!conflict) return null;
  return (
    <div data-testid="rule-eval-conflict">
      {conflict.competing_output_names.length > 0 ? (
        <p>
          The conflict is over output(s):{" "}
          <strong>{conflict.competing_output_names.join(", ")}</strong>.
        </p>
      ) : null}
      <p className="section-note">Competing draft rules (none was selected):</p>
      <ul className="missing-list" data-testid="rule-eval-competing-rules">
        {conflict.competing_rules.map((rule) => (
          <li key={rule.rule_id}>
            <code>{rule.rule_id}</code> ({rule.rule_version}) — in effect{" "}
            {rule.effective_from ?? "unknown start"} to {rule.effective_to ?? "present"}
          </li>
        ))}
      </ul>
    </div>
  );
}

function StateBody({
  presentation,
  document,
}: {
  presentation: RuleEvalPresentation;
  document: RuleEvaluation;
}) {
  switch (presentation) {
    case "applicable_draft":
      return (
        <>
          {document.zoning_district ? (
            <p>
              Draft base-zoning district: <strong>{document.zoning_district}</strong>
              {document.lot_area_sq_ft !== null ? (
                <>
                  {" "}· lot area used: {formatValue(document.lot_area_sq_ft)} sq ft
                  {document.lot_area_source ? ` (${document.lot_area_source})` : ""}
                </>
              ) : null}
            </p>
          ) : null}
          <DraftOutputs evaluations={document.evaluations} />
          <ReasonsList reasons={document.reasons} />
        </>
      );
    case "unsupported":
      return <ReasonsList reasons={document.reasons} />;
    case "missing_evidence":
      return (
        <>
          {document.fail_safe_reason ? (
            <p className="failure-meta">
              Fail-safe reason: <code>{document.fail_safe_reason}</code>
            </p>
          ) : null}
          <ReasonsList reasons={document.reasons} />
        </>
      );
    case "rule_conflict":
      return (
        <>
          <ConflictDetails document={document} />
          <ReasonsList reasons={document.reasons} />
        </>
      );
    case "spatial_uncertainty":
      return (
        <>
          <SpatialCandidates document={document} />
          {document.spatial_uncertainty.review_reasons.length > 0 ? (
            <ul className="missing-list" data-testid="rule-eval-review-reasons">
              {document.spatial_uncertainty.review_reasons.map((reason) => (
                <li key={reason}>{reason}</li>
              ))}
            </ul>
          ) : null}
          <ReasonsList reasons={document.reasons} />
        </>
      );
  }
}

export function RuleEvaluationResult({ document }: { document: RuleEvaluation }) {
  const presentation = classifyRuleEvaluation(document);
  return (
    <section
      className="card"
      data-testid="rule-eval-result"
      data-rule-eval-state={presentation}
      aria-labelledby="rule-eval-heading"
    >
      <div className={`rule-eval-state rule-eval-state-${presentation}`}>
        <h3
          className="section-title"
          id="rule-eval-heading"
          data-testid={`rule-eval-state-${presentation}`}
          data-rule-eval-heading
          tabIndex={-1}
        >
          {HEADINGS[presentation]}
        </h3>
        {/* Prominent DRAFT framing — plain language, never "verified"/"best".
            Emphasis is bold text + a left rule (shape, not color alone). */}
        <p
          className="rule-eval-draft-banner"
          data-testid="rule-eval-draft-banner"
          style={{
            borderLeft: "4px solid currentColor",
            padding: "0.5rem 0.75rem",
            margin: "0.5rem 0",
          }}
        >
          <strong>DRAFT — not a final legal determination.</strong> Produced by an
          unreviewed draft rule pending qualified-human legal approval. Do not rely on
          it for acquisition, design, filing, financing, or construction.
        </p>
        <p style={{ marginTop: "0.25rem" }}>
          <CoverageBadge status={document.coverage_status} />
        </p>
        <p>{INTROS[presentation]}</p>
        <StateBody presentation={presentation} document={document} />
        <DisclaimerDisclosure document={document} />
        <InputAndProvenance document={document} />
      </div>
    </section>
  );
}
