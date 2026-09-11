import Link from "next/link";
import { boundedText } from "@/lib/bounded";
import { completenessDisplay, coverageDisplay } from "@/lib/coverage";
import { formatValue } from "@/lib/format";
import { SCENARIO_KIND_LABELS, envelopeBlockingGaps } from "@/lib/scenario-display";
import type { Scenario } from "@/lib/scenario-contract";
import { CoverageMatrixSection } from "./CoverageMatrixSection";
import { NoScenarioBlock } from "./NoScenarioBlock";
import { ScenarioAssumptions } from "./ScenarioAssumptions";
import { ScenarioCard } from "./ScenarioCard";
import { IntegrityCheckBlock, ScenarioConstraints } from "./ScenarioConstraints";
import { ScenarioProvenance } from "./ScenarioProvenance";
import { ScenarioReasons } from "./ScenarioReasons";

/**
 * Success document renderer for the Compare (Step 3) screen (task M5-T004).
 *
 * Renders the honesty-preserving Step-3 blocks from PRODUCT_FLOW §"Step 3 —
 * Compare": maximum preliminary development potential, the practical-usable-
 * range disclosure, the ranked scenario card (or the no_scenario reason +
 * preserved share ranges), the optimized objective, the constraint breakdown,
 * the coverage labels + rule gaps, the main opportunity + main risk, and one
 * clear next action. Every value comes from the validated document; nothing is
 * computed, ranked, or invented in the client.
 *
 * COMPOSITION IS THE FIX (M5-T004 rework). The two branches used to be
 * DISJOINT — `reasons` rendered only on the no_scenario side, `constraints` and
 * `integrity_check` only on the preliminary side — so NEITHER branch ever
 * showed the whole document (G4-4, DCV-5/10). Everything that belongs to the
 * document rather than to one branch is now mounted here, once, for every
 * branch; only the cap card and the no-scenario block are branch-specific.
 */

/**
 * Block 2: the honest practical-usable-range disclosure.
 *
 * The first sentence is DEFINITIONAL — what a zoning-floor-area cap is and is
 * not. It narrows the claim rather than asserting a fact about this property,
 * so it is safe as fixed copy.
 *
 * The second is not, and used to be hard-coded: "the rule families that would
 * bound a real envelope (height, setbacks, lot coverage, street wall, and
 * others) are still missing" was a client-authored factual claim, true only
 * because the builder happens to emit those families as missing today. M4-T006
 * (R5 height and setbacks) is already in flight. On the day an envelope family
 * ships, that sentence would have become FALSE on a legal-adjacent screen, with
 * nothing in the suite able to detect it — the same client-prose-substituting-
 * for-server-truth defect this packet originally failed for, rebuilt one
 * paragraph to the left. It is now read from `coverage_matrix`, which carries
 * `blocks_buildable_envelope` for precisely this question.
 */
function PracticalRangeBlock({ document }: { document: Scenario }) {
  const blocking = envelopeBlockingGaps(document);
  return (
    <section className="card" data-testid="scenario-practical-range">
      <h2 className="section-title">Practical usable range</h2>
      <p>
        The value above is a draft <em>zoning-floor-area cap</em> only — it is
        not gross, net, sellable, or feasible area, and it is not a buildable
        envelope.
      </p>
      {blocking.length === 0 ? (
        <p data-testid="scenario-practical-range-no-blockers">
          This document records no rule family as both missing and blocking a
          buildable envelope. That is not the same as a practical usable range
          being available: the platform states only what the scenario document
          carries, and this document carries no such range. Nothing on this
          screen infers one.
        </p>
      ) : (
        <p data-testid="scenario-practical-range-blockers">
          No practical usable range can be stated, because this document records{" "}
          {blocking.length}{" "}
          {blocking.length === 1 ? "rule family" : "rule families"} that would
          bound a buildable envelope as still missing:{" "}
          {blocking.map((row) => row.constraint_family).join(", ")}. They are
          listed with the other gaps below.
        </p>
      )}
    </section>
  );
}

/**
 * The identity binding. Before the rework the heading printed the BBL from the
 * `?bbl=` URL parameter and `document.evaluated_input.bbl` was never read, so a
 * document returned for a DIFFERENT property was indistinguishable on screen —
 * an authored identity on a legally sensitive page (DCV CRITICAL-2, G1-7). The
 * shipped test demonstrated it live: it rendered `bbl="1000010100"` over
 * fixtures that all state `evaluated_input.bbl = "1000477501"`, and nothing
 * detected it.
 *
 * The document's own BBL is now the identity shown, a null is stated as "not
 * stated" (the RuleEvaluationResult.tsx:87 precedent), and a disagreement is
 * SURFACED rather than papered over.
 */
