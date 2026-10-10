import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import {
  ANSWER_KEYS,
  ANSWER_TITLES,
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
import { scheduledFloorAreaLine } from "@/lib/architect/presented-results";
import { loadResultsFixture, loadResultsFixtures } from "@/test-support/results-fixtures";
import { ThreeAnswersPanel } from "../ThreeAnswersPanel";

/**
 * The architect-facing results slice after ruling V11 (M5-T149 part A, correction). Renders EVERY
 * committed valid results fixture and reads the expected values from the loaded documents — no
 * number, label, condition or reason is copied into the component or this suite (ruling V2).
 *
 * The building-option card reads the scheduled area from the listed building (never "Not available"
 * when one is listed); each no-value result reads one wording; conditions are referred to by name;
 * a short open-items list sits with the shared conditions; the derivation opens on demand.
 */

afterEach(cleanup);

const FIXTURES = loadResultsFixtures();
const ALL_AVAILABLE = "synthetic_all_answers_available";
const ENVELOPE_MISSING = "synthetic_envelope_not_available_existing_building";
const BENCHMARK = "recorded_215_16_northern_journey";

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
  "building_alternatives",
  "buildings_not_worked",
];
const SNAKE_CASE = /\b[a-z0-9]+(?:_[a-z0-9]+)+\b/;
// Developer / project-status phrases the owner removed (ruling V11 (3)/(4); source-080 finding 2).
const BANNED_WORDS = ["still owed", "Not built yet", "Not worked", "internal preview"];

function card(key: AnswerKey): HTMLElement {
  return screen.getByTestId(`answer-${key}`);
}

function panelText(): string {
  return screen.getByTestId("three-answers-panel").textContent ?? "";
}

function without(text: string, ...parts: string[]): string {
  return parts.reduce((rest, part) => rest.split(part).join(""), text);
}

/** The building-option card is a scheduled summary (not answerView) when the document carries a
 * first-building-options section; the generic loop skips it then and S13 covers it. */
function isSpecialBuildingOption(doc: Results, key: AnswerKey): boolean {
  return key === "building_option" && hasFirstBuildingOptions(doc);
}

it("loads the committed valid results fixtures (never a vacuous run)", () => {
  const names = FIXTURES.map(fixture => fixture.name);
  expect(names.length).toBeGreaterThanOrEqual(4);
  expect(names).toContain(ALL_AVAILABLE);
  expect(names).toContain(BENCHMARK);
});

for (const { name, doc } of FIXTURES) {
  describe(`results fixture ${name}`, () => {
    it("shows each available answer's headline, every value, its sections and measurement", () => {
      render(<ThreeAnswersPanel results={doc} showDraftValues />);
      for (const key of ANSWER_KEYS) {
        if (isSpecialBuildingOption(doc, key)) continue;
        const answer = doc.answers[key];
        if (answer.status !== "available") continue;
        const cardEl = card(key);
        const view = answerView(doc, key, true);
        if (view.kind !== "available") continue;
        if (view.headline.kind === "value") {
          expect(within(cardEl).getAllByTestId("answer-headline-number")).toHaveLength(1);
        } else {
          expect(within(cardEl).getByTestId("answer-headline-withheld")).toBeInTheDocument();
        }
        for (const value of answer.values) {
          const shown = quantityText(displayQuantity(value.value, value.unit));
          expect(cardEl.textContent, value.key).toContain(shown);
          if (value.exception_label) expect(cardEl.textContent).toContain(value.exception_label);
        }
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
        const exceptionCount = answer.values.filter(value => value.exception_label).length;
        expect(within(cardEl).queryAllByTestId("answer-exception")).toHaveLength(exceptionCount);
      }
    });

    it("shows a not-available answer as 'Not available — <reason>', its gap tag, no number, no details", () => {
      render(<ThreeAnswersPanel results={doc} showDraftValues />);
      for (const key of ANSWER_KEYS) {
        if (isSpecialBuildingOption(doc, key)) continue;
        const answer = doc.answers[key];
        if (answer.status !== "not_available") continue;
        const cardEl = card(key);
        const expected = notAvailableText(answer.reason, key);
        expect(within(cardEl).getByTestId("answer-not-available").textContent).toBe(expected);
        const gapLine = gapKindLine(answer.gap_kind);
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
        if (isSpecialBuildingOption(doc, key)) continue;
        const answer = doc.answers[key];
        const cardEl = card(key);
        const expected =
          answer.status === "not_available"
            ? notAvailableText(answer.reason, key)
            : doc.draft
              ? `Not available — ${RULES_NOT_REVIEWED_REASON}`
              : null;
        if (expected === null) continue;
        const gapLine = answer.status === "not_available" ? gapKindLine(answer.gap_kind) : null;
        expect(within(cardEl).getByTestId("answer-not-available").textContent).toBe(expected);
        expect(cardEl.textContent).toBe(`${ANSWER_TITLES[key]}${expected}${gapLine ?? ""}`);
      }
    });

    it("keeps the status strip to at most three items", () => {
      render(<ThreeAnswersPanel results={doc} showDraftValues />);
      const strip = screen.getByTestId("three-answers-status-strip");
      const items = within(strip)
        .queryAllByTestId("three-answers-status-item")
        .map(item => item.textContent);
      expect(items.length).toBeLessThanOrEqual(STRIP_MAX_ITEMS);
      expect(items).toEqual(doc.status_strip.slice(0, STRIP_MAX_ITEMS).map(item => item.text));
    });

    it("shows the completeness line as the document states it", () => {
      render(<ThreeAnswersPanel results={doc} showDraftValues />);
      expect(screen.getByTestId("three-answers-completeness").textContent).toBe(
        doc.completeness_line.text,
      );
    });

    it("shows no internal code, developer word, value key or source id", () => {
      for (const showDraftValues of [false, true]) {
        render(<ThreeAnswersPanel results={doc} showDraftValues={showDraftValues} />);
        const text = panelText();
        expect(text).not.toMatch(SNAKE_CASE);
        for (const code of RAW_CODES) expect(text).not.toContain(code);
        for (const banned of BANNED_WORDS) expect(text).not.toContain(banned);
        cleanup();
      }
    });
  });
}

