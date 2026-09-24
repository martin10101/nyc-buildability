import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import {
  ENVELOPE_GAP_REASONS,
  MAX_ENVELOPE_ROUTE,
  announcementForMaxEnvelope,
  candidateIsAdoptable,
  classifyDimensionRow,
  dimensionRowKind,
  envelopeAggregateIsComplete,
  envelopeAggregateMessage,
  envelopeHasConflictAdvisory,
  envelopeHasContractViolation,
  fetchMaxEnvelope,
  isDocumentedMaxEnvelopePair,
  maxEnvelopeOutcomeIsRecoverable,
  maxEnvelopeRequestForProfile,
  type EnvelopeDimensionView,
  type EnvelopeView,
  type MaxEnvelopeOutcome,
} from "@/lib/architect/max-envelope-api";
import type { PropertyProfile } from "@/lib/contract";

/**
 * Task M5-T070 (D-082-R003 + D-083), max-envelope client decode matrix. The
 * client mirrors the EXACT (HTTP status, state) pair matrix of the UNMOUNTED
 * POST /api/v1/max-envelope route (max_envelope_api.py), bounds every reflected
 * string BEFORE render, size-bounds the body BEFORE parse (fail-closed), and
 * derives the D-083-R004 incomplete-aggregate predicate. The suite is
 * mutation-sensitive: flipping the fixture's gap row to binding (or removing an
 * advisory) flips the asserted aggregate state (AS-3), a malformed 200 is a
 * distinct validation_failure (never a partial render), and the server
 * disclosure passes through verbatim (AS-1).
 */

/** A Response with an explicit numeric Content-Length so the client's
 * bound-before-parse branch runs deterministically in every env. */
function envelopeResponse(body: unknown, status: number, correlationId: string | null = "cid"): Response {
  const text = JSON.stringify(body);
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "Content-Length": String(new TextEncoder().encode(text).length),
  };
  if (correlationId !== null) headers["X-Correlation-ID"] = correlationId;
  return new Response(text, { status, headers });
}

function stub(response: Response): typeof fetch {
  return (async () => response) as typeof fetch;
}

const DISCLOSURE =
  "These are rules-derived preliminary development limits for this lot. Each ceiling is the most " +
  "restrictive applicable rule; this is not a maximum permitted building and requires professional review.";

/** A binding dimension (a resolved per-rule ceiling). */
function bindingDimension(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    dimension_id: "max_far_floor_area",
    family: "floor_area",
    required_output: "max_floor_area_sq_ft",
    direction: "max",
    unit: "sq_ft",
    label: "Maximum floor area",
    saturating: false,
    binding_value: 20000,
    binding_rule_id: "zr-far-r6",
    binding_rule_version: "2024.1",
    coverage_status: "covered",
    out_competed_rule_ids: ["zr-far-r6-alt"],
    rule_citations: [{ section: "23-142" }, { section: "23-145" }],
    gap_reason: null,
    conflict_advisory: null,
    detail: "The floor-area ratio ceiling for the underlying district.",
    ...overrides,
  };
}

/** A gap dimension (the engine could not resolve a ceiling — an honest gap). */
function gapDimension(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    dimension_id: "max_height_ft",
    family: "height",
    required_output: "max_height_ft",
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

function fittedCandidate(): Record<string, unknown> {
  return {
    outline: {
      srid: 2263,
      vertices: [
        [1000000, 200000],
        [1000100, 200000],
        [1000100, 200050],
        [1000000, 200050],
      ],
    },
    levels: [{ level_index: 0, floor_count: 3, floor_to_floor_ft: 10 }],
    exterior_walls: [
      { id: "W-S", start_vertex_index: 0, end_vertex_index: 1 },
      { id: "W-E", start_vertex_index: 1, end_vertex_index: 2 },
    ],
  };
}

/** The full as_dict() body — one binding + one gap dimension by default (a
 * realistic partial-coverage envelope: gap > 0, so aggregate is INCOMPLETE). */
function envelopeBody(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    massing_class: "rectangle_prism",
    label: "BBL 1000010010 preliminary development limits",
    disclosure: DISCLOSURE,
    dimensions: [bindingDimension(), gapDimension()],
    candidate: fittedCandidate(),
    candidate_notes: ["Fitted to the recorded lot area; edit every value after adoption."],
    candidate_placement: {
      status: "fitted",
      detail: "The generated option was fitted inside the lot rectangle and proved contained.",
      lot_rectangle: {},
      footprint: {},
      contained: true,
    },
    candidate_consistency: { consistent: true },
    summary: { binding: 1, gap: 1, saturating_binding: 0, total: 2 },
    rule_input_bindings: {},
    unmapped_lot_facts: [],
    correlation_id: "cid",
    ...overrides,
  };
}

