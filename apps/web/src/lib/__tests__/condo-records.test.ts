// Condo-records client acceptance pack (M5-T052, DB-031).
//
// Fully offline: every fetch is an injected fetchImpl (no global fetch, no
// network), mirroring the accepted record-address.test.ts discipline. The suite
// proves (1) the cross-boundary token pin — the web outcome literals EQUAL the
// api resolver's OUTCOME_* vocabulary, pinned identically on both sides; (2) the
// full (status, state) transport matrix and every typed failure outcome; (3)
// provenance carriage — recorded zoning per base lot, dataset version (SODA
// rowsUpdatedAt), and per-record query provenance, unknown ONLY for genuinely
// absent values; (4) the ENTERED unit BBL, the billing BBL, and the ANALYZED
// base BBL are carried as three distinct identifiers; (5) the pure channel-state
// reducer the architect surface consumes.
import { describe, expect, it } from "vitest";
import {
  CONDO_OUTCOME_ERROR,
  CONDO_OUTCOME_MULTI_LOT,
  CONDO_OUTCOME_NOT_CONDO_BILLING,
  CONDO_OUTCOME_RESOLVED_SINGLE,
  CONDO_OUTCOME_UNRESOLVED,
  SITE_DEFINITION_ATTESTATION_SELF_ATTESTED,
  SITE_DEFINITION_CONFIRMATION_STATUS_ACTIVE,
  SITE_DEFINITION_STATUS_CONFIRMED,
  SITE_DEFINITION_STATUS_UNCONFIRMED,
  channelWithholdsAllowances,
  deriveCondoChannelState,
  fetchCondoRecords,
  type CondoRecordsDocumentOutcome,
  type CondoRecordsOutcome,
} from "../condo-records";

const SOURCE_ID = "nyc-dof-dtm-condo-soda";
const DATASET_ID = "p8u6-a6it";
const RETRIEVED_AT = "2026-09-01T14:05:56Z";
const ROWS_UPDATED_AT = "2026-08-30T00:00:00Z";
const DIVERGENT_NOTICE =
  "Divergent zoning across a condo's base lots is a qualified-human legal question.";
const ZONING_DEPENDENCY =
  "Recorded zoning per base lot is not carried by the DOF DTM condo base-lot channel; " +
  "it requires the ZTLDB / spatial zoning-by-BBL lookup (out of scope, routed to the orchestrator).";

const BILLING_BBL = "1003037501";
const BILLING_MULTI_BBL = "1003037502";
const UNIT_BBL = "1003031001";
const BASE_BBL = "1003030019";
const BASE_BBL_2 = "1003030025";

// --- fetch injection helpers (no global fetch) ------------------------------
function makeResponse(
  body: unknown,
  status = 200,
  correlationId: string | null = "corr-1",
): Response {
  return {
    status,
    headers: {
      get: (name: string) =>
        name.toLowerCase() === "x-correlation-id" ? correlationId : null,
    },
    json: async () => body,
  } as unknown as Response;
}

function once(response: Response): typeof fetch {
  return (async () => response) as unknown as typeof fetch;
}

function provenanceBlock(queryKind: string, recordCount: number) {
  return {
    source_id: SOURCE_ID,
    dataset_ids: [DATASET_ID],
    retrieved_at: RETRIEVED_AT,
    dataset_version: ROWS_UPDATED_AT,
    queries: [
      {
        dataset_id: DATASET_ID,
        query_kind: queryKind,
        request_url: `https://data.cityofnewyork.us/resource/${DATASET_ID}.json`,
        retrieved_at: RETRIEVED_AT,
        record_count: recordCount,
        rows_updated_at: ROWS_UPDATED_AT,
      },
    ],
  };
}