function IdentityMismatchNotice({
  evaluatedBbl,
  requestedBbl,
}: {
  evaluatedBbl: string | null;
  requestedBbl: string;
}) {
  if (evaluatedBbl === null) {
    return (
      <p className="status-label" data-testid="scenario-bbl-not-stated">
        This document does not state which BBL it was evaluated for. It was
        requested for BBL {requestedBbl}, but that is this screen&apos;s request,
        not the document&apos;s own claim.
      </p>
    );
  }
  if (evaluatedBbl === requestedBbl) return null;
  return (
    <p className="status-label" data-testid="scenario-bbl-mismatch">
      IDENTITY MISMATCH — this scenario states it was evaluated for BBL{" "}
      {evaluatedBbl}, but it was requested for BBL {requestedBbl}. Do not treat
      anything below as describing BBL {requestedBbl}. Both values are shown;
      nothing has been reconciled.
    </p>
  );
}

function ScenarioSummary({
  document,
  requestedBbl,
}: {
  document: Scenario;
  requestedBbl: string;
}) {
  const coverage = coverageDisplay(document.coverage_status);
  const completeness = completenessDisplay(document.data_completeness);
  const evaluatedBbl =
    document.evaluated_input.bbl === null
      ? null
      : boundedText(document.evaluated_input.bbl, "");
  return (
    <section className="card" data-testid="scenario-summary">
      {/* Success-outcome focus target (mirrors ConfirmCard). */}
      <h2 className="section-title" tabIndex={-1} data-outcome-heading>
        Step 3 — Preliminary comparison for BBL{" "}
        <span data-testid="scenario-heading-bbl">
          {evaluatedBbl === null || evaluatedBbl === "" ? "not stated" : evaluatedBbl}
        </span>
      </h2>
      <IdentityMismatchNotice
        evaluatedBbl={evaluatedBbl === "" ? null : evaluatedBbl}
        requestedBbl={requestedBbl}
      />

      {/* The document's OWN completeness verdict. It is `missing_critical` in
          every committed fixture, including the one that produces the 15,000 sq
          ft cap — and before the rework this screen showed the milder coverage
          gloss and never the critical one, on the exact page carrying its most
          quantified claim (G1-3, G3-1, DCV-3). */}
      <div
        className="completeness-banner"
        role="status"
        data-testid="scenario-completeness"
      >
        <p className="completeness-headline">
          {completeness.headline} (<code>{completeness.value}</code>)
        </p>
        <p>{completeness.gloss}</p>
      </div>

      <p className="section-note" data-testid="scenario-coverage-status">
        Coverage label: <code>{coverage.symbol} {coverage.value}</code> —{" "}
        {coverage.gloss}
      </p>
      <p className="section-note" data-testid="scenario-kind">
        Scenario kind: <code>{document.scenario_kind}</code> —{" "}
        {SCENARIO_KIND_LABELS[document.scenario_kind]}
      </p>
      <p className="section-note" data-testid="scenario-disclaimer">
        {document.not_verified_disclaimer}
      </p>
    </section>
  );
}

/** Block 7: main opportunity + main risk, both derived from document fields. */
function OpportunityRiskBlock({ document }: { document: Scenario }) {
  const cap = document.draft_zoning_floor_area_cap_sq_ft;
  return (
    <section className="card" data-testid="scenario-opportunity-risk">
      <h2 className="section-title">Main opportunity and main risk</h2>
      <div data-testid="scenario-opportunity">
        <h3 className="section-subtitle">Main opportunity</h3>
        <p>
          {cap !== null
            ? `A draft residential zoning floor-area cap of ${formatValue(
                cap,
              )} square feet is available as a starting point for a preliminary study.`
            : "No draft maximum is available for this property today, so there is no quantified opportunity to surface — only the reasons and preserved ranges above."}
        </p>
      </div>
      <div data-testid="scenario-risk">
        <h3 className="section-subtitle">Main risk</h3>
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
      <h2 className="section-title">Next step</h2>
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
  return (
    <div data-testid="scenario-result">
      <ScenarioSummary document={document} requestedBbl={bbl} />

      {/* Branch-specific: the cap card, or the informative no-maximum block. */}
      {isPreliminary ? (
        <ScenarioCard document={document} rank={1} />
      ) : (
        <NoScenarioBlock document={document} />
      )}

      {/* Document-level: mounted on EVERY branch. */}
      <ScenarioReasons document={document} />
      <PracticalRangeBlock document={document} />
      <ScenarioAssumptions document={document} />
      <ScenarioConstraints document={document} />
      <IntegrityCheckBlock document={document} />
      <CoverageMatrixSection document={document} />
      <ScenarioProvenance document={document} requestedBbl={bbl} />
      <OpportunityRiskBlock document={document} />
      <NextActionBlock bbl={bbl} />
    </div>
  );
}
