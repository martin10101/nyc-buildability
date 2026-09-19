// M5-T045 (D-073-R006): analysis identity record — records-vs-allowances on the
// entered-vs-analyzed BBL, the ONLY identity distinction the web contract
// exposes (there is no base-lot/substrate BBL field). These probes prove the
// neutral wording (no billing/base-lot/condo inference), the fail-safe withhold
// on a divergent or absent analyzed identity, and that the identity is a RECORD
// kept separate from any calculated allowance. This file covers the screen
// surface (the component directly); the printed-brief (ReportView) parity is in
// report-view.test.tsx.
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AnalysisIdentityNotice } from "../AnalysisIdentityNotice";
import { CondoResolutionRecords, PropertyOverview } from "../PropertyOverview";
import { baseProfile } from "@/test-support/fixtures";
import { draftApplicableDoc } from "@/test-support/rule-evaluation-fixtures";
import type { PropertyProfile } from "@/lib/contract";
import type { Scenario } from "@/lib/scenario-contract";
import scenarioFixture from "../../../../../../packages/contracts/fixtures/valid/scenario/preliminary_r5_cap.json";

vi.mock("@/components/address/LotOutlineMap", () => ({ LotOutlineMap: () => <div>Map presentation seam</div> }));
afterEach(cleanup);

const OPENED = "1000010001";

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

describe("CondoResolutionRecords — condo billing-BBL records vs allowances (M5-T045, D-073-R006)", () => {
  it("renders nothing when neither condo channel is populated — a non-condo profile stays byte-identical", () => {
    const { container } = render(<CondoResolutionRecords profile={baseProfile()} />);
    expect(container.firstChild).toBeNull();
    expect(screen.queryByTestId("condo-resolution-records")).toBeNull();
  });

  it("records a resolved single base lot from the connector_notes channel, framed as a record not an allowance", () => {
    render(<CondoResolutionRecords profile={resolvedSingleProfile()} />);
    const section = screen.getByTestId("condo-resolution-records");
    expect(section).toHaveTextContent("Condo billing lot — recorded base lot(s)");
    // Records vs allowances is stated explicitly.
    expect(section).toHaveTextContent("not a computed development allowance");
    // The backend's own record text is re-presented; the machine prefix is stripped.
    const note = screen.getByTestId("condo-resolution-note");
    expect(note).toHaveTextContent(
      "billing BBL 1003037501 resolved to the single recorded base lot 1003030019",
    );
    expect(note).toHaveTextContent("RECORD, not a computed allowance");
    expect(note.textContent ?? "").not.toContain("condo_resolution:");
    // A clean single resolution is never presented as a multi-lot / divergent case.
    expect(screen.queryByTestId("condo-resolution-multilot")).toBeNull();
  });

  it("presents a multi-lot condo as records of every base lot with NO computed allowance and no chosen answer", () => {
    render(<CondoResolutionRecords profile={multiLotProfile()} />);
    const multilot = screen.getByTestId("condo-resolution-multilot");
    expect(multilot).toHaveTextContent("Multiple recorded base lots — no computed allowance");
    const records = screen.getAllByTestId("condo-base-lot-record");
    expect(records).toHaveLength(2);
    expect(records[0]).toHaveTextContent("1003030019");
    expect(records[1]).toHaveTextContent("1003030025");
    // Divergent zoning stays a qualified-human question; the display never collapses it
    // and never invents a computed figure (no FAR / decimal allowance) from the records.
    expect(multilot).toHaveTextContent("no single base lot is presented as the answer");
    expect(multilot.textContent ?? "").not.toMatch(/\d+\.\d+/);
  });

  it("explains an unresolved condo honestly without presenting a reference number as the result", () => {
    render(<CondoResolutionRecords profile={unresolvedProfile()} />);
    const note = screen.getByTestId("condo-resolution-note");
    expect(note).toHaveTextContent("matched no base-lot record");
    expect(note).toHaveTextContent("no reference number is presented as a computed result");
    expect(screen.queryByTestId("condo-resolution-multilot")).toBeNull();
  });

  it("is driven ONLY by the condo channels — unrelated notes/conflicts never trigger this surface", () => {
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
    const { container } = render(<CondoResolutionRecords profile={profile} />);
    expect(container.firstChild).toBeNull();
  });

  it("shows the recorded zoning for each multi-lot base lot when the existing channel carries it", () => {
    const profile = multiLotProfile();
    // Populate the recorded zoning per base lot on the EXISTING conflict-value
    // channel (open-schema `recorded_zoning` key). This is the shape the
    // out-of-scope live propagation would fill (see the producer report).
    (profile.conflicts[0].values[0] as unknown as Record<string, unknown>).recorded_zoning = "R6";
    (profile.conflicts[0].values[1] as unknown as Record<string, unknown>).recorded_zoning = "R7-2";
    render(<CondoResolutionRecords profile={profile} />);
    const zonings = screen.getAllByTestId("condo-base-lot-zoning");
    expect(zonings).toHaveLength(2);
    expect(zonings[0]).toHaveTextContent("recorded zoning: R6");
    expect(zonings[1]).toHaveTextContent("recorded zoning: R7-2");
    // Recorded zoning is a record beside the base lot, never a computed allowance.
    const multilot = screen.getByTestId("condo-resolution-multilot");
    expect(multilot.textContent ?? "").not.toMatch(/\d+\.\d+/);
  });

  it("explicitly preserves UNKNOWN zoning when the channel does not carry it — never fabricates a district", () => {
    render(<CondoResolutionRecords profile={multiLotProfile()} />);
    const zonings = screen.getAllByTestId("condo-base-lot-zoning");
    expect(zonings).toHaveLength(2);
    for (const zoning of zonings) {
      expect(zoning).toHaveTextContent("recorded zoning: not recorded (unknown)");
    }
  });
});

