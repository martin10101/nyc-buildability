import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import cornerLotStudy from "../../../../../../packages/contracts/fixtures/valid/study/synthetic_corner_lot_two_options.json";
import currentFact from "../../../../../../packages/contracts/fixtures/valid/site_fact/synthetic_lot_area_city_records_current.json";
import outOfDateFact from "../../../../../../packages/contracts/fixtures/valid/site_fact/synthetic_lot_area_city_records_out_of_date.json";
import versionUnknownFact from "../../../../../../packages/contracts/fixtures/valid/site_fact/synthetic_street_width_version_unknown.json";
import { validateStudyDocument } from "@/lib/study/study-validator";
import { createStudyStore } from "@/lib/study/study-store";
import { StudyStoreProvider } from "@/lib/study/use-study";
import {
  LOT_SELECTION_STATEMENT,
  MEASUREMENT_LABELS,
  VERSION_CHECK_LABELS,
  type Study,
} from "@/lib/study/study-vocabulary";
import { LotSiteSetup } from "../LotSiteSetup";
import { CROSS_BLOCK_REASON, LOT_A, LOT_B, twoLotCrossBlockStudy, twoLotOfferedStudy } from "./lot-site-fixtures";

afterEach(cleanup);

const corner = cornerLotStudy as unknown as Study;
const CORNER_BBL = corner.property.bbl; // the single-lot fixture BBL
const FIXED_NOW = () => "2026-10-02T09:00:00Z";

type StudySiteFact = Study["site"]["facts"][number];

/**
 * A contract-valid study (the corner-lot fixture) whose only site fact is one of the committed
 * version_check site_fact fixtures, deep-cloned so the shared fixture is never mutated. Used to
 * drive the data-version-status rows (D-04 slice 3).
 */
function studyWithFact(fact: unknown): Study {
  const study = structuredClone(corner);
  study.site.facts = [structuredClone(fact) as unknown as StudySiteFact];
  return study;
}

/** A study-setup document (study_read.py shape) derived from a contract-valid study fixture. */
function studySetupDoc(study: Study) {
  return {
    document_kind: "study_setup",
    bbl: study.property.bbl,
    property: study.property,
    lots: study.lots,
    lot_selection: study.lot_selection,
    site: study.site,
  };
}

function okResponse(doc: unknown): Response {
  return { status: 200, headers: { get: () => null }, json: async () => doc } as unknown as Response;
}
function notFoundResponse(): Response {
  return { status: 404, headers: { get: () => null }, json: async () => ({ detail: "off" }) } as unknown as Response;
}

describe("LotSiteSetup — lot choice + site facts with source labels (D-04, plan M1-13)", () => {
  it("builds against contract-valid studies", () => {
    expect(validateStudyDocument(cornerLotStudy).ok).toBe(true);
    expect(validateStudyDocument(twoLotCrossBlockStudy).ok).toBe(true);
    expect(validateStudyDocument(twoLotOfferedStudy).ok).toBe(true);
  });

  it("states an offered combination as the architect's selection, with no adjacency or verification claim", () => {
    render(<LotSiteSetup bbl="3001230001" study={twoLotOfferedStudy} />);
    const combination = screen.getByTestId("lot-combination");
    expect(combination).toHaveTextContent("Lots shown together");
    expect(combination).toHaveTextContent("These are the lots you selected.");
    expect(screen.queryByTestId("lot-combination-refusal")).toBeNull();
    const text = (combination.textContent ?? "").toLowerCase();
    expect(text).not.toContain("touch");
    expect(text).not.toContain("one block");
    expect(text).not.toContain("verif");
    expect(screen.getByTestId("lot-site-statement")).toHaveTextContent(LOT_SELECTION_STATEMENT);
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
    // A single lot offers no re-pick.
    expect(screen.queryByTestId("lot-site-repick")).toBeNull();

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
    // More than one lot: the use-all-or-pick control is offered.
    expect(screen.getByTestId("lot-site-repick")).toBeInTheDocument();

    const unknown = screen.getByTestId("site-fact-fact-street-width-unknown");
    expect(unknown).toHaveTextContent(MEASUREMENT_LABELS.unknown);
    expect(unknown).toHaveTextContent("Needed for: permitted envelope, building option.");
    expect(screen.getByTestId("lot-site-statement")).toHaveTextContent(LOT_SELECTION_STATEMENT);
  });

  it("reads the shared study store when no study is passed (the live path)", () => {
    const store = createStudyStore();
    store.replace({ ok: true, entry: { study: structuredClone(corner), staleOptionIds: [], parcelChoices: null } });
    render(
      <StudyStoreProvider store={store}>
        <LotSiteSetup bbl="5999999999" />
      </StudyStoreProvider>,
    );
    expect(screen.getByTestId("lot-site-setup")).toBeInTheDocument();
    expect(screen.getByText("This property has 1 lot.")).toBeInTheDocument();
  });
});

