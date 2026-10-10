import { describe, expect, it } from "vitest";
import { capNotices, collectConditions } from "@/lib/architect/presented-notices";
import type { Results } from "@/lib/architect/three-answers";
import { loadResultsFixture } from "@/test-support/results-fixtures";

/**
 * M5-T148 part B scenario S7: the conditions repeated under many results are listed once, each
 * result refers to them and none is lost (tested on the benchmark document); at most three notices
 * are shown and the rest sit behind a count.
 */

const BENCHMARK = "recorded_215_16_northern_journey";

// An independent collector of the document's distinct "If …" lines, mirroring conditionList's rule,
// so "none lost / listed once" is proven against the document rather than hardcoded strings.
function distinctConditionTexts(doc: Results): Set<string> {
  const texts = new Set<string>();
  const add = (state: { way: string; conditions?: { assumption: string }[] }) => {
    if (state.way !== "conditional") return;
    for (const condition of state.conditions ?? []) {
      const trimmed = condition.assumption.trim();
      texts.add(trimmed.startsWith("If ") ? trimmed : `If ${trimmed}`);
    }
  };
  for (const key of ["floor_area_allowance", "permitted_envelope", "building_option"] as const) {
    const answer = doc.answers[key];
    if (answer.status === "available" && answer.value_states) {
      for (const state of Object.values(answer.value_states)) add(state);
    }
  }
  for (const alternative of doc.building_alternatives ?? []) add(alternative.way);
  const coverage = doc.coverage_by_portion;
  if (coverage && coverage.status === "available") add(coverage.way);
  return texts;
}

describe("collectConditions (scenario S7)", () => {
  it("lists each shared condition once, each result refers to them, and none is lost", () => {
    const doc = loadResultsFixture(BENCHMARK);
    const { shared, references } = collectConditions(doc);

    // Listed once: the ids and the texts are each distinct.
    expect(new Set(shared.map(c => c.id)).size).toBe(shared.length);
    expect(new Set(shared.map(c => c.text)).size).toBe(shared.length);
    expect(shared.length).toBe(2); // the benchmark repeats two conditions across many results

    // None lost: the shared set equals the document's distinct condition lines, computed here.
    expect(new Set(shared.map(c => c.text))).toEqual(distinctConditionTexts(doc));

    // Each result refers to shared ids only (never a re-typed line), and ids resolve.
    const sharedIds = new Set(shared.map(c => c.id));
    const textById = new Map(shared.map(c => [c.id, c.text]));
    for (const ref of references) {
      expect(ref.conditionIds.length).toBeGreaterThan(0);
      for (const id of ref.conditionIds) expect(sharedIds.has(id)).toBe(true);
    }

    // Repeated under many results: more than one result refers to the conditions, and the
    // conditions attach with different multiplicities (floor-area values carry two, heights one).
    expect(references.length).toBeGreaterThan(1);
    const sizes = new Set(references.map(ref => ref.conditionIds.length));
    expect(sizes.has(2)).toBe(true);
    expect(sizes.has(1)).toBe(true);

    // Every text reachable through references exists in the shared set (none orphaned).
    const reachable = new Set(references.flatMap(ref => ref.conditionIds.map(id => textById.get(id))));
    expect(reachable).toEqual(new Set(shared.map(c => c.text)));
  });

  it("returns an empty collection for a document with no conditions", () => {
    const doc = loadResultsFixture("synthetic_all_answers_available");
    expect(collectConditions(doc)).toEqual({ shared: [], references: [] });
  });
});

describe("capNotices (scenario S7)", () => {
  it("shows three of five and counts the rest as '2 more', dropping none", () => {
    const notices = ["a", "b", "c", "d", "e"];
    const capped = capNotices(notices);
    expect(capped.visible).toEqual(["a", "b", "c"]);
    expect(capped.hidden).toEqual(["d", "e"]);
    expect(capped.moreLabel).toBe("2 more");
    expect([...capped.visible, ...capped.hidden]).toEqual(notices);
  });

  it("shows all and no count when three or fewer", () => {
    const capped = capNotices(["a", "b", "c"]);
    expect(capped.visible).toEqual(["a", "b", "c"]);
    expect(capped.hidden).toEqual([]);
    expect(capped.moreLabel).toBeNull();
  });
});
