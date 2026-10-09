import { describe, expect, it } from "vitest";
import corner from "../../../../../../packages/contracts/fixtures/valid/study/synthetic_corner_lot_two_options.json";
import { jsonResponse } from "@/test-support/fixtures";
import {
  ensureStudyFromSetup,
  fetchStudySetup,
  repickLots,
  validateStudySetupDocument,
  type StudySetup,
} from "@/lib/study/study-setup-api";
import { createStudyStore } from "@/lib/study/study-store";
import type { NewOption } from "@/lib/study/study-operations";
import { LOT_SELECTION_STATEMENT, MEASUREMENT_LABELS } from "@/lib/study/study-vocabulary";

/**
 * Typed client + store adapter for GET /api/v1/properties/{bbl}/study
 * (lane C, request D-1 slice 1). Proves: documented (status, state) pairs route
 * to typed outcomes; every 200 is contract-validated before use; and
 * `ensureStudyFromSetup` composes ONE shared study from the server's setup plus
 * the CALLER's confirmed option (never invented), idempotently.
 */

const PROPERTY_BBL = "5999999999";
const SECOND_BBL = "5999999998";

/**
 * A fresh, contract-valid study-setup document built from the committed corner
 * fixture. Deep-cloned every call so a test that deliberately mutates its copy
 * (the validation_failure case) cannot corrupt the shared imported fixture for
 * the tests that run after it.
 */
function setupDocument(): Record<string, unknown> {
  const study = JSON.parse(JSON.stringify(corner)) as {
    property: unknown;
    lots: unknown;
    lot_selection: unknown;
    site: unknown;
  };
  return {
    document_kind: "study_setup",
    bbl: PROPERTY_BBL,
    property: study.property,
    lots: study.lots,
    lot_selection: study.lot_selection,
    site: study.site,
  };
}

function stub(response: Response) {
  return { fetchImpl: (async () => response) as typeof fetch };
}

/** The architect's confirmed option inputs - supplied by the caller, test values. */
function callerOption(): NewOption {
  return {
    name: "Option test (test-fixture-synthetic)",
    inputs: {
      addon_selection: [],
      goal: { kind: "most_residential_floor_area", text: null },
      program: ["market_rate_residential"],
      floor_to_floor_heights: {
        ground_floor: {
          height_ft: 12,
          basis: "stated_default",
          statement: "Test fixture ground-floor height 12 ft (test-fixture-synthetic)",
        },
        typical_floor: {
          height_ft: 10,
          basis: "stated_default",
          statement: "Test fixture typical floor height 10 ft (test-fixture-synthetic)",
        },
        per_floor_overrides: [],
      },
      assumptions: [],
      existing_building_plan: "no_existing_building",
    },
  };
}

describe("fetchStudySetup — documented pairs route to typed outcomes", () => {
  it("classifies a valid 200 study-setup body", async () => {
    const outcome = await fetchStudySetup(PROPERTY_BBL, stub(jsonResponse(setupDocument(), 200, "corr-200")));
    expect(outcome.kind).toBe("setup");
    if (outcome.kind === "setup") {
      expect(outcome.setup.property.bbl).toBe(PROPERTY_BBL);
      expect(outcome.setup.lots.length).toBeGreaterThan(0);
      expect(outcome.setup.siteFacts.length).toBeGreaterThan(0);
      expect(outcome.correlationId).toBe("corr-200");
    }
  });

  it("classifies a 404 as not_available (flag off / unmounted)", async () => {
    const outcome = await fetchStudySetup(
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
    const outcome = await fetchStudySetup("x", stub(jsonResponse(body, 422)));
    expect(outcome.kind).toBe("validation_error");
    if (outcome.kind === "validation_error") {
      expect(outcome.code).toBe("invalid_block");
    }
  });

  it("classifies 503 inputs_unavailable as a retryable outcome", async () => {
    const body = { state: "inputs_unavailable", message: "not available right now" };
    const outcome = await fetchStudySetup(PROPERTY_BBL, stub(jsonResponse(body, 503)));
    expect(outcome.kind).toBe("inputs_unavailable");
  });

  it("classifies 500 internal_contract_error as a server contract error", async () => {
    const body = { state: "internal_contract_error", message: "refused" };
    const outcome = await fetchStudySetup(PROPERTY_BBL, stub(jsonResponse(body, 500)));
    expect(outcome.kind).toBe("server_contract_error");
  });

  it("classifies 500 internal_error", async () => {
    const body = { state: "internal_error", message: "unexpected internal error" };
    const outcome = await fetchStudySetup(PROPERTY_BBL, stub(jsonResponse(body, 500)));
    expect(outcome.kind).toBe("internal_error");
  });

  it("rejects a 200 whose body fails client contract validation", async () => {
    const doc = setupDocument();
    // Displace a real field: a zero lot_area is never a real area (site_fact
    // rule). Reverting this restores the `setup` outcome, so the client guard is
    // the thing under test.
    const site = doc.site as { facts: Array<Record<string, unknown>> };
    site.facts[0] = { ...site.facts[0], value: 0 };
    const outcome = await fetchStudySetup(PROPERTY_BBL, stub(jsonResponse(doc, 200)));
    expect(outcome.kind).toBe("validation_failure");
    if (outcome.kind === "validation_failure") {
      expect(outcome.problems.length).toBeGreaterThan(0);
    }
  });

  it("classifies an undocumented (status, state) pair as unexpected_response", async () => {
    const outcome = await fetchStudySetup(
      PROPERTY_BBL,
      stub(jsonResponse({ state: "no_match" }, 200)),
    );
    expect(outcome.kind).toBe("unexpected_response");
  });

  it("classifies a browser-level failure as network_error", async () => {
    const outcome = await fetchStudySetup(PROPERTY_BBL, {
      fetchImpl: (async () => {
        throw new TypeError("Failed to fetch");
      }) as typeof fetch,
    });
    expect(outcome.kind).toBe("network_error");
  });

  it("resolves a pre-aborted request to the aborted outcome", async () => {
    const controller = new AbortController();
    controller.abort();
    const outcome = await fetchStudySetup(PROPERTY_BBL, {
      signal: controller.signal,
      fetchImpl: (async () => jsonResponse(setupDocument(), 200)) as typeof fetch,
    });
    expect(outcome.kind).toBe("aborted");
  });
});

describe("validateStudySetupDocument", () => {
  it("accepts a contract-valid setup", () => {
    const result = validateStudySetupDocument(setupDocument());
    expect(result.ok).toBe(true);
  });

  it("rejects a document missing the property", () => {
    const full = setupDocument();
    const result = validateStudySetupDocument({
      document_kind: full.document_kind,
      bbl: full.bbl,
      lots: full.lots,
      lot_selection: full.lot_selection,
      site: full.site,
    });
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.problems.length).toBeGreaterThan(0);
  });

  it("rejects a non-object body", () => {
    expect(validateStudySetupDocument(null).ok).toBe(false);
    expect(validateStudySetupDocument([]).ok).toBe(false);
  });
});

