import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it, vi } from "vitest";
import {
  fetchLotGeometry,
  validateOutlineGeometry,
  type LotOutlineOutcome,
} from "@/lib/lot-geometry-api";

/**
 * M5-T023 offline pack for the hardened lot-geometry client. Every typed
 * outcome + the boundary/malformed/timeout/abort paths, driven by the COMMITTED
 * contract fixtures (packages/contracts/fixtures/valid/lot_geometry) read from
 * disk so the geometry asserted here IS the recorded contract geometry, never a
 * literal retyped in the test. No network is touched.
 */

const FIXTURE_ROOT = resolve(
  process.cwd(),
  "../../packages/contracts/fixtures/valid/lot_geometry",
);

function fixture(name: string): Record<string, unknown> {
  return JSON.parse(readFileSync(resolve(FIXTURE_ROOT, `${name}.json`), "utf8"));
}

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json",
      "X-Correlation-ID": "lot-cid-abc123",
    },
  });
}

/** A fetchImpl that resolves to a fixed Response, ignoring the URL. */
function fetchReturning(response: Response): typeof fetch {
  return vi.fn().mockResolvedValue(response) as unknown as typeof fetch;
}

const BBL = "1008350041";

async function run(response: Response): Promise<LotOutlineOutcome> {
  return fetchLotGeometry(BBL, { fetchImpl: fetchReturning(response) });
}

