/**
 * Presentation view-model for the parity panel — "Comparable sales & floor area"
 * (queue D-15, plan §11b, queue item B-11). Pure: it reshapes an
 * already-validated `ParityData` (the v1 wiring contract, verified by the lane C
 * adapter `parity-api.ts`) into the rows the panel renders. It carries NO legal
 * meaning and computes NOTHING: no average, no price-per-square-foot, no estimate
 * and no remaining-capacity number ever appears. The recorded sale price and date
 * are the publisher's OWN recorded fields, surfaced verbatim (never derived).
 *
 * §5a rules this model serves:
 *  - item 1/6: one status strip of at most three short items (`parityStripSummary`);
 *  - item 3: remaining development capacity cannot be calculated here, so the
 *    unused-floor-area block shows the owner-settled "Not confirmed" line and its
 *    reason IN PLACE OF a number — never a number with a caution label, never a
 *    digit (the sourced existing-floor-area detail, which carries figures, is NOT
 *    surfaced in this slice);
 *  - item 5: no internal code reaches the face — the BBL, block/lot, DOF
 *    source-id / dataset-id / request-url tokens, the raw exclusion-reason token
 *    and contract keys never become visible text here (the exclusion reason is
 *    mapped to plain words; the dataset provenance is surfaced only inside the
 *    "Source" disclosure, §5a item 4 "details").
 *
 * The disclosed "similar type and size" selection filter is an OPEN owner question
 * (B-11). This layer SHOWS it verbatim (`criteria_text` and the pinned
 * `not_a_valuation` notice, both carried by the contract) and never decides or
 * changes it.
 */

import { boundedText } from "@/lib/bounded";
import {
  NOT_A_VALUATION_NOTICE,
  NOT_CONFIRMED_LABEL,
  NOT_CONFIRMED_REASON,
  type ParityData,
} from "@/lib/parity-api";

/** §5a items 1 and 6: at most three items on the one status strip. */
export const PARITY_STRIP_LIMIT = 3;

/** The plain explanation the one status strip opens on tap (§5a item 1). It only
 * says what the strip counts mean; the honesty disclosures live in their own
 * sections, never repeated here (§5a item 2). */
export const STRIP_DETAIL_NOTE =
  "This shows how many recorded sales matched the disclosed filter, how many were left out, and " +
  "the remaining-capacity status. The details for each are below.";

/** The plain "not connected yet" copy for a 404 (the read route is not mounted / the
 * feature flag is off on the server), mirroring the D-12 slice. */
export const PARITY_NOT_CONNECTED =
  "The comparable-sales and floor-area data for this property is prepared by the data service. " +
  "That service is not connected to this screen yet, so there is nothing to show here. Nothing is " +
  "guessed, and no value is presented as confirmed.";

/** Each stable exclusion-reason token in plain words (the raw token is an internal
 * code and never reaches the screen, §5a item 5). Keyed by the contract enum. */
export const EXCLUDED_REASON_TEXT: Readonly<Record<string, string>> = {
  subject_lot: "This is the subject lot itself.",
  zero_price_transfer: "A $0 sale (a transfer without cash, per city records), not a market sale.",
  different_building_class_category: "A different recorded building type.",
  no_recorded_gross_floor_area: "No recorded floor area to size-match.",
  gross_floor_area_out_of_range: "Recorded floor area outside the disclosed size range.",
};

/** One selected recorded sale as the panel renders it. Every field is the
 * publisher's own recorded value, surfaced verbatim; nothing is derived. */
export interface SaleRowView {
  /** React/data-testid key only — NEVER shown (the BBL is an internal token). */
  readonly key: string;
  readonly address: string;
  /** The publisher's recorded sale price, comma-grouped; null when not recorded. */
  readonly recordedPrice: string | null;
  readonly saleDate: string;
}

/** One excluded candidate, shown only inside the "details" disclosure. */
export interface ExcludedRowView {
  readonly key: string;
  readonly address: string;
  readonly saleDate: string;
  /** The exclusion reason in plain words (never the raw token). */
  readonly reasonText: string;
}

