import { Fragment } from "react";
import { formatValue } from "@/lib/format";
import { CONSTRAINT_STATE_LABELS, provenanceLeaves } from "@/lib/scenario-display";
import type { Scenario, ScenarioConstraint } from "@/lib/scenario-contract";

/**
 * The constraint breakdown and the platform integrity check, HOISTED so they
 * render on every branch (task M5-T004 rework).
 *
 * Both blocks previously lived inside ScenarioCard, which only the
 * `preliminary` branch mounts. A `no_scenario` or `unsupported` document
 * therefore dropped all 11 constraints and the whole integrity record: measured
 * on the data-conflict fixture, 0 of 96 constraint leaves and 0 of 5 integrity
 * leaves reached the screen (DCV-5, G4-4). Those are the documents where the
 * constraint list matters MOST — it is where the conflicting values live, and
 * where the eight notes reading "MUST NOT be inferred, defaulted, or estimated"
 * live.
 *
 * Three further drops are closed here:
 *   - `constraints[].note` (schema-required) is rendered. It is the only
 *     carrier of the anti-inference warning on every missing family, and of the
 *     full "NOT a buildable envelope … NOT Verified" text on the FAR cap. The
 *     state label is weaker, not equivalent (G1-4, DCV-8).
 *   - `constraints[].provenance` is rendered LEAF BY LEAF through the generic
 *     walk, so `source_id`, `dataset_version`, `review_reasons`,
 *     `coverage_note`, `lot_overall_class` and anything else the server
 *     attaches all surface, instead of the hand-listed subset that dropped them
 *     (G1-8, G3-14/15, DCV-8).
 *   - `integrity_check.tolerance` is rendered. The method string is literally
 *     uninterpretable without it — it reads "abs(recomputed - canonical) <=
 *     tolerance * max(1, abs(canonical))" and the tolerance never appeared
 *     (DCV-9).
 */

function ConstraintProvenance({ constraint }: { constraint: ScenarioConstraint }) {
  if (constraint.provenance === null || constraint.provenance === undefined) {
    return (
      <p className="section-note" style={{ margin: 0 }}>
        No provenance is attached to this constraint by the document.
      </p>
    );
  }
  const { leaves, truncated } = provenanceLeaves(constraint.provenance);
  if (leaves.length === 0) {
    return (
      <p className="section-note" style={{ margin: 0 }}>
        A provenance object is attached but records no fields.
      </p>
    );
  }
  return (
    <details
      className="provenance-details"
      data-testid={`scenario-constraint-provenance-${constraint.key}`}
    >
      <summary>Provenance for this constraint ({leaves.length})</summary>
      <div className="provenance-body">
        <dl>
          {leaves.map((leaf) => (
            <Fragment key={leaf.path}>
              <dt>{leaf.path}</dt>
              <dd>{leaf.value}</dd>
            </Fragment>
          ))}
        </dl>
        {truncated ? (
          <p className="section-note" style={{ marginBottom: 0 }}>
            This provenance record is larger than this view shows; the omission
            is stated here rather than left silent.
          </p>
        ) : null}
      </div>
    </details>
  );
}

export function ScenarioConstraints({ document }: { document: Scenario }) {
  return (
    <section className="card" data-testid="scenario-constraints-section">
      <h2 className="section-title">
        Constraints considered ({document.constraints.length})
      </h2>
      <p className="section-note">
        Every candidate constraint the engine looked at, with the state it is in
        and the note it carries. A constraint recorded as <code>missing</code> is
        a gap: it may never be inferred, defaulted, or estimated, and no number
        on this screen accounts for it.
      </p>
      {document.constraints.length === 0 ? (
        <p className="section-note" data-testid="scenario-constraints-empty">
          The document lists no constraints at all. That is unexpected for a
          scenario and is stated here rather than shown as an empty section.
        </p>
      ) : (
        <ul className="missing-list" data-testid="scenario-constraints">
          {document.constraints.map((constraint, index) => (
            <li
              key={`constraint-${index}`}
              data-testid={`scenario-constraint-${constraint.key}`}
            >
              <strong>{constraint.key}</strong>
              {": "}
              <span className="fact-value">{formatValue(constraint.value)}</span>
              {constraint.unit !== null ? (
                <span className="fact-units"> {constraint.unit}</span>
              ) : null}{" "}
              <span className="section-note">
                (state: <code>{constraint.state}</code> —{" "}
                {CONSTRAINT_STATE_LABELS[constraint.state]}; completeness:{" "}
                <code>{constraint.data_completeness}</code>)
              </span>
              <p style={{ margin: 0 }} data-testid={`scenario-constraint-note-${constraint.key}`}>
                {constraint.note === ""
                  ? "The document records an empty note for this constraint."
                  : constraint.note}
              </p>
              <ConstraintProvenance constraint={constraint} />
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export function IntegrityCheckBlock({ document }: { document: Scenario }) {
  const check = document.integrity_check;
  return (
    <section className="card" data-testid="scenario-integrity-section">
      <h2 className="section-title">Platform integrity check</h2>
      <p className="section-note">
        A verification-only recompute the platform runs against its own
        canonical trace value. It never replaces the surfaced number, and a
        disagreement fails closed (no cap at all).
      </p>
      <p data-testid="scenario-integrity">
        {check.performed
          ? `Performed — recompute ${
              check.agreed === true
                ? "agreed with"
                : check.agreed === false
                  ? "did NOT agree with"
                  : "result unrecorded against"
            } the canonical trace value.`
          : "Not performed for this scenario."}{" "}
        {check.note === "" ? "No note was recorded." : check.note}
      </p>
      <p className="failure-meta" data-testid="scenario-integrity-method">
        Method: <code>{check.method}</code> · tolerance used:{" "}
        <code data-testid="scenario-integrity-tolerance">
          {formatValue(check.tolerance)}
        </code>
      </p>
    </section>
  );
}
