import { describe, expect, it } from "vitest";
import { isOptionStale, selectedOption, type StudyEntry } from "../study-entry";
import {
  addOption,
  createStudyEntry,
  duplicateOption,
  markOptionResultsCurrent,
  nextOptionId,
  removeSiteFact,
  renameOption,
  selectOption,
  updateOptionInputs,
  upsertSiteFact,
} from "../study-operations";
import { LOT_SELECTION_STATEMENT } from "../study-vocabulary";
import {
  T1,
  T2,
  enteredStreetWidth,
  expectOk,
  newStudyInput,
  newStudyResult,
  optionInputs,
  twoOptionResult,
} from "./study-test-data";

/** The two-option study (opt-a, opt-b; revision 1) with both options' results current. */
function currentTwoOptions(): StudyEntry {
  let entry = expectOk(twoOptionResult());
  entry = expectOk(markOptionResultsCurrent(entry, "opt-a", entry.study.revision.number));
  return expectOk(markOptionResultsCurrent(entry, "opt-b", entry.study.revision.number));
}

describe("creating a study", () => {
  it("starts at revision 1 with the exact lot-selection statement, one selected option out of date", () => {
    const entry = expectOk(newStudyResult());
    expect(entry.study.revision).toEqual({ number: 1, created_at: "2026-09-30T12:00:00Z", parent: null });
    expect(entry.study.lot_selection.statement).toBe(LOT_SELECTION_STATEMENT);
    expect(entry.study.origin).toEqual({ kind: "new", export_id: null });
    expect(selectedOption(entry)?.name).toBe("Option A");
    expect(entry.staleOptionIds).toEqual(["option-a"]);
    expect(entry.parcelChoices).toBeNull();
  });

  it("creates several options at once; every option starts out of date (no results yet)", () => {
    const entry = expectOk(twoOptionResult());
    expect(entry.study.options.map((option) => option.option_id)).toEqual(["opt-a", "opt-b"]);
    expect(entry.study.selected_option_id).toBe("opt-a");
    expect(entry.staleOptionIds).toEqual(["opt-a", "opt-b"]);
    expect(entry.study.revision.number).toBe(1);
  });

  it("refuses a study the contract rejects", () => {
    const input = newStudyInput();
    const bad = { ...input, initialOption: { ...input.initialOption, inputs: { ...optionInputs(), program: [] } } };
    expect(createStudyEntry(bad)).toMatchObject({ ok: false, code: "invalid_document" });
  });
});

