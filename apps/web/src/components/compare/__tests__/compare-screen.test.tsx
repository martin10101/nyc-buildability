import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { fireEvent } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { CompareScreen } from "@/components/compare/CompareScreen";
import { ConfirmScreen } from "@/components/confirm/ConfirmScreen";
import { fetchScenario } from "@/lib/scenario-api";
import { baseProfile } from "@/test-support/fixtures";
import {
  FIXTURE_BBL,
  conflictScenarioBody,
  jsonResponse,
  notFoundResponse,
  preliminaryScenarioBody,
  professionalReviewScenarioBody,
  stateResponse,
  stubFetch,
  unmeasuredResponse,
  unsupportedScenarioBody,
} from "./scenario-fixtures";

// AS-7: every test drives the screen with an INJECTED fetch (or a stubbed
// global for the Confirm wiring) over the COMMITTED M5-T003 fixtures. No
// network, no Supabase, no Geoclient is touched anywhere in this file.
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

function renderCompare(response: Response, bbl: string = FIXTURE_BBL) {
  return render(<CompareScreen bbl={bbl} fetchImpl={stubFetch(response)} />);
}

/** The three branches that state NO cap. Anything the screen says on these
 * must not presuppose that a value exists. */
const CAPLESS_BRANCHES: Array<[string, () => Record<string, unknown>]> = [
  ["no_scenario", professionalReviewScenarioBody],
  ["data_conflict", conflictScenarioBody],
  ["unsupported", unsupportedScenarioBody],
];

/** Every framing a response can arrive with that does not declare a body size
 * this client is willing to read. All of them must reject before `.json()`. */
const UNREADABLE_CONTENT_LENGTHS: Array<[string, string | null]> = [
  ["over the accepted body size", String(512 * 1024)],
  ["absent entirely (chunked framing)", null],
  ["non-numeric", "abc"],
  ["blank", ""],
  ["signed", "-1"],
];

describe("Compare screen — AS-1 preliminary cap render (verbatim, never recomputed)", () => {
  it("renders the draft cap VERBATIM from the body with objective + draft label", async () => {
    const body = preliminaryScenarioBody();
    renderCompare(jsonResponse(body, 200));

    const capNode = await screen.findByTestId("scenario-cap-value");
    expect(body.draft_zoning_floor_area_cap_sq_ft).toBe(15000);
    // A LITERAL, not `formatValue(bodyCap)`. The previous assertion called the
    // same formatter the component calls, so a rounding or grouping regression
    // moved both sides together and the test still passed — it could not detect
    // the display-magnitude regression it existed to guard (DCV AS-1, G4-7).
    expect(capNode.textContent).toBe("15,000");

    // Certainty is never by color alone — an explicit draft/needs_review label.
    expect(screen.getByTestId("scenario-draft-label")).toBeInTheDocument();

    // The optimized objective is NAMED from the document, never shown as "best".
    expect(screen.getByTestId("scenario-objective-name")).toHaveTextContent(
      "max_residential_floor_area_sq_ft",
    );

    // The verbatim cap_label accompanies the value.
    expect(screen.getByTestId("scenario-cap-label")).toHaveTextContent(
      "DRAFT maximum residential ZONING-FLOOR-AREA CAP",
    );
  });

  it("renders a FRACTIONAL cap without rounding it away", async () => {
    // 15,000 has no fractional part, so even a literal assertion on the shipped
    // fixture cannot catch a rounding regression. This case can: any rounding
    // introduced between the body and the DOM changes this string.
    const body = preliminaryScenarioBody();
    body.draft_zoning_floor_area_cap_sq_ft = 12345.678;
    renderCompare(jsonResponse(body, 200));

    const capNode = await screen.findByTestId("scenario-cap-value");
    expect(capNode.textContent).toBe("12,345.678");
  });

  it("binds the heading identity to the DOCUMENT, not to the URL parameter", async () => {
    renderCompare(jsonResponse(preliminaryScenarioBody(), 200));
    await screen.findByTestId("scenario-result");
    expect(screen.getByTestId("scenario-heading-bbl")).toHaveTextContent(FIXTURE_BBL);
    expect(screen.queryByTestId("scenario-bbl-mismatch")).toBeNull();
    expect(screen.getByTestId("scenario-evaluated-bbl")).toHaveTextContent(FIXTURE_BBL);
  });
});