/** A fully-checked envelope: both dimensions binding, no advisory, gap 0. */
function completeBody(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return envelopeBody({
    dimensions: [
      bindingDimension(),
      bindingDimension({ dimension_id: "max_height_ft", label: "Maximum height", unit: "ft", binding_value: 60 }),
    ],
    summary: { binding: 2, gap: 0, saturating_binding: 0, total: 2 },
    ...overrides,
  });
}

async function run(response: Response): Promise<MaxEnvelopeOutcome> {
  return fetchMaxEnvelope(
    {
      lot: {
        area_sq_ft: 8000,
        area_provenance: { source_id: "architect_surface_lot_context" },
        lot_line_segments: [],
        street_lines: [],
      },
      lot_rule_facts: { zoning_district: "R6" },
      label: "BBL 1000010010 preliminary development limits",
    },
    { fetchImpl: stub(response) },
  );
}

function envelopeOf(outcome: MaxEnvelopeOutcome): EnvelopeView {
  if (outcome.kind !== "envelope") throw new Error(`expected an envelope outcome, got ${outcome.kind}`);
  return outcome.envelope;
}

describe("fetchMaxEnvelope — the documented (status, state) matrix", () => {
  it("decodes a 200 envelope with the server disclosure VERBATIM and per-dimension binding provenance (AS-1)", async () => {
    const envelope = envelopeOf(await run(envelopeResponse(envelopeBody(), 200)));
    expect(envelope.disclosure).toBe(DISCLOSURE);
    expect(envelope.correlationId).toBe("cid");
    expect(envelope.massingClass).toBe("rectangle_prism");
    expect(envelope.dimensions).toHaveLength(2);

    const binding = envelope.dimensions[0];
    expect(binding.bindingValue).toBe(20000);
    expect(binding.bindingRuleId).toBe("zr-far-r6");
    expect(binding.bindingRuleVersion).toBe("2024.1");
    expect(binding.outCompetedRuleIds).toEqual(["zr-far-r6-alt"]);
    expect(binding.citationCount).toBe(2);
    expect(binding.gapReason).toBeNull();
  });

  it("surfaces a gap dimension by its typed gap_reason with NO value (AS-1)", async () => {
    const envelope = envelopeOf(await run(envelopeResponse(envelopeBody(), 200)));
    const gap = envelope.dimensions[1];
    expect(gap.bindingValue).toBeNull();
    expect(gap.gapReason).toBe("allowance_unresolved");
  });

  it("surfaces a conflict advisory with BOTH competing rule ids (surfaced-never-resolved, AS-1)", async () => {
    const body = envelopeBody({
      dimensions: [
        bindingDimension({
          conflict_advisory: { competing_rule_ids: ["zr-far-r6", "zr-far-c4-3"], note: "two districts overlap this lot" },
        }),
        gapDimension(),
      ],
    });
    const envelope = envelopeOf(await run(envelopeResponse(body, 200)));
    expect(envelope.dimensions[0].conflictAdvisory?.competingRuleIds).toEqual(["zr-far-r6", "zr-far-c4-3"]);
    expect(envelope.dimensions[0].conflictAdvisory?.note).toContain("two districts");
  });

  it("exposes the ACTUAL server-provided binding-rule citations (section + snapshot refs), not only the count (AS-1)", async () => {
    // The full evaluator citation shape (_citations_with_provenance): snapshot_id
    // + section + quote + last_amended + provenance. Only the load-bearing
    // references (section, snapshot_id) surface; the rest is ignored, all bounded.
    const body = envelopeBody({
      dimensions: [
        bindingDimension({
          rule_citations: [
            { snapshot_id: "zr-23-142", section: "23-142", quote: "…", last_amended: "2024-03-26", provenance: { source_id: "zr" } },
            { snapshot_id: "zr-23-145", section: "23-145", quote: "…", last_amended: "2024-03-26", provenance: { source_id: "zr" } },
          ],
        }),
        gapDimension(),
      ],
    });
    const envelope = envelopeOf(await run(envelopeResponse(body, 200)));
    const binding = envelope.dimensions[0];
    expect(binding.citationCount).toBe(2);
    expect(binding.citations).toEqual([
      { section: "23-142", snapshotId: "zr-23-142" },
      { section: "23-145", snapshotId: "zr-23-145" },
    ]);
    // A gap dimension resolved no rule, so it exposes no citations at all.
    expect(envelope.dimensions[1].citations).toEqual([]);
  });

  it("classifies a generic 404 (flag off / unmounted) as feature_unavailable", async () => {
    const outcome = await run(envelopeResponse({ detail: "Not Found" }, 404));
    expect(outcome.kind).toBe("feature_unavailable");
  });

  it("classifies (413, payload_too_large), (422, validation_error), (500, internal_error) distinctly", async () => {
    const tooLarge = await run(envelopeResponse({ state: "payload_too_large", message: "too big" }, 413));
    expect(tooLarge.kind).toBe("payload_too_large");

    const invalid = await run(
      envelopeResponse({ state: "validation_error", field: "lot.area_sq_ft", message: "must be positive" }, 422),
    );
    expect(invalid).toMatchObject({ kind: "invalid_request", field: "lot.area_sq_ft" });

    const internal = await run(envelopeResponse({ state: "internal_error", message: "boom" }, 500));
    expect(internal.kind).toBe("internal_error");
  });

  it("rejects an UNDOCUMENTED (status, state) pair as unexpected_response, never routed by state alone", async () => {
    // A 200 carrying a state token is NOT a documented pair (200 has NO state).
    const outcome = await run(envelopeResponse({ state: "internal_error", ...envelopeBody() }, 200));
    expect(outcome.kind).toBe("unexpected_response");
  });

  it("treats a malformed 200 (missing dimensions) as a distinct validation_failure, never a partial render", async () => {
    const outcome = await run(envelopeResponse(envelopeBody({ dimensions: [] }), 200));
    expect(outcome.kind).toBe("validation_failure");
  });

  it("treats a 200 missing the required disclosure as validation_failure", async () => {
    const outcome = await run(envelopeResponse(envelopeBody({ disclosure: "" }), 200));
    expect(outcome.kind).toBe("validation_failure");
  });

  it("rejects an over-large declared Content-Length BEFORE parse (fail-closed)", async () => {
    // A deterministic fake so the size-bound branch is exercised regardless of how
    // the runtime's Response computes Content-Length: the declared length exceeds
    // MAX_RESPONSE_BYTES, so the body is rejected and never parsed/walked.
    const oversized = {
      status: 200,
      headers: { get: (name: string) => (name === "Content-Length" ? "9999999" : null) },
      json: async () => envelopeBody(),
    } as unknown as Response;
    const outcome = await fetchMaxEnvelope(
      { lot: { area_sq_ft: 8000, area_provenance: { source_id: "x" }, lot_line_segments: [], street_lines: [] }, lot_rule_facts: {} },
      { fetchImpl: (async () => oversized) as unknown as typeof fetch },
    );
    expect(outcome.kind).toBe("unexpected_response");
  });
});

