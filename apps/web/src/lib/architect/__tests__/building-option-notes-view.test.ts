import { describe, expect, it } from "vitest";
import {
  BUILDING_OPTION_NOTE_HEADING,
  buildingOptionNoteKindLabel,
  buildingOptionNotesView,
  type Results,
} from "@/lib/architect/three-answers";
import { loadResultsFixture } from "@/test-support/results-fixtures";

/**
 * buildingOptionNotesView (results contract 1.2.0, D-090-R132): the pure read that shapes the
 * building option's draft notes for the card. Reads only the loaded document — no number or string
 * is copied into this suite — and fails safe (a note that is not a draft, a building option that is
 * not available, or one with no notes, all yield an empty list).
 */

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

describe("buildingOptionNotesView — a draft reading read from the document (D-090-R132)", () => {
  it("reads the note's text, kind, ZR sections and snapshots straight from the document", () => {
    const { doc, note } = northernNote();
    const views = buildingOptionNotesView(doc);
    expect(views).toHaveLength(1);
    expect(views[0]).toEqual({
      draftLabel: BUILDING_OPTION_NOTE_HEADING,
      kindLabel: "Minimum base height",
      text: note.text,
      zrSections: note.zr_sections,
      snapshotIds: note.snapshot_ids,
    });
    // The heading is a fixed label marking the reading pending review, not a compliance statement.
    expect(BUILDING_OPTION_NOTE_HEADING).toBe("Draft reading — pending qualified review");
  });

  it("returns an empty list when the building option carries no notes", () => {
    const doc = loadResultsFixture("synthetic_all_answers_available");
    expect(buildingOptionNotesView(doc)).toEqual([]);
  });

  it("returns an empty list when notes is null", () => {
    const { doc, option } = northernNote();
    const probe: Results = {
      ...doc,
      answers: { ...doc.answers, building_option: { ...option, notes: null } },
    };
    expect(buildingOptionNotesView(probe)).toEqual([]);
  });

  it("drops a note whose draft flag is not true (fail closed — never a finding)", () => {
    const { doc, option, note } = northernNote();
    const notDraft = { ...note, draft: false } as unknown as typeof note;
    const probe: Results = {
      ...doc,
      answers: { ...doc.answers, building_option: { ...option, notes: [notDraft] } },
    };
    expect(buildingOptionNotesView(probe)).toEqual([]);
  });

  it("returns an empty list when the building option is not available", () => {
    const doc = loadResultsFixture("synthetic_envelope_not_available_existing_building");
    expect(doc.answers.building_option.status).toBe("not_available");
    expect(buildingOptionNotesView(doc)).toEqual([]);
  });

  it("names a kind in plain words and de-underscores an unmapped kind, never a raw code", () => {
    expect(buildingOptionNoteKindLabel("minimum_base_height")).toBe("Minimum base height");
    expect(buildingOptionNoteKindLabel("some_future_kind")).toBe("Some future kind");
  });
});
