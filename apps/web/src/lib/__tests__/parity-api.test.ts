import { describe, expect, it } from "vitest";
import {
  announcementForParity,
  checkParityData,
  fetchParityData,
  isDocumentedParityPair,
  MAX_RESPONSE_BYTES,
  NOT_A_VALUATION_NOTICE,
  NOT_CONFIRMED_LABEL,
  NOT_CONFIRMED_REASON,
  parityOutcomeIsRecoverable,
} from "@/lib/parity-api";
import type { ParityData } from "@/lib/parity-api";

/**
 * Lane C packet W4, client layer: EXACT (status, state) pair enforcement
 * mirroring PARITY_READ_STATUS_STATE_MATRIX + the flag-off 404, the honesty
 * contract check (not-a-valuation + "Not confirmed" pins, banned valuation /
 * capacity / 485-x keys), the fail-closed Content-Length bound, and the
 * browser-level failure modes. Offline: fixtures are deep-cloned before any
 * mutation so one case never leaks into another.
 */

const DOF_SOURCE = {
  kind: "city_dataset" as const,
  source_id: "nyc-dof-annualized-sales-soda",
  dataset_id: "w2pb-icbu",
  dataset: "DOF NYC Citywide Annualized Calendar Sales (w2pb-icbu)",
  request_url: "https://data.cityofnewyork.us/resource/w2pb-icbu.json?x=1",
  retrieved_at: "2026-10-02T11:00:00Z",
  dataset_last_modified: "2026-09-01",
};

function baseParity(): ParityData {
  return {
    contract_version: "1.0.0",
    comparable_sales: {
      subject: {
        bbl: "4073340070",
        building_class_category: "22 STORE BUILDINGS",
        gross_square_feet: 5091,
      },
      criteria: {
        size_tolerance_fraction: 0.5,
        exclude_zero_price: true,
        require_recorded_size: true,
      },
      criteria_text: "Similar type and size; market sales only; the subject lot is excluded.",
      not_a_valuation: NOT_A_VALUATION_NOTICE,
      selected: [
        {
          bbl: "4073140027",
          borough: "4",
          neighborhood: "BAYSIDE",
          block: "7314",
          lot: "27",
          address: "45-30 BELL BOULEVARD",
          zip_code: "11361",
          building_class_category: "22 STORE BUILDINGS",
          building_class_at_time_of_sale: "K1",
          residential_units: 0,
          commercial_units: 1,
          total_units: 1,
          year_built: 1996,
          land_square_feet: 5415,
          gross_square_feet: 3750,
          sale_price: 3700000,
          sale_date: "2025-11-20",
          source: { ...DOF_SOURCE },
        },
      ],
      excluded: [
        { bbl: "4062620025", address: "201-07 NORTHERN BOULEVARD", sale_date: "2025-04-30", reason: "zero_price_transfer" },
      ],
      source: { ...DOF_SOURCE },
    },
    unused_floor_area: {
      lot_bbl: "4073340070",
      role: "subject",
      status: "not_confirmed",
      label: NOT_CONFIRMED_LABEL,
      reason: NOT_CONFIRMED_REASON,
      existing_floor_area_input: {
        known: false,
        value_sq_ft: null,
        unit: null,
        measurement: { rank: "unknown", label: "Unknown — enter" },
        source: null,
        basis: "unknown",
        basis_label: "Unknown — enter",
        note: null,
      },
      detail: "Remaining development capacity: Not confirmed. No number is computed here.",
    },
  };
}

function bodyText(body: unknown): string {
  return JSON.stringify(body);
}

function jsonResponse(
  body: unknown,
  status: number,
  correlationId: string | null = "corr-1",
  contentLengthOverride?: string,
): Response {
  const text = bodyText(body);
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "Content-Length": contentLengthOverride ?? String(new TextEncoder().encode(text).length),
  };
  if (correlationId !== null) headers["X-Correlation-ID"] = correlationId;
  return new Response(text, { status, headers });
}

const stubFetch = (response: Response): typeof fetch =>
  (async () => response) as typeof fetch;

