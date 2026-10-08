import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { jsonResponse } from "@/test-support/fixtures";
import { loadResultsFixture } from "@/test-support/results-fixtures";
import {
  ANSWER_KEYS,
  displayQuantity,
  quantityText,
  type Results,
} from "@/lib/architect/three-answers";
import type { ResultsRequestBody } from "@/lib/results-api";
import { PARKING_LINE, ResultsPanel, STALE_INPUTS_LINE } from "../ResultsPanel";

/**
 * The results panel (task M5-T140). W-2 proves every shown value, conditional line and "not known"
 * equals the returned document (nothing retyped). W-3 walks the states (before the ask, loading,
 * each server error, a changed input). W-4 proves the panel adds no standing label. W-6 proves the
 * panel has an accessible name. S22 proves a newer request wins. Every expected string is read from
 * the loaded document; the panel never fetches on mount (ruling R2).
 */

afterEach(cleanup);

const BBL = "4073340070";
const JOURNEY = "recorded_215_16_northern_journey";
const SNAKE_CASE = /\b[a-z0-9]+(?:_[a-z0-9]+)+\b/;

function successFetch(doc: Results, correlationId = "corr-ok") {
  return (async () => jsonResponse(doc, 200, correlationId)) as typeof fetch;
}

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>(r => {
    resolve = r;
  });
  return { promise, resolve };
}

async function pressShow() {
  fireEvent.click(screen.getByTestId("results-show"));
}

describe("ResultsPanel — ruling R2: no request before the user asks", () => {
  it("S2/S7/S9: shows the form and makes NO call on mount; the inputs start empty", () => {
    const fetchImpl = vi.fn(async () => jsonResponse(loadResultsFixture(JOURNEY), 200));
    render(<ResultsPanel bbl={BBL} fetchImpl={fetchImpl as unknown as typeof fetch} />);
    expect(screen.getByTestId("results-form")).toBeInTheDocument();
    expect(screen.getByTestId("results-show")).toBeInTheDocument();
    // No result, no loading, no call.
    expect(screen.queryByTestId("results-document")).toBeNull();
    expect(screen.queryByTestId("results-loading")).toBeNull();
    expect(fetchImpl).not.toHaveBeenCalled();
    // The height field is empty and carries its helper line; the website holds no starting number.
    const height = screen.getByTestId<HTMLInputElement>("results-floor-to-floor");
    expect(height.value).toBe("");
    expect(height.getAttribute("value")).not.toMatch(/\d/);
    expect(screen.getByTestId("results-floor-to-floor-help").textContent).toContain("Leave empty");
    // The housing program starts on the standard residence; the statement is not made.
    expect(screen.getByTestId<HTMLSelectElement>("results-housing-program").value).toBe("standard_residence");
    expect(screen.getByTestId<HTMLInputElement>("results-density-statement").checked).toBe(false);
  });

  it("makes exactly one call when the button is pressed", async () => {
    const fetchImpl = vi.fn(async () => jsonResponse(loadResultsFixture(JOURNEY), 200));
    render(<ResultsPanel bbl={BBL} fetchImpl={fetchImpl as unknown as typeof fetch} />);
    await pressShow();
    await screen.findByTestId("results-document");
    expect(fetchImpl).toHaveBeenCalledTimes(1);
  });
});

describe("ResultsPanel — W-2: every value equals the returned document (nothing retyped)", () => {
  it("renders the journey document through the three-answers cards", async () => {
    const doc = loadResultsFixture(JOURNEY);
    render(<ResultsPanel bbl={BBL} fetchImpl={successFetch(doc)} />);
    await pressShow();
    await screen.findByTestId("three-answers-panel");

    for (const key of ANSWER_KEYS) {
      const answer = doc.answers[key];
      const cardEl = screen.getByTestId(`answer-${key}`);
      if (answer.status !== "available") {
        // The whole not-available answer reads its reason (no number falls back).
        expect(within(cardEl).getByTestId("answer-not-available").textContent).toContain("Not available");
        continue;
      }
      const states = answer.value_states ?? {};
      for (const value of answer.values) {
        // Every shown value's number+unit appears exactly as the document carries it.
        expect(cardEl.textContent).toContain(quantityText(displayQuantity(value.value, value.unit)));
        const state = states[value.key];
        // Every conditional value shows its assumption line, read from the document.
        if (state && state.way === "conditional") {
          for (const condition of state.conditions) {
            expect(cardEl.textContent).toContain(condition.assumption);
          }
        }
      }
      // Every withheld value reads "Not known" with its reason, never a number.
      for (const [valueKey, state] of Object.entries(states)) {
        if (state.way !== "withheld") continue;
        const shown = answer.values.some(value => value.key === valueKey);
        if (shown) continue;
        expect(cardEl.textContent).toContain("Not known");
        expect(cardEl.textContent).toContain(state.reason);
      }
    }
    // The completeness line is the document's, verbatim.
    expect(screen.getByTestId("three-answers-completeness").textContent).toBe(doc.completeness_line.text);
  });
});

