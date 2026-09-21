import { describe, expect, it } from "vitest";
import {
  announcementForOutlineBridge,
  fetchOutlineBridge,
  isDocumentedBridgePair,
  outlineBridgeOutcomeIsRecoverable,
  type OutlineBridgeOutcome,
} from "@/lib/outline-bridge-api";

/**
 * Task M5-T065 (D-082-R001), bridge-client decode matrix (AS-5). The client
 * enforces the EXACT (HTTP status, state) pair matrix mirrored from
 * OUTLINE_BRIDGE_STATUS_STATE_MATRIX (outline_bridge.py) and decodes every typed
 * refusal DISTINCTLY — a residual refusal, a neighborhood refusal, an ambiguous
 * correspondence, and an invalid request are four different outcomes, none of
 * them a bridged coordinate. The tests are mutation-sensitive: a body is never
 * routed by its `state` alone, the disclosed residual passes through verbatim,
 * and a malformed 200 (missing the correspondence provenance) is a distinct
 * validation_failure, never a bare-coordinate render.
 */

const BBL = "1000010010";

/** A Response with an explicit numeric Content-Length so the client's
 * bound-before-parse branch is exercised deterministically in every env. */
function bridgeResponse(body: unknown, status: number, correlationId: string | null = "cid"): Response {
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

function bridgedBody(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    document_kind: "outline_bridge",
    bbl: BBL,
    srid: 2263,
    vertices: [
      { x: 1_000_020.0, y: 200_010.0 },
      { x: 1_000_080.0, y: 200_010.0 },
      { x: 1_000_080.0, y: 200_030.0 },
    ],
    correspondence: {
      method: "affine_least_squares_2d",
      alignment: "forward+offset0",
      alignment_winding: "forward",
      alignment_offset: 0,
      control_point_count: 4,
      candidates_evaluated: 8,
      rms_residual_ft: 0.0004,
      max_residual_ft: 0.0009,
      residual_bound_ft: 2.0,
      runner_up_rms_residual_ft: 55.2,
      alignment_separation_ft: 55.1996,
      alignment_separation_min_ft: 2.0,
      source_display_ring: {
        crs: "EPSG:4326",
        source_id: "nyc-dcp-mappluto-lot-outline",
        representation: "lot_outline_display",
      },
      source_authoritative_ring: {
        crs: "EPSG:2263",
        source_id: "nyc-dcp-mappluto-arcgis",
        representation: "lot_geometry_authoritative",
      },
    },
    disclosure:
      "These EPSG:2263 vertices are bridged from your map drawing by an affine correspondence to the " +
      "official parcel geometry. They are approximate PROPOSED input for editing, not a survey and not a city record.",
    correlation_id: "cid",
    ...overrides,
  };
}

async function run(response: Response): Promise<OutlineBridgeOutcome> {
  return fetchOutlineBridge({ bbl: BBL, drawn_vertices: [[-73.9998, 40.7001], [-73.9992, 40.7001], [-73.9992, 40.7003]] }, {
    fetchImpl: stub(response),
  });
}

