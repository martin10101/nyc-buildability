/**
 * Proposal draft model + client-side mirror validation (task M5-T060, D-076
 * phase B3 slice 2).
 *
 * The AUTHORITY of a proposed building here is a NUMERIC EPSG:2263 vertex model
 * (plus levels and exterior walls). The display CRS stays display-only — the
 * recorded measurement law (docs; MapPLUTO lot-outline is 4326 display only,
 * NEVER measured). NO client-side 4326->2263 transform exists in this module
 * and none is added: that bridge, map-based drawing, and scenario emission are
 * the deliberately deferred D-076-R003 post-B3 owner-checkpoint questions.
 *
 * The mirror below is a MIRROR, NEVER an authority. The server refusal at
 * services/api/app/api/v1/proposal_checks_api.py remains the truth surface;
 * every mirrored constant names its exact route source and exists only to give
 * the editor fast, honest feedback before a POST. If the mirror and the route
 * ever disagree, the route wins.
 */

import type { ProposalCheckRequest, ProposalCheckReportView } from "@/lib/proposal-checks-api";

// ---------------------------------------------------------------------------
// Draft types — every field is a numeric/typed caller-attested input, honestly
// labeled in the editor as the analyst's own input (a THIRD input class:
// proposed, never a city record and never a rule allowance; D-076-R002).
// ---------------------------------------------------------------------------
export interface DraftVertex {
  x: number;
  y: number;
}
export interface DraftLevel {
  level_index: number;
  floor_count: number;
  floor_to_floor_ft: number;
}
export interface DraftWall {
  id: string;
  start_vertex_index: number;
  end_vertex_index: number;
}
export interface DraftLotLineSegment {
  id: string;
  start_x: number;
  start_y: number;
  end_x: number;
  end_y: number;
}
export interface DraftStreetLine {
  wall_id: string;
  start_x: number;
  start_y: number;
  end_x: number;
  end_y: number;
  attested_width_ft: number | null;
}
export interface ProposalDraft {
  scenario_label: string;
  proposal_id: string;
  /** 2263 vertices — the numeric AUTHORITY (display CRS is display-only). */
  vertices: DraftVertex[];
  levels: DraftLevel[];
  exterior_walls: DraftWall[];
  /** Caller-attested lot-context inputs the route needs. */
  lot_area_sq_ft: number | null;
  area_provenance_note: string;
  lot_line_segments: DraftLotLineSegment[];
  street_lines: DraftStreetLine[];
  zoning_district: string;
  street_width_class: "" | "wide" | "narrow";
}

/** A client-local, ephemeral saved variation (this browser session only — never
 * a city record, never persisted; D-076-R002). */
export interface ProposalVariation {
  id: string;
  label: string;
  draft: ProposalDraft;
  report: ProposalCheckReportView | null;
}

// ---------------------------------------------------------------------------
// Mirror constants — each names its route source. NOT the authority.
// ---------------------------------------------------------------------------
/** Mirror of MAX_LABEL_LEN (proposal_checks_api.py). */
export const MIRROR_MAX_LABEL_LEN = 200;
/** Mirror of _LABEL_CHARSET (proposal_checks_api.py); fullmatch over the WHOLE
 * value, so a trailing newline is rejected exactly as the route does. */
export const MIRROR_LABEL_CHARSET = /^[A-Za-z0-9 ._:-]+$/;
/** Mirror of ROUTE_MAX_EXTERIOR_WALLS (proposal_checks_api.py). */
export const MIRROR_ROUTE_MAX_EXTERIOR_WALLS = 500;
/** Mirror of ROUTE_MAX_LOT_LINE_SEGMENTS (proposal_checks_api.py). */
export const MIRROR_ROUTE_MAX_LOT_LINE_SEGMENTS = 800;
/** Mirror of ROUTE_MAX_STREET_LINES (proposal_checks_api.py). */
export const MIRROR_ROUTE_MAX_STREET_LINES = 400;
/** Mirror of ROUTE_MAX_TOTAL_OUTLINE_POSITIONS (proposal_checks_api.py). */
export const MIRROR_ROUTE_MAX_TOTAL_OUTLINE_POSITIONS = 1200;

export interface DraftProblem {
  field: string;
  message: string;
  /** The exact route constant this mirror check echoes (the server remains the
   * authority). */
  routeConstant: string;
}