describe("ResultsPanel — W-3 / S13 / S14: states and honest text", () => {
  it("S2: shows a loading state while the request is in flight, button disabled", async () => {
    const gate = deferred<Response>();
    const fetchImpl = (async () => gate.promise) as typeof fetch;
    render(<ResultsPanel bbl={BBL} fetchImpl={fetchImpl} />);
    await pressShow();
    expect(screen.getByTestId("results-loading")).toBeInTheDocument();
    expect(screen.getByTestId("results-show").getAttribute("aria-busy")).toBe("true");
    gate.resolve(jsonResponse(loadResultsFixture(JOURNEY), 200));
    await screen.findByTestId("results-document");
    expect(screen.queryByTestId("results-loading")).toBeNull();
  });

  it("S7/S9: the body carries only what the user chose (empty height and unmade statement are omitted)", async () => {
    const calls: ResultsRequestBody[] = [];
    const fetchImpl = ((_url: string, init: RequestInit) => {
      calls.push(JSON.parse(String(init.body)) as ResultsRequestBody);
      return Promise.resolve(jsonResponse(loadResultsFixture(JOURNEY), 200));
    }) as unknown as typeof fetch;
    render(<ResultsPanel bbl={BBL} fetchImpl={fetchImpl} />);
    // (a) empty height, no statement: the body carries the housing program only.
    await pressShow();
    await screen.findByTestId("results-document");
    expect(calls[0]).toEqual({ housing_program: "standard_residence" });
    expect(calls[0].floor_to_floor_ft).toBeUndefined();
    expect(calls[0].special_density_statement).toBeUndefined();
    // (b) an entered height is sent in feet.
    fireEvent.change(screen.getByTestId("results-floor-to-floor"), { target: { value: "14" } });
    await pressShow();
    await waitFor(() => expect(calls.length).toBe(2));
    expect(calls[1].floor_to_floor_ft).toBe(14);
    // (c) the statement is sent only when made.
    fireEvent.click(screen.getByTestId("results-density-statement"));
    await pressShow();
    await waitFor(() => expect(calls.length).toBe(3));
    expect(calls[2].special_density_statement).toBe(true);
  });

  it("the housing program and the height field are editable", async () => {
    render(<ResultsPanel bbl={BBL} fetchImpl={successFetch(loadResultsFixture(JOURNEY))} />);
    const program = screen.getByTestId<HTMLSelectElement>("results-housing-program");
    fireEvent.change(program, { target: { value: "qualifying_senior_housing" } });
    expect(program.value).toBe("qualifying_senior_housing");
    const height = screen.getByTestId<HTMLInputElement>("results-floor-to-floor");
    fireEvent.change(height, { target: { value: "14" } });
    expect(height.value).toBe("14");
  });

  it("S9/R4: a zero or non-number height is refused with the form's message and no call is made", async () => {
    const fetchImpl = vi.fn(async () => jsonResponse(loadResultsFixture(JOURNEY), 200));
    render(<ResultsPanel bbl={BBL} fetchImpl={fetchImpl as unknown as typeof fetch} />);
    for (const bad of ["0", "-3", "abc"]) {
      fireEvent.change(screen.getByTestId("results-floor-to-floor"), { target: { value: bad } });
      await pressShow();
      expect(screen.getByTestId("results-floor-to-floor-error").textContent).toBe(
        "Enter a height in feet greater than zero.",
      );
    }
    expect(fetchImpl).not.toHaveBeenCalled();
  });

  it("S4: a withheld value shows its reason with 'Not known' and no number of its own", async () => {
    const doc = loadResultsFixture(JOURNEY);
    const envelope = doc.answers.permitted_envelope;
    if (envelope.status !== "available" || !envelope.value_states) throw new Error("fixture changed");
    const coverage = envelope.value_states.max_lot_coverage;
    if (!coverage || coverage.way !== "withheld") throw new Error("fixture changed");
    render(<ResultsPanel bbl={BBL} fetchImpl={successFetch(doc)} />);
    await pressShow();
    await screen.findByTestId("three-answers-panel");
    const card = screen.getByTestId("answer-permitted_envelope");
    const coverageRow = within(card)
      .getAllByTestId("answer-withheld-value")
      .map(row => row.textContent ?? "")
      .find(text => text.includes(coverage.reason));
    expect(coverageRow).toBeDefined();
    expect(coverageRow).toContain("Not known");
    expect(coverageRow).not.toMatch(/\d+%/);
  });

  it("S13: a result shows the parking line and no option is called feasible", async () => {
    render(<ResultsPanel bbl={BBL} fetchImpl={successFetch(loadResultsFixture(JOURNEY))} />);
    await pressShow();
    const doc = await screen.findByTestId("results-document");
    expect(screen.getByTestId("results-parking").textContent).toBe(PARKING_LINE);
    // The only mention of "feasible" is the parking line's own disclaimer ("not shown as
    // feasible"); nothing else on the panel presents an option as feasible.
    const withoutParking = (doc.textContent ?? "").split(PARKING_LINE).join("");
    expect(withoutParking).not.toMatch(/\bfeasible\b/);
    expect(doc.textContent ?? "").not.toContain("maximum for this property");
  });

  it("S14: no engine internal word or snake_case reaches the shown panel", async () => {
    render(<ResultsPanel bbl={BBL} fetchImpl={successFetch(loadResultsFixture(JOURNEY))} />);
    await pressShow();
    const doc = await screen.findByTestId("results-document");
    const sectionTexts = within(doc)
      .queryAllByTestId<HTMLElement>("answer-section")
      .map(element => element.textContent ?? "");
    const text = sectionTexts.reduce((rest, part) => rest.split(part).join(""), doc.textContent ?? "");
    for (const code of ["this slice", "Lane A", "task A-12", "not encoded", "not_available", "rule_not"]) {
      expect(text).not.toContain(code);
    }
    expect(text).not.toMatch(SNAKE_CASE);
  });
});

