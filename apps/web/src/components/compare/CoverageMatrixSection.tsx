import type { CoverageStatus } from "@/lib/contract";
import { coverageDisplay } from "@/lib/coverage";
import { COVERAGE_MATRIX_STATUS_LABELS, missingCoverageGaps } from "@/lib/scenario-display";
import type { Scenario } from "@/lib/scenario-contract";

/**
 * Coverage labels + coverage-matrix gaps for the Compare (Step 3) screen
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
 *  2. Every coverage_matrix family that is MISSING today, listed as a visible
 *     gap with its `governs` text and whether it blocks a buildable envelope
 *     (AS-3). This is why a draft floor-area cap is NOT a buildable envelope.
 *
 * No legal computation: the labels only explain the exact contract values and
 * the exact values are always shown.
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

export function CoverageMatrixSection({ document }: { document: Scenario }) {
  const gaps = missingCoverageGaps(document);
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
          return (
            <li key={status}>
              {/* Plain text, deliberately NOT the badge component (S7). */}
              <code data-testid={`coverage-label-${status}`}>
                {display.symbol} {display.value}
              </code>{" "}
              <span className="legend-gloss">{display.gloss}</span>
            </li>
          );
        })}
      </ul>

      <h3 className="section-subtitle">
        Rule families still missing ({gaps.length})
      </h3>
      {gaps.length === 0 ? (
        <p className="section-note" data-testid="coverage-no-gaps">
          No coverage-matrix family is recorded as missing for this scenario.
        </p>
      ) : (
        <ul className="missing-list" data-testid="coverage-gaps">
          {gaps.map((row) => (
            <li key={row.constraint_family} data-testid={`coverage-gap-${row.constraint_family}`}>
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
