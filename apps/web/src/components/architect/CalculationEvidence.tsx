import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import type { Scenario } from "@/lib/scenario-contract";
import { officialZoningTextUrl } from "@/lib/architect/source-links";
import { formatValue } from "@/lib/format";
import { CoverageBadge } from "@/components/property/CoverageBadge";
import { CapturedRecord } from "./EvidenceRecord";
export function CalculationEvidence({ evaluation, scenario }: {
    evaluation: RuleEvaluation | null;
    scenario: Scenario | null;
}) {
    const traces = evaluation ? [...evaluation.evaluations].sort((a, b) => Number(b.applicability_outcome) - Number(a.applicability_outcome)) : [];
    // DB-025(a,b): the wide-street review label and the "withheld" FAR gate on
    // determination_state, never on a null-FAR heuristic, so a confident
    // within/not-within determination is never mislabeled "Professional review
    // required" here (D-073-R006).
    const wideDeterminationState = evaluation?.wide_street?.determination_state;
    const wideReview = wideDeterminationState === "professional_review_required";
    // DB-025(c): "Wide-street conditional FAR" names the higher conditional value
    // that exists only in the within case (and, withheld, the review case). In the
    // not-within case the value is the CONSERVATIVE standard-row FAR, so its heading
    // and value caption read "Governing floor-area ratio" — the conditional-FAR
    // caption never sits over the conservative value. This mirrors DevelopmentLimits
    // so the screen and the report read identically from the one validated document.
    const wideValueLabel = wideDeterminationState === "not_within_100ft_of_wide_street"
      ? "Governing floor-area ratio"
      : "Wide-street conditional FAR";
    return <div className="architect-calculation-evidence">
    <p className="architect-eyebrow">Deterministic evaluation</p>
    <h2>How this was calculated</h2>
    <p className="architect-status">Draft · Professional review required</p>
    {evaluation ? <>
      <CoverageBadge status={evaluation.coverage_status}/>
      {evaluation.reasons.length > 0 ? <ul className="architect-issue-list">
        {evaluation.reasons.map((reason, i) => <li key={i}>
          {reason}
        </li>)}
      </ul> : null}
      {evaluation.evaluations.length === 0 ? <p>No applicable computation trace was returned. No result is inferred.</p> : null}
      {evaluation.wide_street ? <section className="architect-trace architect-determination architect-wide-street-provenance" data-testid="wide-street-provenance">
        <p className="architect-eyebrow">Wide-street determination</p>
        <h3>{wideValueLabel} · D-052 provenance</h3>
        <p className="architect-status">Draft · {evaluation.wide_street.draft_label}{wideReview ? " · Professional review required" : ""}</p>
        <p>{evaluation.wide_street.reason}</p>
        <p className="section-note">{wideValueLabel} (dimensionless ratio): {wideReview ? "withheld — professional review required" : (evaluation.wide_street.governing_max_residential_far ?? "withheld — professional review required")}. Floor area is derived as FAR × zoning-lot area (sq ft).</p>
        <p className="section-note">{evaluation.wide_street.fallback_direction_note}</p>
        <dl className="architect-definition-list">
          <div><dt>Determination</dt><dd>{evaluation.wide_street.determination_state}</dd></div>
          <div><dt>Conditional-FAR row</dt><dd>{evaluation.wide_street.far_row}</dd></div>
          <div><dt>Exceptions checked</dt><dd>{evaluation.wide_street.exceptions_checked ? "yes" : "no"}</dd></div>
          <div><dt>Named-street override pending</dt><dd>{evaluation.wide_street.named_street_override_pending ? "yes" : "no"}</dd></div>
        </dl>
        <details className="provenance-details">
          <summary>Width-policy decisions and D-052 source provenance</summary>
          <CapturedRecord value={evaluation.wide_street} label="Wide-street determination and D-052 provenance summary"/>
        </details>
      </section> : null}
      {traces.map((trace, index) => <details className="architect-trace architect-determination" key={`${trace.rule_id}-${index}`} open={trace.applicability_outcome}>
        <summary>{trace.applicability_outcome ? "Applicable determination" : "Other determination"} · {trace.rule_id || "Rule identifier not supplied"}</summary>
        <h3>{trace.rule_id || "Rule identifier not supplied"}</h3>
        <p className="section-note">Version {trace.rule_version || "unknown"} · {trace.rule_status} · Applicability: {trace.applicability_outcome ? "applies" : "does not apply"}
        </p>
        <h4>Inputs used</h4>
        <dl className="architect-definition-list">
          {Object.entries(trace.evaluated_inputs).map(([key, value]) => <div key={key}>
            <dt>
              {key}
            </dt>
            <dd>
              {formatValue(value)}
            </dd>
          </div>)}
        </dl>
        <h4>Calculation steps</h4>
        {trace.computation_steps.length ? <div className="table-scroll">
          <table className="facts-table">
            <thead>
              <tr>
                <th>Step / operation</th>
                <th>Resolved inputs</th>
                <th>Result</th>
              </tr>
            </thead>
            <tbody>
              {trace.computation_steps.map(step => <tr key={step.step_id}>
                <th scope="row">
                  {step.step_id} · {step.op}
                  {step.note ? <p className="section-note">
                    {step.note}
                  </p> : null}
                </th>
                <td>
                  {step.resolved_args.map(formatValue).join(" · ")}
                </td>
                <td>
                  {formatValue(step.result)}
                </td>
              </tr>)}
            </tbody>
          </table>
        </div> : <p className="section-note">No calculation steps recorded.</p>}
        <h4>Outputs</h4>
        <dl className="architect-definition-list">
          {Object.entries(trace.outputs).map(([key, value]) => <div key={key}>
            <dt>
              {key}
            </dt>
            <dd>
              {formatValue(value)}
            </dd>
          </div>)}
        </dl>
        <p className="section-note">Units are shown where supplied in the source output.</p>
        <details className="provenance-details">
          <summary>Applicability, validation and uncertainty</summary>
          <CapturedRecord value={{ applicability_trace: trace.applicability_trace, input_validation: trace.input_validation, uncertainty: trace.uncertainty, exceptions_applied: trace.exceptions_applied, notes: trace.notes }}/>
        </details>
        <h4>Rule sources</h4>
        {trace.citations.length ? trace.citations.map((citation, i) => <div className="architect-citation" key={i}>
          <strong>
            {citation.section || "Section not supplied"}
          </strong>
          <blockquote>
            {citation.quote}
          </blockquote>
          <p className="section-note">Snapshot {citation.snapshot_id} · Last amended {citation.last_amended ?? "not supplied"}
          </p>
          {officialZoningTextUrl((citation.provenance as Record<string, unknown>).request_url) ? <p>
            <a href={officialZoningTextUrl((citation.provenance as Record<string, unknown>).request_url)!} target="_blank" rel="noopener noreferrer">Open current official text ↗</a>
          </p> : <p className="section-note">Official text link not supplied in a supported form.</p>}
          <CapturedRecord value={citation.provenance} label="Captured source metadata"/>
        </div>) : <p>No source citation supplied.</p>}
        <details className="provenance-details">
          <summary>Rule version, effective dates and review history</summary>
          <CapturedRecord value={{ effective_window: trace.effective_window, rule_release: trace.rule_release }}/>
          <p className="section-note">These are the supplied review statuses. Individual reviewer events are not included in this record.</p>
        </details>
        <CapturedRecord value={trace} label="Full evaluation trace"/>
      </details>)}
      <CapturedRecord value={evaluation} label="Full rule-evaluation document"/>
    </> : <p>Rule evaluation has not returned a usable document. No calculation trace is available.</p>}
    {scenario ? <section className="architect-trace">
      <h3>Scenario assumptions and area remainder</h3>
      <p>
        {scenario.unused_draft_zoning_floor_area.scope_note}
      </p>
      <p className="architect-formula">
        {scenario.unused_draft_zoning_floor_area.formula ?? "No supported remainder formula"}
      </p>
      <CapturedRecord value={scenario.assumptions} label="All scenario assumptions"/>
      <CapturedRecord value={scenario.unused_draft_zoning_floor_area} label="Remainder inputs, result and provenance"/>
      <CapturedRecord value={scenario} label="Complete scenario record"/>
    </section> : null}
  </div>;
}