describe("LotSiteSetup — loading / error / empty states (plan §5a)", () => {
  it("shows a plain loading state, then the fetched setup", async () => {
    let resolve!: (response: Response) => void;
    const pending = new Promise<Response>((r) => {
      resolve = r;
    });
    const fetchImpl = vi.fn(async () => pending) as unknown as typeof fetch;
    render(<LotSiteSetup bbl={CORNER_BBL} fetchImpl={fetchImpl} />);
    expect(screen.getByTestId("lot-site-loading")).toBeInTheDocument();

    resolve(okResponse(studySetupDoc(corner)));
    expect(await screen.findByTestId("lot-site-setup")).toBeInTheDocument();
    expect(screen.getByText("This property has 1 lot.")).toBeInTheDocument();
  });

  it("shows the §5a failure notice with a Try again on a reachable fault", async () => {
    const fetchImpl = vi.fn(async () => {
      throw new Error("down");
    }) as unknown as typeof fetch;
    render(<LotSiteSetup bbl={CORNER_BBL} fetchImpl={fetchImpl} />);
    expect(await screen.findByTestId("lot-site-failure-notice")).toBeInTheDocument();
    expect(screen.getByTestId("lot-site-failure-title")).toHaveTextContent("Could not reach the app's service");
    expect(screen.getByTestId("lot-site-failure-retry")).toBeInTheDocument();
  });

  it("shows the plain not-connected card (no guessed numbers) when the route is off (404)", async () => {
    const fetchImpl = vi.fn(async () => notFoundResponse()) as unknown as typeof fetch;
    render(
      <StudyStoreProvider store={createStudyStore()}>
        <LotSiteSetup bbl="3001230001" study={null} fetchImpl={fetchImpl} />
      </StudyStoreProvider>,
    );
    expect(await screen.findByTestId("lot-site-unavailable")).toBeInTheDocument();
    expect(screen.getByText("Site setup is not connected yet")).toBeInTheDocument();
    expect(screen.queryByTestId("lot-site-setup")).toBeNull();
  });
});