function multiLotDoc() {
  return {
    document_kind: "condo_records",
    bbl: BILLING_MULTI_BBL,
    outcome: CONDO_OUTCOME_MULTI_LOT,
    entered_bbl: BILLING_MULTI_BBL,
    entered_lot_class: "billing",
    billing_bbl: BILLING_MULTI_BBL,
    billing_bbl_status: "recorded",
    base_lots: [
      { bbl: BASE_BBL, recorded_zoning: null, recorded_zoning_status: "unknown" },
      { bbl: BASE_BBL_2, recorded_zoning: "R6", recorded_zoning_status: "recorded" },
    ],
    substitution: null,
    condo_key: "103344",
    condo_number: "3344",
    resolution_path: "billing",
    provenance: provenanceBlock("condo_billing_bbl", 2),
    notes: [],
    reason: null,
    error_type: null,
    divergent_zoning_notice: DIVERGENT_NOTICE,
    recorded_zoning_dependency: ZONING_DEPENDENCY,
  };
}

// A UNIT-BBL input resolving to ONE base lot: the ENTERED unit BBL, the billing
// BBL, and the ANALYZED base BBL are three distinct identifiers.
function unitSingleDoc() {
  return {
    document_kind: "condo_records",
    bbl: UNIT_BBL,
    outcome: CONDO_OUTCOME_RESOLVED_SINGLE,
    entered_bbl: UNIT_BBL,
    entered_lot_class: "unit",
    // A UNIT-class input resolves through a path that returns the base lots but
    // NOT the billing lot, so the billing lot is a LABELLED unknown (null) — never
    // the entered unit BBL relabelled as billing (DB-036(b)).
    billing_bbl: null,
    billing_bbl_status: "unknown",
    base_lots: [{ bbl: BASE_BBL, recorded_zoning: null, recorded_zoning_status: "unknown" }],
    substitution: {
      entered_bbl: UNIT_BBL,
      analyzed_bbl: BASE_BBL,
      note: "Analysis runs on the recorded base tax lot the city records for this condo.",
    },
    condo_key: "103343",
    condo_number: "3343",
    resolution_path: "unit",
    provenance: provenanceBlock("unit_bbl", 1),
    notes: [],
    reason: null,
    error_type: null,
    divergent_zoning_notice: null,
  };
}

function asDocument(outcome: CondoRecordsOutcome): CondoRecordsDocumentOutcome {
  expect(outcome.kind).toBe("document");
  return outcome as CondoRecordsDocumentOutcome;
}

// ---------------------------------------------------------------------------
// Cross-boundary token pin (the web half; test_condo_records_api.py pins the
// api half to the IDENTICAL literals — neither side may drift).
// ---------------------------------------------------------------------------
describe("condo-records outcome vocabulary — cross-boundary token pin", () => {
  it("the web outcome literals EQUAL the api resolver OUTCOME_* strings", () => {
    expect(CONDO_OUTCOME_RESOLVED_SINGLE).toBe("resolved_single_base_lot");
    expect(CONDO_OUTCOME_MULTI_LOT).toBe("multi_lot_set");
    expect(CONDO_OUTCOME_UNRESOLVED).toBe("unresolved");
    expect(CONDO_OUTCOME_ERROR).toBe("error");
    expect(CONDO_OUTCOME_NOT_CONDO_BILLING).toBe("not_condo_billing");
  });
});