describe("Compare screen — identity disagreement is surfaced, never papered over", () => {
  it("reports a MISMATCH when the document was evaluated for another BBL", async () => {
    // Exactly the disagreement the pre-rework suite shipped silently: the
    // screen requested 1000010100 while every fixture states 1000477501.
    renderCompare(jsonResponse(preliminaryScenarioBody(), 200), "1000010100");

    const mismatch = await screen.findByTestId("scenario-bbl-mismatch");
    expect(mismatch).toHaveTextContent(FIXTURE_BBL);
    expect(mismatch).toHaveTextContent("1000010100");
    expect(mismatch).toHaveTextContent("IDENTITY MISMATCH");
    // The document's own identity heads the result — never the URL's.
    expect(screen.getByTestId("scenario-heading-bbl")).toHaveTextContent(FIXTURE_BBL);
  });

  it("states an absent document BBL explicitly rather than substituting the URL's", async () => {
    const body = preliminaryScenarioBody();
    (body.evaluated_input as Record<string, unknown>).bbl = null;
    renderCompare(jsonResponse(body, 200));

    await screen.findByTestId("scenario-bbl-not-stated");
    expect(screen.getByTestId("scenario-heading-bbl")).toHaveTextContent("not stated");
    expect(screen.getByTestId("scenario-evaluated-bbl")).toHaveTextContent("not stated");
  });
});

describe("Compare screen — the whole document renders on the branch that shows a number", () => {
  it("states the document's own data_completeness beside the cap", async () => {
    renderCompare(jsonResponse(preliminaryScenarioBody(), 200));

    const completeness = await screen.findByTestId("scenario-completeness");
    // The preliminary fixture — the one producing 15,000 — is missing_critical.
    expect(completeness).toHaveTextContent("missing_critical");
    expect(completeness).toHaveTextContent("Critical official inputs are missing");
  });

  it("renders `reasons` on the preliminary branch (they used to drop there)", async () => {
    renderCompare(jsonResponse(preliminaryScenarioBody(), 200));

    const reasons = await screen.findByTestId("scenario-reasons");
    expect(reasons).toHaveTextContent("NOT a buildable envelope");
    expect(reasons).toHaveTextContent("verbatim");
  });

  it("renders every constraint note, the provenance, the assumptions statement and the tolerance", async () => {
    renderCompare(jsonResponse(preliminaryScenarioBody(), 200));
    await screen.findByTestId("scenario-constraints");

    // constraints[].note is schema-required and carries the anti-inference
    // warning that the state label does NOT carry.
    expect(screen.getByTestId("scenario-constraint-note-height_limit")).toHaveTextContent(
      "MUST NOT be inferred, defaulted, or estimated",
    );
    // constraints[].provenance reaches the screen leaf by leaf.
    const provenance = screen.getByTestId("scenario-constraint-provenance-lot_area");
    expect(provenance).toHaveTextContent("nyc-dcp-lot-geometry");
    expect(provenance).toHaveTextContent("26v1");

    // An EMPTY assumptions array is stated, not silently omitted — every
    // committed fixture carries zero assumptions, so this IS the shipped path.
    expect(screen.getByTestId("scenario-assumptions-empty")).toHaveTextContent(
      "No assumptions are declared",
    );

    // integrity_check.tolerance: the method string is uninterpretable without it.
    expect(screen.getByTestId("scenario-integrity-tolerance")).toHaveTextContent("0.000001");
  });

  it("renders contract_version, the evaluated input and the cap citations", async () => {
    renderCompare(jsonResponse(preliminaryScenarioBody(), 200));
    await screen.findByTestId("scenario-provenance");

    expect(screen.getByTestId("scenario-contract-version")).toHaveTextContent("1.0.0");
    expect(screen.getByTestId("scenario-input-fingerprint")).toHaveTextContent(
      "sha256:c499fc3c",
    );

    // The material number is never surfaced without its citation (PRD s19).
    const citation = screen.getByTestId("scenario-citation-0");
    expect(citation).toHaveTextContent("23-21");
    expect(citation).toHaveTextContent("maximum residential floor area ratio");
    expect(citation).toHaveTextContent("nyc-dcp-zoning-resolution-portal");
    expect(citation).toHaveTextContent("extracted_draft");
  });
});

