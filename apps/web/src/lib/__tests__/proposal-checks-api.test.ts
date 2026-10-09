import { describe, expect, it } from "vitest";
import {
  announcementForProposalCheck,
  fetchProposalCheck,
  isDocumentedProposalPair,
  MAX_RESPONSE_BYTES,
  proposalCheckOutcomeIsRecoverable,
} from "@/lib/proposal-checks-api";
import { rectangleSampleDraft, toProposalCheckRequest } from "@/lib/architect/proposal-draft";
import {
  attestedReportBody,
  checkResponse,
  markupEchoReportBody,
  stubFetch,
} from "@/test-support/proposal-check-fixtures";

/**
 * Task M5-T060, client layer: EXACT (status, state) pair enforcement mirroring
 * PROPOSAL_CHECKS_STATUS_STATE_MATRIX + the flag-off 404, the 422 `field`
 * decode, the fail-closed Content-Length bound, bounded echoes (DB-039(k)), and
 * the browser-level failure modes.
 */

const REQUEST = toProposalCheckRequest(rectangleSampleDraft());
const rawStub = (response: Response) => (async () => response) as typeof fetch;

describe("isDocumentedProposalPair", () => {
  it("accepts exactly the route matrix plus the flag-off 404", () => {
    expect(isDocumentedProposalPair(200, null)).toBe(true);
    expect(isDocumentedProposalPair(404, null)).toBe(true);
    expect(isDocumentedProposalPair(413, "payload_too_large")).toBe(true);
    expect(isDocumentedProposalPair(422, "validation_error")).toBe(true);
    expect(isDocumentedProposalPair(500, "internal_error")).toBe(true);
    expect(isDocumentedProposalPair(200, "x")).toBe(false);
    expect(isDocumentedProposalPair(404, "no_match")).toBe(false);
  });
});

