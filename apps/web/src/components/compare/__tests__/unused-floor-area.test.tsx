import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { CompareScreen } from "@/components/compare/CompareScreen";
import { validateScenarioDocument } from "@/lib/scenario-contract";
import {
  FIXTURE_BBL,
  computedUnusedFloorAreaBody,
  jsonResponse,
  notComputableUnusedFloorAreaBody,
  overBuiltUnusedFloorAreaBody,
  preliminaryScenarioBody,
  professionalReviewScenarioBody,
  stubFetch,
} from "./scenario-fixtures";

/**
 * C1 unused-draft-zoning-floor-area coverage (task M5-T018, directive
 * D-041-R001). Two halves:
 *
 *   S1 — the contract-mirror validator now knows the REQUIRED section and its
 *        closed inner shape (mirror-faithful; new negatives that fail if a hole
 *        reopens, plus proof the pre-existing top-level rejection still fires).
 *   S2/S3/S4 — the three honest render states on the Compare screen, driven by
 *        an injected fetch over the shared fixtures + locally-derived computed /
 *        over_built variants. AS-7 discipline: no network, no Supabase.
 */

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

function renderCompare(body: Record<string, unknown>) {
  return render(
    <CompareScreen bbl={FIXTURE_BBL} fetchImpl={stubFetch(jsonResponse(body, 200))} />,
  );
}

function problemsFor(body: unknown): string[] {
  const result = validateScenarioDocument(body);
  return result.ok ? [] : result.problems;
}

describe("S1 — validator mirror fidelity for unused_draft_zoning_floor_area", () => {
  it("accepts every valid state (shared not_computable + derived computed/over_built)", () => {
    expect(validateScenarioDocument(preliminaryScenarioBody()).ok).toBe(true);
    expect(validateScenarioDocument(computedUnusedFloorAreaBody()).ok).toBe(true);
    expect(validateScenarioDocument(overBuiltUnusedFloorAreaBody()).ok).toBe(true);
    for (const reason of [
      "missing_existing_building_area",
      "existing_building_area_unusable",
      "no_draft_far_cap",
    ] as const) {
      expect(
        validateScenarioDocument(notComputableUnusedFloorAreaBody(reason)).ok,
      ).toBe(true);
    }
  });

  it("FAILS a document missing the required section (mirror-faithful required key)", () => {
    const body = preliminaryScenarioBody();
    delete body.unused_draft_zoning_floor_area;
    expect(
      problemsFor(body).some((p) => p.startsWith("unused_draft_zoning_floor_area")),
    ).toBe(true);
  });

  it("FAILS an unknown key inside the section (additionalProperties:false)", () => {
    const body = computedUnusedFloorAreaBody();
    (body.unused_draft_zoning_floor_area as Record<string, unknown>).surprise = 1;
    expect(
      problemsFor(body).some((p) =>
        p.startsWith("unused_draft_zoning_floor_area:"),
      ),
    ).toBe(true);
  });

  it("FAILS an unknown key inside the nested inputs object", () => {
    const body = computedUnusedFloorAreaBody();
    const inputs = (body.unused_draft_zoning_floor_area as Record<string, unknown>)
      .inputs as Record<string, unknown>;
    (inputs.existing_building_floor_area as Record<string, unknown>).surprise = 1;
    expect(
      problemsFor(body).some((p) =>
        p.startsWith(
          "unused_draft_zoning_floor_area.inputs.existing_building_floor_area:",
        ),
      ),
    ).toBe(true);
  });

  it("FAILS an out-of-enum state", () => {
    const body = computedUnusedFloorAreaBody();
    (body.unused_draft_zoning_floor_area as Record<string, unknown>).state = "verified";
    expect(
      problemsFor(body).some((p) =>
        p.startsWith("unused_draft_zoning_floor_area.state"),
      ),
    ).toBe(true);
  });

  it("FAILS an out-of-enum not_computable_reason", () => {
    const body = notComputableUnusedFloorAreaBody("no_draft_far_cap");
    (body.unused_draft_zoning_floor_area as Record<string, unknown>).not_computable_reason =
      "not_a_real_reason";
    expect(
      problemsFor(body).some((p) =>
        p.startsWith("unused_draft_zoning_floor_area.not_computable_reason"),
      ),
    ).toBe(true);
  });

  it("FAILS a NaN-shaped remainder value (finite-or-null, strict JSON)", () => {
    const body = computedUnusedFloorAreaBody();
    (body.unused_draft_zoning_floor_area as Record<string, unknown>).unused_draft_zoning_floor_area_sq_ft =
      Number.NaN;
    expect(
      problemsFor(body).some((p) =>
        p.startsWith("unused_draft_zoning_floor_area.unused_draft_zoning_floor_area_sq_ft"),
      ),
    ).toBe(true);
  });

  it("ACCEPTS an honest NEGATIVE remainder — over_built is never rejected as invalid", () => {
    const body = overBuiltUnusedFloorAreaBody();
    const section = body.unused_draft_zoning_floor_area as Record<string, unknown>;
    expect(section.unused_draft_zoning_floor_area_sq_ft).toBeLessThan(0);
    expect(validateScenarioDocument(body).ok).toBe(true);
  });

  it("still rejects an undocumented TOP-LEVEL key (no weakening of the existing guard)", () => {
    const body = computedUnusedFloorAreaBody();
    body.surprise_field = "hello";
    expect(problemsFor(body).some((p) => p.startsWith("scenario:"))).toBe(true);
  });
});

