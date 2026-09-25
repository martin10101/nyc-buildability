"use client";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import { announcementForRuleEvaluation } from "@/lib/rule-evaluation";
import { validateBblInput } from "@/lib/bbl";
import { announcementForOutcome } from "@/lib/announce";
import { propertyHref, readWorkspaceView, VIEW_LABELS, type WorkspaceView } from "@/lib/architect/navigation";
import { recalledAddress, type SelectedAddress } from "@/lib/architect/selected-address";
import { useProperty } from "@/lib/architect/use-property";
import { useAnalysis } from "@/lib/architect/use-analysis";
import type { PropertyProfile } from "@/lib/contract";
import { evaluationIsInspectable } from "@/lib/architect/development-limits";
import { AddressResolutionScreen } from "@/components/address/AddressResolutionScreen";
import { OutcomeAnnouncer } from "@/components/property/OutcomeAnnouncer";
import { OutcomeFailureStates } from "@/components/property/FailureState";
import { ScenarioFailureStates } from "@/components/compare/ScenarioFailureStates";
import { RuleEvaluationFailure } from "@/components/rule-evaluation/RuleEvaluationFailure";
import { SurveyReviewClientProvider } from "@/lib/surveyReview/context";
import { ReviewInbox } from "@/components/survey-review/ReviewInbox";
import { AnalysisIdentityNotice } from "./AnalysisIdentityNotice";
import { CapturedRecord } from "./EvidenceRecord";
import { ArchitectShell } from "./ArchitectShell";
import { PropertyOverview, PropertyIssuesSummary } from "./PropertyOverview";
import { PropertyFacts, ZoningView, OpenIssues, PlannedView } from "./ProfileViews";
import { EvidenceWorkspace } from "./EvidenceWorkspace";
import { EvidenceInspector } from "./EvidenceInspector";
import { ScenarioWorkspace } from "./ScenarioWorkspace";
import { ReportView } from "./ReportView";
import { ProposalEditor } from "./ProposalEditor";
import { MaxEnvelopePanel } from "./MaxEnvelopePanel";
import { maxEnvelopeRequestForProfile } from "@/lib/architect/max-envelope-api";
import { type ProposalDraft } from "@/lib/architect/proposal-draft";
import { IncompleteEvaluationNotice } from "./DevelopmentLimits";

/**
 * The architect design surface (task M5-T070, D-082-R003 + D-083): the
 * Preliminary-development-limits panel renders FIRST (answer-first, from the
 * lot context alone, before any designer input), then the accepted proposal
 * editor. Adopting the Generated building option seeds the editor's ONE draft
 * model; manual entry stays fully available and unchanged. The panel is
 * ADDITIVE — its absence/loading/failure leaves the editor untouched.
 */