describe("fetchProposalCheck — envelope classification", () => {
  it("decodes a 200 grouped report with the rectangle arithmetic", async () => {
    const outcome = await fetchProposalCheck(REQUEST, {
      fetchImpl: stubFetch(checkResponse(attestedReportBody(), 200, "corr-1")),
    });
    expect(outcome.kind).toBe("report");
    if (outcome.kind === "report") {
      expect(outcome.report.summary).toEqual({ pass: 1, fail: 1, couldNotCheck: 2, total: 4 });
      expect(outcome.correlationId).toBe("corr-1");
      const cov = outcome.report.results.find((r) => r.checkId === "lot_coverage_ratio")!;
      expect(cov.outcome).toBe("fail");
      expect(cov.providedValue).toBe(0.625);
      expect(cov.requiredValue).toBe(0.5);
      expect(cov.shortfall).toBe(0.125);
      const rear = outcome.report.results.find((r) => r.checkId === "rear_yard_depth")!;
      expect(rear.outcome).toBe("could_not_check");
      expect(rear.semanticGap).toContain("not a rear-yard depth");
    }
  });

  it("maps the generic 404 to feature_unavailable", async () => {
    const outcome = await fetchProposalCheck(REQUEST, {
      fetchImpl: stubFetch(checkResponse({ detail: "Not Found" }, 404, null)),
    });
    expect(outcome.kind).toBe("feature_unavailable");
  });

  it("maps 413 to payload_too_large", async () => {
    const outcome = await fetchProposalCheck(REQUEST, {
      fetchImpl: stubFetch(checkResponse({ state: "payload_too_large", message: "too big", correlation_id: "c" }, 413)),
    });
    expect(outcome.kind).toBe("payload_too_large");
  });

  it("maps 422 validation_error and surfaces the refused field", async () => {
    const body = { state: "validation_error", message: "refused", field: "scenario_label", correlation_id: "c" };
    const outcome = await fetchProposalCheck(REQUEST, { fetchImpl: stubFetch(checkResponse(body, 422)) });
    expect(outcome.kind).toBe("validation_error");
    if (outcome.kind === "validation_error") expect(outcome.field).toBe("scenario_label");
  });

  it("maps 500 internal_error", async () => {
    const outcome = await fetchProposalCheck(REQUEST, {
      fetchImpl: stubFetch(checkResponse({ state: "internal_error", message: "boom", correlation_id: "c" }, 500)),
    });
    expect(outcome.kind).toBe("internal_error");
  });

  it("treats an undocumented (200, state) pair as unexpected_response", async () => {
    const outcome = await fetchProposalCheck(REQUEST, {
      fetchImpl: stubFetch(checkResponse(attestedReportBody({ state: "surprise" }), 200)),
    });
    expect(outcome.kind).toBe("unexpected_response");
  });

  it("rejects a 200 that is not the report contract as validation_failure", async () => {
    const outcome = await fetchProposalCheck(REQUEST, {
      fetchImpl: stubFetch(checkResponse({ results: [], summary: { pass: "x" } }, 200)),
    });
    expect(outcome.kind).toBe("validation_failure");
  });

  it("fails closed to unexpected_response when Content-Length is over budget", async () => {
    const text = JSON.stringify(attestedReportBody());
    const response = new Response(text, {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Content-Length": String(MAX_RESPONSE_BYTES + 1),
        "X-Correlation-ID": "c",
      },
    });
    const outcome = await fetchProposalCheck(REQUEST, { fetchImpl: rawStub(response) });
    expect(outcome.kind).toBe("unexpected_response");
  });

  it("treats a non-JSON 200 body as unexpected_response", async () => {
    const text = "{ not json";
    const response = new Response(text, {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Content-Length": String(text.length),
        "X-Correlation-ID": "c",
      },
    });
    const outcome = await fetchProposalCheck(REQUEST, { fetchImpl: rawStub(response) });
    expect(outcome.kind).toBe("unexpected_response");
  });

  it("classifies a browser-level failure as network_error", async () => {
    const outcome = await fetchProposalCheck(REQUEST, {
      fetchImpl: (async () => {
        throw new TypeError("connection refused");
      }) as typeof fetch,
    });
    expect(outcome.kind).toBe("network_error");
  });

  it("resolves a timed-out request to client_timeout", async () => {
    const outcome = await fetchProposalCheck(REQUEST, {
      timeoutMs: 1,
      fetchImpl: ((_url: string, init?: RequestInit) =>
        new Promise<Response>((_resolve, reject) => {
          init?.signal?.addEventListener("abort", () => reject(new DOMException("aborted", "AbortError")));
        })) as unknown as typeof fetch,
    });
    expect(outcome.kind).toBe("client_timeout");
  });

  it("resolves an externally-aborted request to aborted", async () => {
    const controller = new AbortController();
    controller.abort();
    const outcome = await fetchProposalCheck(REQUEST, {
      signal: controller.signal,
      fetchImpl: stubFetch(checkResponse(attestedReportBody(), 200)),
    });
    expect(outcome.kind).toBe("aborted");
  });

  it("bounds echoed strings but preserves them as text (DB-039(k))", async () => {
    const outcome = await fetchProposalCheck(REQUEST, {
      fetchImpl: stubFetch(checkResponse(markupEchoReportBody(), 200)),
    });
    expect(outcome.kind).toBe("report");
    if (outcome.kind === "report") {
      expect(outcome.report.unmappedLotFacts[0]).toBe("<img src=x onerror=alert(1)>");
      expect(typeof outcome.report.scenarioLabel).toBe("string");
    }
  });
});

/**
 * AS-1 — the UNCHANGED rectangle request paired with its MATCHING response.
 *
 * This is the focused request<->response PAIR for the accepted M5-T054 rectangle:
 * the exact request the editor assembles from the *unedited* rectangleSampleDraft
 * is the one the hand-computed rectangle response fixture (attestedReportBody)
 * was written against. It is deliberately DISTINCT from the edited-draft keyboard
 * serialization journey (proposal-editor.test.tsx / proposal-editor.spec.ts),
 * which retypes vertex 0 X to 1000005 and appends a vertex/level/wall (6 vertices
 * / 2 levels / 5 walls). Here NOTHING is edited: 5 vertices, first
 * [1000000, 200000], 1 level, 4 walls — so the AS-1 arithmetic (coverage 0.625
 * vs 0.5 -> shortfall 0.125; height 30 <= 60) is bound to the canonical
 * rectangle, not to an edited variant, and the capturing stub asserts the exact
 * POST body BEFORE the matching response is decoded.
 */
