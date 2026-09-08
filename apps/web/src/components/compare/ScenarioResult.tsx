import Link from "next/link";
import { coverageDisplay } from "@/lib/coverage";
import { formatValue } from "@/lib/format";
import {
  baseDistrictCandidates,
  findConstraint,
  SCENARIO_KIND_LABELS,
} from "@/lib/scenario-display";
import type { Scenario } from "@/lib/scenario-contract";
import { CoverageMatrixSection } from "./CoverageMatrixSection";
import { ScenarioCard } from "./ScenarioCard";

/**
 * Success document renderer for the Compare (Step 3) screen (task M5-T004).
 *
 * Renders the honesty-preserving Step-3 blocks from PRODUCT_FLOW §"Step 3 —
 * Compare": maximum preliminary development potential, the practical-usable-
 * range disclosure, the ranked scenario card (or the no_scenario reason +
 * preserved share ranges), the optimized objective + score breakdown, the
 * coverage labels + rule gaps, the main opportunity + main risk, and one clear
 * next action. Every value comes from the validated document; nothing is
 * computed, ranked, or invented in the client.
 */

/** Block 1 for a no_scenario / unsupported document: an INFORMATIVE "no
 * maximum can be stated" block with the reasons — never an error. Also carries
 * block 3 (review label + preserved share ranges), which the ScenarioCard
 * carries for the preliminary case. */
function NoScenarioBlock({ document }: { document: Scenario }) {
  const candidates = baseDistrictCandidates(findConstraint(document, "zoning_district"));
  return (
    <section className="card" data-testid="scenario-no-scenario">
      <h3 className="section-title">
        {SCENARIO_KIND_LABELS[document.scenario_kind]} — no maximum can be stated
      </h3>
      <p>
        No draft maximum development potential could be stated for this property.
        This is an informative result from the deterministic engine, not an
        error: the reasons below explain what stopped a scenario, and any
        preserved ranges are shown rather than collapsed into a single value.
      </p>
      {document.professional_review_required ? (
        <p className="status-label" data-testid="scenario-review-required">
          Professional review required before any reliance.
        </p>
      ) : null}

      <h4 className="section-subtitle">Why no scenario was produced</h4>
      <ul className="missing-list" data-testid="scenario-reasons">
        {document.reasons.map((reason) => (
          <li key={reason}>{reason}</li>
        ))}
      </ul>

      {candidates.length > 0 ? (
        <>
          <h4 className="section-subtitle">
            Preserved base-district share ranges (never collapsed)
          </h4>
          <ul className="missing-list" data-testid="scenario-share-ranges">
            {candidates.map((candidate, index) => (
              <li
                key={`${candidate.districtLabel ?? "district"}-${index}`}
                data-testid="scenario-share-range"
              >
                <strong>{candidate.districtLabel ?? "Unlabelled district"}</strong>
                {": "}
                share range min {formatValue(candidate.shareMin)} / point{" "}
                {formatValue(candidate.sharePoint)} / max{" "}
                {formatValue(candidate.shareMax)}
                {candidate.minorPortion ? " (minor portion)" : ""}
              </li>
            ))}
          </ul>
        </>
      ) : null}
    </section>
  );
}

/** Block 2: the honest practical-usable-range disclosure. The cap is a draft
 * zoning-floor-area cap, NOT gross/net/sellable/feasible area or a buildable
 * envelope, so a practical usable range cannot be derived — because the
 * buildable-envelope families are MISSING (see coverage gaps). */
function PracticalRangeBlock() {
  return (
    <section className="card" data-testid="scenario-practical-range">
      <h3 className="section-title">Practical usable range</h3>
      <p>
        A practical usable range (gross, net, sellable, or feasible floor area,
        or a buildable envelope) cannot be derived yet. The value above is a
        draft <em>zoning-floor-area cap</em> only — it is not gross, net,
        sellable, or feasible area, and it is not a buildable envelope. The rule
        families that would bound a real envelope (height, setbacks, lot
        coverage, street wall, and others) are still missing; they are listed as
        gaps below.
      </p>
    </section>
  );
}

/** Block 7: main opportunity + main risk, both derived from document fields. */
function OpportunityRiskBlock({ document }: { document: Scenario }) {
  const cap = document.draft_zoning_floor_area_cap_sq_ft;
  return (
    <section className="card" data-testid="scenario-opportunity-risk">
      <h3 className="section-title">Main opportunity and main risk</h3>
      <div data-testid="scenario-opportunity">
        <h4 className="section-subtitle">Main opportunity</h4>
        <p>
          {cap !== null
            ? `A draft residential zoning floor-area cap of ${formatValue(
                cap,
              )} square feet is available as a starting point for a preliminary study.`
            : "No draft maximum is available for this property today, so there is no quantified opportunity to surface — only the reasons and preserved ranges above."}
        </p>
      </div>
      <div data-testid="scenario-risk">
        <h4 className="section-subtitle">Main risk</h4>
        <p>{document.not_verified_disclaimer}</p>
        {document.professional_review_required ? (
          <p className="status-label">
            This scenario is flagged for professional review before any reliance.
          </p>
        ) : null}
      </div>
    </section>
  );
}

/** Block 8: one clear next action + analysis-preserving back navigation. */
function NextActionBlock({ bbl }: { bbl: string }) {
  return (
    <section className="card next-action" data-testid="scenario-next-action">
      <h3 className="section-title">Next step</h3>
      <p className="section-note">
        Evidence and provenance for every value shown here (Step 4) arrive with
        a later milestone; this build does not pretend to run it.
      </p>
      <Link
        className="primary-button next-action-link"
        href={`/property/confirm?bbl=${encodeURIComponent(bbl)}`}
      >
        Back to the confirmed property
      </Link>{" "}
      <Link className="next-action-link" href="/property">
        Back to property lookup
      </Link>
    </section>
  );
}

export function ScenarioResult({
  document,
  bbl,
}: {
  document: Scenario;
  bbl: string;
}) {
  const isPreliminary = document.scenario_kind === "preliminary";
  const coverage = coverageDisplay(document.coverage_status);
  return (
    <div data-testid="scenario-result">
      <section className="card" data-testid="scenario-summary">
        {/* Success-outcome focus target (mirrors ConfirmCard). */}
        <h2 className="section-title" tabIndex={-1} data-outcome-heading>
          Step 3 — Preliminary comparison for BBL {bbl}
        </h2>
        <p className="section-note" data-testid="scenario-coverage-status">
          Coverage label: <code>{coverage.symbol} {coverage.value}</code> —{" "}
          {coverage.gloss}
        </p>
        <p className="section-note" data-testid="scenario-disclaimer">
          {document.not_verified_disclaimer}
        </p>
      </section>

      {isPreliminary ? (
        <ScenarioCard document={document} rank={1} />
      ) : (
        <NoScenarioBlock document={document} />
      )}

      <PracticalRangeBlock />
      <CoverageMatrixSection document={document} />
      <OpportunityRiskBlock document={document} />
      <NextActionBlock bbl={bbl} />
    </div>
  );
}
