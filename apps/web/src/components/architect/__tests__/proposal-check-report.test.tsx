import { afterEach, describe, expect, it } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import { fetchProposalCheck, type CheckResultView, type ProposalCheckOutcome } from "@/lib/proposal-checks-api";
import { rectangleSampleDraft, toProposalCheckRequest } from "@/lib/architect/proposal-draft";
import {
  attestedReportBody,
  checkResponse,
  markupEchoReportBody,
  stubFetch,
} from "@/test-support/proposal-check-fixtures";
import { ProposalCheckReport } from "../ProposalCheckReport";

/**
 * Task M5-T060, report renderer: the AS-1 rectangle arithmetic in the plan's
 * pinned shortfall phrasing, status by icon+text (never colour alone),
 * COULD_NOT_CHECK reasons first-class with semantic_gap behind a disclosure,
 * echoed markup rendered as TEXT (DB-039(k)), and typed failure surfaces.
 */

const REQUEST = toProposalCheckRequest(rectangleSampleDraft());
async function reportOutcome(body: unknown): Promise<ProposalCheckOutcome> {
  return fetchProposalCheck(REQUEST, { fetchImpl: stubFetch(checkResponse(body, 200)) });
}

describe("ProposalCheckReport", () => {
  it("renders the AS-1 rectangle arithmetic with the plan-pinned shortfall phrasing", async () => {
    const outcome = await reportOutcome(attestedReportBody());
    render(<ProposalCheckReport outcome={outcome} />);
    expect(screen.getByTestId("report-honesty")).toHaveTextContent("not a city record");
    expect(screen.getByTestId("proposal-check-summary")).toHaveTextContent("1 did not meet an allowance");
    expect(screen.getByTestId("shortfall-lot_coverage_ratio")).toHaveTextContent(
      "0.625 ratio provided; 0.5 ratio required; 0.125 ratio short",
    );
    const height = screen.getByTestId("result-building_height");
    expect(height).toHaveTextContent("Pass");
    expect(height).toHaveTextContent("30");
    expect(height).toHaveTextContent("60");
  });

  it("shows BOTH COULD_NOT_CHECK reasons first-class, each with its own non-commensurability prose behind a closed disclosure", async () => {
    const outcome = await reportOutcome(attestedReportBody());
    render(<ProposalCheckReport outcome={outcome} />);

    // The summary counts exactly the two could-not-check results asserted below.
    expect(screen.getByTestId("proposal-check-summary")).toHaveTextContent("2 could not be");

    // CNC #1 — rear yard: reason first-class, its own semantic gap behind a closed disclosure.
    const rear = screen.getByTestId("result-rear_yard_depth");
    expect(rear).toHaveTextContent("Could not check");
    expect(rear).toHaveTextContent("matching units are not equivalence");
    const rearGap = rear.querySelector<HTMLDetailsElement>("details.proposal-result-gap");
    expect(rearGap).not.toBeNull();
    expect(rearGap!.open).toBe(false);
    expect(rearGap!).toHaveTextContent("not a rear-yard depth");

    // CNC #2 — residential FAR: the second reason first-class, its own distinct closed disclosure.
    const far = screen.getByTestId("result-residential_far_floor_area");
    expect(far).toHaveTextContent("Could not check");
    expect(far).toHaveTextContent("matching units are not equivalence");
    const farGap = far.querySelector<HTMLDetailsElement>("details.proposal-result-gap");
    expect(farGap).not.toBeNull();
    expect(farGap!.open).toBe(false);
    expect(farGap!).toHaveTextContent("not a residential zoning floor area");
  });

  it("renders echoed markup as TEXT with no injected element (DB-039(k))", async () => {
    const outcome = await reportOutcome(markupEchoReportBody());
    const { container } = render(<ProposalCheckReport outcome={outcome} />);
    expect(screen.getByTestId("unmapped-lot-facts")).toHaveTextContent("<img src=x onerror=alert(1)>");
    expect(container.querySelector("img")).toBeNull();
    expect(container.querySelector("script")).toBeNull();
  });

  it("shows a typed validation failure with the refused field and no retry note (a result, not a fault)", () => {
    render(
      <ProposalCheckReport
        outcome={{ kind: "validation_error", field: "scenario_label", message: "refused at the boundary", correlationId: "c" }}
      />,
    );
    expect(screen.getByTestId("proposal-check-failure")).toHaveTextContent("refused at the boundary");
    expect(screen.getByTestId("validation-field")).toHaveTextContent("scenario_label");
    expect(screen.queryByText("Nothing was checked, and this is safe to retry.")).toBeNull();
  });

  it("offers a retry note for a recoverable network failure", () => {
    render(<ProposalCheckReport outcome={{ kind: "network_error", message: "service unreachable" }} />);
    expect(screen.getByTestId("proposal-check-failure")).toHaveTextContent("service unreachable");
    expect(screen.getByText("Nothing was checked, and this is safe to retry.")).toBeInTheDocument();
  });
});