describe("options are independent (plan section 9)", () => {
  it("editing option A leaves option B byte-identical and B's results current", () => {
    const entry = currentTwoOptions();
    const optionB = entry.study.options[1];
    const optionBBytes = JSON.stringify(optionB);
    const next = expectOk(
      updateOptionInputs(entry, "opt-a", { program: ["market_rate_residential", "community_facility"] }, T1),
    );
    expect(next.study.options[0].program).toEqual(["market_rate_residential", "community_facility"]);
    expect(next.study.options[1]).toBe(optionB);
    expect(JSON.stringify(next.study.options[1])).toBe(optionBBytes);
    expect(next.study.site).toBe(entry.study.site);
    expect(isOptionStale(next, "opt-a")).toBe(true);
    expect(isOptionStale(next, "opt-b")).toBe(false);
    expect(next.study.revision).toEqual({ number: 2, created_at: T1, parent: 1 });
    // The previous entry is untouched.
    expect(entry.study.options[0].program).toEqual(["market_rate_residential"]);
  });

  it("changes only the named input of the option", () => {
    const entry = currentTwoOptions();
    const before = entry.study.options[0];
    const next = expectOk(updateOptionInputs(entry, "opt-a", { existing_building_plan: "keep" }, T1));
    const after = next.study.options[0];
    expect(after.existing_building_plan).toBe("keep");
    expect({ ...after, existing_building_plan: before.existing_building_plan }).toEqual(before);
  });

  it("refuses an option edit the contract rejects and changes nothing", () => {
    const entry = currentTwoOptions();
    const result = updateOptionInputs(entry, "opt-a", { goal: { kind: "other", text: null } }, T1);
    expect(result).toMatchObject({ ok: false, code: "invalid_document" });
    expect(entry.study.options[0].goal).toEqual({ kind: "most_residential_floor_area", text: null });
  });

  it("returns the same entry when an edit changes nothing (no new revision)", () => {
    const entry = currentTwoOptions();
    const same = expectOk(
      updateOptionInputs(entry, "opt-b", { program: ["market_rate_residential", "affordable_residential"] }, T1),
    );
    expect(same).toBe(entry);
  });

  it("adds an option with the next free id; existing options and their flags are unchanged", () => {
    const entry = currentTwoOptions();
    expect(nextOptionId(entry.study)).toBe("option-3");
    const next = expectOk(addOption(entry, { name: "Option C", inputs: optionInputs() }, T1));
    expect(next.study.options.map((option) => option.option_id)).toEqual(["opt-a", "opt-b", "option-3"]);
    expect(next.study.options[0]).toBe(entry.study.options[0]);
    expect(next.study.options[1]).toBe(entry.study.options[1]);
    expect(next.staleOptionIds).toEqual(["option-3"]);
    expect(addOption(next, { optionId: "opt-a", name: "Again", inputs: optionInputs() }, T2)).toMatchObject({
      ok: false,
      code: "duplicate_option_id",
    });
  });

  it("duplicates an option's inputs under a new id; the source option is untouched", () => {
    const entry = currentTwoOptions();
    const next = expectOk(duplicateOption(entry, "opt-b", { optionId: "opt-b2", name: "Option B copy" }, T1));
    const [source, copy] = [next.study.options[1], next.study.options[2]];
    expect(source).toBe(entry.study.options[1]);
    expect(copy.name).toBe("Option B copy");
    expect({ ...copy, option_id: source.option_id, name: source.name }).toEqual(source);
    expect(next.staleOptionIds).toEqual(["opt-b2"]);
    expect(duplicateOption(entry, "missing", { name: "X" }, T1)).toMatchObject({ ok: false, code: "unknown_option" });
  });

  it("renames an option without marking any result out of date", () => {
    const entry = currentTwoOptions();
    const next = expectOk(renameOption(entry, "opt-b", "Option B (affordable)", T1));
    expect(next.study.options[1].name).toBe("Option B (affordable)");
    expect(next.study.options[0]).toBe(entry.study.options[0]);
    expect(next.staleOptionIds).toEqual([]);
    expect(next.study.revision.number).toBe(2);
    expect(renameOption(entry, "opt-b", "", T1)).toMatchObject({ ok: false, code: "invalid_document" });
  });

  it("selects the option that drives the report; selecting it again changes nothing", () => {
    const entry = currentTwoOptions();
    const next = expectOk(selectOption(entry, "opt-b", T1));
    expect(next.study.selected_option_id).toBe("opt-b");
    expect(next.study.options).toBe(entry.study.options);
    expect(next.staleOptionIds).toEqual([]);
    expect(expectOk(selectOption(next, "opt-b", T2))).toBe(next);
    expect(selectOption(entry, "missing", T1)).toMatchObject({ ok: false, code: "unknown_option" });
  });
});

describe("the site is shared by every option (plan section 9)", () => {
  it("a site edit marks every option's results out of date and leaves the options unchanged", () => {
    const entry = currentTwoOptions();
    const next = expectOk(upsertSiteFact(entry, enteredStreetWidth("fact-street-width-a", "Synthetic Street A", 75), T1));
    expect(next.study.site.facts.find((fact) => fact.fact_id === "fact-street-width-a")?.value).toBe(75);
    expect(next.study.options).toBe(entry.study.options);
    expect(next.staleOptionIds).toEqual(["opt-a", "opt-b"]);
    expect(next.study.revision).toEqual({ number: 2, created_at: T1, parent: 1 });
  });

  it("adding and removing a site fact both mark every option out of date", () => {
    const entry = currentTwoOptions();
    const added = expectOk(upsertSiteFact(entry, enteredStreetWidth("fact-street-width-c", "Synthetic Street C", 80), T1));
    expect(added.study.site.facts).toHaveLength(entry.study.site.facts.length + 1);
    expect(added.staleOptionIds).toEqual(["opt-a", "opt-b"]);
    const fresh = expectOk(markOptionResultsCurrent(
      expectOk(markOptionResultsCurrent(added, "opt-a", 2)), "opt-b", 2,
    ));
    const removed = expectOk(removeSiteFact(fresh, "fact-street-width-c", T2));
    expect(removed.study.site.facts).toEqual(entry.study.site.facts);
    expect(removed.staleOptionIds).toEqual(["opt-a", "opt-b"]);
    expect(removeSiteFact(fresh, "missing", T2)).toMatchObject({ ok: false, code: "unknown_fact" });
  });

  it("never overwrites a city value in place with an entered one", () => {
    const entry = currentTwoOptions();
    const edit = {
      ...enteredStreetWidth("fact-lot-area", "unused", 1),
      key: "lot_area" as const,
      street: null,
      unit: "square_feet" as const,
      value: 5200,
    };
    expect(upsertSiteFact(entry, edit, T1)).toMatchObject({ ok: false, code: "city_fact_overwrite" });
    expect(entry.staleOptionIds).toEqual([]);
  });
});

