import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

/**
 * The "Transit and parking zone" section of the parity window (queue D-15 slice 2,
 * plan §5a / §11b, B-10, check C-8). The lane C adapter's HTTP classification is
 * proven by src/lib/__tests__/transit-parking-api.test.ts and the real wiring by
 * parity-panel.test.tsx; this suite drives each §5a STATE the section renders, given
 * the adapter's typed outcomes:
 *   - a recorded 200 renders the plain headline, zone, verbatim detail and the Source
 *     disclosure, with no internal code on the results face;
 *   - a check_needed 200 reads the missing zone as "Not available — <reason>";
 *   - a 404 shows the plain "not connected yet" card;
 *   - a server failure shows the shared §5a FailureNoticeCard;
 *   - loading shows the loading card; a superseded (aborted) request renders nothing.
 * The typed outcomes are built from the COMMITTED contract fixtures (contract-validated
 * through the real adapter), so the rendered values ARE the recorded contract shape.
 */

const { fetchMock } = vi.hoisted(() => ({ fetchMock: vi.fn() }));
vi.mock("@/lib/transit-parking-api", async (importActual) => {
  const actual = await importActual<typeof import("@/lib/transit-parking-api")>();
  return { ...actual, fetchTransitParking: fetchMock };
});

import {
  validateTransitParkingDocument,
  type TransitParking,
  type TransitParkingFetchOutcome,
} from "@/lib/transit-parking-api";
import { TransitParkingSection } from "../TransitParkingSection";

const FIXTURE_ROOT = resolve(
  process.cwd(),
  "../../packages/contracts/fixtures/valid/transit_parking",
);
const BBL = "4073340070";

function status(name: string): TransitParking {
  const body = JSON.parse(readFileSync(resolve(FIXTURE_ROOT, `${name}.json`), "utf8"));
  const result = validateTransitParkingDocument(body);
  if (!result.ok) throw new Error(`fixture ${name} invalid: ${result.problems.join("; ")}`);
  return result.status;
}

function resolveWith(outcome: TransitParkingFetchOutcome) {
  fetchMock.mockResolvedValue(outcome);
}

beforeEach(() => fetchMock.mockReset());
afterEach(cleanup);

describe("TransitParkingSection — recorded 200", () => {
  it("renders the plain headline, zone and verbatim detail; provenance behind Source", async () => {
    const recorded = status("synthetic_recorded");
    resolveWith({ kind: "status", status: recorded, correlationId: "cid" });
    render(<TransitParkingSection bbl={BBL} />);

    const section = await screen.findByTestId("transit-parking");
    expect(screen.getByTestId("transit-parking-headline")).toHaveTextContent("Recorded");
    expect(screen.getByTestId("transit-parking-zone")).toHaveTextContent("Outer Transit Zone");
    expect(screen.getByTestId("transit-parking-detail")).toHaveTextContent(recorded.detail);
    expect(screen.queryByTestId("transit-parking-missing")).toBeNull();

    const source = screen.getByTestId("transit-parking-source");
    expect(source.tagName.toLowerCase()).toBe("details");
    expect(source).toHaveTextContent("26v2"); // dataset version, only inside the disclosure
    expect(within(section).getByText("Source")).toBeInTheDocument();
  });

  it("keeps internal codes off the results face (request url, version, raw tokens, bbl)", async () => {
    resolveWith({ kind: "status", status: status("synthetic_recorded"), correlationId: "cid" });
    render(<TransitParkingSection bbl={BBL} />);
    const section = (await screen.findByTestId("transit-parking")).cloneNode(true) as HTMLElement;
    // The "Source" disclosure is §5a item-4 "details", not the results face.
    section.querySelectorAll<HTMLElement>("details").forEach((node) => node.remove());
    const face = section.textContent ?? "";
    expect(face).not.toContain("://"); // the request url (query_ref) stays in Source
    expect(face).not.toContain("26v2"); // the dataset version stays in Source
    expect(face).not.toContain("_"); // no snake_case token (status / source.kind)
    expect(face).not.toContain("check_needed");
    expect(face).not.toContain("city_dataset");
    expect(face).not.toContain("5999999999"); // the lot bbl is never shown
    // The plain status label IS shown; the raw enum token is not the displayed value.
    expect(face).toContain("Recorded");
  });
});

describe("TransitParkingSection — check_needed 200", () => {
  it("reads a missing zone as 'Not available — <reason>' with no zone line", async () => {
    const checkNeeded = status("synthetic_check_needed");
    resolveWith({ kind: "status", status: checkNeeded, correlationId: "cid" });
    render(<TransitParkingSection bbl={BBL} />);

    await screen.findByTestId("transit-parking");
    expect(screen.getByTestId("transit-parking-headline")).toHaveTextContent("Check needed");
    expect(screen.queryByTestId("transit-parking-zone")).toBeNull();
    const missing = screen.getByTestId("transit-parking-missing");
    expect(missing).toHaveTextContent("Not available —");
    expect(missing).toHaveTextContent(checkNeeded.missing_source ?? "");
  });
});

describe("TransitParkingSection — §5a non-success states", () => {
  it("shows the plain 'not connected yet' card on a 404", async () => {
    resolveWith({ kind: "not_available" });
    render(<TransitParkingSection bbl={BBL} />);
    const card = await screen.findByTestId("transit-parking-unavailable");
    expect(card).toHaveTextContent("not connected yet");
    expect(screen.queryByTestId("transit-parking")).toBeNull();
  });

  it("shows the shared §5a failure card for a server failure, codes behind details", async () => {
    resolveWith({
      kind: "inputs_unavailable",
      message: "not available right now",
      correlationId: "cid",
    });
    render(<TransitParkingSection bbl={BBL} />);
    const notice = await screen.findByTestId("transit-parking-failure-notice");
    expect(screen.getByTestId("transit-parking-failure-title")).toHaveTextContent(
      "The transit and parking zone is not available right now",
    );
    expect(screen.getByTestId("transit-parking-failure-retry")).toBeInTheDocument();
    const technical = within(notice).queryByTestId("transit-parking-failure-technical");
    if (technical) expect(technical.tagName.toLowerCase()).toBe("details");
    expect(screen.queryByTestId("transit-parking")).toBeNull();
  });

  it("shows the loading card before the fetch resolves", async () => {
    // Hold the resolver so the loading state is observable, then settle and flush it
    // before the test ends — nothing is left pending on the mocked module.
    let settle: (outcome: TransitParkingFetchOutcome) => void = () => {};
    fetchMock.mockReturnValue(
      new Promise<TransitParkingFetchOutcome>((resolve) => {
        settle = resolve;
      }),
    );
    const { unmount } = render(<TransitParkingSection bbl={BBL} />);
    expect(screen.getByTestId("transit-parking-loading")).toBeInTheDocument();

    settle({ kind: "aborted" }); // resolve to a superseded request -> section collapses to nothing
    await waitFor(() => expect(screen.queryByTestId("transit-parking-loading")).toBeNull());
    unmount();
  });

  it("renders nothing for a superseded (aborted) request", async () => {
    resolveWith({ kind: "aborted" });
    const { container } = render(<TransitParkingSection bbl={BBL} />);
    // The loading card shows first, then the aborted outcome collapses the section to
    // nothing: a superseded request owns no surface.
    await waitFor(() =>
      expect(container.querySelector('[data-testid^="transit-parking"]')).toBeNull(),
    );
    expect(screen.queryByTestId("transit-parking")).toBeNull();
    expect(screen.queryByTestId("transit-parking-unavailable")).toBeNull();
    expect(screen.queryByTestId("transit-parking-failure-notice")).toBeNull();
  });
});
