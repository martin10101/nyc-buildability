import { describe, expect, it } from "vitest";
import {
  addLevel,
  addVertex,
  addWall,
  adoptOutlineVertices,
  draftIsRunnable,
  emptyDraft,
  MIRROR_MAX_LABEL_LEN,
  MIRROR_ROUTE_MAX_EXTERIOR_WALLS,
  MIRROR_ROUTE_MAX_LOT_LINE_SEGMENTS,
  MIRROR_ROUTE_MAX_STREET_LINES,
  MIRROR_ROUTE_MAX_TOTAL_OUTLINE_POSITIONS,
  rectangleSampleDraft,
  removeVertex,
  toProposalCheckRequest,
  updateVertex,
  validateDraft,
  type ProposalDraft,
} from "@/lib/architect/proposal-draft";

/**
 * Task M5-T060, draft-model layer: the mirror validation must fail closed on
 * every route cap/charset and NAME the exact route constant it echoes (the
 * server refusal remains the authority), and the request assembly must produce
 * the route's documented request contract.
 */

function constants(draft: ProposalDraft): string[] {
  return validateDraft(draft).map((p) => p.routeConstant);
}

describe("validateDraft — mirror of the route boundary caps (each names its route constant)", () => {
  it("passes a clean rectangle sample", () => {
    expect(validateDraft(rectangleSampleDraft())).toEqual([]);
  });

  it("flags an over-length scenario_label naming MAX_LABEL_LEN", () => {
    const draft = { ...rectangleSampleDraft(), scenario_label: "s".repeat(MIRROR_MAX_LABEL_LEN + 1) };
    expect(constants(draft)).toContain("MAX_LABEL_LEN");
  });

  it("flags a bad-charset scenario_label naming _LABEL_CHARSET", () => {
    const draft = { ...rectangleSampleDraft(), scenario_label: "scn<script>" };
    expect(constants(draft)).toContain("_LABEL_CHARSET");
  });

  it("flags a trailing-newline label (fullmatch over the WHOLE value) naming _LABEL_CHARSET", () => {
    const draft = { ...rectangleSampleDraft(), scenario_label: "scenario-A\n" };
    expect(constants(draft)).toContain("_LABEL_CHARSET");
  });

  it("flags a bad-charset proposal_id naming _LABEL_CHARSET", () => {
    const draft = { ...rectangleSampleDraft(), proposal_id: "p/../../etc" };
    expect(constants(draft)).toContain("_LABEL_CHARSET");
  });

  it("flags over-cap exterior_walls naming ROUTE_MAX_EXTERIOR_WALLS", () => {
    const draft = {
      ...rectangleSampleDraft(),
      exterior_walls: Array.from({ length: MIRROR_ROUTE_MAX_EXTERIOR_WALLS + 1 }, (_, i) => ({
        id: `W${i}`,
        start_vertex_index: 0,
        end_vertex_index: 1,
      })),
    };
    expect(constants(draft)).toContain("ROUTE_MAX_EXTERIOR_WALLS");
  });

  it("flags over-cap lot_line_segments naming ROUTE_MAX_LOT_LINE_SEGMENTS", () => {
    const draft = {
      ...rectangleSampleDraft(),
      lot_line_segments: Array.from({ length: MIRROR_ROUTE_MAX_LOT_LINE_SEGMENTS + 1 }, (_, i) => ({
        id: `LL${i}`,
        start_x: 0,
        start_y: 0,
        end_x: 0,
        end_y: 1,
      })),
    };
    expect(constants(draft)).toContain("ROUTE_MAX_LOT_LINE_SEGMENTS");
  });

  it("flags over-cap street_lines naming ROUTE_MAX_STREET_LINES", () => {
    const draft = {
      ...rectangleSampleDraft(),
      street_lines: Array.from({ length: MIRROR_ROUTE_MAX_STREET_LINES + 1 }, () => ({
        wall_id: "south",
        start_x: 0,
        start_y: 0,
        end_x: 1,
        end_y: 0,
        attested_width_ft: null,
      })),
    };
    expect(constants(draft)).toContain("ROUTE_MAX_STREET_LINES");
  });

  it("flags over-cap outline positions naming ROUTE_MAX_TOTAL_OUTLINE_POSITIONS", () => {
    const draft = {
      ...rectangleSampleDraft(),
      vertices: Array.from({ length: MIRROR_ROUTE_MAX_TOTAL_OUTLINE_POSITIONS + 1 }, (_, i) => ({ x: i, y: 0 })),
    };
    expect(constants(draft)).toContain("ROUTE_MAX_TOTAL_OUTLINE_POSITIONS");
  });

  it("flags a non-finite vertex coordinate", () => {
    const draft = updateVertex(rectangleSampleDraft(), 0, { x: Number.NaN });
    expect(constants(draft).some((c) => c.includes("finiteness"))).toBe(true);
  });
});

