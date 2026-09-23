import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { readFileSync } from "node:fs";
import { MaxEnvelopePanel } from "../MaxEnvelopePanel";
import type { MaxEnvelopeRequest } from "@/lib/architect/max-envelope-api";

/**
 * Task M5-T070 (D-082-R003 + D-083), Preliminary-development-limits panel. The
 * answer-first surface renders the computed envelope FIRST; the D-083 claim-class
 * vocabulary is binding (heading "Preliminary development limits"; the emitted
 * candidate is a "Generated building option", the ONLY building-shaped claim; no
 * unrestricted green while any gap/advisory is present; never an unqualified
 * "maximum allowed building"). The suite is mutation-sensitive on AS-3 and proves
 * additive degradation (AS-6) and one-action adoption (AS-4).
 */

const DISCLOSURE =
  "These are rules-derived preliminary development limits for this lot — not a maximum permitted building.";

function bindingDimension(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    dimension_id: "max_far_floor_area",
    family: "floor_area",
    direction: "max",
    unit: "sq_ft",
    label: "Maximum floor area",
    saturating: false,
    binding_value: 20000,
    binding_rule_id: "zr-far-r6",
    binding_rule_version: "2024.1",
    coverage_status: "covered",
    out_competed_rule_ids: ["zr-far-r6-alt"],
    rule_citations: [{ section: "23-142" }],
    gap_reason: null,
    conflict_advisory: null,
    detail: "The floor-area ratio ceiling for the underlying district.",
    ...overrides,
  };
}

function gapDimension(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    dimension_id: "max_height_ft",
    family: "height",
    direction: "max",
    unit: "ft",
    label: "Maximum height",
    saturating: false,
    binding_value: null,
    binding_rule_id: null,
    binding_rule_version: null,
    coverage_status: "uncovered",
    out_competed_rule_ids: [],
    rule_citations: [],
    // [ORCH-CORRECTED per G3-F3/G4-F3] a REAL EnvelopeGapReason token, never prose.
    gap_reason: "allowance_unresolved",
    conflict_advisory: null,
    detail: "The height ceiling depends on a street width this lot has not resolved.",
    ...overrides,
  };
}

function envelopeBody(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    massing_class: "rectangle_prism",
    label: "BBL 1000010010 preliminary development limits",
    disclosure: DISCLOSURE,
    dimensions: [bindingDimension(), gapDimension()],
    candidate: {
      outline: { srid: 2263, vertices: [[1000000, 200000], [1000100, 200000], [1000100, 200050], [1000000, 200050]] },
      levels: [{ level_index: 0, floor_count: 3, floor_to_floor_ft: 10 }],
      exterior_walls: [{ id: "W-S", start_vertex_index: 0, end_vertex_index: 1 }],
    },
    candidate_notes: ["Fitted to the recorded lot area."],
    candidate_placement: { status: "fitted", detail: "fitted and contained", contained: true },
    candidate_consistency: { consistent: true },
    summary: { binding: 1, gap: 1, saturating_binding: 0, total: 2 },
    rule_input_bindings: {},
    unmapped_lot_facts: [],
    correlation_id: "cid",
    ...overrides,
  };
}

function completeBody(): Record<string, unknown> {
  return envelopeBody({
    dimensions: [
      bindingDimension(),
      bindingDimension({ dimension_id: "max_height_ft", label: "Maximum height", unit: "ft", binding_value: 60 }),
    ],
    summary: { binding: 2, gap: 0, saturating_binding: 0, total: 2 },
  });
}

function response(body: unknown, status = 200): Response {
  const text = JSON.stringify(body);
  return new Response(text, {
    status,
    headers: {
      "Content-Type": "application/json",
      "Content-Length": String(new TextEncoder().encode(text).length),
      "X-Correlation-ID": "cid",
    },
  });
}

function stub(res: Response): typeof fetch {
  return (async () => res) as typeof fetch;
}

const REQUEST: MaxEnvelopeRequest = {
  lot: { area_sq_ft: 8000, area_provenance: { source_id: "architect_surface_lot_context" }, lot_line_segments: [], street_lines: [] },
  lot_rule_facts: { zoning_district: "R6" },
  label: "BBL 1000010010 preliminary development limits",
};

afterEach(cleanup);