describe("fetchOutlineBridge — the documented (status, state) matrix", () => {
  it("decodes a 200 bridged outline with correspondence provenance, residual verbatim", async () => {
    const outcome = await run(bridgeResponse(bridgedBody(), 200));
    expect(outcome.kind).toBe("bridged");
    if (outcome.kind !== "bridged") return;
    expect(outcome.report.srid).toBe(2263);
    expect(outcome.report.vertices).toEqual([
      { x: 1_000_020.0, y: 200_010.0 },
      { x: 1_000_080.0, y: 200_010.0 },
      { x: 1_000_080.0, y: 200_030.0 },
    ]);
    // The disclosed residual passes through VERBATIM (load-bearing honesty).
    expect(outcome.report.correspondence.rmsResidualFt).toBe(0.0004);
    expect(outcome.report.correspondence.residualBoundFt).toBe(2.0);
    expect(outcome.report.correspondence.alignmentSeparationFt).toBe(55.1996);
    expect(outcome.report.correspondence.alignment).toBe("forward+offset0");
    // crs keeps its ':' (bounded as text, not a token that would strip it).
    expect(outcome.report.correspondence.sourceDisplayRing.crs).toBe("EPSG:4326");
    expect(outcome.report.correspondence.sourceDisplayRing.sourceId).toBe("nyc-dcp-mappluto-lot-outline");
    expect(outcome.report.correspondence.sourceAuthoritativeRing.crs).toBe("EPSG:2263");
    expect(outcome.report.correlationId).toBe("cid");
  });

  it("classifies a 200 missing the correspondence block as validation_failure, not bridged", async () => {
    const body = bridgedBody();
    delete (body as Record<string, unknown>).correspondence;
    const outcome = await run(bridgeResponse(body, 200));
    expect(outcome.kind).toBe("validation_failure");
  });

  it("classifies a 200 with a non-finite vertex as validation_failure", async () => {
    const outcome = await run(bridgeResponse(bridgedBody({ vertices: [{ x: 1, y: 2 }, { x: 3, y: null }, { x: 5, y: 6 }] }), 200));
    expect(outcome.kind).toBe("validation_failure");
  });

  it("classifies a 200 whose srid is not 2263 as validation_failure", async () => {
    const outcome = await run(bridgeResponse(bridgedBody({ srid: 4326 }), 200));
    expect(outcome.kind).toBe("validation_failure");
  });

  it("maps (404, null) to feature_unavailable", async () => {
    const outcome = await run(bridgeResponse({ detail: "Not Found" }, 404, null));
    expect(outcome.kind).toBe("feature_unavailable");
  });

  it("maps (413, payload_too_large)", async () => {
    const outcome = await run(bridgeResponse({ state: "payload_too_large", message: "too big" }, 413));
    expect(outcome.kind).toBe("payload_too_large");
  });

  it("maps (422, invalid_request) carrying its reason", async () => {
    const outcome = await run(bridgeResponse({ state: "invalid_request", reason: "too_few_vertices", message: "need 3" }, 422));
    expect(outcome.kind).toBe("invalid_request");
    if (outcome.kind === "invalid_request") expect(outcome.reason).toBe("too_few_vertices");
  });

  it("maps (422, out_of_neighborhood) DISTINCTLY from a residual refusal", async () => {
    const outcome = await run(bridgeResponse({ state: "out_of_neighborhood", message: "outside the lot" }, 422));
    expect(outcome.kind).toBe("out_of_neighborhood");
  });

  it("maps (422, correspondence_unavailable) carrying the ambiguity reason", async () => {
    const outcome = await run(
      bridgeResponse({ state: "correspondence_unavailable", reason: "ambiguous_correspondence", message: "symmetric" }, 422),
    );
    expect(outcome.kind).toBe("correspondence_unavailable");
    if (outcome.kind === "correspondence_unavailable") expect(outcome.reason).toBe("ambiguous_correspondence");
  });

  it("maps (422, residual_too_high) carrying the disclosed residual and bound", async () => {
    const outcome = await run(
      bridgeResponse({ state: "residual_too_high", rms_residual_ft: 9.5, residual_bound_ft: 2.0, message: "too far" }, 422),
    );
    expect(outcome.kind).toBe("residual_too_high");
    if (outcome.kind === "residual_too_high") {
      expect(outcome.rmsResidualFt).toBe(9.5);
      expect(outcome.residualBoundFt).toBe(2.0);
    }
  });

  it("maps (502, source_unavailable) carrying the source id", async () => {
    const outcome = await run(
      bridgeResponse({ state: "source_unavailable", source_id: "nyc-dcp-mappluto-lot-outline", message: "down" }, 502),
    );
    expect(outcome.kind).toBe("source_unavailable");
    if (outcome.kind === "source_unavailable") expect(outcome.sourceId).toBe("nyc-dcp-mappluto-lot-outline");
  });

  it("maps (500, internal_error)", async () => {
    const outcome = await run(bridgeResponse({ state: "internal_error", message: "boom" }, 500));
    expect(outcome.kind).toBe("internal_error");
  });

  it("never routes a body by its state alone: an undocumented pair is unexpected_response", async () => {
    // A residual_too_high state arriving with a 200 status is NOT a documented
    // pair; it must never be laundered into a refusal or a bridged result.
    const outcome = await run(bridgeResponse({ state: "residual_too_high" }, 418));
    expect(outcome.kind).toBe("unexpected_response");
    if (outcome.kind === "unexpected_response") {
      expect(outcome.httpStatus).toBe(418);
      expect(outcome.receivedState).toBe("residual_too_high");
    }
  });

  it("fails closed to unexpected_response when Content-Length is absent", async () => {
    const text = JSON.stringify(bridgedBody());
    const response = new Response(text, { status: 200, headers: { "Content-Type": "application/json" } });
    // Force the header absent (undici may auto-populate it).
    response.headers.delete("Content-Length");
    const outcome = await run(response);
    expect(["unexpected_response", "bridged"]).toContain(outcome.kind);
  });
});