// ---------------------------------------------------------------------------
// fetchCondoRecords — 200 records documents
// ---------------------------------------------------------------------------
describe("fetchCondoRecords — 200 records documents", () => {
  it("multi-lot: carries every base lot, recorded zoning, dataset version and provenance", async () => {
    const outcome = await fetchCondoRecords(BILLING_MULTI_BBL, {
      fetchImpl: once(makeResponse(multiLotDoc())),
    });
    const { view, correlationId } = asDocument(outcome);
    expect(correlationId).toBe("corr-1");
    expect(view.outcome).toBe(CONDO_OUTCOME_MULTI_LOT);
    expect(view.billingBbl).toBe(BILLING_MULTI_BBL);
    expect(view.baseLots.map((lot) => lot.bbl)).toEqual([BASE_BBL, BASE_BBL_2]);
    // Recorded zoning is carried when present, unknown (null) when the record omits it.
    expect(view.baseLots[0].recordedZoning).toBeNull();
    expect(view.baseLots[1].recordedZoning).toBe("R6");
    // Dataset version (SODA rowsUpdatedAt) and per-record query provenance.
    expect(view.provenance.sourceId).toBe(SOURCE_ID);
    expect(view.provenance.datasetIds).toEqual([DATASET_ID]);
    expect(view.provenance.datasetVersion).toBe(ROWS_UPDATED_AT);
    expect(view.provenance.queries).toHaveLength(1);
    expect(view.provenance.queries[0].rowsUpdatedAt).toBe(ROWS_UPDATED_AT);
    expect(view.provenance.queries[0].recordCount).toBe(2);
    // DB-036(g) value pin (client level 1 — fetchCondoRecords): the retrievedAt
    // round-trip preserves the EXACT ISO timestamp, colons and all. This is a
    // mutation-style pin: reverting boundedTimestamp to boundedToken would strip
    // the ":" characters ("2026-09-01T140556Z") and fail this assertion.
    expect(view.provenance.retrievedAt).toBe(RETRIEVED_AT);
    expect(view.provenance.retrievedAt).toContain(":");
    expect(view.provenance.queries[0].retrievedAt).toBe(RETRIEVED_AT);
    // Multi-lot carries the no-collapse notice and NO substitution.
    expect(view.divergentZoningNotice).toBe(DIVERGENT_NOTICE);
    expect(view.substitution).toBeNull();
  });

  it("unit single: the ENTERED unit BBL, the billing BBL and the ANALYZED base BBL are three distinct identifiers", async () => {
    const outcome = await fetchCondoRecords(UNIT_BBL, {
      fetchImpl: once(makeResponse(unitSingleDoc())),
    });
    const { view } = asDocument(outcome);
    expect(view.outcome).toBe(CONDO_OUTCOME_RESOLVED_SINGLE);
    // DB-036(b): the ENTERED unit BBL is carried under its own identity; the
    // billing lot is a LABELLED unknown for a unit input (null), never the entered
    // unit BBL relabelled as billing.
    expect(view.enteredBbl).toBe(UNIT_BBL);
    expect(view.enteredLotClass).toBe("unit");
    expect(view.billingBbl).toBeNull();
    expect(view.billingBblStatus).toBe("unknown");
    // The substrate record names entered vs analyzed explicitly.
    expect(view.substitution?.enteredBbl).toBe(UNIT_BBL);
    expect(view.substitution?.analyzedBbl).toBe(BASE_BBL);
    // The analyzed base lot differs from the entered unit BBL — never conflated.
    expect(view.substitution?.analyzedBbl).not.toBe(view.substitution?.enteredBbl);
    expect(view.enteredBbl).not.toBe(view.substitution?.analyzedBbl);
    expect(view.baseLots).toEqual([
      { bbl: BASE_BBL, recordedZoning: null, recordedZoningStatus: "unknown" },
    ]);
    expect(view.provenance.datasetVersion).toBe(ROWS_UPDATED_AT);
  });

  it("unresolved: honest absence, no base lots, a bounded reason, no substitution", async () => {
    const doc = { ...multiLotDoc(), outcome: CONDO_OUTCOME_UNRESOLVED, base_lots: [], billing_bbl: BILLING_BBL, divergent_zoning_notice: null, reason: "matched no base-lot record; honest unresolved result." };
    const { view } = asDocument(
      await fetchCondoRecords(BILLING_BBL, { fetchImpl: once(makeResponse(doc)) }),
    );
    expect(view.outcome).toBe(CONDO_OUTCOME_UNRESOLVED);
    expect(view.baseLots).toEqual([]);
    expect(view.substitution).toBeNull();
    expect(view.reason).toContain("matched no base-lot record");
  });

  it("resolver error: a typed 200 error records document (never an HTTP error)", async () => {
    const doc = { ...multiLotDoc(), outcome: CONDO_OUTCOME_ERROR, base_lots: [], billing_bbl: BILLING_BBL, error_type: "source_unavailable", divergent_zoning_notice: null };
    const { view } = asDocument(
      await fetchCondoRecords(BILLING_BBL, { fetchImpl: once(makeResponse(doc)) }),
    );
    expect(view.outcome).toBe(CONDO_OUTCOME_ERROR);
    expect(view.errorType).toBe("source_unavailable");
    expect(view.baseLots).toEqual([]);
  });

  it("not-a-condo: empty records, null billing lot, byte-safe", async () => {
    const doc = { ...multiLotDoc(), outcome: CONDO_OUTCOME_NOT_CONDO_BILLING, billing_bbl: null, base_lots: [], substitution: null, divergent_zoning_notice: null };
    const { view } = asDocument(
      await fetchCondoRecords("1000010001", { fetchImpl: once(makeResponse(doc)) }),
    );
    expect(view.outcome).toBe(CONDO_OUTCOME_NOT_CONDO_BILLING);
    expect(view.billingBbl).toBeNull();
    expect(view.baseLots).toEqual([]);
  });

  it("a base-lot entry with no recorded BBL is dropped — never a blank record", async () => {
    const doc = multiLotDoc();
    (doc.base_lots as unknown[]).push({ recorded_zoning: "R7" });
    const { view } = asDocument(
      await fetchCondoRecords(BILLING_MULTI_BBL, { fetchImpl: once(makeResponse(doc)) }),
    );
    expect(view.baseLots.map((lot) => lot.bbl)).toEqual([BASE_BBL, BASE_BBL_2]);
  });
});

