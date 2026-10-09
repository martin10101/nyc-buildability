import { describe, expect, it } from "vitest";
import { isOptionStale, selectedOption, type StudyEntry } from "../study-entry";
import {
  addOption,
  createStudyEntry,
  duplicateOption,
  enterSiteFactAssumption,
  enterSiteFactValue,
  markOptionResultsCurrent,
  nextOptionId,
  removeSiteFact,
  renameOption,
  selectOption,
  setLotSelection,
  updateOptionInputs,
  upsertSiteFact,
} from "../study-operations";
import { validateStudyDocument } from "../study-validator";
import { LOT_SELECTION_STATEMENT, MEASUREMENT_LABELS, type Lot, type SiteFact } from "../study-vocabulary";
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

describe("re-picking lots (setLotSelection, request D-1 slice 2)", () => {
  /** Two lots as the SERVER (B-07) would return them; the web never builds this. */
  function serverTwoLots(): Lot[] {
    return [
      {
        bbl: "5999999999",
        approximate_lot_area_sq_ft: 5000,
        size_measurement: { rank: "approximate_tax_map", label: MEASUREMENT_LABELS.approximate_tax_map },
        selected: true,
      },
      {
        bbl: "5999999998",
        approximate_lot_area_sq_ft: 4000,
        size_measurement: { rank: "approximate_tax_map", label: MEASUREMENT_LABELS.approximate_tax_map },
        selected: true,
      },
    ];
  }

  it("replaces lots and combination from the server, keeps the pinned statement, marks every option out of date", () => {
    const entry = currentTwoOptions();
    expect(entry.study.lots).toHaveLength(1);
    const next = expectOk(
      setLotSelection(entry, serverTwoLots(), { mode: "all", combination: { status: "offered", reason: null } }, T1),
    );
    // The lots and the combination are the server's, verbatim.
    expect(next.study.lots.map((lot) => lot.bbl)).toEqual(["5999999999", "5999999998"]);
    expect(next.study.lot_selection.combination).toEqual({ status: "offered", reason: null });
    // The pinned statement is re-applied by the store, never computed or taken from the input.
    expect(next.study.lot_selection.statement).toBe(LOT_SELECTION_STATEMENT);
    // The site changed, so every option is out of date; the option objects are untouched.
    expect(next.staleOptionIds).toEqual(["opt-a", "opt-b"]);
    expect(next.study.options).toBe(entry.study.options);
    expect(next.study.revision).toEqual({ number: 2, created_at: T1, parent: 1 });
    // The previous entry is untouched.
    expect(entry.study.lots).toHaveLength(1);
  });

  it("re-picking to the same lots and selection changes nothing (no new revision)", () => {
    const entry = currentTwoOptions();
    const sameLots = JSON.parse(JSON.stringify(entry.study.lots)) as Lot[];
    const sameCombination = JSON.parse(JSON.stringify(entry.study.lot_selection.combination));
    const same = expectOk(
      setLotSelection(entry, sameLots, { mode: entry.study.lot_selection.mode, combination: sameCombination }, T1),
    );
    expect(same).toBe(entry);
  });

  it("refuses an invalid lot (a 0 area with a known rank) and changes nothing", () => {
    const entry = currentTwoOptions();
    const badLots: Lot[] = [
      {
        bbl: "5999999999",
        approximate_lot_area_sq_ft: 0,
        size_measurement: { rank: "approximate_tax_map", label: MEASUREMENT_LABELS.approximate_tax_map },
        selected: true,
      },
    ];
    const result = setLotSelection(entry, badLots, { mode: "all", combination: { status: "single_lot", reason: null } }, T1);
    expect(result).toMatchObject({ ok: false, code: "invalid_document" });
    expect(entry.study.lots).toHaveLength(1);
    expect(entry.study.lots[0].approximate_lot_area_sq_ft).toBe(5000);
  });
});

