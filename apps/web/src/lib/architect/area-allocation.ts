/**
 * The two-zone area-allocation selector (M5-T187; fitted branch M5-T202 part B2a;
 * D-094 R088/R091/R092/R093/R094/R095/R096, G-14).
 *
 * Reads ONE 1.5.0 `area_allocation` block (and, for the fitted branch, the
 * building's optional `placement`) and returns what the AreaAllocation component
 * must draw. It mirrors the accepted PDF drawing kernel in words AND in geometry
 * (services/api/app/drawings/kit/area_allocation.py, M5-T183):
 *
 *   • a sound, NOT-fitted block  -> a proportional bar split by the apartment
 *     share, with exactly one stated percentage round(share * 100) (R094);
 *   • a sound, FITTED block whose placement is placed with a drawable outline ->
 *     the two zones inside that footprint, split by a single vertical division at
 *     the share ratio, computed by the kernel's own `_poly_area`, `_clip_x` and
 *     `_division_x` (bisection) ported here so the website and the PDF split the
 *     footprint identically (R088/R091/R096); the apartment/other split numbers,
 *     the percentage and the measure come from the block, never recomputed;
 *   • anything else fails CLOSED to an explicit `unavailable` with a plain reason
 *     — never a guessed drawing (no default stands for a fact):
 *       a garbled block, a non-numeric or out-of-range share, an apartment/other
 *       split that does not reconcile with the total or with the share, an
 *       unstated `fitted` flag, a fitted block with no placed outline, or a placed
 *       outline the kernel cannot draw truthfully (too many points, a point out of
 *       range, or no area to divide).
 *
 * The reason strings are byte-equal to the kernel's so the two surfaces explain a
 * refusal in the same words. No legal meaning and no zoning maths live here: the
 * block carries its own pre-computed share and areas; this selector never invents
 * a figure. The only geometry it computes is the proportional division of the
 * block's OWN placed footprint, exactly as the kernel draws it.
 */

import {
  AREA_ALLOCATION_CONVERSION_STATEMENT,
  AREA_ALLOCATION_MEASURE,
  AREA_ALLOCATION_SHARE_MAX,
  AREA_ALLOCATION_SHARE_MIN,
  ILLUSTRATIVE_LABEL,
} from "@/lib/results-contract-checks";

/** apartment + other must equal total within the two-decimal display rounding (kernel _AREA_TOL). */
const AREA_TOLERANCE = 0.01 + 1e-9;
/** the drawn proportion (and the apartment/total consistency check) within 0.5 % (kernel _SHARE_TOL). */
const SHARE_TOLERANCE = 0.005 + 1e-9;
/** A placed footprint carries a handful of vertices (kernel _MAX_OUTLINE_VERTICES). */
const MAX_OUTLINE_VERTICES = 1000;
/** A coordinate magnitude above this would overflow the geometry arithmetic (kernel _COORD_MAX). */
const COORD_MAX = 1.0e9;

/** A plain-word refusal reason, byte-equal to the PDF kernel's Unavailable text. */
export const AREA_REASON_MISSING = "There is no area allocation to draw.";
export const AREA_REASON_INCOMPLETE = "The area allocation is incomplete.";
export const AREA_REASON_SHARE_NOT_NUMBER = "The apartment share is not a number.";
export const AREA_REASON_SHARE_OUT_OF_RANGE = "The apartment share is outside the range shown.";
export const AREA_REASON_SPLIT_NOT_NUMBERS = "The area split is not given in numbers.";
export const AREA_REASON_TOTAL_MISMATCH =
  "The apartment and other areas do not add up to the total.";
export const AREA_REASON_SHARE_MISMATCH = "The apartment area does not match the share shown.";
export const AREA_REASON_FITTED_UNKNOWN = "It is not stated whether the footprint is fitted.";
export const AREA_REASON_NOT_PLACED =
  "The footprint has not been placed on the lot, so the zones cannot be drawn yet.";
