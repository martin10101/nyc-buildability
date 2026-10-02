import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import cornerLotStudy from "../../../../../../packages/contracts/fixtures/valid/study/synthetic_corner_lot_two_options.json";
import { validateStudyDocument } from "@/lib/study/study-validator";
import { createStudyStore } from "@/lib/study/study-store";
import { StudyStoreProvider } from "@/lib/study/use-study";
import { LOT_SELECTION_STATEMENT, MEASUREMENT_LABELS, type Study } from "@/lib/study/study-vocabulary";
import { LotSiteSetup } from "../LotSiteSetup";
import { CROSS_BLOCK_REASON, twoLotCrossBlockStudy } from "./lot-site-fixtures";

afterEach(cleanup);

const corner = cornerLotStudy as unknown as Study;

describe("LotSiteSetup — lot choice + site facts with source labels (D-04, plan M1-13)", () => {
  it("builds against contract-valid studies", () => {
    expect(validateStudyDocument(cornerLotStudy).ok).toBe(true);
    expect(validateStudyDocument(twoLotCrossBlockStudy).ok).toBe(true);
  });

  it("shows one lot with its source, every site fact with its source, and no refusal (Pilot A)", () => {
    render(<LotSiteSetup bbl="5999999999" study={corner} />);
    expect(screen.getByTestId("lot-site-setup")).toBeInTheDocument();
    expect(screen.getByText("This property has 1 lot.")).toBeInTheDocument();
    expect(screen.getByText("The site is this one lot.")).toBeInTheDocument();

    const lot = screen.getByTestId("lot-row-5999999999");
    expect(lot).toHaveTextContent("Lot 9999");
    expect(lot).toHaveTextContent("5,000 sq ft");
    expect(lot).toHaveTextContent(MEASUREMENT_LABELS.approximate_tax_map);
    expect(lot).toHaveTextContent("In the site");

    expect(screen.getByTestId("lot-combination")).toHaveTextContent("One lot");
    expect(screen.queryByTestId("lot-combination-refusal")).toBeNull();

    expect(screen.getByTestId("site-fact-fact-lot-area")).toHaveTextContent("5,000 sq ft");
    expect(screen.getByTestId("site-fact-fact-lot-area")).toHaveTextContent(MEASUREMENT_LABELS.approximate_tax_map);
    expect(screen.getByTestId("site-fact-fact-lot-type")).toHaveTextContent("Corner");
    expect(screen.getByTestId("site-fact-fact-lot-type")).toHaveTextContent(MEASUREMENT_LABELS.city_records);
    expect(screen.getByTestId("site-fact-fact-zoning-district")).toHaveTextContent("R6B");
  });

  it("always carries the owner's zoning-lot statement", () => {
    render(<LotSiteSetup bbl="5999999999" study={corner} />);
    expect(screen.getByTestId("lot-site-statement")).toHaveTextContent(LOT_SELECTION_STATEMENT);
  });

  it("refuses a cross-block combination and shows B-07's reason verbatim", () => {
    render(<LotSiteSetup bbl="3001230001" study={twoLotCrossBlockStudy} />);
    expect(screen.getByText("This property has 2 lots.")).toBeInTheDocument();

    const refusal = screen.getByTestId("lot-combination-refusal");
    expect(refusal).toHaveTextContent("These lots were not combined");
    expect(refusal).toHaveTextContent(CROSS_BLOCK_REASON);

    expect(screen.getByTestId("lot-row-3001230001")).toHaveTextContent("Lot 1");
    expect(screen.getByTestId("lot-row-3004560070")).toHaveTextContent("Lot 70");

    const unknown = screen.getByTestId("site-fact-fact-street-width-unknown");
    expect(unknown).toHaveTextContent(MEASUREMENT_LABELS.unknown);
    expect(unknown).toHaveTextContent("Needed for: permitted envelope, building option.");
    expect(screen.getByTestId("lot-site-statement")).toHaveTextContent(LOT_SELECTION_STATEMENT);
  });

  it("reads the shared study store when no study is passed (the live path)", () => {
    const store = createStudyStore();
    store.replace({ ok: true, entry: { study: corner, staleOptionIds: [], parcelChoices: null } });
    render(
      <StudyStoreProvider store={store}>
        <LotSiteSetup bbl="5999999999" />
      </StudyStoreProvider>,
    );
    expect(screen.getByTestId("lot-site-setup")).toBeInTheDocument();
    expect(screen.getByText("This property has 1 lot.")).toBeInTheDocument();
  });

  it("shows a plain not-connected card and no guessed numbers when no study exists", () => {
    render(
      <StudyStoreProvider store={createStudyStore()}>
        <LotSiteSetup bbl="3001230001" study={null} />
      </StudyStoreProvider>,
    );
    expect(screen.getByTestId("lot-site-unavailable")).toBeInTheDocument();
    expect(screen.getByText("Site setup is not connected yet")).toBeInTheDocument();
    expect(screen.queryByTestId("lot-site-setup")).toBeNull();
  });
});
