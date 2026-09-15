import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { EvidenceInspector } from "../EvidenceInspector";
import { EvidenceRecord } from "../EvidenceRecord";
import { ReportSources } from "../ReportSources";
import { baseProfile } from "@/test-support/fixtures";
import type { PropertyProfile, SourceFact } from "@/lib/contract";
import capturedEsbFact from "../../../../../../project-control/reports/M5-T030-esb-captured-fact.json";

afterEach(cleanup);

function lotProfile() {
  const profile = baseProfile();
  profile.provenance = profile.provenance.filter(record => record.original_field_name === "lotarea");
  return profile;
}

function expectLotLinks(bbl: string) {
  const current = screen.queryByRole("link", { name: "Current PLUTO record (JSON)" });
  expect(current).not.toBeNull();
  expect(current).toHaveAttribute("href", `https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=${bbl}`);
  expect(current).toHaveAttribute("target", "_blank");
  expect(current).toHaveAttribute("rel", "noopener noreferrer");
  expect(screen.getByRole("link", { name: "About this dataset" })).toHaveAttribute("href", "https://data.cityofnewyork.us/d/64uk-42ks");
  expect(screen.getAllByRole("link")[0]).toBe(current);
  expect(screen.getByText(/may differ from .*captured evidence/i)).toBeInTheDocument();
}

describe("selected-lot PLUTO links replace the dataset-only destination", () => {
  it("fact evidence opens the lot record and keeps exact captured source facts", () => {
    const profile = lotProfile();
    const record = profile.provenance[0];
    render(<EvidenceRecord record={record} profile={profile} />);
    expectLotLinks(profile.identity.bbl);
    expect(screen.getByText("lotarea", { exact: true })).toBeInTheDocument();
    expect(screen.getByText("7577714", { exact: true })).toBeInTheDocument();
    expect(screen.getByText("7,577,714", { exact: true })).toBeInTheDocument();
    expect(screen.getByText("square feet", { exact: true })).toBeInTheDocument();
    expect(screen.getByText(record.dataset_version, { exact: true })).toBeInTheDocument();
    expect(screen.getByText(record.retrieved_at, { exact: true })).toBeInTheDocument();
  });

  it("profile sources open the selected lot while retaining captured release and retrieval date", () => {
    const profile = lotProfile();
    render(<EvidenceInspector profile={profile} selected={null} onClose={() => undefined} onEvidence={() => undefined} />);
    expectLotLinks(profile.identity.bbl);
    expect(screen.getByText(profile.reproducibility!.dataset_version!, { exact: true })).toBeInTheDocument();
    expect(screen.getByText(profile.reproducibility!.retrieved_at, { exact: true })).toBeInTheDocument();
  });

  it("the report source appendix retains exact fields and captured values beside the lot link", () => {
    const profile = lotProfile();
    render(<ReportSources profile={profile} />);
    expectLotLinks(profile.identity.bbl);
    expect(screen.getByText("lotarea", { exact: true })).toBeInTheDocument();
    expect(screen.getByRole("rowheader")).toHaveTextContent("Original: 7577714");
    expect(screen.getByRole("rowheader")).toHaveTextContent("Normalized: 7,577,714 square feet");
    expect(screen.getByText(/Captured 2026-07-16T12:00:00Z/)).toBeInTheDocument();
  });
});

const factSurfaces = [
  { name: "fact inspector", show: (profile: PropertyProfile) => render(<EvidenceRecord record={profile.provenance[0]} profile={profile} />) },
  { name: "report appendix", show: (profile: PropertyProfile) => render(<ReportSources profile={profile} />) },
];