describe("Compare screen — the practical-range claim is read from the document", () => {
  it("names the envelope-blocking families the MATRIX records, not a hard-coded list", async () => {
    renderCompare(jsonResponse(preliminaryScenarioBody(), 200));

    const blockers = await screen.findByTestId("scenario-practical-range-blockers");
    // The preliminary fixture marks 5 families both missing and
    // blocks_buildable_envelope.
    expect(blockers).toHaveTextContent("5 rule families");
    expect(blockers).toHaveTextContent("height_limit");
    expect(blockers).toHaveTextContent("special_districts_overlays");
    // parking_loading is missing but does NOT block an envelope — a hard-coded
    // sentence could not make that distinction.
    expect(blockers).not.toHaveTextContent("parking_loading");
  });

  it("changes what it says when the SERVER stops reporting those families as missing", async () => {
    // The regression the hard-coded prose could never fail on: M4-T006 (R5
    // height and setbacks) is in flight, and the day an envelope family ships,
    // "height, setbacks, lot coverage, street wall … are still missing" becomes
    // a false statement on a legal-adjacent screen.
    const body = preliminaryScenarioBody();
    const matrix = body.coverage_matrix as Record<string, unknown>[];
    for (const row of matrix) {
      if (row.blocks_buildable_envelope === true) {
        row.rule_status_today = "draft";
      }
    }
    renderCompare(jsonResponse(body, 200));

    await screen.findByTestId("scenario-practical-range-no-blockers");
    expect(screen.queryByTestId("scenario-practical-range-blockers")).toBeNull();
    // And it still refuses to imply a usable range exists.
    expect(screen.getByTestId("scenario-practical-range")).toHaveTextContent(
      "Nothing on this screen infers one",
    );
  });

  it("keeps the definitional disclaimer on both branches", async () => {
    renderCompare(jsonResponse(preliminaryScenarioBody(), 200));
    const block = await screen.findByTestId("scenario-practical-range");
    expect(block).toHaveTextContent("not a buildable envelope");
    expect(block).toHaveTextContent("zoning-floor-area cap");
  });

  // This block mounts on every branch, and the card immediately above it on
  // these branches says "no maximum can be stated" — so "The value above is a
  // draft zoning-floor-area cap only" asserted the existence of a value
  // precisely where there was none. Prose claiming what the document does not
  // support is this packet's own defect class.
  for (const [kind, build] of CAPLESS_BRANCHES) {
    it(`never claims a value exists on the ${kind} branch, where none can be stated`, async () => {
      renderCompare(jsonResponse(build(), 200));

      await screen.findByTestId("scenario-no-scenario");
      const block = screen.getByTestId("scenario-practical-range");
      expect(block).not.toHaveTextContent("The value above");
      expect(block).not.toHaveTextContent("value above is");
      // The definitional framing survives — this is exactly the branch where a
      // reader most needs to know what a cap is not, so gating the sentence on
      // a non-null cap would have been the worse of the two fixes.
      expect(block).toHaveTextContent("not a buildable envelope");
      expect(block).toHaveTextContent("zoning-floor-area cap");
      // And the preceding card really does say no maximum can be stated.
      expect(screen.getByTestId("scenario-no-scenario")).toHaveTextContent(
        "no maximum can be stated",
      );
      expect(screen.queryByTestId("scenario-cap-value")).toBeNull();
    });
  }

  it("keeps the reconciling clause that ties the 5 blockers to the 8 gaps", async () => {
    // Three counts appear on one screen — 5 envelope blockers named here, the
    // full 11-family matrix, and 8 missing families below (three are missing
    // but non-blocking: parking_loading, use_group_overlay, density_bonuses).
    // This clause is what makes those reconcile for a reader; it is
    // load-bearing, not decoration.
    renderCompare(jsonResponse(preliminaryScenarioBody(), 200));
    const blockers = await screen.findByTestId("scenario-practical-range-blockers");
    expect(blockers).toHaveTextContent("listed with the other gaps below");
  });
});

describe("Compare screen — a blank rule identifier reads as absent, not as nothing", () => {
  it("labels an empty rule_id and rule_version rather than rendering invisible code elements", async () => {
    const body = preliminaryScenarioBody();
    const provenance = body.cap_provenance as Record<string, unknown>;
    provenance.rule_id = "";
    provenance.rule_version = "";
    renderCompare(jsonResponse(body, 200));

    // The cap still renders — a defective rule record is not an outage.
    const cap = await screen.findByTestId("scenario-cap-value");
    expect(cap.textContent).toBe("15,000");
    const objective = screen.getByTestId("scenario-objective");
    expect(objective).toHaveTextContent("id not stated");
    expect(objective).toHaveTextContent("not stated");
  });
});

