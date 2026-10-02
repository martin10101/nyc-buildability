/**
 * Presentation model for the lot-choice + site-facts setup surface (queue D-04,
 * plan M1-13, §3 steps 2-3; §5a). It turns a contract-shaped Study
 * (packages/contracts/schemas/v1/study.schema.json, read through the C-05 store)
 * into plain display rows: the lots that make up the site, whether they were
 * combined and why not, the architect's statement, and each site fact with its
 * source label.
 *
 * Boundaries this module keeps:
 * - It reads only what the study already holds. It computes NO geometry and NO
 *   adjacency: whether lots can be combined, and the refusal reason, come from
 *   B-07 through the study's `lot_selection.combination` (served by Lane C). The
 *   web never re-derives that check (lane prompt; plan §3 step 2).
 * - It claims nothing about a verified zoning lot. The statement line is the
 *   contract-pinned owner wording and is always shown.
 * - No legal logic and no measurement is invented here. An unknown value stays
 *   unknown and names what it blocks (plan §9).
 */

import {
  LOT_SELECTION_STATEMENT,
  MEASUREMENT_LABELS,
  type BlockedOutput,
  type SiteFact,
  type Source,
  type Study,
} from "@/lib/study/study-vocabulary";

export interface LotRow {
  bbl: string;
  /** "Lot 32" — the tax-lot number, as the plan lists lots (§3 step 2), not the raw BBL. */
  lotLabel: string;
  sizeText: string;
  sourceLabel: string;
  selected: boolean;
}

export type CombinationStatus = "single_lot" | "offered" | "not_offered";

export interface CombinationView {
  status: CombinationStatus;
  heading: string;
  /** The B-07 refusal reason verbatim when not offered; a plain site line otherwise; null for one lot. */
  detail: string | null;
  refused: boolean;
}

export interface LotChoiceView {
  count: number;
  heading: string;
  pickLine: string;
  lots: LotRow[];
  /** Owner-pinned statement every result carries (plan §3 step 2). */
  statement: string;
  combination: CombinationView;
}

export interface SiteFactRow {
  factId: string;
  label: string;
  valueText: string;
  sourceLabel: string;
  isUnknown: boolean;
  /** Plain-English outputs a still-unknown value blocks (plan §9); empty for a known value. */
  blocks: string[];
  editable: boolean;
  sourceLines: string[];
}

const SITE_FACT_KEY_LABELS: Record<SiteFact["key"], string> = {
  lot_area: "Lot area",
  lot_frontage: "Frontage",
  lot_depth: "Lot depth",
  lot_type: "Lot type",
  zoning_district: "Zoning district",
  commercial_overlay: "Commercial overlay",
  street_width: "Street width",
  existing_zoning_floor_area: "Existing zoning floor area",
};

const BLOCKED_OUTPUT_LABELS: Record<BlockedOutput, string> = {
  floor_area_allowance: "floor-area allowance",
  remaining_floor_area: "remaining capacity",
  permitted_envelope: "permitted envelope",
  building_option: "building option",
  existing_building_paths: "keep / rebuild comparison",
  unit_estimate: "unit estimate",
  geometry: "diagrams",
};

function unitSuffix(unit: SiteFact["unit"]): string {
  if (unit === "square_feet") return " sq ft";
  if (unit === "feet") return " ft";
  return "";
}

function capitalize(word: string): string {
  return word.length ? word[0].toUpperCase() + word.slice(1) : word;
}

/** The human label for one site fact, naming the street for a per-street value. */
export function siteFactLabel(fact: SiteFact): string {
  const base = SITE_FACT_KEY_LABELS[fact.key];
  return fact.street ? `${base} · ${fact.street}` : base;
}

/** The value as shown on the face: a measured number with its unit, a plain word, or "Unknown — enter". */
export function siteFactValueText(fact: SiteFact): string {
  if (fact.measurement.rank === "unknown" || fact.value === null) {
    return MEASUREMENT_LABELS.unknown;
  }
  if (typeof fact.value === "number") {
    return `${fact.value.toLocaleString("en-US")}${unitSuffix(fact.unit)}`;
  }
  return fact.key === "lot_type" ? capitalize(fact.value) : fact.value;
}

