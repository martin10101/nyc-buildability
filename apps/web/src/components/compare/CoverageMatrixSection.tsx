import type { CoverageStatus } from "@/lib/contract";
import { coverageDisplay } from "@/lib/coverage";
import { COVERAGE_MATRIX_STATUS_LABELS, missingCoverageGaps } from "@/lib/scenario-display";
import type { Scenario } from "@/lib/scenario-contract";

/**
 * Coverage labels + the coverage matrix for the Compare (Step 3) screen
 * (task M5-T004, PRODUCT_FLOW Step 3 blocks 5 and 6).
 *
 * Two honesty jobs:
 *
 *  1. A FULL-VOCABULARY coverage legend rendering every coverage status —
 *     verified / conditional / professional_review_required / data_conflict /
 *     unsupported / not_applicable — as a distinct PLAIN-TEXT label + gloss
 *     (AS-3). It is deliberately NOT the CoverageBadge component: no
 *     `.status-verified` badge node may exist in the DOM for a status the
 *     scenario does not carry (a scenario is never Verified — the S7 honesty
 *     invariant), and this list only documents the vocabulary. The scenario's
 *     OWN coverage_status is surfaced separately by the result header.
 *
 *  2. The coverage matrix, in FULL. Before the rework only the `missing` rows
 *     rendered: the preliminary fixture's 11 rows became 8, and the one `draft`
 *     row — the R5 residential-FAR family that actually produced the number on
 *     screen — plus both `out_of_scope` rows were filtered out with no
 *     disclosure that anything had been filtered (DCV-7). The schema is explicit
 *     that the matrix is "emitted on every scenario in a fixed order". Every row
 *     now renders with its status, and the MISSING rows are additionally called
 *     out as gaps, which is what a reader of a draft cap most needs.
 */

/** Full coverage vocabulary, ordered most→least assured. `verified` is listed
 * ONLY as vocabulary (a scenario never carries it). */
const COVERAGE_VOCABULARY: readonly CoverageStatus[] = [
  "verified",
  "conditional",
  "professional_review_required",
  "data_conflict",
  "unsupported",
  "not_applicable",
];

/**
 * Where a coverage word means something narrower in the SCENARIO contract than
 * the shared profile gloss says, the scenario meaning is stated alongside
 * rather than left to collide silently (DCV-11). The shared gloss lives in
 * lib/coverage.ts, an accepted M2-T001 module outside this task's scope, so it
 * is annotated here rather than rewritten there.
 */
const SCENARIO_STATUS_NOTES: Partial<Record<CoverageStatus, string>> = {
  unsupported:
    "On a scenario this specifically means the district or rule family is not implemented yet — not that a data problem was detected.",
};

export function CoverageMatrixSection({ document }: { document: Scenario }) {
  const gaps = missingCoverageGaps(document);
  const matrix = document.coverage_matrix;
  return (
    <section
      className="card"
      aria-labelledby="compare-coverage-title"
      data-testid="compare-coverage"
    >
      <h2 className="section-title" id="compare-coverage-title">
        Coverage labels and rule gaps
      </h2>
      <p className="section-note">
        Coverage never rises above <code>conditional</code> for a scenario — a
        scenario is never Verified. The label is shown as text (never by color
        alone), and the rule families still missing are listed so the draft cap
        is never mistaken for a complete, buildable answer.
      </p>

      <h3 className="section-subtitle">What the coverage labels mean</h3>
      <ul className="legend-list" data-testid="coverage-vocabulary">
        {COVERAGE_VOCABULARY.map((status) => {
          const display = coverageDisplay(status);
          const scenarioNote = SCENARIO_STATUS_NOTES[status];
          return (
            <li key={status}>
              {/* Plain text, deliberately NOT the badge component (S7). */}
              <code data-testid={`coverage-label-${status}`}>
                {display.symbol} {display.value}
              </code>{" "}
              <span className="legend-gloss">
                {display.gloss}
                {scenarioNote ? ` ${scenarioNote}` : ""}
              </span>
            </li>
          );
        })}
      </ul>

      <h3 className="section-subtitle">
        Full rule-coverage matrix ({matrix.length}{" "}
        {matrix.length === 1 ? "family" : "families"})
      </h3>
      {matrix.length === 0 ? (
        <p className="section-note" data-testid="coverage-matrix-empty">
          The document carries no coverage matrix. The contract emits one on
          every scenario, so its absence is stated here rather than hidden.
        </p>
      ) : (
        <ul className="missing-list" data-testid="coverage-matrix-all">
          {matrix.map((row, index) => (
            <li
              key={`matrix-${index}`}
              data-testid={`coverage-row-${row.constraint_family}`}
            >
              <strong>{row.constraint_family}</strong>
              {row.governs ? <> — {row.governs}</> : null}{" "}
              <span className="section-note">
                (status: <code>{row.rule_status_today}</code> —{" "}
                {COVERAGE_MATRIX_STATUS_LABELS[row.rule_status_today]};{" "}
                {row.blocks_buildable_envelope
                  ? "blocks a buildable envelope"
                  : "does not block a buildable envelope"}
                )
              </span>
            </li>
          ))}
        </ul>
      )}

      <h3 className="section-subtitle">
        Rule families still missing ({gaps.length})
      </h3>
      {gaps.length === 0 ? (
        <p className="section-note" data-testid="coverage-no-gaps">
          No coverage-matrix family is recorded as missing for this scenario.
        </p>
      ) : (
        <ul className="missing-list" data-testid="coverage-gaps">
          {gaps.map((row, index) => (
            <li
              key={`gap-${index}`}
              data-testid={`coverage-gap-${row.constraint_family}`}
            >
              <strong>{row.constraint_family}</strong>
              {row.governs ? <> — {row.governs}</> : null}{" "}
              <span className="section-note">
                (status: <code>{row.rule_status_today}</code> —{" "}
                {COVERAGE_MATRIX_STATUS_LABELS[row.rule_status_today]};{" "}
                {row.blocks_buildable_envelope
                  ? "blocks a buildable envelope"
                  : "does not block a buildable envelope"}
                )
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