function validateLabel(
  value: string,
  field: string,
  { required }: { required: boolean },
  problems: DraftProblem[],
): void {
  const trimmed = value.trim();
  if (trimmed === "") {
    if (required) {
      problems.push({
        field,
        message: `${field} must be a non-empty label`,
        routeConstant: "_require_label",
      });
    }
    return;
  }
  if (value.length > MIRROR_MAX_LABEL_LEN) {
    problems.push({
      field,
      message: `${field} exceeds MAX_LABEL_LEN (${MIRROR_MAX_LABEL_LEN}); got ${value.length} characters`,
      routeConstant: "MAX_LABEL_LEN",
    });
  }
  if (!MIRROR_LABEL_CHARSET.test(value)) {
    problems.push({
      field,
      message: `${field} contains characters outside the allowed set [A-Za-z0-9 ._:-]`,
      routeConstant: "_LABEL_CHARSET",
    });
  }
}

/**
 * Mirror-validate a draft against the route's boundary caps/charsets/finiteness.
 * Returns a problem per violated cap, each naming the exact route constant. This
 * is a client convenience only; the server refusal is the truth (a draft that
 * passes here can still be refused server-side, and that refusal is surfaced as
 * a typed validation_error).
 */
export function validateDraft(draft: ProposalDraft): DraftProblem[] {
  const problems: DraftProblem[] = [];

  validateLabel(draft.scenario_label, "scenario_label", { required: true }, problems);
  validateLabel(draft.proposal_id, "proposal_id", { required: false }, problems);

  if (draft.exterior_walls.length > MIRROR_ROUTE_MAX_EXTERIOR_WALLS) {
    problems.push({
      field: "proposed_massing.exterior_walls",
      message: `${draft.exterior_walls.length} walls exceed the route cap ROUTE_MAX_EXTERIOR_WALLS (${MIRROR_ROUTE_MAX_EXTERIOR_WALLS})`,
      routeConstant: "ROUTE_MAX_EXTERIOR_WALLS",
    });
  }
  if (draft.lot_line_segments.length > MIRROR_ROUTE_MAX_LOT_LINE_SEGMENTS) {
    problems.push({
      field: "lot.lot_line_segments",
      message: `${draft.lot_line_segments.length} lot lines exceed the route cap ROUTE_MAX_LOT_LINE_SEGMENTS (${MIRROR_ROUTE_MAX_LOT_LINE_SEGMENTS})`,
      routeConstant: "ROUTE_MAX_LOT_LINE_SEGMENTS",
    });
  }
  if (draft.street_lines.length > MIRROR_ROUTE_MAX_STREET_LINES) {
    problems.push({
      field: "lot.street_lines",
      message: `${draft.street_lines.length} street lines exceed the route cap ROUTE_MAX_STREET_LINES (${MIRROR_ROUTE_MAX_STREET_LINES})`,
      routeConstant: "ROUTE_MAX_STREET_LINES",
    });
  }
  if (draft.vertices.length > MIRROR_ROUTE_MAX_TOTAL_OUTLINE_POSITIONS) {
    problems.push({
      field: "proposed_massing",
      message: `${draft.vertices.length} outline positions exceed the route cap ROUTE_MAX_TOTAL_OUTLINE_POSITIONS (${MIRROR_ROUTE_MAX_TOTAL_OUTLINE_POSITIONS})`,
      routeConstant: "ROUTE_MAX_TOTAL_OUTLINE_POSITIONS",
    });
  }

  draft.vertices.forEach((v, i) => {
    if (!Number.isFinite(v.x) || !Number.isFinite(v.y)) {
      problems.push({
        field: `proposed_massing.outline.vertices[${i}]`,
        message: `vertex ${i} must be finite EPSG:2263 coordinates`,
        routeConstant: "derive_proposal finiteness",
      });
    }
  });

  return problems;
}

/** A UX-level gate for enabling run-check: no mirror problems and enough
 * geometry to form an outline. NOT a legal/validity judgment — the route
 * remains the authority on a well-formed polygon. */
export function draftIsRunnable(draft: ProposalDraft): boolean {
  return validateDraft(draft).length === 0 && draft.vertices.length >= 3;
}

