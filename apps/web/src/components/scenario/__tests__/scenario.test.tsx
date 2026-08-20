import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { PropertyLookup } from "@/components/property/PropertyLookup";
import { ScenarioFailure } from "@/components/scenario/ScenarioFailure";
import { ScenarioPanel } from "@/components/scenario/ScenarioPanel";
import { ScenarioResult } from "@/components/scenario/ScenarioResult";
import type { Scenario } from "@/lib/scenario-contract";
import { baseProfile, jsonResponse } from "@/test-support/fixtures";
import preliminaryFixture from "../../../../../../packages/contracts/fixtures/valid/scenario/preliminary_r5_cap.json";
import unsupportedFixture from "../../../../../../packages/contracts/fixtures/valid/scenario/unsupported_family.json";
import conflictFixture from "../../../../../../packages/contracts/fixtures/valid/scenario/no_scenario_conflict.json";
import professionalReviewFixture from "../../../../../../packages/contracts/fixtures/valid/scenario/no_scenario_professional_review.json";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

/**
 * Task M5-T002, component layer: the honest scenario states, the never-Verified
 * framing, the draft cap surfaced VERBATIM with its draft-cap label, the
 * reachable provenance / coverage-map drill-downs, and the recoverable failure
 * state. The scenario documents are the committed canonical M5-T001 fixtures.
 */

function clone(doc: unknown): Scenario {
  return structuredClone(doc) as unknown as Scenario;
}

const preliminaryDoc = () => clone(preliminaryFixture);
const unsupportedDoc = () => clone(unsupportedFixture);
const conflictDoc = () => clone(conflictFixture);
const professionalReviewDoc = () => clone(professionalReviewFixture);

// --------------------------------------------------------------------------
// The document-derived states each render distinctly, DRAFT-framed, never Verified.
// --------------------------------------------------------------------------

describe("ScenarioResult — the honest scenario states", () => {
  it.each<[string, () => Scenario, string]>([
    ["preliminary_cap", preliminaryDoc, "Preliminary draft scenario"],
    ["unsupported", unsupportedDoc, "No applicable draft rule"],
    ["conflict", conflictDoc, "Conflicting draft rules"],
    ["professional_review", professionalReviewDoc, "Professional review required"],
  ])("state %s renders its own heading and DRAFT framing", (state, factory, heading) => {
    render(<ScenarioResult document={factory()} />);
    expect(screen.getByTestId(`scenario-state-${state}`)).toHaveTextContent(heading);
    expect(screen.getByTestId("scenario-draft-banner")).toHaveTextContent(
      "DRAFT — not a final legal determination and not a buildable envelope",
    );
  });

  it("surfaces the draft cap VERBATIM with its draft-cap label (never recomputed)", () => {
    render(<ScenarioResult document={preliminaryDoc()} />);
    const cap = screen.getByTestId("scenario-cap");
    // 15000 from the fixture, digit-grouped for display only.
    expect(within(cap).getByTestId("scenario-cap-value")).toHaveTextContent("15,000");
    expect(within(cap).getByTestId("scenario-cap-label")).toHaveTextContent(
      "DRAFT maximum residential ZONING-FLOOR-AREA CAP",
    );
  });

  it("never renders a Verified coverage badge and keeps the disclaimer reachable", () => {
    const { container } = render(<ScenarioResult document={preliminaryDoc()} />);
    expect(container.querySelector(".status-verified")).toBeNull();
    expect(container.querySelector(".status-conditional")).not.toBeNull();
    expect(screen.getByTestId("scenario-result")).toHaveTextContent("conditional");
    const disclaimer = screen.getByTestId("scenario-disclaimer");
    expect(disclaimer).toHaveTextContent(/not a Verified determination/);
    expect(disclaimer.tagName.toLowerCase()).toBe("details");
  });

  it("exposes the cap provenance / legal-source citation on the preliminary state", () => {
    render(<ScenarioResult document={preliminaryDoc()} />);
    const provenance = screen.getByTestId("scenario-provenance");
    expect(provenance.tagName.toLowerCase()).toBe("details");
    expect(within(provenance).getByTestId("scenario-citations")).toHaveTextContent("23-21");
  });

  it("shows the rule-coverage map so the cap is never mistaken for an envelope", () => {
    render(<ScenarioResult document={preliminaryDoc()} />);
    const map = screen.getByTestId("scenario-coverage-matrix");
    expect(map).toHaveTextContent("height_limit");
    expect(map).toHaveTextContent("blocks a buildable envelope");
  });

  it("surfaces no cap value on a no-scenario family (never invented)", () => {
    render(<ScenarioResult document={conflictDoc()} />);
    expect(screen.queryByTestId("scenario-cap")).toBeNull();
    expect(screen.getByTestId("scenario-reasons")).toBeInTheDocument();
  });
});