describe("isDocumentedParityPair", () => {
  it("accepts exactly the route matrix plus the flag-off 404", () => {
    expect(isDocumentedParityPair(200, null)).toBe(true);
    expect(isDocumentedParityPair(404, null)).toBe(true);
    expect(isDocumentedParityPair(422, "validation_error")).toBe(true);
    expect(isDocumentedParityPair(429, "rate_limited")).toBe(true);
    expect(isDocumentedParityPair(503, "inputs_unavailable")).toBe(true);
    expect(isDocumentedParityPair(500, "internal_error")).toBe(true);
    expect(isDocumentedParityPair(500, "internal_contract_error")).toBe(true);
    expect(isDocumentedParityPair(200, "x")).toBe(false);
    expect(isDocumentedParityPair(404, "no_match")).toBe(false);
    expect(isDocumentedParityPair(503, null)).toBe(false);
  });
});

describe("checkParityData", () => {
  it("accepts the valid parity document", () => {
    const result = checkParityData(baseParity());
    expect(result.ok).toBe(true);
  });

  it("rejects a tampered not-a-valuation disclosure", () => {
    const bad = structuredClone(baseParity());
    bad.comparable_sales.not_a_valuation =
      "my professional appraisal" as unknown as ParityData["comparable_sales"]["not_a_valuation"];
    const result = checkParityData(bad);
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.problems.some((p) => p.includes("not_a_valuation"))).toBe(true);
    }
  });

  it("rejects an unused-floor-area line that is not 'Not confirmed'", () => {
    const bad = structuredClone(baseParity());
    bad.unused_floor_area.label =
      "Remaining capacity: 12,000 sq ft" as unknown as ParityData["unused_floor_area"]["label"];
    const result = checkParityData(bad);
    expect(result.ok).toBe(false);
  });

  it("rejects a document that smuggles in a banned capacity field", () => {
    const bad = structuredClone(baseParity()) as unknown as Record<string, unknown>;
    (bad.unused_floor_area as Record<string, unknown>).remaining_floor_area = 12000;
    const result = checkParityData(bad);
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.problems.some((p) => p.includes("banned"))).toBe(true);
    }
  });
});

