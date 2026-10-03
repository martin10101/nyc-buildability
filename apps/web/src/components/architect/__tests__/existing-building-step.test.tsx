import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import existingZfaUnknownStudy from "../../../../../../packages/contracts/fixtures/valid/study/synthetic_copied_from_export_existing_zfa_unknown.json";
import assumedExistingZfaFact from "../../../../../../packages/contracts/fixtures/valid/site_fact/synthetic_existing_zoning_floor_area_assumed.json";
import { createStudyStore } from "@/lib/study/study-store";
import { StudyStoreProvider } from "@/lib/study/use-study";
import { MEASUREMENT_LABELS, type SiteFact, type Study } from "@/lib/study/study-vocabulary";
import {
  CHOOSE_SOURCE_REASON,
  existingFloorAreaAssumptionStatement,
} from "@/lib/architect/existing-building-view";
import { ENTER_POSITIVE_NUMBER } from "@/lib/architect/lot-site-setup";
import { ExistingBuildingStep } from "../ExistingBuildingStep";
import { LotSiteSetup } from "../LotSiteSetup";

afterEach(cleanup);

const unknownStudy = existingZfaUnknownStudy as unknown as Study;
const BBL = unknownStudy.property.bbl; // "5999999998", plan "keep", existing-zfa unknown
const unknownFacts = unknownStudy.site.facts;
const assumedFact = assumedExistingZfaFact as unknown as SiteFact;
const FIXED_NOW = () => "2026-10-03T09:00:00Z";

/**
 * A valid study with NO existing-zfa fact (so the first-creation edge runs: buildExistingFloorAreaFact
 * + upsertSiteFact) and a CITY value parked at the exact id that edge would write. The store never
 * overwrites a city value in place, so the write fails — the honest path behind the fallback message.
 */
function studyThatRefusesTheFirstCreation(): Study {
  const study = structuredClone(unknownStudy);
  study.site.facts = study.site.facts
    .filter((fact) => fact.key !== "existing_zoning_floor_area")
    .map((fact) =>
      fact.fact_id === "fact-zoning-district" ? { ...fact, fact_id: "existing-zoning-floor-area" } : fact,
    );
  return study;
}

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

describe("ExistingBuildingStep — the three-way choice (plan §3 step 4)", () => {
  it("shows no floor-area input and an honest note when nothing is chosen (no silent keep/remove)", () => {
    render(<ExistingBuildingStep plan={null} onChoosePlan={vi.fn()} facts={unknownFacts} onRecordFloorArea={vi.fn()} />);
    expect(screen.getByTestId("existing-building-unchosen")).toBeInTheDocument();
    expect(screen.queryByTestId("existing-floor-area")).toBeNull();
    for (const option of screen.getAllByRole<HTMLInputElement>("radio")) expect(option.checked).toBe(false);
  });

  it("writes the chosen plan through the callback", () => {
    const onChoosePlan = vi.fn();
    render(<ExistingBuildingStep plan={null} onChoosePlan={onChoosePlan} facts={unknownFacts} onRecordFloorArea={vi.fn()} />);
    fireEvent.click(screen.getByRole("radio", { name: "Keep the existing building" }));
    expect(onChoosePlan).toHaveBeenCalledWith("keep");
  });

  it("hides the floor-area input for remove and for no existing building", () => {
    const { rerender } = render(
      <ExistingBuildingStep plan="remove" onChoosePlan={vi.fn()} facts={unknownFacts} onRecordFloorArea={vi.fn()} />,
    );
    expect(screen.queryByTestId("existing-floor-area")).toBeNull();
    rerender(
      <ExistingBuildingStep plan="no_existing_building" onChoosePlan={vi.fn()} facts={unknownFacts} onRecordFloorArea={vi.fn()} />,
    );
    expect(screen.queryByTestId("existing-floor-area")).toBeNull();
  });
});