// ---------------------------------------------------------------------------
// Request assembly — build the exact route request contract from a draft.
// ---------------------------------------------------------------------------
export function toProposalCheckRequest(draft: ProposalDraft): ProposalCheckRequest {
  const lot_rule_facts: Record<string, unknown> = {};
  if (draft.zoning_district.trim() !== "") lot_rule_facts.zoning_district = draft.zoning_district.trim();
  if (draft.street_width_class !== "") lot_rule_facts.street_width_class = draft.street_width_class;
  return {
    proposed_massing: {
      outline: { srid: 2263, vertices: draft.vertices.map((v) => [v.x, v.y]) },
      levels: draft.levels.map((l) => ({
        level_index: l.level_index,
        floor_count: l.floor_count,
        floor_to_floor_ft: l.floor_to_floor_ft,
      })),
      exterior_walls: draft.exterior_walls.map((w) => ({
        id: w.id,
        start_vertex_index: w.start_vertex_index,
        end_vertex_index: w.end_vertex_index,
      })),
      provenance: { author: "proposal-editor", kind: "proposed", editor_version: "proposal-editor/0.1.0" },
    },
    lot: {
      area_sq_ft: draft.lot_area_sq_ft,
      area_provenance: { source: "caller_attested", note: draft.area_provenance_note },
      lot_line_segments: draft.lot_line_segments.map((s) => ({
        id: s.id,
        start: [s.start_x, s.start_y],
        end: [s.end_x, s.end_y],
      })),
      street_lines: draft.street_lines.map((s) => ({
        wall_id: s.wall_id,
        start: [s.start_x, s.start_y],
        end: [s.end_x, s.end_y],
        attestation:
          s.attested_width_ft === null
            ? { source: "caller_attested" }
            : { source: "caller_attested", width_ft: s.attested_width_ft },
      })),
    },
    lot_rule_facts,
    scenario_label: draft.scenario_label,
    proposal_id: draft.proposal_id.trim() === "" ? null : draft.proposal_id,
  };
}

// ---------------------------------------------------------------------------
// Pure, immutable draft mutation helpers (keep the editor component thin and
// the transitions unit-testable).
// ---------------------------------------------------------------------------
function replaceAt<T>(items: T[], index: number, next: T): T[] {
  return items.map((item, i) => (i === index ? next : item));
}
function removeAt<T>(items: T[], index: number): T[] {
  return items.filter((_, i) => i !== index);
}

export function addVertex(draft: ProposalDraft, vertex: DraftVertex): ProposalDraft {
  return { ...draft, vertices: [...draft.vertices, vertex] };
}
export function updateVertex(draft: ProposalDraft, index: number, patch: Partial<DraftVertex>): ProposalDraft {
  return { ...draft, vertices: replaceAt(draft.vertices, index, { ...draft.vertices[index], ...patch }) };
}
export function removeVertex(draft: ProposalDraft, index: number): ProposalDraft {
  return { ...draft, vertices: removeAt(draft.vertices, index) };
}
/** True when an exterior wall's endpoints both reference a vertex index that
 * exists in an outline of `vertexCount` vertices. A wall with a non-integer or
 * out-of-range endpoint would dangle after the outline is replaced. */
function wallReferencesInRange(wall: DraftWall, vertexCount: number): boolean {
  return (
    Number.isInteger(wall.start_vertex_index) &&
    Number.isInteger(wall.end_vertex_index) &&
    wall.start_vertex_index >= 0 &&
    wall.start_vertex_index < vertexCount &&
    wall.end_vertex_index >= 0 &&
    wall.end_vertex_index < vertexCount
  );
}

/**
 * The ids of exterior walls that would DANGLE if the outline were replaced with
 * an outline of `vertexCount` vertices — i.e. walls whose start/end vertex index
 * no longer exists (task M5-T066, DB-045(f)/HJ-2). validateDraft does NOT catch
 * a wall pointing at a removed vertex, so adoption uses this to reconcile the
 * model and the editor uses it to announce exactly what was dropped (never a
 * silent structural change).
 */
export function danglingWallIds(walls: DraftWall[], vertexCount: number): string[] {
  return walls.filter((w) => !wallReferencesInRange(w, vertexCount)).map((w) => w.id);
}

