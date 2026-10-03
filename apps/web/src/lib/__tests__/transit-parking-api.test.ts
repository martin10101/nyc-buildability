import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import { jsonResponse } from "@/test-support/fixtures";
import {
  fetchTransitParking,
  validateTransitParkingDocument,
} from "@/lib/transit-parking-api";

/**
 * Typed client for GET /api/v1/properties/{bbl}/transit-parking (lane C packet
 * W3, plan check C-8 / queue item B-10). Fully offline: every fetch is an
 * injected fetchImpl (no global fetch, no network), mirroring the accepted
 * study-setup-api.test.ts discipline. Proves: documented (status, state) pairs
 * route to typed outcomes; every 200 is contract-validated before use; the
 * document carries the zone ONLY (no parking-outcome field survives the client
 * contract check). The 200 bodies are the COMMITTED contract fixtures read from
 * disk (deep-cloned per read), so the shape asserted IS the recorded contract
 * shape, never a literal retyped here.
 */

const FIXTURE_ROOT = resolve(
  process.cwd(),
  "../../packages/contracts/fixtures/valid/transit_parking",
);

const PROPERTY_BBL = "5999999999";

/** A fresh deep copy of a committed valid fixture (re-parsed from disk each call,
 * so a test that mutates its copy cannot corrupt the others). */
function recordedDocument(): Record<string, unknown> {
  return JSON.parse(readFileSync(resolve(FIXTURE_ROOT, "synthetic_recorded.json"), "utf8"));
}

function checkNeededDocument(): Record<string, unknown> {
  return JSON.parse(readFileSync(resolve(FIXTURE_ROOT, "synthetic_check_needed.json"), "utf8"));
}

function stub(response: Response) {
  return { fetchImpl: (async () => response) as typeof fetch };
}