describe("PropertyOverview — multi-lot/unresolved condo withholds computed allowances (M5-T045, D-073-R006)", () => {
  it("control: a non-condo profile SHOWS the computed allowances (proves the fixtures are displayable)", () => {
    const { profile, evaluation, scenario } = displayableInputs();
    render(<PropertyOverview profile={profile} scenario={scenario} evaluation={evaluation} onInspect={vi.fn()} />);
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("1.50");
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("15,000 sq ft");
    expect(screen.queryByTestId("condo-resolution-records")).toBeNull();
  });

  it("a multi-lot condo withholds every computed allowance though the SAME scenario/evaluation would otherwise display them", () => {
    const { profile, evaluation, scenario } = displayableInputs();
    profile.conflicts = multiLotProfile().conflicts;
    render(<PropertyOverview profile={profile} scenario={scenario} evaluation={evaluation} onInspect={vi.fn()} />);
    // The scenario/evaluation are unchanged from the passing control, yet no
    // computed allowance is shown: the evaluated FAR and the draft cap fall back
    // to "Not calculated".
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated");
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
    // The records view explains the withhold; the base lots stay records only.
    expect(screen.getByTestId("condo-resolution-records")).toHaveTextContent("not a computed development allowance");
    expect(screen.getByTestId("condo-resolution-multilot")).toHaveTextContent("no computed allowance");
    expect(screen.getAllByTestId("condo-base-lot-record")).toHaveLength(2);
  });

  it("an unresolved condo withholds the computed allowances and explains the result honestly", () => {
    const { profile, evaluation, scenario } = displayableInputs();
    profile.reproducibility!.connector_notes = unresolvedProfile().reproducibility!.connector_notes;
    render(<PropertyOverview profile={profile} scenario={scenario} evaluation={evaluation} onInspect={vi.fn()} />);
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated");
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
    expect(screen.getByTestId("condo-resolution-note")).toHaveTextContent("matched no base-lot record");
  });

  it("a resolved single base lot STILL shows the computed allowances — the analysis ran on the substituted base lot", () => {
    const { profile, evaluation, scenario } = displayableInputs();
    profile.reproducibility!.connector_notes = resolvedSingleProfile().reproducibility!.connector_notes;
    render(<PropertyOverview profile={profile} scenario={scenario} evaluation={evaluation} onInspect={vi.fn()} />);
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("1.50");
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("15,000 sq ft");
    expect(screen.getByTestId("condo-resolution-note")).toHaveTextContent("resolved to the single recorded base lot");
  });

  it("a condo note with a MISSING outcome token withholds every computed allowance — fail-safe on a note the display cannot confirm ran on a single base lot", () => {
    const { profile, evaluation, scenario } = displayableInputs();
    // A condo_resolution note WITHOUT the machine outcome token (the legacy /
    // defensive shape condoResolutionNotes falls back on): the text still
    // renders, but the guard can no longer confirm a single-base-lot
    // substitution, so it must fail safe and withhold — the SAME scenario /
    // evaluation that display allowances in the control above now show none.
    profile.reproducibility!.connector_notes = [
      "condo_resolution: billing BBL 1003037501 mapped to a recorded base lot " +
        "(source nyc-dof-dtm-condo-soda, dataset(s) p8u6-a6it); no machine outcome token.",
    ];
    render(<PropertyOverview profile={profile} scenario={scenario} evaluation={evaluation} onInspect={vi.fn()} />);
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated");
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
    // The record still renders honestly; only the computed allowance is withheld.
    expect(screen.getByTestId("condo-resolution-note")).toHaveTextContent("mapped to a recorded base lot");
  });

  it("a condo note with an UNKNOWN outcome token withholds every computed allowance — fail-safe on a token this build does not recognise", () => {
    const { profile, evaluation, scenario } = displayableInputs();
    // A well-formed bracket carrying a token that is NOT resolved_single_base_lot
    // (e.g. a future backend outcome): the allow-list withholds, never open.
    profile.reproducibility!.connector_notes = [
      "condo_resolution: [resolved_multi_condo_v2] billing BBL 1003037501 produced a future outcome " +
        "this build does not recognise (source nyc-dof-dtm-condo-soda, dataset(s) p8u6-a6it).",
    ];
    render(<PropertyOverview profile={profile} scenario={scenario} evaluation={evaluation} onInspect={vi.fn()} />);
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated");
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
  });

  it("a condo note with a MALFORMED outcome bracket (unparseable) withholds every computed allowance", () => {
    const { profile, evaluation, scenario } = displayableInputs();
    // A bracket the outcome regex cannot parse (spaces / non [a-z_] content) ->
    // outcome null -> fail-safe withhold, exactly like a missing token.
    profile.reproducibility!.connector_notes = [
      "condo_resolution: [resolved single base lot] billing BBL 1003037501 " +
        "carries a malformed outcome token (source nyc-dof-dtm-condo-soda).",
    ];
    render(<PropertyOverview profile={profile} scenario={scenario} evaluation={evaluation} onInspect={vi.fn()} />);
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated");
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
  });
});