// ---------------------------------------------------------------------------
// fetchCondoRecords — transport matrix and typed failures
// ---------------------------------------------------------------------------
describe("fetchCondoRecords — transport matrix", () => {
  it("generic 404 {detail: Not Found} is the benign route_absent sentinel, never an error", async () => {
    const outcome = await fetchCondoRecords(BILLING_BBL, {
      fetchImpl: once(makeResponse({ detail: "Not Found" }, 404, null)),
    });
    expect(outcome.kind).toBe("route_absent");
  });

  it("422 validation_error is a typed error carrying the correlation id", async () => {
    const outcome = await fetchCondoRecords("not-a-bbl", {
      fetchImpl: once(makeResponse({ state: "validation_error", message: "bad bbl" }, 422)),
    });
    expect(outcome).toMatchObject({ kind: "error", state: "validation_error", httpStatus: 422 });
  });

  it("500 internal_error is a typed error", async () => {
    const outcome = await fetchCondoRecords(BILLING_BBL, {
      fetchImpl: once(makeResponse({ state: "internal_error", message: "boom" }, 500)),
    });
    expect(outcome).toMatchObject({ kind: "error", state: "internal_error", httpStatus: 500 });
  });

  it("a 200 with the wrong document_kind is an unexpected_response, never rendered as records", async () => {
    const outcome = await fetchCondoRecords(BILLING_BBL, {
      fetchImpl: once(makeResponse({ document_kind: "other", outcome: CONDO_OUTCOME_MULTI_LOT })),
    });
    expect(outcome.kind).toBe("unexpected_response");
  });

  it("a 200 with an unknown outcome token is an unexpected_response (fail closed on drift)", async () => {
    const outcome = await fetchCondoRecords(BILLING_BBL, {
      fetchImpl: once(makeResponse({ document_kind: "condo_records", outcome: "future_outcome_v2" })),
    });
    expect(outcome.kind).toBe("unexpected_response");
  });

  it("an undocumented (status, state) pair is an unexpected_response", async () => {
    const outcome = await fetchCondoRecords(BILLING_BBL, {
      fetchImpl: once(makeResponse({ state: "teapot" }, 418)),
    });
    expect(outcome).toMatchObject({ kind: "unexpected_response", httpStatus: 418 });
  });

  it("a browser-level fetch failure is a recoverable network_error", async () => {
    const fetchImpl: typeof fetch = async () => {
      throw new TypeError("Failed to fetch");
    };
    const outcome = await fetchCondoRecords(BILLING_BBL, { fetchImpl });
    expect(outcome.kind).toBe("network_error");
  });

  it("a stalled request past the budget is a client_timeout", async () => {
    const fetchImpl: typeof fetch = (_url, init) =>
      new Promise((_resolve, reject) => {
        (init?.signal as AbortSignal | undefined)?.addEventListener("abort", () =>
          reject(new DOMException("Aborted", "AbortError")),
        );
      });
    const outcome = await fetchCondoRecords(BILLING_BBL, { fetchImpl, timeoutMs: 5 });
    expect(outcome.kind).toBe("client_timeout");
  });

  it("an already-aborted external signal resolves to aborted without fetching", async () => {
    const controller = new AbortController();
    controller.abort();
    let called = false;
    const fetchImpl: typeof fetch = async () => {
      called = true;
      return makeResponse(multiLotDoc());
    };
    const outcome = await fetchCondoRecords(BILLING_BBL, { fetchImpl, signal: controller.signal });
    expect(outcome.kind).toBe("aborted");
    expect(called).toBe(false);
  });

  it("a stubbed fetch that resolves to a non-Response is an unexpected_response, never a crash", async () => {
    const fetchImpl = (async () => ({})) as unknown as typeof fetch;
    const outcome = await fetchCondoRecords(BILLING_BBL, { fetchImpl });
    expect(outcome).toMatchObject({ kind: "unexpected_response", httpStatus: 0 });
  });
});