function ProposalSurface({ bbl, profile }: { bbl: string; profile: PropertyProfile }) {
    const request = useMemo(() => maxEnvelopeRequestForProfile(profile), [profile]);
    const [adoptedDraft, setAdoptedDraft] = useState<ProposalDraft | null>(null);
    return <>
    <MaxEnvelopePanel request={request} onAdopt={setAdoptedDraft}/>
    <ProposalEditor bbl={bbl} adoptedDraft={adoptedDraft}/>
  </>;
}
function PropertySearch() {
    const router = useRouter();
    const [bbl, setBbl] = useState("");
    const [error, setError] = useState<string | null>(null);
    const submit = (event: FormEvent) => {
        event.preventDefault();
        const result = validateBblInput(bbl);
        if (!result.ok) {
            setError(result.message);
            return;
        }
        router.push(propertyHref(result.canonical));
    };
    return <div className="architect-search-view">
    <p className="architect-eyebrow">Property intelligence · New York City</p>
    {/* DB-083(f) / HJ ADV-4: the environment badge + professional-review line stay
        visible on the search surface at EVERY width — the shell's own
        `.architect-environment` disclosure and nav footnote are hidden ≤700px
        (architect.css P0 gap), so the internal-build / no-access-control /
        do-not-share / "nothing here is a legal determination" meaning (LS-P01/A01)
        and the "professional review required" meaning (A03) are carried here in a
        search-scoped element that no breakpoint hides. This is the environment
        notice, NOT the PRD §29 disclaimer — that stays verbatim in the global
        footer via REQUIRED_DISCLAIMER (never retyped, DB-083 b). */}
    <div className="architect-search-environment" role="note" data-testid="search-environment">
      <span className="architect-search-env-badge">Internal build</span>
      <span className="architect-search-env-note">No sign-in or access control yet, the official data shown is unreviewed, and nothing here is a legal determination — do not share outside the engineering team.</span>
    </div>
    <AddressResolutionScreen architect/>
    <details className="card architect-disclosure architect-search-bbl">
      <summary>Search by tax lot (BBL)</summary>
      <p className="section-note">Already have the 10-digit borough–block–lot? Open it directly — this is an alternative to the address search above, not a separate step.</p>
      <form className="bbl-form" onSubmit={submit} noValidate>
        <div className="field-group">
          <label className="field-label" htmlFor="architect-bbl">BBL</label>
          <input id="architect-bbl" className="text-input" inputMode="numeric" autoComplete="off" placeholder="10-digit borough–block–lot" value={bbl} onChange={event => { setBbl(event.target.value); setError(null); }} aria-describedby="architect-bbl-error" aria-invalid={error ? true : undefined}/>
        </div>
        <button type="submit" className="primary-button">Open property</button>
      </form>
      {/* The four distinct lib/bbl.ts validation messages (empty / non_numeric /
          wrong_length / invalid_borough) render verbatim from validateBblInput —
          never one generic red icon (spec §5.1 Missing). role="status" is kept for
          the aria-describedby announcer contract; the styled wrapper only appears
          when there is a message, so the honest empty state is unchanged. */}
      <p id="architect-bbl-error" role="status" className={error ? "architect-search-bbl-error" : undefined} data-testid="architect-bbl-error">
        {error}
      </p>
    </details>
    <p className="architect-search-review" data-testid="search-review">Preliminary analysis — professional review required before any reliance.</p>
  </div>;
}
function LoadedWorkspace({ profile, view, surveyEnabled }: {
    profile: PropertyProfile;
    view: WorkspaceView;
    surveyEnabled: boolean;
}) {
    const router = useRouter();
    const analysis = useAnalysis(profile.identity.bbl);
    const returnedScenario = analysis.scenario?.kind === "scenario" ? analysis.scenario.document : null;
    const returnedEvaluation = analysis.evaluation?.kind === "evaluation" ? analysis.evaluation.document : null;
    const scenario = returnedScenario?.evaluated_input.bbl === profile.identity.bbl ? returnedScenario : null;
    const identityEvaluation = returnedEvaluation?.evaluated_input.bbl === profile.identity.bbl ? returnedEvaluation : null;
    const evaluation = evaluationIsInspectable(identityEvaluation) ? identityEvaluation : null;
    const evaluationAnnouncement = returnedEvaluation && !identityEvaluation
        ? `Rule evaluation identity ${returnedEvaluation.evaluated_input.bbl ? "mismatch" : "missing"}. Requested BBL ${profile.identity.bbl}; returned BBL ${returnedEvaluation.evaluated_input.bbl ?? "not stated"}. Results are withheld from this property.`
        : identityEvaluation && !evaluation ? "Rule details incomplete. Numerical summaries are unavailable; the returned record is preserved."
        : analysis.evaluation ? announcementForRuleEvaluation(analysis.evaluation) : "";
    const [address, setAddress] = useState<SelectedAddress | null>(null);
    const [selection, setSelection] = useState("calculation");
    const [inspectorSelection, setInspectorSelection] = useState<string | null>(null);
    const headingRef = useRef<HTMLHeadingElement | null>(null);
    const bbl = profile.identity.bbl;
    useEffect(() => { setAddress(recalledAddress(bbl)); setSelection("calculation"); setInspectorSelection(null); }, [bbl]);
    useEffect(() => { headingRef.current?.focus(); }, [view]);
    const label = address?.label ?? profile.identity.address?.normalized_address ?? `BBL ${bbl}`;
    const showInspector = !["overview", "proposal", "evidence", "report", "documents", "envelope", "units", "financials"].includes(view) || inspectorSelection !== null;
    const openEvidence = () => { setSelection(inspectorSelection ?? "calculation"); router.push(propertyHref(bbl, "evidence")); };
    const closeInspector = useCallback(() => setInspectorSelection(null), []);
    const inspect = (id: string) => { setInspectorSelection(id); };
    const profileAddress = profile.identity.address?.normalized_address;
    const analysisView = ["overview", "zoning", "scenarios", "evidence", "issues", "report"].includes(view);
    let content;
    switch (view) {
        case "overview":
            content = <PropertyOverview profile={profile} scenario={scenario} evaluation={evaluation} onInspect={inspect}/>;
            break;
        case "facts":
            content = <PropertyFacts profile={profile} onInspect={inspect}/>;
            break;
        case "zoning":
            content = <ZoningView profile={profile} evaluation={evaluation} scenario={scenario} onInspect={inspect}/>;
            break;
        case "scenarios":
            content = <>
    <PropertyIssuesSummary profile={profile}/>
    {scenario ? <ScenarioWorkspace document={scenario} evaluation={evaluation} bbl={bbl}/> : null}
  </>;
            break;
        case "evidence":
            content = <EvidenceWorkspace profile={profile} evaluation={evaluation} scenario={scenario} address={address} selection={selection} onSelect={setSelection}/>;
            break;
        case "issues":
            content = <>
    <OpenIssues profile={profile}/>
    {scenario ? <section className="card">
      <h2>Analysis issues</h2>
      <ul className="architect-issue-list">
        {scenario.constraints.filter(item => !["known", "draft"].includes(item.state)).map(item => <li key={item.key}>
          <strong>
            {item.key}: {item.state}
          </strong>
          <p>
            {item.note}
          </p>
        </li>)}
      </ul>
    </section> : null}
  </>;
            break;
        case "documents":
            content = surveyEnabled ? <SurveyReviewClientProvider>
    <ReviewInbox bbl={bbl} embedded/>
  </SurveyReviewClientProvider> : <section className="card architect-empty">
    <h2>Document review is unavailable in this environment</h2>
    <p>Survey review must be enabled before document records can be retrieved. No document inventory or upload service is available here.</p>
  </section>;
            break;
        case "report":
            content = <ReportView profile={profile} evaluation={returnedEvaluation} scenario={returnedScenario} label={label}/>;
            break;
        case "proposal":
            content = <ProposalSurface bbl={bbl} profile={profile}/>;
            break;
        default: content = <PlannedView label={VIEW_LABELS[view]}/>;
    }
    return <div data-testid="profile-view">
    <OutcomeAnnouncer testId="rule-eval-announcer" message={evaluationAnnouncement}/>
    <header className="architect-property-header">
      <div>
        <div className="architect-title-line">
          <h1 tabIndex={-1} ref={headingRef} data-outcome-heading>
            {label}
          </h1>
          <span className="architect-status">Draft analysis</span>
        </div>
        <p>
          {profile.identity.address?.borough ?? "Borough not supplied"} · BBL <span className="architect-bbl">
            {bbl}
          </span> · {VIEW_LABELS[view]}
        </p>
        {address && profileAddress && profileAddress !== address.label ? <p className="architect-address-alias" data-testid="representative-address">Searched address retained · PLUTO representative address: {profileAddress}
        </p> : null}
      </div>
      <Link href={propertyHref()} className="secondary-button">Change property</Link>
    </header>
    <div className={`architect-workspace-grid ${showInspector ? "has-inspector" : ""}`}>
      <div className="architect-main-view">
      {analysisView && !analysis.scenario ? <p className="architect-inline-loading" role="status">Loading draft scenario…</p> : null}
      {analysisView && analysis.scenario && analysis.scenario.kind !== "scenario" && analysis.scenario.kind !== "aborted" ? <ScenarioFailureStates outcome={analysis.scenario} onRetry={() => { headingRef.current?.focus(); analysis.retryScenario(); }}/> : null}
      {analysisView && analysis.evaluation && analysis.evaluation.kind !== "evaluation" ? <RuleEvaluationFailure outcome={analysis.evaluation} onRetry={() => { headingRef.current?.focus(); analysis.retryEvaluation(); }}/> : null}
      {analysisView && view !== "report" ? <>
          <AnalysisIdentityNotice label="Scenario" requestedBbl={bbl} document={returnedScenario}/>
          <AnalysisIdentityNotice label="Rule evaluation" requestedBbl={bbl} document={returnedEvaluation}/>
          <IncompleteEvaluationNotice evaluation={identityEvaluation}/>
        </> : null}
      {content}
    </div>
      {showInspector ? <EvidenceInspector profile={profile} selected={inspectorSelection} onClose={closeInspector} onEvidence={openEvidence}/> : null}
    </div>
  </div>;
}
/** Route adapter only. Legacy server flags select this tree; no client flag can open it. */
export function ArchitectEntry({ defaultView = "overview", surveyEnabled = false, requireBbl = false }: {
    defaultView?: WorkspaceView;
    surveyEnabled?: boolean;
    requireBbl?: boolean;
}) {
    const params = useSearchParams();
    const rawBbl = params.get("bbl") ?? "";
    const valid = validateBblInput(rawBbl);
    const bbl = valid.ok ? valid.canonical : null;
    const view = params.has("view") ? readWorkspaceView(params.get("view")) : defaultView;
    const property = useProperty(bbl);
    const returnedProfile = property.outcome?.kind === "profile" ? property.outcome.profile : null;
    const message = returnedProfile && bbl && returnedProfile.identity.bbl !== bbl
        ? `Property identity mismatch. Requested BBL ${bbl}; returned BBL ${returnedProfile.identity.bbl}. This record cannot be used for the selected property.`
        : property.outcome ? announcementForOutcome(property.outcome) : "";
    return <ArchitectShell bbl={bbl} active={bbl ? view : "search"} surveyEnabled={surveyEnabled}>
    <OutcomeAnnouncer message={message}/>
    {!bbl ? <>
      {rawBbl || requireBbl ? <section className="card failure-state" role="alert">
        <strong>No property selected</strong>
        <p>
          {rawBbl ? "The property identifier is invalid. Enter a valid 10-digit BBL or search an address." : "Choose a property to open this workspace."}
        </p>
      </section> : null}
      <PropertySearch />
    </> : property.loading ? <section className="card architect-loading" aria-busy="true" role="status">
      <p className="architect-eyebrow">BBL {bbl}
      </p>
      <h1>Retrieving property facts…</h1>
      <p>Loading the official property profile.</p>
    </section> : property.outcome?.kind === "profile" && property.outcome.profile.identity.bbl !== bbl ? <section className="card failure-state" role="alert">
      <h1>Property identity mismatch</h1>
      <p>Requested BBL {bbl}; returned BBL {property.outcome.profile.identity.bbl}. This record cannot be used for the selected property.</p>
      <CapturedRecord value={property.outcome.profile} label="Returned property record"/>
      <Link className="secondary-button" href={propertyHref()}>Change property</Link>
    </section> : property.outcome?.kind === "profile" ? <LoadedWorkspace key={bbl} profile={property.outcome.profile} view={view} surveyEnabled={surveyEnabled}/> : property.outcome ? <>
      <OutcomeFailureStates outcome={property.outcome} onRetry={property.retry}/>
      <Link href={propertyHref()} className="secondary-button">Change property</Link>
    </> : null}
  </ArchitectShell>;
}
