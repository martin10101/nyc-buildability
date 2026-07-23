import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { PropertyLookup } from "@/components/property/PropertyLookup";
import { RuleEvaluationFailure } from "@/components/rule-evaluation/RuleEvaluationFailure";
import { RuleEvaluationPanel } from "@/components/rule-evaluation/RuleEvaluationPanel";
import { RuleEvaluationResult } from "@/components/rule-evaluation/RuleEvaluationResult";
import { baseProfile, jsonResponse } from "@/test-support/fixtures";
import {
  draftApplicableDoc,
  missingEvidenceDoc,
  ruleConflictDoc,
  spatialUncertaintyDoc,
  unsupportedDoc,
} from "@/test-support/rule-evaluation-fixtures";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

/**
 * Task M4-T005 phase 3, component layer: the six explicit UI states, the
 * never-Verified framing, the reachable provenance drill-down, and the
 * defense-in-depth no-fetch guarantee when the surface is disabled.
 */

// --------------------------------------------------------------------------
// The five document-derived states each render distinctly, DRAFT-framed, and
// never present the result as Verified.
// --------------------------------------------------------------------------

describe("RuleEvaluationResult — the five document-derived states", () => {
  it.each<[string, () => import("@/lib/rule-evaluation-contract").RuleEvaluation, string]>([
    ["applicable_draft", draftApplicableDoc, "Draft determination"],
    ["unsupported", unsupportedDoc, "No applicable draft rule"],
    ["missing_evidence", missingEvidenceDoc, "evidence missing"],
    ["rule_conflict", ruleConflictDoc, "Conflicting draft rules"],
    ["spatial_uncertainty", spatialUncertaintyDoc, "Spatial uncertainty"],
  ])("state %s renders its own heading and DRAFT framing", (state, factory, heading) => {
    render(<RuleEvaluationResult document={factory()} />);
    const stateNode = screen.getByTestId(`rule-eval-state-${state}`);
    expect(stateNode).toHaveTextContent(heading);
    // Prominent DRAFT framing on every state.
    expect(screen.getByTestId("rule-eval-draft-banner")).toHaveTextContent(
      "DRAFT — not a final legal determination",
    );
  });

  it("never renders a Verified coverage badge, and keeps the disclaimer reachable", () => {
    const { container } = render(<RuleEvaluationResult document={draftApplicableDoc()} />);
    // Certainty is never encoded by color alone: the badge carries its exact
    // enum value; and a draft is never Verified.
    expect(container.querySelector(".status-verified")).toBeNull();
    expect(container.querySelector(".status-conditional")).not.toBeNull();
    expect(screen.getByTestId("rule-eval-result")).toHaveTextContent("conditional");
    // The exact server disclaimer (which contains the word "Verified") is
    // surfaced inside the reachable, labeled disclosure — not as a claim.
    const disclaimer = screen.getByTestId("rule-eval-disclaimer");
    expect(disclaimer).toHaveTextContent(/DRAFT - not a Verified determination/);
    expect(disclaimer.tagName.toLowerCase()).toBe("details");
  });

  it("preserves split-lot share RANGES and never collapses them to one value", () => {
    render(<RuleEvaluationResult document={spatialUncertaintyDoc()} />);
    const candidates = screen.getByTestId("rule-eval-candidates");
    // Both districts and their full [min, max] ranges are shown.
    expect(candidates).toHaveTextContent("R5");
    expect(candidates).toHaveTextContent("0.55–0.65");
    expect(candidates).toHaveTextContent("R6");
    expect(candidates).toHaveTextContent("0.35–0.45");
  });

  it("surfaces the typed rule conflict visibly (never hidden), with no value produced", () => {
    render(<RuleEvaluationResult document={ruleConflictDoc()} />);
    const conflict = screen.getByTestId("rule-eval-competing-rules");
    expect(conflict).toHaveTextContent("res-far-synth-a");
    expect(conflict).toHaveTextContent("res-far-synth-b");
    // No computed draft outputs when rules conflict.
    expect(screen.queryByTestId("rule-eval-outputs")).toBeNull();
  });

  it("exposes an evaluated-input + provenance drill-down on every state", () => {
    render(<RuleEvaluationResult document={draftApplicableDoc()} />);
    const provenance = screen.getByTestId("rule-eval-provenance");
    expect(provenance.tagName.toLowerCase()).toBe("details");
    expect(provenance).toHaveTextContent("Input fingerprint");
    // The draft rule's legal-source citation is reachable in the disclosure.
    expect(within(provenance).getByTestId("rule-eval-citations")).toHaveTextContent(
      "23-21",
    );
  });

  it("shows the draft computed outputs for an applicable draft", () => {
    render(<RuleEvaluationResult document={draftApplicableDoc()} />);
    const outputs = screen.getByTestId("rule-eval-outputs");
    expect(outputs).toHaveTextContent("max_residential_far");
    expect(outputs).toHaveTextContent("1.5");
  });
});