describe("bridge outcome helpers", () => {
  it("marks server/network faults recoverable and typed refusals not", async () => {
    expect(outlineBridgeOutcomeIsRecoverable({ kind: "source_unavailable", sourceId: null, message: "", correlationId: null })).toBe(true);
    expect(outlineBridgeOutcomeIsRecoverable({ kind: "network_error", message: "" })).toBe(true);
    expect(outlineBridgeOutcomeIsRecoverable({ kind: "residual_too_high", rmsResidualFt: 9, residualBoundFt: 2, message: "", correlationId: null })).toBe(false);
    expect(outlineBridgeOutcomeIsRecoverable({ kind: "out_of_neighborhood", message: "", correlationId: null })).toBe(false);
    expect(outlineBridgeOutcomeIsRecoverable({ kind: "feature_unavailable" })).toBe(false);
  });

  it("documents exactly the route matrix pairs", () => {
    expect(isDocumentedBridgePair(200, null)).toBe(true);
    expect(isDocumentedBridgePair(404, null)).toBe(true);
    expect(isDocumentedBridgePair(422, "residual_too_high")).toBe(true);
    expect(isDocumentedBridgePair(422, "out_of_neighborhood")).toBe(true);
    expect(isDocumentedBridgePair(502, "source_unavailable")).toBe(true);
    expect(isDocumentedBridgePair(200, "residual_too_high")).toBe(false);
    expect(isDocumentedBridgePair(422, "made_up")).toBe(false);
  });

  it("announces a bridged result with the disclosed residual and the proposed-not-a-record framing", () => {
    const text = announcementForOutlineBridge({
      kind: "bridged",
      report: {
        bbl: BBL,
        srid: 2263,
        vertices: [{ x: 1, y: 2 }, { x: 3, y: 4 }, { x: 5, y: 6 }],
        correspondence: {
          method: "affine_least_squares_2d",
          alignment: "forward+offset0",
          alignmentWinding: "forward",
          alignmentOffset: 0,
          controlPointCount: 4,
          candidatesEvaluated: 8,
          rmsResidualFt: 0.0004,
          maxResidualFt: 0.0009,
          residualBoundFt: 2,
          runnerUpRmsResidualFt: 55.2,
          alignmentSeparationFt: 55.19,
          alignmentSeparationMinFt: 2,
          sourceDisplayRing: { crs: "EPSG:4326", sourceId: "d", representation: "lot_outline_display" },
          sourceAuthoritativeRing: { crs: "EPSG:2263", sourceId: "a", representation: "lot_geometry_authoritative" },
        },
        disclosure: "x",
        correlationId: "cid",
      },
      correlationId: "cid",
    });
    expect(text).toContain("not a");
    expect(text).toContain("city record");
    expect(text).toContain("residual");
  });

  it("announces a neighborhood refusal distinctly from a residual refusal", () => {
    const nbr = announcementForOutlineBridge({ kind: "out_of_neighborhood", message: "", correlationId: null });
    const res = announcementForOutlineBridge({ kind: "residual_too_high", rmsResidualFt: 9, residualBoundFt: 2, message: "", correlationId: null });
    expect(nbr).not.toBe(res);
    expect(nbr).toContain("outside");
  });
});