describe("candidate bounding + adoptability gate (AS-4)", () => {
  it("bounds a fitted, contained candidate and marks it adoptable", async () => {
    const envelope = envelopeOf(await run(envelopeResponse(envelopeBody(), 200)));
    expect(envelope.candidate).not.toBeNull();
    expect(candidateIsAdoptable(envelope)).toBe(true);
  });

  it("is NOT adoptable when the placement is not a contained fit", async () => {
    const body = envelopeBody({
      // [ORCH-CORRECTED per G3-F1/G4-F2] a REAL CandidatePlacementStatus value.
      candidate_placement: { status: "footprint_exceeds_lot", detail: "the lot rectangle is too small", contained: false },
    });
    const envelope = envelopeOf(await run(envelopeResponse(body, 200)));
    expect(candidateIsAdoptable(envelope)).toBe(false);
  });

  it("drops a malformed candidate (wrong srid) rather than laundering it — limits still stand", async () => {
    const body = envelopeBody({ candidate: { ...fittedCandidate(), outline: { srid: 4326, vertices: [[0, 0]] } } });
    const envelope = envelopeOf(await run(envelopeResponse(body, 200)));
    expect(envelope.candidate).toBeNull();
    expect(candidateIsAdoptable(envelope)).toBe(false);
    // The binding limits are unaffected by a dropped candidate.
    expect(envelope.dimensions[0].bindingValue).toBe(20000);
  });

  // [G3-F2(2)] Every boundCandidate rejection path OTHER than the srid check, each
  // isolated (the rest of the candidate stays valid) so each case is the ONLY guard
  // that rejects it: deleting that guard returns a non-null candidate and reddens it.
  // Where a guard is otherwise shadowed by a later one, the probe is chosen to reach
  // it alone (an object-shaped vertex for the pair check; "" for the levels/walls
  // array checks, which iterates to nothing instead of throwing). Without the
  // vertices isArray check, "vertices missing" throws inside the decode (red by
  // exception). The `raw.length < 2` disjunct is shadowed by the finite-y check for
  // every JSON input (raw[1] is undefined), so it has no separately observable probe.
  function candidateWith(patch: (c: Record<string, unknown>) => void): Record<string, unknown> {
    const c = fittedCandidate();
    patch(c);
    return c;
  }
  const outline = (vertices: unknown) => ({ srid: 2263, vertices });
  const GOOD_V = [[1000000, 200000], [1000100, 200000], [1000100, 200050]];
  it.each([
    { path: "vertices array empty", c: candidateWith((c) => { c.outline = outline([]); }) },
    { path: "vertices missing (not an array)", c: candidateWith((c) => { c.outline = { srid: 2263 }; }) },
    { path: "vertex not an array (object with 0/1 keys)", c: candidateWith((c) => { c.outline = outline([...GOOD_V, { 0: 1000000, 1: 200050 }]); }) },
    { path: "vertex x not finite", c: candidateWith((c) => { c.outline = outline([...GOOD_V, ["1000000", 200050]]); }) },
    { path: "vertex y not finite", c: candidateWith((c) => { c.outline = outline([...GOOD_V, [1000000, null]]); }) },
    { path: "levels not an array", c: candidateWith((c) => { c.levels = ""; }) },
    { path: "level_index not finite", c: candidateWith((c) => { c.levels = [{ level_index: null, floor_count: 3, floor_to_floor_ft: 10 }]; }) },
    { path: "floor_count not finite", c: candidateWith((c) => { c.levels = [{ level_index: 0, floor_count: "3", floor_to_floor_ft: 10 }]; }) },
    { path: "floor_to_floor_ft not finite", c: candidateWith((c) => { c.levels = [{ level_index: 0, floor_count: 3, floor_to_floor_ft: "10" }]; }) },
    { path: "exterior_walls not an array", c: candidateWith((c) => { c.exterior_walls = ""; }) },
    { path: "wall id not a string", c: candidateWith((c) => { c.exterior_walls = [{ id: 7, start_vertex_index: 0, end_vertex_index: 1 }]; }) },
    { path: "wall start index not finite", c: candidateWith((c) => { c.exterior_walls = [{ id: "W-S", start_vertex_index: "0", end_vertex_index: 1 }]; }) },
    { path: "wall end index not finite", c: candidateWith((c) => { c.exterior_walls = [{ id: "W-S", start_vertex_index: 0, end_vertex_index: null }]; }) },
  ])("drops a candidate whose $path — never adoptable, limits still stand", async ({ c }) => {
    const envelope = envelopeOf(await run(envelopeResponse(envelopeBody({ candidate: c }), 200)));
    expect(envelope.candidate).toBeNull();
    expect(candidateIsAdoptable(envelope)).toBe(false);
    expect(envelope.dimensions[0].bindingValue).toBe(20000);
  });

  it("control: the same valid candidate survives bounding (so each reject above is the guard's doing)", async () => {
    const envelope = envelopeOf(await run(envelopeResponse(envelopeBody({ candidate: candidateWith(() => {}) }), 200)));
    expect(envelope.candidate).not.toBeNull();
  });
});