/**
 * AS-1 arithmetic — SEPARATE coverage, deliberately decoupled from the
 * transport/fixture pass-through above (which only echoes the transcribed
 * rectangle constants). Two independent pins:
 *   (a) the plan's shortfall PHRASING is COMPOSED for values that are NOT the
 *       rectangle fixture (a minimum check, feet, 18/20/2) — proving the phrase
 *       is generated by shortfallPhrase, not copied from one fixture; and
 *   (b) the rectangle fixture's own numbers are ARITHMETICALLY self-consistent:
 *       the coverage shortfall IS provided - required (0.625 - 0.5 = 0.125), not
 *       an arbitrary constant, and the height PASS is a true inequality
 *       (30 <= 60, 30 ft of headroom). These relations are exact IEEE-754
 *       (eighths and integers), so no epsilon is used.
 */
const RESULT_DEFAULTS: CheckResultView = {
  checkId: "synthetic",
  family: "synthetic",
  label: "synthetic check",
  unit: "feet",
  direction: "minimum",
  outcome: "fail",
  providedValue: null,
  requiredValue: null,
  shortfall: null,
  couldNotCheckReason: null,
  detail: "",
  semanticGap: null,
  ruleId: null,
  coverageStatus: null,
  providedInputIds: [],
};
function resultView(overrides: Partial<CheckResultView>): CheckResultView {
  return { ...RESULT_DEFAULTS, ...overrides };
}
function syntheticReportOutcome(results: CheckResultView[]): ProposalCheckOutcome {
  return {
    kind: "report",
    correlationId: null,
    report: {
      scenarioLabel: "synthetic",
      proposalId: null,
      sourceClass: "proposed",
      outlineDigest: "",
      results,
      summary: {
        pass: results.filter((r) => r.outcome === "pass").length,
        fail: results.filter((r) => r.outcome === "fail").length,
        couldNotCheck: results.filter((r) => r.outcome === "could_not_check").length,
        total: results.length,
      },
      unmappedLotFacts: [],
      correlationId: null,
    },
  };
}

describe("AS-1 arithmetic — separate coverage (phrasing composition + fixture self-consistency)", () => {
  it("composes the plan's shortfall phrasing for a non-fixture minimum check (18 ft / 20 ft / 2 ft short)", () => {
    const outcome = syntheticReportOutcome([
      resultView({
        checkId: "synthetic_min_setback",
        label: "synthetic minimum setback",
        unit: "feet",
        direction: "minimum",
        outcome: "fail",
        providedValue: 18,
        requiredValue: 20,
        shortfall: 2,
      }),
    ]);
    render(<ProposalCheckReport outcome={outcome} />);
    expect(screen.getByTestId("shortfall-synthetic_min_setback")).toHaveTextContent(
      "18 ft provided; 20 ft required; 2 ft short",
    );
  });

  it("pins the rectangle fixture numbers as arithmetically self-consistent (0.625 - 0.5 = 0.125; 30 <= 60)", async () => {
    const outcome = await reportOutcome(attestedReportBody());
    expect(outcome.kind).toBe("report");
    if (outcome.kind !== "report") return;

    const cov = outcome.report.results.find((r) => r.checkId === "lot_coverage_ratio");
    expect(cov).toBeDefined();
    expect(cov!.providedValue).not.toBeNull();
    expect(cov!.requiredValue).not.toBeNull();
    expect(cov!.shortfall).not.toBeNull();
    // The transcribed shortfall IS provided - required (exact eighths), never a bare constant.
    expect(cov!.providedValue! - cov!.requiredValue!).toBe(cov!.shortfall!);
    expect(cov!.shortfall).toBe(0.125);

    const height = outcome.report.results.find((r) => r.checkId === "building_height");
    expect(height).toBeDefined();
    expect(height!.outcome).toBe("pass");
    // A true PASS inequality: provided within the maximum allowance, 30 ft of headroom.
    expect(height!.providedValue! <= height!.requiredValue!).toBe(true);
    expect(height!.requiredValue! - height!.providedValue!).toBe(30);
  });
});

afterEach(cleanup);
