// M5-T122 (D-086 P3b): the condo RECORDS surface moved to CondoRecordsSection.tsx
// (AS-2 modularity) plus the spec §5.4 visual/state pass (AS-1). These probes cover
// (1) the compatibility FACADE — PropertyOverview re-exports the same references
// CondoRecordsSection now owns, so no importer is edited; and (2) the ADDED §5.4
// elements: the "Reference only" tag (C02) placed OUTSIDE the h2 so the locked
// accessible name is unchanged, the "Zoning missing for N lots" summary (C08), the
// "Human record" claim-class label (C04), and the "Parcels differ" label + the
// recorded-vs-current comparison disclosure (C06). Every existing exit-gate state
// (single / multi_lot / self-attested / revoked / discrepant / unavailable) already
// has coverage in condo-resolution-display.test.tsx — those are NOT rebuilt here.
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import * as facade from "../PropertyOverview";
import {
  CondoRecordsChannelSection,
  deriveCondoSurface,
  deriveCondoDisplay,
  condoWithholdsAllowances,
} from "../CondoRecordsSection";
import {
  CONDO_OUTCOME_MULTI_LOT,
  CONDO_OUTCOME_RESOLVED_SINGLE,
  fetchCondoRecords,
  type CondoRecordsOutcome,
} from "@/lib/condo-records";
import { baseProfile } from "@/test-support/fixtures";

afterEach(cleanup);

// --- channel stubs (mirror condo-resolution-display.test.tsx) ----------------
const CHANNEL_PROVENANCE = {
  source_id: "nyc-dof-dtm-condo-soda",
  dataset_ids: ["p8u6-a6it"],
  retrieved_at: "2026-09-01T14:05:56Z",
  dataset_version: "2026-08-30T00:00:00Z",
  queries: [],
};

function channelResponse(body: unknown, status = 200): Response {
  return {
    status,
    headers: { get: () => null },
    json: async () => body,
  } as unknown as Response;
}

async function channelOutcome(body: unknown, status = 200): Promise<CondoRecordsOutcome> {
  return fetchCondoRecords("1000010010", {
    fetchImpl: (async () => channelResponse(body, status)) as unknown as typeof fetch,
  });
}

type BaseLot = { bbl: string; recorded_zoning: string | null; recorded_zoning_status: string };

function multiLotDoc(baseLots: BaseLot[], siteDefinition: unknown = undefined): Record<string, unknown> {
  return {
    document_kind: "condo_records",
    bbl: "1003037502",
    outcome: CONDO_OUTCOME_MULTI_LOT,
    entered_bbl: "1003037502",
    entered_lot_class: "billing",
    billing_bbl: "1003037502",
    billing_bbl_status: "recorded",
    base_lots: baseLots,
    substitution: null,
    condo_key: "103344",
    condo_number: "3344",
    resolution_path: "billing",
    provenance: CHANNEL_PROVENANCE,
    notes: [],
    reason: null,
    error_type: null,
    divergent_zoning_notice:
      "Divergent zoning across a condo's base lots is a qualified-human legal question.",
    recorded_zoning_dependency:
      "Recorded zoning per base lot is not carried by the DOF DTM condo base-lot channel; " +
      "it requires the ZTLDB / spatial zoning-by-BBL lookup (out of scope).",
    ...(siteDefinition === undefined ? {} : { site_definition: siteDefinition }),
  };
}

const MIXED_LOTS: BaseLot[] = [
  { bbl: "1003030019", recorded_zoning: null, recorded_zoning_status: "unknown" },
  { bbl: "1003030025", recorded_zoning: "R7-2", recorded_zoning_status: "recorded" },
];
const ALL_UNKNOWN_LOTS: BaseLot[] = [
  { bbl: "1003030019", recorded_zoning: null, recorded_zoning_status: "unknown" },
  { bbl: "1003030025", recorded_zoning: null, recorded_zoning_status: "unknown" },
];
const ALL_RECORDED_LOTS: BaseLot[] = [
  { bbl: "1003030019", recorded_zoning: "R6", recorded_zoning_status: "recorded" },
  { bbl: "1003030025", recorded_zoning: "R7-2", recorded_zoning_status: "recorded" },
];