describe("per-fact edit (enterSiteFactValue, request D-1 slice 2)", () => {
  it("edits a city fact into a NEW entered fact and leaves the city fact intact", () => {
    const entry = currentTwoOptions();
    const cityArea = entry.study.site.facts.find((fact) => fact.fact_id === "fact-lot-area");
    expect(cityArea?.source?.kind).toBe("tax_map_computation");
    const next = expectOk(enterSiteFactValue(entry, { factId: "fact-lot-area", value: 6200 }, T1));
    // The city value is never overwritten in place: the original fact is still present, unchanged.
    expect(next.study.site.facts.find((fact) => fact.fact_id === "fact-lot-area")).toEqual(cityArea);
    // The edit is a new fact at rank "entered", sourced to the architect, following the contract.
    const entered = next.study.site.facts.find((fact) => fact.fact_id === "fact-lot-area-entered");
    expect(entered?.value).toBe(6200);
    expect(entered?.unit).toBe("square_feet");
    expect(entered?.key).toBe("lot_area");
    expect(entered?.measurement).toEqual({ rank: "entered", label: MEASUREMENT_LABELS.entered });
    expect(entered?.source?.kind).toBe("architect_entry");
    expect(entered?.source?.retrieved_at).toBe(T1);
    expect(entered?.blocks).toEqual([]);
    // The site is shared, so every option's results are out of date.
    expect(next.staleOptionIds).toEqual(["opt-a", "opt-b"]);
    expect(next.study.revision).toEqual({ number: 2, created_at: T1, parent: 1 });
  });

  it("edits a text-valued city fact (lot type) into an entered fact with a null unit", () => {
    const entry = currentTwoOptions();
    const next = expectOk(enterSiteFactValue(entry, { factId: "fact-lot-type", value: "interior" }, T1));
    const entered = next.study.site.facts.find((fact) => fact.fact_id === "fact-lot-type-entered");
    expect(entered?.value).toBe("interior");
    expect(entered?.unit).toBeNull();
    expect(entered?.measurement.rank).toBe("entered");
    expect(entered?.source?.kind).toBe("architect_entry");
  });

  it("edits a non-city fact in place under its own id", () => {
    const entry = currentTwoOptions();
    const before = entry.study.site.facts.find((fact) => fact.fact_id === "fact-street-width-a");
    expect(before?.source?.kind).toBe("architect_entry");
    expect(before?.value).toBe(60);
    const next = expectOk(enterSiteFactValue(entry, { factId: "fact-street-width-a", value: 75 }, T2));
    // No new fact: the non-city value is replaced in place.
    expect(next.study.site.facts).toHaveLength(entry.study.site.facts.length);
    const edited = next.study.site.facts.find((fact) => fact.fact_id === "fact-street-width-a");
    expect(edited?.value).toBe(75);
    expect(edited?.street).toBe("Synthetic Street A");
    expect(edited?.unit).toBe("feet");
    expect(edited?.measurement).toEqual({ rank: "entered", label: MEASUREMENT_LABELS.entered });
    expect(next.staleOptionIds).toEqual(["opt-a", "opt-b"]);
  });

  it("uses a caller-supplied id for the new entered fact", () => {
    const entry = currentTwoOptions();
    const next = expectOk(
      enterSiteFactValue(entry, { factId: "fact-lot-area", value: 6000, enteredFactId: "fact-lot-area-mine" }, T1),
    );
    expect(next.study.site.facts.some((fact) => fact.fact_id === "fact-lot-area-mine")).toBe(true);
  });

  it("refuses an invalid value (a 0 lot area) and changes nothing", () => {
    const entry = currentTwoOptions();
    const result = enterSiteFactValue(entry, { factId: "fact-lot-area", value: 0 }, T1);
    expect(result).toMatchObject({ ok: false, code: "invalid_document" });
    expect(entry.study.site.facts.some((fact) => fact.fact_id === "fact-lot-area-entered")).toBe(false);
    expect(entry.staleOptionIds).toEqual([]);
  });

  it("refuses an edit to a fact that is not in the study", () => {
    const entry = currentTwoOptions();
    expect(enterSiteFactValue(entry, { factId: "fact-missing", value: 10 }, T1)).toMatchObject({
      ok: false,
      code: "unknown_fact",
    });
  });
});

