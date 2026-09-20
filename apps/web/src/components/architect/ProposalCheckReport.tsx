import {
  proposalCheckOutcomeIsRecoverable,
  type CheckResultView,
  type ProposalCheckOutcome,
} from "@/lib/proposal-checks-api";

/**
 * Grouped proposal-check report (task M5-T060). Renders the accepted route's
 * grouped PASS / FAIL / COULD_NOT_CHECK report:
 *   - status by ICON + TEXT, never colour alone (frontend rule; a11y);
 *   - a FAIL shortfall in the plan's exact phrasing "<provided> provided;
 *     <required> required; <shortfall> short" WITH units;
 *   - COULD_NOT_CHECK reasons first-class, with the non-commensurability prose
 *     (semantic_gap) behind a disclosure;
 *   - every echoed value already bounded by the client (DB-039(k)); rendered as
 *     React-escaped TEXT — no raw-HTML injection sink is used anywhere.
 *
 * Nothing here labels a proposed-derived number as a record or an allowance:
 * the honesty banner and the leading FAIL/COULD_NOT_CHECK counts keep a passing
 * subset from reading as whole-building approval (D-076-R002).
 */

function unitLabel(unit: string): string {
  switch (unit) {
    case "feet":
      return "ft";
    case "square_feet":
      return "sq ft";
    case "ratio":
      return "ratio";
    default:
      return unit;
  }
}

/** Server values are exact JSON doubles (never recomputed here), so String is
 * faithful — this never derives or rounds a value. */
function num(value: number): string {
  return String(value);
}

/** The plan's pinned FAIL phrasing (e.g. "18 ft provided; 20 ft required; 2 ft
 * short"), rendered verbatim from the server's provided/required/shortfall. */
function shortfallPhrase(r: CheckResultView): string | null {
  if (r.providedValue === null || r.requiredValue === null || r.shortfall === null) return null;
  const u = unitLabel(r.unit);
  return `${num(r.providedValue)} ${u} provided; ${num(r.requiredValue)} ${u} required; ${num(r.shortfall)} ${u} short`;
}

const OUTCOME_META: Record<string, { icon: string; text: string; className: string }> = {
  fail: { icon: "✕", text: "Fail", className: "proposal-result-fail" },
  pass: { icon: "✓", text: "Pass", className: "proposal-result-pass" },
  could_not_check: { icon: "!", text: "Could not check", className: "proposal-result-cnc" },
};

const REASON_LABELS: Record<string, string> = {
  provided_fact_absent: "The proposal provides no such value.",
  provided_fact_not_commensurate:
    "The proposed value does not establish the quantity this rule governs — matching units are not equivalence.",
  no_applicable_rule: "No rule in this family applies to the supplied lot facts.",
  allowance_unresolved:
    "An applicable rule produced no usable allowance (a required input is missing, or it needs professional review).",
  family_unsupported: "No rule for this family is implemented yet.",
  ambiguous_rule:
    "More than one rule produced an allowance; which one governs is a professional determination, not made here.",
};

function StatusBadge({ outcome }: { outcome: string }) {
  const meta = OUTCOME_META[outcome] ?? { icon: "?", text: outcome, className: "proposal-result-unknown" };
  return (
    <span className={`proposal-result-status ${meta.className}`}>
      <span aria-hidden="true">{meta.icon}</span> {meta.text}
    </span>
  );
}

function ResultRow({ r }: { r: CheckResultView }) {
  const phrase = shortfallPhrase(r);
  return (
    <li className="proposal-result" data-testid={`result-${r.checkId}`}>
      <div className="proposal-result-head">
        <StatusBadge outcome={r.outcome} />
        <span className="proposal-result-label">{r.label}</span>
      </div>
      {r.outcome === "fail" && phrase ? (
        <p className="proposal-result-shortfall" data-testid={`shortfall-${r.checkId}`}>
          {phrase}
        </p>
      ) : null}
      {r.outcome === "pass" && r.providedValue !== null && r.requiredValue !== null ? (
        <p className="proposal-result-note">
          {num(r.providedValue)} {unitLabel(r.unit)} provided; {num(r.requiredValue)} {unitLabel(r.unit)} allowed
        </p>
      ) : null}
      {r.outcome === "could_not_check" ? (
        <>
          <p className="proposal-result-reason">
            {r.couldNotCheckReason
              ? REASON_LABELS[r.couldNotCheckReason] ?? r.couldNotCheckReason
              : "This check could not be run."}
          </p>
          {r.providedValue !== null ? (
            <p className="proposal-result-note">
              Proposed value recorded: {num(r.providedValue)} {unitLabel(r.unit)} (your input, not compared).
            </p>
          ) : null}
          {r.semanticGap ? (
            <details className="proposal-result-gap">
              <summary>Why this cannot be compared</summary>
              <p>{r.semanticGap}</p>
            </details>
          ) : null}
        </>
      ) : null}
      {r.ruleId || r.coverageStatus ? (
        <p className="proposal-result-provenance">
          {r.ruleId ? `Rule ${r.ruleId}` : ""}
          {r.ruleId && r.coverageStatus ? " · " : ""}
          {r.coverageStatus ? `coverage ${r.coverageStatus}` : ""}
        </p>
      ) : null}
    </li>
  );
}