describe("Compare screen — AS-2 no_scenario / professional review", () => {
  it("shows the reason + review label + preserved share ranges and NO cap, as an informative result", async () => {
    renderCompare(jsonResponse(professionalReviewScenarioBody(), 200));

    await screen.findByTestId("scenario-no-scenario");
    // An informative result, never an error page.
    expect(screen.getByTestId("scenario-result")).toBeInTheDocument();
    expect(screen.getByTestId("scenario-review-required")).toBeInTheDocument();

    // No cap is fabricated for a no_scenario document.
    expect(screen.queryByTestId("scenario-cap-value")).toBeNull();

    // The reasons are surfaced.
    expect(screen.getByTestId("scenario-reasons")).toHaveTextContent(
      "NO SCENARIO (fail-closed)",
    );

    // Preserved base-district share ranges are shown, NEVER collapsed.
    const ranges = screen.getByTestId("scenario-share-ranges");
    for (const value of ["0.4", "0.55", "0.7", "0.3", "0.45", "0.6"]) {
      expect(ranges).toHaveTextContent(value);
    }
    // Both candidate districts are present.
    expect(ranges).toHaveTextContent("R5");
    expect(ranges).toHaveTextContent("R6");
    // The qualifier explaining WHY the share is uncertain renders too.
    expect(ranges).toHaveTextContent("boundary_uncertain");
  });

  it("keeps the constraints and the integrity check on the no_scenario branch", async () => {
    // Before the rework this branch dropped ALL 11 constraints and the whole
    // integrity record: 0 of 96 constraint leaves rendered (DCV-5, G4-4).
    renderCompare(jsonResponse(professionalReviewScenarioBody(), 200));

    await screen.findByTestId("scenario-constraints");
    expect(screen.getByTestId("scenario-constraint-lot_area")).toHaveTextContent("10,000");
    expect(screen.getByTestId("scenario-integrity")).toBeInTheDocument();
    expect(screen.getByTestId("scenario-integrity-tolerance")).toBeInTheDocument();

    // The escalation's own stated reasons reach the screen.
    const districtProvenance = screen.getByTestId(
      "scenario-constraint-provenance-zoning_district",
    );
    expect(districtProvenance).toHaveTextContent("split_lot");
    expect(districtProvenance).toHaveTextContent("lot spans two base districts");
  });

  it("shows the COMPETING RULES on the data-conflict fixture, as its own gloss promises", async () => {
    // The screen printed "both values are shown, nothing was resolved" twice
    // while showing neither, because ruleConflict() had zero consumers
    // repo-wide (G1-6, G3-7, G4-3, DCV-6).
    renderCompare(jsonResponse(conflictScenarioBody(), 200));

    await screen.findByTestId("scenario-no-scenario");
    const conflict = screen.getByTestId("scenario-rule-conflict");
    expect(conflict).toHaveTextContent("max_residential_floor_area_sq_ft");

    const competing = screen.getByTestId("scenario-competing-rules");
    expect(competing).toHaveTextContent("r5-residential-far");
    expect(competing).toHaveTextContent("0.1.0-draft");
    expect(competing).toHaveTextContent("r5-residential-far-alt");
    expect(competing).toHaveTextContent("0.2.0-draft");

    // And the conflicting VALUES the gloss promises are shown.
    expect(screen.getByTestId("scenario-conflicting-values")).toHaveTextContent("R5");
    expect(screen.queryByTestId("scenario-cap-value")).toBeNull();
  });

  it("renders the unsupported-family fixture as an honest, complete result", async () => {
    // unsupported_family.json has been committed and unused since M5-T003, so
    // the `unsupported` branch had never been rendered by anything.
    renderCompare(jsonResponse(unsupportedScenarioBody(), 200));

    const block = await screen.findByTestId("scenario-no-scenario");
    expect(block).toHaveTextContent("Not supported yet");
    expect(block).toHaveTextContent("unsupported");
    expect(screen.queryByTestId("scenario-cap-value")).toBeNull();
    // The whole document still renders on this branch.
    expect(screen.getByTestId("scenario-constraints")).toBeInTheDocument();
    expect(screen.getByTestId("scenario-reasons")).toBeInTheDocument();
    expect(screen.getByTestId("coverage-matrix-all")).toBeInTheDocument();
  });
});

