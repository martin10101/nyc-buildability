// M5-T045 (D-073-R006): analysis identity record — records-vs-allowances on the
// entered-vs-analyzed BBL, the ONLY identity distinction the web contract
// exposes (there is no base-lot/substrate BBL field). These probes prove the
// neutral wording (no billing/base-lot/condo inference), the fail-safe withhold
// on a divergent or absent analyzed identity, and that the identity is a RECORD
// kept separate from any calculated allowance. This file covers the screen
// surface (the component directly); the printed-brief (ReportView) parity is in
// report-view.test.tsx.
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AnalysisIdentityNotice } from "../AnalysisIdentityNotice";
import { CondoRecordsChannelSection, PropertyOverview, deriveCondoSurface } from "../PropertyOverview";
import {
  CONDO_OUTCOME_ERROR,
  CONDO_OUTCOME_MULTI_LOT,
  CONDO_OUTCOME_NOT_CONDO_BILLING,
  CONDO_OUTCOME_RESOLVED_SINGLE,
  CONDO_OUTCOME_UNRESOLVED,
  fetchCondoRecords,
  type CondoRecordsOutcome,
} from "@/lib/condo-records";
import { baseProfile } from "@/test-support/fixtures";
import { draftApplicableDoc } from "@/test-support/rule-evaluation-fixtures";
import type { PropertyProfile } from "@/lib/contract";
import type { Scenario } from "@/lib/scenario-contract";
import scenarioFixture from "../../../../../../packages/contracts/fixtures/valid/scenario/preliminary_r5_cap.json";

vi.mock("@/components/address/LotOutlineMap", () => ({ LotOutlineMap: () => <div>Map presentation seam</div> }));
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

const OPENED = "1000010001";

// --- condo-records CHANNEL stubs (M5-T052) ----------------------------------
// PropertyOverview reads the production channel via useCondoRecords(bbl), which
// uses the global fetch; these helpers stub that channel deterministically. The
// same document builders drive the pure deriveCondoSurface decision tests.
const CHANNEL_SOURCE = "nyc-dof-dtm-condo-soda";
const CHANNEL_DATASET = "p8u6-a6it";
const CHANNEL_RETRIEVED = "2026-09-01T14:05:56Z";
const CHANNEL_VERSION = "2026-08-30T00:00:00Z";
const CHANNEL_DIVERGENT =
  "Divergent zoning across a condo's base lots is a qualified-human legal question.";

function channelResponse(body: unknown, status = 200): Response {
  return {
    status,
    headers: { get: () => null },
    json: async () => body,
  } as unknown as Response;
}

function stubChannel(body: unknown, status = 200) {
  vi.stubGlobal("fetch", vi.fn(async () => channelResponse(body, status)));
}

function stubChannelFailure() {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => {
      throw new TypeError("condo records channel unreachable");
    }),
  );
}

function channelProvenance() {
  return {
    source_id: CHANNEL_SOURCE,
    dataset_ids: [CHANNEL_DATASET],
    retrieved_at: CHANNEL_RETRIEVED,
    dataset_version: CHANNEL_VERSION,
    queries: [
      {
        dataset_id: CHANNEL_DATASET,
        query_kind: "condo_billing_bbl",
        retrieved_at: CHANNEL_RETRIEVED,
        record_count: 2,
        rows_updated_at: CHANNEL_VERSION,
      },
    ],
  };
}

function channelMultiLotDoc() {
  return {
    document_kind: "condo_records",
    bbl: "1003037502",
    outcome: CONDO_OUTCOME_MULTI_LOT,
    billing_bbl: "1003037502",
    base_lots: [
      { bbl: "1003030019", recorded_zoning: null },
      { bbl: "1003030025", recorded_zoning: "R7-2" },
    ],
    substitution: null,
    condo_key: "103344",
    condo_number: "3344",
    resolution_path: "billing",
    provenance: channelProvenance(),
    notes: [],
    reason: null,
    error_type: null,
    divergent_zoning_notice: CHANNEL_DIVERGENT,
  };
}

