/**
 * Plan §5a ("Label on the box") for the single-page dashboard (queue D-03, M1-17): the one
 * status strip, the notices behind it and the plain "Not available — <reason>" lines.
 * Presentation only. It rewords statuses the existing guards already computed
 * (`@/lib/architect/development-limits`) and never decides a legal or numeric result.
 */
import type { PropertyProfile } from "@/lib/contract";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import type { ResidentialReference } from "@/lib/architect/development-limits";
import type { CondoSurfaceDecision } from "../CondoRecordsSection";
import type { DashboardTool } from "./types";

/** Plan §5a items 1 and 6: at most three items on the strip and three notices on screen. */
export const STRIP_LIMIT = 3;

/** Plan §5a item 2, worded exactly as the plan requires. No records lookup is made. */
export const FLOOR_AREA_REMINDER = "Make sure this floor area is available for use. Confirm with the owner or developer that none of it was sold or merged with another lot.";
export const NOT_AN_APPROVAL = "This is not a Buildings Department approval.";
export const DISTRICT_INCOMPLETE = "The rules for this zoning district are not complete in the app yet, so some limits are not calculated.";
export const DRAFT_RULES_NOTE = "These numbers come from draft rules that a qualified reviewer has not approved yet.";
export const WITHHELD_NOTE = "Results are withheld until the site is confirmed.";
export const MEASUREMENTS_NOTE = "Lot measurements come from city records, not a survey.";

/** Plan §5a items 1 and 3: the visible mark on the draft-rule numbers (cap and FAR). It is the
 * first strip item whenever such a number is shown, never beside the number (D-05 marks its
 * results heading the same way). */
export const DRAFT_MARK = "Draft — not reviewed";

export const SITE_REVIEW_REASON = "the site needs review first";
export const NO_RESULTS_REASON = "no rule results for this property";
export const LOADING_REASON = "the results are still loading";
export const OTHER_PROPERTY_REASON = "the results belong to another property";
export const SCENARIO_MISMATCH_REASON = "the scenario belongs to another property";
export const RULE_DETAILS_REASON = "the rule details are incomplete";

export function notAvailable(reason: string): string {
  return `Not available — ${reason}`;
}

/** Plan §3 step 2. Lot choice is not built yet (queue D-04), so a single lot is "the lot you entered". */
export function zoningLotNotice(multiLot: boolean): string {
  return `Based on the ${multiLot ? "lots on record" : "lot you entered"} — the app does not verify the zoning lot.`;
}

// Plain reasons for the statuses `calculationStatus` returns (its text is shared with the
// multi-page screen, so it is reworded here rather than changed there). Failure labels not
// listed are already plain English and are used as they are.
const CALCULATION_REASONS: Record<string, string> = {
  "Draft assessment": "not calculated for this property yet",
  "Property identity mismatch": OTHER_PROPERTY_REASON,
  "Analysis records differ": "the rule and scenario records do not match",
  "Rule details incomplete": RULE_DETAILS_REASON,
  "Rule result unavailable": "the rule result is unavailable",
  "Scenario integrity check failed": "the scenario check failed",
  "Rule source support incomplete": "the rule sources are incomplete",
  "Conflicting results": "the results conflict",
};

export function calculationReason(status: string): string {
  const head = status.split(" · ")[0];
  return CALCULATION_REASONS[head] ?? head.charAt(0).toLowerCase() + head.slice(1);
}

const BULK_REASONS: Record<string, string> = {
  "Conflicting results": "the results conflict",
  "Conflicting records": "the records conflict",
  "Not supported": "not supported for this property yet",
  "Review required": "needs professional review",
  "Not calculated": "not calculated yet",
};

export function bulkReason(status: string): string {
  return BULK_REASONS[status] ?? calculationReason(status);
}

const REFERENCE_REASONS: Record<ResidentialReference["status"], string> = {
  "City reference": "not in city records",
  Unknown: "not in city records",
  "Conflicting records": "city records disagree",
  "Source value unavailable": "the city record has no usable value",
};

