import {
  CEILING_NOT_AVAILABLE,
  DRAFT_GATED_LINE,
  ESTIMATE_NOT_AVAILABLE,
  apartmentFiguresView,
  type ApartmentEstimateView,
  type LegalCeiling,
} from "@/lib/architect/apartment-figures";
import type { ThreeAnswersResults } from "@/lib/architect/three-answers";

/**
 * The page-1 parity block (M5-T171; D-094 R041/R057): the legal ceiling beside the apartment
 * estimate, the identical distinction line beneath them, the R055 lot-area assumption line and, while
 * the zoning lot is unconfirmed, the zoning-lot concern — the SAME answer report page 1 shows. It is
 * ADDITIVE: it changes no other card (the allowance card keeps its own value); the legal ceiling and
 * the estimate are side by side and DISTINCT, each told apart by its WORD (the status label), never
 * by colour alone.
 *
 * Every figure is read from the document through apartment-figures.ts; nothing is recalculated here.
 * Where the document carries no legal unit limit or no capacity estimate the block shows no figure and
 * says so in plain words; a withheld ceiling shows the document's own reason; the 29 is never shown as
 * settled. The block uses its OWN test ids — never answer-conditional-marker / answer-value /
 * answer-headline-number, which whole-panel and e2e tests query across the rest of the panel.
 *
 * `showDraftValues` carries the panel's draft gate (D-090-R010): a draft document on an architect
 * surface (the flag off) hides every figure here exactly as the answer cards do, so an unreviewed
 * number never reaches an architect.
 */
export function ApartmentFigures({
  results,
  showDraftValues = false,
}: {
  results: ThreeAnswersResults;
  showDraftValues?: boolean;
}) {
  const view = apartmentFiguresView(results, showDraftValues);
  if (view.draftGated) {
    return (
      <section
        className="af-figures"
        data-testid="apartment-figures"
        aria-label="The legal ceiling and the apartment estimate"
      >
        <p className="af-not-available" data-testid="apartment-figures-draft-gated">
          {DRAFT_GATED_LINE}
        </p>
      </section>
    );
  }
  return (
    <section
      className="af-figures"
      data-testid="apartment-figures"
      aria-label="The legal ceiling and the apartment estimate"
    >
      <h3 className="af-title">The legal ceiling and the apartment estimate</h3>
      <div className="af-pair">
        <CeilingCell ceiling={view.ceiling} />
        <EstimateCell estimate={view.estimate} />
      </div>
      <p className="af-distinction" data-testid="apartment-figures-distinction">
        {view.distinction}
      </p>
      <p className="af-lot-area" data-testid="apartment-figures-lot-area">
        {view.lotArea}
      </p>
      {view.zoningLotConcern !== null ? (
        <p className="af-zoning-lot" data-testid="apartment-figures-zoning-lot">
          {view.zoningLotConcern}
        </p>
      ) : null}
    </section>
  );
}

/** The legal-ceiling half of the pair: a shown figure with its own (never settled) label, a withheld
 * ceiling as the document's reason with its label, or a plain "not available" line — never a number
 * that is not in the document. */
function CeilingCell({ ceiling }: { ceiling: LegalCeiling }) {
  if (ceiling.kind === "value") {
    return (
      <div className="af-cell af-ceiling" data-testid="apartment-figures-ceiling">
        <span className="af-figure" data-testid="apartment-figures-ceiling-value">
          {`Legal ceiling ${ceiling.figure}`}
        </span>
        <StatusChip label={ceiling.label} testid="apartment-figures-ceiling-chip" />
      </div>
    );
  }
  if (ceiling.kind === "withheld") {
    return (
      <div className="af-cell af-ceiling" data-testid="apartment-figures-ceiling">
        <span className="af-figure" data-testid="apartment-figures-ceiling-value">
          {`Legal ceiling: ${ceiling.reason}`}
        </span>
        <StatusChip label={ceiling.label} testid="apartment-figures-ceiling-chip" />
      </div>
    );
  }
  return (
    <div className="af-cell af-ceiling" data-testid="apartment-figures-ceiling">
      <span className="af-figure" data-testid="apartment-figures-ceiling-value">
        {CEILING_NOT_AVAILABLE}
      </span>
    </div>
  );
}

/** The apartment-estimate half of the pair: the range from the document labelled Provisional, or a
 * plain "not available" line — never an invented range. */
function EstimateCell({ estimate }: { estimate: ApartmentEstimateView }) {
  if (estimate.kind === "value") {
    return (
      <div className="af-cell af-estimate" data-testid="apartment-figures-estimate">
        <span className="af-figure" data-testid="apartment-figures-estimate-value">
          {estimate.figure}
        </span>
        <StatusChip label={estimate.label} testid="apartment-figures-estimate-chip" />
      </div>
    );
  }
  return (
    <div className="af-cell af-estimate" data-testid="apartment-figures-estimate">
      <span className="af-figure" data-testid="apartment-figures-estimate-value">
        {ESTIMATE_NOT_AVAILABLE}
      </span>
    </div>
  );
}

/** The status label beside a figure, a plain-word pill. The meaning is the WORD (Conditional /
 * Provisional / …); both chips carry the same neutral surface, so status is never told by colour
 * alone (presentation contract; the design rule). It uses the block's own test id, never
 * answer-conditional-marker. */
function StatusChip({ label, testid }: { label: string; testid: string }) {
  return (
    <span className="af-chip" data-testid={testid}>
      {label}
    </span>
  );
}
