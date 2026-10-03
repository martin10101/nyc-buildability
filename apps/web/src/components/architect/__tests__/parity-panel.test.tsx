import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import realDof from "../../../../../../packages/contracts/fixtures/valid/parity_data/real_dof_bayside.json";
import { NOT_CONFIRMED_LABEL, NOT_CONFIRMED_REASON, type ParityData } from "@/lib/parity-api";
import { parityUiEnabled } from "@/lib/architect/parity-panel-ui-flag";
import { parityFaceBudget } from "@/lib/architect/parity-panel-view";
import { ParityPanel } from "../ParityPanel";

/**
 * The parity panel — "Comparable sales & floor area" (queue D-15, plan §11b, B-11).
 * Proves: flag off by default and no fetch when off; recorded sales render with
 * their source and date; the disclosed filter is shown verbatim; excluded rows and
 * reasons sit behind a "details" disclosure; the not-a-valuation notice is present;
 * the unused-floor-area block is the owner-settled wording with NO digit; no
 * internal code reaches the face; a 404 shows the plain "not connected yet" card;
 * and a server failure shows the shared §5a FailureNoticeCard.
 */

const BBL = "4073340070";

function parity(): unknown {
  // Deep-clone so a test can never mutate the shared fixture module.
  return JSON.parse(JSON.stringify(realDof));
}

/** A JSON Response with a correct Content-Length — the parity adapter fail-closes
 * (unexpected_response) on an absent/blank length BEFORE it parses. */
function parityResponse(body: unknown, status: number, correlationId: string | null = "test-correlation-id"): Response {
  const text = JSON.stringify(body);
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "Content-Length": String(new TextEncoder().encode(text).length),
  };
  if (correlationId !== null) headers["X-Correlation-ID"] = correlationId;
  return new Response(text, { status, headers });
}
function stub(response: Response): typeof fetch {
  return (async () => response) as typeof fetch;
}

afterEach(cleanup);

describe("ParityPanel — flag gate (no fetch when off)", () => {
  it("renders nothing and never fetches when the flag is off by default", () => {
    const spy = vi.fn(async () => parityResponse(parity(), 200));
    const enabled = parityUiEnabled({}); // default-off server gate (D-15)
    // Mirrors the parent gate in DashboardTools: the panel mounts only when enabled.
    render(enabled ? <ParityPanel bbl={BBL} fetchImpl={spy as unknown as typeof fetch} /> : <div data-testid="parity-off" />);
    expect(enabled).toBe(false);
    expect(spy).not.toHaveBeenCalled();
    expect(screen.queryByTestId("parity-panel")).toBeNull();
    expect(screen.getByTestId("parity-off")).toBeInTheDocument();
  });
});