describe("ExistingBuildingStep — keep: the existing zoning floor area", () => {
  it("shows Unknown — enter and what it blocks when none is established", () => {
    render(<ExistingBuildingStep plan="keep" onChoosePlan={vi.fn()} facts={unknownFacts} onRecordFloorArea={vi.fn()} />);
    const block = screen.getByTestId("existing-floor-area");
    expect(block).toHaveTextContent(MEASUREMENT_LABELS.unknown);
    expect(block).toHaveTextContent("Needed for: remaining capacity, keep / rebuild comparison.");
    expect(screen.getByTestId("existing-floor-area-input")).toBeInTheDocument();
  });

  it("records a value with the architect's explicit source choice (never a city source)", () => {
    const onRecordFloorArea = vi.fn(() => null);
    render(<ExistingBuildingStep plan="keep" onChoosePlan={vi.fn()} facts={unknownFacts} onRecordFloorArea={onRecordFloorArea} />);
    fireEvent.change(screen.getByTestId("existing-floor-area-input"), { target: { value: "6200" } });
    fireEvent.click(screen.getByRole("radio", { name: "Stated assumption" }));
    fireEvent.click(screen.getByTestId("existing-floor-area-save"));
    expect(onRecordFloorArea).toHaveBeenCalledWith(6200, "assumption");
  });

  it("rejects a non-positive value with the validator's message and records nothing", () => {
    const onRecordFloorArea = vi.fn(() => null);
    render(<ExistingBuildingStep plan="keep" onChoosePlan={vi.fn()} facts={unknownFacts} onRecordFloorArea={onRecordFloorArea} />);
    fireEvent.change(screen.getByTestId("existing-floor-area-input"), { target: { value: "0" } });
    fireEvent.click(screen.getByRole("radio", { name: "Architect entry" }));
    fireEvent.click(screen.getByTestId("existing-floor-area-save"));
    expect(screen.getByTestId("existing-floor-area-error")).toHaveTextContent(ENTER_POSITIVE_NUMBER);
    expect(onRecordFloorArea).not.toHaveBeenCalled();
  });

  it("requires an explicit source choice before recording a value", () => {
    const onRecordFloorArea = vi.fn(() => null);
    render(<ExistingBuildingStep plan="keep" onChoosePlan={vi.fn()} facts={unknownFacts} onRecordFloorArea={onRecordFloorArea} />);
    fireEvent.change(screen.getByTestId("existing-floor-area-input"), { target: { value: "6200" } });
    fireEvent.click(screen.getByTestId("existing-floor-area-save"));
    expect(screen.getByTestId("existing-floor-area-error")).toHaveTextContent(CHOOSE_SOURCE_REASON);
    expect(onRecordFloorArea).not.toHaveBeenCalled();
  });

  it("shows an established value with its source and no input until the architect changes it", () => {
    render(<ExistingBuildingStep plan="keep" onChoosePlan={vi.fn()} facts={[assumedFact]} onRecordFloorArea={vi.fn()} />);
    expect(screen.getByTestId("existing-floor-area-value")).toHaveTextContent("6,200 sq ft");
    expect(screen.getByTestId("existing-floor-area-source-label")).toHaveTextContent(MEASUREMENT_LABELS.assumed);
    expect(screen.queryByTestId("existing-floor-area-input")).toBeNull();
    fireEvent.click(screen.getByTestId("existing-floor-area-change"));
    expect(screen.getByTestId("existing-floor-area-input")).toBeInTheDocument();
  });

  it("shows no internal codes on the face", () => {
    const { container } = render(
      <ExistingBuildingStep plan="keep" onChoosePlan={vi.fn()} facts={unknownFacts} onRecordFloorArea={vi.fn()} />,
    );
    const text = container.textContent ?? "";
    for (const token of [
      "no_existing_building",
      "architect_entry",
      "existing_zoning_floor_area",
      "remaining_floor_area",
      "existing_building_paths",
      "fact-existing",
      "fact_id",
    ]) {
      expect(text).not.toContain(token);
    }
  });
});

