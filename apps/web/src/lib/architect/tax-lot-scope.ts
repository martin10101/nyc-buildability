/**
 * Tax-lot-only scope of the calculated results (owner directive 2026-10-01).
 *
 * Every floor-area and FAR number the app calculates is for ONE tax lot: the one entered. The
 * legal zoning lot can include other tax lots (benchmark 215-16 Northern: a DOB filing describes
 * one zoning lot of tax lots 1 and 70), so the whole-site limit, the room left after existing
 * buildings and the combined lot's rear yard and coverage are not calculated. Until they are,
 * every surface that shows such a number carries a visible warning, and the results carry plain
 * labels. Presentation wording only: this module reads no records, verifies nothing and decides
 * no legal question. The verified variant renders only from a verified zoning-lot fact that a
 * caller passes in; no such fact is wired to the web yet.
 */

/** The label on the floor-area cap value itself (a plain-text line, never a coloured chip). */
export const TAX_LOT_ONLY_ESTIMATE = "Tax-lot-only estimate";

/** The value of every combined-zoning-lot result row the app does not calculate. */
export const NOT_CONFIRMED = "Not confirmed";

/** Row label for the room left after existing buildings (owner wording, D-090-R038). */
export const REMAINING_CAPACITY_LABEL = "Remaining development capacity";

/** The reason line under "Remaining development capacity: Not confirmed" wherever no verified
 * value exists (owner wording, settled 2026-10-01: D-090-R038, DB-101 option A). */
export const REMAINING_CAPACITY_REASON = "Needs verified zoning-lot boundaries and existing zoning floor area.";

const NOT_CALCULATED_YET = "The whole-site limit, the room left after existing buildings, and the combined lot's rear yard and coverage are not calculated yet.";

/** The always-visible warning when no verified zoning-lot fact is supplied. */
export const TAX_LOT_ONLY_WARNING = `These numbers cover only the tax lot you entered. The full zoning lot may include other lots. ${NOT_CALCULATED_YET}`;

/** Result rows for the combined zoning lot. Each reads NOT_CONFIRMED until it is calculated. */
export const ZONING_LOT_ROWS = [
  ["whole-site-capacity", "Whole-site capacity"],
  ["remaining-capacity", REMAINING_CAPACITY_LABEL],
  ["combined-coverage", "Combined zoning lot: coverage"],
  ["combined-rear-yard", "Combined zoning lot: rear yard"],
] as const;

/** The reason line a row shows under its NOT_CONFIRMED value, keyed by row. */
export const ZONING_LOT_ROW_REASONS: Readonly<Partial<Record<(typeof ZONING_LOT_ROWS)[number][0], string>>> = {
  "remaining-capacity": REMAINING_CAPACITY_REASON,
};

/**
 * A VERIFIED zoning-lot fact: every tax lot on the zoning lot and the one tax lot the numbers
 * were calculated for, each as a 10-digit BBL. Callers pass it only from a verified source;
 * a "mentioned" or unconfirmed zoning lot is not one.
 */
export interface VerifiedZoningLot {
  taxLotBbls: readonly string[];
  calculatedBbl: string;
}

const CANONICAL_BBL = /^[1-5]\d{9}$/;

function lotNumber(bbl: string): number {
  return Number(bbl.slice(6));
}

function joinLots(lots: readonly number[]): string {
  return lots.length === 2 ? `${lots[0]} and ${lots[1]}` : `${lots.slice(0, -1).join(", ")}, and ${lots[lots.length - 1]}`;
}

/**
 * The verified zoning lot's tax-lot numbers, or null when the fact is absent or does not hold
 * together for this property: the calculated lot must be the property shown, appear in the list,
 * and every lot must be a distinct canonical BBL on the same block. Fail safe: null falls back to
 * the generic warning, so an incoherent fact never prints specific lot numbers.
 */
export function verifiedZoningLotNumbers(zoningLot: VerifiedZoningLot | null | undefined, bbl: string): { lots: number[]; calculated: number } | null {
  if (!zoningLot || !CANONICAL_BBL.test(bbl) || zoningLot.calculatedBbl !== bbl) return null;
  const listed: unknown = zoningLot.taxLotBbls;
  if (!Array.isArray(listed) || listed.length < 2) return null;
  const block = bbl.slice(0, 6);
  const lots: number[] = [];
  for (const item of listed) {
    if (typeof item !== "string" || !CANONICAL_BBL.test(item) || item.slice(0, 6) !== block || lotNumber(item) === 0) return null;
    lots.push(lotNumber(item));
  }
  const calculated = lotNumber(bbl);
  if (new Set(lots).size !== lots.length || !lots.includes(calculated)) return null;
  return { lots: lots.sort((a, b) => a - b), calculated };
}

/** The warning text for the property `bbl`: the verified variant when a coherent verified
 * zoning-lot fact is supplied, else the generic tax-lot-only warning. */
export function taxLotScopeWarning(bbl: string, zoningLot?: VerifiedZoningLot | null): string {
  const verified = verifiedZoningLotNumbers(zoningLot, bbl);
  return verified
    ? `This zoning lot includes tax lots ${joinLots(verified.lots)}. These numbers use lot ${verified.calculated} only. ${NOT_CALCULATED_YET}`
    : TAX_LOT_ONLY_WARNING;
}