describe("ResultsPanel — W-3 server error states (plain, no stack or path)", () => {
  function errorFetch(status: number, state: string, extra: Record<string, unknown> = {}) {
    return (async () => jsonResponse({ state, message: "a plain message", ...extra }, status)) as typeof fetch;
  }

  const cases: Array<[string, typeof fetch, string]> = [
    ["404 not connected", (async () => jsonResponse({ detail: "Not Found" }, 404)) as typeof fetch, "results-unavailable"],
    ["422 validation_error", errorFetch(422, "validation_error", { detail: { code: "invalid_json" } }), "results-failure-notice"],
    ["429 rate_limited", errorFetch(429, "rate_limited"), "results-failure-notice"],
    ["503 inputs_unavailable", errorFetch(503, "inputs_unavailable"), "results-failure-notice"],
    ["503 lot_conditions_unconfirmed", errorFetch(503, "lot_conditions_unconfirmed"), "results-failure-notice"],
    ["500 internal_error", errorFetch(500, "internal_error"), "results-failure-notice"],
    ["500 internal_contract_error", errorFetch(500, "internal_contract_error"), "results-failure-notice"],
  ];

  for (const [name, fetchImpl, testid] of cases) {
    it(`S11: ${name} shows its plain state`, async () => {
      render(<ResultsPanel bbl={BBL} fetchImpl={fetchImpl} />);
      await pressShow();
      await screen.findByTestId(testid);
      expect(screen.queryByTestId("results-document")).toBeNull();
    });
  }

  it("S11: the 404 card and the two not-available notices say exactly true words", async () => {
    // 404: a request WAS made and "this build" is inner language — plain, true words instead.
    render(<ResultsPanel bbl={BBL} fetchImpl={(async () => jsonResponse({ detail: "Not Found" }, 404)) as typeof fetch} />);
    await pressShow();
    expect((await screen.findByTestId("results-unavailable")).textContent).toContain(
      "The results service is not available on this server. No results were shown.",
    );
    cleanup();
    // 503 inputs_unavailable: the website does not know the cause and makes no promise beyond "safe".
    render(<ResultsPanel bbl={BBL} fetchImpl={(async () => jsonResponse({ state: "inputs_unavailable", message: "not available right now" }, 503)) as typeof fetch} />);
    await pressShow();
    const inputsNotice = await screen.findByTestId("results-failure-notice");
    expect(within(inputsNotice).getByTestId("results-failure-title").textContent).toBe("The results could not be loaded right now");
    expect(inputsNotice.textContent).toContain("Trying again is safe.");
    expect(inputsNotice.textContent).not.toContain("did not return the inputs yet");
    cleanup();
    // 503 lot_conditions_unconfirmed: never called safe to retry; the recovery states the contract truth.
    render(<ResultsPanel bbl={BBL} fetchImpl={(async () => jsonResponse({ state: "lot_conditions_unconfirmed", message: "a recorded fact could not be read" }, 503)) as typeof fetch} />);
    await pressShow();
    const lotNotice = await screen.findByTestId("results-failure-notice");
    expect(within(lotNotice).getByTestId("results-failure-title").textContent).toBe("The results are not available for this lot");
    expect(lotNotice.textContent).toContain("Trying again will give the same answer until that record can be read.");
    expect(within(lotNotice).queryByTestId("results-failure-retry")).toBeNull();
  });

  it("S12: a network failure shows a plain 'could not reach' notice with retry", async () => {
    const fetchImpl = (async () => {
      throw new TypeError("Failed to fetch");
    }) as typeof fetch;
    render(<ResultsPanel bbl={BBL} fetchImpl={fetchImpl} />);
    await pressShow();
    const title = await screen.findByTestId("results-failure-title");
    expect(title.textContent).toBe("Could not reach the server");
    expect(screen.getByTestId("results-failure-retry")).toBeInTheDocument();
  });

  it("S12/S21: a 200 that fails the website's own check renders no partial document", async () => {
    const fetchImpl = (async () => jsonResponse({ contract_version: "1.0.0" }, 200)) as typeof fetch;
    render(<ResultsPanel bbl={BBL} fetchImpl={fetchImpl} />);
    await pressShow();
    await screen.findByTestId("results-failure-notice");
    expect(screen.getByTestId("results-failure-title").textContent).toBe("The results could not be loaded");
    expect(screen.queryByTestId("results-document")).toBeNull();
  });
});

