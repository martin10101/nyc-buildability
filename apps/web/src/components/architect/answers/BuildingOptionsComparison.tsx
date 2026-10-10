import {
  COMPARISON_NOT_KNOWN,
  type BuildingOptionsComparisonView,
  type ComparisonColumn,
} from "@/lib/architect/first-building-options";
import { SITE_FIT_NOT_VERIFIED } from "@/lib/architect/presented-results";

/**
 * One comparison of the step-P6 method's buildings, side by side (M5-T149 part B; presentation
 * contract §2 point 5 "What changes between options?", §3 "stacked option summaries with a detailed
 * table behind them"; row R894). Every value is READ from the view the document built (ruling V2):
 * this component types no number, condition or reason. The owner's question A2 is open, so every
 * building is shown and NONE is preferred (row R894). A building that was not worked reads "Not
 * known" with its reason — never 0 and never an empty cell — and that one wording is used for every
 * unavailable cell (row R894). A scheduled building is never "achieved" (row R895).
 *
 * Two presentations of the same buildings, both in the DOM: per-building summaries that sit side by
 * side on a wide screen and stack on a narrow one (the "stacked option summaries"); and one aligned
 * table, in a labelled, keyboard-reachable scroll region, with identical rows, order and units for
 * every building (the "detailed table behind them"). No status is told by colour; the words carry it.
 */

/** The lead: the buildings are shown together, and none is preferred (question A2 open, row R894). */
const COMPARISON_LEAD =
  "The method's buildings, side by side on the same measures. None is ranked ahead of the others, and none is checked against where it would sit on the lot.";

/** The comparison's metric rows, in one fixed order with one unit each — the SAME rows for every
 * building (row R894). A not-worked building reads the one not-known wording in each cell. */
const METRIC_ROWS: { id: string; label: string; cell: (column: ComparisonColumn) => string }[] = [
  { id: "storeys", label: "Storeys", cell: c => (c.kind === "worked" ? c.storeys : COMPARISON_NOT_KNOWN) },
  { id: "height", label: "Height", cell: c => (c.kind === "worked" ? c.height : COMPARISON_NOT_KNOWN) },
  {
    id: "scheduled-area",
    label: "Scheduled area",
    cell: c => (c.kind === "worked" ? c.scheduledArea : COMPARISON_NOT_KNOWN),
  },
  {
    id: "plan-per-storey",
    label: "Plan per storey",
    cell: c => (c.kind === "worked" ? c.planPerStorey : COMPARISON_NOT_KNOWN),
  },
  { id: "estimate", label: "Estimate", cell: c => (c.kind === "worked" ? c.estimate : COMPARISON_NOT_KNOWN) },
];

export function BuildingOptionsComparison({ view }: { view: BuildingOptionsComparisonView }) {
  return (
    <section
      className="bo-compare"
      data-testid="building-options-comparison"
      aria-label="How the building options compare"
    >
      <h4 className="bo-compare-title">How the building options compare</h4>
      <p className="bo-compare-lead" data-testid="building-options-comparison-lead">
        {COMPARISON_LEAD}
      </p>

      {/* The stacked option summaries: side by side on a wide screen, stacked on a narrow one. */}
      <div className="bo-compare-summaries" data-testid="comparison-summaries">
        {view.columns.map((column, index) => (
          <ComparisonSummary key={`${column.building}-${index}`} column={column} />
        ))}
      </div>

      {/* The detailed table behind them. On a narrow screen it scrolls INSIDE this box, not the page;
          the box is a named, keyboard-reachable region so every column stays reachable. */}
      <div
        className="bo-compare-table-scroll"
        data-testid="comparison-table-scroll"
        role="region"
        aria-label="Building options compared, in a table"
        tabIndex={0}
      >
        <table className="bo-compare-table" data-testid="comparison-table">
          <caption className="bo-compare-caption">
            The method&apos;s buildings compared on the same measures
          </caption>
          <thead>
            <tr>
              <th scope="col" className="bo-compare-corner bo-compare-rowhead">
                Measure
              </th>
              {view.columns.map((column, index) => (
                <th scope="col" key={`${column.building}-${index}`} data-testid="comparison-column-head">
                  {column.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {METRIC_ROWS.map(row => (
              <tr key={row.id} data-testid="comparison-row">
                <th scope="row" className="bo-compare-rowhead" data-testid="comparison-row-head">
                  {row.label}
                </th>
                {view.columns.map((column, index) => (
                  <td key={`${column.building}-${index}`} data-testid="comparison-cell">
                    {row.cell(column)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

/** One building's summary: a worked building lists its measures under "Site fit not verified"; a
 * not-worked building reads the one not-known wording with its reason (never 0, never empty). */
function ComparisonSummary({ column }: { column: ComparisonColumn }) {
  if (column.kind === "not_worked") {
    return (
      <div
        className="bo-compare-summary bo-compare-summary-not-worked"
        data-testid="comparison-summary"
      >
        <h5 className="bo-compare-summary-label" data-testid="comparison-summary-label">
          {column.label}
        </h5>
        <p className="bo-compare-not-known" data-testid="comparison-summary-not-known">
          {COMPARISON_NOT_KNOWN} — {column.reason}
        </p>
      </div>
    );
  }
  return (
    <div className="bo-compare-summary" data-testid="comparison-summary">
      <h5 className="bo-compare-summary-label" data-testid="comparison-summary-label">
        {column.label}
      </h5>
      <p className="bo-compare-site-fit" data-testid="comparison-summary-site-fit">
        {SITE_FIT_NOT_VERIFIED}
      </p>
      <dl className="bo-compare-summary-metrics">
        <div className="bo-row">
          <dt>Storeys</dt>
          <dd>{column.storeys}</dd>
        </div>
        <div className="bo-row">
          <dt>Height</dt>
          <dd>{column.height}</dd>
        </div>
        <div className="bo-row">
          <dt>Scheduled area</dt>
          <dd>{column.scheduledArea}</dd>
        </div>
        <div className="bo-row">
          <dt>Plan per storey</dt>
          <dd>{column.planPerStorey}</dd>
        </div>
        <div className="bo-row">
          <dt>Estimate</dt>
          <dd>{column.estimate}</dd>
        </div>
      </dl>
    </div>
  );
}
