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
  VERSION_CHECK_LABELS,
  type BlockedOutput,
  type Lot,
  type LotSelection,
  type SiteFact,
  type Source,
  type SourceKind,
  type Study,
} from "@/lib/study/study-vocabulary";
import type { StudySetup } from "@/lib/study/study-setup-api";

/**
 * Short, fact-forward site-facts intro (D-090-R082 "say less"). It names the one
 * thing the architect needs to know — each value shows its source and can be
 * overridden — without the earlier paragraph's restatement.
 */
export const SITE_FACTS_INTRO =
  "Each value shows its source. Enter your own for any fact — it is saved as “Entered” beside the city value.";

/** The plain "not connected yet" copy, worded as a fact (not a caution), for the
 * empty state (route off / no setup). Keeps the honesty that nothing is guessed. */
export const SITE_SETUP_NOT_CONNECTED =
  "The site-facts service is not wired to this screen, so there is nothing to show here. No measurement is guessed.";

/**
 * The display source the panel renders over: the lots, the lot selection (mode +
 * B-07's combination only — the pinned statement is re-applied here) and the site
 * facts. BOTH a full `Study` (read from the C-05 store once an option is
 * confirmed) and a server `StudySetup` (the setup half, before any option exists)
 * reduce to this shape, so the panel shows the same surface either way. Nothing
 * here is computed; it only re-keys the fields.
 */
export interface LotSiteSource {
  lots: Lot[];
  lotSelection: Pick<LotSelection, "mode" | "combination">;
  siteFacts: SiteFact[];
}

export function sourceFromStudy(study: Study): LotSiteSource {
  return { lots: study.lots, lotSelection: study.lot_selection, siteFacts: study.site.facts };
}

export function sourceFromSetup(setup: StudySetup): LotSiteSource {
  return { lots: setup.lots, lotSelection: setup.lotSelection, siteFacts: setup.siteFacts };
}

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

/** The version-check status on a fact's source (site_fact.schema.json#/$defs/version_check). */
type VersionCheckStatus = NonNullable<Source["version_check"]>["status"];

/**
 * The per-fact data-version status for display (site_fact `source.version_check`, contract 1.1.0;
 * plan §5a items 3-4). `label` is the vocabulary constant (never a new literal) and `reason` is the
 * server's plain sentence; the panel always shows the two together in the fact's source details.
 * `onFace` is true ONLY for an out-of-date version — a stale number must never look current, so its
 * short marker shows beside the fact without a tap; "current" and "version_unknown" stay in details.
 * The internal status token and the latest-known query ref are never carried onto the face.
 */
export interface SiteFactVersionView {
  status: VersionCheckStatus;
  label: string;
  reason: string;
  onFace: boolean;
}

/** The version-check view for a fact whose source records one; null when it does not (renders as today). */
export function siteFactVersionViewOf(fact: SiteFact): SiteFactVersionView | null {
  const versionCheck = fact.source?.version_check;
  if (!versionCheck) return null;
  const { status, reason } = versionCheck;
  return { status, label: VERSION_CHECK_LABELS[status], reason, onFace: status === "out_of_date" };
}