async function renderMulti(baseLots: BaseLot[], siteDefinition: unknown = undefined) {
  const decision = deriveCondoSurface(baseProfile(), await channelOutcome(multiLotDoc(baseLots, siteDefinition)));
  render(<CondoRecordsChannelSection decision={decision} />);
  return decision;
}

const SD_CONFIRMED_AT = "2026-09-20T08:23:30.089123+00:00";
function confirmation(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    record_id: "rec-abc123",
    condo_key: "103344",
    billing_bbl: "1003037502",
    entered_bbl: "1003037502",
    parcels: ["1003030019", "1003030025"],
    confirmer: { name: "Dana Reviewer", role: "qualified_professional" },
    attestation_status: "unauthenticated_self_attested",
    refused_for_calculation: true,
    confirmed_at: SD_CONFIRMED_AT,
    status: "active",
    supersedes_id: null,
    superseded_by_id: null,
    reason: null,
    note: null,
    transitions: [],
    provenance: {},
    ...overrides,
  };
}
function siteDefBlock(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    condo_key: "103344",
    status: "confirmed",
    active_confirmation: confirmation(),
    confirmations: [confirmation()],
    parcel_discrepancy: null,
    note: "recorded human confirmation",
    ...overrides,
  };
}

describe("M5-T122 AS-2: PropertyOverview re-exports the moved condo API (compatibility facade)", () => {
  it("re-exports the SAME references CondoRecordsSection now owns — no importer breaks", () => {
    expect(facade.CondoRecordsChannelSection).toBe(CondoRecordsChannelSection);
    expect(facade.deriveCondoSurface).toBe(deriveCondoSurface);
    expect(facade.deriveCondoDisplay).toBe(deriveCondoDisplay);
    expect(facade.condoWithholdsAllowances).toBe(condoWithholdsAllowances);
  });
});

describe("M5-T122 AS-1 §5.4 C02: the 'Reference only' tag sits OUTSIDE the locked h2 name", () => {
  it("shows a 'Reference only' tag on the multi-lot records group while the h2 name stays exactly 'City records for this condo'", async () => {
    await renderMulti(MIXED_LOTS);
    // The locked accessible name (report-view.test.tsx pins this exact string) is
    // unchanged — the tag is a sibling, never inside the h2.
    expect(
      screen.getByRole("heading", { level: 2, name: "City records for this condo" }),
    ).toBeInTheDocument();
    const tag = screen.getByTestId("condo-records-reference-only");
    expect(tag).toHaveTextContent("Reference only");
    // Records never read as allowances.
    expect(tag.textContent ?? "").not.toMatch(/allowance|permitted|approved|maximum allowed/i);
  });

  it("joins the single/allow substitution identity with a 'City record' claim tag while its h2 name stays exactly 'Recorded base lot for this condo'", async () => {
    const singleDoc = {
      document_kind: "condo_records",
      bbl: "1003031001",
      outcome: CONDO_OUTCOME_RESOLVED_SINGLE,
      entered_bbl: "1003031001",
      entered_lot_class: "unit",
      billing_bbl: null,
      billing_bbl_status: "unknown",
      base_lots: [{ bbl: "1003030019", recorded_zoning: null, recorded_zoning_status: "unknown" }],
      substitution: { entered_bbl: "1003031001", analyzed_bbl: "1003030019", note: "runs on base lot" },
      condo_key: "103343",
      condo_number: "3343",
      resolution_path: "unit",
      provenance: CHANNEL_PROVENANCE,
      notes: [],
      reason: null,
      error_type: null,
      divergent_zoning_notice: null,
    };
    const decision = deriveCondoSurface(baseProfile(), await channelOutcome(singleDoc));
    render(<CondoRecordsChannelSection decision={decision} />);
    expect(
      screen.getByRole("heading", { level: 2, name: "Recorded base lot for this condo" }),
    ).toBeInTheDocument();
    expect(screen.getByTestId("condo-substitution-city-record")).toHaveTextContent("City record");
  });
});