describe("fetchTransitParking — documented pairs route to typed outcomes", () => {
  it("classifies a valid 200 recorded transit/parking body", async () => {
    const outcome = await fetchTransitParking(
      PROPERTY_BBL,
      stub(jsonResponse(recordedDocument(), 200, "corr-200")),
    );
    expect(outcome.kind).toBe("status");
    if (outcome.kind === "status") {
      expect(outcome.status.status).toBe("recorded");
      expect(outcome.status.transit_zone).toBe("Outer Transit Zone");
      expect(outcome.status.missing_source).toBeNull();
      expect(outcome.correlationId).toBe("corr-200");
    }
  });

  it("classifies a valid 200 check_needed body", async () => {
    const outcome = await fetchTransitParking(
      PROPERTY_BBL,
      stub(jsonResponse(checkNeededDocument(), 200)),
    );
    expect(outcome.kind).toBe("status");
    if (outcome.kind === "status") {
      expect(outcome.status.status).toBe("check_needed");
      expect(outcome.status.transit_zone).toBeNull();
      // The adapter has no transitional phase: it validates the 1.1.0 document the
      // check-needed fixture carries. The id lives in the Source-disclosure ref
      // (request D-2, D-090-R095); the face string names DCP Transit Zones, id-free.
      expect(outcome.status.missing_source).toContain("DCP Transit Zones");
      expect(outcome.status.missing_source).not.toContain("6ztr-wgff");
      expect(outcome.status.missing_source_ref?.dataset_id).toBe("6ztr-wgff");
    }
  });

  it("classifies a 404 as not_available (flag off / unmounted)", async () => {
    const outcome = await fetchTransitParking(
      PROPERTY_BBL,
      stub(jsonResponse({ detail: "Not Found" }, 404)),
    );
    expect(outcome.kind).toBe("not_available");
  });

  it("classifies 422 validation_error with detail.code", async () => {
    const body = {
      state: "validation_error",
      message: "BBL tax block must be 1-99999",
      detail: { code: "invalid_block", raw_value: "'x'" },
    };
    const outcome = await fetchTransitParking("x", stub(jsonResponse(body, 422)));
    expect(outcome.kind).toBe("validation_error");
    if (outcome.kind === "validation_error") {
      expect(outcome.code).toBe("invalid_block");
    }
  });

  it("classifies 503 inputs_unavailable as a retryable outcome", async () => {
    const body = { state: "inputs_unavailable", message: "not available right now" };
    const outcome = await fetchTransitParking(PROPERTY_BBL, stub(jsonResponse(body, 503)));
    expect(outcome.kind).toBe("inputs_unavailable");
  });

  it("classifies 500 internal_contract_error as a server contract error", async () => {
    const body = { state: "internal_contract_error", message: "refused" };
    const outcome = await fetchTransitParking(PROPERTY_BBL, stub(jsonResponse(body, 500)));
    expect(outcome.kind).toBe("server_contract_error");
  });

  it("classifies 500 internal_error", async () => {
    const body = { state: "internal_error", message: "unexpected internal error" };
    const outcome = await fetchTransitParking(PROPERTY_BBL, stub(jsonResponse(body, 500)));
    expect(outcome.kind).toBe("internal_error");
  });

  it("rejects a 200 whose body fails client contract validation", async () => {
    const doc = recordedDocument();
    // Displace a real field: a `recorded` status whose transit_zone is null fails
    // the coherence rule (recorded must carry a zone). Reverting this restores the
    // `status` outcome, so the client guard is the thing under test (red/green).
    doc.transit_zone = null;
    const outcome = await fetchTransitParking(PROPERTY_BBL, stub(jsonResponse(doc, 200)));
    expect(outcome.kind).toBe("validation_failure");
    if (outcome.kind === "validation_failure") {
      expect(outcome.problems.length).toBeGreaterThan(0);
    }
    // The untouched fixture still classifies as a status (the revert).
    const ok = await fetchTransitParking(PROPERTY_BBL, stub(jsonResponse(recordedDocument(), 200)));
    expect(ok.kind).toBe("status");
  });

  it("classifies an undocumented (status, state) pair as unexpected_response", async () => {
    const outcome = await fetchTransitParking(
      PROPERTY_BBL,
      stub(jsonResponse({ state: "no_match" }, 200)),
    );
    expect(outcome.kind).toBe("unexpected_response");
  });

  it("classifies a browser-level failure as network_error", async () => {
    const outcome = await fetchTransitParking(PROPERTY_BBL, {
      fetchImpl: (async () => {
        throw new TypeError("Failed to fetch");
      }) as typeof fetch,
    });
    expect(outcome.kind).toBe("network_error");
  });

  it("resolves a pre-aborted request to the aborted outcome", async () => {
    const controller = new AbortController();
    controller.abort();
    const outcome = await fetchTransitParking(PROPERTY_BBL, {
      signal: controller.signal,
      fetchImpl: (async () => jsonResponse(recordedDocument(), 200)) as typeof fetch,
    });
    expect(outcome.kind).toBe("aborted");
  });

  it("requests the transit-parking path for the BBL (no query)", async () => {
    let seenUrl = "";
    const fetchImpl = (async (input: Parameters<typeof fetch>[0]) => {
      seenUrl = String(input);
      return jsonResponse(recordedDocument(), 200);
    }) as typeof fetch;
    await fetchTransitParking(PROPERTY_BBL, { fetchImpl });
    expect(seenUrl.endsWith(`/api/v1/properties/${PROPERTY_BBL}/transit-parking`)).toBe(true);
    expect(seenUrl.includes("?")).toBe(false);
  });
});