export interface SiteFactRow {
  factId: string;
  /** The site_fact key, for a stable display hook and for grouping an entered value with its fact. */
  key: SiteFact["key"];
  label: string;
  valueText: string;
  sourceLabel: string;
  isUnknown: boolean;
  /** Plain-English outputs a still-unknown value blocks (plan §9); empty for a known value. */
  blocks: string[];
  editable: boolean;
  sourceLines: string[];
  /** The fact's data-version status (plan §5a), or null when its source records none. */
  versionCheck: SiteFactVersionView | null;
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
export function lotRowsOf(lots: Lot[]): LotRow[] {
  return lots.map((lot) => ({
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
export function lotRows(study: Study): LotRow[] {
  return lotRowsOf(study.lots);
}

/**
 * Whether the selected lots were combined, straight from B-07's recorded result (never
 * recomputed). B-07 supplies a `reason` ONLY when the combination is not offered; for an offered
 * or single-lot combination the reason is null. This function therefore makes no geometry,
 * adjacency ("one block", "touch") or verification claim of its own for those cases — it states
 * only what the architect selected. The pinned zoning-lot statement (`lotChoiceView.statement`)
 * carries the "the app does not verify the zoning lot" caveat.
 */
export function combinationViewOf(lotSelection: Pick<LotSelection, "combination">): CombinationView {
  const { status, reason } = lotSelection.combination;
  if (status === "not_offered") {
    return { status, heading: "These lots were not combined", detail: reason, refused: true };
  }
  if (status === "offered") {
    return { status, heading: "Lots shown together", detail: "These are the lots you selected.", refused: false };
  }
  return { status, heading: "One lot", detail: null, refused: false };
}
export function combinationView(study: Study): CombinationView {
  return combinationViewOf(study.lot_selection);
}

/** The full lot-choice view for the panel header (plan §3 step 2). */
export function lotChoiceViewOf(source: LotSiteSource): LotChoiceView {
  const count = source.lots.length;
  return {
    count,
    heading: `This property has ${count} lot${count === 1 ? "" : "s"}.`,
    pickLine:
      count === 1
        ? "The site is this one lot."
        : "Use all (default), or pick the lots that make up the site.",
    lots: lotRowsOf(source.lots),
    statement: LOT_SELECTION_STATEMENT,
    combination: combinationViewOf(source.lotSelection),
  };
}
export function lotChoiceView(study: Study): LotChoiceView {
  return lotChoiceViewOf(sourceFromStudy(study));
}

/** One display row per site fact, with its source label (plan §3 step 3, §4). */
export function siteFactRowsOf(facts: SiteFact[]): SiteFactRow[] {
  return facts.map((fact) => {
    const isUnknown = fact.measurement.rank === "unknown";
    return {
      factId: fact.fact_id,
      key: fact.key,
      label: siteFactLabel(fact),
      valueText: siteFactValueText(fact),
      sourceLabel: MEASUREMENT_LABELS[fact.measurement.rank],
      isUnknown,
      blocks: isUnknown ? blockedLabels(fact) : [],
      editable: fact.editable,
      sourceLines: sourceLines(fact.source),
      versionCheck: siteFactVersionViewOf(fact),
    };
  });
}
export function siteFactRows(study: Study): SiteFactRow[] {
  return siteFactRowsOf(study.site.facts);
}

export interface SiteFactGroup {
  /** The city/original (or standalone) value row. */
  primary: SiteFactRow;
  /** The architect's "Entered" value shown beside the primary, when one was recorded. */
  entered: SiteFactRow | null;
}

const ENTERED_SUFFIX = "-entered";

/**
 * Group an entered value with the fact it edits, so the city value stays visible BESIDE the entered
 * one (plan §4). An entered fact carries the id "<fact_id>-entered" (study-operations.ts
 * enterSiteFactValue, and the setup-only mirror below); it is grouped under its base only when the
 * base fact is also present. A standalone "-entered" id, or any server fact, is its own primary.
 * Groups keep each base's first appearance order (the entered fact is always appended after its
 * base, so the base is seen first).
 */
export function groupSiteFactRows(rows: SiteFactRow[]): SiteFactGroup[] {
  const ids = new Set(rows.map((row) => row.factId));
  const order: string[] = [];
  const groups = new Map<string, SiteFactGroup>();
  for (const row of rows) {
    const isEntered =
      row.factId.endsWith(ENTERED_SUFFIX) && ids.has(row.factId.slice(0, -ENTERED_SUFFIX.length));
    const base = isEntered ? row.factId.slice(0, -ENTERED_SUFFIX.length) : row.factId;
    let group = groups.get(base);
    if (!group) {
      group = { primary: row, entered: null };
      groups.set(base, group);
      order.push(base);
    }
    if (isEntered) group.entered = row;
    else group.primary = row;
  }
  return order.map((base) => groups.get(base)!);
}

/**
 * The unit site_fact.schema.json ties to each key. This MIRRORS study-operations.ts
 * SITE_FACT_KEY_UNITS, which the C-05 store uses when a study exists; it is duplicated here ONLY
 * for the setup-only working copy (no study, so no store operation to call). It is contract
 * reference data, not a computation. The test cross-checks an entered fact against the real
 * enterSiteFactValue so the two can never drift silently.
 */
const SITE_FACT_KEY_UNITS: { readonly [K in SiteFact["key"]]: SiteFact["unit"] } = {
  lot_area: "square_feet",
  lot_frontage: "feet",
  lot_depth: "feet",
  street_width: "feet",
  existing_zoning_floor_area: "square_feet",
  lot_type: null,
  zoning_district: null,
  commercial_overlay: null,
};

/** Source kinds that are a city value (mirrors study-operations.ts CITY_SOURCE_KINDS): a city value
 * is never overwritten in place — an edit ADDS an "entered" fact beside it (site_fact `editable`). */
const CITY_SOURCE_KINDS: readonly SourceKind[] = ["city_dataset", "city_filing", "tax_map_computation"];

function isCityFact(fact: SiteFact): boolean {
  return fact.source !== null && CITY_SOURCE_KINDS.includes(fact.source.kind);
}

export type FactInputResult =
  | { ok: true; value: number | string }
  | { ok: false; reason: string };

/** Plain, shared input messages (no internal code). Exported so the step-4 existing-building
 * entry (./existing-building-view) rejects a bad floor area with the SAME words as a per-fact edit. */
export const ENTER_VALUE_FIRST = "Enter a value first.";
export const ENTER_POSITIVE_NUMBER = "Enter a number greater than zero.";

/**
 * Validate the architect's typed value for one fact, in plain words with no internal code. No value
 * is computed: a measured key (square feet / feet) must be a number greater than zero; lot type must
 * be one of the three plain words; a district or overlay must be non-empty text. The contract (and,
 * for a real study, the store's own validation) remains the final guard.
 */
export function validateFactInput(fact: SiteFact, raw: string): FactInputResult {
  const trimmed = raw.trim();
  if (trimmed === "") return { ok: false, reason: ENTER_VALUE_FIRST };
  const unit = SITE_FACT_KEY_UNITS[fact.key];
  if (unit === "square_feet" || unit === "feet") {
    const value = Number(trimmed);
    if (!Number.isFinite(value) || value <= 0) {
      return { ok: false, reason: ENTER_POSITIVE_NUMBER };
    }
    return { ok: true, value };
  }
  if (fact.key === "lot_type") {
    const word = trimmed.toLowerCase();
    if (word !== "corner" && word !== "interior" && word !== "through") {
      return { ok: false, reason: "Enter one of: corner, interior or through." };
    }
    return { ok: true, value: word };
  }
  return { ok: true, value: trimmed };
}

export type FactEditResult =
  | { ok: true; source: LotSiteSource }
  | { ok: false; reason: string };

/**
 * Record a value on a setup-only working source (no study/store yet). It MIRRORS
 * study-operations.ts enterSiteFactValue for the no-study case: the value becomes a fact at rank
 * "entered" sourced to the architect; a CITY value is kept and the entered value is added BESIDE it
 * under "<fact_id>-entered"; a non-city value (an earlier entry, or an unknown placeholder) is
 * replaced in place. The key, unit, lot and street are the edited fact's — nothing is computed. When
 * a real study exists the panel calls enterSiteFactValue itself, so this path is the working copy
 * only.
 */
export function applyEnteredFactToSource(
  source: LotSiteSource,
  factId: string,
  value: number | string,
  at: string,
): FactEditResult {
  const existing = source.siteFacts.find((fact) => fact.fact_id === factId);
  if (!existing) return { ok: false, reason: "That value is not part of this site." };
  const entered: SiteFact = {
    contract_version: existing.contract_version,
    fact_id: isCityFact(existing) ? `${existing.fact_id}${ENTERED_SUFFIX}` : existing.fact_id,
    key: existing.key,
    lot_bbl: existing.lot_bbl,
    street: existing.street,
    value,
    unit: SITE_FACT_KEY_UNITS[existing.key],
    measurement: { rank: "entered", label: MEASUREMENT_LABELS.entered },
    source: {
      kind: "architect_entry",
      dataset: null,
      dataset_version: null,
      retrieved_at: at,
      query_ref: null,
      document_ref: null,
      statement: null,
    },
    blocks: [],
    editable: true,
  };
  return { ok: true, source: withSiteFact(source, entered) };
}

/**
 * Replace the site fact with the same `fact_id` on a setup-only working source, or append it when
 * none matches. Pure (no clock, no store): the caller builds the fully-formed, contract-shaped fact
 * (./existing-building-view does, for the step-4 existing-building value). When a study exists the
 * panel calls the store's upsertSiteFact instead; this is the no-study working-copy mirror.
 */
export function withSiteFact(source: LotSiteSource, fact: SiteFact): LotSiteSource {
  const index = source.siteFacts.findIndex((existing) => existing.fact_id === fact.fact_id);
  const siteFacts =
    index >= 0
      ? source.siteFacts.map((existing, position) => (position === index ? fact : existing))
      : [...source.siteFacts, fact];
  return { ...source, siteFacts };
}

// ---------------------------------------------------------------------------
// §5a face-text budget (D-090-R082 "say less, show exact information"). A pure
// measure the tests assert against: the app's own standing copy on the results
// face stays short, and the face carries at most three notice blocks (§5a item
// 6). The owner-pinned zoning-lot statement and B-07's verbatim refusal reason
// are shown exactly and are listed separately, exempt from the length budget.
// Lot numbers, sizes, source labels and fact values are pass-through data.
// ---------------------------------------------------------------------------

/** A single readable fact line at the §5a 14 px floor fits roughly this many
 * characters before it wraps into the "long paragraph" R082 forbids. */
export const FACE_TEXT_MAX_CHARS = 140;

export interface FaceTextBudget {
  /** App-authored standing strings shown on the results face (NOT behind <details>);
   * each must be <= FACE_TEXT_MAX_CHARS. */
  readonly appStrings: string[];
  /** Verbatim owner-pinned / source-verbatim strings on the face (shown exactly by
   * design, so exempt from the length budget). */
  readonly pinned: string[];
  /** Standing notice blocks on the face (<= 3, §5a item 6): the combination note
   * and the pinned zoning-lot statement. */
  readonly noticeCount: number;
}

/**
 * The lot & site setup panel's face-text budget. The app-authored face copy is the
 * two section leads (the lot-choice heading + pick line and the site-facts intro)
 * and the combination heading; the pinned zoning-lot statement and — when the
 * combination is refused — B-07's verbatim reason are exempt. Two standing notice
 * blocks sit on the face: the combination note and the pinned statement.
 */
export function lotSiteSetupFaceBudget(source: LotSiteSource): FaceTextBudget {
  const choice = lotChoiceViewOf(source);
  const appStrings: string[] = [choice.heading, choice.pickLine, choice.combination.heading, SITE_FACTS_INTRO];
  const pinned: string[] = [choice.statement];
  if (choice.combination.detail) {
    // A refused combination carries B-07's reason verbatim (pinned/source text); an
    // offered/single-lot detail is the app's own short line and is length-budgeted.
    (choice.combination.refused ? pinned : appStrings).push(choice.combination.detail);
  }
  return { appStrings, pinned, noticeCount: 2 };
}