describe("Compare screen — absence is stated, never rendered as an empty element", () => {
  it("labels an empty citation snapshot_id, section and quote", async () => {
    // All three are checkString (empty-permitting, deliberately — they are
    // propagated from the rule record and the schemas set no minLength), so an
    // empty one reached an invisible <code></code> / empty <dd> on the citation
    // backing the only material number on the screen.
    const body = preliminaryScenarioBody();
    const provenance = body.cap_provenance as Record<string, unknown>;
    const citation = (provenance.citations as Record<string, unknown>[])[0];
    citation.snapshot_id = "";
    citation.section = "";
    citation.quote = "";
    renderCompare(jsonResponse(body, 200));

    const block = await screen.findByTestId("scenario-citation-0");
    expect(block).toHaveTextContent("snapshot id not stated");
    expect(block).toHaveTextContent("no quoted text was carried");
    // "Last amended" already stated its absence; the others now match it.
    expect(block).toHaveTextContent("not stated");
  });

  it("treats an EMPTY competing-rule field as absent, not just a null one", async () => {
    // `asStringOrNull` runs every provenance string through boundedText, which
    // yields "" for a value that cleans to nothing — so `?? "…"` caught only
    // half of absence and the other half rendered blank.
    const body = conflictScenarioBody();
    const constraints = body.constraints as Record<string, unknown>[];
    const provenance = constraints[0].provenance as Record<string, unknown>;
    const rules = provenance.competing_rules as Record<string, unknown>[];
    rules[0].rule_id = "   ";
    rules[0].rule_version = "";
    rules[0].effective_from = "";
    renderCompare(jsonResponse(body, 200));

    const competing = await screen.findByTestId("scenario-competing-rules");
    expect(competing).toHaveTextContent("rule id not stated");
    expect(competing).toHaveTextContent("version not stated");
    expect(competing).toHaveTextContent("start not stated");
  });

  it("NEVER substitutes 'present' for an absent rule end date", async () => {
    // The committed conflict fixture carries effective_to: null on both
    // competing rules. Rendering that as "present" asserts the draft rule is in
    // legal effect right now — an authored legal claim no source here supports,
    // and worse in this block than elsewhere: these are COMPETING rules, and
    // saying both run "to present" edges towards asserting both currently
    // govern, which is exactly what this block refuses to do.
    renderCompare(jsonResponse(conflictScenarioBody(), 200));

    const competing = await screen.findByTestId("scenario-competing-rules");
    expect(competing).toHaveTextContent("end not stated");
    expect(competing).not.toHaveTextContent("to present");
  });

  it("labels an empty district label and omits an empty pair classification", async () => {
    const body = professionalReviewScenarioBody();
    const constraints = body.constraints as Record<string, unknown>[];
    const provenance = constraints[2].provenance as Record<string, unknown>;
    const candidates = provenance.base_district_candidates as Record<string, unknown>[];
    candidates[0].district_label = "";
    candidates[0].pair_class = "";
    renderCompare(jsonResponse(body, 200));

    const ranges = await screen.findByTestId("scenario-share-ranges");
    expect(ranges).toHaveTextContent("district not stated");
    // An empty classification is omitted rather than rendered as an empty
    // "(classification: )" with nothing inside it.
    expect(ranges).not.toHaveTextContent("classification: )");
    // The second candidate is untouched, so the block still works normally.
    expect(ranges).toHaveTextContent("R6");
  });
});

describe("Compare screen — AS-3 coverage labels + full matrix + missing-family gaps", () => {
  it("renders every coverage status as a distinct TEXT label and lists the 8 missing families", async () => {
    renderCompare(jsonResponse(preliminaryScenarioBody(), 200));

    await screen.findByTestId("coverage-vocabulary");
    for (const status of [
      "verified",
      "conditional",
      "professional_review_required",
      "data_conflict",
      "unsupported",
      "not_applicable",
    ]) {
      expect(screen.getByTestId(`coverage-label-${status}`)).toHaveTextContent(
        status,
      );
    }

    // The preliminary fixture has exactly 8 MISSING coverage families.
    expect(screen.getByText(/Rule families still missing \(8\)/)).toBeInTheDocument();
    const gaps = screen
      .getByTestId("coverage-gaps")
      .querySelectorAll('[data-testid^="coverage-gap-"]');
    expect(gaps.length).toBe(8);
    // A missing envelope family is flagged as blocking a buildable envelope.
    expect(screen.getByTestId("coverage-gap-height_limit")).toHaveTextContent(
      "blocks a buildable envelope",
    );
  });

  it("renders the FULL 11-row matrix, not only the 8 missing rows", async () => {
    // Only `missing` rows rendered before the rework: the draft R5 row that
    // actually produced the number, and both out_of_scope rows, were filtered
    // out with no disclosure of the total (DCV-7).
    renderCompare(jsonResponse(preliminaryScenarioBody(), 200));

    const matrix = await screen.findByTestId("coverage-matrix-all");
    const rows = matrix.querySelectorAll('[data-testid^="coverage-row-"]');
    expect(rows.length).toBe(11);
    expect(matrix).toHaveTextContent("out_of_scope");
    expect(screen.getByTestId("coverage-row-residential_far_cap")).toHaveTextContent(
      "draft",
    );
    // The two out_of_scope families were filtered out entirely before.
    expect(matrix).toHaveTextContent("higher_density_bulk_tower");
    expect(matrix).toHaveTextContent("gross_to_net_efficiency_yield");
  });
});