describe("ensureStudyFromSetup", () => {
  function validatedSetup(): StudySetup {
    const result = validateStudySetupDocument(setupDocument());
    if (!result.ok) throw new Error(`setup invalid: ${result.problems.join("; ")}`);
    return result.setup;
  }

  it("creates one shared study from the setup plus the caller's option", () => {
    const store = createStudyStore();
    const setup = validatedSetup();
    const result = ensureStudyFromSetup(store, setup, {
      studyId: "test-fixture-synthetic-study",
      initialOption: callerOption(),
      at: "2026-09-30T12:00:00Z",
    });
    expect(result.ok).toBe(true);
    if (result.ok) {
      const study = result.entry.study;
      expect(study.property.bbl).toBe(PROPERTY_BBL);
      expect(study.lots.length).toBe(setup.lots.length);
      expect(study.site.facts.length).toBe(setup.siteFacts.length);
      // The option is the caller's, carried verbatim - never invented here.
      expect(study.options).toHaveLength(1);
      expect(study.options[0].name).toBe("Option test (test-fixture-synthetic)");
      expect(study.options[0].goal).toEqual({ kind: "most_residential_floor_area", text: null });
    }
  });

  it("is idempotent: a second ensure returns the first study", () => {
    const store = createStudyStore();
    const setup = validatedSetup();
    const first = ensureStudyFromSetup(store, setup, {
      studyId: "s1",
      initialOption: callerOption(),
      at: "2026-09-30T12:00:00Z",
    });
    const second = ensureStudyFromSetup(store, setup, {
      studyId: "s2-ignored",
      initialOption: callerOption(),
      at: "2026-09-30T13:00:00Z",
    });
    expect(first.ok && second.ok).toBe(true);
    if (first.ok && second.ok) {
      expect(second.entry).toBe(first.entry);
      expect(second.entry.study.study_id).toBe("s1");
    }
  });

  it("stores the study under the setup's property BBL", () => {
    const store = createStudyStore();
    const setup = validatedSetup();
    ensureStudyFromSetup(store, setup, {
      studyId: "s1",
      initialOption: callerOption(),
      at: "2026-09-30T12:00:00Z",
    });
    expect(store.get(PROPERTY_BBL)).not.toBeNull();
  });
});

describe("validateStudySetupDocument — document_kind and bbl hardening (review NB)", () => {
  it("rejects a body whose document_kind is not 'study_setup'", () => {
    const doc = setupDocument();
    doc.document_kind = "property_profile";
    const result = validateStudySetupDocument(doc);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.problems.some((problem) => problem.includes("document_kind"))).toBe(true);
  });

  it("rejects a body whose top-level bbl does not equal property.bbl", () => {
    const doc = setupDocument();
    // Displace ONLY the top-level bbl; property.bbl stays PROPERTY_BBL. Reverting
    // this restores acceptance (the next test), so the bbl guard is under test.
    doc.bbl = SECOND_BBL;
    const result = validateStudySetupDocument(doc);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.problems.some((problem) => problem.includes("bbl"))).toBe(true);
  });

  it("accepts a body whose top-level bbl equals property.bbl", () => {
    expect(validateStudySetupDocument(setupDocument()).ok).toBe(true);
  });
});