describe("S1 — the identity line comes first, and the two-column composition (ruling V11 (7))", () => {
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
    expect(values).toContain("standard residence");
    expect(values).toContain("10 feet");
    expect(identity.textContent ?? "").not.toMatch(SNAKE_CASE);
  });

  it("orders the left column: identity, strip, the three answers, building options, then conditions (V12)", () => {
    const doc = loadResultsFixture(BENCHMARK);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const left = screen.getByTestId("three-answers-left");
    const right = screen.getByTestId("three-answers-right");
    expect(left.compareDocumentPosition(right) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    // The contract's reading order (§2): the answers lead the first screen, the shared conditions and
    // open items come last in the left column; the scope detail stays in the right column.
    const sequence = [
      within(left).getByTestId("three-answers-identity"),
      within(left).getByTestId("three-answers-status-strip"),
      within(left).getByTestId("answer-floor_area_allowance"),
      within(left).getByTestId("answer-permitted_envelope"),
      within(left).getByTestId("answer-building_option"),
      within(left).getByTestId("first-building-options"),
      within(left).getByTestId("shared-conditions"),
    ];
    for (let index = 1; index < sequence.length; index += 1) {
      const relation = sequence[index - 1].compareDocumentPosition(sequence[index]);
      expect(relation & Node.DOCUMENT_POSITION_FOLLOWING, `item ${index} must follow ${index - 1}`).toBeTruthy();
    }
    // the assumed conditions / scope detail are in the RIGHT column.
    expect(within(right).getByTestId("three-answers-scope")).toBeInTheDocument();
    expect(within(right).queryByTestId("first-building-options")).toBeNull();
  });

  it("renders no identity line for a document that carries no scope", () => {
    const doc = loadResultsFixture(ALL_AVAILABLE);
    expect(doc.scope ?? null).toBeNull();
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    expect(screen.queryByTestId("three-answers-identity")).toBeNull();
  });
});

describe("S3/S14 — shared conditions once, named, with the open-items list (ruling V11 (5)/(6))", () => {
  it("lists each distinct condition once as 'Condition N', never an internal id such as 'C1'", () => {
    const doc = loadResultsFixture(BENCHMARK);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const block = screen.getByTestId("shared-conditions");
    expect(within(block).getAllByTestId("shared-condition")).toHaveLength(2);
    const labels = within(block)
      .getAllByTestId("shared-condition-label")
      .map(label => label.textContent);
    expect(labels).toEqual(["Condition 1", "Condition 2"]);
    expect(block.textContent ?? "").not.toMatch(/\bC\d\b/);
  });

  it("shows a short 'What needs resolving' list — at most three — each with what settles it", () => {
    const doc = loadResultsFixture(BENCHMARK);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const items = screen.getAllByTestId("open-item");
    expect(items.length).toBeGreaterThan(0);
    expect(items.length).toBeLessThanOrEqual(3);
    for (const item of items) {
      expect((within(item).getByTestId("open-item-affects").textContent ?? "").length).toBeGreaterThan(0);
      expect(within(item).getByTestId("open-item-settle").textContent).toContain(
        "What would settle it:",
      );
    }
  });

  it("refers to the shared conditions by name under the answers and the building option", () => {
    const doc = loadResultsFixture(BENCHMARK);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const refs = screen.getAllByTestId("answer-condition-refs").map(element => element.textContent ?? "");
    expect(refs.length).toBeGreaterThan(0);
    expect(refs.some(ref => ref.startsWith("Applies: Condition 1"))).toBe(true);
    // never the full condition text under a result (stated once above) — no "If …" outside the
    // shared-conditions block.
    const shared = screen.getByTestId("shared-conditions");
    const refNodes = screen.getAllByTestId("answer-condition-refs");
    for (const node of refNodes) {
      expect(shared.contains(node)).toBe(false);
      expect(node.textContent ?? "").not.toContain("If ");
    }
  });
});

