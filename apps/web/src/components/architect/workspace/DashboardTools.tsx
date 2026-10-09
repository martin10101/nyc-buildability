"use client";
import { useEffect, useMemo, useState } from "react";
import type { PropertyProfile } from "@/lib/contract";
import type { Scenario } from "@/lib/scenario-contract";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import type { SelectedAddress } from "@/lib/architect/selected-address";
import type { ProposalDraft } from "@/lib/architect/proposal-draft";
import { maxEnvelopeRequestForProfile } from "@/lib/architect/max-envelope-api";
import { SurveyReviewClientProvider } from "@/lib/surveyReview/context";
import { ReviewInbox } from "@/components/survey-review/ReviewInbox";
import { PropertyFacts, ZoningView, OpenIssues, PlannedView } from "../ProfileViews";
import { LotSiteSetup } from "../LotSiteSetup";
import { HiddenIssueFlags } from "../HiddenIssueFlags";
import { ParityPanel } from "../ParityPanel";
import { ResultsPanel } from "../ResultsPanel";
import { CondoRecordsChannelSection, type CondoSurfaceDecision } from "../CondoRecordsSection";
import { ParcelStudyPanel } from "../ParcelStudyPanel";
import { EvidenceWorkspace } from "../EvidenceWorkspace";
import { ScenarioWorkspace } from "../ScenarioWorkspace";
import { ReportView } from "../ReportView";
import { ProposalEditor } from "../ProposalEditor";
import { MaxEnvelopePanel } from "../MaxEnvelopePanel";
import { CapturedRecord } from "../EvidenceRecord";
import { DashboardMap } from "./DashboardMap";
import { TOOL_LABELS, type DashboardTool } from "./types";