describe("LotSiteSetup — per-fact edit records an Entered value beside the city value", () => {
  it("adds the entered value next to the kept city value (setup path)", async () => {
    const fetchImpl = vi.fn(async () => okResponse(studySetupDoc(corner))) as unknown as typeof fetch;
    render(<LotSiteSetup bbl={CORNER_BBL} fetchImpl={fetchImpl} now={FIXED_NOW} />);
    await screen.findByTestId("lot-site-setup");

    fireEvent.click(screen.getByTestId("site-fact-edit-fact-lot-area"));
    fireEvent.change(screen.getByTestId("site-fact-input-fact-lot-area"), { target: { value: "10500" } });
    fireEvent.click(screen.getByTestId("site-fact-save-fact-lot-area"));

    const entered = await screen.findByTestId("site-fact-entered-fact-lot-area");
    expect(entered).toHaveTextContent(MEASUREMENT_LABELS.entered);
    expect(entered).toHaveTextContent("10,500 sq ft");
    // The city value stays visible beside it, and no internal code is shown.
    const row = screen.getByTestId("site-fact-fact-lot-area");
    expect(row).toHaveTextContent("5,000 sq ft");
    expect(row).toHaveTextContent(MEASUREMENT_LABELS.approximate_tax_map);
    expect(row.textContent ?? "").not.toContain("architect_entry");
  });

  it("changes nothing and says why in plain words on invalid input", async () => {
    const fetchImpl = vi.fn(async () => okResponse(studySetupDoc(corner))) as unknown as typeof fetch;
    render(<LotSiteSetup bbl={CORNER_BBL} fetchImpl={fetchImpl} now={FIXED_NOW} />);
    await screen.findByTestId("lot-site-setup");

    fireEvent.click(screen.getByTestId("site-fact-edit-fact-lot-area"));
    fireEvent.change(screen.getByTestId("site-fact-input-fact-lot-area"), { target: { value: "0" } });
    fireEvent.click(screen.getByTestId("site-fact-save-fact-lot-area"));

    expect(screen.getByTestId("site-fact-error-fact-lot-area")).toHaveTextContent(
      "Enter a number greater than zero.",
    );
    expect(screen.queryByTestId("site-fact-entered-fact-lot-area")).toBeNull();
  });

  it("records the edit through the C-05 store's enterSiteFactValue when a study exists", async () => {
    const store = createStudyStore();
    store.replace({ ok: true, entry: { study: structuredClone(corner), staleOptionIds: [], parcelChoices: null } });
    render(
      <StudyStoreProvider store={store}>
        <LotSiteSetup bbl={CORNER_BBL} now={FIXED_NOW} />
      </StudyStoreProvider>,
    );
    await screen.findByTestId("lot-site-setup");

    fireEvent.click(screen.getByTestId("site-fact-edit-fact-lot-area"));
    fireEvent.change(screen.getByTestId("site-fact-input-fact-lot-area"), { target: { value: "10500" } });
    fireEvent.click(screen.getByTestId("site-fact-save-fact-lot-area"));

    const entered = await screen.findByTestId("site-fact-entered-fact-lot-area");
    expect(entered).toHaveTextContent("10,500 sq ft");
    // The shared study carries the entered fact (a city value is kept; the edit is a new fact).
    const stored = store.get(CORNER_BBL)!;
    const facts = stored.study.site.facts;
    expect(facts.find((fact) => fact.fact_id === "fact-lot-area")?.value).toBe(5000);
    expect(facts.find((fact) => fact.fact_id === "fact-lot-area-entered")?.value).toBe(10500);
  });
});

describe("LotSiteSetup — re-pick (use all or pick); the server decides the combination", () => {
  it("sends the selection as `selected`, shows the server's new result, and the web computes no adjacency", async () => {
    const oneLot: Study = {
      ...twoLotCrossBlockStudy,
      lots: [twoLotCrossBlockStudy.lots[0]],
      lot_selection: { ...twoLotCrossBlockStudy.lot_selection, combination: { status: "single_lot", reason: null } },
    };
    const fetchImpl = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      return okResponse(studySetupDoc(url.includes("selected=") ? oneLot : twoLotCrossBlockStudy));
    }) as unknown as typeof fetch;

    render(<LotSiteSetup bbl={LOT_A} fetchImpl={fetchImpl} now={FIXED_NOW} />);
    await screen.findByTestId("lot-site-setup");
    // The initial fetch is the two-lot refusal, shown verbatim.
    expect(screen.getByText("This property has 2 lots.")).toBeInTheDocument();
    expect(screen.getByTestId("lot-combination-refusal")).toHaveTextContent(CROSS_BLOCK_REASON);

    // Drop the second lot and re-pick.
    fireEvent.click(screen.getByTestId(`lot-pick-${LOT_B}`));
    fireEvent.click(screen.getByTestId("lot-repick-apply"));

    expect(await screen.findByText("This property has 1 lot.")).toBeInTheDocument();
    expect(screen.queryByTestId("lot-combination-refusal")).toBeNull();
    // The selection was sent as `selected`; the panel never re-derived a combination.
    const calls = (fetchImpl as unknown as ReturnType<typeof vi.fn>).mock.calls.map((call) => String(call[0]));
    expect(calls.some((url) => url.includes(`selected=${LOT_A}`))).toBe(true);
  });
});