describe("S2 — computed line renders its own labeled line beneath the cap", () => {
  it("shows the document label verbatim, the exact value + unit, and the scope note", async () => {
    const body = computedUnusedFloorAreaBody(); // cap 15,000 − existing 10,000
    const section = body.unused_draft_zoning_floor_area as Record<string, unknown>;
    renderCompare(body);

    await screen.findByTestId("scenario-result");

    // The remainder is DERIVED from the fixture cap, not retyped, then shown
    // with locale grouping (a literal DOM string catches a formatter regression).
    expect(section.unused_draft_zoning_floor_area_sq_ft).toBe(5000);
    expect(screen.getByTestId("scenario-unused-floor-area-value").textContent).toBe(
      "5,000",
    );
    expect(screen.getByTestId("scenario-unused-floor-area")).toHaveTextContent(
      "square feet",
    );

    // The label is the document's own precise-noun string, verbatim.
    expect(screen.getByTestId("scenario-unused-floor-area-label").textContent).toBe(
      section.label,
    );

    // Research 3.1: the material assumption (scope note) sits beneath the number.
    expect(
      screen.getByTestId("scenario-unused-floor-area-scope-note").textContent,
    ).toBe(section.scope_note);

    // DRAFT discipline is present on the C1 line.
    expect(
      screen.getByTestId("scenario-unused-floor-area-draft-label"),
    ).toBeInTheDocument();

    // The existing cap line is unchanged and still shows the verbatim cap.
    expect(screen.getByTestId("scenario-cap-value").textContent).toBe("15,000");
  });
});

describe("S3 — over-built renders the negative HONESTLY and routes to review", () => {
  it("shows the negative remainder, the explicit statement, and an accessible review notice", async () => {
    const body = overBuiltUnusedFloorAreaBody(); // cap 15,000 − existing 20,000
    const section = body.unused_draft_zoning_floor_area as Record<string, unknown>;
    renderCompare(body);

    await screen.findByTestId("scenario-result");

    // The negative is preserved EXACTLY — never clamped to zero, never made
    // positive, never hidden.
    expect(section.unused_draft_zoning_floor_area_sq_ft).toBe(-5000);
    const valueNode = screen.getByTestId("scenario-unused-floor-area-value");
    expect(valueNode.textContent).toBe("-5,000");
    expect(valueNode.textContent).not.toBe("5,000");
    expect(valueNode.textContent).not.toBe("0");

    // The document's own over_built_statement is rendered verbatim.
    expect(
      screen.getByTestId("scenario-unused-floor-area-over-built").textContent,
    ).toBe(section.over_built_statement);

    // The needs-professional-review notice is exposed to assistive tech via a
    // role="status" region and carried as TEXT, not colour alone.
    const review = screen.getByTestId("scenario-unused-floor-area-review");
    expect(review).toHaveAttribute("role", "status");
    expect(review).toHaveTextContent("professional review");
  });
});

describe("S4 — not_computable renders the standard no-supported-estimate treatment", () => {
  const CASES: Array<[string, () => Record<string, unknown>, string]> = [
    // Two shared-fixture states + one locally-derived variant.
    [
      "missing_existing_building_area (shared preliminary fixture)",
      preliminaryScenarioBody,
      "No existing building floor-area record",
    ],
    [
      "no_draft_far_cap (shared no_scenario fixture)",
      professionalReviewScenarioBody,
      "No draft residential zoning floor-area cap",
    ],
    [
      "existing_building_area_unusable (local variant)",
      () => notComputableUnusedFloorAreaBody("existing_building_area_unusable"),
      "cannot be used for this calculation",
    ],
  ];

  for (const [name, build, expectedPhrase] of CASES) {
    it(`renders no number and the typed reason in plain language: ${name}`, async () => {
      renderCompare(build());
      await screen.findByTestId("scenario-result");

      // No number, no invented zero.
      expect(screen.queryByTestId("scenario-unused-floor-area-value")).toBeNull();
      expect(
        screen.getByTestId("scenario-unused-floor-area-no-estimate"),
      ).toHaveTextContent("No supported estimate");

      // The typed reason is surfaced in plain language derived from the document.
      expect(
        screen.getByTestId("scenario-unused-floor-area-reason"),
      ).toHaveTextContent(expectedPhrase);

      // The rest of the scenario still renders.
      expect(screen.getByTestId("scenario-result")).toBeInTheDocument();
    });
  }
});