describe("AS-1 — the unchanged rectangle request paired with its matching response", () => {
  it("POSTs the exact unchanged rectangle contract and decodes the matching rectangle arithmetic", async () => {
    const request = toProposalCheckRequest(rectangleSampleDraft());
    const captured: { body: unknown } = { body: undefined };
    const fetchImpl = (async (_url: string, init?: RequestInit) => {
      const raw = init?.body;
      captured.body = typeof raw === "string" ? JSON.parse(raw) : null;
      return checkResponse(attestedReportBody(), 200, "corr-as1");
    }) as unknown as typeof fetch;

    const outcome = await fetchProposalCheck(request, { fetchImpl });

    // (a) the serialized POST body is the UNCHANGED rectangle request verbatim...
    expect(captured.body).toEqual(request);
    // ...pinned by the anchors that distinguish it from the edited-draft journey:
    expect(request.proposed_massing.outline.srid).toBe(2263);
    expect(request.proposed_massing.outline.vertices).toHaveLength(5); // edited journey: 6
    expect(request.proposed_massing.outline.vertices[0]).toEqual([1000000, 200000]); // edited journey: [1000005, 200000]
    expect(request.proposed_massing.levels).toHaveLength(1); // edited journey: 2
    expect(request.proposed_massing.exterior_walls).toHaveLength(4); // edited journey: 5
    expect(request.lot.area_sq_ft).toBe(8000);
    expect(request.lot_rule_facts).toEqual({ zoning_district: "R5", street_width_class: "wide" });
    expect(request.scenario_label).toBe("scenario-A-baseline");

    // (b) ...and the MATCHING rectangle response decodes to the AS-1 arithmetic.
    expect(outcome.kind).toBe("report");
    if (outcome.kind === "report") {
      expect(outcome.report.summary).toEqual({ pass: 1, fail: 1, couldNotCheck: 2, total: 4 });
      const cov = outcome.report.results.find((r) => r.checkId === "lot_coverage_ratio")!;
      expect([cov.providedValue, cov.requiredValue, cov.shortfall]).toEqual([0.625, 0.5, 0.125]);
      const height = outcome.report.results.find((r) => r.checkId === "building_height")!;
      expect(height.outcome).toBe("pass");
      expect([height.providedValue, height.requiredValue]).toEqual([30, 60]);
    }
  });
});

describe("recoverability + announcements", () => {
  it("marks server/network faults recoverable and results not", () => {
    expect(proposalCheckOutcomeIsRecoverable({ kind: "network_error", message: "" })).toBe(true);
    expect(proposalCheckOutcomeIsRecoverable({ kind: "internal_error", message: "", correlationId: null })).toBe(true);
    expect(proposalCheckOutcomeIsRecoverable({ kind: "feature_unavailable" })).toBe(false);
    expect(
      proposalCheckOutcomeIsRecoverable({ kind: "validation_error", field: null, message: "", correlationId: null }),
    ).toBe(false);
    expect(proposalCheckOutcomeIsRecoverable({ kind: "payload_too_large", message: "", correlationId: null })).toBe(
      false,
    );
  });

  it("announces the report with fail/could-not-check counts and the honesty note; nothing for aborted", async () => {
    const outcome = await fetchProposalCheck(REQUEST, {
      fetchImpl: stubFetch(checkResponse(attestedReportBody(), 200)),
    });
    const message = announcementForProposalCheck(outcome);
    expect(message).toMatch(/did not meet a rule allowance/);
    expect(message).toMatch(/not a city record/);
    expect(message).not.toMatch(/\bverified\b/i);
    expect(announcementForProposalCheck({ kind: "aborted" })).toBe("");
  });
});