describe("M5-T122 AS-1 §5.4 C08: the 'Zoning missing for N lots' summary (present + absent)", () => {
  it("counts ONE missing lot on a mixed set (some recorded, some unknown)", async () => {
    await renderMulti(MIXED_LOTS);
    expect(screen.getByTestId("condo-zoning-missing-count")).toHaveTextContent("Zoning missing for 1 lot");
    // Singular, not "1 lots".
    expect(screen.getByTestId("condo-zoning-missing-count").textContent ?? "").not.toMatch(/1 lots/);
  });

  it("counts every base lot when none carry recorded zoning", async () => {
    await renderMulti(ALL_UNKNOWN_LOTS);
    expect(screen.getByTestId("condo-zoning-missing-count")).toHaveTextContent("Zoning missing for 2 lots");
  });

  it("ABSENT: no missing-count line when every base lot carries recorded zoning", async () => {
    await renderMulti(ALL_RECORDED_LOTS);
    expect(screen.queryByTestId("condo-zoning-missing-count")).toBeNull();
    // The gap note is also absent when nothing is missing.
    expect(screen.queryByTestId("condo-zoning-dependency")).toBeNull();
  });
});

describe("M5-T122 AS-1 §5.4 C04: the 'Human record' claim-class label (present + absent)", () => {
  it("labels a recorded active confirmation 'Human record' as text", async () => {
    await renderMulti(MIXED_LOTS, siteDefBlock());
    const label = screen.getByTestId("condo-site-definition-claim");
    expect(label).toHaveTextContent("Human record");
    // A record, never an allowance.
    const group = screen.getByTestId("condo-site-definition");
    expect(group.textContent ?? "").not.toMatch(/allowance/i);
  });

  it("ABSENT: an unconfirmed site definition carries no 'Human record' label", async () => {
    await renderMulti(MIXED_LOTS, siteDefBlock({ status: "unconfirmed", active_confirmation: null, confirmations: [] }));
    expect(screen.queryByTestId("condo-site-definition-claim")).toBeNull();
    expect(screen.getByTestId("condo-site-definition-unconfirmed")).toBeInTheDocument();
  });
});

describe("M5-T122 AS-1 §5.4 C06: the 'Parcels differ' label + comparison disclosure (present + absent)", () => {
  it("shows 'Parcels differ' and lists the recorded-vs-current base lots in a native disclosure without revoking the record", async () => {
    await renderMulti(
      MIXED_LOTS,
      siteDefBlock({
        parcel_discrepancy: {
          recorded_parcels: ["1003030019", "1003030025"],
          current_resolver_parcels: ["1003030019", "1003030099"],
        },
      }),
    );
    const discrepancy = screen.getByTestId("condo-site-definition-discrepancy");
    expect(discrepancy).toHaveTextContent("Parcels differ");
    expect(discrepancy).toHaveTextContent("does not change the confirmation");
    // The comparison lists both the recorded and the current base lots.
    const detail = within(discrepancy).getByTestId("condo-site-definition-discrepancy-detail");
    expect(detail).toHaveTextContent("Recorded in the confirmation: 1003030019, 1003030025");
    expect(detail).toHaveTextContent("Current city records: 1003030019, 1003030099");
    // The confirmation itself is still surfaced (a discrepancy never silently revokes it).
    expect(screen.getByTestId("condo-site-definition")).toBeInTheDocument();
  });

  it("ABSENT: no discrepancy element when the recorded parcels match the current resolver set", async () => {
    await renderMulti(MIXED_LOTS, siteDefBlock());
    expect(screen.queryByTestId("condo-site-definition-discrepancy")).toBeNull();
  });
});
