import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { fireEvent } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { CompareScreen } from "@/components/compare/CompareScreen";
import { ConfirmScreen } from "@/components/confirm/ConfirmScreen";
import { fetchScenario } from "@/lib/scenario-api";
import { formatValue } from "@/lib/format";
import { baseProfile } from "@/test-support/fixtures";
import {
  conflictScenarioBody,
  jsonResponse,
  notFoundResponse,
  preliminaryScenarioBody,
  professionalReviewScenarioBody,
  stateResponse,
  stubFetch,
} from "./scenario-fixtures";

// AS-7: every test drives the screen with an INJECTED fetch (or a stubbed
// global for the Confirm wiring) over the COMMITTED M5-T003 fixtures. No
// network, no Supabase, no Geoclient is touched anywhere in this file.
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

const PRELIMINARY_BBL = "1000010100";

function renderCompare(response: Response) {
  return render(
    <CompareScreen bbl={PRELIMINARY_BBL} fetchImpl={stubFetch(response)} />,
  );
}

describe("Compare screen — AS-1 preliminary cap render (verbatim, never recomputed)", () => {
  it("renders the draft cap VERBATIM from the body with objective + breakdown + draft label", async () => {
    const body = preliminaryScenarioBody();
    renderCompare(jsonResponse(body, 200));

    const capNode = await screen.findByTestId("scenario-cap-value");
    // The rendered cap === the endpoint body value, formatted for display only
    // (the client transports it; it never recomputes far * lot_area).
    const bodyCap = body.draft_zoning_floor_area_cap_sq_ft as number;
    expect(bodyCap).toBe(15000);
    expect(capNode.textContent).toBe(formatValue(bodyCap));

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

    // Score breakdown surfaces the constraints + the platform integrity check.
    expect(screen.getByTestId("scenario-constraints")).toBeInTheDocument();
    expect(screen.getByTestId("scenario-integrity")).toBeInTheDocument();
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
  });

  it("also renders the data-conflict no_scenario fixture as an informative result", async () => {
    renderCompare(jsonResponse(conflictScenarioBody(), 200));
    await screen.findByTestId("scenario-no-scenario");
    expect(screen.getByTestId("scenario-reasons")).toBeInTheDocument();
    expect(screen.queryByTestId("scenario-cap-value")).toBeNull();
  });
});

describe("Compare screen — AS-3 coverage labels + missing-family gaps", () => {
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

    render(<CompareScreen bbl={PRELIMINARY_BBL} fetchImpl={mutableFetch} />);
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
      `/property/confirm?bbl=${PRELIMINARY_BBL}`,
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

    const outcome = await fetchScenario(PRELIMINARY_BBL, {
      fetchImpl: hangingFetch,
      timeoutMs: 5,
    });
    expect(outcome.kind).toBe("client_timeout");
  });

  it("resolves to aborted when the caller's signal is already aborted", async () => {
    const controller = new AbortController();
    controller.abort();
    const outcome = await fetchScenario(PRELIMINARY_BBL, {
      fetchImpl: stubFetch(jsonResponse(preliminaryScenarioBody(), 200)),
      signal: controller.signal,
    });
    expect(outcome.kind).toBe("aborted");
  });

  it("classifies a documented preliminary 200 body as a validated scenario", async () => {
    const outcome = await fetchScenario(PRELIMINARY_BBL, {
      fetchImpl: stubFetch(jsonResponse(preliminaryScenarioBody(), 200)),
    });
    expect(outcome.kind).toBe("scenario");
  });
});
