import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import {
  ANSWER_KEYS,
  ANSWER_TITLES,
  BUILDING_OPTIONS_BELOW_REASON,
  RULES_NOT_REVIEWED_REASON,
  STRIP_MAX_ITEMS,
  answerView,
  displayQuantity,
  gapKindLine,
  hasFirstBuildingOptions,
  notAvailableText,
  quantityText,
  type AnswerKey,
  type Results,
} from "@/lib/architect/three-answers";
import { loadResultsFixture, loadResultsFixtures } from "@/test-support/results-fixtures";
import { ThreeAnswersPanel } from "../ThreeAnswersPanel";

/**
 * The architect-facing results slice (presentation contract step 3; M5-T149 part A). Renders EVERY
 * committed valid results fixture and reads the expected values from the loaded documents — no
 * number, label, condition or reason is copied into the component or this suite (ruling V2).
 *
 * The three answers lead with a short face (label → value or unavailable state with its gap kind →
 * one exception → Details button); the derivation (other rows, conditions, rule sections,
 * measurement) opens on demand in a focus-managed region that stays in the DOM when closed.
 * Committed fixtures are drafts, so numbers are asserted with `showDraftValues`.
 */

afterEach(cleanup);

const FIXTURES = loadResultsFixtures();
const ALL_AVAILABLE = "synthetic_all_answers_available";
const ENVELOPE_MISSING = "synthetic_envelope_not_available_existing_building";
const BENCHMARK = "recorded_215_16_northern_journey";

// Contract enum codes (results.schema.json) that must never reach the screen (contract §4).
const RAW_CODES = [
  "not_available",
  "not_applicable",
  "missing_input",
  "rule_not_implemented",
  "rule_not_reviewed",
  "eligibility_unresolved",
  "geometry_unsupported",
  "square_feet",
  "dwelling_units",
  "approximate_tax_map",
  "city_records",
  "survey_entered",
  "site_fact",
  "rule_table",
  "zoning_resolution",
];
const SNAKE_CASE = /\b[a-z0-9]+(?:_[a-z0-9]+)+\b/;

function card(key: AnswerKey): HTMLElement {
  return screen.getByTestId(`answer-${key}`);
}

function panelText(): string {
  return screen.getByTestId("three-answers-panel").textContent ?? "";
}

/** Text with every given part removed, to check that nothing numeric is left. */
function without(text: string, ...parts: string[]): string {
  return parts.reduce((rest, part) => rest.split(part).join(""), text);
}

function notAvailableFor(doc: Results, key: AnswerKey, reason: string): string {
  return key === "building_option" && hasFirstBuildingOptions(doc)
    ? notAvailableText(BUILDING_OPTIONS_BELOW_REASON, key)
    : notAvailableText(reason, key);
}
function gapKindFor(
  doc: Results,
  key: AnswerKey,
  gapKind: Parameters<typeof gapKindLine>[0],
): string | null {
  return key === "building_option" && hasFirstBuildingOptions(doc) ? null : gapKindLine(gapKind);
}

it("loads the committed valid results fixtures (never a vacuous run)", () => {
  const names = FIXTURES.map(fixture => fixture.name);
  expect(names.length).toBeGreaterThanOrEqual(4);
  expect(names).toContain(ALL_AVAILABLE);
  expect(names).toContain(ENVELOPE_MISSING);
  expect(names).toContain(BENCHMARK);
});

