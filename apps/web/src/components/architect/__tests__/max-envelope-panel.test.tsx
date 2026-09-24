import { afterEach, describe, expect, it, vi } from "vitest";
import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { readFileSync } from "node:fs";
import { GAP_REASON_COPY, MaxEnvelopePanel, gapReasonCopy } from "../MaxEnvelopePanel";
import { ENVELOPE_GAP_REASONS, type MaxEnvelopeRequest } from "@/lib/architect/max-envelope-api";

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
    // [ORCH-CORRECTED per G4 micro-delta] AS-1's "instead of a value" clause asserts
    // in ITS OWN test (restored after the SEC-F1 insertion displaced it).
    expect(screen.queryByTestId("envelope-value-max_height_ft")).toBeNull();
  });

  it("a prototype-chain token like __proto__ renders as its literal text, never a crash (SEC F1)", async () => {
    // [ORCH-CORRECTED per SEC F1] Object.prototype keys must not resolve through the
    // copy map: "__proto__" would return an object (React 19 throws, killing the whole
    // property page through the route error boundary) and "constructor" a function
    // (silently blank reason). The own-property guard renders the literal token instead.
    const body = envelopeBody({
      dimensions: [bindingDimension(), gapDimension({ gap_reason: "__proto__" })],
    });
    render(<MaxEnvelopePanel request={REQUEST} fetchImpl={stub(response(body))} />);
    const gap = await screen.findByTestId("envelope-gap-max_height_ft");
    expect(gap).toHaveTextContent("Could not check — __proto__");
    cleanup();

    // "constructor" resolves to a function through the prototype chain — React
    // renders a function child as nothing, silently blanking the reason. The
    // guard renders the literal token instead.
    const body2 = envelopeBody({
      dimensions: [bindingDimension(), gapDimension({ gap_reason: "constructor" })],
    });
    render(<MaxEnvelopePanel request={REQUEST} fetchImpl={stub(response(body2))} />);
    const gap2 = await screen.findByTestId("envelope-gap-max_height_ft");
    expect(gap2).toHaveTextContent("Could not check — constructor");
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

/**
 * DB-050(l): the claim-class copy wall must catch case/hyphen/space variants of the
 * banned claims (e.g. "Maximum-allowed building"), not only the exact lowercase
 * phrase. It scans RENDERED copy, so comments (which legitimately DISCUSS the banned
 * phrases to say the copy never uses them — MaxEnvelopePanel.tsx:33,
 * max-envelope-api.ts:576) are stripped first; otherwise a negation comment would
 * false-positive. The strengthened wall still passes on the accepted copy.
 */
function strippedSource(source: string): string {
  return source
    .replace(/\/\*[\s\S]*?\*\//g, " ") // block / JSDoc comments
    .replace(/\/\/[^\n]*/g, " "); // line comments
}
function containsBannedClaim(source: string): boolean {
  // Strip comments, lowercase, then collapse runs of hyphens/whitespace to one space,
  // so "Maximum-allowed  building" and "maximum allowed building" both normalize to a
  // single canonical form.
  const normalized = strippedSource(source).toLowerCase().replace(/[-\s]+/g, " ");
  return (
    normalized.includes("maximum allowed building") || normalized.includes("demonstrated maximum")
  );
}

describe("MaxEnvelopePanel — claim-class copy wall (AS-2/AS-3, DB-050(l): case/hyphen/space-proof)", () => {
  it("no changed panel/lib RENDERED copy asserts an unqualified 'maximum allowed building' / 'demonstrated maximum'", () => {
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
      const source = readFileSync(new URL(rel, import.meta.url), "utf8");
      expect(containsBannedClaim(source), rel).toBe(false);
    }
  });

  it("HAS TEETH: rejects injected case/hyphen/space variants and comment-free banned copy", () => {
    // Case + spacing variants and the hyphenated form the old exact-match wall missed.
    expect(containsBannedClaim("<p>This is the Maximum-allowed building for this lot</p>")).toBe(true);
    expect(containsBannedClaim("MAXIMUM ALLOWED BUILDING")).toBe(true);
    expect(containsBannedClaim("the demonstrated   maximum envelope")).toBe(true);
    expect(containsBannedClaim("the demonstrated-maximum envelope")).toBe(true);
  });

  it("does NOT flag the accepted claim-class copy, or the phrases when they appear only in comments", () => {
    // The accepted, honest copy stays clean.
    expect(containsBannedClaim("Preliminary development limits")).toBe(false);
    expect(containsBannedClaim("Generated building option")).toBe(false);
    expect(containsBannedClaim("not a maximum permitted building")).toBe(false);
    // A negation ABOUT the banned phrase, in a comment, is not rendered copy — exempt.
    expect(containsBannedClaim("// copy never asserts a maximum-allowed-building claim")).toBe(false);
    expect(containsBannedClaim("/** never a maximum allowed building */")).toBe(false);
  });
});

describe("MaxEnvelopePanel — gap-reason copy map (AS-3, DB-050(m): exhaustive over the server union)", () => {
  it("maps EVERY server gap-reason token to plain analyst copy (never the raw token)", () => {
    for (const token of ENVELOPE_GAP_REASONS) {
      const copy = GAP_REASON_COPY[token];
      expect(copy, token).toBeTruthy();
      // The analyst copy is prose, never the raw snake_case machine token.
      expect(copy, token).not.toBe(token);
      expect(copy, token).not.toContain("_");
      // gapReasonCopy resolves the known token to that same copy.
      expect(gapReasonCopy(token)).toBe(copy);
    }
    // Every documented key of the copy map is a known server token (no stray copy).
    expect(Object.keys(GAP_REASON_COPY).sort()).toEqual([...ENVELOPE_GAP_REASONS].sort());
  });

  it("renders an UNKNOWN runtime token verbatim (fail-honest) and a missing reason as a stated fallback", () => {
    expect(gapReasonCopy("some_unmapped_token")).toBe("some_unmapped_token");
    expect(gapReasonCopy(null)).toBe("the reason was not stated");
    expect(gapReasonCopy("")).toBe("the reason was not stated");
  });
});

describe("MaxEnvelopePanel — binding-or-gap XOR fail-closed (AS-2, DB-050(d), mutation-sensitive)", () => {
  it("a row carrying BOTH binding_value and gap_reason NEVER renders a value; aggregate stays incomplete", async () => {
    const body = envelopeBody({
      dimensions: [
        // binding_value 20000 AND gap_reason set: a server XOR violation.
        bindingDimension({ gap_reason: "allowance_unresolved" }),
        bindingDimension({ dimension_id: "max_height_ft", label: "Maximum height", unit: "ft", binding_value: 60 }),
      ],
      summary: { binding: 2, gap: 0, saturating_binding: 0, total: 2 },
    });
    render(<MaxEnvelopePanel request={REQUEST} fetchImpl={stub(response(body))} />);
    // The violating row surfaces as a typed contract failure, NEVER a limit value.
    expect(await screen.findByTestId("envelope-contract-violation-max_far_floor_area")).toHaveTextContent(
      "broke the binding-or-gap data contract",
    );
    expect(screen.queryByTestId("envelope-value-max_far_floor_area")).toBeNull();
    expect(screen.getByTestId("envelope-contract-detail-max_far_floor_area")).toHaveTextContent("returned both");
    // The aggregate stays visibly INCOMPLETE even though the server's gap count is 0.
    const aggregate = screen.getByTestId("envelope-aggregate");
    expect(aggregate).toHaveAttribute("data-complete", "false");
    expect(aggregate).toHaveTextContent("binding-or-gap data contract");
  });

  it("a row carrying NEITHER binding_value nor gap_reason NEVER renders 'null' as a value", async () => {
    const body = envelopeBody({
      dimensions: [
        gapDimension({ gap_reason: null }), // binding_value null AND gap_reason null: NEITHER
        bindingDimension({ dimension_id: "max_far_floor_area", binding_value: 20000 }),
      ],
      summary: { binding: 1, gap: 0, saturating_binding: 0, total: 2 },
    });
    render(<MaxEnvelopePanel request={REQUEST} fetchImpl={stub(response(body))} />);
    const violation = await screen.findByTestId("envelope-contract-violation-max_height_ft");
    expect(violation).toBeInTheDocument();
    expect(screen.queryByTestId("envelope-value-max_height_ft")).toBeNull();
    expect(screen.getByTestId("envelope-contract-detail-max_height_ft")).toHaveTextContent("returned neither");
    expect(screen.getByTestId("envelope-aggregate")).toHaveAttribute("data-complete", "false");
  });
});

describe("MaxEnvelopePanel — loading / retry / superseded (AS-1, DB-050(c)/(i))", () => {
  it("shows the loading card (role=status, aria-busy) while the request is in flight", async () => {
    // Stays pending until its signal aborts (on unmount), so the panel holds the
    // loading card during the test and the client's timeout timer is cleared cleanly
    // on teardown (no dangling timer).
    const fetchImpl = ((_url: string, init?: RequestInit) =>
      new Promise<Response>((_resolve, reject) => {
        init?.signal?.addEventListener("abort", () => reject(new DOMException("aborted", "AbortError")));
      })) as unknown as typeof fetch;
    render(<MaxEnvelopePanel request={REQUEST} fetchImpl={fetchImpl} />);
    const loading = await screen.findByTestId("envelope-loading");
    expect(loading).toHaveAttribute("aria-busy", "true");
    expect(loading).toHaveTextContent("Computing the preliminary development limits");
    expect(screen.queryByTestId("envelope-disclosure")).toBeNull();
    expect(screen.queryByTestId("envelope-failure")).toBeNull();
  });

  it("Retry issues EXACTLY ONE new request per click (the reloadNonce guard)", async () => {
    let calls = 0;
    const fetchImpl = (async () => {
      calls += 1;
      return response({ state: "internal_error", message: "boom" }, 500);
    }) as unknown as typeof fetch;
    render(<MaxEnvelopePanel request={REQUEST} fetchImpl={fetchImpl} />);
    const retry = await screen.findByTestId("envelope-retry");
    expect(calls).toBe(1); // the initial request
    fireEvent.click(retry);
    await screen.findByTestId("envelope-retry");
    expect(calls).toBe(2); // exactly one MORE
    fireEvent.click(await screen.findByTestId("envelope-retry"));
    await screen.findByTestId("envelope-retry");
    expect(calls).toBe(3); // one more still — never a double-fetch per click
  });

  it("a superseded request never overwrites the latest state, and no reasonless card appears (superseded guard)", async () => {
    let resolveFirst: (r: Response) => void = () => {};
    const first = new Promise<Response>((res) => {
      resolveFirst = res;
    });
    const queued: Array<Promise<Response>> = [first, Promise.resolve(response(completeBody()))];
    let i = 0;
    const fetchImpl = (async () => queued[i++]) as unknown as typeof fetch;
    const { rerender } = render(<MaxEnvelopePanel request={REQUEST} fetchImpl={fetchImpl} />);
    // Supersede the still-pending first request with a second that resolves complete.
    rerender(<MaxEnvelopePanel request={{ ...REQUEST, label: "second request" }} fetchImpl={fetchImpl} />);
    const aggregate = await screen.findByTestId("envelope-aggregate");
    expect(aggregate).toHaveAttribute("data-complete", "true");
    // Now the STALE first request resolves to a 500 failure — it must NOT overwrite
    // the latest (complete) state, and must not flash a reasonless failure card.
    await act(async () => {
      resolveFirst(response({ state: "internal_error", message: "boom" }, 500));
      // Flush the stale request's remaining hops (json parse + classify + the
      // panel's .then); the superseded guard drops it, so no state update occurs.
      await new Promise((r) => setTimeout(r, 0));
    });
    expect(screen.queryByTestId("envelope-failure")).toBeNull();
    expect(screen.getByTestId("envelope-aggregate")).toHaveAttribute("data-complete", "true");
  });

  it("the failure card always carries a NON-EMPTY reason (never a reasonless card, DB-050(c))", async () => {
    render(<MaxEnvelopePanel request={REQUEST} fetchImpl={stub(response({ state: "internal_error", message: "boom" }, 500))} />);
    const failure = await screen.findByTestId("envelope-failure");
    const reason = failure.querySelector<HTMLParagraphElement>("p");
    expect(reason).not.toBeNull();
    expect(reason!.textContent?.trim().length ?? 0).toBeGreaterThan(0);
  });
});