describe("validateTransitParkingDocument", () => {
  it("accepts a contract-valid recorded status", () => {
    expect(validateTransitParkingDocument(recordedDocument()).ok).toBe(true);
  });

  it("accepts a contract-valid check_needed status", () => {
    expect(validateTransitParkingDocument(checkNeededDocument()).ok).toBe(true);
  });

  it("rejects a non-object body", () => {
    expect(validateTransitParkingDocument(null).ok).toBe(false);
    expect(validateTransitParkingDocument([]).ok).toBe(false);
  });

  it("rejects a document missing a required key", () => {
    const doc = recordedDocument();
    delete doc.detail;
    const result = validateTransitParkingDocument(doc);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.problems.some((p) => p.includes("detail"))).toBe(true);
  });

  it("rejects a parking-outcome field: the document carries the zone only", () => {
    // The zone only - never spaces, a waiver or an exemption (Lane A / G6). A body
    // that smuggles a parking-outcome field is refused by the closed key set.
    const doc = recordedDocument();
    (doc as Record<string, unknown>).parking_spaces = 16;
    const result = validateTransitParkingDocument(doc);
    expect(result.ok).toBe(false);
    // The closed key set (checkKeys -> checkNoUnknownKeys) reports the offending
    // document by path + "outside the documented key set", not by the key name.
    // This problem is emitted ONLY when the extra key is rejected, so the test
    // fails if the validator were weakened to accept it.
    if (!result.ok) {
      expect(
        result.problems.some((p) =>
          p.includes("transit_parking: carries a key outside the documented key set"),
        ),
      ).toBe(true);
    }
  });

  it("rejects an incoherent status (recorded with no transit zone)", () => {
    const doc = recordedDocument();
    doc.transit_zone = null;
    const result = validateTransitParkingDocument(doc);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.problems.some((p) => p.includes("transit_zone"))).toBe(true);
  });

  it("rejects a check_needed status that carries a transit zone", () => {
    const doc = checkNeededDocument();
    doc.transit_zone = "Outer Transit Zone";
    const result = validateTransitParkingDocument(doc);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.problems.some((p) => p.includes("transit_zone"))).toBe(true);
  });

  it("rejects a wrong contract_version", () => {
    const doc = recordedDocument();
    doc.contract_version = "9.9.9";
    const result = validateTransitParkingDocument(doc);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.problems.some((p) => p.includes("contract_version"))).toBe(true);
  });

  it("accepts both the 1.0.0 and 1.1.0 contract versions", () => {
    const v10 = recordedDocument();
    v10.contract_version = "1.0.0";
    delete v10.missing_source_ref; // a 1.0.0 body omits the key
    expect(validateTransitParkingDocument(v10).ok).toBe(true);
    expect(validateTransitParkingDocument(recordedDocument()).ok).toBe(true); // 1.1.0
  });
});

describe("validateTransitParkingDocument — missing_source_ref (contract 1.1.0)", () => {
  it("accepts the structured ref object the check-needed fixture carries", () => {
    const result = validateTransitParkingDocument(checkNeededDocument());
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.status.missing_source_ref?.dataset_id).toBe("6ztr-wgff");
      expect(result.status.missing_source_ref?.components?.[0]?.dataset_id).toBe("vhqf-adkz");
    }
  });

  it("accepts a null ref (the recorded fixture: no source to reference)", () => {
    const doc = recordedDocument();
    expect(doc.missing_source_ref).toBeNull();
    expect(validateTransitParkingDocument(doc).ok).toBe(true);
  });

  it("accepts a document that omits missing_source_ref (a 1.0.0 body)", () => {
    const doc = recordedDocument();
    delete doc.missing_source_ref;
    doc.contract_version = "1.0.0";
    expect(validateTransitParkingDocument(doc).ok).toBe(true);
  });

  it("rejects a ref object missing its required 'dataset'", () => {
    const doc = checkNeededDocument();
    // A deliberate invalid-shape probe: neither branch of the ref anyOf is
    // satisfied (object shape nor null), so the client contract refuses it. The
    // key is typed `unknown` on the document record, so no cast is needed.
    doc.missing_source_ref = { dataset_id: "6ztr-wgff" };
    const result = validateTransitParkingDocument(doc);
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.problems.some((p) => p.includes("missing_source_ref.dataset"))).toBe(true);
    }
  });

  it("rejects a ref whose dataset is empty", () => {
    const doc = checkNeededDocument();
    (doc.missing_source_ref as Record<string, unknown>).dataset = "";
    const result = validateTransitParkingDocument(doc);
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.problems.some((p) => p.includes("missing_source_ref.dataset"))).toBe(true);
    }
  });

  it("rejects a ref that is not an object or null", () => {
    const doc = checkNeededDocument();
    doc.missing_source_ref = "6ztr-wgff";
    const result = validateTransitParkingDocument(doc);
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.problems.some((p) => p.includes("missing_source_ref"))).toBe(true);
    }
  });
});