describe("fetchLotGeometry — 200 outline documents", () => {
  it("single_lot: returns a document with the fixture geometry structurally UNCHANGED", async () => {
    const fx = fixture("single_lot_polygon");
    const outcome = await run(jsonResponse(fx, 200));
    expect(outcome.kind).toBe("document");
    if (outcome.kind !== "document") return;
    expect(outcome.view.outcome).toBe("single_lot");
    expect(outcome.view.geometry).toEqual(fx.geometry);
    expect(outcome.view.geometryUnusable).toBe(false);
    expect(outcome.correlationId).toBe("lot-cid-abc123");
    // Bounded provenance + honest copy present.
    expect(outcome.view.accuracyNote).toContain("20 ft");
    expect(outcome.view.attribution).toContain("City Planning");
    expect(outcome.view.source.sourceId).toBe("nyc-dcp-mappluto-arcgis");
  });

  it("multipolygon: EVERY polygon and ring reaches the view exactly as in the fixture (no ring dropped, no first-polygon pick)", async () => {
    const fx = fixture("single_lot_multipolygon");
    const outcome = await run(jsonResponse(fx, 200));
    expect(outcome.kind).toBe("document");
    if (outcome.kind !== "document") return;
    expect(outcome.view.geometry).toEqual(fx.geometry);
    const geom = outcome.view.geometry;
    expect(geom?.type).toBe("MultiPolygon");
    // Structural parity: same polygon count as the fixture.
    const fxCoords = (fx.geometry as { coordinates: unknown[] }).coordinates;
    expect((geom as { coordinates: unknown[] }).coordinates).toHaveLength(
      fxCoords.length,
    );
  });

  it("condo unit no_outline: typed reason, geometry null, no shape", async () => {
    const fx = fixture("no_outline_condo_unit");
    const outcome = await run(jsonResponse(fx, 200));
    expect(outcome.kind).toBe("document");
    if (outcome.kind !== "document") return;
    expect(outcome.view.outcome).toBe("no_outline");
    expect(outcome.view.noOutlineReason).toBe("condo_unit_lot_no_polygon");
    expect(outcome.view.geometry).toBeNull();
  });

  it("no_feature no_outline: typed reason no_feature_for_bbl", async () => {
    const fx = fixture("no_outline_no_feature");
    const outcome = await run(jsonResponse(fx, 200));
    if (outcome.kind !== "document") throw new Error("expected document");
    expect(outcome.view.noOutlineReason).toBe("no_feature_for_bbl");
    expect(outcome.view.geometry).toBeNull();
  });

  it("multiple_features: review_required, geometry withheld (null)", async () => {
    const fx = fixture("multiple_features_review");
    const outcome = await run(jsonResponse(fx, 200));
    if (outcome.kind !== "document") throw new Error("expected document");
    expect(outcome.view.outcome).toBe("multiple_features");
    expect(outcome.view.reviewRequired).toBe(true);
    expect(outcome.view.geometry).toBeNull();
  });

  it("invalid_geometry: typed outcome, geometry null", async () => {
    const fx = fixture("invalid_geometry");
    const outcome = await run(jsonResponse(fx, 200));
    if (outcome.kind !== "document") throw new Error("expected document");
    expect(outcome.view.outcome).toBe("invalid_geometry");
    expect(outcome.view.geometry).toBeNull();
  });

  it("never draws a first-pick: geometry on a NON-single_lot body is discarded", async () => {
    const fx = fixture("multiple_features_review");
    fx.geometry = fixture("single_lot_polygon").geometry; // hostile: geometry on a review body
    const outcome = await run(jsonResponse(fx, 200));
    if (outcome.kind !== "document") throw new Error("expected document");
    expect(outcome.view.outcome).toBe("multiple_features");
    expect(outcome.view.geometry).toBeNull();
  });

  it("single_lot with a non-number coordinate: geometryUnusable, no fabricated shape", async () => {
    const fx = fixture("single_lot_polygon");
    // Corrupt one ordinate into a string; JSON preserves it as a string.
    (fx.geometry as { coordinates: number[][][] }).coordinates[0][0] = [
      "x" as unknown as number,
      40.7,
    ];
    const outcome = await run(jsonResponse(fx, 200));
    if (outcome.kind !== "document") throw new Error("expected document");
    expect(outcome.view.outcome).toBe("single_lot");
    expect(outcome.view.geometry).toBeNull();
    expect(outcome.view.geometryUnusable).toBe(true);
  });

  it("unrecognized outcome / wrong document_kind / crs -> unexpected_response", async () => {
    const bad = { ...fixture("single_lot_polygon"), document_kind: "not_it" };
    expect((await run(jsonResponse(bad, 200))).kind).toBe("unexpected_response");
    const badCrs = { ...fixture("single_lot_polygon"), crs: "EPSG:2263" };
    expect((await run(jsonResponse(badCrs, 200))).kind).toBe("unexpected_response");
    const badOutcome = { ...fixture("single_lot_polygon"), outcome: "surprise" };
    expect((await run(jsonResponse(badOutcome, 200))).kind).toBe(
      "unexpected_response",
    );
  });
});

describe("fetchLotGeometry — non-200 documented pairs", () => {
  it("generic 404 {detail: Not Found} -> route_absent (never an error)", async () => {
    const outcome = await run(
      new Response(JSON.stringify({ detail: "Not Found" }), { status: 404 }),
    );
    expect(outcome.kind).toBe("route_absent");
  });

  it("422 validation_error -> typed error", async () => {
    const outcome = await run(
      jsonResponse({ state: "validation_error", message: "bad bbl" }, 422),
    );
    expect(outcome.kind).toBe("error");
    if (outcome.kind !== "error") return;
    expect(outcome.state).toBe("validation_error");
    expect(outcome.httpStatus).toBe(422);
  });

  it("502 upstream_error and 500 internal_error -> typed errors", async () => {
    const up = await run(jsonResponse({ state: "upstream_error", message: "x" }, 502));
    expect(up.kind).toBe("error");
    const int = await run(
      jsonResponse({ state: "internal_error", message: "x" }, 500),
    );
    expect(int.kind).toBe("error");
  });

  it("an UNDOCUMENTED (status, state) pair -> unexpected_response", async () => {
    const outcome = await run(jsonResponse({ state: "teapot" }, 418));
    expect(outcome.kind).toBe("unexpected_response");
    if (outcome.kind !== "unexpected_response") return;
    expect(outcome.receivedState).toBe("teapot");
  });

  it("a documented status with an undocumented state -> unexpected_response", async () => {
    // 502 is documented only with specific states; a novel state is a surprise.
    const outcome = await run(jsonResponse({ state: "brand_new_502" }, 502));
    expect(outcome.kind).toBe("unexpected_response");
  });
});

