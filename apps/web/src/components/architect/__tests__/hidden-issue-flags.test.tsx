import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import validFour from "../../../../../../packages/contracts/fixtures/valid/hidden_issue_flags/synthetic_four_groups.json";
import { jsonResponse } from "@/test-support/fixtures";
import { HiddenIssueFlags } from "../HiddenIssueFlags";

/**
 * The §8a hidden-issue-flags panel (queue D-12, plan M2-06 / §8a). Proves: the four
 * groups render each item once with its status label and meaning; "No flag" reads
 * as a specific check result, never a clean bill; a 404 shows the plain
 * "not connected yet" card (the route is unmounted this slice); a server failure
 * shows the shared §5a FailureNoticeCard; and no internal code reaches the face.
 */

const BBL = "5999999999";

function fourGroups() {
  return JSON.parse(JSON.stringify(validFour));
}
function stub(response: Response): typeof fetch {
  return (async () => response) as typeof fetch;
}

afterEach(cleanup);

describe("HiddenIssueFlags — success render (four §8a groups)", () => {
  it("shows the four groups, each item once, with its status label", async () => {
    render(<HiddenIssueFlags bbl={BBL} fetchImpl={stub(jsonResponse(fourGroups(), 200))} />);
    await screen.findByTestId("hidden-issues");

    expect(screen.getByTestId("hidden-issues-group-existing_building")).toBeInTheDocument();
    expect(screen.getByTestId("hidden-issues-group-zoning_lot_history")).toBeInTheDocument();
    expect(screen.getByTestId("hidden-issues-group-map_based_rules")).toBeInTheDocument();
    expect(screen.getByTestId("hidden-issues-group-site_shape_and_street")).toBeInTheDocument();

    expect(screen.getByTestId("hidden-issue-status-existing_building.larger_than_today")).toHaveTextContent("Check needed");
    expect(screen.getByTestId("hidden-issue-status-zoning_lot_history.recorded_mentions")).toHaveTextContent("Flag");
    expect(screen.getByTestId("hidden-issue-status-map_based_rules.commercial_overlay")).toHaveTextContent("Flag");
    expect(screen.getByTestId("hidden-issue-status-site_shape_and_street.through_lot")).toHaveTextContent("No flag");

    // Each item appears once.
    expect(screen.getAllByTestId(/^hidden-issue-status-/)).toHaveLength(4);
  });

  it("reads 'No flag' as this check's result, never an overall clean bill", async () => {
    render(<HiddenIssueFlags bbl={BBL} fetchImpl={stub(jsonResponse(fourGroups(), 200))} />);
    await screen.findByTestId("hidden-issues");
    const through = screen.getByTestId("hidden-issue-site_shape_and_street.through_lot");
    expect(through).toHaveTextContent("No flag");
    expect(through).toHaveTextContent("This check found nothing to flag.");
    // The panel never asserts an all-clear for the property.
    expect(screen.getByTestId("hidden-issues-strip-detail")).toHaveTextContent("not an all-clear for the property");
    const panel = screen.getByTestId("hidden-issues");
    expect((panel.textContent ?? "").toLowerCase()).not.toContain("no issues");
  });

  it("shows the one §5a strip with at most three summary items", async () => {
    render(<HiddenIssueFlags bbl={BBL} fetchImpl={stub(jsonResponse(fourGroups(), 200))} />);
    await screen.findByTestId("hidden-issues");
    const items = screen.getByTestId("hidden-issues-strip-items");
    expect(items).toHaveTextContent("2 flags");
    expect(items).toHaveTextContent("1 to check");
  });

  it("names the related site fact beside a flag that carries a fact_ref", async () => {
    render(<HiddenIssueFlags bbl={BBL} fetchImpl={stub(jsonResponse(fourGroups(), 200))} />);
    await screen.findByTestId("hidden-issues");
    expect(screen.getByTestId("hidden-issue-relation-existing_building.larger_than_today")).toHaveTextContent(
      "Relates to: existing zoning floor area.",
    );
  });

  it("puts no internal code on the face (item_id, raw fact_ref, source tokens stay off)", async () => {
    render(<HiddenIssueFlags bbl={BBL} fetchImpl={stub(jsonResponse(fourGroups(), 200))} />);
    await screen.findByTestId("hidden-issues");
    const panel = screen.getByTestId("hidden-issues").cloneNode(true) as HTMLElement;
    // The face excludes the <details> disclosures (strip notes + per-flag "Source"),
    // which are §5a item-4 "details", not the results face.
    panel.querySelectorAll("details").forEach((node) => node.remove());
    const face = panel.textContent ?? "";
    expect(face).not.toContain("_");
    expect(face).not.toContain("://");
    expect(face).not.toContain("existing_building.larger_than_today");
    expect(face).not.toContain("5999999999:existing_zoning_floor_area");
    expect(face).not.toContain("city_dataset");
  });
});

describe("HiddenIssueFlags — unmounted route and failures (§5a)", () => {
  it("shows the plain 'not connected yet' card on a 404 (route unmounted this slice)", async () => {
    render(<HiddenIssueFlags bbl={BBL} fetchImpl={stub(jsonResponse({ detail: "off" }, 404))} />);
    const card = await screen.findByTestId("hidden-issues-unavailable");
    expect(card).toHaveTextContent("not connected yet");
    expect(card).toHaveTextContent("Nothing is guessed");
    expect(screen.queryByTestId("hidden-issues")).toBeNull();
  });

  it("shows the shared §5a failure card for a server failure, codes behind details", async () => {
    render(
      <HiddenIssueFlags
        bbl={BBL}
        fetchImpl={stub(jsonResponse({ state: "inputs_unavailable", message: "not available right now" }, 503))}
      />,
    );
    const notice = await screen.findByTestId("hidden-issues-failure-notice");
    expect(screen.getByTestId("hidden-issues-failure-title")).toHaveTextContent(
      "The hidden-issue checks are not available right now",
    );
    // Retryable -> a Try again control; no raw code on the plain face.
    expect(screen.getByTestId("hidden-issues-failure-retry")).toBeInTheDocument();
    const technical = within(notice).queryByTestId("hidden-issues-failure-technical");
    // The reference id (a code) lives behind the Technical details disclosure, not the face.
    if (technical) expect(technical.tagName.toLowerCase()).toBe("details");
    expect(screen.queryByTestId("hidden-issues")).toBeNull();
  });
});