// --------------------------------------------------------------------------
// Failure states — recoverable and never blocking.
// --------------------------------------------------------------------------

describe("ScenarioFailure", () => {
  it("renders a recoverable network failure with a working retry", () => {
    const onRetry = vi.fn();
    render(
      <ScenarioFailure
        outcome={{ kind: "network_error", message: "could not reach the service" }}
        onRetry={onRetry}
      />,
    );
    expect(screen.getByTestId("scenario-state-network_error")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Retry draft scenario" }));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("renders the benign feature-unavailable note without a retry", () => {
    render(<ScenarioFailure outcome={{ kind: "feature_unavailable" }} onRetry={vi.fn()} />);
    expect(screen.getByTestId("scenario-state-feature_unavailable")).toHaveTextContent(
      "not available",
    );
    expect(screen.queryByRole("button", { name: "Retry draft scenario" })).toBeNull();
  });
});

// --------------------------------------------------------------------------
// Panel: loads independently, announces, and recovers via retry.
// --------------------------------------------------------------------------

describe("ScenarioPanel — independent load + retry", () => {
  it("loads a draft scenario and announces it once through its own live region", async () => {
    render(
      <ScenarioPanel
        bbl="1000010100"
        fetchImpl={(async () => jsonResponse(preliminaryDoc(), 200)) as typeof fetch}
      />,
    );
    await screen.findByTestId("scenario-result");
    expect(screen.getByTestId("scenario-announcer")).toHaveTextContent("Draft scenario loaded");
  });

  it("recovers from a server failure when Retry succeeds", async () => {
    let call = 0;
    const fetchImpl = (async () => {
      call += 1;
      return call === 1
        ? jsonResponse({ state: "internal_error", message: "boom" }, 500)
        : jsonResponse(professionalReviewDoc(), 200);
    }) as typeof fetch;

    render(<ScenarioPanel bbl="1000010100" fetchImpl={fetchImpl} />);
    await screen.findByTestId("scenario-state-internal_error");
    fireEvent.click(screen.getByRole("button", { name: "Retry draft scenario" }));
    await screen.findByTestId("scenario-result");
    expect(call).toBe(2);
  });

  it("shows the benign feature-unavailable note when the server flag is off", async () => {
    render(
      <ScenarioPanel
        bbl="1000010100"
        fetchImpl={(async () => jsonResponse({ detail: "Not Found" }, 404)) as typeof fetch}
      />,
    );
    await screen.findByTestId("scenario-state-feature_unavailable");
  });
});

// --------------------------------------------------------------------------
// Defense-in-depth at the property-screen integration point (M5-T002 wiring):
// when the surface is disabled the panel is never mounted and no request to the
// scenario endpoint is ever issued (mirrors the rule-eval gating test).
// --------------------------------------------------------------------------

function stubProfileAndScenario(): { urls: string[] } {
  const urls: string[] = [];
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string) => {
      urls.push(url);
      return url.includes("/scenario")
        ? jsonResponse(preliminaryDoc(), 200)
        : jsonResponse(baseProfile(), 200);
    }),
  );
  return { urls };
}

function submitBbl(value: string) {
  fireEvent.change(screen.getByLabelText("BBL"), { target: { value } });
  fireEvent.click(screen.getByRole("button", { name: "Look up property" }));
}

describe("PropertyLookup — scenario surface gating (no-fetch when disabled)", () => {
  it("does NOT mount the scenario panel or call the endpoint when disabled", async () => {
    const { urls } = stubProfileAndScenario();
    render(<PropertyLookup scenarioEnabled={false} />);
    submitBbl("1000010010");
    await screen.findByTestId("profile-view");

    await new Promise((resolve) => setTimeout(resolve, 20));
    expect(screen.queryByTestId("scenario-panel")).toBeNull();
    expect(urls.some((url) => url.includes("/scenario"))).toBe(false);
  });

  it("mounts the panel and calls the scenario endpoint exactly when enabled", async () => {
    const { urls } = stubProfileAndScenario();
    render(<PropertyLookup scenarioEnabled={true} />);
    submitBbl("1000010010");
    await screen.findByTestId("profile-view");
    await screen.findByTestId("scenario-panel");
    await waitFor(() =>
      expect(urls.some((url) => url.endsWith("/1000010010/scenario"))).toBe(true),
    );
  });
});