/**
 * Replace the draft outline with vertices adopted from the map-drawing bridge
 * (task M5-T065, D-082-R001). The bridge returns EPSG:2263 vertices converted
 * from a map drawing by correspondence to the official parcel geometry; they
 * land in the numeric AUTHORITY here EXACTLY as if the analyst had typed them —
 * the table stays visible, editable, and authoritative (manual remains the
 * option, D-082-R003). Pure/immutable: levels and lot inputs are untouched (the
 * analyst still supplies those). The incoming coordinates are the bridge's
 * output with its residual disclosed by the caller — never presented here as
 * survey-grade.
 *
 * RECONCILIATION (task M5-T066, DB-045(f)/HJ-2): the outline can be replaced
 * with a DIFFERENT vertex count than the current draft. Exterior walls address
 * vertices by index, so a smaller-count adoption would leave walls pointing at
 * removed vertices — a dangling reference validateDraft does not catch. Adoption
 * therefore drops every wall whose endpoints no longer exist, so the result is
 * ALWAYS internally consistent. An equal- or larger-count adoption keeps every
 * wall (all indices stay in range), preserving the accepted equal-count
 * semantics. Lot-line segments reference explicit coordinates, not vertex
 * indices, so they can never dangle on an outline replacement and are untouched.
 */
export function adoptOutlineVertices(draft: ProposalDraft, vertices: DraftVertex[]): ProposalDraft {
  const nextVertices = vertices.map((v) => ({ x: v.x, y: v.y }));
  const exterior_walls = draft.exterior_walls.filter((w) =>
    wallReferencesInRange(w, nextVertices.length),
  );
  return { ...draft, vertices: nextVertices, exterior_walls };
}
export function addLevel(draft: ProposalDraft, level: DraftLevel): ProposalDraft {
  return { ...draft, levels: [...draft.levels, level] };
}
export function updateLevel(draft: ProposalDraft, index: number, patch: Partial<DraftLevel>): ProposalDraft {
  return { ...draft, levels: replaceAt(draft.levels, index, { ...draft.levels[index], ...patch }) };
}
export function removeLevel(draft: ProposalDraft, index: number): ProposalDraft {
  return { ...draft, levels: removeAt(draft.levels, index) };
}
export function addWall(draft: ProposalDraft, wall: DraftWall): ProposalDraft {
  return { ...draft, exterior_walls: [...draft.exterior_walls, wall] };
}
export function updateWall(draft: ProposalDraft, index: number, patch: Partial<DraftWall>): ProposalDraft {
  return { ...draft, exterior_walls: replaceAt(draft.exterior_walls, index, { ...draft.exterior_walls[index], ...patch }) };
}
export function removeWall(draft: ProposalDraft, index: number): ProposalDraft {
  return { ...draft, exterior_walls: removeAt(draft.exterior_walls, index) };
}

// ---------------------------------------------------------------------------
// Seed drafts.
// ---------------------------------------------------------------------------
export function emptyDraft(): ProposalDraft {
  return {
    scenario_label: "New proposal",
    proposal_id: "",
    vertices: [],
    levels: [],
    exterior_walls: [],
    lot_area_sq_ft: null,
    area_provenance_note: "",
    lot_line_segments: [],
    street_lines: [],
    zoning_district: "",
    street_width_class: "",
  };
}

/** The accepted M5-T054 rectangle case as an editable draft (100 ft x 50 ft, 3
 * floors, 8000 sq ft R5 lot). Seeding it makes the editor immediately
 * meaningful; run against the accepted route it reproduces the AS-1 arithmetic
 * (coverage 0.625 vs 0.5; height 30 <= 60). */
export function rectangleSampleDraft(): ProposalDraft {
  return {
    scenario_label: "scenario-A-baseline",
    proposal_id: "prop-0001",
    vertices: [
      { x: 1000000, y: 200000 },
      { x: 1000100, y: 200000 },
      { x: 1000100, y: 200050 },
      { x: 1000000, y: 200050 },
      { x: 1000000, y: 200000 },
    ],
    levels: [{ level_index: 0, floor_count: 3, floor_to_floor_ft: 10 }],
    exterior_walls: [
      { id: "W-S", start_vertex_index: 0, end_vertex_index: 1 },
      { id: "W-E", start_vertex_index: 1, end_vertex_index: 2 },
      { id: "W-N", start_vertex_index: 2, end_vertex_index: 3 },
      { id: "W-W", start_vertex_index: 3, end_vertex_index: 0 },
    ],
    lot_area_sq_ft: 8000,
    area_provenance_note: "caller-attested lot area (example)",
    lot_line_segments: [{ id: "LL-W", start_x: 999990, start_y: 199990, end_x: 999990, end_y: 200060 }],
    street_lines: [],
    zoning_district: "R5",
    street_width_class: "wide",
  };
}