describe("Compare screen — AS-4 contract safety (validate before render; bounded errors)", () => {
  it("renders a validation_failure with ONLY the correlation id when a 200 body fails validation", async () => {
    renderCompare(jsonResponse({ not: "a scenario document" }, 200));

    await screen.findByTestId("scenario-validation-failure");
    // Nothing partial is rendered.
    expect(screen.queryByTestId("scenario-result")).toBeNull();
    expect(screen.queryByTestId("scenario-cap-value")).toBeNull();
    // The allowlisted correlation id is carried.
    expect(screen.getByTestId("scenario-correlation-id")).toBeInTheDocument();
  });

  it("refuses a cap whose provenance cannot name the optimized objective", async () => {
    // The exact G4 finding 2 body: a plausible 200 that passed validation and
    // rendered a 15,000 sq ft maximum with an EMPTY objective name and an
    // empty rule id, because `{}` is truthy and took the populated branch.
    const body = preliminaryScenarioBody();
    body.cap_provenance = { note: "tbd" };
    renderCompare(jsonResponse(body, 200));

    await screen.findByTestId("scenario-validation-failure");
    expect(screen.queryByTestId("scenario-cap-value")).toBeNull();
    expect(screen.queryByTestId("scenario-objective-name")).toBeNull();
  });

  it("renders unexpected_response for a (status, state) pair outside the documented matrix", async () => {
    renderCompare(stateResponse(418, "teapot"));

    await screen.findByTestId("scenario-unexpected-response");
    expect(screen.getByTestId("scenario-unexpected-state")).toHaveTextContent(
      "teapot",
    );
    expect(screen.queryByTestId("scenario-result")).toBeNull();
  });
});

describe("Compare screen — AS-5 flag-off / upstream / recoverable states", () => {
  it("maps the generic flag-off 404 to a benign feature_unavailable note (no correlation id, no retry)", async () => {
    renderCompare(notFoundResponse());

    await screen.findByTestId("scenario-feature-unavailable");
    expect(screen.queryByTestId("scenario-correlation-id")).toBeNull();
    expect(
      screen.queryByRole("button", { name: "Retry compare" }),
    ).toBeNull();
    expect(screen.queryByTestId("scenario-result")).toBeNull();
  });

  it.each([
    ["source_unavailable", 503],
    ["rate_limited", 503],
    ["timeout", 504],
    ["schema_drift", 502],
  ])("renders the documented upstream state %s recoverably with its correlation id", async (state, status) => {
    renderCompare(stateResponse(status as number, state as string));

    await screen.findByTestId(`scenario-${state}`);
    expect(screen.getByTestId("scenario-correlation-id")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Retry compare" })).toBeInTheDocument();
    // No raw scenario / invented value leaked.
    expect(screen.queryByTestId("scenario-result")).toBeNull();
    cleanup();
  });

  it("recovers on Retry: an upstream failure then a preliminary success", async () => {
    let calls = 0;
    const mutableFetch = (async () => {
      calls += 1;
      return calls === 1
        ? stateResponse(503, "source_unavailable")
        : jsonResponse(preliminaryScenarioBody(), 200);
    }) as unknown as typeof fetch;

    render(<CompareScreen bbl={FIXTURE_BBL} fetchImpl={mutableFetch} />);
    fireEvent.click(await screen.findByRole("button", { name: "Retry compare" }));
    await screen.findByTestId("scenario-result");
    expect(screen.getByTestId("scenario-cap-value")).toBeInTheDocument();
  });
});

describe("Compare screen — AS-6 navigation (Confirm rewire + analysis-preserving links)", () => {
  it("Confirm 'Next step' now routes to the Compare screen for the confirmed BBL", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => jsonResponse(baseProfile(), 200)));
    render(<ConfirmScreen bbl="1000010010" />);

    const link = await screen.findByTestId("confirm-next-compare");
    expect(link).toHaveAttribute("href", "/property/compare?bbl=1000010010");
    expect(link.tagName).toBe("A");
  });

  it("the Compare next action preserves the analysis via ?bbl= and is keyboard-reachable", async () => {
    renderCompare(jsonResponse(preliminaryScenarioBody(), 200));
    const nextAction = await screen.findByTestId("scenario-next-action");
    const confirmLink = nextAction.querySelector('a[href^="/property/confirm"]');
    expect(confirmLink).toHaveAttribute(
      "href",
      `/property/confirm?bbl=${FIXTURE_BBL}`,
    );
  });
});