/** The four placed-outline refusals (kernel `_outline_unavailable`), byte-equal. */
export const AREA_REASON_OUTLINE_TOO_MANY_POINTS = "The footprint has too many points to draw.";
export const AREA_REASON_OUTLINE_NOT_POINTS = "The footprint shape is not given as points.";
export const AREA_REASON_OUTLINE_OUT_OF_RANGE =
  "The footprint shape has a point that is out of range.";
export const AREA_REASON_OUTLINE_NO_AREA = "The footprint has no area to show as two zones.";

/** One footprint vertex in the block's placed frame (feet). */
export type AreaPoint = readonly [number, number];

/** The NOT-fitted state: a proportional bar from the block's own share. */
export interface AreaBarView {
  readonly kind: "bar";
  /** round(share * 100) — the one stated percentage, read from the block, never hardcoded. */
  readonly percent: number;
  /** the apartment segment's share of the bar (0.60-0.75); the other segment is the remainder. */
  readonly apartmentFraction: number;
  /** the block's own conversion statement (validated equal to the fixed G-14 text). */
  readonly conversionStatement: string;
}

/**
 * The FITTED state: two zones inside the placed footprint, split by a single
 * vertical division. The geometry is the kernel's own; the component only places
 * and hatches these polygons — it computes no zoning maths.
 */
export interface AreaZonesView {
  readonly kind: "fitted_zones";
  /** round(share * 100) — the one stated percentage, read from the block. */
  readonly percent: number;
  /** the apartment zone's share of the FOOTPRINT area (the drawn proportion). */
  readonly apartmentFraction: number;
  readonly conversionStatement: string;
  /** the x at which the vertical division splits the footprint at the share ratio (feet). */
  readonly divisionX: number;
  /** the division segment's lower/upper y at that x (feet). */
  readonly divisionYLo: number;
  readonly divisionYHi: number;
  /** the de-duplicated exterior ring, and the two zone polygons (feet). */
  readonly ring: readonly AreaPoint[];
  readonly apartmentPolygon: readonly AreaPoint[];
  readonly otherPolygon: readonly AreaPoint[];
  /** the ring's axis-aligned bounds (feet), for the component's placement transform. */
  readonly bounds: {
    readonly minX: number;
    readonly maxX: number;
    readonly minY: number;
    readonly maxY: number;
  };
}

/** A fail-closed state: nothing is drawn; the component shows this plain reason. */
export interface AreaUnavailableView {
  readonly kind: "unavailable";
  readonly reason: string;
}

export type AreaAllocationView = AreaBarView | AreaZonesView | AreaUnavailableView;

function isFiniteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/** True when `value` is a finite number whose magnitude cannot overflow the geometry
 * arithmetic (kernel `_plausible_coord`: rejects NaN, +/-inf, a non-number and an over-large
 * magnitude such as 1e308). */
function plausibleCoord(value: unknown): value is number {
  return isFiniteNumber(value) && Math.abs(value) <= COORD_MAX;
}

// -- geometry (polygon split by a single vertical division at the share ratio) --
// Ported verbatim from kit/area_allocation.py (_poly_area, _clip_x, _division_x);
// double arithmetic is identical under IEEE-754, so the two surfaces split alike.

/** Shoelace area of a closed polygon given as open vertices (kernel `_poly_area`). */
export function polyArea(pts: readonly AreaPoint[]): number {
  let area = 0;
  const n = pts.length;
  for (let i = 0; i < n; i += 1) {
    const [x1, y1] = pts[i];
    const [x2, y2] = pts[(i + 1) % n];
    area += x1 * y2 - x2 * y1;
  }
  return Math.abs(area) / 2;
}

/** Sutherland-Hodgman clip of `pts` against the vertical line x = c, keeping the
 * x <= c side (`keepLeft`) or the x >= c side (kernel `_clip_x`). */