function channelSingleDoc() {
  return {
    document_kind: "condo_records",
    bbl: "1003031001",
    outcome: CONDO_OUTCOME_RESOLVED_SINGLE,
    billing_bbl: "1003031001",
    base_lots: [{ bbl: "1003030019", recorded_zoning: null }],
    substitution: {
      entered_bbl: "1003031001",
      analyzed_bbl: "1003030019",
      note: "Analysis runs on the recorded base tax lot the city records for this condo.",
    },
    condo_key: "103343",
    condo_number: "3343",
    resolution_path: "unit",
    provenance: channelProvenance(),
    notes: [],
    reason: null,
    error_type: null,
    divergent_zoning_notice: null,
  };
}

function channelSimpleDoc(outcome: string) {
  return {
    document_kind: "condo_records",
    bbl: "1003037501",
    outcome,
    billing_bbl: outcome === CONDO_OUTCOME_NOT_CONDO_BILLING ? null : "1003037501",
    base_lots: [],
    substitution: null,
    condo_key: null,
    condo_number: null,
    resolution_path: "billing",
    provenance: channelProvenance(),
    notes: [],
    reason: "honest absence — no base lot fabricated.",
    error_type: outcome === CONDO_OUTCOME_ERROR ? "source_unavailable" : null,
    divergent_zoning_notice: null,
  };
}

async function channelOutcome(body: unknown, status = 200): Promise<CondoRecordsOutcome> {
  return fetchCondoRecords("1000010010", {
    fetchImpl: (async () => channelResponse(body, status)) as unknown as typeof fetch,
  });
}

function doc(bbl: string | null): { evaluated_input: { bbl: string | null } } {
  return { evaluated_input: { bbl } };
}

// Representative fixtures that populate ONLY the existing contract-1.3.0 channels
// the accepted backend seam (condo_resolution_report) feeds — the note text and
// the multi-lot conflict shape mirror
// services/api/app/profile/zoning_crosscheck.py field-for-field (real captured
// condo_key 103343 -> base lot 1003030019, source/dataset ids verbatim). No
// resolution is inferred from a BBL difference and no contract field is invented.
function resolvedSingleProfile(): PropertyProfile {
  const profile = baseProfile();
  profile.reproducibility!.connector_notes = [
    "condo_resolution: [resolved_single_base_lot] billing BBL 1003037501 resolved to the single recorded base lot 1003030019 " +
      "(source nyc-dof-dtm-condo-soda, dataset(s) p8u6-a6it, condo_key=103343, retrieved 2026-09-01T14:05:56Z); " +
      "the analysis substrate is the recorded base lot. RECORD, not a computed allowance.",
  ];
  return profile;
}

function unresolvedProfile(): PropertyProfile {
  const profile = baseProfile();
  profile.reproducibility!.connector_notes = [
    "condo_resolution: [unresolved] billing BBL 1003037599 matched no base-lot record and the fallbacks were exhausted " +
      "(source nyc-dof-dtm-condo-soda, dataset(s) p8u6-a6it, condo_key=none, retrieved n/a); honest unresolved " +
      "result - no base lot is fabricated and no reference number is presented as a computed result.",
  ];
  return profile;
}

// A condo_resolution note WITHOUT a machine outcome token (the legacy/defensive
// shape): the guard cannot confirm a single-base-lot substitution, so it fails
// safe and withholds — and, per the M5-T052 ruling, it is NOT a records case.
function missingTokenProfile(): PropertyProfile {
  const profile = baseProfile();
  profile.reproducibility!.connector_notes = [
    "condo_resolution: billing BBL 1003037501 mapped to a recorded base lot " +
      "(source nyc-dof-dtm-condo-soda, dataset(s) p8u6-a6it); no machine outcome token.",
  ];
  return profile;
}

// A well-formed bracket carrying a token this build does not recognise (a future
// backend outcome): the allow-list withholds, and it is NOT a records case.
function unknownTokenProfile(): PropertyProfile {
  const profile = baseProfile();
  profile.reproducibility!.connector_notes = [
    "condo_resolution: [resolved_multi_condo_v2] billing BBL 1003037501 produced a future outcome " +
      "this build does not recognise (source nyc-dof-dtm-condo-soda, dataset(s) p8u6-a6it).",
  ];
  return profile;
}