describe("ParityPanel — success render (comparable sales + unused floor area)", () => {
  it("shows the loading card before the fetch resolves", () => {
    const stuck = (() => new Promise<Response>(() => {})) as unknown as typeof fetch;
    render(<ParityPanel bbl={BBL} fetchImpl={stuck} />);
    expect(screen.getByTestId("parity-loading")).toBeInTheDocument();
  });

  it("renders each recorded sale with its recorded price, date and source", async () => {
    render(<ParityPanel bbl={BBL} fetchImpl={stub(parityResponse(parity(), 200))} />);
    await screen.findByTestId("parity-panel");

    const first = screen.getByTestId("parity-sale-0");
    expect(first).toHaveTextContent("45-30 BELL BOULEVARD");
    expect(first).toHaveTextContent("Recorded sale price: $3,700,000");
    expect(first).toHaveTextContent("Sale date: 2025-11-20");

    // The DOF provenance is disclosed behind the "Source" details (§5a item 4).
    const source = screen.getByTestId("parity-source");
    expect(source.tagName.toLowerCase()).toBe("details");
    expect(source).toHaveTextContent("DOF");
    expect(source).toHaveTextContent("2026-10-02T11:00:00Z");
  });

  it("shows the disclosed selection filter verbatim (an open owner question, B-11)", async () => {
    const data = parity() as { comparable_sales: { criteria_text: string } };
    render(<ParityPanel bbl={BBL} fetchImpl={stub(parityResponse(parity(), 200))} />);
    await screen.findByTestId("parity-panel");
    expect(screen.getByTestId("parity-criteria")).toHaveTextContent(data.comparable_sales.criteria_text);
  });

  it("shows the not-a-valuation notice", async () => {
    render(<ParityPanel bbl={BBL} fetchImpl={stub(parityResponse(parity(), 200))} />);
    await screen.findByTestId("parity-panel");
    expect(screen.getByTestId("parity-not-a-valuation")).toHaveTextContent(
      "not a valuation or an appraisal",
    );
  });

  it("puts excluded rows and their reasons behind a details disclosure", async () => {
    render(<ParityPanel bbl={BBL} fetchImpl={stub(parityResponse(parity(), 200))} />);
    await screen.findByTestId("parity-panel");
    const excluded = screen.getByTestId("parity-excluded");
    expect(excluded.tagName.toLowerCase()).toBe("details");
    expect(excluded).toHaveTextContent("not a market sale"); // zero_price_transfer -> plain words
    expect(within(excluded).getByText("201-07 NORTHERN BOULEVARD")).toBeInTheDocument();
  });

  it("shows the unused-floor-area block as the owner-settled wording with no digit", async () => {
    render(<ParityPanel bbl={BBL} fetchImpl={stub(parityResponse(parity(), 200))} />);
    await screen.findByTestId("parity-panel");
    const block = screen.getByTestId("parity-unused");
    expect(screen.getByTestId("parity-unused-label")).toHaveTextContent(NOT_CONFIRMED_LABEL);
    expect(screen.getByTestId("parity-unused-reason")).toHaveTextContent(NOT_CONFIRMED_REASON);
    expect(/[0-9]/.test(block.textContent ?? "")).toBe(false);
  });

  it("carries no app chatter on a populated face (R082 §5a budget helper)", async () => {
    render(<ParityPanel bbl={BBL} fetchImpl={stub(parityResponse(parity(), 200))} />);
    await screen.findByTestId("parity-panel");
    const budget = parityFaceBudget(parity() as ParityData);
    expect(budget.appStrings).toEqual([]); // recorded sales present -> no empty-state line
    expect(budget.noticeCount).toBeLessThanOrEqual(3);
    // The pinned not-a-valuation notice and settled capacity block are the standing
    // blocks, both rendered verbatim on the face.
    expect(screen.getByTestId("parity-not-a-valuation")).toHaveTextContent("not a valuation or an appraisal");
    expect(screen.getByTestId("parity-unused-label")).toHaveTextContent(NOT_CONFIRMED_LABEL);
  });

  it("puts no internal code on the face (bbl, source tokens, contract keys stay off)", async () => {
    render(<ParityPanel bbl={BBL} fetchImpl={stub(parityResponse(parity(), 200))} />);
    await screen.findByTestId("parity-panel");
    const panel = screen.getByTestId("parity-panel").cloneNode(true) as HTMLElement;
    // The face excludes the <details> disclosures (strip detail, excluded, source),
    // which are §5a item-4 "details", not the results face.
    panel.querySelectorAll<HTMLElement>("details").forEach((node) => node.remove());
    const face = panel.textContent ?? "";
    expect(face).not.toContain("_");
    expect(face).not.toContain("://");
    expect(face).not.toContain("4073340070"); // subject bbl
    expect(face).not.toContain("4073140027"); // a sale's bbl
    expect(face).not.toContain("nyc-dof-annualized-sales-soda"); // source_id
    expect(face).not.toContain("zero_price_transfer"); // raw exclusion token
    expect(face).not.toContain("city_dataset");
  });
});

describe("ParityPanel — unmounted route and failures (§5a)", () => {
  it("shows the plain 'not connected yet' card on a 404 (route not mounted this slice)", async () => {
    render(<ParityPanel bbl={BBL} fetchImpl={stub(parityResponse({ detail: "Not Found" }, 404, null))} />);
    const card = await screen.findByTestId("parity-unavailable");
    expect(card).toHaveTextContent("not connected yet");
    expect(card).toHaveTextContent("nothing to show here");
    expect(screen.queryByTestId("parity-panel")).toBeNull();
  });

  it("shows the shared §5a failure card for a server failure, codes behind details", async () => {
    render(
      <ParityPanel
        bbl={BBL}
        fetchImpl={stub(parityResponse({ state: "inputs_unavailable", message: "not available right now" }, 503))}
      />,
    );
    const notice = await screen.findByTestId("parity-failure-notice");
    expect(screen.getByTestId("parity-failure-title")).toHaveTextContent(
      "Comparable sales and floor area are not available right now",
    );
    expect(screen.getByTestId("parity-failure-retry")).toBeInTheDocument();
    const technical = within(notice).queryByTestId("parity-failure-technical");
    if (technical) expect(technical.tagName.toLowerCase()).toBe("details");
    expect(screen.queryByTestId("parity-panel")).toBeNull();
  });
});