describe("fetchLotGeometry — transport faults", () => {
  it("a thrown fetch -> network_error (safe to retry copy)", async () => {
    const fetchImpl = vi.fn().mockRejectedValue(new Error("offline")) as unknown as typeof fetch;
    const outcome = await fetchLotGeometry(BBL, { fetchImpl });
    expect(outcome.kind).toBe("network_error");
  });

  it("unparseable body -> unexpected_response", async () => {
    const bad = new Response("<<not json>>", {
      status: 200,
      headers: { "content-type": "application/json" },
    });
    const outcome = await run(bad);
    expect(outcome.kind).toBe("unexpected_response");
  });

  it("an already-aborted external signal -> aborted, and NO fetch is issued", async () => {
    const controller = new AbortController();
    controller.abort();
    const fetchImpl = vi.fn() as unknown as typeof fetch;
    const outcome = await fetchLotGeometry(BBL, {
      fetchImpl,
      signal: controller.signal,
    });
    expect(outcome.kind).toBe("aborted");
    expect(fetchImpl).not.toHaveBeenCalled();
  });

  it("the client timeout aborts and resolves to client_timeout", async () => {
    // A fetch that never resolves until aborted models a hung upstream.
    const fetchImpl = vi.fn((_url: unknown, init: { signal: AbortSignal }) => {
      return new Promise<Response>((_res, rej) => {
        init.signal.addEventListener("abort", () => rej(new Error("aborted")));
      });
    }) as unknown as typeof fetch;
    const outcome = await fetchLotGeometry(BBL, { fetchImpl, timeoutMs: 5 });
    expect(outcome.kind).toBe("client_timeout");
    if (outcome.kind !== "client_timeout") return;
    expect(outcome.timeoutMs).toBe(5);
  });

  it("a non-Response resolution (misbehaving fetch) -> unexpected_response, not a crash", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(undefined) as unknown as typeof fetch;
    const outcome = await fetchLotGeometry(BBL, { fetchImpl });
    expect(outcome.kind).toBe("unexpected_response");
  });
});

describe("validateOutlineGeometry — structural pass-through (never measurement)", () => {
  it("preserves a Polygon with an interior hole exactly (no hole filled)", () => {
    const exterior = [
      [-74, 40.7],
      [-73.99, 40.7],
      [-73.99, 40.71],
      [-74, 40.71],
      [-74, 40.7],
    ];
    const hole = [
      [-73.998, 40.702],
      [-73.992, 40.702],
      [-73.992, 40.708],
      [-73.998, 40.708],
      [-73.998, 40.702],
    ];
    const geom = { type: "Polygon", coordinates: [exterior, hole] };
    const validated = validateOutlineGeometry(geom);
    expect(validated).toEqual(geom);
    expect(validated?.coordinates).toHaveLength(2); // exterior + hole both kept
  });

  it("preserves a MultiPolygon's polygon count", () => {
    const poly = [
      [
        [-74, 40.7],
        [-73.99, 40.7],
        [-73.99, 40.71],
        [-74, 40.7],
      ],
    ];
    const geom = { type: "MultiPolygon", coordinates: [poly, poly] };
    expect(validateOutlineGeometry(geom)).toEqual(geom);
  });

  it("rejects non-finite / non-number coordinates and non-polygon geometry", () => {
    expect(
      validateOutlineGeometry({ type: "Polygon", coordinates: [[["a", 1]]] }),
    ).toBeNull();
    expect(validateOutlineGeometry({ type: "Point", coordinates: [1, 2] })).toBeNull();
    expect(validateOutlineGeometry(null)).toBeNull();
  });
});
