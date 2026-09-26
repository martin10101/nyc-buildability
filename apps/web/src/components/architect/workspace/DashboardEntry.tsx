"use client";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useRef, useState, type MouseEvent } from "react";
import { validateBblInput } from "@/lib/bbl";
import { useProperty } from "@/lib/architect/use-property";
import { useAnalysis } from "@/lib/architect/use-analysis";
import { recalledAddress, type SelectedAddress } from "@/lib/architect/selected-address";
import { evaluationIsInspectable } from "@/lib/architect/development-limits";
import { announcementForOutcome } from "@/lib/announce";
import { announcementForRuleEvaluation } from "@/lib/rule-evaluation";
import { useCondoRecords } from "@/lib/condo-records";
import type { PropertyProfile } from "@/lib/contract";
import { InternalBanner } from "@/components/property/InternalBanner";
import { OutcomeAnnouncer } from "@/components/property/OutcomeAnnouncer";
import { OutcomeFailureStates } from "@/components/property/FailureState";
import { ScenarioFailureStates } from "@/components/compare/ScenarioFailureStates";
import { RuleEvaluationFailure } from "@/components/rule-evaluation/RuleEvaluationFailure";
import { AnalysisIdentityNotice } from "../AnalysisIdentityNotice";
import { IncompleteEvaluationNotice } from "../DevelopmentLimits";
import { CapturedRecord } from "../EvidenceRecord";
import { deriveCondoSurface } from "../CondoRecordsSection";
import { DashboardSearch } from "./DashboardSearch";
import { DashboardPanels } from "./DashboardPanels";
import { DashboardMap } from "./DashboardMap";
import { DashboardTools } from "./DashboardTools";
import { FloatingWorkspaceWindow } from "./FloatingWorkspaceWindow";
import { DASHBOARD_TOOLS, TOOL_LABELS, dashboardHref, readDashboardTool, type DashboardTool } from "./types";

const PERSISTENT_TOOLS: readonly DashboardTool[] = ["map", "facts", "proposal", "study", "evidence", "documents"];

function LoadedDashboard({ profile, initialTool, surveyEnabled, addressRevision, onSelect }: {
  profile: PropertyProfile; initialTool: DashboardTool | null; surveyEnabled: boolean; addressRevision: number; onSelect: (bbl: string) => void;
}) {
  const bbl = profile.identity.bbl;
  const analysis = useAnalysis(bbl);
  const returnedScenario = analysis.scenario?.kind === "scenario" ? analysis.scenario.document : null;
  const returnedEvaluation = analysis.evaluation?.kind === "evaluation" ? analysis.evaluation.document : null;
  const matchingScenario = returnedScenario?.evaluated_input.bbl === bbl ? returnedScenario : null;
  const identityEvaluation = returnedEvaluation?.evaluated_input.bbl === bbl ? returnedEvaluation : null;
  const inspectableEvaluation = evaluationIsInspectable(identityEvaluation) ? identityEvaluation : null;
  const condoOutcome = useCondoRecords(bbl);
  const condo = deriveCondoSurface(profile, condoOutcome);
  const associationMismatch = !!((returnedScenario && !matchingScenario) || (returnedEvaluation && !identityEvaluation));
  const scenario = condo.withholdAllowances || associationMismatch ? null : matchingScenario;
  const evaluation = condo.withholdAllowances || associationMismatch ? null : inspectableEvaluation;
  const [address, setAddress] = useState<SelectedAddress | null>(null);
  const [tool, setTool] = useState<DashboardTool | null>(initialTool === "envelope" ? "proposal" : initialTool);
  const [selection, setSelection] = useState("calculation");
  const root = useRef<HTMLDivElement>(null);
  useEffect(() => { setAddress(recalledAddress(bbl)); }, [bbl, addressRevision]);
  useEffect(() => { root.current?.querySelector<HTMLElement>("h1")?.focus(); }, [bbl, addressRevision]);
  const label = address?.label ?? profile.identity.address?.normalized_address ?? `BBL ${bbl}`;
  const open = useCallback((value: DashboardTool) => setTool(value === "envelope" ? "proposal" : value), []);
  const inspect = (id: string) => { setSelection(id); open("evidence"); };

  function followWorkspaceLink(event: MouseEvent) {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const link = (event.target as Element).closest("a");
    if (!link) return;
    if (link.getAttribute("href") === "#condo-records") { event.preventDefault(); open("records"); return; }
    const url = new URL(link.href, window.location.href);
    if (url.origin !== window.location.origin || url.pathname !== "/property") return;
    const target = validateBblInput(url.searchParams.get("bbl") ?? "");
    if (!target.ok) return;
    if (target.canonical !== bbl) { event.preventDefault(); onSelect(target.canonical); return; }
    const view = url.searchParams.get("view");
    const next = readDashboardTool(view);
    if (next || view === "overview" || view === null) { event.preventDefault(); if (next) open(next); else setTool(null); }
  }
  const evaluationMessage = returnedEvaluation && !identityEvaluation
    ? "Rule evaluation identity mismatch. Results are withheld from this property."
    : identityEvaluation && !inspectableEvaluation ? "Rule details incomplete. Numerical summaries are unavailable; the returned record is preserved."
    : analysis.evaluation ? announcementForRuleEvaluation(analysis.evaluation) : "";

  return <div ref={root} data-testid="connected-dashboard" onClickCapture={followWorkspaceLink} className={tool === "report" ? "dashboard-report-open" : ""}>
    <OutcomeAnnouncer testId="rule-eval-announcer" message={evaluationMessage}/>
    <div className="dashboard-analysis-notices">
      <AnalysisIdentityNotice label="Scenario" requestedBbl={bbl} document={returnedScenario}/>
      <AnalysisIdentityNotice label="Rule evaluation" requestedBbl={bbl} document={returnedEvaluation}/>
      <IncompleteEvaluationNotice evaluation={identityEvaluation}/>
      {analysis.scenario && analysis.scenario.kind !== "scenario" && analysis.scenario.kind !== "aborted" ? <details><summary>Scenario unavailable · retry or inspect</summary><ScenarioFailureStates outcome={analysis.scenario} onRetry={analysis.retryScenario}/></details> : null}
      {analysis.evaluation && analysis.evaluation.kind !== "evaluation" ? <details><summary>Rule evaluation unavailable · retry or inspect</summary><RuleEvaluationFailure outcome={analysis.evaluation} onRetry={analysis.retryEvaluation}/></details> : null}
      {!analysis.scenario || !analysis.evaluation ? <p className="section-note" role="status">Loading analysis… Property records remain available.</p> : null}
    </div>
    {address && profile.identity.address?.normalized_address && profile.identity.address.normalized_address !== address.label ? <p className="dashboard-address-alias" data-testid="representative-address">Searched address retained · PLUTO representative address: {profile.identity.address.normalized_address}</p> : null}
    <DashboardPanels profile={profile} scenario={scenario} evaluation={evaluation} condo={condo} label={label} map={<DashboardMap bbl={bbl} condo={condo} compact/>} onOpen={open} onInspect={inspect}/>
    {DASHBOARD_TOOLS.filter(value => value !== "envelope").map(value => <FloatingWorkspaceWindow key={value} id={`workspace-${value}`} title={TOOL_LABELS[value]} open={tool === value} onClose={() => setTool(null)} wide={["map", "proposal", "study", "report", "evidence"].includes(value)}>
      {tool === value || PERSISTENT_TOOLS.includes(value) ? <DashboardTools tool={value} profile={profile} scenario={scenario} evaluation={evaluation} returnedScenario={returnedScenario} returnedEvaluation={returnedEvaluation} condo={condo} address={address} label={label} selection={selection} onSelectEvidence={setSelection} onInspect={inspect} onOpen={open} surveyEnabled={surveyEnabled}/> : null}
    </FloatingWorkspaceWindow>)}
  </div>;
}

