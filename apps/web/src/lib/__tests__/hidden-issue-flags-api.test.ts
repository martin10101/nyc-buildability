import { describe, expect, it } from "vitest";
import validFour from "../../../../../packages/contracts/fixtures/valid/hidden_issue_flags/synthetic_four_groups.json";
import invalidZlhOpportunity from "../../../../../packages/contracts/fixtures/invalid/hidden_issue_flags/zoning_lot_history_opportunity.json";
import { jsonResponse } from "@/test-support/fixtures";
import { fetchHiddenIssueFlags } from "@/lib/hidden-issue-flags-api";
import { validateHiddenIssueFlagsDocument } from "@/lib/hidden-issue-flags-contract-checks";

/**
 * Typed client + contract checks for GET
 * /api/v1/properties/{bbl}/hidden-issue-flags (lane C packet W2). Proves: the
 * documented (status, state) pairs route to typed outcomes; every 200 body is
 * contract-validated before use; and the client contract check enforces the W0
 * shape, including the plan-P-2 "zoning-lot-history is a reminder only" rule.
 */

const PROPERTY_BBL = "5999999999";

type FlagsDoc = {
  contract_version: string;
  groups: Array<{
    group_id: string;
    flags: Array<Record<string, unknown>>;
  }>;
};

/** A fresh deep-clone of the committed valid four-group fixture, so a test that
 * mutates its copy cannot corrupt the shared imported fixture for later tests. */
function validDocument(): FlagsDoc {
  return JSON.parse(JSON.stringify(validFour)) as FlagsDoc;
}

function stub(response: Response) {
  return { fetchImpl: (async () => response) as typeof fetch };
}

describe("fetchHiddenIssueFlags — documented pairs route to typed outcomes", () => {
  it("classifies a valid 200 flags body", async () => {
    const outcome = await fetchHiddenIssueFlags(
      PROPERTY_BBL,
      stub(jsonResponse(validDocument(), 200, "corr-200")),
    );
    expect(outcome.kind).toBe("flags");
    if (outcome.kind === "flags") {
      expect(outcome.document.contract_version).toBe("1.0.0");
      expect(outcome.document.groups.map((g) => g.group_id)).toEqual([
        "existing_building",
        "zoning_lot_history",
        "map_based_rules",
        "site_shape_and_street",
      ]);
      expect(outcome.correlationId).toBe("corr-200");
    }
  });

  it("classifies a 404 as not_available (flag off / unmounted)", async () => {
    const outcome = await fetchHiddenIssueFlags(
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
    const outcome = await fetchHiddenIssueFlags("x", stub(jsonResponse(body, 422)));
    expect(outcome.kind).toBe("validation_error");
    if (outcome.kind === "validation_error") {
      expect(outcome.code).toBe("invalid_block");
    }
  });

  it("classifies 429 rate_limited as a retryable outcome", async () => {
    const body = { state: "rate_limited", message: "per-caller rate limit exceeded; retry later" };
    const outcome = await fetchHiddenIssueFlags(PROPERTY_BBL, stub(jsonResponse(body, 429)));
    expect(outcome.kind).toBe("rate_limited");
  });

  it("classifies 503 inputs_unavailable as a retryable outcome", async () => {
    const body = { state: "inputs_unavailable", message: "not available right now" };
    const outcome = await fetchHiddenIssueFlags(PROPERTY_BBL, stub(jsonResponse(body, 503)));
    expect(outcome.kind).toBe("inputs_unavailable");
  });

  it("classifies 500 internal_contract_error as a server contract error", async () => {
    const body = { state: "internal_contract_error", message: "refused" };
    const outcome = await fetchHiddenIssueFlags(PROPERTY_BBL, stub(jsonResponse(body, 500)));
    expect(outcome.kind).toBe("server_contract_error");
  });

  it("classifies 500 internal_error", async () => {
    const body = { state: "internal_error", message: "unexpected internal error" };
    const outcome = await fetchHiddenIssueFlags(PROPERTY_BBL, stub(jsonResponse(body, 500)));
    expect(outcome.kind).toBe("internal_error");
  });

  it("rejects a 200 whose body fails client contract validation", async () => {
    const doc = validDocument();
    // Displace a real field: break the status/label one-to-one tie. Reverting
    // this restores the `flags` outcome, so the client guard is the thing under
    // test (red/green).
    doc.groups[0].flags[0].status_label = "Flag"; // status is "check_needed"
    const outcome = await fetchHiddenIssueFlags(PROPERTY_BBL, stub(jsonResponse(doc, 200)));
    expect(outcome.kind).toBe("validation_failure");
    if (outcome.kind === "validation_failure") {
      expect(outcome.problems.length).toBeGreaterThan(0);
    }
  });

  it("classifies an undocumented (status, state) pair as unexpected_response", async () => {
    const outcome = await fetchHiddenIssueFlags(
      PROPERTY_BBL,
      stub(jsonResponse({ state: "no_match" }, 200)),
    );
    expect(outcome.kind).toBe("unexpected_response");
  });

  it("maps a thrown fetch to a retryable network_error", async () => {
    const outcome = await fetchHiddenIssueFlags(PROPERTY_BBL, {
      fetchImpl: (async () => {
        throw new Error("down");
      }) as typeof fetch,
    });
    expect(outcome.kind).toBe("network_error");
  });

  it("returns aborted when the external signal is already aborted", async () => {
    const controller = new AbortController();
    controller.abort();
    const outcome = await fetchHiddenIssueFlags(PROPERTY_BBL, {
      signal: controller.signal,
      fetchImpl: (async () => jsonResponse(validDocument(), 200)) as typeof fetch,
    });
    expect(outcome.kind).toBe("aborted");
  });
});

describe("validateHiddenIssueFlagsDocument — W0 contract shape", () => {
  it("accepts the committed valid four-group fixture", () => {
    const result = validateHiddenIssueFlagsDocument(validDocument());
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.document.groups.length).toBe(4);
    }
  });

  it("rejects a status_label that does not match its status", () => {
    const doc = validDocument();
    doc.groups[0].flags[0].status_label = "Opportunity"; // status is "check_needed"
    const result = validateHiddenIssueFlagsDocument(doc);
    expect(result.ok).toBe(false);
  });

  it("enforces plan P-2: zoning-lot-history admits only flag or check_needed", () => {
    // Baseline: the unmutated clone is valid (the mutation is what breaks it).
    expect(validateHiddenIssueFlagsDocument(validDocument()).ok).toBe(true);

    const doc = validDocument();
    const zlh = doc.groups.find((g) => g.group_id === "zoning_lot_history");
    expect(zlh).toBeDefined();
    // 'opportunity' with its matching label passes the label tie but violates P-2.
    zlh!.flags[0].status = "opportunity";
    zlh!.flags[0].status_label = "Opportunity";
    const result = validateHiddenIssueFlagsDocument(doc);
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.problems.some((p) => p.includes("P-2"))).toBe(true);
    }
  });

  it("rejects the committed invalid fixture (zoning-lot-history opportunity)", () => {
    const result = validateHiddenIssueFlagsDocument(
      JSON.parse(JSON.stringify(invalidZlhOpportunity)),
    );
    expect(result.ok).toBe(false);
  });

  it("rejects a non-object body", () => {
    expect(validateHiddenIssueFlagsDocument(null).ok).toBe(false);
    expect(validateHiddenIssueFlagsDocument("x").ok).toBe(false);
  });
});