describe("LotSiteSetup — each site fact's data-version status (D-04 slice 3, plan C-7 / §5a)", () => {
  it("builds against contract-valid studies carrying version_check facts", () => {
    expect(validateStudyDocument(studyWithFact(currentFact)).ok).toBe(true);
    expect(validateStudyDocument(studyWithFact(outOfDateFact)).ok).toBe(true);
    expect(validateStudyDocument(studyWithFact(versionUnknownFact)).ok).toBe(true);
  });

  it("current → label with its reason in the source details only, nothing on the face", () => {
    render(<LotSiteSetup bbl="5999999999" study={studyWithFact(currentFact)} />);
    const row = screen.getByTestId("site-fact-fact-lot-area-current");
    // The label and its reason live only in the source details disclosure.
    const detail = screen.getByTestId("site-fact-version-fact-lot-area-current");
    expect(detail).toHaveTextContent(VERSION_CHECK_LABELS.current);
    expect(detail).toHaveTextContent("is the newest published version on record");
    // A current fact shows no on-face marker.
    expect(screen.queryByTestId("site-fact-version-flag-fact-lot-area-current")).toBeNull();
    // No internal status token and no query ref on the face.
    const text = row.textContent ?? "";
    expect(text).not.toContain("out_of_date");
    expect(text).not.toContain("version_unknown");
    expect(text).not.toContain("pluto/version");
  });

  it("out_of_date → a short marker on the face, plus the label with its reason in details", () => {
    render(<LotSiteSetup bbl="5999999999" study={studyWithFact(outOfDateFact)} />);
    const row = screen.getByTestId("site-fact-fact-lot-area-out-of-date");
    const flag = screen.getByTestId("site-fact-version-flag-fact-lot-area-out-of-date");
    // The stale marker uses the vocabulary label and is visible WITHOUT opening the details.
    expect(flag).toHaveTextContent(VERSION_CHECK_LABELS.out_of_date);
    const details = row.querySelector<HTMLDetailsElement>("details.lot-site-fact__detail");
    expect(details).not.toBeNull();
    expect(details!.contains(flag)).toBe(false);
    // The details still carry the label together with the full reason.
    const detail = screen.getByTestId("site-fact-version-fact-lot-area-out-of-date");
    expect(detail).toHaveTextContent(VERSION_CHECK_LABELS.out_of_date);
    expect(detail).toHaveTextContent("a newer version, 26v2, is published");
    // No internal status token and no query ref on the face.
    const text = row.textContent ?? "";
    expect(text).not.toContain("out_of_date");
    expect(text).not.toContain("pluto/version");
  });

  it("version_unknown → label with its reason in details only, nothing on the face", () => {
    render(<LotSiteSetup bbl="5999999999" study={studyWithFact(versionUnknownFact)} />);
    const row = screen.getByTestId("site-fact-fact-street-width-version-unknown");
    const detail = screen.getByTestId("site-fact-version-fact-street-width-version-unknown");
    expect(detail).toHaveTextContent(VERSION_CHECK_LABELS.version_unknown);
    expect(detail).toHaveTextContent("has no recorded version");
    // Not out of date, so there is no on-face marker.
    expect(screen.queryByTestId("site-fact-version-flag-fact-street-width-version-unknown")).toBeNull();
    // The internal token never appears on the face (the plain reason itself may say "current").
    const text = row.textContent ?? "";
    expect(text).not.toContain("version_unknown");
    expect(text).not.toContain("out_of_date");
  });

  it("a fact with no version_check renders unchanged — no marker and no version line", () => {
    render(<LotSiteSetup bbl="5999999999" study={corner} />);
    expect(screen.queryByTestId("site-fact-version-flag-fact-lot-area")).toBeNull();
    expect(screen.queryByTestId("site-fact-version-fact-lot-area")).toBeNull();
    // The fact itself still renders as before.
    expect(screen.getByTestId("site-fact-fact-lot-area")).toHaveTextContent("5,000 sq ft");
  });
});