export function referenceReason(status: ResidentialReference["status"]): string {
  return REFERENCE_REASONS[status];
}

/** Why the entry passes the panels no rule results, or null when the panels' own guard status
 * applies. Results still loading, or returned for another property, are never "no rule results". */
export function analysisReason({ loading, evaluationMismatch, scenarioMismatch, evaluationIncomplete }: {
  loading: boolean; evaluationMismatch: boolean; scenarioMismatch: boolean; evaluationIncomplete: boolean;
}): string | null {
  if (evaluationMismatch) return OTHER_PROPERTY_REASON;
  if (scenarioMismatch) return SCENARIO_MISMATCH_REASON;
  if (evaluationIncomplete) return RULE_DETAILS_REASON;
  return loading ? LOADING_REASON : null;
}

export interface DashboardNotice { text: string; tool: DashboardTool }

function plural(count: number, noun: string): string {
  return `${count} ${noun}${count === 1 ? "" : "s"}`;
}

/** Exceptions that need the architect's attention. Missing inputs that neither block a
 * calculation nor affect feasibility stay in the "Items to review" tool (plan §5a item 4). */
export function dashboardNotices(profile: PropertyProfile, condo: CondoSurfaceDecision, evaluation: RuleEvaluation | null): DashboardNotice[] {
  const notices: DashboardNotice[] = [];
  const conflicts = profile.conflicts.filter(item => item.resolution === "unresolved").length;
  const missing = profile.missing_inputs.filter(item => item.criticality === "critical" || item.feasibility_relevant === true);
  const critical = missing.filter(item => item.criticality === "critical").length;
  if (condo.withholdAllowances) notices.push({ text: "Site definition needs review", tool: "records" });
  if (condo.conflict) notices.push({ text: "Condo records disagree", tool: "records" });
  if (conflicts) notices.push({ text: `${plural(conflicts, "record conflict")} to resolve`, tool: "issues" });
  if (missing.length) notices.push({ text: `${plural(missing.length, "missing input")}${critical ? ` (${critical} critical)` : ""}`, tool: "issues" });
  if (profile.reproducibility?.staleness?.stale) notices.push({ text: "Property records out of date", tool: "evidence" });
  if (profile.spatial_intersection?.professional_review_required || profile.lot_geometry?.review_required) notices.push({ text: "Lot outline needs professional review", tool: "zoning" });
  if (evaluation?.wide_street?.determination_state === "professional_review_required") notices.push({ text: "Street width needs professional review", tool: "zoning" });
  return notices;
}

export interface DashboardStatus {
  /** The strip line: exactly STRIP_LIMIT short items. */
  items: string[];
  /** What the strip items mean, shown behind the strip. */
  notes: string[];
  /** Plan §5a item 2: always behind the strip, never beside a number. */
  standing: string[];
}

export function dashboardStatus({ withheld, calculated, multiLot, baseLots }: {
  withheld: boolean; calculated: boolean; multiLot: boolean; baseLots: number;
}): DashboardStatus {
  // Fail safe: a shown draft number always carries the draft mark, whatever else is set.
  const basis = calculated ? DRAFT_MARK : withheld ? "Results withheld" : "Zoning maximum not available";
  const lots = multiLot ? plural(baseLots, "lot") + " on record" : "Lot you entered";
  const notes = [calculated ? DRAFT_RULES_NOTE : withheld ? WITHHELD_NOTE : null, MEASUREMENTS_NOTE].filter((note): note is string => note !== null);
  return {
    // Not trimmed: a fourth item must fail the strip test, not vanish silently.
    items: [basis, "City-record measurements", lots],
    notes,
    standing: [NOT_AN_APPROVAL, FLOOR_AREA_REMINDER, zoningLotNotice(multiLot), DISTRICT_INCOMPLETE],
  };
}
