import { CoverageBadge } from "@/components/property/CoverageBadge";
import { formatValue, urlHost } from "@/lib/format";
import { classifyScenario, type ScenarioPresentation } from "@/lib/scenario";
import type { Scenario, ScenarioConstraint } from "@/lib/scenario-contract";

/**
 * Draft scenario RESULT surface (task M5-T002): the honest scenario states —
 * preliminary (the draft zoning-floor-area cap surfaced VERBATIM), unsupported,
 * conflict, professional review, and missing controlling input. The network /
 * server failure state is a non-200 outcome rendered by ScenarioFailure, never
 * here.
 *
 * Every value shown is delivered by the deterministic backend + scenario builder
 * and displayed verbatim; this component performs NO legal or numeric
 * computation and NEVER recomputes or relabels the cap
 * (docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md). The presentation template is chosen
 * by classifyScenario from server discriminators only.
 *
 * NEVER-VERIFIED discipline: the prominent framing states DRAFT / not-final /
 * professional-review-required WITHOUT ever presenting the result as Published,
 * Verified, legally final, or a buildable envelope, and without encoding
 * certainty by color alone (the coverage badge always carries its exact enum
 * value + a non-color symbol + a screen-reader gloss). The exact server
 * disclaimer string (`not_verified_disclaimer`) is surfaced in a reachable,
 * labeled disclosure.
 */

const HEADINGS: Record<ScenarioPresentation, string> = {
  preliminary_cap: "Preliminary draft scenario — requires professional review",
  unsupported: "No applicable draft rule for this property",
  conflict: "Conflicting draft rules or data — professional review required",
  professional_review: "Professional review required — spatial uncertainty",
  missing: "No draft scenario — a required input is missing",
};

const INTROS: Record<ScenarioPresentation, string> = {
  preliminary_cap:
    "A draft rule produced the zoning-floor-area cap below. It is unreviewed and NOT a final " +
    "determination and NOT a buildable envelope — height, setbacks, yards, and other constraints " +
    "are unknown (see the coverage map). A qualified New York professional must review it before any reliance.",
  unsupported:
    "The platform has no draft rule that applies to this property, so no draft scenario is produced. " +
    "This is shown explicitly rather than left silent.",
  conflict:
    "More than one draft rule or a data conflict is present. Which rule governs is a legal " +
    "determination, so the platform produced no scenario value and picked no winner.",
  professional_review:
    "The platform could not confidently establish the spatial inputs a draft scenario needs, so it " +
    "produced no value and made no guess. The gap is shown, not hidden.",
  missing:
    "A required controlling input for a draft scenario is absent, so no value was produced and " +
    "nothing was inferred to fill the gap.",
};

function CapCallout({ document }: { document: Scenario }) {
  // The draft cap is surfaced VERBATIM with its mandatory draft-cap label. The
  // value is displayed exactly as delivered (formatValue only groups digits);
  // it is NEVER recomputed or relabeled here.
  if (document.draft_zoning_floor_area_cap_sq_ft === null || document.cap_label === null) {
    return null;
  }
  return (
    <div className="provenance-body" data-testid="scenario-cap">
      <p className="section-note">Draft zoning-floor-area cap (surfaced verbatim from the rule trace):</p>
      <p style={{ fontSize: "1.25rem", margin: "0.25rem 0" }}>
        <strong data-testid="scenario-cap-value">
          {formatValue(document.draft_zoning_floor_area_cap_sq_ft)}
        </strong>{" "}
        sq ft
      </p>
      <p className="failure-meta" data-testid="scenario-cap-label">
        {document.cap_label}
      </p>
    </div>
  );
}

function ReasonsList({ reasons }: { reasons: string[] }) {
  if (reasons.length === 0) return null;
  return (
    <ul className="missing-list" data-testid="scenario-reasons">
      {reasons.map((reason) => (
        <li key={reason}>{reason}</li>
      ))}
    </ul>
  );
}

function KnownConstraints({ constraints }: { constraints: ScenarioConstraint[] }) {
  // Surface the confidently-known contextual constraints (lot area, district)
  // verbatim; never the always-missing envelope families (shown in the map).
  const known = constraints.filter(
    (constraint) =>
      (constraint.key === "lot_area" || constraint.key === "zoning_district") &&
      constraint.state === "known" &&
      constraint.value !== null,
  );
  if (known.length === 0) return null;
  return (
    <dl data-testid="scenario-known-constraints">
      {known.map((constraint) => (
        <div key={constraint.key}>
          <dt>{constraint.key === "lot_area" ? "Lot area" : "Base zoning district"}</dt>
          <dd>
            {formatValue(constraint.value)}
            {constraint.unit ? ` ${constraint.unit === "square_feet" ? "sq ft" : constraint.unit}` : ""}
          </dd>
        </div>
      ))}
    </dl>
  );
}

function CoverageMap({ document }: { document: Scenario }) {
  // The full rule-coverage dependency matrix, verbatim: honest about which rule
  // families are still MISSING or out of scope, so the cap is never mistaken for
  // a buildable envelope.
  if (document.coverage_matrix.length === 0) return null;
  return (
    <details className="provenance-details" data-testid="scenario-coverage-matrix">
      <summary>Rule-coverage map (what this scenario does and does not cover)</summary>
      <div className="provenance-body">
        <ul className="missing-list">
          {document.coverage_matrix.map((row) => (
            <li key={row.constraint_family}>
              <strong>{row.constraint_family}</strong> — {row.governs}: {row.rule_status_today}
              {row.blocks_buildable_envelope ? " (blocks a buildable envelope)" : ""}
            </li>
          ))}
        </ul>
      </div>
    </details>
  );
}