describe("aggregate state predicate (D-083-R004, AS-3 — mutation-sensitive)", () => {
  it("is INCOMPLETE while any dimension is a gap", async () => {
    const envelope = envelopeOf(await run(envelopeResponse(envelopeBody(), 200)));
    expect(envelope.summary.gap).toBe(1);
    expect(envelopeAggregateIsComplete(envelope)).toBe(false);
  });

  it("MUTATION: flipping the gap row to binding (gap 0, no advisory) flips the aggregate to complete", async () => {
    const envelope = envelopeOf(await run(envelopeResponse(completeBody(), 200)));
    expect(envelope.summary.gap).toBe(0);
    expect(envelopeHasConflictAdvisory(envelope)).toBe(false);
    expect(envelopeAggregateIsComplete(envelope)).toBe(true);
  });

  it("MUTATION: a conflict advisory alone keeps the aggregate INCOMPLETE even with gap 0", async () => {
    const body = completeBody({
      dimensions: [
        bindingDimension({ conflict_advisory: { competing_rule_ids: ["a", "b"], note: null } }),
        bindingDimension({ dimension_id: "max_height_ft", label: "Maximum height", unit: "ft", binding_value: 60 }),
      ],
    });
    const envelope = envelopeOf(await run(envelopeResponse(body, 200)));
    expect(envelope.summary.gap).toBe(0);
    expect(envelopeHasConflictAdvisory(envelope)).toBe(true);
    expect(envelopeAggregateIsComplete(envelope)).toBe(false);
  });
});

