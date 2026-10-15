/**
 * The two-zone area-allocation selector (M5-T187; D-094 R087-R098, G-14).
 *
 * Reads ONE 1.5.0 `area_allocation` block (and, for the fitted branch, the
 * building's optional `placement`) and returns what the AreaAllocation component
 * must draw. It mirrors the accepted PDF drawing kernel in words and behaviour
 * (services/api/app/drawings/kit/area_allocation.py, M5-T183):
 *
 *   • a sound, NOT-fitted block  -> a proportional bar split by the apartment
 *     share, with exactly one stated percentage round(share * 100) (R094);
 *   • a sound, FITTED block whose placement is placed with an outline -> the
 *     zones-in-footprint path, which THIS part defers (the component renders a
 *     marked placeholder; Part B / M5-T173 draws the zones in lockstep with the
 *     PDF, so the website never shows an illustration the PDF lacks — R096);
 *   • anything else fails CLOSED to an explicit `unavailable` with a plain reason
 *     — never a guessed bar (no default stands for a fact):
 *       a garbled block, a non-numeric or out-of-range share, an apartment/other
 *       split that does not reconcile with the total or with the share, an
 *       unstated `fitted` flag, or a fitted block with no placed outline.
 *
 * The reason strings are byte-equal to the kernel's so the two surfaces explain a
 * refusal in the same words. No legal meaning and no zoning maths live here: the
 * block carries its own pre-computed share and areas; this selector never
 * recomputes a figure and never invents one.
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

/** The FITTED state, deferred in this part: the zones-in-footprint illustration lands with M5-T173. */
export interface AreaFittedDeferredView {
  readonly kind: "fitted_deferred";
}

/** A fail-closed state: nothing is drawn; the component shows this plain reason. */
export interface AreaUnavailableView {
  readonly kind: "unavailable";
  readonly reason: string;
}

export type AreaAllocationView = AreaBarView | AreaFittedDeferredView | AreaUnavailableView;

function isFiniteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/** True when `placement` is placed and carries a ring of at least three finite coordinate pairs.
 * This part does not draw the zones, so it only decides WHETHER a drawable outline exists; the full
 * geometry fail-closed (vertex caps, coordinate magnitude, zero area) binds to Part B's drawing. */
function hasPlacedOutline(placement: unknown): boolean {
  if (!isRecord(placement) || placement.status !== "placed") return false;
  const outline = placement.outline;
  if (!Array.isArray(outline) || outline.length === 0) return false;
  const ring = outline[0];
  if (!Array.isArray(ring)) return false;
  const points = ring.filter(
    (vertex): vertex is readonly [number, number] =>
      Array.isArray(vertex) &&
      vertex.length >= 2 &&
      isFiniteNumber(vertex[0]) &&
      isFiniteNumber(vertex[1]),
  );
  if (points.length !== ring.length) return false;
  const first = points[0];
  const last = points[points.length - 1];
  const open =
    points.length > 1 && first[0] === last[0] && first[1] === last[1]
      ? points.slice(0, -1)
      : points;
  return open.length >= 3;
}

/**
 * What the AreaAllocation component must draw for one building's `area_allocation`
 * block (and, for the fitted branch, its `placement`). See the module docstring.
 */
export function areaAllocationView(
  allocation: unknown,
  placement?: unknown,
): AreaAllocationView {
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
    // A fitted block needs a placed outline; without one the kernel fails closed (never a bar
    // mislabelled fitted). With one, the zones-in-footprint drawing is deferred to Part B.
    return hasPlacedOutline(placement)
      ? { kind: "fitted_deferred" }
      : { kind: "unavailable", reason: AREA_REASON_NOT_PLACED };
  }
  return {
    kind: "bar",
    percent: Math.round(share * 100),
    apartmentFraction: share,
    conversionStatement,
  };
}