describe("Compare screen — AS-8 accessibility (announcement + focus + text labels)", () => {
  it("announces the outcome via a persistent aria-live region and focuses the outcome heading", async () => {
    renderCompare(jsonResponse(preliminaryScenarioBody(), 200));

    const announcer = screen.getByTestId("compare-announcer");
    expect(announcer).toHaveAttribute("aria-live", "polite");

    await screen.findByTestId("scenario-result");
    await waitFor(() => expect(announcer).toHaveTextContent("preliminary"));

    // Focus moved to the outcome heading (never dropped to <body>).
    await waitFor(() => {
      const active = document.activeElement as HTMLElement | null;
      expect(active?.getAttribute("data-outcome-heading")).not.toBeNull();
    });
  });

  it("announces the loading region, matching the Property and Confirm screens", async () => {
    // LoadingStages.tsx:34-41 carries aria-live for Property and Confirm; the
    // Compare loading region had none, so a screen-reader user got silence
    // between submitting and the outcome on the one screen whose request can
    // take twelve seconds.
    const neverResolves = (() => new Promise<Response>(() => {})) as unknown as typeof fetch;
    render(<CompareScreen bbl={FIXTURE_BBL} fetchImpl={neverResolves} />);

    const loading = await screen.findByTestId("compare-loading");
    expect(loading).toHaveAttribute("aria-live", "polite");
    // Exactly one region has content: the outcome announcer stays empty while
    // loading, so the two can never double-announce.
    expect(screen.getByTestId("compare-announcer").textContent).toBe("");
  });

  it("moves focus to the failure title on an error outcome", async () => {
    renderCompare(stateResponse(503, "source_unavailable"));
    await screen.findByTestId("scenario-source_unavailable");
    await waitFor(() => {
      const active = document.activeElement as HTMLElement | null;
      expect(active?.getAttribute("data-outcome-heading")).not.toBeNull();
    });
  });
});

