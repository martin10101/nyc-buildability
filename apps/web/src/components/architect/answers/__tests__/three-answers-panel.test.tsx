import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import {
  ANSWER_KEYS,
  ANSWER_TITLES,
  REACHES_ALLOWANCE_TEXT,
  RULES_NOT_REVIEWED_REASON,
  STRIP_MAX_ITEMS,
  displayQuantity,
  gapKindLine,
  notAvailableText,
  quantityText,
  type AnswerKey,
  type Results,
} from "@/lib/architect/three-answers";
import { loadResultsFixture, loadResultsFixtures } from "@/test-support/results-fixtures";
import { ThreeAnswersPanel } from "../ThreeAnswersPanel";

/**
 * Queue D-05 (plan §5 "Three separate answers" / "Calculation behavior", §5a "Label on the
 * box"). Renders EVERY committed valid results fixture
 * (packages/contracts/fixtures/valid/results/) and reads the expected values from the loaded
 * documents — no number is copied into the component or this suite.
 *
 * All committed fixtures are drafts (their rule versions are not published), so the numbers
 * are asserted with `showDraftValues` (a lane-flag surface) and the architect default is
 * asserted separately: every available answer then reads "Not available — …".
 */

afterEach(cleanup);

const FIXTURES = loadResultsFixtures();
const ALL_AVAILABLE = "synthetic_all_answers_available";
const ENVELOPE_MISSING = "synthetic_envelope_not_available_existing_building";

// Contract enum codes (results.schema.json) that must never reach the screen (plan §5a item 5).
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
// A compared number for probe shortfall reasons (never rendered by the panel).
const PROBE_VALUE = { name: "probe height", value: 1, unit: "feet" as const };

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

/** Headline and value rows of an available card, as {label, text}. */
function renderedValues(cardEl: HTMLElement): { label: string; text: string }[] {
  const headline = within(cardEl).getByTestId("answer-headline");
  const headlineLabel = headline.querySelector<HTMLElement>(".ta-headline-label");
  const rows = within(cardEl)
    .queryAllByTestId("answer-value")
    .map(row => ({
      label: row.querySelector<HTMLElement>("dt")?.textContent ?? "",
      text: row.querySelector<HTMLElement>("dd")?.textContent ?? "",
    }));
  return [{ label: headlineLabel?.textContent ?? "", text: headline.textContent ?? "" }, ...rows];
}

it("loads the committed valid results fixtures (never a vacuous run)", () => {
  const names = FIXTURES.map(fixture => fixture.name);
  expect(names.length).toBeGreaterThanOrEqual(4);
  expect(names).toContain(ALL_AVAILABLE);
  expect(names).toContain(ENVELOPE_MISSING);
});

