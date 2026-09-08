import { formatValue } from "@/lib/format";
import { CONSTRAINT_STATE_LABELS, SCENARIO_KIND_LABELS } from "@/lib/scenario-display";
import type { Scenario } from "@/lib/scenario-contract";

/**
 * One ranked scenario card for the Compare (Step 3) screen (task M5-T004,
 * PRODUCT_FLOW Step 3 blocks 3 and 4).
 *
 * The deterministic engine emits exactly one scenario today, so exactly one
 * card (rank 1), honestly labelled as the single preliminary scenario — extra
 * scenarios are NEVER fabricated (AI-boundary). Everything the card shows is
 * transported VERBATIM from the endpoint body:
 *
 *  - the draft zoning-floor-area cap value and its cap_label (the client never
 *    recomputes the cap — AS-1),
 *  - the optimized objective NAMED from cap_provenance.output_name (the UI rule
 *    forbids showing a "best"/max value without naming the objective),
 *  - the score/constraint breakdown (each constraint value + state + note), and
 *  - the platform's own integrity_check record surfaced verbatim (the client
 *    does not verify anything itself).
 *
 * A needs_review / draft text label always accompanies the cap so certainty is
 * never implied by color or a friendly word alone.
 */
export function ScenarioCard({
  document,
  rank,
}: {
  document: Scenario;
  rank: number;
}) {
  const cap = document.draft_zoning_floor_area_cap_sq_ft;
  const provenance = document.cap_provenance;
  return (
    <section className="card" data-testid={`scenario-card-${rank}`}>
      <h3 className="section-title">
        Scenario {rank}: {SCENARIO_KIND_LABELS[document.scenario_kind]}
      </h3>
      <p className="section-note">
        This is the single preliminary scenario the deterministic engine
        produced. No additional or ranked alternatives are invented.
      </p>

      {/* --- Maximum preliminary development potential (block 1) ---------- */}
      <div data-testid="scenario-cap">
        <p>
          <span className="section-note">
            Draft maximum residential zoning floor-area cap:
          </span>{" "}
          <strong className="fact-value" data-testid="scenario-cap-value">
            {formatValue(cap)}
          </strong>{" "}
          {cap !== null ? <span className="fact-units">square feet</span> : null}{" "}
          {/* Certainty is never implied by color alone — an explicit label. */}
          {document.needs_review ? (
            <span className="status-label" data-testid="scenario-draft-label">
              (DRAFT — needs professional review, not Verified)
            </span>
          ) : null}
        </p>
        {document.cap_label ? (
          <p className="section-note" data-testid="scenario-cap-label">
            {document.cap_label}
          </p>
        ) : null}
      </div>

      {/* --- Objective + score / constraint breakdown (block 4) ---------- */}
      <h4 className="section-subtitle">Optimized objective and score breakdown</h4>
      {provenance ? (
        <dl className="confirm-grid" data-testid="scenario-objective">
          <div className="confirm-row">
            <dt>Optimized objective</dt>
            <dd>
              <code data-testid="scenario-objective-name">
                {provenance.output_name}
              </code>
            </dd>
          </div>
          <div className="confirm-row">
            <dt>Rule</dt>
            <dd>
              <code>{provenance.rule_id}</code> (version{" "}
              <code>{provenance.rule_version}</code>, status{" "}
              <code>{provenance.rule_status}</code>)
            </dd>
          </div>
          {provenance.note ? (
            <div className="confirm-row">
              <dt>Note</dt>
              <dd className="section-note">{provenance.note}</dd>
            </div>
          ) : null}
        </dl>
      ) : (
        <p className="section-note">
          No cap provenance is attached to this scenario.
        </p>
      )}

      <h4 className="section-subtitle">Constraints used in this scenario</h4>
      <ul className="missing-list" data-testid="scenario-constraints">
        {document.constraints.map((constraint) => (
          <li key={constraint.key} data-testid={`scenario-constraint-${constraint.key}`}>
            <strong>{constraint.key}</strong>:{" "}
            <span className="fact-value">{formatValue(constraint.value)}</span>
            {constraint.unit ? (
              <span className="fact-units"> {constraint.unit}</span>
            ) : null}{" "}
            <span className="section-note">
              ({CONSTRAINT_STATE_LABELS[constraint.state]}; completeness:{" "}
              <code>{constraint.data_completeness}</code>)
            </span>
          </li>
        ))}
      </ul>

      {/* --- Platform integrity check, surfaced verbatim ----------------- */}
      <h4 className="section-subtitle">Platform integrity check</h4>
      <p className="section-note" data-testid="scenario-integrity">
        {document.integrity_check.performed
          ? `Performed — recompute ${
              document.integrity_check.agreed === true
                ? "agreed with"
                : document.integrity_check.agreed === false
                  ? "did NOT agree with"
                  : "result unrecorded against"
            } the canonical trace value.`
          : "Not performed for this scenario."}{" "}
        {document.integrity_check.note}
      </p>
      <p className="failure-meta">
        Method: <code>{document.integrity_check.method}</code>
      </p>
    </section>
  );
}