export function clipX(pts: readonly AreaPoint[], c: number, keepLeft: boolean): AreaPoint[] {
  const out: AreaPoint[] = [];
  const n = pts.length;
  for (let i = 0; i < n; i += 1) {
    const cur = pts[i];
    const nxt = pts[(i + 1) % n];
    const curIn = keepLeft ? cur[0] <= c : cur[0] >= c;
    const nxtIn = keepLeft ? nxt[0] <= c : nxt[0] >= c;
    if (curIn) out.push(cur);
    if (curIn !== nxtIn) {
      const t = (c - cur[0]) / (nxt[0] - cur[0]);
      out.push([c, cur[1] + t * (nxt[1] - cur[1])]);
    }
  }
  return out;
}

/** The x at which a vertical line splits `pts` so the area to its left is `share` of
 * the whole. Deterministic bisection, 100 steps (kernel `_division_x`). */
export function divisionX(pts: readonly AreaPoint[], share: number): number {
  const total = polyArea(pts);
  const target = share * total;
  let lo = Math.min(...pts.map((p) => p[0]));
  let hi = Math.max(...pts.map((p) => p[0]));
  for (let i = 0; i < 100; i += 1) {
    const mid = (lo + hi) / 2;
    if (polyArea(clipX(pts, mid, true)) < target) {
      lo = mid;
    } else {
      hi = mid;
    }
  }
  return (lo + hi) / 2;
}

/** The outcome of reading the placed exterior ring (kernel `_placed_ring`). */
type RingResult =
  | { readonly kind: "ring"; readonly points: readonly AreaPoint[] }
  | { readonly kind: "not_placed" }
  | { readonly kind: "invalid"; readonly reason: string };

/**
 * The placed footprint's exterior ring, mirroring the kernel's `_placed_ring`:
 *   • `not_placed` when no outline is placed;
 *   • `invalid` (with the kernel's plain reason) when an outline IS placed but
 *     cannot be drawn truthfully — too many points (F3), a vertex that is not a
 *     finite point of plausible magnitude (F1), or a zero-area ring (F2);
 *   • `ring` with the de-duplicated vertices otherwise.
 */
function placedRing(placement: unknown): RingResult {
  if (!isRecord(placement) || placement.status !== "placed") return { kind: "not_placed" };
  const outline = placement.outline;
  if (!Array.isArray(outline) || outline.length === 0) return { kind: "not_placed" };
  const ring: unknown = outline[0];
  if (!Array.isArray(ring)) return { kind: "not_placed" };
  if (ring.length > MAX_OUTLINE_VERTICES) {
    return { kind: "invalid", reason: AREA_REASON_OUTLINE_TOO_MANY_POINTS }; // F3
  }
  const pts: AreaPoint[] = [];
  for (const vertex of ring) {
    if (!Array.isArray(vertex) || vertex.length < 2) {
      return { kind: "invalid", reason: AREA_REASON_OUTLINE_NOT_POINTS }; // F1
    }
    if (!(plausibleCoord(vertex[0]) && plausibleCoord(vertex[1]))) {
      return { kind: "invalid", reason: AREA_REASON_OUTLINE_OUT_OF_RANGE }; // F1
    }
    pts.push([vertex[0], vertex[1]]);
  }
  let open = pts;
  if (pts.length > 1) {
    const first = pts[0];
    const last = pts[pts.length - 1];
    if (first[0] === last[0] && first[1] === last[1]) open = pts.slice(0, -1);
  }
  if (open.length < 3) return { kind: "not_placed" };
  if (polyArea(open) <= 0) {
    return { kind: "invalid", reason: AREA_REASON_OUTLINE_NO_AREA }; // F2
  }
  return { kind: "ring", points: open };
}