describe.each(factSurfaces)("$name source boundaries", ({ show }) => {
  it("never links a wrong lot as the selected property's evidence", () => {
    const profile = lotProfile();
    profile.provenance[0].bbl = "3021720001";
    show(profile);
    expect(screen.queryByRole("link", { name: "Current PLUTO record (JSON)" })).toBeNull();
    expect(screen.getByRole("link", { name: "About this dataset" })).toHaveAttribute("href", "https://data.cityofnewyork.us/d/64uk-42ks");
    expect(screen.getByText("lotarea", { exact: true })).toBeInTheDocument();
  });

  it("does not borrow PLUTO metadata for a different source", () => {
    const profile = lotProfile();
    profile.provenance[0].source_id = "another-source";
    delete profile.provenance[0].dataset_id;
    show(profile);
    expect(screen.queryAllByRole("link")).toHaveLength(0);
    expect(screen.getByText(/^another-source/)).toBeVisible();
  });

  it("uses source-matched metadata when the captured fact has no dataset id", () => {
    const profile = lotProfile();
    delete profile.provenance[0].dataset_id;
    show(profile);
    expectLotLinks(profile.identity.bbl);
  });

  it("preserves a different record dataset without presenting it as a PLUTO lot", () => {
    const profile = lotProfile();
    profile.provenance[0].dataset_id = "abcd-1234";
    show(profile);
    expect(screen.queryByRole("link", { name: "Current PLUTO record (JSON)" })).toBeNull();
    expect(screen.getByRole("link", { name: "About this dataset" })).toHaveAttribute("href", "https://data.cityofnewyork.us/d/abcd-1234");
  });

  it("keeps current-record linking closed when same-source datasets conflict", () => {
    const profile = lotProfile();
    profile.reproducibility!.dataset_id = "abcd-1234";
    show(profile);
    expect(screen.queryByRole("link", { name: "Current PLUTO record (JSON)" })).toBeNull();
    expect(screen.getByRole("link", { name: "About this dataset" })).toHaveAttribute("href", "https://data.cityofnewyork.us/d/64uk-42ks");
  });
});

it.each([
  { source: "another-source", dataset: "64uk-42ks", bbl: "1000010010" },
  { source: "nyc-dcp-pluto-soda", dataset: "abcd-1234", bbl: "1000010010" },
  { source: "nyc-dcp-pluto-soda", dataset: "64uk-42ks", bbl: "1000010010\n" },
])("profile sources refuse unproven current-record context %j", ({ source, dataset, bbl }) => {
  const profile = lotProfile();
  profile.identity.bbl = bbl;
  profile.reproducibility!.source_id = source;
  profile.reproducibility!.dataset_id = dataset;
  render(<EvidenceInspector profile={profile} selected={null} onClose={() => undefined} onEvidence={() => undefined} />);
  expect(screen.queryByRole("link", { name: "Current PLUTO record (JSON)" })).toBeNull();
});

it("profile sources retain the complete captured retrieval metadata", () => {
  const profile = lotProfile();
  render(<EvidenceInspector profile={profile} selected={null} onClose={() => undefined} onEvidence={() => undefined} />);
  const raw = screen.getByText("Full captured source metadata").closest("details")!.querySelector("pre")!;
  expect(JSON.parse(raw.textContent!)).toEqual(profile.reproducibility);
});

it("changing the selected property removes a previously valid but now wrong-lot link", () => {
  const profile = lotProfile();
  const { rerender } = render(<EvidenceRecord record={profile.provenance[0]} profile={profile} />);
  expectLotLinks(profile.identity.bbl);
  const changed = { ...profile, identity: { bbl: "1008350041" } };
  rerender(<EvidenceRecord record={profile.provenance[0]} profile={changed} />);
  expect(screen.queryByRole("link", { name: "Current PLUTO record (JSON)" })).toBeNull();
});

it("renders the actual captured Empire State Building lotarea and its verified official lot URL", () => {
  // Exact live DOM capture in the task evidence; this is a component check,
  // not a claim that the changed application has already been deployed.
  const record = capturedEsbFact as SourceFact;
  const profile = lotProfile();
  profile.identity = { bbl: record.bbl };
  profile.provenance = [record];
  profile.reproducibility = undefined;
  render(<EvidenceRecord record={record} profile={profile} />);
  expectLotLinks("1008350041");
  for (const value of ["lotarea", "91351", "91,351", "square feet", "26v2", "2026-09-15T00:38:20Z"]) {
    expect(screen.getByText(value, { exact: true })).toBeInTheDocument();
  }
  const raw = screen.getByText("Full captured source record").closest("details")!.querySelector("pre")!;
  expect(JSON.parse(raw.textContent!)).toEqual(capturedEsbFact);
});