describe("toProposalCheckRequest — the route request contract", () => {
  it("maps the 2263 authority, labels, and lot rule facts", () => {
    const req = toProposalCheckRequest(rectangleSampleDraft());
    expect(req.proposed_massing.outline.srid).toBe(2263);
    expect(req.proposed_massing.outline.vertices[0]).toEqual([1000000, 200000]);
    expect(req.proposed_massing.exterior_walls).toHaveLength(4);
    expect(req.scenario_label).toBe("scenario-A-baseline");
    expect(req.proposal_id).toBe("prop-0001");
    expect(req.lot_rule_facts).toEqual({ zoning_district: "R5", street_width_class: "wide" });
    expect(req.lot.area_sq_ft).toBe(8000);
  });

  it("sends a null proposal_id when the field is blank", () => {
    const req = toProposalCheckRequest({ ...rectangleSampleDraft(), proposal_id: "" });
    expect(req.proposal_id).toBeNull();
  });

  it("omits unattested lot rule facts", () => {
    const req = toProposalCheckRequest({ ...rectangleSampleDraft(), zoning_district: "", street_width_class: "" });
    expect(req.lot_rule_facts).toEqual({});
  });
});

describe("draft helpers", () => {
  it("adds, updates, and removes vertices/levels/walls immutably", () => {
    const base = rectangleSampleDraft();
    const added = addVertex(base, { x: 5, y: 6 });
    expect(added.vertices).toHaveLength(base.vertices.length + 1);
    expect(base.vertices).toHaveLength(5); // unchanged
    expect(updateVertex(base, 0, { x: 42 }).vertices[0]).toEqual({ x: 42, y: 200000 });
    expect(removeVertex(base, 0).vertices).toHaveLength(4);
    expect(addLevel(base, { level_index: 1, floor_count: 2, floor_to_floor_ft: 11 }).levels).toHaveLength(2);
    expect(addWall(base, { id: "W-X", start_vertex_index: 0, end_vertex_index: 1 }).exterior_walls).toHaveLength(5);
  });

  it("marks a runnable sample runnable and an empty draft not", () => {
    expect(draftIsRunnable(rectangleSampleDraft())).toBe(true);
    expect(draftIsRunnable(emptyDraft())).toBe(false);
  });

  it("adopts bridged 2263 vertices into the outline, replacing it and leaving levels/walls intact", () => {
    const base = rectangleSampleDraft();
    const adopted = adoptOutlineVertices(base, [
      { x: 1000020, y: 200010 },
      { x: 1000080, y: 200010 },
      { x: 1000080, y: 200030 },
    ]);
    expect(adopted.vertices).toEqual([
      { x: 1000020, y: 200010 },
      { x: 1000080, y: 200010 },
      { x: 1000080, y: 200030 },
    ]);
    // Only the outline is replaced; the rest of the draft is preserved.
    expect(adopted.levels).toEqual(base.levels);
    expect(adopted.exterior_walls).toEqual(base.exterior_walls);
    expect(adopted.scenario_label).toBe(base.scenario_label);
    // Immutable: the source draft is untouched.
    expect(base.vertices).toHaveLength(5);
  });
});
