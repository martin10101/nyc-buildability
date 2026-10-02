import { describe, expect, it } from "vitest";
import validFour from "../../../../../../packages/contracts/fixtures/valid/hidden_issue_flags/synthetic_four_groups.json";
import validAllowance from "../../../../../../packages/contracts/fixtures/valid/hidden_issue_flags/real_existing_building_allowance.json";
import type { HiddenIssueFlagsDocument } from "@/lib/hidden-issue-flags-contract-checks";
import {
  NOT_A_CLEAN_BILL_NOTE,
  STATUS_MEANINGS,
  evidenceView,
  factRelationText,
  flagStripSummary,
  flagView,
  groupViews,
  humanFactName,
  orderedGroups,
} from "@/lib/architect/hidden-issue-flags-view";

/**
 * Pure view-model for the §8a hidden-issue flags (queue D-12, plan M2-06 / §8a).
 * Proves: group ordering; the one §5a status strip (<=3 items, honest fallback);
 * each status's plain meaning; "No flag" read as a specific result not a clean
 * bill; "beside the affected results" fact relation; and that no internal code
 * (item_id, raw fact_ref, source kind/query token) reaches the visible rows.
 */

function fourGroups(): HiddenIssueFlagsDocument {
  return JSON.parse(JSON.stringify(validFour)) as HiddenIssueFlagsDocument;
}
function allowance(): HiddenIssueFlagsDocument {
  return JSON.parse(JSON.stringify(validAllowance)) as HiddenIssueFlagsDocument;
}

describe("hidden-issue-flags-view — grouping and §5a strip", () => {
  it("orders the groups in the canonical §8a order", () => {
    const doc = fourGroups();
    expect(orderedGroups(doc).map((g) => g.group_id)).toEqual([
      "existing_building",
      "zoning_lot_history",
      "map_based_rules",
      "site_shape_and_street",
    ]);
    expect(groupViews(doc).map((g) => g.key)).toEqual([
      "existing_building",
      "zoning_lot_history",
      "map_based_rules",
      "site_shape_and_street",
    ]);
  });

  it("shows each item exactly once in its group", () => {
    const groups = groupViews(fourGroups());
    const keys = groups.flatMap((g) => g.flags.map((f) => f.key));
    expect(new Set(keys).size).toBe(keys.length);
    expect(keys.length).toBe(4);
  });

  it("summarises the strip as at most three present categories", () => {
    const summary = flagStripSummary(fourGroups());
    // four-group fixture: 2 flags (zlh + map), 1 check_needed, 1 not_flagged.
    expect(summary.counts).toEqual({ flag: 2, opportunity: 0, check_needed: 1, not_flagged: 1 });
    expect(summary.items).toEqual(["2 flags", "1 to check"]);
    expect(summary.items.length).toBeLessThanOrEqual(3);
  });

  it("never asserts 'no issues': an all-not_flagged doc gets a per-check line", () => {
    const doc = fourGroups();
    for (const group of doc.groups) {
      for (const flag of group.flags) {
        // Presentation-only probe; the contract's P-2 rule is enforced elsewhere.
        (flag as unknown as { status: string }).status = "not_flagged";
      }
    }
    const summary = flagStripSummary(doc);
    expect(summary.items).toEqual(["Each check below shows its own result"]);
    const joined = summary.items.join(" ").toLowerCase();
    expect(joined).not.toContain("no issue");
    expect(joined).not.toContain("clear");
  });
});

describe("hidden-issue-flags-view — status meanings and honesty", () => {
  it("maps every status to its label and a plain meaning", () => {
    const byId = new Map(
      groupViews(fourGroups()).flatMap((g) => g.flags.map((f) => [f.key, f] as const)),
    );
    const eb = byId.get("existing_building.larger_than_today");
    expect(eb?.statusLabel).toBe("Check needed");
    expect(eb?.statusMeaning).toBe(STATUS_MEANINGS.check_needed);

    const zlh = byId.get("zoning_lot_history.recorded_mentions");
    expect(zlh?.statusLabel).toBe("Flag");
    expect(zlh?.statusMeaning).toBe(STATUS_MEANINGS.flag);

    const site = byId.get("site_shape_and_street.through_lot");
    expect(site?.statusLabel).toBe("No flag");
    expect(site?.statusMeaning).toBe("This check found nothing to flag.");
  });

  it("reads 'No flag' as one check's result, never an all-clear for the property", () => {
    expect(STATUS_MEANINGS.not_flagged.toLowerCase()).toContain("this check");
    expect(STATUS_MEANINGS.not_flagged.toLowerCase()).not.toContain("property");
    expect(NOT_A_CLEAN_BILL_NOTE.toLowerCase()).toContain("not an all-clear");
  });

  it("maps the real allowance fixture's flag + check_needed items", () => {
    const groups = groupViews(allowance());
    expect(groups.map((g) => g.key)).toEqual(["existing_building"]);
    const statuses = groups[0].flags.map((f) => f.statusLabel);
    expect(statuses).toEqual(["Flag", "Check needed", "Check needed", "Check needed", "Check needed"]);
  });
});

describe("hidden-issue-flags-view — beside-the-results relation and sources", () => {
  it("names the related site fact in plain words, never the raw token", () => {
    expect(humanFactName("1000010100:existing_zoning_floor_area")).toBe("existing zoning floor area");
    const doc = allowance();
    const larger = doc.groups[0].flags[0];
    const relation = factRelationText(larger);
    expect(relation).toBe("Relates to: existing zoning floor area.");
    expect(relation).not.toContain("_");
    expect(relation).not.toContain(":");
  });

  it("returns no relation for a flag with no fact_ref", () => {
    const doc = fourGroups();
    const zlh = doc.groups.find((g) => g.group_id === "zoning_lot_history")!.flags[0];
    expect(zlh.fact_refs).toEqual([]);
    expect(factRelationText(zlh)).toBeNull();
  });

  it("surfaces provenance plainly and hides the internal kind/query tokens", () => {
    const doc = fourGroups();
    const mapFlag = doc.groups.find((g) => g.group_id === "map_based_rules")!.flags[0];
    const view = flagView(mapFlag);
    const [evidence] = view.evidence;
    expect(evidence.hasSource).toBe(true);
    const lines = evidence.sourceLines.join(" ");
    expect(lines).toContain("Dataset: test-fixture-synthetic PLUTO (26v2)");
    expect(lines).toContain("Recorded:");
    expect(lines).not.toContain("city_dataset");
    expect(lines).not.toContain("://");
    expect(lines).not.toContain("query_ref");
  });

  it("says plainly when an input carries no dataset", () => {
    const doc = fourGroups();
    const eb = doc.groups.find((g) => g.group_id === "existing_building")!.flags[0];
    const view = evidenceView(eb.evidence[0]);
    expect(view.hasSource).toBe(false);
    expect(view.sourceLines).toEqual(["No dataset is connected for this input."]);
  });
});