describe("outcome helpers", () => {
  it("isDocumentedMaxEnvelopePair recognises exactly the documented pairs", () => {
    expect(isDocumentedMaxEnvelopePair(200, null)).toBe(true);
    expect(isDocumentedMaxEnvelopePair(404, null)).toBe(true);
    expect(isDocumentedMaxEnvelopePair(413, "payload_too_large")).toBe(true);
    expect(isDocumentedMaxEnvelopePair(422, "validation_error")).toBe(true);
    expect(isDocumentedMaxEnvelopePair(500, "internal_error")).toBe(true);
    expect(isDocumentedMaxEnvelopePair(200, "internal_error")).toBe(false);
    expect(isDocumentedMaxEnvelopePair(418, null)).toBe(false);
  });

  it("marks server/network faults recoverable but a typed refusal / feature-off a RESULT", () => {
    expect(maxEnvelopeOutcomeIsRecoverable({ kind: "internal_error", message: "x", correlationId: null })).toBe(true);
    expect(maxEnvelopeOutcomeIsRecoverable({ kind: "network_error", message: "x" })).toBe(true);
    expect(maxEnvelopeOutcomeIsRecoverable({ kind: "feature_unavailable" })).toBe(false);
    expect(maxEnvelopeOutcomeIsRecoverable({ kind: "invalid_request", field: null, message: "x", correlationId: null })).toBe(false);
  });

  it("announces an incomplete envelope with the honest count and NEVER 'maximum allowed building' (D-083)", async () => {
    const incomplete = announcementForMaxEnvelope(await run(envelopeResponse(envelopeBody(), 200)));
    // [HJ-1] The announcer speaks the SAME aggregate line the panel shows, incl. "incomplete".
    expect(incomplete).toBe(
      "Preliminary development limits loaded. Could not check 1 of 2 development limits. " +
        "This preliminary picture is incomplete. A rules-derived estimate requiring professional review, " +
        "not a maximum permitted building.",
    );
    expect(incomplete.toLowerCase()).not.toContain("maximum allowed building");

    const complete = announcementForMaxEnvelope(await run(envelopeResponse(completeBody(), 200)));
    expect(complete).toBe(
      "Preliminary development limits loaded for 2 dimensions. A rules-derived estimate requiring " +
        "professional review, not a maximum permitted building.",
    );
    expect(complete.toLowerCase()).not.toContain("maximum allowed building");

    // A superseded (aborted) request announces nothing.
    expect(announcementForMaxEnvelope({ kind: "aborted" })).toBe("");
  });
});

describe("maxEnvelopeRequestForProfile — answer-first request assembly (D-083-R003)", () => {
  function profile(overrides: Record<string, unknown> = {}): PropertyProfile {
    return {
      identity: { bbl: "1000010010" },
      lot_facts: { lotarea: { value: 8000 } },
      zoning: { districts: ["R6"] },
      ...overrides,
    } as unknown as PropertyProfile;
  }

  it("builds a request from the recorded lot area + single district, sending NO lot geometry", () => {
    const request = maxEnvelopeRequestForProfile(profile());
    expect(request).not.toBeNull();
    expect(request?.lot.area_sq_ft).toBe(8000);
    expect(request?.lot.lot_line_segments).toEqual([]);
    expect(request?.lot.street_lines).toEqual([]);
    expect(request?.lot_rule_facts).toEqual({ zoning_district: "R6" });
    expect(request?.label).toContain("1000010010");
  });

  it("omits the zoning district when the lot spans more than one (never guesses which governs)", () => {
    const request = maxEnvelopeRequestForProfile(profile({ zoning: { districts: ["R6", "C4-3"] } }));
    expect(request?.lot_rule_facts).toEqual({});
  });

  it("returns NULL (degrade to a typed card, never a fabricated limit) when no usable lot area is recorded", () => {
    expect(maxEnvelopeRequestForProfile(profile({ lot_facts: { lotarea: { value: 0 } } }))).toBeNull();
    expect(maxEnvelopeRequestForProfile(profile({ lot_facts: {} }))).toBeNull();
  });
});