// A fully displayable profile + scenario + evaluation (the SAME pattern the
// DevelopmentLimits suite uses): a non-condo profile renders evaluated FAR
// "1.50" and the draft cap "15,000 sq ft". The condo guard tests below layer a
// condo resolution state ON TOP of these and prove the computed allowances then
// disappear even though the scenario/evaluation are unchanged and would
// otherwise be displayable.
function displayableInputs() {
  const profile = baseProfile();
  const evaluation = draftApplicableDoc();
  const scenario = structuredClone(scenarioFixture) as Scenario;
  evaluation.evaluated_input.bbl = profile.identity.bbl;
  scenario.evaluated_input.bbl = profile.identity.bbl;
  Object.assign(profile.provenance.find(record => record.original_field_name === "residfar")!, { normalized_value: 3, original_value: "3.00" });
  Object.assign(profile.provenance.find(record => record.original_field_name === "builtfar")!, { normalized_value: 2.61, original_value: "2.61" });
  profile.existing_building_facts.builtfar!.value = 2.61;
  return { profile, evaluation, scenario };
}

function multiLotProfile(): PropertyProfile {
  const profile = baseProfile();
  profile.conflicts = [
    {
      field: "condo_base_lot_resolution",
      values: [
        {
          source_id: "nyc-dof-dtm-condo-soda",
          value: "1003030019",
          derivation:
            "recorded base tax lot for condo billing BBL 1003037502 (source nyc-dof-dtm-condo-soda, " +
            "dataset(s) p8u6-a6it, condo_key=103344, retrieved 2026-09-01T14:05:56Z); one of 2 base " +
            "lots - a RECORD, never a chosen answer",
        },
        {
          source_id: "nyc-dof-dtm-condo-soda",
          value: "1003030025",
          derivation:
            "recorded base tax lot for condo billing BBL 1003037502 (source nyc-dof-dtm-condo-soda, " +
            "dataset(s) p8u6-a6it, condo_key=103344, retrieved 2026-09-01T14:05:56Z); one of 2 base " +
            "lots - a RECORD, never a chosen answer",
        },
      ],
      resolution: "unresolved",
      reason:
        "condo billing BBL 1003037502 resolves to 2 base tax lots ['1003030019', '1003030025']; the " +
        "base lots are presented as RECORDS with NO computed allowance.",
    },
  ] as unknown as PropertyProfile["conflicts"];
  return profile;
}

describe("AnalysisIdentityNotice — entered-vs-analyzed identity record (M5-T045)", () => {
  it("renders nothing when no analysis document is present", () => {
    const { container } = render(
      <AnalysisIdentityNotice label="Rule evaluation" requestedBbl={OPENED} document={null} />,
    );
    expect(container.firstChild).toBeNull();
  });

  it("matching identity proceeds with no withhold — results are not suppressed", () => {
    const { container } = render(
      <AnalysisIdentityNotice label="Rule evaluation" requestedBbl={OPENED} document={doc(OPENED)} />,
    );
    expect(container.firstChild).toBeNull();
    expect(screen.queryByRole("alert")).toBeNull();
    expect(screen.queryByText(/Results are withheld from this property/)).toBeNull();
  });

  it("differing identity withholds results and records the identifiers neutrally, inferring no relationship", () => {
    render(
      <AnalysisIdentityNotice label="Rule evaluation" requestedBbl={OPENED} document={doc("5000010001")} />,
    );
    const alert = screen.getByRole("alert");
    // Locked fail-safe strings (parity with the ArchitectEntry announcer and entry.test.tsx).
    expect(alert).toHaveTextContent("Rule evaluation identity mismatch");
    expect(alert).toHaveTextContent(
      "Requested BBL 1000010001; returned BBL 5000010001. Results are withheld from this property.",
    );
    // Neutral entered-vs-analyzed record; no billing/base-lot (condo) inference.
    expect(alert).toHaveTextContent(
      "You opened BBL 1000010001; this rule evaluation was analyzed for BBL 5000010001.",
    );
    expect(alert).toHaveTextContent("no relationship between them is inferred");
    expect(alert.textContent ?? "").not.toMatch(/base lot|billing|condo|resolved/i);
    // Records vs allowances: the returned record is captured; no allowance is shown.
    expect(alert).toHaveTextContent("no calculated allowance is shown");
    expect(screen.getByText("Returned rule evaluation record")).toBeInTheDocument();
    expect(alert).toHaveAttribute("data-identity-state", "differs");
  });

  it("absent analyzed identity is reported as missing and withheld (not stated)", () => {
    render(
      <AnalysisIdentityNotice label="Rule evaluation" requestedBbl={OPENED} document={doc(null)} />,
    );
    const alert = screen.getByRole("alert");
    expect(alert).toHaveTextContent("Rule evaluation identity missing");
    expect(alert).toHaveTextContent("returned BBL not stated. Results are withheld from this property.");
    expect(alert).toHaveTextContent("analyzed for an unstated identifier");
    expect(alert).toHaveAttribute("data-identity-state", "absent");
  });

  it("an unrelated returned identity is still withheld — never reclassified as a benign resolution", () => {
    // A document whose analyzed BBL is an unrelated property must fail safe; the
    // neutral wording must never become licence to accept foreign results.
    render(
      <AnalysisIdentityNotice label="Scenario" requestedBbl={OPENED} document={doc("3999990099")} />,
    );
    const alert = screen.getByRole("alert");
    expect(alert).toHaveTextContent("Scenario identity mismatch");
    expect(alert).toHaveTextContent("Results are withheld from this property");
    expect(alert.textContent ?? "").not.toMatch(/resolved|base lot|proceed|accepted/i);
  });

  it("labels the record by analysis kind (scenario vs rule evaluation)", () => {
    const { rerender } = render(
      <AnalysisIdentityNotice label="Scenario" requestedBbl={OPENED} document={doc("5000010001")} />,
    );
    expect(screen.getByTestId("analysis-identity-scenario")).toBeInTheDocument();
    rerender(
      <AnalysisIdentityNotice label="Rule evaluation" requestedBbl={OPENED} document={doc("5000010001")} />,
    );
    expect(screen.getByTestId("analysis-identity-rule-evaluation")).toBeInTheDocument();
  });
});