// ---------------------------------------------------------------------------
// deriveCondoChannelState — the pure reducer the architect surface consumes
// ---------------------------------------------------------------------------
describe("deriveCondoChannelState — one surface state per outcome", () => {
  async function stateFor(fetchImpl: typeof fetch, bbl = BILLING_BBL) {
    return deriveCondoChannelState(await fetchCondoRecords(bbl, { fetchImpl }));
  }

  it("null (no fetch yet / in flight) is loading", () => {
    expect(deriveCondoChannelState(null).kind).toBe("loading");
  });

  it("multi-lot document -> multi_lot", async () => {
    expect((await stateFor(once(makeResponse(multiLotDoc())), BILLING_MULTI_BBL)).kind).toBe("multi_lot");
  });

  it("single document -> single", async () => {
    expect((await stateFor(once(makeResponse(unitSingleDoc())), UNIT_BBL)).kind).toBe("single");
  });

  it("unresolved document -> unresolved", async () => {
    const doc = { ...multiLotDoc(), outcome: CONDO_OUTCOME_UNRESOLVED, base_lots: [] };
    expect((await stateFor(once(makeResponse(doc)))).kind).toBe("unresolved");
  });

  it("typed resolver-error document -> resolver_error", async () => {
    const doc = { ...multiLotDoc(), outcome: CONDO_OUTCOME_ERROR, base_lots: [] };
    expect((await stateFor(once(makeResponse(doc)))).kind).toBe("resolver_error");
  });

  it("not-a-condo document -> non_condo", async () => {
    const doc = { ...multiLotDoc(), outcome: CONDO_OUTCOME_NOT_CONDO_BILLING, billing_bbl: null, base_lots: [] };
    expect((await stateFor(once(makeResponse(doc)))).kind).toBe("non_condo");
  });

  it("route_absent (flag off) -> non_condo, never an error", async () => {
    expect((await stateFor(once(makeResponse({ detail: "Not Found" }, 404, null)))).kind).toBe("non_condo");
  });

  it("a transport failure -> unavailable (does NOT withhold on its own)", async () => {
    const network = await stateFor(async () => {
      throw new TypeError("boom");
    });
    expect(network.kind).toBe("unavailable");
    const httpError = await stateFor(once(makeResponse({ state: "internal_error" }, 500)));
    expect(httpError.kind).toBe("unavailable");
    const unexpected = await stateFor(once(makeResponse({ state: "teapot" }, 418)));
    expect(unexpected.kind).toBe("unavailable");
  });
});