describe("per-fact stated assumption (enterSiteFactAssumption, request D-3)", () => {
  /** An unknown existing-zoning-floor-area fact as the server would supply it (no DOB figure). */
  function unknownExistingZfaFact(): SiteFact {
    return {
      contract_version: "1.0.0",
      fact_id: "fact-existing-zfa",
      key: "existing_zoning_floor_area",
      lot_bbl: "5999999999",
      street: null,
      value: null,
      unit: null,
      measurement: { rank: "unknown", label: MEASUREMENT_LABELS.unknown },
      source: null,
      blocks: ["remaining_floor_area"],
      editable: true,
    };
  }

  it("records an assumption on a city fact as a NEW assumed fact and leaves the city fact intact", () => {
    const entry = currentTwoOptions();
    const cityArea = entry.study.site.facts.find((fact) => fact.fact_id === "fact-lot-area");
    expect(cityArea?.source?.kind).toBe("tax_map_computation");
    const next = expectOk(
      enterSiteFactAssumption(
        entry,
        { factId: "fact-lot-area", value: 6200, statement: "  Assume ~6,200 sq ft from the prior survey  " },
        T1,
      ),
    );
    // The city value is never overwritten in place: the original fact is still present, unchanged.
    expect(next.study.site.facts.find((fact) => fact.fact_id === "fact-lot-area")).toEqual(cityArea);
    // The assumption is a new fact at rank "assumed", sourced to the assumption, following the contract.
    const assumed = next.study.site.facts.find((fact) => fact.fact_id === "fact-lot-area-entered");
    expect(assumed?.value).toBe(6200);
    expect(assumed?.unit).toBe("square_feet");
    expect(assumed?.key).toBe("lot_area");
    expect(assumed?.measurement).toEqual({ rank: "assumed", label: MEASUREMENT_LABELS.assumed });
    expect(assumed?.source?.kind).toBe("assumption");
    expect(assumed?.source?.retrieved_at).toBe(T1);
    // The statement is stored trimmed and non-empty.
    expect(assumed?.source?.statement).toBe("Assume ~6,200 sq ft from the prior survey");
    expect(assumed?.blocks).toEqual([]);
    // The site is shared, so every option's results are out of date, and the whole study is contract-valid.
    expect(next.staleOptionIds).toEqual(["opt-a", "opt-b"]);
    expect(next.study.revision).toEqual({ number: 2, created_at: T1, parent: 1 });
    expect(validateStudyDocument(next.study).ok).toBe(true);
  });

  it("records an assumption in place on a non-city fact under its own id", () => {
    const entry = currentTwoOptions();
    const before = entry.study.site.facts.find((fact) => fact.fact_id === "fact-street-width-a");
    expect(before?.source?.kind).toBe("architect_entry");
    const next = expectOk(
      enterSiteFactAssumption(
        entry,
        { factId: "fact-street-width-a", value: 80, statement: "Assume an 80 ft mapped street width" },
        T2,
      ),
    );
    // No new fact: the non-city value is replaced in place.
    expect(next.study.site.facts).toHaveLength(entry.study.site.facts.length);
    const assumed = next.study.site.facts.find((fact) => fact.fact_id === "fact-street-width-a");
    expect(assumed?.value).toBe(80);
    expect(assumed?.street).toBe("Synthetic Street A");
    expect(assumed?.unit).toBe("feet");
    expect(assumed?.measurement).toEqual({ rank: "assumed", label: MEASUREMENT_LABELS.assumed });
    expect(assumed?.source?.kind).toBe("assumption");
    expect(assumed?.source?.statement).toBe("Assume an 80 ft mapped street width");
    expect(next.staleOptionIds).toEqual(["opt-a", "opt-b"]);
    expect(validateStudyDocument(next.study).ok).toBe(true);
  });

  it("records an assumption for existing zoning floor area (an unknown placeholder becomes assumed)", () => {
    const withUnknown = expectOk(upsertSiteFact(currentTwoOptions(), unknownExistingZfaFact(), T1));
    const next = expectOk(
      enterSiteFactAssumption(
        withUnknown,
        {
          factId: "fact-existing-zfa",
          value: 6200,
          statement: "Assume existing zoning floor area 6,200 sq ft (no DOB filing on record)",
        },
        T2,
      ),
    );
    const assumed = next.study.site.facts.find((fact) => fact.fact_id === "fact-existing-zfa");
    expect(assumed?.key).toBe("existing_zoning_floor_area");
    expect(assumed?.value).toBe(6200);
    expect(assumed?.unit).toBe("square_feet");
    expect(assumed?.measurement).toEqual({ rank: "assumed", label: MEASUREMENT_LABELS.assumed });
    expect(assumed?.source?.kind).toBe("assumption");
    expect(assumed?.blocks).toEqual([]);
    expect(validateStudyDocument(next.study).ok).toBe(true);
  });

  it("refuses a missing or blank statement and changes nothing (the existing invalid_document code)", () => {
    const entry = currentTwoOptions();
    for (const statement of ["", "   "]) {
      expect(
        enterSiteFactAssumption(entry, { factId: "fact-lot-area", value: 6200, statement }, T1),
      ).toMatchObject({ ok: false, code: "invalid_document" });
    }
    expect(entry.study.site.facts.some((fact) => fact.fact_id === "fact-lot-area-entered")).toBe(false);
    expect(entry.staleOptionIds).toEqual([]);
  });

  it("refuses a non-positive assumed value (the existing dimension message) and changes nothing", () => {
    const entry = currentTwoOptions();
    for (const value of [0, -5]) {
      expect(
        enterSiteFactAssumption(entry, { factId: "fact-lot-area", value, statement: "Assume a value" }, T1),
      ).toMatchObject({ ok: false, code: "invalid_document" });
    }
    expect(entry.study.site.facts.some((fact) => fact.fact_id === "fact-lot-area-entered")).toBe(false);
    expect(entry.staleOptionIds).toEqual([]);
  });

  it("refuses an assumption on a fact that is not in the study", () => {
    const entry = currentTwoOptions();
    expect(
      enterSiteFactAssumption(entry, { factId: "fact-missing", value: 10, statement: "Assume ten" }, T1),
    ).toMatchObject({ ok: false, code: "unknown_fact" });
  });

  it("uses a caller-supplied id for the new assumed fact", () => {
    const entry = currentTwoOptions();
    const next = expectOk(
      enterSiteFactAssumption(
        entry,
        {
          factId: "fact-lot-area",
          value: 6000,
          statement: "Assume 6,000 sq ft",
          enteredFactId: "fact-lot-area-assumed",
        },
        T1,
      ),
    );
    const assumed = next.study.site.facts.find((fact) => fact.fact_id === "fact-lot-area-assumed");
    expect(assumed?.measurement.rank).toBe("assumed");
    expect(assumed?.source?.kind).toBe("assumption");
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