describe("non-finite numbers are refused, never rewritten to null (review correction 2)", () => {
  it("refuses an assumption value of NaN instead of saving it as null", () => {
    const entry = currentTwoOptions();
    const result = updateOptionInputs(
      entry,
      "opt-a",
      { assumptions: [{ assumption_id: "a1", statement: "s", value: Number.NaN, unit: null }] },
      T1,
    );
    expect(result).toMatchObject({ ok: false, code: "invalid_document" });
    expect(entry.study.options[0].assumptions).toEqual([]);
  });

  it("does not mistake a NaN for the null already stored (no silent no-op)", () => {
    const entry = currentTwoOptions();
    const withNaN = entry.study.options[1].assumptions.map((item) => ({ ...item, value: Number.NaN }));
    expect(entry.study.options[1].assumptions[0].value).toBeNull();
    expect(updateOptionInputs(entry, "opt-b", { assumptions: withNaN }, T1)).toMatchObject({
      ok: false,
      code: "invalid_document",
    });
  });

  it("refuses an unknown site value carrying NaN (it would otherwise pass as null)", () => {
    const entry = currentTwoOptions();
    const result = upsertSiteFact(
      entry,
      {
        ...enteredStreetWidth("fact-street-width-c", "Synthetic Street C", 1),
        value: Number.NaN,
        unit: null,
        measurement: { rank: "unknown", label: "Unknown — enter" },
        source: null,
        blocks: ["permitted_envelope"],
      },
      T1,
    );
    expect(result).toMatchObject({ ok: false, code: "invalid_document" });
  });

  it("refuses Infinity when a study is created", () => {
    const input = newStudyInput();
    const inputs = optionInputs();
    inputs.floor_to_floor_heights.typical_floor.height_ft = Number.POSITIVE_INFINITY;
    expect(createStudyEntry({ ...input, initialOption: { ...input.initialOption, inputs } })).toMatchObject({
      ok: false,
      code: "invalid_document",
      problems: [expect.stringContaining("not finite")],
    });
  });
});

describe("out-of-date flags", () => {
  it("results computed for an earlier revision never clear a newer flag (late responses)", () => {
    const entry = currentTwoOptions();
    const edited = expectOk(updateOptionInputs(entry, "opt-a", { existing_building_plan: "remove" }, T1));
    expect(markOptionResultsCurrent(edited, "opt-a", 1)).toMatchObject({ ok: false, code: "stale_revision" });
    const current = expectOk(markOptionResultsCurrent(edited, "opt-a", 2));
    expect(isOptionStale(current, "opt-a")).toBe(false);
    expect(current.study).toBe(edited.study);
  });
});

describe("immutability", () => {
  it("freezes entries so no surface can edit the shared study in place", () => {
    const entry = currentTwoOptions();
    expect(Object.isFrozen(entry.study.options[0].floor_to_floor_heights.ground_floor)).toBe(true);
    expect(() => {
      entry.study.options[0].name = "Edited in place";
    }).toThrow(TypeError);
  });

  it("keeps no reference to the caller's input objects", () => {
    const inputs = optionInputs();
    const entry = expectOk(addOption(currentTwoOptions(), { optionId: "opt-c", name: "Option C", inputs }, T1));
    inputs.program.push("commercial");
    expect(entry.study.options[2].program).toEqual(["market_rate_residential"]);
  });
});
