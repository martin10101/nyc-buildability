import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { ConflictsSection } from "@/components/property/ConflictsSection";
import { MissingInputsSection } from "@/components/property/MissingInputsSection";
import { ProvenanceDisclosure } from "@/components/property/ProvenanceDisclosure";
import { baseProfile } from "@/test-support/fixtures";
import type { Conflict, Reproducibility, SourceFact } from "@/lib/contract";

afterEach(cleanup);

/** A minimal, contract-shaped SourceFact record for standalone rendering. */
function sourceFactRecord(overrides: Partial<SourceFact> = {}): SourceFact {
  return {
    provenance_id: "prov-1",
    source_id: "nyc-dcp-pluto-soda",
    original_field_name: "lotarea",
    original_value: "2500",
    normalized_value: 2500,
    retrieved_at: "2026-07-16T00:00:00Z",
    dataset_version: "26v1",
    effective_date: null,
    bbl: "1000010010",
    confidence: 1,
    user_confirmed_or_overridden: "none",
    conflict_status: "none",
    ...overrides,
  } as SourceFact;
}

function reproducibility(overrides: Partial<Reproducibility> = {}): Reproducibility {
  return {
    correlation_id: "corr-1",
    source_id: "nyc-dcp-pluto-soda",
    dataset_id: "64uk-42ks",
    dataset_version: "26v1",
    request_url: "https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=1000010010",
    retrieved_at: "2026-07-16T00:00:00Z",
    record_count: 1,
    drift_signals: [],
    connector_notes: [],
    coverage_policy: "pluto-authoritative",
    ...overrides,
  } as Reproducibility;
}

describe("ConflictsSection (S1/S6)", () => {
  it("shows every conflicting value WITH its source and the unresolved label", () => {
    // SYNTHETIC conflict entry shaped exactly like the accepted M1-T005
    // builder emits for a borocode disagreement (services/api builder
    // _conflicts()); labeled synthetic, no official value invented.
    // `derivation` is an OPEN-schema key the builder emits (not documented
    // in the generated conflict-value type) — the cast mirrors how it
    // arrives over the wire; the component reads it via the runtime
    // narrowing helper in src/lib/contract.ts.
    const conflicts = [
      {
        field: "borocode",
        values: [
          {
            source_id: "nyc-dcp-pluto-soda",
            value: "1",
            derivation: "derived from the canonical BBL digits",
          },
          {
            source_id: "nyc-dcp-pluto-soda",
            value: "3",
            derivation: "record field 'borocode' verbatim",
          },
        ],
        resolution: "unresolved",
      },
    ] as unknown as Conflict[];
    render(<ConflictsSection conflicts={conflicts} />);
    expect(screen.getByText(/resolution: unresolved/)).toBeInTheDocument();
    expect(screen.getByText("1")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getAllByText(/nyc-dcp-pluto-soda/).length).toBe(2);
    expect(screen.getByText(/derived from the canonical BBL digits/)).toBeInTheDocument();
    expect(screen.getByText(/record field 'borocode' verbatim/)).toBeInTheDocument();
    expect(
      screen.getByText(/Nothing has been resolved automatically/),
    ).toBeInTheDocument();
  });

  it("renders an explicit empty state instead of hiding the section", () => {
    render(<ConflictsSection conflicts={[]} />);
    expect(
      screen.getByText(/No cross-source conflicts were detected/),
    ).toBeInTheDocument();
  });
});