describe("fetchStudySetup — the re-pick selected query (request D-1 slice 2)", () => {
  it("passes re-picked BBLs as repeated selected query params", async () => {
    let seenUrl = "";
    const fetchImpl = (async (input: Parameters<typeof fetch>[0]) => {
      seenUrl = String(input);
      return jsonResponse(setupDocument(), 200);
    }) as typeof fetch;
    const outcome = await fetchStudySetup(PROPERTY_BBL, {
      fetchImpl,
      selected: [PROPERTY_BBL, SECOND_BBL],
    });
    expect(outcome.kind).toBe("setup");
    expect(seenUrl).toContain(
      `/api/v1/properties/${PROPERTY_BBL}/study?selected=${PROPERTY_BBL}&selected=${SECOND_BBL}`,
    );
  });

  it("sends no query when no BBLs are re-picked (server default 'use all')", async () => {
    let seenUrl = "";
    const fetchImpl = (async (input: Parameters<typeof fetch>[0]) => {
      seenUrl = String(input);
      return jsonResponse(setupDocument(), 200);
    }) as typeof fetch;
    await fetchStudySetup(PROPERTY_BBL, { fetchImpl });
    expect(seenUrl.includes("?")).toBe(false);
    expect(seenUrl.endsWith("/study")).toBe(true);
  });
});

describe("repickLots — fetch + store update (request D-1 slice 2)", () => {
  /** The server's re-pick response: two lots and B-07's combination, NOT the web's. */
  function repickDocument(): Record<string, unknown> {
    const doc = setupDocument();
    doc.lots = [
      {
        bbl: PROPERTY_BBL,
        approximate_lot_area_sq_ft: 5000,
        size_measurement: { rank: "approximate_tax_map", label: MEASUREMENT_LABELS.approximate_tax_map },
        selected: true,
      },
      {
        bbl: SECOND_BBL,
        approximate_lot_area_sq_ft: 4000,
        size_measurement: { rank: "approximate_tax_map", label: MEASUREMENT_LABELS.approximate_tax_map },
        selected: true,
      },
    ];
    doc.lot_selection = {
      mode: "all",
      statement: LOT_SELECTION_STATEMENT,
      combination: { status: "offered", reason: null },
    };
    return doc;
  }

  function storeWithStudy() {
    const store = createStudyStore();
    const result = validateStudySetupDocument(setupDocument());
    if (!result.ok) throw new Error(`setup invalid: ${result.problems.join("; ")}`);
    ensureStudyFromSetup(store, result.setup, {
      studyId: "s1",
      initialOption: callerOption(),
      at: "2026-09-30T12:00:00Z",
    });
    return store;
  }

  it("fetches with the selected BBLs, then replaces the store's lots and lot_selection from the server", async () => {
    const store = storeWithStudy();
    expect(store.get(PROPERTY_BBL)?.study.lots).toHaveLength(1);
    let seenUrl = "";
    const fetchImpl = (async (input: Parameters<typeof fetch>[0]) => {
      seenUrl = String(input);
      return jsonResponse(repickDocument(), 200, "corr-repick");
    }) as typeof fetch;
    const outcome = await repickLots(store, PROPERTY_BBL, [PROPERTY_BBL, SECOND_BBL], "2026-09-30T13:00:00Z", {
      fetchImpl,
    });
    expect(seenUrl).toContain(`?selected=${PROPERTY_BBL}&selected=${SECOND_BBL}`);
    expect(outcome.kind).toBe("updated");
    if (outcome.kind === "updated") {
      expect(outcome.correlationId).toBe("corr-repick");
      expect(outcome.result.ok).toBe(true);
    }
    const entry = store.get(PROPERTY_BBL);
    // The store took the SERVER's lots and combination verbatim.
    expect(entry?.study.lots.map((lot) => lot.bbl)).toEqual([PROPERTY_BBL, SECOND_BBL]);
    expect(entry?.study.lot_selection.combination).toEqual({ status: "offered", reason: null });
    // The pinned statement stays, and the change is a new revision.
    expect(entry?.study.lot_selection.statement).toBe(LOT_SELECTION_STATEMENT);
    expect(entry?.study.revision.number).toBe(2);
  });

  it("returns fetch_failed and leaves the store untouched when the server returns no setup", async () => {
    const store = storeWithStudy();
    const before = store.get(PROPERTY_BBL);
    const outcome = await repickLots(store, PROPERTY_BBL, [PROPERTY_BBL], "2026-09-30T13:00:00Z", {
      fetchImpl: (async () => jsonResponse({ detail: "Not Found" }, 404)) as typeof fetch,
    });
    expect(outcome.kind).toBe("fetch_failed");
    if (outcome.kind === "fetch_failed") expect(outcome.outcome.kind).toBe("not_available");
    // The store is unchanged: the same frozen entry is still there.
    expect(store.get(PROPERTY_BBL)).toBe(before);
  });
});
