import { validateBblInput } from "@/lib/bbl";

export const DASHBOARD_TOOLS = ["map", "facts", "lotsite", "zoning", "scenarios", "proposal", "evidence", "documents", "issues", "hiddenissues", "parity", "report", "results", "records", "study", "envelope", "units", "financials"] as const;
export type DashboardTool = (typeof DASHBOARD_TOOLS)[number];
export const TOOL_LABELS: Record<DashboardTool, string> = {
  map: "Property map", facts: "Property facts", lotsite: "Lot & site setup",
  zoning: "Zoning & development limits",
  scenarios: "Scenarios", proposal: "Proposal editor", evidence: "Evidence & sources",
  documents: "Plans & documents", issues: "Items to review", hiddenissues: "Hidden issues",
  parity: "Comparable sales & floor area",
  report: "Property report",
  results: "Results",
  records: "Condo & parcel records", study: "Parcel study", envelope: "Preliminary envelope",
  units: "Unit estimate", financials: "Financials",
};
/** One plain-English line per floating tool window (queue D-03, plan §5a item 5): it names what
 * the opened detail surface shows, in plain words with no internal codes. It is the window's
 * own description; it never repeats a status-strip notice (plan §5a item 2). */
export const TOOL_DESCRIPTIONS: Record<DashboardTool, string> = {
  map: "The lot and its surroundings on the map.",
  facts: "Recorded lot and building facts, each with its source.",
  lotsite: "The lots that make up the site, and each site fact with its source.",
  zoning: "The zoning districts and the development limits they set.",
  scenarios: "The worked scenario behind these development limits.",
  proposal: "A preliminary proposal and envelope check.",
  evidence: "The sources and calculation steps behind these numbers.",
  documents: "Plans and documents for this property.",
  issues: "Items to review before relying on these numbers.",
  hiddenissues: "Hidden issues and opportunities that are easy to miss, each with its check result.",
  parity: "Recorded comparable sales, and the remaining floor-area status.",
  report: "A preview of the property report.",
  results: "The development results for this property, each shown as settled, conditional or not known.",
  records: "Condo and parcel records for this lot.",
  study: "Study the recorded parcels together or separately.",
  envelope: "A preliminary envelope check.",
  units: "An early unit-count estimate.",
  financials: "Early financial figures.",
};
export function readDashboardTool(value: string | null): DashboardTool | null {
  return DASHBOARD_TOOLS.includes(value as DashboardTool) ? value as DashboardTool : null;
}
export function dashboardHref(bbl?: string | null): string {
  const valid = validateBblInput(bbl ?? "");
  return `/property/workspace?ruleeval=on${valid.ok ? `&bbl=${valid.canonical}` : ""}`;
}