describe("S4 — the Details focus behaviour and the 'Conditional' marker (UX-09; ruling L3)", () => {
  it("moves focus into the region on open and returns focus to the button on Escape", () => {
    const doc = loadResultsFixture(BENCHMARK);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const allowance = card("floor_area_allowance");
    const button = within(allowance).getByTestId<HTMLButtonElement>("answer-details-button");
    const region = within(allowance).getByTestId<HTMLDivElement>("answer-details-region");
    expect(region).toHaveAttribute("hidden");
    fireEvent.click(button);
    expect(region).not.toHaveAttribute("hidden");
    expect(document.activeElement).toBe(region);
    fireEvent.keyDown(region, { key: "Escape" });
    expect(region).toHaveAttribute("hidden");
    expect(document.activeElement).toBe(button);
  });

  it("marks a conditional headline figure 'Conditional' on the face; a settled figure has none", () => {
    const doc = loadResultsFixture(BENCHMARK);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const allowance = card("floor_area_allowance");
    const headline = within(allowance).getByTestId("answer-headline");
    expect(within(headline).getByTestId("answer-conditional-marker").textContent).toBe("Conditional");
    cleanup();
    render(<ThreeAnswersPanel results={loadResultsFixture(ALL_AVAILABLE)} showDraftValues />);
    expect(screen.queryAllByTestId("answer-conditional-marker")).toHaveLength(0);
  });
});

describe("S13 — the building-option answer is the scheduled area (ruling V11 (2))", () => {
  it("S8: at 10 ft the card reads the ONE-LINE scheduled phrase, never 'Not available'/'shown below'", () => {
    const doc = loadResultsFixture(BENCHMARK);
    const alternative = (doc.building_alternatives ?? [])[0];
    if (!alternative) throw new Error("fixture changed: the benchmark must list a building");
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const cardEl = card("building_option");
    // S8: one wording across the screen — the compact card uses the same adapter line as the block.
    expect(within(cardEl).getByTestId("answer-scheduled-area").textContent).toBe(
      scheduledFloorAreaLine(quantityText(displayQuantity(alternative.total_floor_area_sqft, "square_feet"))),
    );
    // the wave-20 pair no longer renders on the card.
    expect(within(cardEl).queryByTestId("answer-site-fit")).toBeNull();
    expect(cardEl.textContent ?? "").not.toContain("Site fit not verified");
    expect(cardEl.textContent ?? "").not.toContain("Not available");
    expect(cardEl.textContent ?? "").not.toContain("shown below");
  });

  it("with no worked building reads 'Not known' with the document's reason, never a scheduled area", () => {
    const base = loadResultsFixture(BENCHMARK);
    const notWorked = base.buildings_not_worked ?? [];
    if (notWorked.length === 0) throw new Error("fixture changed: need a not-worked building");
    const doc: Results = { ...base, building_alternatives: [], buildings_not_worked: notWorked };
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const cardEl = card("building_option");
    expect(within(cardEl).getByTestId("answer-not-known").textContent).toBe(
      `Not known — ${notWorked[0].reason}`,
    );
    expect(cardEl.textContent ?? "").not.toContain("Scheduled floor area");
    expect(cardEl.textContent ?? "").not.toContain("Not available");
  });
});

