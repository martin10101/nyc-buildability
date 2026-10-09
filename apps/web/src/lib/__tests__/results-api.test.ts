import { describe, expect, it, vi } from "vitest";
import { jsonResponse } from "@/test-support/fixtures";
import { loadResultsFixture } from "@/test-support/results-fixtures";
import { fetchResults, type ResultsRequestBody } from "@/lib/results-api";

/**
 * W-1 [WIRING] (task M5-T140): the typed client maps every server answer of the route's
 * RESULTS_READ_STATUS_STATE_MATRIX to its outcome, verifies the 200 body against the website's
 * own check before trusting it, and classifies browser-level failures. Nothing here reads a
 * legal value; the 200 success body is the committed journey document.
 */

const BBL = "4073340070";
const BODY: ResultsRequestBody = { housing_program: "standard_residence" };

function stub(response: Response) {
  return { fetchImpl: (async () => response) as typeof fetch };
}

describe("fetchResults — documented (status, state) pairs route to typed outcomes [WIRING]", () => {
  it("sends a POST with the option body to the results route", async () => {
    const fetchImpl = vi.fn(async () => jsonResponse(loadResultsFixture("recorded_215_16_northern_journey"), 200, "corr-ok"));
    const outcome = await fetchResults(
      BBL,
      { housing_program: "standard_residence", floor_to_floor_ft: 14, special_density_statement: true },
      { fetchImpl: fetchImpl as unknown as typeof fetch },
    );
    expect(outcome.kind).toBe("success");
    expect(fetchImpl).toHaveBeenCalledTimes(1);
    const [url, init] = fetchImpl.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toContain(`/api/v1/properties/${BBL}/results`);
    expect(init.method).toBe("POST");
    expect(JSON.parse(String(init.body))).toEqual({
      housing_program: "standard_residence",
      floor_to_floor_ft: 14,
      special_density_statement: true,
    });
  });

  it("classifies a valid 200 results body as success and carries the document + correlation id", async () => {
    const outcome = await fetchResults(
      BBL,
      BODY,
      stub(jsonResponse(loadResultsFixture("recorded_215_16_northern_journey"), 200, "corr-200")),
    );
    expect(outcome.kind).toBe("success");
    if (outcome.kind === "success") {
      expect(outcome.document.answers.building_option.status).toBe("not_available");
      expect(outcome.correlationId).toBe("corr-200");
    }
  });

  it("classifies a 404 as not_available (flag off / unmounted)", async () => {
    const outcome = await fetchResults(BBL, BODY, stub(jsonResponse({ detail: "Not Found" }, 404)));
    expect(outcome.kind).toBe("not_available");
  });

  it("classifies 422 validation_error with its code and field", async () => {
    const body = {
      state: "validation_error",
      message: "the floor-to-floor height must be a positive, finite number of feet",
      detail: { code: "floor_to_floor_ft_invalid", field: "floor_to_floor_ft" },
    };
    const outcome = await fetchResults(BBL, BODY, stub(jsonResponse(body, 422)));
    expect(outcome.kind).toBe("validation_error");
    if (outcome.kind === "validation_error") {
      expect(outcome.code).toBe("floor_to_floor_ft_invalid");
      expect(outcome.field).toBe("floor_to_floor_ft");
      expect(outcome.message).toContain("positive, finite");
    }
  });

  it("classifies 429 rate_limited", async () => {
    const body = { state: "rate_limited", message: "per-caller rate limit exceeded; retry later" };
    const outcome = await fetchResults(BBL, BODY, stub(jsonResponse(body, 429)));
    expect(outcome.kind).toBe("rate_limited");
  });

  it("classifies 503 inputs_unavailable (safe to retry)", async () => {
    const body = { state: "inputs_unavailable", message: "not available right now; safe to retry" };
    const outcome = await fetchResults(BBL, BODY, stub(jsonResponse(body, 503)));
    expect(outcome.kind).toBe("inputs_unavailable");
  });

  it("classifies 503 lot_conditions_unconfirmed (distinct from inputs_unavailable)", async () => {
    const body = {
      state: "lot_conditions_unconfirmed",
      message: "a recorded fact needed to work out this lot's results could not be read",
    };
    const outcome = await fetchResults(BBL, BODY, stub(jsonResponse(body, 503)));
    expect(outcome.kind).toBe("lot_conditions_unconfirmed");
  });

  it("classifies the two 500 states apart", async () => {
    const internal = await fetchResults(
      BBL,
      BODY,
      stub(jsonResponse({ state: "internal_error", message: "unexpected internal error" }, 500)),
    );
    expect(internal.kind).toBe("internal_error");
    const contract = await fetchResults(
      BBL,
      BODY,
      stub(jsonResponse({ state: "internal_contract_error", message: "held back" }, 500)),
    );
    expect(contract.kind).toBe("internal_contract_error");
  });

  it("classifies a 200 body that fails the website's own check as validation_failure", async () => {
    // A 200 that is not the three-way layer: the website refuses it and renders nothing of it.
    const outcome = await fetchResults(BBL, BODY, stub(jsonResponse({ contract_version: "1.0.0" }, 200)));
    expect(outcome.kind).toBe("validation_failure");
    if (outcome.kind === "validation_failure") expect(outcome.problems.length).toBeGreaterThan(0);
  });

  it("classifies a browser-level failure as network_error", async () => {
    const outcome = await fetchResults(BBL, BODY, {
      fetchImpl: (async () => {
        throw new TypeError("Failed to fetch");
      }) as typeof fetch,
    });
    expect(outcome.kind).toBe("network_error");
  });

  it("resolves a pre-aborted request to the aborted outcome (no call result is shown)", async () => {
    const controller = new AbortController();
    controller.abort();
    const outcome = await fetchResults(BBL, BODY, {
      signal: controller.signal,
      fetchImpl: (async () => jsonResponse({ contract_version: "1.3.0" }, 200)) as typeof fetch,
    });
    expect(outcome.kind).toBe("aborted");
  });

  it("resolves a timed-out request to client_timeout", async () => {
    const outcome = await fetchResults(BBL, BODY, {
      timeoutMs: 5,
      fetchImpl: ((_url: string, init: RequestInit) =>
        new Promise((_resolve, reject) => {
          const signal = init.signal as AbortSignal;
          signal.addEventListener("abort", () =>
            reject(new DOMException("aborted", "AbortError")),
          );
        })) as unknown as typeof fetch,
    });
    expect(outcome.kind).toBe("client_timeout");
  });

  it("classifies an undocumented (status, state) pair as unexpected_response", async () => {
    const outcome = await fetchResults(BBL, BODY, stub(jsonResponse({ state: "teapot" }, 418)));
    expect(outcome.kind).toBe("unexpected_response");
    if (outcome.kind === "unexpected_response") expect(outcome.httpStatus).toBe(418);
  });
});
