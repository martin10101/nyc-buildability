import { validateBblInput } from "@/lib/bbl";
export const WORKSPACE_VIEWS = ["overview", "facts", "zoning", "scenarios", "proposal", "evidence", "documents", "issues", "report", "envelope", "units", "financials"] as const;
export type WorkspaceView = (typeof WORKSPACE_VIEWS)[number];
export const VIEW_LABELS: Record<WorkspaceView, string> = {
    overview: "Overview", facts: "Property facts", zoning: "Zoning", scenarios: "Scenarios",
    proposal: "Proposal editor",
    evidence: "Evidence", documents: "Documents", issues: "Open issues", report: "Report",
    envelope: "Envelope", units: "Units", financials: "Financials",
};
export function readWorkspaceView(raw: string | null): WorkspaceView {
    return WORKSPACE_VIEWS.includes(raw as WorkspaceView) ? raw as WorkspaceView : "overview";
}
export function propertyHref(bbl?: string | null, view: WorkspaceView = "overview"): string {
    const validated = validateBblInput(bbl ?? "");
    if (!validated.ok)
        return "/property?ruleeval=on";
    return `/property?ruleeval=on&bbl=${validated.canonical}&view=${view}`;
}