/**
 * Source detail lines for the per-fact "Source" disclosure (plan §5a item 4:
 * dataset versions and ids live in details, not on the face). The internal query
 * URL is never surfaced; only architect-meaningful references are.
 */
export function sourceLines(source: Source | null): string[] {
  if (source === null) return ["No source recorded — this value was not found and must be entered."];
  const lines: string[] = [];
  if (source.dataset) {
    lines.push(source.dataset_version ? `${source.dataset} (${source.dataset_version})` : source.dataset);
  }
  if (source.kind === "architect_entry") lines.push("Entered by you.");
  if (source.kind === "assumption" && source.statement) lines.push(source.statement);
  if (source.kind === "survey") lines.push(source.document_ref ? `Survey: ${source.document_ref}` : "Survey.");
  if (source.kind === "city_filing" && source.document_ref) lines.push(`Filing: ${source.document_ref}`);
  if (source.retrieved_at) lines.push(`Recorded ${source.retrieved_at.slice(0, 10)}.`);
  return lines;
}

function blockedLabels(fact: SiteFact): string[] {
  return fact.blocks.map((output) => BLOCKED_OUTPUT_LABELS[output]);
}

/** The tax-lot number from a canonical BBL (last four digits, no padding): display only. */
function lotNumberLabel(bbl: string): string {
  return `Lot ${Number(bbl.slice(6))}`;
}

/** One display row per lot in the lot choice (plan §3 step 2). */
export function lotRows(study: Study): LotRow[] {
  return study.lots.map((lot) => ({
    bbl: lot.bbl,
    lotLabel: lotNumberLabel(lot.bbl),
    sizeText:
      lot.approximate_lot_area_sq_ft === null
        ? "Size unknown"
        : `${lot.approximate_lot_area_sq_ft.toLocaleString("en-US")} sq ft`,
    sourceLabel: MEASUREMENT_LABELS[lot.size_measurement.rank],
    selected: lot.selected,
  }));
}

/**
 * Whether the selected lots were combined, straight from B-07's recorded result (never
 * recomputed). B-07 supplies a `reason` ONLY when the combination is not offered; for an offered
 * or single-lot combination the reason is null. This function therefore makes no geometry,
 * adjacency ("one block", "touch") or verification claim of its own for those cases — it states
 * only what the architect selected. The pinned zoning-lot statement (`lotChoiceView.statement`)
 * carries the "the app does not verify the zoning lot" caveat.
 */
export function combinationView(study: Study): CombinationView {
  const { status, reason } = study.lot_selection.combination;
  if (status === "not_offered") {
    return { status, heading: "These lots were not combined", detail: reason, refused: true };
  }
  if (status === "offered") {
    return { status, heading: "Lots shown together", detail: "These are the lots you selected.", refused: false };
  }
  return { status, heading: "One lot", detail: null, refused: false };
}

/** The full lot-choice view for the panel header (plan §3 step 2). */
export function lotChoiceView(study: Study): LotChoiceView {
  const count = study.lots.length;
  return {
    count,
    heading: `This property has ${count} lot${count === 1 ? "" : "s"}.`,
    pickLine:
      count === 1
        ? "The site is this one lot."
        : "Use all (default), or pick the lots that make up the site.",
    lots: lotRows(study),
    statement: LOT_SELECTION_STATEMENT,
    combination: combinationView(study),
  };
}

/** One display row per site fact, with its source label (plan §3 step 3, §4). */
export function siteFactRows(study: Study): SiteFactRow[] {
  return study.site.facts.map((fact) => {
    const isUnknown = fact.measurement.rank === "unknown";
    return {
      factId: fact.fact_id,
      label: siteFactLabel(fact),
      valueText: siteFactValueText(fact),
      sourceLabel: MEASUREMENT_LABELS[fact.measurement.rank],
      isUnknown,
      blocks: isUnknown ? blockedLabels(fact) : [],
      editable: fact.editable,
      sourceLines: sourceLines(fact.source),
    };
  });
}