describe("CondoRecordsChannelSection on the printed brief — the SHARED surface decision (M5-T052, D-073-R006)", () => {
  // The printed brief (ReportView) now renders the SAME CondoRecordsChannelSection
  // the screen (PropertyOverview) uses, from the SAME shared decision
  // (deriveCondoSurface). These probes drive that component with decisions built
  // from the live per-BBL channel folded onto the accepted profile guard, so the
  // brief and the screen can never disagree on records, substitution, a
  // profile/channel disagreement, or honest absence.
  async function decisionFor(profile: PropertyProfile, body: unknown, status = 200) {
    return deriveCondoSurface(profile, await channelOutcome(body, status));
  }

  it("renders nothing for a non-condo channel — honest absence, byte-identical to no condo section", async () => {
    const decision = await decisionFor(baseProfile(), { detail: "Not Found" }, 404);
    const { container } = render(<CondoRecordsChannelSection decision={decision} />);
    expect(container.firstChild).toBeNull();
    expect(screen.queryByTestId("condo-resolution-records")).toBeNull();
    expect(screen.queryByTestId("condo-substitution-record")).toBeNull();
  });

  it("a channel OUTAGE renders nothing on the brief and does not withhold on its own", () => {
    const decision = deriveCondoSurface(baseProfile(), { kind: "network_error", message: "down" });
    const { container } = render(<CondoRecordsChannelSection decision={decision} />);
    expect(container.firstChild).toBeNull();
    expect(decision.withholdAllowances).toBe(false);
  });

  it("a multi-lot condo prints the city records — RECORD-class wording, NO allowance vocabulary, no chosen answer", async () => {
    const decision = await decisionFor(baseProfile(), channelMultiLotDoc());
    render(<CondoRecordsChannelSection decision={decision} />);
    const section = screen.getByTestId("condo-resolution-records");
    expect(section).toHaveTextContent("City records for this condo");
    // HJ-A3 heading semantics + the D-073-R006 grep gate: RECORD class only — no
    // analysis/result words AND no allowance-class vocabulary in the printed
    // records section.
    expect(section.textContent ?? "").not.toMatch(/\banalys(is|es|ed)\b|zoning result|computed result/i);
    expect(section.textContent ?? "").not.toMatch(/allowance/i);
    const records = screen.getAllByTestId("condo-base-lot-record");
    expect(records).toHaveLength(2);
    expect(records[0]).toHaveTextContent("1003030019");
    expect(records[0]).toHaveTextContent("recorded zoning: not recorded (unknown)");
    expect(records[1]).toHaveTextContent("1003030025");
    expect(records[1]).toHaveTextContent("recorded zoning: R7-2");
    expect(screen.getByTestId("condo-divergent-notice")).toHaveTextContent("qualified-human legal question");
    // Records, never allowances: no computed decimal figure appears in the section.
    expect(section.textContent ?? "").not.toMatch(/\d+\.\d+/);
  });

  it("a resolved-single condo is the ALLOW path — the substitution is recorded (entered vs analyzed), no records section", async () => {
    const decision = await decisionFor(baseProfile(), channelSingleDoc());
    render(<CondoRecordsChannelSection decision={decision} />);
    const sub = screen.getByTestId("condo-substitution-record");
    expect(sub).toHaveTextContent("1003031001"); // entered (unit BBL)
    expect(sub).toHaveTextContent("1003030019"); // analyzed base lot
    expect(sub.textContent ?? "").not.toMatch(/allowance/i);
    expect(screen.queryByTestId("condo-resolution-records")).toBeNull();
  });

  it("an unresolved condo prints no records — honest absence on the brief", async () => {
    const decision = await decisionFor(baseProfile(), channelSimpleDoc(CONDO_OUTCOME_UNRESOLVED));
    const { container } = render(<CondoRecordsChannelSection decision={decision} />);
    expect(container.firstChild).toBeNull();
    expect(screen.queryByTestId("condo-resolution-records")).toBeNull();
  });

  it("a resolver-error condo fabricates no records — honest absence on the brief", async () => {
    const decision = await decisionFor(baseProfile(), channelSimpleDoc(CONDO_OUTCOME_ERROR));
    const { container } = render(<CondoRecordsChannelSection decision={decision} />);
    expect(container.firstChild).toBeNull();
    expect(screen.queryByTestId("condo-resolution-records")).toBeNull();
  });

  // --- Focused profile/channel DISAGREEMENT cases (M5-T052 reconciliation) -----
  it("profile withholds but the channel reports a benign single: fail-safe governs, the disagreement is surfaced, and NO records are shown", async () => {
    // The accepted profile guard (a multi-lot conflict) withholds; the live
    // channel reports a single base lot. The brief fails safe (withhold), shows
    // the honest disagreement notice, and never prints records or a substitution —
    // the professional-review determination above governs.
    const decision = await decisionFor(multiLotProfile(), channelSingleDoc());
    expect(decision.withholdAllowances).toBe(true);
    expect(decision.conflict).toBe(true);
    render(<CondoRecordsChannelSection decision={decision} />);
    const conflict = screen.getByTestId("condo-records-conflict");
    expect(conflict).toHaveTextContent("differ on this condo");
    expect(conflict).toHaveTextContent("professional-review determination above governs");
    expect(conflict.textContent ?? "").not.toMatch(/allowance/i);
    expect(screen.queryByTestId("condo-resolution-records")).toBeNull();
    expect(screen.queryByTestId("condo-substitution-record")).toBeNull();
  });

  it("the channel alone confirms a multi-lot condo the profile does not carry: the brief prints those city records with no false disagreement", async () => {
    // A profile with no condo signal + a channel multi-lot outcome is NOT a
    // disagreement (the profile guard simply has nothing to say), so the brief
    // surfaces the channel's city records exactly as the screen does.
    const decision = await decisionFor(baseProfile(), channelMultiLotDoc());
    expect(decision.conflict).toBe(false);
    render(<CondoRecordsChannelSection decision={decision} />);
    expect(screen.getByTestId("condo-resolution-records")).toBeInTheDocument();
    expect(screen.queryByTestId("condo-records-conflict")).toBeNull();
  });

  it("every note-only condo profile is honest absence on the brief when the channel confirms no multi-lot set (coherent with the screen)", async () => {
    // resolved-single, unresolved, a MISSING token, and an UNKNOWN token are all
    // note-only profile states with no channel multi-lot outcome. On the brief
    // they are honest ABSENCE — records only ever come from a channel-confirmed
    // multi-lot set — exactly as the screen renders them. The withhold for the
    // fail-safe outcomes still flows through the unchanged profile guard.
    const noteOnlyProfiles: PropertyProfile[] = [
      resolvedSingleProfile(),
      unresolvedProfile(),
      missingTokenProfile(),
      unknownTokenProfile(),
    ];
    for (const profile of noteOnlyProfiles) {
      const decision = await decisionFor(profile, { detail: "Not Found" }, 404);
      const { container, unmount } = render(<CondoRecordsChannelSection decision={decision} />);
      expect(container.firstChild).toBeNull();
      expect(screen.queryByTestId("condo-resolution-records")).toBeNull();
      unmount();
    }
  });

  it("unrelated notes/conflicts never trigger the brief records surface", async () => {
    const profile = baseProfile();
    profile.reproducibility!.connector_notes = [
      "ztldb_crosscheck: compared 12 lot-level zoning fields across 2 official presentations for BBL 1003030019.",
    ];
    profile.conflicts = [
      {
        field: "zonedist1",
        values: [
          { source_id: "nyc-dcp-pluto-soda", value: "R6" },
          { source_id: "nyc-dcp-ztldb-soda", value: "R7" },
        ],
        resolution: "unresolved",
      },
    ] as unknown as PropertyProfile["conflicts"];
    const decision = await decisionFor(profile, { detail: "Not Found" }, 404);
    const { container } = render(<CondoRecordsChannelSection decision={decision} />);
    expect(container.firstChild).toBeNull();
  });
});