function ProposalTool({ profile, focusEnvelope = false, envelopeRequest = 0 }: { profile: PropertyProfile; focusEnvelope?: boolean; envelopeRequest?: number }) {
  const request = useMemo(() => maxEnvelopeRequestForProfile(profile), [profile]);
  const [adoptedDraft, setAdoptedDraft] = useState<ProposalDraft | null>(null);
  const [limitsOpen, setLimitsOpen] = useState(focusEnvelope);
  useEffect(() => { setLimitsOpen(focusEnvelope); }, [focusEnvelope, envelopeRequest]);
  return <><details className="dashboard-tool-details" open={limitsOpen} onToggle={event => setLimitsOpen(event.currentTarget.open)}><summary>Preliminary development limits · inspect status &amp; sources</summary><MaxEnvelopePanel request={request} onAdopt={setAdoptedDraft} bbl={profile.identity.bbl}/></details><ProposalEditor bbl={profile.identity.bbl} adoptedDraft={adoptedDraft}/></>;
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
  /** Server-read INTERNAL_PROPOSAL_EDITOR_ENABLED (D-01, plan §7); absent -> off. */
  proposalEditorEnabled?: boolean;
  /** Server-read INTERNAL_UNUSED_FLOOR_AREA_SECTION_ENABLED (D-06, plan §3 step 4); absent -> off. */
  unusedFloorAreaSectionEnabled?: boolean;
  /** Server-read INTERNAL_LOT_SITE_SETUP_ENABLED (D-04, plan M1-13); absent -> off. */
  lotSiteSetupEnabled?: boolean;
  /** Server-read INTERNAL_HIDDEN_ISSUE_FLAGS_UI_ENABLED (D-12, plan M2-06); absent -> off. */
  hiddenIssueFlagsEnabled?: boolean;
  /** Server-read INTERNAL_PARITY_UI_ENABLED (D-15, plan §11b); absent -> off. */
  parityUiEnabled?: boolean;
  /** Server-read INTERNAL_RESULTS_UI_ENABLED (M5-T140, ruling R1); absent -> off. */
  resultsUiEnabled?: boolean;
  focusEnvelope?: boolean;
  envelopeRequest?: number;
}
/** Existing guarded detail surfaces keep their provenance and honest-gap copy. */
export function DashboardTools(props: DashboardToolsProps) {
  const { tool, profile, scenario, evaluation, returnedScenario, returnedEvaluation, condo, address, label, selection, onSelectEvidence, onInspect, onOpen, surveyEnabled } = props;
  const unusedFloorAreaSectionEnabled = props.unusedFloorAreaSectionEnabled ?? false;
  const bbl = profile.identity.bbl;
  const associationMismatch = !!((returnedScenario && returnedScenario.evaluated_input.bbl !== bbl)
    || (returnedEvaluation && returnedEvaluation.evaluated_input.bbl !== bbl));
  switch (tool) {
    case "map": return <DashboardMap bbl={bbl} condo={condo}/>;
    case "facts": return <PropertyFacts profile={profile} onInspect={onInspect}/>;
    // D-04 (plan M1-13): lot choice + site facts, behind a default-off server flag.
    // A deep link or tool open with the flag off gets the plain not-available view.
    case "lotsite": return props.lotSiteSetupEnabled ? <LotSiteSetup bbl={bbl}/> : <PlannedView label={TOOL_LABELS.lotsite}/>;
    case "zoning": return <ZoningView profile={profile} evaluation={evaluation} scenario={scenario} onInspect={onInspect}/>;
    case "records": return <div id="condo-records"><CondoRecordsChannelSection decision={condo}/>{!condo.showRecords && !condo.showSubstitution ? <p>No separate condo parcel record is available. The entered property record remains available in Property facts.</p> : null}</div>;
    case "study": return condo.recordsView?.outcome === "multi_lot_set"
      ? <ParcelStudyPanel requestedBbl={bbl} records={condo.recordsView} recordsConflict={condo.conflict}/>
      : <section className="card"><h2>Parcel study</h2><p>A validated multi-parcel record is required for combined and separate studies.</p><button type="button" className="secondary-button" onClick={() => onOpen("records")}>Inspect parcel records</button></section>;
    case "evidence": return <><EvidenceWorkspace profile={profile} evaluation={evaluation} scenario={scenario} address={address} selection={selection} onSelect={onSelectEvidence} unusedFloorAreaSectionEnabled={unusedFloorAreaSectionEnabled}/>
      {condo.withholdAllowances || associationMismatch ? <section className="card" aria-label="Withheld analysis records"><h2>Withheld analysis records</h2><p>Original returned evidence only. {associationMismatch ? "At least one analysis record does not identify the selected property. " : null}{condo.withholdAllowances ? "The legal analysis site is unresolved. " : null}These figures are not development allowances for this property.</p>
        {returnedEvaluation ? <CapturedRecord value={returnedEvaluation} label="Original rule-evaluation record · allowances withheld"/> : null}
        {returnedScenario ? <CapturedRecord value={returnedScenario} label="Original scenario record · allowances withheld"/> : null}
      </section> : null}</>;
    case "issues": return <><OpenIssues profile={profile}/><CondoRecordsChannelSection decision={condo}/></>;
    // D-12 (plan M2-06, §8a): hidden-issue flags, behind a default-off server flag.
    // A deep link or tool open with the flag off gets the plain not-available view.
    case "hiddenissues": return props.hiddenIssueFlagsEnabled ? <HiddenIssueFlags bbl={bbl}/> : <PlannedView label={TOOL_LABELS.hiddenissues}/>;
    // D-15 (plan §11b, B-11): parity panel — comparable sales + unused floor area,
    // behind a default-off server flag. A deep link or tool open with the flag off
    // gets the plain not-available view (no fetch when off).
    case "parity": return props.parityUiEnabled ? <ParityPanel bbl={bbl}/> : <PlannedView label={TOOL_LABELS.parity}/>;
    // M5-T140 (ruling R1): the results panel, behind a default-off website switch. A deep link or
    // tool open with the switch off gets the plain not-available view (no fetch when off, R2).
    case "results": return props.resultsUiEnabled ? <ResultsPanel bbl={bbl}/> : <PlannedView label={TOOL_LABELS.results}/>;
    case "scenarios": return scenario ? <ScenarioWorkspace document={scenario} evaluation={evaluation} bbl={bbl} unusedFloorAreaSectionEnabled={unusedFloorAreaSectionEnabled}/> : <section className="card"><h2>Scenario results unavailable</h2><p>{condo.withholdAllowances ? "Computed allowances are withheld until the legal analysis site is resolved." : "No matching, usable scenario was supplied."}</p>{returnedScenario ? <CapturedRecord value={returnedScenario} label="Returned scenario record · not a site allowance"/> : null}</section>;
    case "report": return <ReportView profile={profile} scenario={returnedScenario} evaluation={returnedEvaluation} label={label} condoDecision={condo} unusedFloorAreaSectionEnabled={unusedFloorAreaSectionEnabled}/>;
    // D-01 (plan §7): the proposal editor and envelope panel are set aside behind a
    // default-off server flag; a deep link or tool open gets the plain not-available view.
    case "proposal":
    case "envelope": return !props.proposalEditorEnabled ? <PlannedView label={TOOL_LABELS.proposal}/> : condo.withholdAllowances
      ? <section className="card"><h2>Site definition required</h2><p>Combined-site proposal and envelope checks are unavailable for this unresolved condo site. Recorded base parcels can be studied together or separately without establishing development rights.</p><button type="button" className="primary-button" onClick={() => onOpen("study")}>Open parcel study</button></section>
      : <ProposalTool profile={profile} focusEnvelope={props.focusEnvelope} envelopeRequest={props.envelopeRequest}/>;
    case "documents": return surveyEnabled ? <SurveyReviewClientProvider><ReviewInbox bbl={bbl} embedded/></SurveyReviewClientProvider> : <section className="card"><h2>Document review is unavailable in this environment</h2><p>Survey review must be enabled before document records can be retrieved. No document inventory or upload service is available here.</p></section>;
    case "units": return <PlannedView label="Units"/>;
    case "financials": return <PlannedView label="Financials"/>;
  }
}
