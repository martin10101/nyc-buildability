import { formatValue } from "@/lib/format";
import { SCENARIO_KIND_LABELS } from "@/lib/scenario-display";
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
 *    recomputes the cap — AS-1), and
 *  - the optimized objective NAMED from cap_provenance.output_name (the UI rule
 *    at .claude/rules/frontend-web.md:13 forbids showing a "best"/max value
 *    without naming the objective).
 *
 * That naming guarantee is now ENFORCED rather than asserted: before the rework
 * the validator checked `cap_provenance` only as "object or null" before
 * casting, so a body carrying `cap_provenance: {"note":"tbd"}` rendered a
 * 15,000 sq ft maximum with an EMPTY objective name and an empty rule id — and
 * because `{}` is truthy, it took the populated branch rather than the honest
 * "no cap provenance" fallback (G4 finding 2). scenario-contract.ts now
 * type-checks all six fields and refuses a non-null cap with a null provenance.
 *
 * The constraint breakdown and the integrity check used to live here too, which
 * is exactly why the no_scenario branch lost them; they are now in
 * ScenarioConstraints, mounted by ScenarioResult on every branch.
 *
 * A needs_review / draft text label always accompanies the cap so certainty is
 * never implied by color or a friendly word alone. The prefix at the top of the
 * cap line is UNCONDITIONAL — no server field can switch it off.
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
      <h2 className="section-title">
        Scenario {rank}: {SCENARIO_KIND_LABELS[document.scenario_kind]} (
        <code>{document.scenario_kind}</code>)
      </h2>
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

      {/* --- Objective + rule that produced the cap (block 4) ------------- */}
      <h3 className="section-subtitle">Optimized objective and the rule behind it</h3>
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
          <div className="confirm-row">
            <dt>Note</dt>
            <dd className="section-note">{provenance.note}</dd>
          </div>
        </dl>
      ) : (
        <p className="section-note">
          No cap provenance is attached to this scenario, so no objective can be
          named — and no cap is shown, because the contract forbids surfacing a
          material value without its provenance.
        </p>
      )}
      <p className="section-note">
        The full citation chain for this number — snapshot, section, quoted
        text, source, retrieval and verification status — is in the evaluated
        input and provenance disclosure below.
      </p>
    </section>
  );
}
