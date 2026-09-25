import { cleanup, fireEvent, render, screen, within, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { CondoRecordsView } from "@/lib/condo-records";
import { ParcelStudyPanel } from "../ParcelStudyPanel";
import { createParcelStudy, deriveParcelStudyScope, exportParcelStudy } from "@/lib/architect/parcel-study";

const data = vi.hoisted(() => ({ load: vi.fn(() => ({ records: [], loading: false, retry: vi.fn() })) }));
vi.mock("@/lib/architect/use-parcel-study-records", () => ({ useParcelStudyRecords: data.load }));
vi.mock("../ParcelStudyMap", () => ({ ParcelStudyMap: ({ arrangement }: { arrangement: string }) => <div>Map grouping: {arrangement}</div> }));
vi.mock("../ParcelStudyRecords", () => ({ ParcelStudyRecords: () => <div>Parcel source records</div> }));

const ENTERED = "3022647515";
const LOTS = ["3022640032", "3022640033"];
function records(lots = LOTS): CondoRecordsView {
  return {
    outcome: "multi_lot_set", enteredBbl: ENTERED, enteredLotClass: "billing", billingBbl: ENTERED,
    billingBblStatus: "recorded", baseLots: lots.map(bbl => ({ bbl, recordedZoning: null, recordedZoningStatus: "unknown" })),
    substitution: null, condoKey: null, condoNumber: null, divergentZoningNotice: null,
    recordedZoningDependency: null, reason: null, errorType: null,
    provenance: { sourceId: "test-only", datasetIds: [], retrievedAt: null, datasetVersion: null, queries: [] },
    siteDefinition: null, studyIdentityIntegrity: true,
  };
}

afterEach(() => { cleanup(); vi.clearAllMocks(); });

describe("parcel study choices stay separate from legal status and calculations", () => {
  it("offers both arrangements with undecided buildings and no numerical development allowance", () => {
    render(<ParcelStudyPanel requestedBbl={ENTERED} records={records()}/>);
    expect(screen.getByRole("radio", { name: /Compare/ })).toBeChecked();
    expect(screen.getByRole("radio", { name: "Not decided", exact: true })).toBeChecked();
    expect(screen.getByText("Not established here")).toBeVisible();
    const comparison = screen.getByRole("region", { name: "Study comparison" });
    expect(within(comparison).getAllByText("Not calculated")).toHaveLength(6);
    expect(comparison).not.toHaveTextContent(/3\.44|sq ft|approved|verified/i);
  });

  it("changes arrangement without changing building intent or legal status", () => {
    render(<ParcelStudyPanel requestedBbl={ENTERED} records={records()}/>);
    fireEvent.change(screen.getByLabelText("Existing buildings on Lot 32"), { target: { value: "retain" } });
    fireEvent.click(screen.getByRole("radio", { name: "Multiple buildings", exact: true }));
    fireEvent.click(screen.getByRole("radio", { name: /Separately/ }));
    expect(screen.getByText("2 proposed sites")).toBeVisible();
    expect(screen.queryByText("1 proposed site")).toBeNull();
    fireEvent.click(screen.getByRole("radio", { name: /Together/ }));
    expect(screen.getByText("1 proposed site")).toBeVisible();
    expect(screen.getByRole("radio", { name: "Multiple buildings", exact: true })).toBeChecked();
    expect(screen.getByLabelText("Existing buildings on Lot 32")).toHaveValue("retain");
    expect(screen.getByText("Not established here")).toBeVisible();
  });

  it("resets the draft when current parcel membership changes", () => {
    const view = render(<ParcelStudyPanel requestedBbl={ENTERED} records={records()}/>);
    fireEvent.click(screen.getByRole("radio", { name: /Together/ }));
    fireEvent.change(screen.getByLabelText("Existing buildings on Lot 32"), { target: { value: "demolish" } });
    view.rerender(<ParcelStudyPanel requestedBbl={ENTERED} records={records([LOTS[0], "3022640034"])}/>);
    expect(screen.getByRole("radio", { name: /Compare/ })).toBeChecked();
    expect(screen.getByLabelText("Existing buildings on Lot 32")).toHaveValue("undecided");
    expect(screen.queryByLabelText("Existing buildings on Lot 33")).toBeNull();
  });

  it.each(["wrong_property", "duplicate", "conflict", "partial_source", "legacy_without_integrity"])("refuses an ambiguous source scope: %s", kind => {
    const value = records(kind === "duplicate" ? [LOTS[0], LOTS[0]] : LOTS);
    if (kind === "partial_source") value.studyIdentityIntegrity = false;
    if (kind === "legacy_without_integrity") delete value.studyIdentityIntegrity;
    render(<ParcelStudyPanel requestedBbl={kind === "wrong_property" ? "1000017501" : ENTERED}
      records={value} recordsConflict={kind === "conflict"}/>);
    expect(screen.getByRole("heading", { name: "Parcel study needs matching records" })).toBeVisible();
    expect(data.load).not.toHaveBeenCalled();
  });

  it("a self-attested confirmation does not establish the legal site or unlock results", () => {
    const value = records();
    value.siteDefinition = { status: "confirmed", condoKey: null, confirmationCount: 1, parcelDiscrepancy: null,
      activeConfirmation: { recordId: "example", status: "active", confirmerName: "Example", confirmerRole: "architect",
        attestationStatus: "unauthenticated_self_attested", refusedForCalculation: true, confirmedAt: null,
        parcels: LOTS, reason: null, note: null } };
    render(<ParcelStudyPanel requestedBbl={ENTERED} records={value}/>);
    expect(screen.getByText("Not established here")).toBeVisible();
    expect(screen.getAllByText("Not calculated")).toHaveLength(6);
  });

  it("restores only choices for the current scope and rejects injected legal claims", async () => {
    render(<ParcelStudyPanel requestedBbl={ENTERED} records={records()}/>);
    const scope = deriveParcelStudyScope(records());
    expect(scope.ok).toBe(true);
    if (!scope.ok) throw new Error(scope.message);
    const draft = createParcelStudy(scope.scope);
    draft.arrangement = "separate";
    const exported = exportParcelStudy(draft, scope.scope);
    if (!exported.ok) throw new Error(exported.message);
    const input = screen.getByLabelText("Restore parcel study file");
    fireEvent.change(input, { target: { files: [{ size: exported.json.length, text: async () => exported.json }] } });
    await waitFor(() => expect(screen.getByRole("radio", { name: /Separately/ })).toBeChecked());
    const injected = JSON.stringify({ ...draft, legalStatus: "verified" });
    fireEvent.change(input, { target: { files: [{ size: injected.length, text: async () => injected }] } });
    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("Only study choices can be restored"));
    expect(screen.getByRole("radio", { name: /Separately/ })).toBeChecked();
    expect(screen.getByText("Not established here")).toBeVisible();
  });
});