/** Build the fitted two-zone view from a sound share and a drawable placed ring. */
function zonesView(
  share: number,
  conversionStatement: string,
  ring: readonly AreaPoint[],
): AreaZonesView {
  const total = polyArea(ring);
  const c = divisionX(ring, share);
  const apartmentPolygon = clipX(ring, c, true);
  const otherPolygon = clipX(ring, c, false);
  const apartmentFraction = polyArea(apartmentPolygon) / total;

  const xs = ring.map((p) => p[0]);
  const ys = ring.map((p) => p[1]);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);

  // The single division segment's y-extent at the cut (kernel `_draw_zones`).
  const onDivision = apartmentPolygon.filter((p) => Math.abs(p[0] - c) <= 1e-6);
  const divisionYLo = onDivision.length >= 2 ? Math.min(...onDivision.map((p) => p[1])) : minY;
  const divisionYHi = onDivision.length >= 2 ? Math.max(...onDivision.map((p) => p[1])) : maxY;

  return {
    kind: "fitted_zones",
    percent: Math.round(share * 100),
    apartmentFraction,
    conversionStatement,
    divisionX: c,
    divisionYLo,
    divisionYHi,
    ring,
    apartmentPolygon,
    otherPolygon,
    bounds: { minX, maxX, minY, maxY },
  };
}

/**
 * What the AreaAllocation component must draw for one building's `area_allocation`
 * block (and, for the fitted branch, its `placement`). See the module docstring.
 */
export function areaAllocationView(allocation: unknown, placement?: unknown): AreaAllocationView {
  if (!isRecord(allocation)) {
    return { kind: "unavailable", reason: AREA_REASON_MISSING };
  }
  const conversionStatement = allocation.conversion_statement;
  if (
    allocation.label !== ILLUSTRATIVE_LABEL ||
    allocation.measure !== AREA_ALLOCATION_MEASURE ||
    conversionStatement !== AREA_ALLOCATION_CONVERSION_STATEMENT
  ) {
    return { kind: "unavailable", reason: AREA_REASON_INCOMPLETE };
  }
  const share = allocation.share;
  if (!isFiniteNumber(share)) {
    return { kind: "unavailable", reason: AREA_REASON_SHARE_NOT_NUMBER };
  }
  if (share < AREA_ALLOCATION_SHARE_MIN || share > AREA_ALLOCATION_SHARE_MAX) {
    return { kind: "unavailable", reason: AREA_REASON_SHARE_OUT_OF_RANGE };
  }
  const apartment = allocation.apartment_area_sqft;
  const other = allocation.other_area_sqft;
  const total = allocation.total_sqft;
  if (!isFiniteNumber(apartment) || !isFiniteNumber(other) || !isFiniteNumber(total)) {
    return { kind: "unavailable", reason: AREA_REASON_SPLIT_NOT_NUMBERS };
  }
  if (total <= 0 || Math.abs(apartment + other - total) > AREA_TOLERANCE) {
    return { kind: "unavailable", reason: AREA_REASON_TOTAL_MISMATCH };
  }
  if (Math.abs(apartment / total - share) > SHARE_TOLERANCE) {
    return { kind: "unavailable", reason: AREA_REASON_SHARE_MISMATCH };
  }
  const fitted = allocation.fitted;
  if (fitted !== true && fitted !== false) {
    return { kind: "unavailable", reason: AREA_REASON_FITTED_UNKNOWN };
  }
  if (fitted) {
    // A fitted block needs a placed outline the kernel can draw truthfully; otherwise it fails
    // closed with the kernel's own reason (never a bar mislabelled fitted).
    const ring = placedRing(placement);
    if (ring.kind === "not_placed") {
      return { kind: "unavailable", reason: AREA_REASON_NOT_PLACED };
    }
    if (ring.kind === "invalid") {
      return { kind: "unavailable", reason: ring.reason };
    }
    return zonesView(share, conversionStatement, ring.points);
  }
  return {
    kind: "bar",
    percent: Math.round(share * 100),
    apartmentFraction: share,
    conversionStatement,
  };
}
