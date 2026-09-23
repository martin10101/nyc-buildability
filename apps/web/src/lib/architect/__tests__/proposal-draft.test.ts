import { describe, expect, it } from "vitest";
import {
  addLevel,
  addVertex,
  addWall,
  adoptOutlineVertices,
  danglingWallIds,
  draftFromCandidate,
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
  type CandidateSeed,
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

  it("adopts an EQUAL-count outline, replacing the vertices and leaving levels/walls intact (accepted T065 semantics)", () => {
    const base = rectangleSampleDraft(); // 5 vertices, 4 walls referencing indices 0-3
    const nextOutline = [
      { x: 1000020, y: 200010 },
      { x: 1000090, y: 200010 },
      { x: 1000090, y: 200040 },
      { x: 1000020, y: 200040 },
      { x: 1000020, y: 200010 },
    ];
    const adopted = adoptOutlineVertices(base, nextOutline);
    expect(adopted.vertices).toEqual(nextOutline);
    // Equal count keeps every wall (all indices stay in range) and levels intact.
    expect(adopted.levels).toEqual(base.levels);
    expect(adopted.exterior_walls).toEqual(base.exterior_walls);
    expect(adopted.scenario_label).toBe(base.scenario_label);
    // Immutable: the source draft is untouched.
    expect(base.vertices).toHaveLength(5);
  });

  // -------------------------------------------------------------------------
  // AS-6 / DB-045(f) / HJ-2 — adoption reconciliation: adopting a DIFFERENT
  // vertex count must never leave a wall pointing at a removed vertex.
  // -------------------------------------------------------------------------
  it("AS-6: adopting a SMALLER outline drops the walls that would dangle, leaving NO out-of-range wall reference", () => {
    const base = rectangleSampleDraft(); // walls reference vertex indices up to 3
    // Adopt only 3 vertices: valid indices are now 0,1,2 — walls touching 3 dangle.
    const adopted = adoptOutlineVertices(base, [
      { x: 1000020, y: 200010 },
      { x: 1000080, y: 200010 },
      { x: 1000080, y: 200030 },
    ]);
    expect(adopted.vertices).toHaveLength(3);
    // MUTATION GUARD: every surviving wall references an in-range vertex — the
    // model can never carry a dangling reference after adoption. Reverting the
    // reconciliation (keeping base.exterior_walls) turns this red, because
    // W-N (end 3) and W-W (start 3) point past the new 3-vertex outline.
    for (const wall of adopted.exterior_walls) {
      expect(wall.start_vertex_index).toBeLessThan(adopted.vertices.length);
      expect(wall.end_vertex_index).toBeLessThan(adopted.vertices.length);
    }
    // The two south/east walls (indices 0-1, 1-2) survive; the two that touch
    // vertex 3 are dropped.
    expect(adopted.exterior_walls.map((w) => w.id)).toEqual(["W-S", "W-E"]);
    // Levels are still untouched by an outline replacement.
    expect(adopted.levels).toEqual(base.levels);
  });

  it("AS-6: adopting a LARGER outline keeps every wall (all indices stay in range), mirroring equal-count preservation", () => {
    const base = rectangleSampleDraft(); // walls reference vertex indices 0-3
    const larger = Array.from({ length: 7 }, (_, i) => ({ x: 1_000_000 + i, y: 200_000 }));
    const adopted = adoptOutlineVertices(base, larger);
    expect(adopted.vertices).toHaveLength(7);
    // Every original wall index (max 3) is still in range under 7 vertices, so
    // nothing is dropped — the accepted preservation semantics extend to a
    // larger-count adoption, not just the equal-count case.
    expect(adopted.exterior_walls).toEqual(base.exterior_walls);
    expect(adopted.levels).toEqual(base.levels);
  });

  it("danglingWallIds reports exactly the walls whose endpoints fall outside the new outline", () => {
    const base = rectangleSampleDraft();
    // A 3-vertex outline invalidates the walls that reference vertex index 3.
    expect(danglingWallIds(base.exterior_walls, 3)).toEqual(["W-N", "W-W"]);
    // An equal-or-larger outline dangles nothing.
    expect(danglingWallIds(base.exterior_walls, 5)).toEqual([]);
    expect(danglingWallIds(base.exterior_walls, 8)).toEqual([]);
    // A non-integer/negative endpoint is treated as dangling (can never index).
    expect(danglingWallIds([{ id: "W-bad", start_vertex_index: -1, end_vertex_index: 0 }], 5)).toEqual([
      "W-bad",
    ]);
  });
});

// ---------------------------------------------------------------------------
// Task M5-T070 (D-083-R002 / AS-4): seed THIS one draft model from a Generated
// building option candidate. The candidate's 2263 outline + levels + walls pass
// through VERBATIM (no math, no CRS transform) and land as PROPOSED input, and
// the adopted draft is immediately runnable against the check route.
// ---------------------------------------------------------------------------
describe("draftFromCandidate — adoption seeding of the Generated building option", () => {
  const candidate: CandidateSeed = {
    outline: {
      vertices: [
        [1000000, 200000],
        [1000100, 200000],
        [1000100, 200050],
        [1000000, 200050],
      ],
    },
    levels: [{ level_index: 0, floor_count: 5, floor_to_floor_ft: 10 }],
    exterior_walls: [
      { id: "W-S", start_vertex_index: 0, end_vertex_index: 1 },
      { id: "W-E", start_vertex_index: 1, end_vertex_index: 2 },
    ],
  };

  it("passes the candidate outline/levels/walls through VERBATIM (no math, no CRS transform)", () => {
    const draft = draftFromCandidate(candidate);
    expect(draft.vertices).toEqual([
      { x: 1000000, y: 200000 },
      { x: 1000100, y: 200000 },
      { x: 1000100, y: 200050 },
      { x: 1000000, y: 200050 },
    ]);
    expect(draft.levels).toEqual([{ level_index: 0, floor_count: 5, floor_to_floor_ft: 10 }]);
    expect(draft.exterior_walls).toEqual(candidate.exterior_walls);
  });

  it("labels the draft the D-083 claim class by default and marks the provenance PROPOSED, not a city record", () => {
    const draft = draftFromCandidate(candidate);
    expect(draft.scenario_label).toBe("Generated building option");
    expect(draft.area_provenance_note).toContain("proposed input, not a city record");
    // proposal_id is blank (the analyst names their own scenario), and no lot geometry is fabricated.
    expect(draft.proposal_id).toBe("");
    expect(draft.lot_line_segments).toEqual([]);
    expect(draft.street_lines).toEqual([]);
  });

  it("threads the SAME max-envelope request lot context (area/zoning) so the adopted draft is immediately runnable", () => {
    const draft = draftFromCandidate(candidate, {
      lot_area_sq_ft: 8000,
      zoning_district: "R6",
      street_width_class: "wide",
    });
    expect(draft.lot_area_sq_ft).toBe(8000);
    expect(draft.zoning_district).toBe("R6");
    expect(draft.street_width_class).toBe("wide");
    // With ≥3 vertices and no mirror problems the seeded draft is runnable at once.
    expect(draftIsRunnable(draft)).toBe(true);
  });

  it("honors an explicit label override", () => {
    expect(draftFromCandidate(candidate, { label: "Option A" }).scenario_label).toBe("Option A");
  });
});