for (const { name, doc } of FIXTURES) {
  describe(`results fixture ${name}`, () => {
    it("shows every available answer's numbers with units, exceptions and rule sections", () => {
      render(<ThreeAnswersPanel results={doc} showDraftValues />);
      for (const key of ANSWER_KEYS) {
        const answer = doc.answers[key];
        if (answer.status !== "available") continue;
        const cardEl = card(key);
        expect(within(cardEl).getAllByTestId("answer-headline-number")).toHaveLength(1);
        const rendered = renderedValues(cardEl);
        expect(rendered.map(entry => entry.label).sort()).toEqual(
          answer.values.map(value => value.label).sort(),
        );
        const sectionItems = within(cardEl)
          .getAllByTestId("answer-section")
          .map(item => item.textContent ?? "");
        for (const value of answer.values) {
          const entry = rendered.find(candidate => candidate.label === value.label);
          expect(entry, value.key).toBeDefined();
          const text = entry?.text ?? "";
          expect(text).toContain(quantityText(displayQuantity(value.value, value.unit)));
          // Independent of the panel's formatter: whole numbers read with en-US grouping.
          if (Number.isInteger(value.value)) {
            expect(text).toContain(value.value.toLocaleString("en-US"));
          }
          if (value.exception_label) expect(text).toContain(value.exception_label);
          const sections = sectionItems.find(item => item.startsWith(`${value.label}: `));
          expect(sections, value.key).toBeDefined();
          for (const section of value.zr_sections) expect(sections).toContain(section);
        }
        // Rule sections and the measurement label are behind a closed disclosure (§5a item 4).
        const details = within(cardEl).getByTestId("answer-details");
        expect(details.tagName).toBe("DETAILS");
        expect(details).not.toHaveAttribute("open");
        expect(details).toHaveTextContent(`Measurements: ${answer.measurement.label}`);
        // At most one exception beside each number (§5a item 3).
        const exceptionCount = answer.values.filter(value => value.exception_label).length;
        expect(within(cardEl).queryAllByTestId("answer-exception")).toHaveLength(exceptionCount);
      }
    });

    it("shows a not-available answer as 'Not available — <reason>', with only its kind-of-gap line", () => {
      render(<ThreeAnswersPanel results={doc} showDraftValues />);
      for (const key of ANSWER_KEYS) {
        const answer = doc.answers[key];
        if (answer.status !== "not_available") continue;
        const cardEl = card(key);
        const expected = notAvailableText(answer.reason, key);
        expect(expected.startsWith("Not available — ")).toBe(true);
        const line = within(cardEl).getByTestId("answer-not-available");
        expect(line.textContent).toBe(expected);
        // An answer that carries a gap_kind also shows the plain-words kind line (ruling R6); a
        // not-available answer with no gap_kind shows none.
        const gapLine = gapKindLine(answer.gap_kind);
        if (gapLine) {
          expect(within(cardEl).getByTestId("answer-gap-kind").textContent).toBe(gapLine);
        } else {
          expect(within(cardEl).queryByTestId("answer-gap-kind")).toBeNull();
        }
        // The card holds its title, that one line and (if any) its kind line: no number, no
        // caution tag, no details.
        expect(cardEl.textContent).toBe(`${ANSWER_TITLES[key]}${expected}${gapLine ?? ""}`);
        expect(without(cardEl.textContent ?? "", expected, gapLine ?? "")).not.toMatch(/\d/);
        expect(within(cardEl).queryByTestId("answer-headline")).toBeNull();
        expect(within(cardEl).queryAllByTestId("answer-value")).toHaveLength(0);
        expect(within(cardEl).queryAllByTestId("answer-exception")).toHaveLength(0);
        expect(within(cardEl).queryByTestId("answer-details")).toBeNull();
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
            ? notAvailableText(answer.reason, key)
            : doc.draft
              ? `Not available — ${RULES_NOT_REVIEWED_REASON}`
              : null;
        if (expected === null) continue;
        // Only a natively not-available answer carries its own gap_kind line; the draft gate adds none.
        const gapLine = answer.status === "not_available" ? gapKindLine(answer.gap_kind) : null;
        expect(within(cardEl).getByTestId("answer-not-available").textContent).toBe(expected);
        expect(cardEl.textContent).toBe(`${ANSWER_TITLES[key]}${expected}${gapLine ?? ""}`);
        expect(without(cardEl.textContent ?? "", expected, gapLine ?? "")).not.toMatch(/\d/);
      }
      if (doc.draft) {
        expect(screen.queryAllByTestId("answer-headline")).toHaveLength(0);
        expect(screen.queryAllByTestId("answer-exception")).toHaveLength(0);
        expect(screen.queryAllByTestId("answer-shortfall")).toHaveLength(0);
      }
    });

    it("keeps the status strip to at most three items, with the details behind a tap", () => {
      render(<ThreeAnswersPanel results={doc} showDraftValues />);
      const strip = screen.getByTestId("three-answers-status-strip");
      expect(strip.tagName).toBe("DETAILS");
      expect(strip).not.toHaveAttribute("open");
      const items = within(strip)
        .queryAllByTestId("three-answers-status-item")
        .map(item => item.textContent);
      expect(items.length).toBeLessThanOrEqual(STRIP_MAX_ITEMS);
      expect(items).toEqual(doc.status_strip.slice(0, STRIP_MAX_ITEMS).map(item => item.text));
      const details = within(strip).getByTestId("three-answers-status-details");
      expect(details).toHaveTextContent(doc.lot_selection_statement);
      if (doc.notices_count > 0) {
        expect(within(details).getByTestId("three-answers-notes").textContent).toBe(
          `Notes (${doc.notices_count})`,
        );
      }
      if (doc.out_of_date && doc.out_of_date_reason) {
        expect(within(details).getByTestId("three-answers-out-of-date").textContent).toBe(
          `Out of date — ${doc.out_of_date_reason}`,
        );
      }
      // One strip only.
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
        // A source ref may legitimately appear only in the "Rule sections" disclosure — the same
        // answer-section items the rule-sections test reads (line ~118); strip those once so the
        // checks below can require a ZR ref to live there and nowhere else.
        const outsideSections = without(
          text,
          ...screen.queryAllByTestId("answer-section").map(item => item.textContent ?? ""),
        );
        for (const key of ANSWER_KEYS) {
          const answer = doc.answers[key];
          if (answer.status !== "available") continue;
          for (const value of answer.values) {
            for (const source of value.sources) {
              // The contract (results.schema.json $defs.value_source) allows value_source.kind
              // `zoning_resolution`, whose ref IS a shown ZR section, so it is excluded from the
              // bare-ref ban: it must equal one of this value's zr_sections and appear only inside
              // the rule sections. Internal ids (site_fact, rule_table) stay forbidden everywhere.
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
    // Owner wording, settled 2026-10-01 (D-090-R038; replaces plan §3 step 4's): without a
    // verified value the row reads "Remaining development capacity" → "Not confirmed", then the
    // reason line, while the full-site allowance shows.
    const allowance = card("floor_area_allowance");
    const row = within(allowance).getByTestId("answer-supplement");
    expect(row.querySelector<HTMLElement>("dt")?.textContent).toBe("Remaining development capacity");
    expect(within(allowance).getByTestId("answer-supplement-not-available").textContent).toBe("Not confirmed");
    expect(within(allowance).getByTestId("answer-supplement-reason").textContent).toBe(
      "Needs verified zoning-lot boundaries and existing zoning floor area.",
    );
    expect(row.textContent).toBe(
      "Remaining development capacityNot confirmedNeeds verified zoning-lot boundaries and existing zoning floor area.",
    );
    // No shortfall is drawn for an option that is not shown.
    expect(screen.queryByTestId("answer-shortfall")).toBeNull();
  });

  it("all-available fixture: no remaining row without a kept building; the option reaches the allowance", () => {
    const doc = loadResultsFixture(ALL_AVAILABLE);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    expect(screen.queryByTestId("answer-supplement")).toBeNull();
    expect(within(card("building_option")).getByTestId("answer-shortfall").textContent).toBe(
      REACHES_ALLOWANCE_TEXT,
    );
    expect(screen.getByTestId("three-answers-draft-tag")).toBeInTheDocument();
  });

  it("a shortfall shows the gap and each computed reason (plan §5 answer 3)", () => {
    const doc: Results = {
      ...loadResultsFixture(ALL_AVAILABLE),
      shortfall: {
        status: "shortfall",
        sq_ft: 1250,
        reasons: [
          { text: "Probe reason one.", computed_from: ["probe-constraint"], values: [PROBE_VALUE] },
          { text: "Probe reason two.", computed_from: ["probe-constraint"], values: [PROBE_VALUE] },
        ],
      },
    };
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const option = card("building_option");
    expect(within(option).getByTestId("answer-shortfall-amount").textContent).toBe("1,250 sq ft");
    expect(
      within(option)
        .getAllByTestId("answer-shortfall-reason")
        .map(item => item.textContent),
    ).toEqual(["Probe reason one.", "Probe reason two."]);
  });

  it("a shortfall that is not available reads 'Not available — …' beside the option", () => {
    const doc: Results = {
      ...loadResultsFixture(ALL_AVAILABLE),
      shortfall: {
        status: "not_available",
        reason: "the envelope check is not built yet",
        reason_kind: "rule_not_implemented",
      },
    };
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const line = within(card("building_option")).getByTestId("answer-supplement-not-available");
    expect(line.textContent).toBe("Not available — the envelope check is not built yet");
    expect(within(card("building_option")).queryByTestId("answer-supplement-reason")).toBeNull();
  });

  it("a remaining floor area that is available shows beside the allowance", () => {
    const doc: Results = {
      ...loadResultsFixture(ENVELOPE_MISSING),
      remaining_floor_area: {
        status: "available",
        value_sf: 1500,
        existing_zoning_floor_area_fact_id: "probe-fact-existing-zoning-floor-area",
      },
    };
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const row = within(card("floor_area_allowance")).getByTestId("answer-supplement");
    expect(row).toHaveTextContent("Remaining after the existing building");
    expect(row).toHaveTextContent("1,500 sq ft");
    expect(within(row).queryByTestId("answer-supplement-reason")).toBeNull();
  });

  it("strip items beyond three move behind the strip (plan §5a items 1 and 6)", () => {
    // The contract caps the strip at three; this probe proves the panel keeps the cap even if a
    // producer ever breaks it.
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
    // Synthetic probe: `draft: false` is valid only when every rule version is published; the
    // committed fixtures are all drafts, so the flag is flipped here to prove the gate reads it.
    const doc: Results = { ...loadResultsFixture(ALL_AVAILABLE), draft: false };
    render(<ThreeAnswersPanel results={doc} />);
    for (const key of ANSWER_KEYS) {
      expect(within(card(key)).getByTestId("answer-headline")).toBeInTheDocument();
    }
    expect(screen.queryByTestId("three-answers-draft-tag")).toBeNull();
  });
});

describe("the three-way value-states layer (results contract 1.3.0; S14, R556, R570)", () => {
  function threeWayProbe(): Results {
    // A 1.3.0 probe from the all-available fixture: the floor-area headline is conditional and a
    // withheld value (a legal unit limit, not shown in values[]) carries only its reason.
    const base = loadResultsFixture(ALL_AVAILABLE);
    const answer = base.answers.floor_area_allowance;
    if (answer.status !== "available") throw new Error("fixture changed: allowance not available");
    return {
      ...base,
      contract_version: "1.3.0",
      answers: {
        ...base.answers,
        floor_area_allowance: {
          ...answer,
          value_states: {
            max_residential_floor_area: {
              way: "conditional",
              conditions: [
                {
                  kind: "unchecked_condition",
                  assumption: "If the recorded lot area is confirmed",
                  settled_by: "A survey or deed dimensions",
                },
              ],
            },
            legal_unit_limit_standard: {
              way: "withheld",
              label: "Legal dwelling-unit limit, standard residences",
              reason: "There is no evidence of a special density area, so it is not known.",
              gap_kind: "work_owed",
              resolved_by: "Sourced evidence of the special density area",
            },
          },
        },
      },
    };
  }

  it("shows a conditional value's 'If <assumption>' and a withheld value's reason, no number", () => {
    const doc = threeWayProbe();
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const allowance = card("floor_area_allowance");
    // the conditional headline shows its assumption line
    const condition = within(allowance).getByTestId("answer-condition");
    expect(condition.textContent).toBe("If the recorded lot area is confirmed");
    // the withheld value shows its reason with "Not known" and no number of its own
    const withheld = within(allowance).getByTestId("answer-withheld-value");
    expect(withheld.textContent).toContain("Legal dwelling-unit limit, standard residences");
    expect(withheld.textContent).toContain("Not known");
    expect(withheld.textContent).toContain(
      "There is no evidence of a special density area, so it is not known.",
    );
    // the withheld value never shows a number, and its reason carries no internal snake_case code
    const reason = within(withheld).getByTestId("answer-withheld-reason");
    expect(reason.textContent ?? "").not.toMatch(SNAKE_CASE);
  });

  it("S5: a withheld value shows its kind-of-gap line beside its reason (journey fixture, R6)", () => {
    const doc = loadResultsFixture("recorded_215_16_northern_journey");
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const envelope = card("permitted_envelope");
    const gapLines = within(envelope)
      .getAllByTestId("answer-gap-kind")
      .map(element => element.textContent);
    // Coverage, rear yard and the setback are withheld as work still owed on this lot.
    expect(gapLines.length).toBeGreaterThanOrEqual(3);
    for (const line of gapLines) {
      expect(line).toBe("Not built yet: this part of the program is still owed.");
    }
    // The building option is a whole not-available answer carrying the same kind line.
    const option = card("building_option");
    expect(within(option).getByTestId("answer-gap-kind").textContent).toBe(
      "Not built yet: this part of the program is still owed.",
    );
  });

  it("a withheld HEADLINE key shows its reason, never the first value (R556)", () => {
    const base = loadResultsFixture(ALL_AVAILABLE);
    const envelope = base.answers.permitted_envelope;
    if (envelope.status !== "available") throw new Error("fixture changed: envelope not available");
    const without = envelope.values.filter(value => value.key !== "max_building_height");
    const probe: Results = {
      ...base,
      contract_version: "1.3.0",
      answers: {
        ...base.answers,
        permitted_envelope: {
          ...envelope,
          values: without,
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
    const card_ = card("permitted_envelope");
    // the headline is the withheld reason, not a number from a different value
    expect(within(card_).queryByTestId("answer-headline")).toBeNull();
    const headlineWithheld = within(card_).getByTestId("answer-headline-withheld");
    expect(headlineWithheld.textContent).toContain("Maximum building height");
    expect(headlineWithheld.textContent).toContain("Not known");
  });
});
