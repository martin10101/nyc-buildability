import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import { validateTransitParkingDocument, type TransitParking } from "@/lib/transit-parking-api";
import {
  NOT_AVAILABLE_PREFIX,
  STATUS_HEADLINE,
  transitParkingView,
} from "@/lib/architect/transit-parking-view";

/**
 * Pure view-model for the "Transit and parking zone" section (queue D-15 slice 2,
 * plan §5a / §11b, B-10, check C-8). Proves: every schema `status` enum value maps
 * to the plain `status_label` vocabulary (never the raw token); both committed
 * contract fixtures reshape into the rows the section renders; a missing zone reads
 * "Not available — <reason>"; the detail is carried verbatim; and the structured
 * provenance is grouped for the "Source" disclosure only. The 200 bodies are the
 * COMMITTED contract fixtures read from disk and contract-validated here, so the
 * shape mapped IS the recorded contract shape, never a literal retyped in the test.
 */

const FIXTURE_ROOT = resolve(
  process.cwd(),
  "../../packages/contracts/fixtures/valid/transit_parking",
);

function fixture(name: string): TransitParking {
  const body = JSON.parse(readFileSync(resolve(FIXTURE_ROOT, `${name}.json`), "utf8"));
  const result = validateTransitParkingDocument(body);
  if (!result.ok) throw new Error(`fixture ${name} is not contract-valid: ${result.problems.join("; ")}`);
  return result.status;
}

describe("STATUS_HEADLINE — every schema status enum value maps to plain words", () => {
  // One case per schema `status` enum token (recorded, check_needed).
  it.each([
    ["recorded", "Recorded"],
    ["check_needed", "Check needed"],
  ] as const)("maps %s to the plain label %s", (token, plain) => {
    expect(STATUS_HEADLINE[token]).toBe(plain);
  });

  it("maps each token to the contract's OWN status_label (no invented value)", () => {
    for (const name of ["synthetic_recorded", "synthetic_check_needed"]) {
      const status = fixture(name);
      expect(STATUS_HEADLINE[status.status]).toBe(status.status_label);
    }
  });
});

describe("transitParkingView — the recorded fixture", () => {
  const view = transitParkingView(fixture("synthetic_recorded"));

  it("headlines with the plain status label, not the raw token", () => {
    expect(view.headline).toBe("Recorded");
    expect(view.headline).not.toBe("recorded");
  });

  it("carries the verbatim transit zone and no missing-source line", () => {
    expect(view.zone).toBe("Outer Transit Zone");
    expect(view.missingSource).toBeNull();
  });

  it("carries the server's one-line detail verbatim", () => {
    expect(view.detail).toBe(fixture("synthetic_recorded").detail);
  });

  it("groups the PLUTO provenance for the Source disclosure", () => {
    expect(view.source).not.toBeNull();
    expect(view.source?.dataset).toBe("test-fixture-synthetic PLUTO");
    expect(view.source?.datasetVersion).toBe("26v2");
    expect(view.source?.retrievedAt).toBe("2026-09-30T12:00:00Z");
    expect(view.source?.requestUrl).toBe("test-fixture-synthetic://pluto/5999999999");
  });
});

describe("transitParkingView — the check_needed fixture", () => {
  const raw = fixture("synthetic_check_needed");
  const view = transitParkingView(raw);

  it("headlines Check needed with no recorded zone", () => {
    expect(view.headline).toBe("Check needed");
    expect(view.zone).toBeNull();
  });

  it("reads a missing zone as 'Not available — <reason>', never a bare value", () => {
    expect(view.missingSource).toBe(`${NOT_AVAILABLE_PREFIX}${raw.missing_source}`);
    expect(view.missingSource?.startsWith("Not available — ")).toBe(true);
  });

  it("carries the check-needed detail verbatim", () => {
    expect(view.detail).toBe(raw.detail);
  });
});

describe("transitParkingView — source edge cases", () => {
  it("returns a null source view when the document carries no source", () => {
    const base = fixture("synthetic_recorded");
    const view = transitParkingView({ ...base, source: null });
    expect(view.source).toBeNull();
  });

  it("nulls an absent dataset version / request url rather than an empty row", () => {
    const base = fixture("synthetic_recorded");
    const source = base.source;
    expect(source).not.toBeNull();
    const view = transitParkingView({
      ...base,
      source: source ? { ...source, dataset_version: null, query_ref: null } : null,
    });
    expect(view.source?.datasetVersion).toBeNull();
    expect(view.source?.requestUrl).toBeNull();
    expect(view.source?.dataset).toBe("test-fixture-synthetic PLUTO");
  });
});

describe("transitParkingView — the source-to-check reference (contract 1.1.0)", () => {
  const checkNeeded = fixture("synthetic_check_needed");
  const view = transitParkingView(checkNeeded);

  it("exposes the structured reference from a present missing_source_ref", () => {
    const ref = view.missingSourceRef;
    expect(ref).not.toBeNull();
    expect(ref?.dataset).toBe("Transit Zones");
    expect(ref?.datasetId).toBe("6ztr-wgff");
    expect(ref?.publisher).toBe("Department of City Planning (DCP)");
    expect(ref?.url).toBe("https://data.cityofnewyork.us/d/6ztr-wgff");
  });

  it("nulls a dataset version the source does not record (honest, never invented)", () => {
    expect(view.missingSourceRef?.datasetVersion).toBeNull();
  });

  it("carries each component sub-dataset with its id", () => {
    expect(view.missingSourceRef?.components).toEqual([
      { dataset: "Greater Transit Zone", datasetId: "vhqf-adkz" },
      { dataset: "Appendix I - Transit Zones", datasetId: "dpnc-b2hd" },
    ]);
  });

  it("is null when the recorded document carries a null missing_source_ref", () => {
    expect(transitParkingView(fixture("synthetic_recorded")).missingSourceRef).toBeNull();
  });

  it("is null when the document omits missing_source_ref entirely (a 1.0.0 body)", () => {
    const withoutRef: TransitParking = { ...checkNeeded, missing_source_ref: undefined };
    expect(transitParkingView(withoutRef).missingSourceRef).toBeNull();
  });

  it("nulls an absent url rather than carrying an empty link", () => {
    const ref = checkNeeded.missing_source_ref;
    expect(ref).toBeTruthy();
    const nullUrl: TransitParking = {
      ...checkNeeded,
      missing_source_ref: ref ? { ...ref, url: null } : null,
    };
    expect(transitParkingView(nullUrl).missingSourceRef?.url).toBeNull();
  });
});