/** Route adapter: the existing API hooks retain their identity and stale-response guards. */
export function DashboardEntry({ surveyEnabled = false }: { surveyEnabled?: boolean }) {
  const params = useSearchParams();
  const router = useRouter();
  const valid = validateBblInput(params.get("bbl") ?? "");
  const bbl = valid.ok ? valid.canonical : null;
  const property = useProperty(bbl);
  const [addressRevision, setAddressRevision] = useState(0);
  const select = (selected: string) => {
    const next = validateBblInput(selected);
    if (!next.ok) return;
    setAddressRevision(value => value + 1);
    router.replace(dashboardHref(next.canonical), { scroll: false });
    // The old confirmation button is about to leave; never leave focus on body.
    document.getElementById("architect-address")?.focus();
  };
  const profile = property.outcome?.kind === "profile" && property.outcome.profile.identity.bbl === bbl ? property.outcome.profile : null;
  const mismatch = property.outcome?.kind === "profile" && !profile;
  return <div className="architect-shell dashboard-shell">
    <a className="architect-skip" href="#dashboard-content">Skip to workspace</a>
    <header className="dashboard-topbar">
      <Link href={dashboardHref()} className="dashboard-brand"><svg width="29" height="32" viewBox="0 0 27 30" fill="none" aria-hidden="true"><path d="M1 28h25M4 28V14h7v14M11 28V2h9v26M20 8h4v20" stroke="currentColor" strokeWidth="1.7"/></svg><span>NYC Buildability<small>Zoning · FAR · Feasibility · Reports · Maps</small></span></Link>
      <span className="dashboard-internal-label">Internal · Engineering team only</span>
      <details className="dashboard-environment"><summary>Build & review status</summary><InternalBanner/><p>Preliminary analysis — professional review required before any reliance.</p></details>
    </header>
    <DashboardSearch onSelect={select}/>
    <p className="dashboard-review-line">Preliminary analysis · Professional review required · No sign-in or access control</p>
    <div id="dashboard-content" className="dashboard-content">
      <OutcomeAnnouncer message={mismatch ? "Property identity mismatch. Results withheld." : property.outcome ? announcementForOutcome(property.outcome) : ""}/>
      {!bbl ? <section className="dashboard-welcome"><h1>Your property workspace</h1><p>{params.get("bbl") ? "Invalid property identifier. Search an address or enter a valid 10-digit BBL." : "Search an address and confirm the lot to load its map, records and available development limits."}</p></section>
        : property.loading ? <section className="card" role="status" aria-busy="true"><h1>Retrieving property facts…</h1><p>BBL {bbl}</p></section>
        : profile ? <LoadedDashboard key={bbl} profile={profile} initialTool={readDashboardTool(params.get("tool"))} surveyEnabled={surveyEnabled} addressRevision={addressRevision} onSelect={select}/>
        : mismatch && property.outcome?.kind === "profile" ? <section className="card" role="alert"><h1>Property identity mismatch</h1><p>Requested BBL {bbl}; returned BBL {property.outcome.profile.identity.bbl}. This record cannot be used for the selected property.</p><CapturedRecord value={property.outcome.profile} label="Returned property record"/></section>
        : property.outcome ? <OutcomeFailureStates outcome={property.outcome} onRetry={property.retry}/> : null}
    </div>
  </div>;
}