describe("ResultsPanel — W-4 / W-6 / S19 / S22", () => {
  it("W-4: the panel adds no standing not-reviewed label (the dashboard renders the one copy)", async () => {
    render(<ResultsPanel bbl={BBL} fetchImpl={successFetch(loadResultsFixture(JOURNEY))} />);
    await pressShow();
    await screen.findByTestId("results-document");
    expect(screen.queryAllByTestId("standing-review-label")).toHaveLength(0);
  });

  it("W-6: the panel has an accessible name", () => {
    render(<ResultsPanel bbl={BBL} fetchImpl={successFetch(loadResultsFixture(JOURNEY))} />);
    expect(screen.getByRole("region", { name: "Development results" })).toBeInTheDocument();
  });

  it("S19: changing an input after a result shows the stale line; the numbers do not change until pressed again", async () => {
    render(<ResultsPanel bbl={BBL} fetchImpl={successFetch(loadResultsFixture(JOURNEY))} />);
    await pressShow();
    await screen.findByTestId("results-document");
    expect(screen.queryByTestId("results-stale")).toBeNull();
    // Change an input: the stale line appears and the shown numbers are unchanged.
    fireEvent.change(screen.getByTestId("results-housing-program"), {
      target: { value: "qualifying_affordable_housing" },
    });
    expect(screen.getByTestId("results-stale").textContent).toBe(STALE_INPUTS_LINE);
    expect(screen.getByTestId("results-document")).toBeInTheDocument();
    // Press again: the line clears.
    await pressShow();
    await waitFor(() => expect(screen.queryByTestId("results-stale")).toBeNull());
  });

  it("S22: a newer request wins; an older answer never replaces a newer one", async () => {
    const first = deferred<Response>();
    const second = deferred<Response>();
    const docA: Results = {
      ...loadResultsFixture(JOURNEY),
      completeness_line: { text: "First answer completeness.", not_yet_covered: [] },
    };
    const docB: Results = {
      ...loadResultsFixture(JOURNEY),
      completeness_line: { text: "Second answer completeness.", not_yet_covered: [] },
    };
    const responses = [first.promise, second.promise];
    const fetchImpl = (async () => responses.shift()) as unknown as typeof fetch;
    render(<ResultsPanel bbl={BBL} fetchImpl={fetchImpl} />);
    await pressShow(); // request 1 (in flight)
    await pressShow(); // request 2 (in flight) — aborts/supersedes request 1
    // The second answer arrives first, then the first (stale) answer arrives after it.
    second.resolve(jsonResponse(docB, 200));
    await waitFor(() =>
      expect(screen.getByTestId("three-answers-completeness").textContent).toBe("Second answer completeness."),
    );
    first.resolve(jsonResponse(docA, 200));
    // The stale first answer is discarded: the panel still shows the second answer only.
    await waitFor(() =>
      expect(screen.getByTestId("three-answers-completeness").textContent).toBe("Second answer completeness."),
    );
    expect(screen.getByTestId("three-answers-completeness").textContent).not.toBe("First answer completeness.");
  });
});