describe("fetchMaxEnvelope — browser-level modes (DB-050(i): client_timeout, aborted)", () => {
  it("returns client_timeout when the request exceeds the budget (never a hang, never `aborted`)", async () => {
    // A fetch that only settles when its signal aborts: the internal timeout fires,
    // aborts the controller, and the timed-out branch classifies it as client_timeout.
    const fetchImpl = ((_url: string, init?: RequestInit) =>
      new Promise<Response>((_resolve, reject) => {
        init?.signal?.addEventListener("abort", () => reject(new DOMException("aborted", "AbortError")));
      })) as unknown as typeof fetch;
    const outcome = await fetchMaxEnvelope(
      { lot: { area_sq_ft: 8000, area_provenance: { source_id: "x" }, lot_line_segments: [], street_lines: [] }, lot_rule_facts: {} },
      { fetchImpl, timeoutMs: 5 },
    );
    // MUTATION: dropping the `if (timedOut)` branch reddens this — it would misclassify
    // a timeout as `aborted`.
    expect(outcome).toEqual({ kind: "client_timeout", timeoutMs: 5 });
  });

  it("returns `aborted` WITHOUT any fetch when the caller signal is already aborted (a superseded request)", async () => {
    const controller = new AbortController();
    controller.abort();
    let called = false;
    const fetchImpl = (async () => {
      called = true;
      return envelopeResponse(envelopeBody(), 200);
    }) as unknown as typeof fetch;
    const outcome = await fetchMaxEnvelope(
      { lot: { area_sq_ft: 8000, area_provenance: { source_id: "x" }, lot_line_segments: [], street_lines: [] }, lot_rule_facts: {} },
      { fetchImpl, signal: controller.signal },
    );
    // MUTATION: dropping the pre-flight `externalSignal.aborted` check reddens this —
    // it would fire a network request for an already-superseded panel state.
    expect(outcome).toEqual({ kind: "aborted" });
    expect(called).toBe(false);
  });
});

describe("dimensionRowKind — binding-or-gap XOR classifier (D-083-R004, DB-050(d), mutation-sensitive)", () => {
  function dimOf(bindingValue: number | null, gapReason: string | null): EnvelopeDimensionView {
    // A deliberate minimal shape: the classifier reads only the bounded values and
    // their raw-presence flags (a well-formed field is present iff its value is set).
    return {
      bindingValue,
      gapReason,
      bindingValuePresent: bindingValue !== null,
      gapReasonPresent: gapReason !== null,
    } as unknown as EnvelopeDimensionView;
  }

  it("classifies a value-only row as `value` and a gap-only row as `gap`", () => {
    expect(dimensionRowKind(dimOf(20000, null))).toBe("value");
    expect(dimensionRowKind(dimOf(null, "allowance_unresolved"))).toBe("gap");
    // Two-mutant rule: a real 0 limit is a VALUE (a truthiness check would withhold it).
    expect(dimensionRowKind(dimOf(0, null))).toBe("value");
  });

  it("classifies BOTH-set and NEITHER-set rows as `contract_violation` (never a value)", () => {
    // MUTATION: removing the `hasValue === hasGap` XOR branch collapses both of these
    // to "value"/"gap" and reddens this spec — a null would then render as a limit.
    expect(dimensionRowKind(dimOf(20000, "allowance_unresolved"))).toBe("contract_violation");
    expect(dimensionRowKind(dimOf(null, null))).toBe("contract_violation");
  });

  it("a BOTH/NEITHER row keeps the aggregate INCOMPLETE even with the server's gap count 0", async () => {
    const both = envelopeOf(
      await run(
        envelopeResponse(
          completeBody({
            dimensions: [
              // binding_value AND gap_reason both set: a server XOR violation.
              bindingDimension({ gap_reason: "allowance_unresolved" }),
              bindingDimension({ dimension_id: "max_height_ft", label: "Maximum height", unit: "ft", binding_value: 60 }),
            ],
            summary: { binding: 2, gap: 0, saturating_binding: 0, total: 2 },
          }),
          200,
        ),
      ),
    );
    expect(both.summary.gap).toBe(0);
    expect(envelopeHasContractViolation(both)).toBe(true);
    // MUTATION: dropping the violation term from envelopeAggregateIsComplete reddens
    // this — gap 0 + no advisory would falsely read as complete.
    expect(envelopeAggregateIsComplete(both)).toBe(false);

    const neither = envelopeOf(
      await run(
        envelopeResponse(
          completeBody({
            dimensions: [
              gapDimension({ gap_reason: null }), // binding_value null AND gap_reason null: NEITHER
              bindingDimension({ dimension_id: "max_height_ft", label: "Maximum height", unit: "ft", binding_value: 60 }),
            ],
            summary: { binding: 1, gap: 0, saturating_binding: 0, total: 2 },
          }),
          200,
        ),
      ),
    );
    expect(envelopeHasContractViolation(neither)).toBe(true);
    expect(envelopeAggregateIsComplete(neither)).toBe(false);
  });

  /** A body row with EXACT raw binding_value / gap_reason (`undefined` = key omitted). */
  function rawRow(bindingValue: unknown, gapReason: unknown): Record<string, unknown> {
    const row = bindingDimension({ binding_value: bindingValue, gap_reason: gapReason });
    if (bindingValue === undefined) delete row.binding_value;
    if (gapReason === undefined) delete row.gap_reason;
    return row;
  }

  // [G3-F1] The XOR runs on RAW presence, decided in boundDimension BEFORE bounding
  // nulls a malformed field. Every row goes through the real decode path (run()).
  const RAW_ROWS: Array<{ label: string; bv: unknown; gr: unknown; expected: { kind: string; returned?: string } }> = [
    { label: "value only", bv: 20000, gr: null, expected: { kind: "value" } },
    { label: "a real 0 value (two-mutant rule)", bv: 0, gr: null, expected: { kind: "value" } },
    { label: "gap only", bv: null, gr: "allowance_unresolved", expected: { kind: "gap" } },
    { label: "value + gap token", bv: 20000, gr: "allowance_unresolved", expected: { kind: "contract_violation", returned: "both" } },
    { label: 'value + blank gap_reason ""', bv: 20000, gr: "", expected: { kind: "contract_violation", returned: "both" } },
    { label: 'value + whitespace gap_reason " "', bv: 20000, gr: " ", expected: { kind: "contract_violation", returned: "both" } },
    { label: "value + non-string gap_reason 7", bv: 20000, gr: 7, expected: { kind: "contract_violation", returned: "both" } },
    { label: "value + object gap_reason {}", bv: 20000, gr: {}, expected: { kind: "contract_violation", returned: "both" } },
    { label: "both null", bv: null, gr: null, expected: { kind: "contract_violation", returned: "neither" } },
    { label: "both keys omitted", bv: undefined, gr: undefined, expected: { kind: "contract_violation", returned: "neither" } },
    { label: 'blank gap_reason "" alone', bv: null, gr: "", expected: { kind: "contract_violation", returned: "unreadable" } },
    { label: "non-string gap_reason 7 alone", bv: null, gr: 7, expected: { kind: "contract_violation", returned: "unreadable" } },
    { label: 'string binding_value "20000" alone', bv: "20000", gr: null, expected: { kind: "contract_violation", returned: "unreadable" } },
  ];
  it.each(RAW_ROWS)("raw row ($label) classifies as $expected.kind", async ({ bv, gr, expected }) => {
    const body = completeBody({
      dimensions: [
        rawRow(bv, gr),
        bindingDimension({ dimension_id: "max_height_ft", label: "Maximum height", unit: "ft", binding_value: 60 }),
      ],
      summary: { binding: 2, gap: 0, saturating_binding: 0, total: 2 },
    });
    const envelope = envelopeOf(await run(envelopeResponse(body, 200)));
    // MUTATION (G3-F1 leak): classifying on the BOUNDED fields turns "", " ", 7 and {}
    // into "absent" -> the value+malformed rows read `value`; this table reddens.
    expect(classifyDimensionRow(envelope.dimensions[0])).toEqual(expected);
    expect(envelopeAggregateIsComplete(envelope)).toBe(expected.kind === "value");
  });

  it("records raw presence for BOTH fields before bounding (present-but-malformed is not absent)", async () => {
    const body = completeBody({ dimensions: [rawRow(20000, ""), rawRow(null, null)] });
    const envelope = envelopeOf(await run(envelopeResponse(body, 200)));
    expect(envelope.dimensions[0]).toMatchObject({ bindingValue: 20000, gapReason: null, bindingValuePresent: true, gapReasonPresent: true });
    expect(envelope.dimensions[1]).toMatchObject({ bindingValue: null, gapReason: null, bindingValuePresent: false, gapReasonPresent: false });
  });
});

