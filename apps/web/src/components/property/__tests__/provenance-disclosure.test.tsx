import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, it } from "vitest";
import { ProvenanceDisclosure } from "../ProvenanceDisclosure";
import { baseProfile } from "@/test-support/fixtures";

afterEach(cleanup);

it("legacy evidence opens its captured lot's current PLUTO record and keeps the dataset secondary", () => {
  const profile = baseProfile();
  const record = profile.provenance.find(item => item.original_field_name === "lotarea")!;
  render(<ProvenanceDisclosure records={[record]} reproducibility={profile.reproducibility} label="Source for Lot area" />);
  fireEvent.click(screen.getByText("Source for Lot area"));
  const current = screen.queryByRole("link", { name: "Current PLUTO record (JSON)" });
  expect(current).not.toBeNull();
  expect(current).toHaveAttribute("href", `https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=${record.bbl}`);
  expect(current).toHaveAttribute("target", "_blank");
  expect(current).toHaveAttribute("rel", "noopener noreferrer");
  expect(screen.getByRole("link", { name: /About this dataset/ })).toHaveAttribute("href", "https://data.cityofnewyork.us/d/64uk-42ks");
  expect(screen.getAllByRole("link")[0]).toBe(current);
  expect(screen.getByText(/may differ from .*captured evidence/i)).toBeInTheDocument();
  for (const value of ["lotarea", "7577714", "7,577,714", "square feet", record.dataset_version, record.retrieved_at]) {
    expect(screen.getByText(value, { exact: true })).toBeInTheDocument();
  }
});

it("legacy evidence does not inherit another source's PLUTO dataset", () => {
  const profile = baseProfile();
  const record = { ...profile.provenance[0], source_id: "another-source" };
  delete record.dataset_id;
  render(<ProvenanceDisclosure records={[record]} reproducibility={profile.reproducibility} label="Source" />);
  fireEvent.click(screen.getByText("Source", { selector: "summary" }));
  expect(screen.queryAllByRole("link")).toHaveLength(0);
  expect(screen.getByText("another-source", { exact: true })).toBeInTheDocument();
});

it.each(["1000010010\n", "1000010010\r\n", "1000010010&bbl=3021720001", "javascript:alert(1)"])("legacy evidence refuses malformed captured BBL %j", bbl => {
  const profile = baseProfile();
  const record = { ...profile.provenance[0], bbl };
  render(<ProvenanceDisclosure records={[record]} reproducibility={profile.reproducibility} label="Source" />);
  fireEvent.click(screen.getByText("Source", { selector: "summary" }));
  expect(screen.queryByRole("link", { name: "Current PLUTO record (JSON)" })).toBeNull();
  expect(screen.getByRole("link", { name: /About this dataset/ })).toHaveAttribute("href", "https://data.cityofnewyork.us/d/64uk-42ks");
});

it("legacy evidence refuses a conflicting dataset and preserves exact captured review metadata", () => {
  const profile = baseProfile();
  const record = { ...profile.provenance[0], conflict_status: "conflicting" as const, user_confirmed_or_overridden: "overridden" as const, request_url: "javascript:alert(1)" };
  profile.reproducibility!.dataset_id = "abcd-1234";
  render(<ProvenanceDisclosure records={[record]} reproducibility={profile.reproducibility} label="Source" />);
  fireEvent.click(screen.getByText("Source", { selector: "summary" }));
  expect(screen.queryByRole("link", { name: "Current PLUTO record (JSON)" })).toBeNull();
  expect(screen.getByRole("link", { name: /About this dataset/ })).toHaveAttribute("href", "https://data.cityofnewyork.us/d/64uk-42ks");
  expect(screen.getByText("conflicting", { exact: true })).toBeInTheDocument();
  expect(screen.getByText("overridden", { exact: true })).toBeInTheDocument();
  const raw = screen.getByText("Full captured source record").closest("details")!.querySelector("pre")!;
  expect(JSON.parse(raw.textContent!)).toEqual(record);
  expect(document.querySelector('a[href^="javascript:"]')).toBeNull();
});

it("legacy evidence can use its own confirmed dataset without profile metadata", () => {
  const profile = baseProfile();
  render(<ProvenanceDisclosure records={[profile.provenance[0]]} label="Source" />);
  fireEvent.click(screen.getByText("Source", { selector: "summary" }));
  expect(screen.getByRole("link", { name: "Current PLUTO record (JSON)" })).toHaveAttribute("href", `https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=${profile.identity.bbl}`);
});
