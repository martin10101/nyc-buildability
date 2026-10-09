import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import type { PropertyProfile } from "@/lib/contract";
import type { ParcelStudyRecord } from "@/lib/architect/use-parcel-study-records";
import { baseProfile } from "@/test-support/fixtures";
import { ParcelStudyRecords } from "../ParcelStudyRecords";

afterEach(cleanup);
const BBL = "3022640032";

/** Synthetic presentation fixture only; these are not Wallabout findings. */
function recordedProfile(): PropertyProfile {
  const profile = baseProfile();
  profile.identity.bbl = BBL;
  profile.provenance = profile.provenance.map(record => ({ ...record, bbl: BBL }));
  profile.provenance = profile.provenance.filter(record => record.original_field_name !== "residfar");
  profile.provenance.push({
    provenance_id: "test-residfar", source_id: "nyc-dcp-pluto-soda", original_field_name: "residfar",
    original_value: "3.44", normalized_value: 3.44, retrieved_at: "2026-09-25T12:00:00Z",
    dataset_version: "test-only", effective_date: null, bbl: BBL, confidence: 1,
    user_confirmed_or_overridden: "none", conflict_status: "none",
  });
  profile.lot_facts = {
    lotarea: { value: 5405, units: "sq ft", provenance_ref: "test-area" },
    lotfront: { value: 54.5, units: "ft", provenance_ref: "test-front" },
    lotdepth: { value: 100, units: "ft", provenance_ref: "test-depth" },
  };
  profile.zoning.districts = ["R7-1"];
  profile.conflicts = [];
  profile.missing_inputs = [];
  profile.reproducibility = {
    correlation_id: "test-records", source_id: "nyc-dcp-pluto-soda", dataset_id: "64uk-42ks",
    dataset_version: "test-only", request_url: "https://data.cityofnewyork.us/resource/64uk-42ks.json",
    retrieved_at: "2026-09-25T12:00:00Z", record_count: 1, drift_signals: [], connector_notes: [],
    coverage_policy: "test only", staleness: { stale: true, served_from_cache: true },
  };
  return profile;
}

function record(profile = recordedProfile()): ParcelStudyRecord {
  return {
    bbl: BBL, profileOutcome: { kind: "profile", profile, correlationId: "test" },
    outlineOutcome: { kind: "route_absent", httpStatus: 404 }, loading: false,
  };
}

describe("ParcelStudyRecords: source references never become allowances", () => {
  it("labels recorded dimensions, zoning, and FAR while keeping source evidence expandable", () => {
    const { container } = render(<ParcelStudyRecords records={[record()]} />);
    const facts = container.querySelector(".parcel-study-facts") as HTMLElement;
    expect(within(facts).getByText("5,405 sq ft")).toBeInTheDocument();
    expect(within(facts).getByText("54.5 ft")).toBeInTheDocument();
    expect(within(facts).getByText("100 ft")).toBeInTheDocument();
    expect(within(facts).getByText("Zoning · city record")).toBeInTheDocument();
    expect(within(facts).getByText("Residential FAR · PLUTO reference")).toBeInTheDocument();
    expect(within(facts).getByText("3.44")).toBeInTheDocument();
    expect(screen.getByText(/not buildable dimensions or development allowances/)).toBeInTheDocument();
    expect(screen.getByText("Stale source")).toBeInTheDocument();
    const sources = screen.getByText("Sources and record limits").closest("details");
    expect(sources).not.toHaveAttribute("open");
    expect(sources).toHaveTextContent("2026-09-25T12:00:00Z");
    expect(screen.getByText("Existing building information").closest("details")).not.toHaveAttribute("open");
    expect(screen.queryByText("18,593.2")).not.toBeInTheDocument();
  });

  it("retains source conflicts and suppresses a conflicting FAR reference", () => {
    const profile = recordedProfile();
    profile.conflicts = [{ field: "residfar", resolution: "unresolved", values: [
      { source_id: "source-a", value: 3.44 }, { source_id: "source-b", value: 4 },
    ] }];
    const { container } = render(<ParcelStudyRecords records={[record(profile)]} />);
    const facts = container.querySelector(".parcel-study-facts") as HTMLElement;
    expect(within(facts).getByText("Conflicting records")).toBeInTheDocument();
    expect(within(facts).queryByText("3.44")).not.toBeInTheDocument();
    expect(screen.getByText("Source conflicts")).toBeInTheDocument();
    expect(screen.getByText("Source conflicts (1)").closest("details")).toHaveTextContent("source-b: 4");
  });

  it("keeps absent facts unknown rather than fabricating dimensions or zoning", () => {
    const profile = recordedProfile();
    profile.lot_facts = {};
    profile.zoning.districts = [];
    profile.provenance = [];
    const { container } = render(<ParcelStudyRecords records={[record(profile)]} />);
    const facts = container.querySelector(".parcel-study-facts") as HTMLElement;
    expect(within(facts).getAllByText("Unknown")).toHaveLength(5);
    expect(facts).not.toHaveTextContent("R7-1");
    expect(facts).not.toHaveTextContent("0 ft");
  });

  it("does not render source values from a wrong-BBL profile even if passed directly", () => {
    const profile = recordedProfile();
    profile.identity.bbl = "3022640033";
    render(<ParcelStudyRecords records={[record(profile)]} />);
    expect(screen.getByText("Property identity mismatch")).toBeInTheDocument();
    expect(screen.queryByText("5,405 sq ft")).not.toBeInTheDocument();
    expect(screen.queryByText("R7-1")).not.toBeInTheDocument();
  });
});