describe("fetchParityData — envelope classification", () => {
  it("decodes a 200 parity document and bounds its disclosure", async () => {
    const outcome = await fetchParityData("4073340070", {
      fetchImpl: stubFetch(jsonResponse(baseParity(), 200, "corr-1")),
    });
    expect(outcome.kind).toBe("parity");
    if (outcome.kind === "parity") {
      expect(outcome.correlationId).toBe("corr-1");
      expect(outcome.data.comparable_sales.selected).toHaveLength(1);
      expect(outcome.disclosure.notAValuation).toContain("not a valuation");
      expect(outcome.disclosure.unusedLabel).toBe(NOT_CONFIRMED_LABEL);
      expect(outcome.disclosure.unusedReason).toBe(NOT_CONFIRMED_REASON);
    }
  });

  it("maps the generic 404 to feature_unavailable", async () => {
    const outcome = await fetchParityData("4073340070", {
      fetchImpl: stubFetch(jsonResponse({ detail: "Not Found" }, 404, null)),
    });
    expect(outcome.kind).toBe("feature_unavailable");
  });

  it("maps 422 validation_error", async () => {
    const body = { state: "validation_error", message: "bad bbl", correlation_id: "c", detail: { code: "x" } };
    const outcome = await fetchParityData("NOT-A-BBL", { fetchImpl: stubFetch(jsonResponse(body, 422)) });
    expect(outcome.kind).toBe("validation_error");
  });

  it("maps 429 rate_limited and is recoverable", async () => {
    const body = { state: "rate_limited", message: "slow down", correlation_id: "c" };
    const outcome = await fetchParityData("4073340070", { fetchImpl: stubFetch(jsonResponse(body, 429)) });
    expect(outcome.kind).toBe("rate_limited");
    expect(parityOutcomeIsRecoverable(outcome)).toBe(true);
  });

  it("maps 503 inputs_unavailable", async () => {
    const body = { state: "inputs_unavailable", message: "withheld", correlation_id: "c" };
    const outcome = await fetchParityData("4073340070", { fetchImpl: stubFetch(jsonResponse(body, 503)) });
    expect(outcome.kind).toBe("inputs_unavailable");
  });

  it("maps 500 internal_error", async () => {
    const body = { state: "internal_error", message: "boom", correlation_id: "c" };
    const outcome = await fetchParityData("4073340070", { fetchImpl: stubFetch(jsonResponse(body, 500)) });
    expect(outcome.kind).toBe("internal_error");
    if (outcome.kind === "internal_error") expect(outcome.state).toBe("internal_error");
  });

  it("maps 500 internal_contract_error and carries the distinguishing state", async () => {
    const body = { state: "internal_contract_error", message: "withheld", correlation_id: "c" };
    const outcome = await fetchParityData("4073340070", { fetchImpl: stubFetch(jsonResponse(body, 500)) });
    expect(outcome.kind).toBe("internal_error");
    if (outcome.kind === "internal_error") expect(outcome.state).toBe("internal_contract_error");
  });

  it("treats an undocumented (200, state) pair as unexpected_response", async () => {
    const tampered = structuredClone(baseParity()) as unknown as Record<string, unknown>;
    tampered.state = "surprise";
    const outcome = await fetchParityData("4073340070", {
      fetchImpl: stubFetch(jsonResponse(tampered, 200)),
    });
    expect(outcome.kind).toBe("unexpected_response");
  });

  it("rejects a 200 that fails the honesty contract as validation_failure", async () => {
    const bad = structuredClone(baseParity());
    bad.comparable_sales.not_a_valuation =
      "an appraisal" as unknown as ParityData["comparable_sales"]["not_a_valuation"];
    const outcome = await fetchParityData("4073340070", { fetchImpl: stubFetch(jsonResponse(bad, 200)) });
    expect(outcome.kind).toBe("validation_failure");
  });

  it("fails closed to unexpected_response when Content-Length is over budget", async () => {
    const outcome = await fetchParityData("4073340070", {
      fetchImpl: stubFetch(jsonResponse(baseParity(), 200, "c", String(MAX_RESPONSE_BYTES + 1))),
    });
    expect(outcome.kind).toBe("unexpected_response");
  });

  it("treats a non-JSON 200 body as unexpected_response", async () => {
    const text = "{ not json";
    const response = new Response(text, {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Content-Length": String(new TextEncoder().encode(text).length),
        "X-Correlation-ID": "c",
      },
    });
    const outcome = await fetchParityData("4073340070", { fetchImpl: stubFetch(response) });
    expect(outcome.kind).toBe("unexpected_response");
  });

  it("maps a transport failure to network_error", async () => {
    const outcome = await fetchParityData("4073340070", {
      fetchImpl: (async () => {
        throw new Error("down");
      }) as typeof fetch,
    });
    expect(outcome.kind).toBe("network_error");
  });

  it("resolves a pre-aborted signal to aborted", async () => {
    const controller = new AbortController();
    controller.abort();
    const outcome = await fetchParityData("4073340070", {
      fetchImpl: stubFetch(jsonResponse(baseParity(), 200)),
      signal: controller.signal,
    });
    expect(outcome.kind).toBe("aborted");
  });
});

describe("announcementForParity", () => {
  it("leads a loaded document with the not-a-valuation framing and 'Not confirmed'", () => {
    const outcome = {
      kind: "parity" as const,
      data: baseParity(),
      disclosure: {
        notAValuation: NOT_A_VALUATION_NOTICE,
        criteriaText: "",
        unusedLabel: NOT_CONFIRMED_LABEL,
        unusedReason: NOT_CONFIRMED_REASON,
        unusedDetail: "",
      },
      correlationId: "c",
    };
    const text = announcementForParity(outcome);
    expect(text).toContain("not a valuation");
    expect(text).toContain("Not confirmed");
  });

  it("announces nothing for a superseded (aborted) request", () => {
    expect(announcementForParity({ kind: "aborted" })).toBe("");
  });
});