// The production per-BBL condo-records channel (useCondoRecords) now drives the
// architect SCREEN. PropertyOverview reads it via the global fetch, so every
// render below stubs that channel deterministically; the profile fail-safe guard
// (the accepted M5-T045 allow-list) is layered underneath and STILL withholds on
// its own even when the live channel is absent (records never unlock allowances).
describe("PropertyOverview — the condo-records channel drives records + withhold (M5-T052, D-073-R006)", () => {
  it("control: a non-condo profile SHOWS the computed allowances and renders no condo section", async () => {
    const { profile, evaluation, scenario } = displayableInputs();
    stubChannel({ detail: "Not Found" }, 404); // route absent -> non-condo
    render(<PropertyOverview profile={profile} scenario={scenario} evaluation={evaluation} onInspect={vi.fn()} />);
    await waitFor(() => expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("1.50"));
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("15,000 sq ft");
    expect(screen.queryByTestId("condo-resolution-records")).toBeNull();
    expect(screen.queryByTestId("condo-substitution-record")).toBeNull();
  });

  it("a channel-confirmed multi-lot condo withholds every computed allowance and shows the city records UNDER the fail-safe", async () => {
    const { profile, evaluation, scenario } = displayableInputs();
    stubChannel(channelMultiLotDoc());
    render(<PropertyOverview profile={profile} scenario={scenario} evaluation={evaluation} onInspect={vi.fn()} />);
    // The records section appears once the channel resolves...
    await waitFor(() => expect(screen.getByTestId("condo-resolution-records")).toBeInTheDocument());
    // ...and the SAME scenario/evaluation that display in the control now show no
    // computed allowance (the channel multi-lot withholds).
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated");
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
    // Every recorded base lot is a RECORD; recorded zoning is carried or an
    // explicit unknown; the no-collapse notice stays visible.
    const records = screen.getAllByTestId("condo-base-lot-record");
    expect(records).toHaveLength(2);
    expect(records[0]).toHaveTextContent("1003030019");
    expect(records[0]).toHaveTextContent("recorded zoning: not recorded (unknown)");
    expect(records[1]).toHaveTextContent("1003030025");
    expect(records[1]).toHaveTextContent("recorded zoning: R7-2");
    expect(screen.getByTestId("condo-divergent-notice")).toHaveTextContent("qualified-human legal question");
    // RECORDS not allowances: the section carries no computed decimal figure.
    expect(screen.getByTestId("condo-resolution-records").textContent ?? "").not.toMatch(/\d+\.\d+/);
  });

  it("a channel-confirmed single base lot proceeds on the allow path: allowances show AND the substitution is recorded (entered vs analyzed)", async () => {
    const { profile, evaluation, scenario } = displayableInputs();
    stubChannel(channelSingleDoc());
    render(<PropertyOverview profile={profile} scenario={scenario} evaluation={evaluation} onInspect={vi.fn()} />);
    await waitFor(() => expect(screen.getByTestId("condo-substitution-record")).toBeInTheDocument());
    // The allow path: the analysis ran on the substituted base lot, so the
    // computed allowances still display.
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("1.50");
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("15,000 sq ft");
    const sub = screen.getByTestId("condo-substitution-record");
    expect(sub).toHaveTextContent("1003031001"); // entered (unit BBL)
    expect(sub).toHaveTextContent("1003030019"); // analyzed base lot
    // The allow path is never a multi-lot records view.
    expect(screen.queryByTestId("condo-resolution-records")).toBeNull();
  });

  it("a channel-confirmed unresolved condo withholds allowances and shows no records (honest absence)", async () => {
    const { profile, evaluation, scenario } = displayableInputs();
    stubChannel(channelSimpleDoc(CONDO_OUTCOME_UNRESOLVED));
    render(<PropertyOverview profile={profile} scenario={scenario} evaluation={evaluation} onInspect={vi.fn()} />);
    await waitFor(() => expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated"));
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
    expect(screen.queryByTestId("condo-resolution-records")).toBeNull();
    expect(screen.queryByTestId("condo-substitution-record")).toBeNull();
  });

  it("a channel-confirmed resolver error withholds allowances and fabricates no records", async () => {
    const { profile, evaluation, scenario } = displayableInputs();
    stubChannel(channelSimpleDoc(CONDO_OUTCOME_ERROR));
    render(<PropertyOverview profile={profile} scenario={scenario} evaluation={evaluation} onInspect={vi.fn()} />);
    await waitFor(() => expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated"));
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
    expect(screen.queryByTestId("condo-resolution-records")).toBeNull();
  });

  it("a condo-records channel OUTAGE does not withhold on its own — a non-condo profile keeps its allowances", async () => {
    const { profile, evaluation, scenario } = displayableInputs();
    stubChannelFailure();
    render(<PropertyOverview profile={profile} scenario={scenario} evaluation={evaluation} onInspect={vi.fn()} />);
    await waitFor(() => expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("1.50"));
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("15,000 sq ft");
    expect(screen.queryByTestId("condo-resolution-records")).toBeNull();
  });

  // --- The accepted profile fail-safe guard (M5-T045 allow-list), which stays
  // authoritative even with the live channel absent: records never unlock
  // allowances. The channel is stubbed route-absent so ONLY the profile guard
  // decides. The brief (ReportView) renders the SAME CondoRecordsChannelSection
  // from the SAME shared decision (covered by the shared-decision suite above);
  // the SCREEN assertion here is the fail-safe withhold.
  it("an unresolved condo (profile note) withholds the computed allowances even with the live channel absent", async () => {
    const { profile, evaluation, scenario } = displayableInputs();
    profile.reproducibility!.connector_notes = unresolvedProfile().reproducibility!.connector_notes;
    stubChannel({ detail: "Not Found" }, 404);
    render(<PropertyOverview profile={profile} scenario={scenario} evaluation={evaluation} onInspect={vi.fn()} />);
    await waitFor(() => expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated"));
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
  });

  it("a resolved single base lot (profile note) STILL shows the computed allowances — the analysis ran on the substituted base lot", async () => {
    const { profile, evaluation, scenario } = displayableInputs();
    profile.reproducibility!.connector_notes = resolvedSingleProfile().reproducibility!.connector_notes;
    stubChannel({ detail: "Not Found" }, 404);
    render(<PropertyOverview profile={profile} scenario={scenario} evaluation={evaluation} onInspect={vi.fn()} />);
    await waitFor(() => expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("1.50"));
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("15,000 sq ft");
  });

  it("a condo note with a MISSING outcome token withholds every computed allowance — fail-safe on a note it cannot confirm ran on a single base lot", async () => {
    const { profile, evaluation, scenario } = displayableInputs();
    // A condo_resolution note WITHOUT the machine outcome token (the legacy /
    // defensive shape condoResolutionNotes falls back on): the guard can no longer
    // confirm a single-base-lot substitution, so it must fail safe and withhold —
    // the SAME scenario/evaluation that display allowances in the control show none.
    profile.reproducibility!.connector_notes = [
      "condo_resolution: billing BBL 1003037501 mapped to a recorded base lot " +
        "(source nyc-dof-dtm-condo-soda, dataset(s) p8u6-a6it); no machine outcome token.",
    ];
    stubChannel({ detail: "Not Found" }, 404);
    render(<PropertyOverview profile={profile} scenario={scenario} evaluation={evaluation} onInspect={vi.fn()} />);
    await waitFor(() => expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated"));
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
  });

  it("a condo note with an UNKNOWN outcome token withholds every computed allowance — fail-safe on a token this build does not recognise", async () => {
    const { profile, evaluation, scenario } = displayableInputs();
    // A well-formed bracket carrying a token that is NOT resolved_single_base_lot
    // (e.g. a future backend outcome): the allow-list withholds, never open.
    profile.reproducibility!.connector_notes = [
      "condo_resolution: [resolved_multi_condo_v2] billing BBL 1003037501 produced a future outcome " +
        "this build does not recognise (source nyc-dof-dtm-condo-soda, dataset(s) p8u6-a6it).",
    ];
    stubChannel({ detail: "Not Found" }, 404);
    render(<PropertyOverview profile={profile} scenario={scenario} evaluation={evaluation} onInspect={vi.fn()} />);
    await waitFor(() => expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated"));
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
  });

  it("a condo note with a MALFORMED outcome bracket (unparseable) withholds every computed allowance", async () => {
    const { profile, evaluation, scenario } = displayableInputs();
    // A bracket the outcome regex cannot parse (spaces / non [a-z_] content) ->
    // outcome null -> fail-safe withhold, exactly like a missing token.
    profile.reproducibility!.connector_notes = [
      "condo_resolution: [resolved single base lot] billing BBL 1003037501 " +
        "carries a malformed outcome token (source nyc-dof-dtm-condo-soda).",
    ];
    stubChannel({ detail: "Not Found" }, 404);
    render(<PropertyOverview profile={profile} scenario={scenario} evaluation={evaluation} onInspect={vi.fn()} />);
    await waitFor(() => expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated"));
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
  });
});

// ---------------------------------------------------------------------------
// deriveCondoSurface — the ONE coherent condo-surface decision (the T045 G3-A2
// answer). Pure and total: the fail-safe guard, the records-section eligibility,
// and the substitution explanation are all derived here in ONE place, so they can
// never disagree. Combining is MONOTONIC — the channel may only ADD withholding,
// never remove it.
// ---------------------------------------------------------------------------
describe("deriveCondoSurface — one coherent condo-surface decision", () => {
  it("multi-lot channel: withholds allowances AND shows the records section (no substitution)", async () => {
    const decision = deriveCondoSurface(baseProfile(), await channelOutcome(channelMultiLotDoc()));
    expect(decision.withholdAllowances).toBe(true);
    expect(decision.showRecords).toBe(true);
    expect(decision.showSubstitution).toBe(false);
  });

  it("single channel: the allow path — no withhold, the substitution is shown, no records section", async () => {
    const decision = deriveCondoSurface(baseProfile(), await channelOutcome(channelSingleDoc()));
    expect(decision.withholdAllowances).toBe(false);
    expect(decision.showSubstitution).toBe(true);
    expect(decision.showRecords).toBe(false);
  });

  it("unresolved / resolver-error channel: withhold, no records, no substitution", async () => {
    for (const outcome of [CONDO_OUTCOME_UNRESOLVED, CONDO_OUTCOME_ERROR]) {
      const decision = deriveCondoSurface(baseProfile(), await channelOutcome(channelSimpleDoc(outcome)));
      expect(decision.withholdAllowances).toBe(true);
      expect(decision.showRecords).toBe(false);
      expect(decision.showSubstitution).toBe(false);
    }
  });

  it("a channel outage does NOT withhold on its own — the accepted fail-safes stay authoritative", () => {
    const decision = deriveCondoSurface(baseProfile(), { kind: "network_error", message: "down" });
    expect(decision.withholdAllowances).toBe(false);
    expect(decision.showRecords).toBe(false);
    expect(decision.showSubstitution).toBe(false);
  });

  it("monotonic: the profile guard withholds even when the channel reports a benign single, and the disagreement is surfaced", async () => {
    const decision = deriveCondoSurface(multiLotProfile(), await channelOutcome(channelSingleDoc()));
    expect(decision.withholdAllowances).toBe(true);
    expect(decision.showSubstitution).toBe(false);
    expect(decision.conflict).toBe(true);
  });
});
