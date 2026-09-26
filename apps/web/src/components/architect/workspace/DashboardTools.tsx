"use client";
import { useMemo, useState } from "react";
import type { PropertyProfile } from "@/lib/contract";
import type { Scenario } from "@/lib/scenario-contract";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import type { SelectedAddress } from "@/lib/architect/selected-address";
import type { ProposalDraft } from "@/lib/architect/proposal-draft";
import { maxEnvelopeRequestForProfile } from "@/lib/architect/max-envelope-api";
import { SurveyReviewClientProvider } from "@/lib/surveyReview/context";
import { ReviewInbox } from "@/components/survey-review/ReviewInbox";
import { PropertyFacts, ZoningView, OpenIssues, PlannedView } from "../ProfileViews";
import { CondoRecordsChannelSection, type CondoSurfaceDecision } from "../CondoRecordsSection";
import { ParcelStudyPanel } from "../ParcelStudyPanel";
import { EvidenceWorkspace } from "../EvidenceWorkspace";
import { ScenarioWorkspace } from "../ScenarioWorkspace";
import { ReportView } from "../ReportView";
import { ProposalEditor } from "../ProposalEditor";
import { MaxEnvelopePanel } from "../MaxEnvelopePanel";
import { CapturedRecord } from "../EvidenceRecord";
import { DashboardMap } from "./DashboardMap";
import type { DashboardTool } from "./types";

function ProposalTool({ profile }: { profile: PropertyProfile }) {
  const request = useMemo(() => maxEnvelopeRequestForProfile(profile), [profile]);
  const [adoptedDraft, setAdoptedDraft] = useState<ProposalDraft | null>(null);
  return <><MaxEnvelopePanel request={request} onAdopt={setAdoptedDraft}/><ProposalEditor bbl={profile.identity.bbl} adoptedDraft={adoptedDraft}/></>;
}
export interface DashboardToolsProps {
  tool: DashboardTool;
  profile: PropertyProfile;
  scenario: Scenario | null;
  evaluation: RuleEvaluation | null;
  returnedScenario: Scenario | null;
  returnedEvaluation: RuleEvaluation | null;
  condo: CondoSurfaceDecision;
  address: SelectedAddress | null;
  label: string;
  selection: string;
  onSelectEvidence: (value: string) => void;
  onInspect: (id: string) => void;
  onOpen: (tool: DashboardTool) => void;
  surveyEnabled: boolean;
}
/** Existing guarded detail surfaces keep their provenance and honest-gap copy. */
export function DashboardTools(props: DashboardToolsProps) {
  const { tool, profile, scenario, evaluation, returnedScenario, returnedEvaluation, condo, address, label, selection, onSelectEvidence, onInspect, onOpen, surveyEnabled } = props;
  const bbl = profile.identity.bbl;
  switch (tool) {
    case "map": return <DashboardMap bbl={bbl} condo={condo}/>;
    case "facts": return <PropertyFacts profile={profile} onInspect={onInspect}/>;
    case "zoning": return <ZoningView profile={profile} evaluation={evaluation} scenario={scenario} onInspect={onInspect}/>;
    case "records": return <div id="condo-records"><CondoRecordsChannelSection decision={condo}/>{!condo.showRecords && !condo.showSubstitution ? <p>No separate condo parcel record is available. The entered property record remains available in Property facts.</p> : null}</div>;
    case "study": return condo.recordsView?.outcome === "multi_lot_set"
      ? <ParcelStudyPanel requestedBbl={bbl} records={condo.recordsView} recordsConflict={condo.conflict}/>
      : <section className="card"><h2>Parcel study</h2><p>A validated multi-parcel record is required for combined and separate studies.</p><button type="button" className="secondary-button" onClick={() => onOpen("records")}>Inspect parcel records</button></section>;
    case "evidence": return <><EvidenceWorkspace profile={profile} evaluation={evaluation} scenario={scenario} address={address} selection={selection} onSelect={onSelectEvidence}/>
      {condo.withholdAllowances ? <section className="card"><h2>Withheld analysis records</h2><p>Original returned evidence only. These figures are not allowances for the unresolved site.</p>
        {returnedEvaluation ? <CapturedRecord value={returnedEvaluation} label="Original rule-evaluation record · site allowance withheld"/> : null}
        {returnedScenario ? <CapturedRecord value={returnedScenario} label="Original scenario record · site allowance withheld"/> : null}
      </section> : null}</>;
    case "issues": return <><OpenIssues profile={profile}/><CondoRecordsChannelSection decision={condo}/></>;
    case "scenarios": return scenario ? <ScenarioWorkspace document={scenario} evaluation={evaluation} bbl={bbl}/> : <section className="card"><h2>Scenario results unavailable</h2><p>{condo.withholdAllowances ? "Computed allowances are withheld until the legal analysis site is resolved." : "No matching, usable scenario was supplied."}</p>{returnedScenario ? <CapturedRecord value={returnedScenario} label="Returned scenario record · not a site allowance"/> : null}</section>;
    case "report": return <ReportView profile={profile} scenario={returnedScenario} evaluation={returnedEvaluation} label={label} condoDecision={condo}/>;
    case "proposal":
    case "envelope": return condo.withholdAllowances
      ? <section className="card"><h2>Site definition required</h2><p>Combined-site proposal and envelope checks are unavailable for this unresolved condo site. Recorded base parcels can be studied together or separately without establishing development rights.</p><button type="button" className="primary-button" onClick={() => onOpen("study")}>Open parcel study</button></section>
      : <ProposalTool profile={profile}/>;
    case "documents": return surveyEnabled ? <SurveyReviewClientProvider><ReviewInbox bbl={bbl} embedded/></SurveyReviewClientProvider> : <section className="card"><h2>Document review is unavailable in this environment</h2><p>Survey review must be enabled before document records can be retrieved. No document inventory or upload service is available here.</p></section>;
    case "units": return <PlannedView label="Units"/>;
    case "financials": return <PlannedView label="Financials"/>;
  }
}