describe("MaxEnvelopePanel — answer-first limits (AS-1) + claim-class vocabulary (AS-2)", () => {
  it("renders the heading class, the verbatim server disclosure, and per-dimension binding provenance", async () => {
    render(<MaxEnvelopePanel request={REQUEST} fetchImpl={stub(response(envelopeBody()))} />);
    expect(await screen.findByRole("heading", { name: "Preliminary development limits" })).toBeInTheDocument();
    expect(await screen.findByTestId("envelope-disclosure")).toHaveTextContent(DISCLOSURE);

    expect(screen.getByTestId("envelope-value-max_far_floor_area")).toHaveTextContent("20000 sq_ft");
    expect(screen.getByTestId("envelope-binding-max_far_floor_area")).toHaveTextContent("zr-far-r6");
    expect(screen.getByTestId("envelope-binding-max_far_floor_area")).toHaveTextContent("v2024.1");
    expect(screen.getByTestId("envelope-binding-max_far_floor_area")).toHaveTextContent("1 rule out-competed");
  });

  it("shows a gap dimension by its typed reason instead of a value (AS-1)", async () => {
    render(<MaxEnvelopePanel request={REQUEST} fetchImpl={stub(response(envelopeBody()))} />);
    const gap = await screen.findByTestId("envelope-gap-max_height_ft");
    expect(gap).toHaveTextContent("Could not check");
    // The headline maps the server token to plain copy; the raw token never leads.
    expect(gap).toHaveTextContent("the governing allowance could not be resolved");
    expect(gap).not.toHaveTextContent("allowance_unresolved");
    expect(screen.queryByTestId("envelope-value-max_height_ft")).toBeNull();
  });

  it("renders the ONE building-shaped claim as a 'Generated building option', never a permitted building (AS-2)", async () => {
    render(<MaxEnvelopePanel request={REQUEST} fetchImpl={stub(response(envelopeBody()))} />);
    const section = await screen.findByTestId("generated-building-option");
    expect(section).toHaveTextContent("Generated building option");
    expect(section).toHaveTextContent("never combined into one building");
  });

  it("surfaces a conflict advisory with both competing rule ids, surfaced-never-resolved (AS-1)", async () => {
    const body = envelopeBody({
      dimensions: [
        bindingDimension({ conflict_advisory: { competing_rule_ids: ["zr-far-r6", "zr-far-c4-3"], note: "overlap" } }),
        gapDimension(),
      ],
    });
    render(<MaxEnvelopePanel request={REQUEST} fetchImpl={stub(response(body))} />);
    const advisory = await screen.findByTestId("envelope-advisory-max_far_floor_area");
    expect(advisory).toHaveTextContent("not resolved here");
    expect(advisory).toHaveTextContent("zr-far-r6, zr-far-c4-3");
  });
});

describe("MaxEnvelopePanel — no unrestricted green (AS-3, D-083-R004, mutation-sensitive)", () => {
  it("stays visibly INCOMPLETE while a gap is present", async () => {
    render(<MaxEnvelopePanel request={REQUEST} fetchImpl={stub(response(envelopeBody()))} />);
    const aggregate = await screen.findByTestId("envelope-aggregate");
    expect(aggregate).toHaveAttribute("data-complete", "false");
    expect(aggregate).toHaveTextContent("Could not check 1 of 2");
    expect(aggregate).toHaveTextContent("incomplete");
  });

  it("MUTATION: flipping the gap row to binding flips the aggregate to a checked (non-green-unrestricted) state", async () => {
    render(<MaxEnvelopePanel request={REQUEST} fetchImpl={stub(response(completeBody()))} />);
    const aggregate = await screen.findByTestId("envelope-aggregate");
    expect(aggregate).toHaveAttribute("data-complete", "true");
    expect(aggregate).toHaveTextContent("All 2 preliminary development limits were checked");
    expect(aggregate).toHaveTextContent("requiring professional review");
  });
});