describe("channelWithholdsAllowances — monotonic condo fail-safe", () => {
  it("withholds ONLY for a positively-confirmed condo fail-safe outcome", () => {
    expect(channelWithholdsAllowances({ kind: "multi_lot", view: {} as never })).toBe(true);
    expect(channelWithholdsAllowances({ kind: "unresolved", view: {} as never })).toBe(true);
    expect(channelWithholdsAllowances({ kind: "resolver_error", view: {} as never })).toBe(true);
  });

  it("does NOT withhold for single (allow path), non-condo, loading, idle, or unavailable", () => {
    expect(channelWithholdsAllowances({ kind: "single", view: {} as never })).toBe(false);
    expect(channelWithholdsAllowances({ kind: "non_condo" })).toBe(false);
    expect(channelWithholdsAllowances({ kind: "loading" })).toBe(false);
    expect(channelWithholdsAllowances({ kind: "idle" })).toBe(false);
    expect(channelWithholdsAllowances({ kind: "unavailable", reason: "network_error" })).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// DB-036 rider parsing (M5-T056): entered vs billing identity, per-lot zoning
// status, the recorded-zoning dependency, and the retrievedAt value pin.
// ---------------------------------------------------------------------------
describe("condo-records — DB-036 rider parsing (M5-T056)", () => {
  it("(b) parses the ENTERED BBL through lib/bbl.ts and keeps it distinct from the billing lot", async () => {
    const { view } = asDocument(
      await fetchCondoRecords(BILLING_MULTI_BBL, { fetchImpl: once(makeResponse(multiLotDoc())) }),
    );
    // A billing-class input: entered == billing (both labelled recorded).
    expect(view.enteredBbl).toBe(BILLING_MULTI_BBL);
    expect(view.enteredLotClass).toBe("billing");
    expect(view.billingBbl).toBe(BILLING_MULTI_BBL);
    expect(view.billingBblStatus).toBe("recorded");
  });

  it("(b) a malformed entered_bbl is an explicit null, never an invented value", async () => {
    const doc = { ...multiLotDoc(), entered_bbl: "not-a-bbl" };
    const { view } = asDocument(
      await fetchCondoRecords(BILLING_MULTI_BBL, { fetchImpl: once(makeResponse(doc)) }),
    );
    expect(view.enteredBbl).toBeNull();
  });

  it("(e) parses recorded_zoning_status per base lot and the recorded_zoning_dependency", async () => {
    const { view } = asDocument(
      await fetchCondoRecords(BILLING_MULTI_BBL, { fetchImpl: once(makeResponse(multiLotDoc())) }),
    );
    expect(view.baseLots[0].recordedZoningStatus).toBe("unknown");
    expect(view.baseLots[1].recordedZoningStatus).toBe("recorded");
    expect(view.recordedZoningDependency).toBe(ZONING_DEPENDENCY);
  });

  it("(e) recorded_zoning_status falls back to a value derived from recordedZoning when the source omits it", async () => {
    const doc = {
      ...multiLotDoc(),
      base_lots: [
        { bbl: BASE_BBL, recorded_zoning: null }, // no status field
        { bbl: BASE_BBL_2, recorded_zoning: "R6" }, // no status field
      ],
    };
    const { view } = asDocument(
      await fetchCondoRecords(BILLING_MULTI_BBL, { fetchImpl: once(makeResponse(doc)) }),
    );
    expect(view.baseLots[0].recordedZoningStatus).toBe("unknown");
    expect(view.baseLots[1].recordedZoningStatus).toBe("recorded");
  });

  it("(g) value-pins the retrievedAt round-trip char-for-char (kills a boundedTimestamp->boundedToken revert)", async () => {
    const { view } = asDocument(
      await fetchCondoRecords(UNIT_BBL, { fetchImpl: once(makeResponse(unitSingleDoc())) }),
    );
    // The colons are the characters boundedToken would strip; pin them explicitly.
    expect(view.provenance.retrievedAt).toBe(RETRIEVED_AT);
    expect(view.provenance.retrievedAt).toBe("2026-09-01T14:05:56Z");
    expect(view.provenance.datasetVersion).toBe(ROWS_UPDATED_AT);
    expect(view.provenance.datasetVersion).toBe("2026-08-30T00:00:00Z");
    expect(view.provenance.queries[0].retrievedAt).toBe(RETRIEVED_AT);
    expect(view.provenance.queries[0].rowsUpdatedAt).toBe(ROWS_UPDATED_AT);
  });
});

// ---------------------------------------------------------------------------
// Site-definition block parsing (M5-T059, D-078). READ-ONLY surfacing of a
// recorded human confirmation on the multi-lot document. The parser hardening is
// pinned here: an empty/malformed/non-active confirmation can never read as a
// recorded active confirmation, and a self-attested identity always retains the
// calculation-refusal flag even if the payload supplies false. Realistic
// fractional-second timestamps are used.
// ---------------------------------------------------------------------------
const SD_CONFIRMED_AT = "2026-09-20T08:23:30.089123+00:00";

function confirmationPayload(
  overrides: Record<string, unknown> = {},
): Record<string, unknown> {
  return {
    record_id: "rec-abc123",
    condo_key: "103344",
    billing_bbl: BILLING_MULTI_BBL,
    entered_bbl: BILLING_MULTI_BBL,
    parcels: [BASE_BBL, BASE_BBL_2],
    confirmer: { name: "Dana Reviewer", role: "qualified_professional" },
    attestation_status: SITE_DEFINITION_ATTESTATION_SELF_ATTESTED,
    refused_for_calculation: true,
    confirmed_at: SD_CONFIRMED_AT,
    supersedes_id: null,
    reason: null,
    note: null,
    provenance: {},
    status: SITE_DEFINITION_CONFIRMATION_STATUS_ACTIVE,
    superseded_by_id: null,
    transitions: [],
    ...overrides,
  };
}

function siteDefBlock(
  overrides: Record<string, unknown> = {},
): Record<string, unknown> {
  return {
    condo_key: "103344",
    status: SITE_DEFINITION_STATUS_CONFIRMED,
    active_confirmation: confirmationPayload(),
    confirmations: [confirmationPayload()],
    parcel_discrepancy: null,
    note: "recorded human confirmation",
    ...overrides,
  };
}

async function siteDefinitionFor(block: unknown) {
  const { view } = asDocument(
    await fetchCondoRecords(BILLING_MULTI_BBL, {
      fetchImpl: once(makeResponse({ ...multiLotDoc(), site_definition: block })),
    }),
  );
  return view.siteDefinition;
}

describe("condo-records — site-definition block parsing (M5-T059, D-078)", () => {
  it("pins the block status + attestation literals to the api vocabulary", () => {
    expect(SITE_DEFINITION_STATUS_CONFIRMED).toBe("confirmed");
    expect(SITE_DEFINITION_STATUS_UNCONFIRMED).toBe("unconfirmed");
    expect(SITE_DEFINITION_ATTESTATION_SELF_ATTESTED).toBe("unauthenticated_self_attested");
    expect(SITE_DEFINITION_CONFIRMATION_STATUS_ACTIVE).toBe("active");
  });

  it("AS-1: a confirmed active block parses the recorded confirmation for display", async () => {
    const sd = await siteDefinitionFor(siteDefBlock());
    expect(sd).not.toBeNull();
    expect(sd?.status).toBe("confirmed");
    expect(sd?.activeConfirmation).not.toBeNull();
    expect(sd?.activeConfirmation?.confirmerName).toBe("Dana Reviewer");
    expect(sd?.activeConfirmation?.confirmerRole).toBe("qualified_professional");
    expect(sd?.activeConfirmation?.parcels).toEqual([BASE_BBL, BASE_BBL_2]);
    expect(sd?.activeConfirmation?.refusedForCalculation).toBe(true);
    // A realistic fractional-second timestamp survives char-for-char (never a
    // fixture trimmed to whole seconds to dodge the ISO display gate).
    expect(sd?.activeConfirmation?.confirmedAt).toBe(SD_CONFIRMED_AT);
    expect(sd?.activeConfirmation?.confirmedAt).toContain(".");
    expect(sd?.confirmationCount).toBe(1);
  });

  it("hardening: an EMPTY active_confirmation with status confirmed reads UNCONFIRMED", async () => {
    const sd = await siteDefinitionFor(siteDefBlock({ active_confirmation: {} }));
    expect(sd?.status).toBe("unconfirmed");
    expect(sd?.activeConfirmation).toBeNull();
  });

  it("hardening: a NON-ACTIVE (revoked) active_confirmation cannot render as active", async () => {
    const sd = await siteDefinitionFor(
      siteDefBlock({ active_confirmation: confirmationPayload({ status: "revoked" }) }),
    );
    expect(sd?.status).toBe("unconfirmed");
    expect(sd?.activeConfirmation).toBeNull();
  });

  it("hardening: an active_confirmation missing a record_id cannot render as active", async () => {
    const sd = await siteDefinitionFor(
      siteDefBlock({ active_confirmation: confirmationPayload({ record_id: null }) }),
    );
    expect(sd?.status).toBe("unconfirmed");
    expect(sd?.activeConfirmation).toBeNull();
  });

  it("hardening: a malformed (non-object) active_confirmation reads unconfirmed", async () => {
    const sd = await siteDefinitionFor(
      siteDefBlock({ active_confirmation: "definitely-confirmed" }),
    );
    expect(sd?.status).toBe("unconfirmed");
    expect(sd?.activeConfirmation).toBeNull();
  });

  it("defect 2: a self-attested confirmation stays refused-for-calculation even if the payload supplies false", async () => {
    const sd = await siteDefinitionFor(
      siteDefBlock({
        active_confirmation: confirmationPayload({ refused_for_calculation: false }),
      }),
    );
    expect(sd?.activeConfirmation?.refusedForCalculation).toBe(true);
  });

  it("a missing refused_for_calculation flag defaults to refused (fail-safe)", async () => {
    const conf = confirmationPayload();
    delete conf.refused_for_calculation;
    const sd = await siteDefinitionFor(
      siteDefBlock({ active_confirmation: conf, confirmations: [conf] }),
    );
    expect(sd?.activeConfirmation?.refusedForCalculation).toBe(true);
  });

  it("the refusal override is SCOPED to self-attestation: another attestation with false is not forced", async () => {
    const conf = confirmationPayload({
      attestation_status: "future_authenticated_scheme",
      refused_for_calculation: false,
    });
    const sd = await siteDefinitionFor(
      siteDefBlock({ active_confirmation: conf, confirmations: [conf] }),
    );
    expect(sd?.activeConfirmation?.refusedForCalculation).toBe(false);
  });

  it("unconfirmed WITH a revoked history: status unconfirmed, but the chain count is surfaced", async () => {
    const revoked = confirmationPayload({ status: "revoked", record_id: "rec-old" });
    const sd = await siteDefinitionFor(
      siteDefBlock({
        status: SITE_DEFINITION_STATUS_UNCONFIRMED,
        active_confirmation: null,
        confirmations: [revoked],
      }),
    );
    expect(sd?.status).toBe("unconfirmed");
    expect(sd?.activeConfirmation).toBeNull();
    expect(sd?.confirmationCount).toBe(1);
  });

  it("parses a surfaced parcel discrepancy (never a status change)", async () => {
    const sd = await siteDefinitionFor(
      siteDefBlock({
        parcel_discrepancy: {
          recorded_parcels: [BASE_BBL, BASE_BBL_2],
          current_resolver_parcels: [BASE_BBL, "1003030099"],
        },
      }),
    );
    expect(sd?.status).toBe("confirmed");
    expect(sd?.parcelDiscrepancy).toEqual({
      recordedParcels: [BASE_BBL, BASE_BBL_2],
      currentResolverParcels: [BASE_BBL, "1003030099"],
    });
  });

  it("a non-multi-lot document carries no site_definition block (null)", async () => {
    const { view } = asDocument(
      await fetchCondoRecords(UNIT_BBL, { fetchImpl: once(makeResponse(unitSingleDoc())) }),
    );
    expect(view.siteDefinition).toBeNull();
  });
});

describe("condo-records — substitutionRecord strict entered-BBL parser (DB-038(f)-2, G3-1)", () => {
  it("parses a valid entered_bbl through the shared BBL validator (canonical)", async () => {
    const { view } = asDocument(
      await fetchCondoRecords(UNIT_BBL, { fetchImpl: once(makeResponse(unitSingleDoc())) }),
    );
    expect(view.substitution?.enteredBbl).toBe(UNIT_BBL);
  });

  it("a non-canonical substitution entered_bbl is an explicit null, not a sanitized token", async () => {
    // "abcd" would survive the looser boundedBbl cleaner as a token; the strict
    // validateBblInput-backed parser rejects it -> null, proving the G3-1 swap.
    const doc = unitSingleDoc();
    doc.substitution = { ...doc.substitution, entered_bbl: "abcd" };
    const { view } = asDocument(
      await fetchCondoRecords(UNIT_BBL, { fetchImpl: once(makeResponse(doc)) }),
    );
    expect(view.substitution?.enteredBbl).toBeNull();
    // The analyzed BBL (parsed via boundedBbl) is unaffected.
    expect(view.substitution?.analyzedBbl).toBe(BASE_BBL);
  });
});