for (const { name, doc } of FIXTURES) {
  describe(`results fixture ${name}`, () => {
    it("shows each available answer's headline, every value, its exceptions, sections and measurement", () => {
      render(<ThreeAnswersPanel results={doc} showDraftValues />);
      for (const key of ANSWER_KEYS) {
        const answer = doc.answers[key];
        if (answer.status !== "available") continue;
        const cardEl = card(key);
        const view = answerView(doc, key, true);
        // An available answer with no shown values collapses to a not-available view (NO_VALUE_REASON);
        // the committed fixtures do not carry that, but skip it rather than assert a headline.
        if (view.kind !== "available") continue;
        // The headline is on the face: a number when the headline key is a value, else its reason.
        if (view.headline.kind === "value") {
          expect(within(cardEl).getAllByTestId("answer-headline-number")).toHaveLength(1);
        } else {
          expect(within(cardEl).getByTestId("answer-headline-withheld")).toBeInTheDocument();
        }
        // Every shown value's number+unit is in the card (face or details — details stay in the DOM).
        for (const value of answer.values) {
          const shown = quantityText(displayQuantity(value.value, value.unit));
          expect(cardEl.textContent, value.key).toContain(shown);
          if (Number.isInteger(value.value)) {
            expect(cardEl.textContent).toContain(value.value.toLocaleString("en-US"));
          }
          if (value.exception_label) expect(cardEl.textContent).toContain(value.exception_label);
        }
        // The detail region carries the rule sections and the measurement basis, hidden by default.
        const region = within(cardEl).getByTestId("answer-details-region");
        expect(region).toHaveAttribute("hidden");
        expect(region).toHaveTextContent(`Measurements: ${answer.measurement.label}`);
        const sectionItems = within(cardEl)
          .getAllByTestId("answer-section")
          .map(item => item.textContent ?? "");
        for (const value of answer.values) {
          const sections = sectionItems.find(item => item.startsWith(`${value.label}: `));
          expect(sections, value.key).toBeDefined();
          for (const section of value.zr_sections) expect(sections).toContain(section);
        }
        // At most one exception beside each number (contract §4).
        const exceptionCount = answer.values.filter(value => value.exception_label).length;
        expect(within(cardEl).queryAllByTestId("answer-exception")).toHaveLength(exceptionCount);
      }
    });

    it("shows a not-available answer as 'Not available — <reason>', its gap line, no number, no details", () => {
      render(<ThreeAnswersPanel results={doc} showDraftValues />);
      for (const key of ANSWER_KEYS) {
        const answer = doc.answers[key];
        if (answer.status !== "not_available") continue;
        const cardEl = card(key);
        const expected = notAvailableFor(doc, key, answer.reason);
        expect(expected.startsWith("Not available — ")).toBe(true);
        expect(within(cardEl).getByTestId("answer-not-available").textContent).toBe(expected);
        const gapLine = gapKindFor(doc, key, answer.gap_kind);
        if (gapLine) {
          expect(within(cardEl).getByTestId("answer-gap-kind").textContent).toBe(gapLine);
        } else {
          expect(within(cardEl).queryByTestId("answer-gap-kind")).toBeNull();
        }
        expect(cardEl.textContent).toBe(`${ANSWER_TITLES[key]}${expected}${gapLine ?? ""}`);
        expect(without(cardEl.textContent ?? "", expected, gapLine ?? "")).not.toMatch(/\d/);
        expect(within(cardEl).queryByTestId("answer-headline")).toBeNull();
        expect(within(cardEl).queryByTestId("answer-details-button")).toBeNull();
      }
    });

    it("by default (an architect surface) a draft document shows no number at all", () => {
      render(<ThreeAnswersPanel results={doc} />);
      expect(screen.queryByTestId("three-answers-draft-tag")).toBeNull();
      for (const key of ANSWER_KEYS) {
        const answer = doc.answers[key];
        const cardEl = card(key);
        const expected =
          answer.status === "not_available"
            ? notAvailableFor(doc, key, answer.reason)
            : doc.draft
              ? `Not available — ${RULES_NOT_REVIEWED_REASON}`
              : null;
        if (expected === null) continue;
        const gapLine = answer.status === "not_available" ? gapKindFor(doc, key, answer.gap_kind) : null;
        expect(within(cardEl).getByTestId("answer-not-available").textContent).toBe(expected);
        expect(cardEl.textContent).toBe(`${ANSWER_TITLES[key]}${expected}${gapLine ?? ""}`);
        expect(without(cardEl.textContent ?? "", expected, gapLine ?? "")).not.toMatch(/\d/);
      }
      if (doc.draft) {
        expect(screen.queryAllByTestId("answer-headline")).toHaveLength(0);
        expect(screen.queryAllByTestId("answer-details-button")).toHaveLength(0);
      }
    });

    it("keeps the status strip to at most three items, with the details behind a tap", () => {
      render(<ThreeAnswersPanel results={doc} showDraftValues />);
      const strip = screen.getByTestId("three-answers-status-strip");
      expect(strip.tagName).toBe("DETAILS");
      const items = within(strip)
        .queryAllByTestId("three-answers-status-item")
        .map(item => item.textContent);
      expect(items.length).toBeLessThanOrEqual(STRIP_MAX_ITEMS);
      expect(items).toEqual(doc.status_strip.slice(0, STRIP_MAX_ITEMS).map(item => item.text));
      expect(screen.getAllByTestId("three-answers-status-strip")).toHaveLength(1);
    });

    it("shows the completeness line as the document states it", () => {
      render(<ThreeAnswersPanel results={doc} showDraftValues />);
      expect(screen.getByTestId("three-answers-completeness").textContent).toBe(
        doc.completeness_line.text,
      );
    });

    it("shows no internal code, value key or source id, with or without draft numbers", () => {
      for (const showDraftValues of [false, true]) {
        render(<ThreeAnswersPanel results={doc} showDraftValues={showDraftValues} />);
        const text = panelText();
        expect(text).not.toMatch(SNAKE_CASE);
        for (const code of RAW_CODES) expect(text).not.toContain(code);
        const outsideSections = without(
          text,
          ...screen.queryAllByTestId("answer-section").map(item => item.textContent ?? ""),
        );
        for (const key of ANSWER_KEYS) {
          const answer = doc.answers[key];
          if (answer.status !== "available") continue;
          for (const value of answer.values) {
            for (const source of value.sources) {
              if (source.kind === "zoning_resolution") {
                expect(value.zr_sections, value.key).toContain(source.ref);
                expect(outsideSections).not.toContain(source.ref);
              } else {
                expect(text).not.toContain(source.ref);
              }
            }
          }
        }
        cleanup();
      }
    });
  });
}