describe("LotSiteSetup — step 4 wired to the store (a study exists)", () => {
  function renderWithStore() {
    const store = createStudyStore();
    store.replace({ ok: true, entry: { study: structuredClone(unknownStudy), staleOptionIds: [], parcelChoices: null } });
    render(
      <StudyStoreProvider store={store}>
        <LotSiteSetup bbl={BBL} now={FIXED_NOW} />
      </StudyStoreProvider>,
    );
    return store;
  }

  it("shows the plan from the selected option and keeps the existing-zfa out of the step-3 facts", () => {
    renderWithStore();
    expect(screen.getByTestId("existing-building-step")).toBeInTheDocument();
    expect(screen.getByRole<HTMLInputElement>("radio", { name: "Keep the existing building" }).checked).toBe(true);
    // The existing zoning floor area is step 4, not step 3.
    expect(screen.queryByTestId("site-fact-fact-existing-zfa")).toBeNull();
    expect(screen.getByTestId("existing-floor-area")).toBeInTheDocument();
  });

  it("records a stated assumption into the shared study (rank Assumed, source assumption)", async () => {
    const store = renderWithStore();
    fireEvent.change(screen.getByTestId("existing-floor-area-input"), { target: { value: "6200" } });
    fireEvent.click(screen.getByRole("radio", { name: "Stated assumption" }));
    fireEvent.click(screen.getByTestId("existing-floor-area-save"));

    // Recorded through the real store op (enterSiteFactAssumption), no study-operations mocking.
    await waitFor(() => {
      const fact = store.get(BBL)?.study.site.facts.find((candidate) => candidate.fact_id === "fact-existing-zfa");
      expect(fact).toBeDefined();
      expect(fact?.measurement.rank).toBe("assumed");
      expect(fact?.measurement.label).toBe(MEASUREMENT_LABELS.assumed);
      expect(fact?.value).toBe(6200);
      expect(fact?.source?.kind).toBe("assumption");
      expect(fact?.source?.statement).toBe(existingFloorAreaAssumptionStatement(6200));
    });
  });

  it("records an architect entry into the shared study (rank Entered, source architect_entry)", async () => {
    const store = renderWithStore();
    fireEvent.change(screen.getByTestId("existing-floor-area-input"), { target: { value: "6200" } });
    fireEvent.click(screen.getByRole("radio", { name: "Architect entry" }));
    fireEvent.click(screen.getByTestId("existing-floor-area-save"));

    // Recorded through the real store op (enterSiteFactValue), no study-operations mocking.
    await waitFor(() => {
      const fact = store.get(BBL)?.study.site.facts.find((candidate) => candidate.fact_id === "fact-existing-zfa");
      expect(fact).toBeDefined();
      expect(fact?.measurement.rank).toBe("entered");
      expect(fact?.measurement.label).toBe(MEASUREMENT_LABELS.entered);
      expect(fact?.value).toBe(6200);
      expect(fact?.source?.kind).toBe("architect_entry");
      expect(fact?.source?.statement).toBeNull();
    });
  });

  it("writes a plan change to the selected option and hides the floor-area input", async () => {
    const store = renderWithStore();
    fireEvent.click(screen.getByRole("radio", { name: "Remove the existing building" }));
    await waitFor(() => {
      expect(store.get(BBL)!.study.options[0].existing_building_plan).toBe("remove");
    });
    expect(screen.queryByTestId("existing-floor-area")).toBeNull();
  });

  it("surfaces the fallback message and records nothing when the store refuses the write", async () => {
    // A real store + real ops (no study-operations mocking): the op genuinely fails because the
    // store will not overwrite a city value in place, and the UI shows the unchanged fallback.
    const store = createStudyStore();
    store.replace({
      ok: true,
      entry: { study: studyThatRefusesTheFirstCreation(), staleOptionIds: [], parcelChoices: null },
    });
    render(
      <StudyStoreProvider store={store}>
        <LotSiteSetup bbl={BBL} now={FIXED_NOW} />
      </StudyStoreProvider>,
    );

    // Plan "keep" with no existing-zfa fact shows the first-creation entry form.
    fireEvent.change(screen.getByTestId("existing-floor-area-input"), { target: { value: "6200" } });
    fireEvent.click(screen.getByRole("radio", { name: "Architect entry" }));
    fireEvent.click(screen.getByTestId("existing-floor-area-save"));

    expect(await screen.findByTestId("existing-floor-area-error")).toHaveTextContent(
      "That value could not be recorded.",
    );
    const facts = store.get(BBL)?.study.site.facts ?? [];
    expect(facts.some((fact) => fact.key === "existing_zoning_floor_area")).toBe(false);
  });
});

describe("LotSiteSetup — step 4 over a fetched setup (no study/option yet — the flag-on path)", () => {
  it("chooses keep, enters a stated assumption, then hides the input for no existing building", async () => {
    const fetchImpl = vi.fn(async () => okResponse(studySetupDoc(unknownStudy))) as unknown as typeof fetch;
    render(<LotSiteSetup bbl={BBL} fetchImpl={fetchImpl} now={FIXED_NOW} />);
    await screen.findByTestId("lot-site-setup");

    // Nothing chosen yet: the honest note shows and there is no floor-area input.
    expect(screen.getByTestId("existing-building-unchosen")).toBeInTheDocument();
    expect(screen.queryByTestId("existing-floor-area")).toBeNull();

    // Keep → Unknown — enter.
    fireEvent.click(screen.getByRole("radio", { name: "Keep the existing building" }));
    expect(screen.getByTestId("existing-floor-area")).toHaveTextContent(MEASUREMENT_LABELS.unknown);

    // Enter a value as a stated assumption → listed with that source label.
    fireEvent.change(screen.getByTestId("existing-floor-area-input"), { target: { value: "6200" } });
    fireEvent.click(screen.getByRole("radio", { name: "Stated assumption" }));
    fireEvent.click(screen.getByTestId("existing-floor-area-save"));
    expect(await screen.findByTestId("existing-floor-area-value")).toHaveTextContent("6,200 sq ft");
    expect(screen.getByTestId("existing-floor-area-source-label")).toHaveTextContent(MEASUREMENT_LABELS.assumed);

    // No existing building → the floor-area input is gone.
    fireEvent.click(screen.getByRole("radio", { name: "No existing building" }));
    expect(screen.queryByTestId("existing-floor-area")).toBeNull();
  });

  it("does not compute or show remaining development capacity", async () => {
    const fetchImpl = vi.fn(async () => okResponse(studySetupDoc(unknownStudy))) as unknown as typeof fetch;
    const { container } = render(<LotSiteSetup bbl={BBL} fetchImpl={fetchImpl} now={FIXED_NOW} />);
    await screen.findByTestId("lot-site-setup");
    fireEvent.click(screen.getByRole("radio", { name: "Keep the existing building" }));
    expect(container.textContent ?? "").not.toContain("Remaining development capacity");
  });
});
