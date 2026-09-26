import { validateBblInput } from "@/lib/bbl";

export const DASHBOARD_TOOLS = ["map", "facts", "zoning", "scenarios", "proposal", "evidence", "documents", "issues", "report", "records", "study", "envelope", "units", "financials"] as const;
export type DashboardTool = (typeof DASHBOARD_TOOLS)[number];
export const TOOL_LABELS: Record<DashboardTool, string> = {
  map: "Property map", facts: "Property facts", zoning: "Zoning & development limits",
  scenarios: "Scenarios", proposal: "Proposal editor", evidence: "Evidence & sources",
  documents: "Plans & documents", issues: "Items to review", report: "Property report",
  records: "Condo & parcel records", study: "Parcel study", envelope: "Preliminary envelope",
  units: "Unit estimate", financials: "Financials",
};
export function readDashboardTool(value: string | null): DashboardTool | null {
  return DASHBOARD_TOOLS.includes(value as DashboardTool) ? value as DashboardTool : null;
}
export function dashboardHref(bbl?: string | null): string {
  const valid = validateBblInput(bbl ?? "");
  return `/property/workspace?ruleeval=on${valid.ok ? `&bbl=${valid.canonical}` : ""}`;
}