function DisclaimerDisclosure({ document }: { document: Scenario }) {
  // The exact server disclaimer string is surfaced in a REACHABLE, labeled native
  // disclosure (mirroring the accepted rule-evaluation surface): the prominent
  // framing above already carries the plain-language DRAFT / not-final /
  // professional-review message, and the verbatim string is one keystroke away.
  return (
    <details className="provenance-details" data-testid="scenario-disclaimer">
      <summary>Draft-scenario disclaimer (exact wording)</summary>
      <div className="provenance-body">
        <p style={{ margin: 0 }}>{document.not_verified_disclaimer}</p>
      </div>
    </details>
  );
}

function CapProvenance({ document }: { document: Scenario }) {
  const provenance = document.cap_provenance;
  if (!provenance) return null;
  const citations = provenance.citations ?? [];
  return (
    <details className="provenance-details" data-testid="scenario-provenance">
      <summary>Cap rule and source provenance</summary>
      <div className="provenance-body">
        <dl>
          <dt>Rule</dt>
          <dd>
            <code>{provenance.rule_id}</code> ({provenance.rule_version}, {provenance.rule_status})
          </dd>
          <dt>Output surfaced</dt>
          <dd>
            <code>{provenance.output_name}</code>
          </dd>
        </dl>
        {citations.length > 0 ? (
          <div data-testid="scenario-citations">
            <p className="section-note">
              Legal-source citations backing the draft cap (unverified draft extraction; not a
              Verified reading of the source):
            </p>
            {citations.map((citation, index) => {
              const prov = (citation.provenance ?? {}) as Record<string, unknown>;
              const requestUrl = prov.request_url;
              return (
                <dl key={`${citation.snapshot_id}-${citation.section}-${index}`}>
                  <dt>Section</dt>
                  <dd>{citation.section}</dd>
                  <dt>Quote</dt>
                  <dd>{citation.quote}</dd>
                  {typeof prov.source_id === "string" ? (
                    <>
                      <dt>Source</dt>
                      <dd>{prov.source_id}</dd>
                    </>
                  ) : null}
                  {typeof requestUrl === "string" ? (
                    <>
                      <dt>Retrieved from</dt>
                      <dd>{urlHost(requestUrl)}</dd>
                    </>
                  ) : null}
                  {typeof prov.retrieved_at === "string" ? (
                    <>
                      <dt>Retrieved at</dt>
                      <dd>{prov.retrieved_at}</dd>
                    </>
                  ) : null}
                </dl>
              );
            })}
          </div>
        ) : (
          <p className="section-note">
            No legal-source citations accompany this result (there is no surfaced cap to cite).
          </p>
        )}
      </div>
    </details>
  );
}

function EvaluatedInput({ document }: { document: Scenario }) {
  const input = document.evaluated_input;
  return (
    <details className="provenance-details" data-testid="scenario-evaluated-input">
      <summary>Evaluated input (identified by reference, never an embedded profile)</summary>
      <div className="provenance-body">
        <dl>
          <dt>Evaluated BBL</dt>
          <dd>{input.bbl ?? "not stated"}</dd>
          <dt>Property-profile contract version</dt>
          <dd>{input.profile_contract_version}</dd>
          <dt>Rule-evaluation contract version</dt>
          <dd>{input.rule_evaluation_contract_version}</dd>
          <dt>Input fingerprint</dt>
          <dd>{input.input_fingerprint ? <code>{input.input_fingerprint}</code> : "not stated"}</dd>
        </dl>
      </div>
    </details>
  );
}

export function ScenarioResult({ document }: { document: Scenario }) {
  const presentation = classifyScenario(document);
  return (
    <section
      className="card"
      data-testid="scenario-result"
      data-scenario-state={presentation}
      aria-labelledby="scenario-heading"
    >
      <div className={`scenario-state scenario-state-${presentation}`}>
        <h3
          className="section-title"
          id="scenario-heading"
          data-testid={`scenario-state-${presentation}`}
          data-scenario-heading
          tabIndex={-1}
        >
          {HEADINGS[presentation]}
        </h3>
        {/* Prominent DRAFT framing — plain language, never "verified"/"best".
            Emphasis is bold text + a left rule (shape, not color alone). */}
        <p
          className="scenario-draft-banner"
          data-testid="scenario-draft-banner"
          style={{ borderLeft: "4px solid currentColor", padding: "0.5rem 0.75rem", margin: "0.5rem 0" }}
        >
          <strong>DRAFT — not a final legal determination and not a buildable envelope.</strong>{" "}
          Produced by an unreviewed draft rule pending qualified-human legal approval. Do not rely on
          it for acquisition, design, filing, financing, or construction.
        </p>
        <p style={{ marginTop: "0.25rem" }}>
          <CoverageBadge status={document.coverage_status} />
        </p>
        <p>{INTROS[presentation]}</p>
        {presentation === "preliminary_cap" ? <CapCallout document={document} /> : null}
        <KnownConstraints constraints={document.constraints} />
        <ReasonsList reasons={document.reasons} />
        <CoverageMap document={document} />
        <CapProvenance document={document} />
        <DisclaimerDisclosure document={document} />
        <EvaluatedInput document={document} />
      </div>
    </section>
  );
}