// --------------------------------------------------------------------------
// The sixth state — network / server failure — is recoverable and never blocks.
// --------------------------------------------------------------------------

describe("RuleEvaluationFailure — the sixth state", () => {
  it("renders a recoverable network failure with a working retry", () => {
    const onRetry = vi.fn();
    render(
      <RuleEvaluationFailure
        outcome={{ kind: "network_error", message: "could not reach the service" }}
        onRetry={onRetry}
      />,
    );
    expect(screen.getByTestId("rule-eval-state-network_error")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Retry draft evaluation" }));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("renders the benign feature-unavailable note without a retry", () => {
    render(
      <RuleEvaluationFailure outcome={{ kind: "feature_unavailable" }} onRetry={vi.fn()} />,
    );
    expect(screen.getByTestId("rule-eval-state-feature_unavailable")).toHaveTextContent(
      "not available",
    );
    expect(screen.queryByRole("button", { name: "Retry draft evaluation" })).toBeNull();
  });
});

// --------------------------------------------------------------------------
// Panel: loads independently, announces, and recovers via retry.
// --------------------------------------------------------------------------

describe("RuleEvaluationPanel — independent load + retry", () => {
  it("loads a draft result and announces it once through its own live region", async () => {
    render(
      <RuleEvaluationPanel
        bbl="1000010100"
        fetchImpl={(async () => jsonResponse(draftApplicableDoc(), 200)) as typeof fetch}
      />,
    );
    await screen.findByTestId("rule-eval-result");
    expect(screen.getByTestId("rule-eval-announcer")).toHaveTextContent(
      "Draft rule evaluation loaded",
    );
  });

  it("recovers from a server failure when Retry succeeds", async () => {
    let call = 0;
    const fetchImpl = (async () => {
      call += 1;
      return call === 1
        ? jsonResponse({ state: "internal_error", message: "boom" }, 500)
        : jsonResponse(missingEvidenceDoc(), 200);
    }) as typeof fetch;

    render(<RuleEvaluationPanel bbl="1000010100" fetchImpl={fetchImpl} />);
    await screen.findByTestId("rule-eval-state-internal_error");
    fireEvent.click(screen.getByRole("button", { name: "Retry draft evaluation" }));
    await screen.findByTestId("rule-eval-result");
    expect(call).toBe(2);
  });
});

// --------------------------------------------------------------------------
// Defense-in-depth: when the surface is disabled the panel is never mounted and
// no request to the rule-evaluation endpoint is ever issued.
// --------------------------------------------------------------------------

function stubProfileAndRuleEval(): { urls: string[] } {
  const urls: string[] = [];
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string) => {
      urls.push(url);
      return url.includes("/rule-evaluation")
        ? jsonResponse(missingEvidenceDoc(), 200)
        : jsonResponse(baseProfile(), 200);
    }),
  );
  return { urls };
}

function submitBbl(value: string) {
  fireEvent.change(screen.getByLabelText("BBL"), { target: { value } });
  fireEvent.click(screen.getByRole("button", { name: "Look up property" }));
}

describe("PropertyLookup — rule-eval surface gating (no-fetch when disabled)", () => {
  it("does NOT mount the panel or call the rule-eval endpoint when disabled", async () => {
    const { urls } = stubProfileAndRuleEval();
    render(<PropertyLookup ruleEvalEnabled={false} />);
    submitBbl("1000010010");
    await screen.findByTestId("profile-view");

    // Give any stray effect a chance to fire, then assert silence.
    await new Promise((resolve) => setTimeout(resolve, 20));
    expect(screen.queryByTestId("rule-eval-panel")).toBeNull();
    expect(urls.some((url) => url.includes("/rule-evaluation"))).toBe(false);
  });

  it("mounts the panel and calls the rule-eval endpoint exactly when enabled", async () => {
    const { urls } = stubProfileAndRuleEval();
    render(<PropertyLookup ruleEvalEnabled={true} />);
    submitBbl("1000010010");
    await screen.findByTestId("profile-view");
    await screen.findByTestId("rule-eval-panel");
    await waitFor(() =>
      expect(urls.some((url) => url.endsWith("/1000010010/rule-evaluation"))).toBe(true),
    );
  });
});