/** The DOF provenance, shown only inside the "Source" disclosure (§5a item 4). */
export interface SourceView {
  readonly dataset: string;
  readonly datasetId: string;
  readonly requestUrl: string;
  readonly retrievedAt: string;
  readonly vintage: string | null;
}

export interface ComparableSalesView {
  readonly notAValuation: string;
  readonly criteriaText: string;
  readonly selected: SaleRowView[];
  readonly excluded: ExcludedRowView[];
  readonly source: SourceView | null;
}

export interface UnusedFloorAreaView {
  readonly label: string;
  readonly reason: string;
}

export interface ParityStripSummary {
  readonly items: string[];
}

const ADDRESS_FALLBACK = "Address not recorded";
const DATE_FALLBACK = "Sale date not recorded";

/** Comma-group the publisher's recorded integer price verbatim. This is display
 * formatting of a recorded fact, NOT a computed value; null stays null. */
export function formatRecordedPrice(value: number | null): string | null {
  if (typeof value !== "number" || !Number.isFinite(value)) return null;
  return `$${Math.trunc(value).toLocaleString("en-US")}`;
}

export function comparableSalesView(data: ParityData): ComparableSalesView {
  const comps = data.comparable_sales;
  const selected: SaleRowView[] = comps.selected.map((sale, index) => ({
    key: `sale-${index}`,
    address: boundedText(sale.address, ADDRESS_FALLBACK),
    recordedPrice: formatRecordedPrice(sale.sale_price),
    saleDate: boundedText(sale.sale_date, DATE_FALLBACK),
  }));
  const excluded: ExcludedRowView[] = comps.excluded.map((candidate, index) => ({
    key: `excluded-${index}`,
    address: boundedText(candidate.address, ADDRESS_FALLBACK),
    saleDate: boundedText(candidate.sale_date, DATE_FALLBACK),
    reasonText: EXCLUDED_REASON_TEXT[candidate.reason] ?? "Not selected by the disclosed filter.",
  }));
  const source = comps.source;
  return {
    notAValuation: boundedText(comps.not_a_valuation, NOT_A_VALUATION_NOTICE),
    criteriaText: boundedText(comps.criteria_text, ""),
    selected,
    excluded,
    source: source
      ? {
          dataset: boundedText(source.dataset, "Recorded city dataset"),
          datasetId: boundedText(source.dataset_id, ""),
          requestUrl: boundedText(source.request_url, ""),
          retrievedAt: boundedText(source.retrieved_at, ""),
          vintage: source.dataset_last_modified ? boundedText(source.dataset_last_modified, "") : null,
        }
      : null,
  };
}

/** The unused-floor-area block: ONLY the owner-settled wording (D-090-R038),
 * in place of a number (§5a item 3). The contract's `detail` line carries the
 * sourced existing-floor-area figure; it is deliberately NOT surfaced in this
 * slice, so this block never shows a digit and never claims a verified zoning lot. */
export function unusedFloorAreaView(data: ParityData): UnusedFloorAreaView {
  const unused = data.unused_floor_area;
  return {
    label: boundedText(unused.label, NOT_CONFIRMED_LABEL),
    reason: boundedText(unused.reason, NOT_CONFIRMED_REASON),
  };
}

/** The one §5a status strip: at most three short items. */
export function parityStripSummary(data: ParityData): ParityStripSummary {
  const selectedCount = data.comparable_sales.selected.length;
  const excludedCount = data.comparable_sales.excluded.length;
  const items: string[] = [
    `${selectedCount} recorded ${selectedCount === 1 ? "sale" : "sales"}`,
    "Remaining capacity: Not confirmed",
  ];
  if (excludedCount > 0) {
    items.push(`${excludedCount} not included`);
  }
  return { items: items.slice(0, PARITY_STRIP_LIMIT) };
}