describe("S1 — the identity line comes first (presentation contract §2 item 1)", () => {
  it("names the lot, the program and the floor height, read from the document's scope", () => {
    const doc = loadResultsFixture(BENCHMARK);
    const scope = doc.scope;
    if (!scope) throw new Error("fixture changed: the benchmark must carry a scope");
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const identity = screen.getByTestId("three-answers-identity");
    expect(within(identity).getByTestId("three-answers-identity-lot").textContent).toBe(
      scope.lot.display,
    );
    const values = within(identity)
      .getAllByTestId("three-answers-identity-fact-value")
      .map(element => element.textContent);
    const program = scope.assumptions.find(entry => entry.key === "housing_program");
    const floor = scope.assumptions.find(entry => entry.key === "floor_to_floor_ft");
    if (!program || !floor) throw new Error("fixture changed: program/floor assumptions missing");
    expect(values).toContain("standard residence"); // housing_program, in plain words
    expect(values).toContain("10 feet"); // floor_to_floor_ft, grouped with its unit
    expect(identity.textContent ?? "").not.toMatch(SNAKE_CASE);
  });

  it("renders no identity line for a document that carries no scope", () => {
    const doc = loadResultsFixture(ALL_AVAILABLE);
    expect(doc.scope ?? null).toBeNull();
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    expect(screen.queryByTestId("three-answers-identity")).toBeNull();
  });

  it("composes a left region (identity + answers) and a right region (details + options), in that order", () => {
    // The desktop two-column grid lives in these two regions; jsdom cannot measure the grid itself
    // (the browser test checks the 44/56 widths), so this proves the regions exist in reading order.
    const doc = loadResultsFixture(BENCHMARK);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const left = screen.getByTestId("three-answers-left");
    const right = screen.getByTestId("three-answers-right");
    // left precedes right in the DOM (the stacked reading order below 1000 px)
    const relation = left.compareDocumentPosition(right);
    expect(relation & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    // the answers (and the identity line) are in the left region
    expect(within(left).getByTestId("three-answers-identity")).toBeInTheDocument();
    for (const key of ANSWER_KEYS) {
      expect(within(left).getByTestId(`answer-${key}`)).toBeInTheDocument();
    }
    // the details (scope) and Part B's building options are in the right region
    expect(within(right).getByTestId("three-answers-scope")).toBeInTheDocument();
    expect(within(right).getByTestId("first-building-options")).toBeInTheDocument();
  });
});

describe("S3 — shared conditions stated once (presentation contract §1/§3; walkthrough note N3)", () => {
  it("lists each distinct condition once as 'Condition N', never an internal id such as 'C1'", () => {
    const doc = loadResultsFixture(BENCHMARK);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const block = screen.getByTestId("shared-conditions");
    const items = within(block).getAllByTestId("shared-condition");
    // The benchmark's two "If …" lines repeat across many results; they are listed once here.
    expect(items.length).toBe(2);
    const labels = within(block)
      .getAllByTestId("shared-condition-label")
      .map(label => label.textContent);
    expect(labels).toEqual(["Condition 1", "Condition 2"]);
    expect(block.textContent ?? "").not.toMatch(/\bC\d\b/); // never the adapter id "C1"/"C2"
    // Each line's text is read from the document (the same "If …" the engine emitted).
    const fa = doc.answers.floor_area_allowance;
    if (fa.status !== "available" || !fa.value_states) throw new Error("fixture changed");
    const headlineState = fa.value_states.max_residential_floor_area;
    if (!headlineState || headlineState.way !== "conditional") throw new Error("fixture changed");
    for (const condition of headlineState.conditions) {
      expect(block.textContent).toContain(condition.assumption);
    }
  });

  it("shows at most three conditions and counts the rest behind a label (S3 cap)", () => {
    // A probe that carries exactly five distinct conditions proves the cap holds past three. Built
    // from the no-condition all-available fixture so the only conditions are the five supplied here.
    const base = loadResultsFixture(ALL_AVAILABLE);
    const fa = base.answers.floor_area_allowance;
    if (fa.status !== "available") throw new Error("fixture changed");
    const conditions = [1, 2, 3, 4, 5].map(n => ({
      kind: "unchecked_condition" as const,
      assumption: `If probe condition ${n} holds`,
      settled_by: "A probe source",
    }));
    const doc: Results = {
      ...base,
      contract_version: "1.3.0",
      answers: {
        ...base.answers,
        floor_area_allowance: {
          ...fa,
          value_states: {
            max_residential_floor_area: { way: "conditional", conditions },
          },
        },
      },
    };
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const block = screen.getByTestId("shared-conditions");
    expect(within(block).getAllByTestId("shared-condition")).toHaveLength(3);
    expect(within(block).getByTestId("shared-conditions-more").textContent).toBe("2 more");
  });

  it("shows no shared-conditions block for a document with no conditions", () => {
    const doc = loadResultsFixture(ALL_AVAILABLE);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    expect(screen.queryByTestId("shared-conditions")).toBeNull();
  });
});

describe("S4 — each result's order and the Details focus behaviour (presentation contract §4; UX-09)", () => {
  it("shows a Details button whose region is hidden until opened", () => {
    const doc = loadResultsFixture(BENCHMARK);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const allowance = card("floor_area_allowance");
    const button = within(allowance).getByTestId("answer-details-button");
    expect(button.getAttribute("aria-expanded")).toBe("false");
    expect(within(allowance).getByTestId("answer-details-region")).toHaveAttribute("hidden");
  });

  it("moves focus into the region on open and returns focus to the button on Escape", () => {
    const doc = loadResultsFixture(BENCHMARK);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const allowance = card("floor_area_allowance");
    const button = within(allowance).getByTestId<HTMLButtonElement>("answer-details-button");
    const region = within(allowance).getByTestId<HTMLDivElement>("answer-details-region");
    fireEvent.click(button);
    expect(region).not.toHaveAttribute("hidden");
    expect(button.getAttribute("aria-expanded")).toBe("true");
    expect(document.activeElement).toBe(region);
    fireEvent.keyDown(region, { key: "Escape" });
    expect(region).toHaveAttribute("hidden");
    expect(button.getAttribute("aria-expanded")).toBe("false");
    expect(document.activeElement).toBe(button);
  });

  it("marks a conditional headline figure 'Conditional' on the face so it never reads as confirmed", () => {
    const doc = loadResultsFixture(BENCHMARK);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const allowance = card("floor_area_allowance");
    const headline = within(allowance).getByTestId("answer-headline");
    expect(within(headline).getByTestId("answer-conditional-marker").textContent).toBe("Conditional");
  });

  it("shows no 'Conditional' marker on a settled figure", () => {
    const base = loadResultsFixture(ALL_AVAILABLE);
    render(<ThreeAnswersPanel results={base} showDraftValues />);
    // all_available carries no value_states, so every value is settled: no marker anywhere.
    expect(screen.queryAllByTestId("answer-conditional-marker")).toHaveLength(0);
  });
});

describe("S5 — the legal unit limit sits with the allowance, apart from the estimate (DB-214 N2)", () => {
  function densityStatementProbe(): Results {
    // The owner's special-density statement makes the standard legal unit limit a CONDITIONAL
    // value of the floor-area allowance (walkthrough state 5). Built from the benchmark; the figure
    // and condition are supplied as document data, never typed by the component.
    const base = loadResultsFixture(BENCHMARK);
    const fa = base.answers.floor_area_allowance;
    if (fa.status !== "available") throw new Error("fixture changed");
    return {
      ...base,
      answers: {
        ...base.answers,
        floor_area_allowance: {
          ...fa,
          values: [
            ...fa.values,
            {
              key: "legal_unit_limit_standard",
              label: "Legal dwelling-unit limit, standard residences",
              value: 29,
              unit: "dwelling_units",
              exception_label: null,
              zr_sections: ["ZR 23-22"],
              sources: [],
            },
          ],
          value_states: {
            ...(fa.value_states ?? {}),
            legal_unit_limit_standard: {
              way: "conditional",
              conditions: [
                {
                  kind: "unchecked_condition",
                  assumption: "If the lot is not in a special density area, as the user states",
                  settled_by: "Sourced evidence of the special density area",
                },
              ],
            },
          },
        },
      },
    };
  }

  it("shows '29 units' with the allowance, marked Conditional, and never in the building-options section", () => {
    const doc = densityStatementProbe();
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const allowance = card("floor_area_allowance");
    expect(allowance.textContent).toContain("29 units");
    // it is a conditional value, so a 'Conditional' marker qualifies it (never reads as confirmed)
    expect(within(allowance).getAllByTestId("answer-conditional-marker").length).toBeGreaterThan(0);
    // the estimate is the building options' job (Part B); the legal limit never appears there
    const options = screen.getByTestId("first-building-options");
    expect(options.textContent ?? "").not.toContain("29 units");
    // and the estimate range is not inside the allowance card (kept apart — N2)
    expect(allowance.textContent ?? "").not.toContain("17.27 to 21.59");
  });
});

describe("S8 — normal and partial states (UX-02, UX-03)", () => {
  it("the normal state shows three headline numbers with units", () => {
    const doc = loadResultsFixture(ALL_AVAILABLE);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    for (const key of ANSWER_KEYS) {
      expect(within(card(key)).getByTestId("answer-headline-number")).toBeInTheDocument();
    }
  });

  it("the partial state shows a withheld result as 'Not known' with its kind of gap and no number", () => {
    const doc = loadResultsFixture(BENCHMARK);
    const env = doc.answers.permitted_envelope;
    if (env.status !== "available" || !env.value_states) throw new Error("fixture changed");
    const coverage = env.value_states.max_lot_coverage;
    if (!coverage || coverage.way !== "withheld") throw new Error("fixture changed");
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const envCard = card("permitted_envelope");
    const row = within(envCard)
      .getAllByTestId("answer-withheld-value")
      .find(entry => (entry.querySelector("dt")?.textContent ?? "") === coverage.label);
    if (!row) throw new Error("the withheld coverage row is missing");
    expect(within(row).getByTestId("answer-withheld-reason").textContent).toBe(
      `Not known — ${coverage.reason}`,
    );
    expect(row.textContent ?? "").not.toMatch(/\d+%/); // no number falls back
    const gap = within(row).getByTestId("answer-gap-kind");
    expect(gap.textContent).toBe("Missing information about this property.");
  });
});

describe("a withheld headline key shows its reason, never the first value (R556)", () => {
  it("renders the withheld reason as the headline, no number from another value", () => {
    const base = loadResultsFixture(ALL_AVAILABLE);
    const envelope = base.answers.permitted_envelope;
    if (envelope.status !== "available") throw new Error("fixture changed");
    const withoutHeight = envelope.values.filter(value => value.key !== "max_building_height");
    const probe: Results = {
      ...base,
      contract_version: "1.3.0",
      answers: {
        ...base.answers,
        permitted_envelope: {
          ...envelope,
          values: withoutHeight,
          value_states: {
            max_building_height: {
              way: "withheld",
              label: "Maximum building height",
              reason: "The height depends on a rule the program has not built yet.",
              gap_kind: "work_owed",
              resolved_by: "Building the rule and checking it against a worked example",
            },
          },
        },
      },
    };
    render(<ThreeAnswersPanel results={probe} showDraftValues />);
    const envCard = card("permitted_envelope");
    expect(within(envCard).queryByTestId("answer-headline")).toBeNull();
    const headlineWithheld = within(envCard).getByTestId("answer-headline-withheld");
    expect(headlineWithheld.textContent).toContain("Maximum building height");
    expect(headlineWithheld.textContent).toContain("Not known");
  });
});

describe("fixture-specific behaviour", () => {
  it("envelope fixture: the allowance still shows; the envelope and option read their reasons", () => {
    const doc = loadResultsFixture(ENVELOPE_MISSING);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    expect(within(card("floor_area_allowance")).getByTestId("answer-headline")).toBeInTheDocument();
    expect(within(card("permitted_envelope")).getByTestId("answer-not-available").textContent).toBe(
      "Not available — height rules for this district are not built yet.",
    );
    expect(within(card("building_option")).getByTestId("answer-not-available").textContent).toBe(
      "Not available — it needs the permitted envelope.",
    );
    // Owner wording (D-090-R038): the remaining-capacity row reads "Not confirmed" + reason, in the
    // allowance card's detail.
    const allowance = card("floor_area_allowance");
    const row = within(allowance).getByTestId("answer-supplement");
    expect(row.querySelector<HTMLElement>("dt")?.textContent).toBe("Remaining development capacity");
    expect(within(allowance).getByTestId("answer-supplement-not-available").textContent).toBe(
      "Not confirmed",
    );
    expect(within(allowance).getByTestId("answer-supplement-reason").textContent).toBe(
      "Needs verified zoning-lot boundaries and existing zoning floor area.",
    );
  });

  it("all-available fixture: no remaining row without a kept building; the option reaches the allowance", () => {
    const doc = loadResultsFixture(ALL_AVAILABLE);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    expect(screen.queryByTestId("answer-supplement")).toBeNull();
    expect(within(card("building_option")).getByTestId("answer-shortfall").textContent).toContain(
      "Reaches the full floor-area allowance.",
    );
    expect(screen.getByTestId("three-answers-draft-tag")).toBeInTheDocument();
  });

  it("strip items beyond three move behind the strip", () => {
    const doc: Results = {
      ...loadResultsFixture(ALL_AVAILABLE),
      status_strip: ["One", "Two", "Three", "Four", "Five"].map(text => ({ text })),
    };
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const strip = screen.getByTestId("three-answers-status-strip");
    expect(
      within(strip)
        .getAllByTestId("three-answers-status-item")
        .map(item => item.textContent),
    ).toEqual(["One", "Two", "Three"]);
    expect(
      within(strip)
        .getAllByTestId("three-answers-status-overflow")
        .map(item => item.textContent),
    ).toEqual(["Four", "Five"]);
  });

  it("a document that is not a draft shows its numbers without the lane-flag option", () => {
    const doc: Results = { ...loadResultsFixture(ALL_AVAILABLE), draft: false };
    render(<ThreeAnswersPanel results={doc} />);
    for (const key of ANSWER_KEYS) {
      expect(within(card(key)).getByTestId("answer-headline")).toBeInTheDocument();
    }
    expect(screen.queryByTestId("three-answers-draft-tag")).toBeNull();
  });
});

describe("the tokens: no colour literal lives in three-answers.css (every part)", () => {
  it("uses only var(--token) for colour — no hex, rgb/rgba or hsl literal", () => {
    const css = readFileSync(
      resolve(process.cwd(), "src/components/architect/answers/three-answers.css"),
      "utf8",
    );
    expect(css).not.toMatch(/#[0-9a-fA-F]{3,8}\b/);
    expect(css).not.toMatch(/\brgba?\(/);
    expect(css).not.toMatch(/\bhsla?\(/);
    // and it does use the shared tokens
    expect(css).toMatch(/var\(--pt-color-/);
  });
});