describe("aggregate line + completeness from row kinds (G3-A1, HJ-1, HJ-2)", () => {
  it("[G3-A1] a GAP ROW keeps the aggregate incomplete even when the server's summary.gap is 0", async () => {
    // One binding + one gap row, but the server's own summary claims gap 0.
    const envelope = envelopeOf(
      await run(envelopeResponse(envelopeBody({ summary: { binding: 1, gap: 0, saturating_binding: 0, total: 2 } }), 200)),
    );
    // MUTATION: dropping the gap-row term from envelopeAggregateIsComplete reddens this.
    expect(envelopeAggregateIsComplete(envelope)).toBe(false);
    expect(envelopeAggregateMessage(envelope)).toBe(
      "Could not check 1 of 2 development limits. The service's own count listed 0 of 2 as not checked. " +
        "This preliminary picture is incomplete.",
    );
  });

  it("the accepted gap / gap+advisory / complete lines are unchanged", async () => {
    expect(envelopeAggregateMessage(envelopeOf(await run(envelopeResponse(envelopeBody(), 200))))).toBe(
      "Could not check 1 of 2 development limits. This preliminary picture is incomplete.",
    );
    const withAdvisory = envelopeBody({
      dimensions: [bindingDimension({ conflict_advisory: { competing_rule_ids: ["a", "b"], note: null } }), gapDimension()],
    });
    expect(envelopeAggregateMessage(envelopeOf(await run(envelopeResponse(withAdvisory, 200))))).toBe(
      "Could not check 1 of 2 development limits, and a rule conflict needs professional review. " +
        "This preliminary picture is incomplete.",
    );
    expect(envelopeAggregateMessage(envelopeOf(await run(envelopeResponse(completeBody(), 200))))).toBe(
      "All 2 preliminary development limits were checked — a rules-derived estimate requiring professional review.",
    );
  });

  it("[HJ-2] a withheld-only envelope counts the withheld row and never says 'Could not check 0 of'", async () => {
    const body = completeBody({
      dimensions: [
        bindingDimension({ gap_reason: "allowance_unresolved" }),
        bindingDimension({ dimension_id: "max_height_ft", label: "Maximum height", unit: "ft", binding_value: 60 }),
      ],
    });
    const outcome = await run(envelopeResponse(body, 200));
    const line = envelopeAggregateMessage(envelopeOf(outcome));
    expect(line).toBe(
      "Could not check 1 of 2 development limits (1 withheld because the service's answer was inconsistent " +
        "or unreadable). The service's own count listed 0 of 2 as not checked. This preliminary picture is incomplete.",
    );
    expect(line).not.toContain("Could not check 0 of");
    // [HJ-1] The announcer repeats the withheld clause and "incomplete".
    expect(announcementForMaxEnvelope(outcome)).toBe(
      `Preliminary development limits loaded. ${line} A rules-derived estimate requiring professional review, ` +
        "not a maximum permitted building.",
    );
  });

  it("an advisory-only envelope says so plainly (no 'Could not check 0 of')", async () => {
    const body = completeBody({
      dimensions: [
        bindingDimension({ conflict_advisory: { competing_rule_ids: ["a", "b"], note: null } }),
        bindingDimension({ dimension_id: "max_height_ft", label: "Maximum height", unit: "ft", binding_value: 60 }),
      ],
    });
    expect(envelopeAggregateMessage(envelopeOf(await run(envelopeResponse(body, 200))))).toBe(
      "A rule conflict needs professional review. This preliminary picture is incomplete.",
    );
  });

  it("a server summary.gap with no gap rows is disclosed, never dropped", async () => {
    const body = completeBody({ summary: { binding: 2, gap: 1, saturating_binding: 0, total: 2 } });
    const envelope = envelopeOf(await run(envelopeResponse(body, 200)));
    expect(envelopeAggregateIsComplete(envelope)).toBe(false);
    expect(envelopeAggregateMessage(envelope)).toBe(
      "The service's own count listed 1 of 2 as not checked. This preliminary picture is incomplete.",
    );
  });
});