describe("MaxEnvelopePanel — one-action adoption (AS-4)", () => {
  it("adopts the Generated building option through the ONE draft model, labeled proposed", async () => {
    const onAdopt = vi.fn();
    render(<MaxEnvelopePanel request={REQUEST} fetchImpl={stub(response(envelopeBody()))} onAdopt={onAdopt} />);
    const adopt = await screen.findByTestId("adopt-candidate");
    fireEvent.click(adopt);
    expect(onAdopt).toHaveBeenCalledTimes(1);
    const draft = onAdopt.mock.calls[0][0];
    expect(draft.scenario_label).toBe("Generated building option");
    expect(draft.vertices[0]).toEqual({ x: 1000000, y: 200000 });
    expect(draft.zoning_district).toBe("R6");
    expect(draft.area_provenance_note).toContain("proposed input, not a city record");
  });

  it("offers NO adopt action when the candidate was not a contained fit (adoption impossible)", async () => {
    // [ORCH-CORRECTED per G3-F1/G4-F2] a REAL CandidatePlacementStatus value.
    const body = envelopeBody({
      candidate_placement: { status: "footprint_exceeds_lot", detail: "the lot rectangle is too small", contained: false },
    });
    render(<MaxEnvelopePanel request={REQUEST} fetchImpl={stub(response(body))} />);
    expect(await screen.findByTestId("candidate-unavailable")).toHaveTextContent("No building option can be adopted");
    expect(screen.queryByTestId("adopt-candidate")).toBeNull();
  });

  it("renders the PRODUCTION-REACHABLE placement state honestly: lot_geometry_unsupported with no candidate (G4-F1)", async () => {
    // [ORCH-CORRECTED per G3-F2/G4-F1] With the geometry-free request this client
    // actually sends, the server returns lot_geometry_unsupported and NO candidate
    // (max_envelope.py:632-637 / :795-800). This spec pins that real state: the
    // honest card leads with the server's own prose and no adopt affordance exists,
    // so the mount seam cannot silently ship a permanently dead adoption button.
    const SERVER_DETAIL =
      "no lot-line geometry was supplied, so the footprint cannot be fitted to the lot; " +
      "no candidate is emitted (never a fixed-anchor schematic)";
    const body = envelopeBody({
      candidate: null,
      candidate_placement: { status: "lot_geometry_unsupported", detail: SERVER_DETAIL, contained: false },
    });
    render(<MaxEnvelopePanel request={REQUEST} fetchImpl={stub(response(body))} />);
    const card = await screen.findByTestId("candidate-unavailable");
    expect(card).toHaveTextContent("No building option can be adopted");
    expect(card).toHaveTextContent("no lot-line geometry was supplied");
    expect(screen.queryByTestId("adopt-candidate")).toBeNull();
  });
});

describe("MaxEnvelopePanel — additive degradation (AS-6): never a dead surface, never a fabricated limit", () => {
  it("shows a typed 'cannot compute' card (never a limit) when there is no request context", () => {
    render(<MaxEnvelopePanel request={null} fetchImpl={stub(response(envelopeBody()))} />);
    expect(screen.getByTestId("envelope-no-context")).toHaveTextContent("no usable lot area is recorded");
    expect(screen.queryByTestId("envelope-disclosure")).toBeNull();
  });

  it("degrades to a typed, RETRYABLE failure card on a server error (nothing fabricated)", async () => {
    render(<MaxEnvelopePanel request={REQUEST} fetchImpl={stub(response({ state: "internal_error", message: "boom" }, 500))} />);
    const failure = await screen.findByTestId("envelope-failure");
    expect(failure).toHaveTextContent("unavailable right now");
    expect(failure).toHaveTextContent("Nothing was fabricated");
    expect(screen.getByTestId("envelope-retry")).toBeInTheDocument();
  });

  it("degrades WITHOUT a retry when the feature is unavailable (a result, not a fault)", async () => {
    render(<MaxEnvelopePanel request={REQUEST} fetchImpl={stub(response({ detail: "Not Found" }, 404))} />);
    expect(await screen.findByTestId("envelope-failure")).toBeInTheDocument();
    expect(screen.queryByTestId("envelope-retry")).toBeNull();
  });
});

describe("MaxEnvelopePanel — claim-class copy wall (AS-2, source grep across the changed web files)", () => {
  it("no changed panel/lib source asserts an unqualified 'maximum allowed building' or 'demonstrated maximum'", () => {
    const files = [
      "../MaxEnvelopePanel.tsx",
      "../../../lib/architect/max-envelope-api.ts",
      "../../../lib/architect/proposal-draft.ts",
      // [ORCH-CORRECTED per G3-F4/G4-A1] every changed production file with
      // analyst-facing copy is inside the wall, per AS-2's own wording.
      "../ArchitectEntry.tsx",
      "../ProposalEditor.tsx",
    ];
    for (const rel of files) {
      const source = readFileSync(new URL(rel, import.meta.url), "utf8").toLowerCase();
      expect(source, rel).not.toContain("maximum allowed building");
      expect(source, rel).not.toContain("demonstrated maximum");
    }
  });
});
