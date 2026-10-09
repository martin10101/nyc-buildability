import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { scenarioOutcomeIsRecoverable, type ScenarioOutcome } from "@/lib/scenario-api";
import { ruleOutcomeIsRecoverable, type RuleEvaluationOutcome } from "@/lib/rule-evaluation";
import {
  enrichmentFailureNotice,
  RULE_EVALUATION_SURFACE,
  SCENARIO_SURFACE,
  type EnrichmentFailureOutcome,
  type EnrichmentSurface,
} from "../dashboard-enrichment-failure";
import { DashboardEnrichmentNotice } from "../DashboardEnrichmentNotice";

afterEach(cleanup);

// A distinctive correlation id so a test can prove it never reaches the face (plan §5a item 5).
const REF = "corr-abc-123";

// One representative outcome per documented scenario failure (src/lib/scenario-api.ts). Each is
// exactly its union member's shape, so a contract field rename fails this file. The same literals
// are re-typed as the rule-evaluation failure union below: the assignment compiles only while the
// two contracts stay structurally identical, which is why one mapper can serve both surfaces.
const SCENARIO_OUTCOMES: Record<string, Exclude<ScenarioOutcome, { kind: "scenario" }>> = {
  feature_unavailable: { kind: "feature_unavailable" },
  no_match: { kind: "no_match", bbl: "1000010010", message: "The official dataset has no record.", correlationId: REF },
  validation_error: { kind: "validation_error", code: "invalid_block", message: "Block is out of range.", correlationId: REF },
  rate_limited: { kind: "upstream_failure", state: "rate_limited", httpStatus: 429, message: "x", correlationId: REF },
  source_unavailable: { kind: "upstream_failure", state: "source_unavailable", httpStatus: 503, message: "x", correlationId: REF },
  timeout_upstream: { kind: "upstream_failure", state: "timeout", httpStatus: 504, message: "x", correlationId: REF },
  schema_drift: { kind: "upstream_failure", state: "schema_drift", httpStatus: 502, message: "x", correlationId: REF },
  internal_error: { kind: "internal_error", message: "x", correlationId: REF },
  server_contract_error: { kind: "server_contract_error", message: "x", correlationId: REF },
  validation_failure: { kind: "validation_failure", problems: ["outputs[0].value: missing"], correlationId: REF },
  network_error: { kind: "network_error", message: "The network request failed before a reply." },
  client_timeout: { kind: "client_timeout", timeoutMs: 12000 },
  unexpected_response: { kind: "unexpected_response", httpStatus: 500, receivedState: "no_match", correlationId: REF },
  aborted: { kind: "aborted" },
};
const RULE_OUTCOMES: Record<string, Exclude<RuleEvaluationOutcome, { kind: "evaluation" }>> = SCENARIO_OUTCOMES;

const SURFACES: ReadonlyArray<{
  surface: EnrichmentSurface;
  outcomes: Record<string, EnrichmentFailureOutcome>;
}> = [
  { surface: SCENARIO_SURFACE, outcomes: SCENARIO_OUTCOMES },
  { surface: RULE_EVALUATION_SURFACE, outcomes: RULE_OUTCOMES },
];

