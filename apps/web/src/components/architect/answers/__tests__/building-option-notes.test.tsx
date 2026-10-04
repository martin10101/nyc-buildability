import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import {
  BUILDING_OPTION_NOTE_HEADING,
  buildingOptionNotesView,
  type Results,
} from "@/lib/architect/three-answers";
import { loadResultsFixture } from "@/test-support/results-fixtures";
import { ThreeAnswersPanel } from "../ThreeAnswersPanel";

/**
 * The building-option draft note on the card beside the heights (results contract 1.2.0,
 * D-090-R132: "carry the computed note into the actual results and the screen wherever the sample
 * building appears"). The note shows ONLY while the building-option heights show (the same draft
 * gate) and ONLY as a draft reading pending qualified review — never a compliance statement. Every
 * string is read from the loaded fixture; nothing is retyped here.
 */

afterEach(cleanup);

const NOTE_FIXTURE = "synthetic_building_option_min_base_height_note_northern";

/** The Northern note fixture and its single committed note, so a change fails loudly. */
function northernNote() {
  const doc = loadResultsFixture(NOTE_FIXTURE);
  const option = doc.answers.building_option;
  if (option.status !== "available" || !option.notes || option.notes.length === 0) {
    throw new Error(`fixture changed: ${NOTE_FIXTURE} must carry a building-option note`);
  }
  return { doc, option, note: option.notes[0] };
}

function optionCard(): HTMLElement {
  return screen.getByTestId("answer-building_option");
}

describe("building-option draft note on the card (D-090-R132)", () => {
  it("shows the note verbatim under the building-option heights, marked pending review", () => {
    const { doc, note } = northernNote();
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    // The heights the note interprets are shown on this lane-flag surface.
    expect(within(optionCard()).getByTestId("answer-headline")).toBeInTheDocument();
    const block = within(optionCard()).getByTestId("building-option-note");
    // Heading marks it a draft reading pending qualified review (a fixed label, not a finding).
    expect(within(block).getByTestId("building-option-note-heading").textContent).toBe(
      BUILDING_OPTION_NOTE_HEADING,
    );
    expect(BUILDING_OPTION_NOTE_HEADING).toBe("Draft reading — pending qualified review");
    // The note text, byte-exact from the document.
    expect(block.textContent).toContain(note.text);
    // The kind in plain words, never the enum code.
    expect(block.textContent).toContain("Minimum base height");
    expect(block.textContent).not.toContain(note.kind);
    // The ZR sections in plain words.
    expect(block.textContent).toContain(`Based on ${note.zr_sections.join(", ")} as captured`);
    // The snapshot ids behind a disclosure, not bare in the prose.
    const snapshots = within(block).getByTestId("building-option-note-snapshots");
    for (const id of note.snapshot_ids) expect(snapshots.textContent).toContain(id);
  });

  it("pins the draft flag and register the document carries (never shown as a finding)", () => {
    const { note } = northernNote();
    expect(note.draft).toBe(true);
    expect(note.register).toBe("draft reading of the captured text");
  });

  it("hides the note on the default architect surface, where the heights are withheld", () => {
    const { doc } = northernNote();
    render(<ThreeAnswersPanel results={doc} />);
    // The draft gate hides the building-option numbers here; the note goes with them.
    expect(within(optionCard()).queryByTestId("answer-headline")).toBeNull();
    expect(screen.queryByTestId("building-option-note")).toBeNull();
  });

  it("renders no note block when the building option carries notes null", () => {
    const { doc, option } = northernNote();
    const probe: Results = {
      ...doc,
      answers: { ...doc.answers, building_option: { ...option, notes: null } },
    };
    expect(buildingOptionNotesView(probe)).toEqual([]);
    render(<ThreeAnswersPanel results={probe} showDraftValues />);
    // The heights still show; just no note block.
    expect(within(optionCard()).getByTestId("answer-headline")).toBeInTheDocument();
    expect(screen.queryByTestId("building-option-note")).toBeNull();
  });

  it("drops a note whose draft flag is not true — never shows a reading as a finding", () => {
    const { doc, option, note } = northernNote();
    const notDraft = { ...note, draft: false } as unknown as typeof note;
    const probe: Results = {
      ...doc,
      answers: { ...doc.answers, building_option: { ...option, notes: [notDraft] } },
    };
    render(<ThreeAnswersPanel results={probe} showDraftValues />);
    expect(screen.queryByTestId("building-option-note")).toBeNull();
    // Its text never reaches the screen.
    expect(screen.getByTestId("three-answers-panel").textContent).not.toContain(note.text);
  });

  it("introduces no snake_case or raw code, and leaks no ZR source ref into the prose", () => {
    const { doc } = northernNote();
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const panel = screen.getByTestId("three-answers-panel");
    const text = panel.textContent ?? "";
    // No machine snake_case word and no enum code reaches the screen (plan §5a item 5).
    expect(text).not.toMatch(/\b[a-z0-9]+(?:_[a-z0-9]+)+\b/);
    for (const code of ["minimum_base_height", "zoning_resolution", "rule_table", "site_fact"]) {
      expect(text).not.toContain(code);
    }
    // "ZR 23-432" is also a building-option value's zoning_resolution source: the note's citations
    // live only inside the answer-section surface the panel guard strips, so none leaks into the
    // plain prose. Mirror the guard: strip every answer-section text once, then the ref is gone.
    const sectionTexts = within(panel)
      .queryAllByTestId<HTMLElement>("answer-section")
      .map(element => element.textContent ?? "");
    const outsideSections = sectionTexts.reduce((rest, part) => rest.split(part).join(""), text);
    expect(text).toContain("ZR 23-432");
    expect(outsideSections).not.toContain("ZR 23-432");
  });
});