describe("no client-side CRS math in the panel and client modules (DB-050(f), AS-3)", () => {
  const files = [
    "../../../components/architect/MaxEnvelopePanel.tsx",
    "../max-envelope-api.ts",
    "../proposal-draft.ts",
  ];
  // Import-/call-level markers of an ACTUAL coordinate-reference transform. Deliberately
  // NOT the bare word "transform" (these modules' own comments state a transform must
  // NOT exist), so the guard is comment-safe and reddens ONLY when a real projection
  // library or transform call is injected (AS-3).
  const bannedMarkers: Array<[string, RegExp]> = [
    ["proj4", /\bproj4\b/i],
    ["reproject", /reproject/i],
    ["fromLonLat(", /\bfromLonLat\s*\(/],
    ["toLonLat(", /\btoLonLat\s*\(/],
    ["@turf/", /@turf\//],
    ["ol/proj import", /["']ol\/proj["']/],
    ["transformCoordinates", /transformCoordinates/i],
  ];
  it.each(files)("%s imports no projection library and defines no CRS transform", (rel) => {
    const source = readFileSync(new URL(rel, import.meta.url), "utf8");
    for (const [name, marker] of bannedMarkers) {
      expect(marker.test(source), `${rel} must contain no CRS transform (${name})`).toBe(false);
    }
  });
});

describe("gap-reason vocabulary mirror (DB-050(m))", () => {
  it("carries exactly the four server EnvelopeGapReason tokens, in the mirror set", () => {
    expect([...ENVELOPE_GAP_REASONS]).toEqual([
      "no_applicable_rule",
      "allowance_unresolved",
      "family_unsupported",
      "non_commensurable_with_massing",
    ]);
  });
});

describe("route path", () => {
  it("targets the UNMOUNTED contract path exactly", () => {
    expect(MAX_ENVELOPE_ROUTE).toBe("/api/v1/max-envelope");
  });
});