describe("MissingInputsSection (S6 / D3 policy + M2-T002 D1/D4)", () => {
  it("shows the total, surfaces relevant fields WITH human labels, and reveals the grouped rest via the count toggle", () => {
    const entries = baseProfile().missing_inputs;
    render(<MissingInputsSection entries={entries} />);

    // Total always visible in the heading.
    expect(
      screen.getByRole("heading", { name: /Missing official inputs \(24\)/ }),
    ).toBeInTheDocument();

    // Feasibility-relevant entries surfaced immediately, labeled (D1):
    // no raw PLUTO column name reaches the user.
    expect(screen.getByText("Commercial overlay 1")).toBeInTheDocument();
    expect(
      screen.getByText("Mandatory Inclusionary Housing option 1"),
    ).toBeInTheDocument();
    expect(screen.queryByText("overlay1")).toBeNull();
    expect(screen.queryByText("mih_opt1")).toBeNull();

    // Administrative entries hidden behind an EXPLICIT count toggle.
    expect(screen.queryByText("Input data vintage (base map)")).toBeNull();
    const toggle = screen.getByRole("button", { name: /more missing fields/ });
    expect(toggle).toHaveAttribute("aria-expanded", "false");
    expect(toggle.textContent).toMatch(/\d+ more missing fields/);

    fireEvent.click(toggle);
    expect(screen.getByText("Input data vintage (base map)")).toBeInTheDocument();
    expect(screen.getByText("Input data vintage (DCAS)")).toBeInTheDocument();
    expect(screen.queryByText("basempdate")).toBeNull();
    expect(
      screen.getByRole("button", { name: /Hide \d+ additional missing fields/ }),
    ).toHaveAttribute("aria-expanded", "true");
  });

  it("D4: states the shared boilerplate reason ONCE and keeps per-field exceptions inline", () => {
    const shared =
      "column absent from the SODA record (null-omission semantics): " +
      "the value is unknown for this tax lot and is never fabricated";
    const entries = baseProfile().missing_inputs.map((entry) => ({ ...entry }));
    // Give one entry a DIFFERENT reason (per-field exception).
    const exception = entries.find((entry) => entry.field === "overlay1");
    if (!exception) throw new Error("fixture is missing overlay1");
    exception.reason = "numfloors_not_available: official dictionary p.28 rule";
    render(<MissingInputsSection entries={entries} />);

    // Shared reason appears exactly once, in the section-level note.
    expect(screen.getByTestId("shared-missing-reason")).toHaveTextContent(
      "null-omission semantics",
    );
    expect(screen.getAllByText(new RegExp("null-omission semantics")).length).toBe(1);

    // The exception's own reason stays visible inline.
    expect(screen.getByText(/official dictionary p\.28 rule/)).toBeInTheDocument();
    expect(entries.filter((entry) => entry.reason === shared).length).toBeGreaterThan(0);
  });
});

describe("ProvenanceDisclosure — safe outbound source link (M5-T025, D-056-R001)", () => {
  it("valid dataset_id: renders a clickable link with the EXACT expected href, target=_blank, rel=noopener noreferrer", () => {
    render(
      <ProvenanceDisclosure
        records={[sourceFactRecord()]}
        reproducibility={reproducibility({ dataset_id: "64uk-42ks" })}
        label="Source for Lot area"
      />,
    );
    fireEvent.click(screen.getByText("Source for Lot area"));
    const link = screen.getByTestId("provenance-source-link");
    expect(link).toHaveAttribute("href", "https://data.cityofnewyork.us/d/64uk-42ks");
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", "noopener noreferrer");
    expect(link).toHaveTextContent("64uk-42ks");
  });

  it("invalid dataset_id: honest text, no anchor", () => {
    render(
      <ProvenanceDisclosure
        records={[sourceFactRecord()]}
        reproducibility={reproducibility({ dataset_id: "not-a-valid-id" })}
        label="Source for Lot area"
      />,
    );
    fireEvent.click(screen.getByText("Source for Lot area"));
    expect(screen.queryByTestId("provenance-source-link")).toBeNull();
    expect(screen.getByTestId("provenance-dataset-id")).toHaveTextContent(
      "not-a-valid-id",
    );
  });

  it("absent reproducibility: no dataset-id row at all, no anchor (existing behavior preserved)", () => {
    render(
      <ProvenanceDisclosure records={[sourceFactRecord()]} label="Source for Lot area" />,
    );
    fireEvent.click(screen.getByText("Source for Lot area"));
    expect(screen.queryByTestId("provenance-source-link")).toBeNull();
    expect(screen.queryByTestId("provenance-dataset-id")).toBeNull();
  });

  it("NEGATIVE: a hostile request_url NEVER appears in any href, regardless of its value", () => {
    const hostile = "https://evil.example.com/steal?x=<script>alert(1)</script>";
    render(
      <ProvenanceDisclosure
        records={[sourceFactRecord()]}
        reproducibility={reproducibility({
          dataset_id: "not-a-valid-id",
          request_url: hostile,
        })}
        label="Source for Lot area"
      />,
    );
    fireEvent.click(screen.getByText("Source for Lot area"));
    // No anchor exists at all in this invalid-id case...
    expect(screen.queryByTestId("provenance-source-link")).toBeNull();
    cleanup();
    // ...and even generally: no href anywhere in the rendered tree contains
    // the hostile request_url content, no matter what value it carries.
    const { container } = render(
      <ProvenanceDisclosure
        records={[sourceFactRecord()]}
        reproducibility={reproducibility({
          dataset_id: "64uk-42ks",
          request_url: hostile,
        })}
        label="Source for Lot area 2"
      />,
    );
    fireEvent.click(screen.getByText("Source for Lot area 2"));
    const hrefs = Array.from(container.querySelectorAll("a")).map((a) =>
      a.getAttribute("href"),
    );
    for (const href of hrefs) {
      expect(href ?? "").not.toContain("evil.example.com");
    }
    // The valid dataset id link is still exactly the constant-prefix href.
    expect(screen.getByTestId("provenance-source-link")).toHaveAttribute(
      "href",
      "https://data.cityofnewyork.us/d/64uk-42ks",
    );
  });
});