describe("S5 — the legal unit limit sits with the allowance, apart from the estimate (DB-214 N2)", () => {
  function densityStatementProbe(): Results {
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

  const DENSITY_CONDITION = "If the lot is not in a special density area, as the user states";

  it("shows '29 units' with the allowance, apart from the estimate", () => {
    const doc = densityStatementProbe();
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const allowance = card("floor_area_allowance");
    expect(allowance.textContent).toContain("29 units");
    // the estimate is the building options' job; the legal limit never appears there
    const options = screen.getByTestId("first-building-options");
    expect(options.textContent ?? "").not.toContain("29 units");
    // and the estimate range is not inside the allowance card (kept apart — N2)
    expect(allowance.textContent ?? "").not.toContain("17.27 to 21.59");
  });

  it("keeps the density condition IN FULL with the '29 units' value, never only in the shared list", () => {
    // The statement's condition applies to the legal-unit-limit alone, so it is a local exception:
    // shown in full with that result (the contract's local-exception rule), not in the shared list.
    const doc = densityStatementProbe();
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const allowance = card("floor_area_allowance");
    const legalRow = within(allowance)
      .getAllByTestId("answer-value")
      .find(row => (row.querySelector("dt")?.textContent ?? "").includes("Legal dwelling-unit limit"));
    if (!legalRow) throw new Error("the legal-limit value row is missing");
    expect(legalRow.textContent).toContain(DENSITY_CONDITION);
    // it is a one-result condition, so it is NOT named and NOT in the shared-conditions list.
    const shared = screen.getByTestId("shared-conditions");
    expect(shared.textContent ?? "").not.toContain(DENSITY_CONDITION);
    // the shared list still holds the two conditions shared across the other results, by name.
    expect(within(shared).getAllByTestId("shared-condition").length).toBeGreaterThanOrEqual(2);
  });
});

describe("S8 — normal and partial states (UX-02, UX-03)", () => {
  it("the normal state shows three headline numbers (building option as its scheduled area)", () => {
    const doc = loadResultsFixture(ALL_AVAILABLE);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    for (const key of ANSWER_KEYS) {
      expect(within(card(key)).getByTestId("answer-headline-number")).toBeInTheDocument();
    }
  });

  it("the partial state shows a withheld result as 'Not known' with the short gap tag and no number", () => {
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
    expect(row.textContent ?? "").not.toMatch(/\d+%/);
    // its gap kind reads the short tag now (ruling V11 (3)), never the old sentence.
    expect(within(row).getByTestId("answer-gap-kind").textContent).toBe("Needs property information");
    expect(row.textContent ?? "").not.toContain("Missing information about this property");
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
  it("envelope fixture (no building options): the allowance shows; envelope and option read reasons", () => {
    const doc = loadResultsFixture(ENVELOPE_MISSING);
    expect(hasFirstBuildingOptions(doc)).toBe(false);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    expect(within(card("floor_area_allowance")).getByTestId("answer-headline")).toBeInTheDocument();
    expect(within(card("permitted_envelope")).getByTestId("answer-not-available").textContent).toBe(
      "Not available — height rules for this district are not built yet.",
    );
    expect(within(card("building_option")).getByTestId("answer-not-available").textContent).toBe(
      "Not available — it needs the permitted envelope.",
    );
    const allowance = card("floor_area_allowance");
    expect(within(allowance).getByTestId("answer-supplement-not-available").textContent).toBe(
      "Not confirmed",
    );
  });

  it("all-available fixture (no building options): the option reaches the allowance in its details", () => {
    const doc = loadResultsFixture(ALL_AVAILABLE);
    expect(hasFirstBuildingOptions(doc)).toBe(false);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    expect(within(card("building_option")).getByTestId("answer-shortfall").textContent).toContain(
      "Reaches the full floor-area allowance.",
    );
    expect(screen.getByTestId("three-answers-draft-tag").textContent).toContain(
      "rules not professionally reviewed",
    );
  });
});

describe("S1: the rendered results never hold a word that overstates a result (ruling X5)", () => {
  // The seven words the owner forbids for a result, anywhere on the website (scenario S1, ruling
  // X5): 'achieved', 'no allowance left unused', 'optimal', 'compliant', 'feasible', 'preferred',
  // 'recommended'. The scan reads the whole panel's textContent (the ResultDetails keep their
  // children in the DOM, so folded detail is scanned too).
  const FORBIDDEN = [
    "achieved",
    "no allowance left unused",
    "optimal",
    "compliant",
    "feasible",
    "preferred",
    "recommended",
  ];
  // The live product path is the building-alternatives shape (the journey): the building-option
  // answer is the BuildingOptionCard and building B is a worked alternative. On that path the
  // presentation types no result wording of its own that overstates a result. (A legacy
  // single-answer fixture carries the engine's own "Achieved zoning floor area" label, which is
  // document/engine wording — services/** and packages/**, outside this task; the key
  // `achieved_zoning_floor_area` stays a key, and in this path no presentation text overstates.)
  it(`${BENCHMARK}: the panel text holds none of the forbidden words, and building B is honest`, () => {
    render(<ThreeAnswersPanel results={loadResultsFixture(BENCHMARK)} showDraftValues />);
    const text = (screen.getByTestId("three-answers-panel").textContent ?? "").toLowerCase();
    for (const word of FORBIDDEN) expect(text).not.toContain(word);
    // building B's scheduled line reads the honest one-line phrase.
    expect(text).toContain("scheduled floor area");
    expect(text).toContain("site fit unverified");
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
    expect(css).toMatch(/var\(--pt-color-/);
  });
});