function ResultGroup({ heading, results }: { heading: string; results: CheckResultView[] }) {
  if (results.length === 0) return null;
  return (
    <section className="proposal-result-group">
      <h4>{heading}</h4>
      <ul>
        {results.map((r) => (
          <ResultRow key={r.checkId} r={r} />
        ))}
      </ul>
    </section>
  );
}

function describeFailure(outcome: ProposalCheckOutcome): string {
  switch (outcome.kind) {
    case "feature_unavailable":
      return "Proposal checking is not available in this environment.";
    case "payload_too_large":
      return outcome.message;
    case "validation_error":
      return outcome.message;
    case "internal_error":
      return outcome.message;
    case "validation_failure":
      return "The response did not match the published data contract, so nothing was rendered.";
    case "network_error":
      return outcome.message;
    case "client_timeout":
      return "The request took too long and was cancelled.";
    case "unexpected_response":
      return "The platform API returned an unexpected response.";
    default:
      return "The proposal could not be checked.";
  }
}

export function ProposalCheckReport({
  outcome,
  checking = false,
}: {
  outcome: ProposalCheckOutcome | null;
  checking?: boolean;
}) {
  if (checking) {
    return (
      <section className="card proposal-check-report" aria-busy="true">
        <p role="status">Checking the proposal against the rules…</p>
      </section>
    );
  }
  if (!outcome) {
    return (
      <section className="card proposal-check-report proposal-check-empty">
        <p className="section-note">
          Enter a proposal and run a check to see how it measures against the rules. Every value is a
          proposed value you entered — not a city record.
        </p>
      </section>
    );
  }
  if (outcome.kind === "report") {
    const { report } = outcome;
    const fails = report.results.filter((r) => r.outcome === "fail");
    const cnc = report.results.filter((r) => r.outcome === "could_not_check");
    const passes = report.results.filter((r) => r.outcome === "pass");
    return (
      <section className="card proposal-check-report" aria-label="Proposal check report">
        <p className="proposal-honesty" data-testid="report-honesty">
          Proposed — your input, not a city record. Preliminary result; professional review required.
        </p>
        <p className="proposal-check-summary" data-testid="proposal-check-summary">
          {report.summary.fail} did not meet an allowance · {report.summary.couldNotCheck} could not be
          checked · {report.summary.pass} met an allowance
        </p>
        <ResultGroup heading="Did not meet a rule allowance" results={fails} />
        <ResultGroup heading="Could not be checked" results={cnc} />
        <ResultGroup heading="Met the rule allowance" results={passes} />
        {report.unmappedLotFacts.length ? (
          <p className="section-note" data-testid="unmapped-lot-facts">
            Inputs not used by any rule: {report.unmappedLotFacts.join(", ")}
          </p>
        ) : null}
        {report.correlationId ? <p className="failure-meta">Reference: {report.correlationId}</p> : null}
      </section>
    );
  }
  const recoverable = proposalCheckOutcomeIsRecoverable(outcome);
  return (
    <section className="card failure-state proposal-check-report" role="alert" data-testid="proposal-check-failure">
      <strong>The proposal could not be checked</strong>
      <p>{describeFailure(outcome)}</p>
      {outcome.kind === "validation_error" && outcome.field ? (
        <p className="failure-meta" data-testid="validation-field">
          Field: {outcome.field}
        </p>
      ) : null}
      {recoverable ? <p className="section-note">Nothing was checked, and this is safe to retry.</p> : null}
    </section>
  );
}
