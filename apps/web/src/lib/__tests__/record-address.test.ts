import { describe, expect, it } from "vitest";
import {
  fetchRecordAddress,
  normalizeAddressForCompare,
  recordAddressDiffersFromMatched,
} from "../record-address";

/**
 * M5-T047 (DB-032): the record-address channel client + the differ helper the
 * confirm card uses to decide whether to show the labeled city-record line.
 * Deterministic — every case drives a mocked fetch or a pure function; no
 * network. The fixture basis is corpus §6: PLUTO.address "3622 13 AVENUE",
 * version "26v2" for bbl 3052960043 (matched frontage "1279 37 STREET").
 */

const HTTP_CID = "ra-http-cid-1234";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json", "X-Correlation-ID": HTTP_CID },
  });
}

function recordDoc(over: Record<string, unknown> = {}) {
  return {
    document_kind: "record_address",
    bbl: "3052960043",
    outcome: "address_of_record",
    address: "3622 13 AVENUE",
    reason: null,
    source: {
      source_id: "nyc-dcp-pluto-soda",
      dataset_id: "64uk-42ks",
      dataset_version: "26v2",
      retrieved_at: "2026-09-19T04:00:03Z",
      request_url:
        "https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=3052960043",
    },
    ...over,
  };
}

/** A fetch stub that resolves once with `response`. */
const once =
  (response: Response): typeof fetch =>
  async () =>
    response;

describe("fetchRecordAddress — typed outcomes", () => {
  it("address_of_record: returns the verbatim PLUTO address + provenance", async () => {
    const result = await fetchRecordAddress("3052960043", {
      fetchImpl: once(jsonResponse(recordDoc())),
    });
    expect(result.kind).toBe("document");
    if (result.kind !== "document") return;
    expect(result.view.outcome).toBe("address_of_record");
    expect(result.view.address).toBe("3622 13 AVENUE");
    expect(result.view.source.datasetVersion).toBe("26v2");
    expect(result.view.source.sourceId).toBe("nyc-dcp-pluto-soda");
    expect(result.correlationId).toBe(HTTP_CID);
  });

  it("no_address_of_record: honest absence (address null), still a document", async () => {
    const result = await fetchRecordAddress("3052960043", {
      fetchImpl: once(
        jsonResponse(
          recordDoc({ outcome: "no_address_of_record", address: null, reason: "no address column" }),
        ),
      ),
    });
    expect(result.kind).toBe("document");
    if (result.kind !== "document") return;
    expect(result.view.outcome).toBe("no_address_of_record");
    expect(result.view.address).toBeNull();
  });

  it("no_record: honest absence for a lot with no PLUTO record", async () => {
    const result = await fetchRecordAddress("3052960043", {
      fetchImpl: once(
        jsonResponse(recordDoc({ outcome: "no_record", address: null, reason: "no record" })),
      ),
    });
    expect(result.kind === "document" && result.view.outcome).toBe("no_record");
  });

  it("a blank address string is treated as absence (never an empty line)", async () => {
    const result = await fetchRecordAddress("3052960043", {
      fetchImpl: once(jsonResponse(recordDoc({ address: "   " }))),
    });
    expect(result.kind === "document" && result.view.address).toBeNull();
  });

  it("generic 404 (flag off / unmounted) is a first-class route_absent, never an error", async () => {
    const result = await fetchRecordAddress("3052960043", {
      fetchImpl: once(jsonResponse({ detail: "Not Found" }, 404)),
    });
    expect(result).toEqual({ kind: "route_absent", httpStatus: 404 });
  });

  it("a connector 502 source_unavailable surfaces as a typed error", async () => {
    const result = await fetchRecordAddress("3052960043", {
      fetchImpl: once(
        jsonResponse({ state: "source_unavailable", message: "SODA down" }, 502),
      ),
    });
    expect(result.kind).toBe("error");
    if (result.kind !== "error") return;
    expect(result.state).toBe("source_unavailable");
    expect(result.httpStatus).toBe(502);
  });

  it("a 429 rate_limited surfaces as a typed error", async () => {
    const result = await fetchRecordAddress("3052960043", {
      fetchImpl: once(jsonResponse({ state: "rate_limited", message: "slow down" }, 429)),
    });
    expect(result.kind === "error" && result.state).toBe("rate_limited");
  });

  it("a 422 validation_error surfaces as a typed error", async () => {
    const result = await fetchRecordAddress("not-a-bbl", {
      fetchImpl: once(jsonResponse({ state: "validation_error", message: "bad bbl" }, 422)),
    });
    expect(result.kind === "error" && result.state).toBe("validation_error");
  });

  it("a transport failure is a network_error (safe to retry)", async () => {
    const result = await fetchRecordAddress("3052960043", {
      fetchImpl: async () => {
        throw new Error("offline");
      },
    });
    expect(result.kind).toBe("network_error");
  });

  it("a 200 body with the wrong document_kind is unexpected_response", async () => {
    const result = await fetchRecordAddress("3052960043", {
      fetchImpl: once(jsonResponse({ document_kind: "lot_outline", outcome: "single_lot" })),
    });
    expect(result.kind).toBe("unexpected_response");
  });

  it("an undocumented (status,state) pair is unexpected_response", async () => {
    const result = await fetchRecordAddress("3052960043", {
      fetchImpl: once(jsonResponse({ state: "teapot" }, 418)),
    });
    expect(result.kind).toBe("unexpected_response");
  });

  it("a slow reply past the deadline is a distinct client_timeout", async () => {
    // The fetch respects the abort signal (as a real fetch does), rejecting when
    // the deadline aborts the controller.
    const fetchImpl: typeof fetch = (_url, init) =>
      new Promise((_resolve, reject) => {
        init?.signal?.addEventListener("abort", () =>
          reject(new DOMException("Aborted", "AbortError")),
        );
      });
    const result = await fetchRecordAddress("3052960043", { fetchImpl, timeoutMs: 5 });
    expect(result).toEqual({ kind: "client_timeout", timeoutMs: 5 });
  });

  it("an externally-aborted request returns aborted", async () => {
    const controller = new AbortController();
    controller.abort();
    const result = await fetchRecordAddress("3052960043", {
      signal: controller.signal,
      fetchImpl: once(jsonResponse(recordDoc())),
    });
    expect(result).toEqual({ kind: "aborted" });
  });
});

describe("recordAddressDiffersFromMatched / normalizeAddressForCompare", () => {
  it("true when the record address differs from the matched frontage (corner lot)", () => {
    expect(recordAddressDiffersFromMatched("3622 13 AVENUE", "1279 37 STREET")).toBe(true);
  });

  it("false when they are equal after normalization (case/whitespace-insensitive)", () => {
    expect(recordAddressDiffersFromMatched("120 broadway", "120 BROADWAY")).toBe(false);
    expect(recordAddressDiffersFromMatched("  120   BROADWAY ", "120 BROADWAY")).toBe(false);
  });

  it("false when the record address is absent (null) or blank", () => {
    expect(recordAddressDiffersFromMatched(null, "120 BROADWAY")).toBe(false);
    expect(recordAddressDiffersFromMatched("   ", "120 BROADWAY")).toBe(false);
  });

  it("normalizeAddressForCompare collapses whitespace, trims, and upper-cases", () => {
    expect(normalizeAddressForCompare("  3622   13\tavenue ")).toBe("3622 13 AVENUE");
  });
});