describe("fetchScenario — offline client hardening (AS-4/AS-5 unit coverage)", () => {
  it("resolves to client_timeout when the request budget elapses", async () => {
    const hangingFetch = ((_url: string, init?: RequestInit) =>
      new Promise<Response>((_resolve, reject) => {
        init?.signal?.addEventListener("abort", () =>
          reject(new DOMException("aborted", "AbortError")),
        );
      })) as unknown as typeof fetch;

    const outcome = await fetchScenario(FIXTURE_BBL, {
      fetchImpl: hangingFetch,
      timeoutMs: 5,
    });
    expect(outcome.kind).toBe("client_timeout");
  });

  it("resolves to aborted when the caller's signal is already aborted", async () => {
    const controller = new AbortController();
    controller.abort();
    const outcome = await fetchScenario(FIXTURE_BBL, {
      fetchImpl: stubFetch(jsonResponse(preliminaryScenarioBody(), 200)),
      signal: controller.signal,
    });
    expect(outcome.kind).toBe("aborted");
  });

  it("classifies a documented preliminary 200 body as a validated scenario", async () => {
    const outcome = await fetchScenario(FIXTURE_BBL, {
      fetchImpl: stubFetch(jsonResponse(preliminaryScenarioBody(), 200)),
    });
    expect(outcome.kind).toBe("scenario");
  });

  it("BLOCKING REGRESSION: an HTTP 500 carrying state=no_match is NEVER a no-match result", async () => {
    // The owner-directed adversarial pair recorded at
    // packages/contracts/fixtures/client_regression/http500_state_no_match.json
    // and named blocking at lib/contract-matrix.ts:12-17. scenario-api.ts
    // reimplements the very pair check that defends against it, and nothing
    // drove the pair through fetchScenario (G4-7).
    const outcome = await fetchScenario(FIXTURE_BBL, {
      fetchImpl: stubFetch(
        stateResponse(500, "no_match", { bbl: "5999999999" }),
      ),
    });
    expect(outcome.kind).toBe("unexpected_response");
    expect(outcome.kind === "unexpected_response" && outcome.httpStatus).toBe(500);
  });

  it("accepts a response that declares a readable body size", async () => {
    // The positive control for the guard below: a well-formed Content-Length
    // within budget must NOT be rejected. Every other test in this file relies
    // on it, so it is asserted once directly.
    const outcome = await fetchScenario(FIXTURE_BBL, {
      fetchImpl: stubFetch(jsonResponse(preliminaryScenarioBody(), 200)),
    });
    expect(outcome.kind).toBe("scenario");
  });

  // The guard must reject anything that is not a plain digit string within
  // budget. An earlier version rejected only a header that was present AND over
  // budget, so an actor controlling the response could drop the header
  // (chunked) and walk past it at zero cost — and `Number(null)` is 0, which is
  // finite, so the absent case never even reached the comparison.
  for (const [label, contentLength] of UNREADABLE_CONTENT_LENGTHS) {
    it(`FAILS CLOSED and parses nothing when Content-Length is ${label}`, async () => {
      const outcome = await fetchScenario(FIXTURE_BBL, {
        fetchImpl: stubFetch(unmeasuredResponse(contentLength)),
      });
      expect(outcome.kind).toBe("unexpected_response");
      // Rejected BEFORE parsing: no state is echoed, because the body was
      // never read.
      expect(
        outcome.kind === "unexpected_response" && outcome.receivedState,
      ).toBeNull();
    });
  }

  it("fails closed even when the unmeasured body would otherwise be a valid scenario", async () => {
    // The dangerous case: a document that WOULD pass validation still never
    // reaches the validator, because its framing was not declared.
    const outcome = await fetchScenario(FIXTURE_BBL, {
      fetchImpl: stubFetch(unmeasuredResponse(null, preliminaryScenarioBody(), 200)),
    });
    expect(outcome.kind).toBe("unexpected_response");
  });

  it("bounds a unit label without silently rewriting it", async () => {
    const body = preliminaryScenarioBody();
    const constraints = body.constraints as Record<string, unknown>[];
    // A unit the token allowlist would quietly mangle to "sqft", and one that
    // is genuinely over the 64-character cap.
    constraints[0].unit = "sq ft";
    constraints[1].unit = "z".repeat(200);
    const outcome = await fetchScenario(FIXTURE_BBL, {
      fetchImpl: stubFetch(jsonResponse(body, 200)),
    });
    expect(outcome.kind).toBe("scenario");
    if (outcome.kind !== "scenario") return;
    expect(outcome.document.constraints[0].unit).toBe("sq ft");
    expect(outcome.document.constraints[1].unit).toBe(
      `${"z".repeat(64)}… [truncated]`,
    );
  });

  it("reports a rejected oversized ARRAY rather than silently truncating it", async () => {
    const body = preliminaryScenarioBody();
    body.reasons = Array.from({ length: 65 }, (_, index) => `reason ${index}`);
    const outcome = await fetchScenario(FIXTURE_BBL, {
      fetchImpl: stubFetch(jsonResponse(body, 200)),
    });
    expect(outcome.kind).toBe("validation_failure");
    expect(
      outcome.kind === "validation_failure" &&
        outcome.problems.some((problem) => problem.startsWith("reasons:")),
    ).toBe(true);
  });

  it("truncates an over-long free-text string EXPLICITLY instead of dropping it", async () => {
    const body = preliminaryScenarioBody();
    const constraints = body.constraints as Record<string, unknown>[];
    constraints[0].note = "x".repeat(900);
    const outcome = await fetchScenario(FIXTURE_BBL, {
      fetchImpl: stubFetch(jsonResponse(body, 200)),
    });
    expect(outcome.kind).toBe("scenario");
    if (outcome.kind !== "scenario") return;
    const note = outcome.document.constraints[0].note;
    expect(note.endsWith("… [truncated]")).toBe(true);
    expect(note.length).toBe(600 + "… [truncated]".length);
  });
});