describe("enrichmentFailureNotice (plan §5a notices for the dashboard's optional enrichments)", () => {
  it("returns no notice for a superseded (aborted) request, on either surface", () => {
    expect(enrichmentFailureNotice(SCENARIO_OUTCOMES.aborted, SCENARIO_SURFACE)).toBeNull();
    expect(enrichmentFailureNotice(RULE_OUTCOMES.aborted, RULE_EVALUATION_SURFACE)).toBeNull();
  });

  it("keeps every internal code off the face and only in the technical details (§5a item 5)", () => {
    for (const { surface, outcomes } of SURFACES) {
      for (const [name, outcome] of Object.entries(outcomes)) {
        const notice = enrichmentFailureNotice(outcome, surface);
        if (!notice) continue;
        const face = `${notice.title} ${notice.body} ${notice.recovery}`;
        const codes = notice.technical.map(detail => detail.value);
        expect(face, `${surface.testId}/${name} face has no reference id`).not.toContain(REF);
        for (const code of codes) {
          expect(face, `${surface.testId}/${name} face has no code "${code}"`).not.toContain(code);
        }
        if (
          outcome.kind !== "network_error" &&
          outcome.kind !== "client_timeout" &&
          outcome.kind !== "feature_unavailable"
        ) {
          expect(codes, `${surface.testId}/${name} carries its reference id behind details`).toContain(REF);
        }
      }
    }
  });

  it("marks a scenario notice retryable exactly when scenarioOutcomeIsRecoverable does", () => {
    for (const [name, outcome] of Object.entries(SCENARIO_OUTCOMES)) {
      const notice = enrichmentFailureNotice(outcome, SCENARIO_SURFACE);
      if (!notice) continue;
      expect(notice.retryable, `scenario/${name}`).toBe(scenarioOutcomeIsRecoverable(outcome));
    }
  });

  it("marks a rule-evaluation notice retryable exactly when ruleOutcomeIsRecoverable does", () => {
    for (const [name, outcome] of Object.entries(RULE_OUTCOMES)) {
      const notice = enrichmentFailureNotice(outcome, RULE_EVALUATION_SURFACE);
      if (!notice) continue;
      expect(notice.retryable, `rule-eval/${name}`).toBe(ruleOutcomeIsRecoverable(outcome));
    }
  });

  it("names which surface failed and promises the property profile is unaffected", () => {
    const scenario = enrichmentFailureNotice(SCENARIO_OUTCOMES.internal_error, SCENARIO_SURFACE);
    const rule = enrichmentFailureNotice(RULE_OUTCOMES.internal_error, RULE_EVALUATION_SURFACE);
    expect(scenario?.title).toContain("scenario comparison");
    expect(rule?.title).toContain("draft rule evaluation");
    expect(scenario?.body).toContain("The rest of this property's facts are complete and unaffected.");
    expect(rule?.body).toContain("The rest of this property's facts are complete and unaffected.");
  });

  it("treats a disabled feature as a benign note: no Try again and no codes", () => {
    const notice = enrichmentFailureNotice(SCENARIO_OUTCOMES.feature_unavailable, SCENARIO_SURFACE);
    expect(notice?.title).toBe("Scenario comparison is not available here");
    expect(notice?.retryable).toBe(false);
    expect(notice?.technical).toHaveLength(0);
  });

  it("names the client timeout in whole seconds on the face, with no code behind it", () => {
    const notice = enrichmentFailureNotice(RULE_OUTCOMES.client_timeout, RULE_EVALUATION_SURFACE);
    expect(notice?.body).toContain("within 12 seconds");
    expect(notice?.technical).toHaveLength(0);
  });

  it("lists each client-validation problem as its own technical row", () => {
    const notice = enrichmentFailureNotice(SCENARIO_OUTCOMES.validation_failure, SCENARIO_SURFACE);
    expect(notice?.technical.filter(detail => detail.label === "Format problem")).toHaveLength(1);
  });

  it("carries only the reference row for a server-contract failure (no machine state leaks)", () => {
    const notice = enrichmentFailureNotice(RULE_OUTCOMES.server_contract_error, RULE_EVALUATION_SURFACE);
    expect(notice?.technical).toEqual([{ label: "Reference id for support", value: REF }]);
  });
});

describe("DashboardEnrichmentNotice component (plan §5a)", () => {
  it("renders a plain h2 title and body, with the codes hidden until the details are tapped", () => {
    const { container } = render(
      <DashboardEnrichmentNotice
        outcome={SCENARIO_OUTCOMES.source_unavailable}
        surface={SCENARIO_SURFACE}
        onRetry={vi.fn()}
      />,
    );
    const title = screen.getByTestId("scenario-title");
    expect(title.tagName).toBe("H2");
    expect(title).toHaveTextContent("The city data source could not be reached");
    const technical = screen.getByTestId("scenario-technical");
    expect(within(technical).getByText(REF)).toBeInTheDocument();
    expect(within(technical).getByText("503")).toBeInTheDocument();
    expect(within(technical).getByText("source_unavailable")).toBeInTheDocument();
    expect(title).not.toHaveTextContent(REF);
    expect(screen.getByTestId("scenario-body")).not.toHaveTextContent("503");
    expect(technical).not.toHaveAttribute("open");
    const codeNodes = container.querySelectorAll<HTMLElement>("p code");
    expect(codeNodes).toHaveLength(0);
  });

  it("gives each surface its own distinct testids", () => {
    render(
      <DashboardEnrichmentNotice
        outcome={RULE_OUTCOMES.network_error}
        surface={RULE_EVALUATION_SURFACE}
        onRetry={vi.fn()}
      />,
    );
    expect(screen.getByTestId("rule-eval-notice")).toBeInTheDocument();
    expect(screen.getByTestId("rule-eval-title")).toHaveTextContent("Could not reach the draft rule evaluation service");
    expect(screen.queryByTestId("scenario-notice")).not.toBeInTheDocument();
  });

  it("offers one Try again for a recoverable fault and calls back on click", () => {
    const onRetry = vi.fn();
    render(
      <DashboardEnrichmentNotice
        outcome={SCENARIO_OUTCOMES.internal_error}
        surface={SCENARIO_SURFACE}
        onRetry={onRetry}
      />,
    );
    fireEvent.click(screen.getByTestId("scenario-retry"));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("offers no Try again when retrying cannot help (feature disabled)", () => {
    render(
      <DashboardEnrichmentNotice
        outcome={RULE_OUTCOMES.feature_unavailable}
        surface={RULE_EVALUATION_SURFACE}
        onRetry={vi.fn()}
      />,
    );
    expect(screen.queryByTestId("rule-eval-retry")).not.toBeInTheDocument();
  });

  it("renders nothing for a superseded (aborted) request", () => {
    const { container } = render(
      <DashboardEnrichmentNotice
        outcome={SCENARIO_OUTCOMES.aborted}
        surface={SCENARIO_SURFACE}
        onRetry={vi.fn()}
      />,
    );
    expect(container).toBeEmptyDOMElement();
  });
});
