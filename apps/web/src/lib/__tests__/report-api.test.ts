import { describe, expect, it, vi } from "vitest";
import { fetchReport, sanitizeReportAddress, type ReportRequestBody } from "@/lib/report-api";

/**
 * M5-T153 scenario S4 [WIRING]: the report client POSTs the SAME body the results form sends to the
 * report route and classifies the answer into ONE plain state. The real route arrives with M5-T151;
 * here the route is STUBBED with the shape of ruling X9 d (a 200 text/html body carrying the report
 * HTML string). No status code, route or field name is carried into any user-facing message.
 */

const BBL = "4073340070";
const BODY: ReportRequestBody = { housing_program: "standard_residence" };

/** A text/html response, as the real report route answers (ruling X9 d). */
function htmlResponse(html: string, status = 200): Response {
  return new Response(html, { status, headers: { "Content-Type": "text/html; charset=utf-8" } });
}
function jsonResponse(body: unknown, status: number): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
function stub(response: Response) {
  return { fetchImpl: (async () => response) as typeof fetch };
}

const REPORT_HTML = "<!doctype html><html><head><title>Report</title></head><body><h1>Decision summary</h1></body></html>";

describe("fetchReport — the report route's answers route to one plain state [WIRING]", () => {
  it("POSTs the same body the results form sends to the report route", async () => {
    const fetchImpl = vi.fn(async () => htmlResponse(REPORT_HTML));
    await fetchReport(
      BBL,
      { housing_program: "standard_residence", floor_to_floor_ft: 14, special_density_statement: true },
      { fetchImpl: fetchImpl as unknown as typeof fetch },
    );
    expect(fetchImpl).toHaveBeenCalledTimes(1);
    const [url, init] = fetchImpl.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toContain(`/api/v1/properties/${BBL}/report`);
    expect(init.method).toBe("POST");
    expect(JSON.parse(String(init.body))).toEqual({
      housing_program: "standard_residence",
      floor_to_floor_ft: 14,
      special_density_statement: true,
    });
  });

  it("classifies a 200 text/html body as success and carries the report HTML", async () => {
    const outcome = await fetchReport(BBL, BODY, stub(htmlResponse(REPORT_HTML)));
    expect(outcome.kind).toBe("success");
    if (outcome.kind === "success") expect(outcome.html).toBe(REPORT_HTML);
  });

  it("classifies a 404 as not_available (route off / not mounted yet)", async () => {
    const outcome = await fetchReport(BBL, BODY, stub(jsonResponse({ detail: "Not Found" }, 404)));
    expect(outcome.kind).toBe("not_available");
  });

  it("classifies a 503 gating refusal with the server's own plain message", async () => {
    const message = "The report is not available for this lot until a recorded fact can be read.";
    const outcome = await fetchReport(
      BBL,
      BODY,
      stub(jsonResponse({ state: "lot_conditions_unconfirmed", message }, 503)),
    );
    expect(outcome.kind).toBe("refused");
    if (outcome.kind === "refused") {
      expect(outcome.message).toBe(message);
      // No status code, route or field name reaches the user-facing message (ruling X6).
      expect(outcome.message).not.toMatch(/503|\/report|lot_conditions_unconfirmed/);
    }
  });

  it("classifies a 422 refusal with no message as refused with a default plain line", async () => {
    const outcome = await fetchReport(BBL, BODY, stub(jsonResponse({ state: "validation_error" }, 422)));
    expect(outcome.kind).toBe("refused");
    if (outcome.kind === "refused") expect(outcome.message.length).toBeGreaterThan(0);
  });

  it("classifies a transport failure as a plain error", async () => {
    const outcome = await fetchReport(BBL, BODY, {
      fetchImpl: (async () => {
        throw new Error("ECONNRESET");
      }) as typeof fetch,
    });
    expect(outcome.kind).toBe("error");
  });

  it("classifies a 500 and a non-HTML 200 as a plain error", async () => {
    expect((await fetchReport(BBL, BODY, stub(jsonResponse({ state: "internal_error" }, 500)))).kind).toBe(
      "error",
    );
    expect((await fetchReport(BBL, BODY, stub(jsonResponse({ ok: true }, 200)))).kind).toBe("error");
    expect((await fetchReport(BBL, BODY, stub(htmlResponse("   ")))).kind).toBe("error");
  });

  it("returns aborted when the signal is already aborted (never calls fetch)", async () => {
    const fetchImpl = vi.fn(async () => htmlResponse(REPORT_HTML));
    const outcome = await fetchReport(BBL, BODY, {
      fetchImpl: fetchImpl as unknown as typeof fetch,
      signal: AbortSignal.abort(),
    });
    expect(outcome.kind).toBe("aborted");
    expect(fetchImpl).not.toHaveBeenCalled();
  });
});

describe("fetchReport — the optional street address query parameter (S9)", () => {
  it("carries the street address as ?address=<encoded> when the website knows it", async () => {
    const fetchImpl = vi.fn(async () => htmlResponse(REPORT_HTML));
    await fetchReport(BBL, BODY, {
      fetchImpl: fetchImpl as unknown as typeof fetch,
      address: "215-16 Northern Boulevard, Queens",
    });
    const url = (fetchImpl.mock.calls[0] as unknown as [string])[0];
    expect(url).toContain(`/${BBL}/report?address=`);
    expect(new URL(url).searchParams.get("address")).toBe("215-16 Northern Boulevard, Queens");
  });

  it("sends no parameter when no address is known", async () => {
    const fetchImpl = vi.fn(async () => htmlResponse(REPORT_HTML));
    await fetchReport(BBL, BODY, { fetchImpl: fetchImpl as unknown as typeof fetch });
    const url = (fetchImpl.mock.calls[0] as unknown as [string])[0];
    expect(url).toContain(`/${BBL}/report`);
    expect(url).not.toContain("?address=");
  });

  it("trims, strips and caps an over-long or dirty address to the server's rule", async () => {
    const fetchImpl = vi.fn(async () => htmlResponse(REPORT_HTML));
    const overLong = `  ${"A".repeat(200)}  `;
    await fetchReport(BBL, BODY, { fetchImpl: fetchImpl as unknown as typeof fetch, address: overLong });
    const url = (fetchImpl.mock.calls[0] as unknown as [string])[0];
    expect((new URL(url).searchParams.get("address") ?? "").length).toBe(120);
  });

  it("sanitizeReportAddress trims, strips disallowed characters, caps to 120, and empties to null", () => {
    expect(sanitizeReportAddress("  215-16 Northern Blvd, Queens  ")).toBe("215-16 Northern Blvd, Queens");
    expect(sanitizeReportAddress("12 Main St* (Apt 4!)")).toBe("12 Main St Apt 4");
    expect((sanitizeReportAddress("A".repeat(200)) ?? "").length).toBe(120);
    expect(sanitizeReportAddress("")).toBeNull();
    expect(sanitizeReportAddress("   ")).toBeNull();
    expect(sanitizeReportAddress(undefined)).toBeNull();
    expect(sanitizeReportAddress("=@%")).toBeNull();
  });
});