describe("ProvenanceDisclosure — ZoLa-first human-readable lot link (M5-T032, D-064-R005)", () => {
  const ZOLA_PREFIX = "https://zola.planning.nyc.gov/bbl/";

  it("valid PLUTO fact: the ZoLa lot page is the PRIMARY link and the raw PLUTO JSON record is demoted to a clearly secondary link", () => {
    const { container } = render(
      <ProvenanceDisclosure
        records={[sourceFactRecord()]}
        reproducibility={reproducibility({ dataset_id: "64uk-42ks" })}
        label="Source for Lot area"
      />,
    );
    fireEvent.click(screen.getByText("Source for Lot area"));
    const zola = screen.getByTestId("zola-lot-link");
    expect(zola).toHaveAttribute("href", `${ZOLA_PREFIX}1000010010`);
    expect(zola).toHaveAttribute("target", "_blank");
    expect(zola).toHaveAttribute("rel", "noopener noreferrer");
    // The human-readable primary link is NOT the demoted-secondary style…
    expect(zola).not.toHaveClass("section-note");
    // …while the raw PLUTO JSON record is present but demoted (secondary).
    const raw = screen.getByRole("link", { name: "Current PLUTO record (JSON)" });
    expect(raw).toHaveAttribute(
      "href",
      "https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=1000010010",
    );
    expect(raw).toHaveClass("section-note");
    // Primary first: ZoLa renders before the raw record in the DOM.
    const links = Array.from(container.querySelectorAll("a"));
    expect(links.indexOf(zola)).toBeLessThan(links.indexOf(raw));
  });

  it("a same-source dataset conflict closes BOTH the ZoLa link and the raw record (honest absence), keeping the fact's own About link", () => {
    render(
      <ProvenanceDisclosure
        records={[sourceFactRecord({ dataset_id: "abcd-1234" })]}
        reproducibility={reproducibility({ dataset_id: "64uk-42ks" })}
        label="Source for Lot area"
      />,
    );
    fireEvent.click(screen.getByText("Source for Lot area"));
    expect(screen.queryByTestId("zola-lot-link")).toBeNull();
    expect(
      screen.queryByRole("link", { name: "Current PLUTO record (JSON)" }),
    ).toBeNull();
    // The fact's own dataset About link is preserved (its independent metadata).
    expect(screen.getByTestId("provenance-source-link")).toHaveAttribute(
      "href",
      "https://data.cityofnewyork.us/d/abcd-1234",
    );
  });

  it("a non-PLUTO source renders no ZoLa link and no raw record (no borrowed lot identity)", () => {
    render(
      <ProvenanceDisclosure
        records={[sourceFactRecord({ source_id: "nyc-dob-now" })]}
        reproducibility={reproducibility()}
        label="Source for Lot area"
      />,
    );
    fireEvent.click(screen.getByText("Source for Lot area"));
    expect(screen.queryByTestId("zola-lot-link")).toBeNull();
    expect(
      screen.queryByRole("link", { name: "Current PLUTO record (JSON)" }),
    ).toBeNull();
  });

  it("a BBL that fails canonical validation renders no ZoLa link even for a PLUTO fact", () => {
    render(
      <ProvenanceDisclosure
        records={[sourceFactRecord({ bbl: "12345" })]}
        reproducibility={reproducibility({ dataset_id: "64uk-42ks" })}
        label="Source for Lot area"
      />,
    );
    fireEvent.click(screen.getByText("Source for Lot area"));
    expect(screen.queryByTestId("zola-lot-link")).toBeNull();
    expect(
      screen.queryByRole("link", { name: "Current PLUTO record (JSON)" }),
    ).toBeNull();
  });
});
