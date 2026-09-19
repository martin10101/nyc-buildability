"use client";
import { useEffect, useRef, useState } from "react";
import type { PropertyProfile } from "@/lib/contract";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import type { Scenario } from "@/lib/scenario-contract";
import { provenanceById } from "@/lib/provenance";
import { ZoningSection } from "@/components/property/ZoningSection";
import { ScenarioConstraints } from "@/components/compare/ScenarioConstraints";
import { ScenarioAssumptions } from "@/components/compare/ScenarioAssumptions";
import { PropertyFacts, OpenIssues } from "./ProfileViews";
import { PropertyIssuesSummary, CondoRecordsChannelSection, deriveCondoSurface } from "./PropertyOverview";
import { useCondoRecords } from "@/lib/condo-records";
import { DevelopmentLimits, IncompleteEvaluationNotice } from "./DevelopmentLimits";
import { evaluationIsInspectable } from "@/lib/architect/development-limits";
import { AdditionalZoningFlags } from "./AdditionalZoningFlags";
import { CapturedRecord } from "./EvidenceRecord";
import { CalculationEvidence } from "./CalculationEvidence";
import { ReportSources } from "./ReportSources";
import { AnalysisIdentityNotice } from "./AnalysisIdentityNotice";
export function ReportView({ profile, scenario: returnedScenario, evaluation: returnedEvaluation, label }: {
    profile: PropertyProfile;
    scenario: Scenario | null;
    evaluation: RuleEvaluation | null;
    label: string;
}) {
    // Retain original returns inside the print boundary. Only records associated
    // with the selected property may reach its result and calculation views.
    const bbl = profile.identity.bbl;
    const matchedScenario = returnedScenario?.evaluated_input.bbl === bbl ? returnedScenario : null;
    const identityEvaluation = returnedEvaluation?.evaluated_input.bbl === bbl ? returnedEvaluation : null;
    const inspectableEvaluation = evaluationIsInspectable(identityEvaluation) ? identityEvaluation : null;
    // D-073-R006 (M5-T052 reconciliation): the printed brief consumes the SAME
    // shared condo-surface decision the screen (PropertyOverview) uses.
    // deriveCondoSurface folds the ACCEPTED profile fail-safe guard
    // (condoWithholdsAllowances — byte-unchanged) together with the live per-BBL
    // records channel (useCondoRecords). The withhold is MONOTONIC: the profile
    // guard stays fully authoritative and the channel may only ADD withholding
    // (multi-lot / unresolved / typed resolver error), never remove it. So a
    // multi-lot / unresolved / error condo withholds EVERY computed development
    // allowance on the brief exactly as it does on the screen — even when a
    // scenario or rule evaluation matching this BBL would otherwise be displayable.
    // The records section, the substitution explanation, a profile/channel
    // disagreement, and honest absence all render from this ONE decision, so the
    // brief and the screen can never disagree.
    const condoOutcome = useCondoRecords(bbl);
    const condo = deriveCondoSurface(profile, condoOutcome);
    const condoWithholds = condo.withholdAllowances;
    const scenario = condoWithholds ? null : matchedScenario;
    const evaluation = condoWithholds ? null : inspectableEvaluation;
    const [auditAppendix, setAuditAppendix] = useState(false);
    const reportRef = useRef<HTMLDivElement | null>(null);
    const preparePrint = useRef<() => void>(() => undefined);
    useEffect(() => {
        let states: Array<{ item: HTMLDetailsElement; open: boolean }> | null = null;
        const prepare = () => {
            if (states) return;
            states = Array.from(reportRef.current?.querySelectorAll<HTMLDetailsElement>("details") ?? []).map(item => ({ item, open: item.open }));
            states.forEach(({ item }) => { item.open = auditAppendix || !item.classList.contains("architect-raw"); });
        };
        const restore = () => { states?.forEach(({ item, open }) => { item.open = open; }); states = null; };
        preparePrint.current = prepare;
        window.addEventListener("beforeprint", prepare);
        window.addEventListener("afterprint", restore);
        return () => { restore(); window.removeEventListener("beforeprint", prepare); window.removeEventListener("afterprint", restore); };
    }, [auditAppendix]);
    const print = () => { preparePrint.current(); window.print(); };
    return <div ref={reportRef} className={`architect-report ${auditAppendix ? "includes-audit" : ""}`}>
    <section className="card architect-report-intro">
      <div>
        <p className="architect-eyebrow">Property brief</p>
        <h2>
          {label}
        </h2>
        <p>BBL {profile.identity.bbl} · Profile generated {profile.profile_version.generated_at}
        </p>
        <p className="section-note">Print the current facts, draft results, limitations and source appendix. This brief is not saved automatically.</p>
      </div>
      <div className="architect-print-controls">
        <button type="button" className="primary-button" onClick={print}>Print property brief</button>
        <label>
          <input type="checkbox" checked={auditAppendix} onChange={event => setAuditAppendix(event.target.checked)}/> Include full audit appendix</label>
      </div>
    </section>
    <AnalysisIdentityNotice label="Scenario" requestedBbl={bbl} document={returnedScenario}/>
    <AnalysisIdentityNotice label="Rule evaluation" requestedBbl={bbl} document={returnedEvaluation}/>
    <IncompleteEvaluationNotice evaluation={identityEvaluation}/>
    {/* [ORCH-CORRECTED per M5-T037 HJ F1] The report feeds DevelopmentLimits the same
        inspectability-GATED evaluation every screen surface uses (and that
        CalculationEvidence below already receives), so screen and report can never
        quietly disagree on a non-inspectable document (D-073-R003). */}
    <DevelopmentLimits profile={profile} scenario={scenario} evaluation={evaluation}/>
    {/* M5-T052 (D-073-R006): the condo RECORDS reach the printed brief from the
        SAME shared decision and the SAME CondoRecordsChannelSection the screen
        (PropertyOverview) uses, rendered UNDER the professional-review fail-safe
        (DevelopmentLimits above) — records, substitution, a profile/channel
        disagreement, and honest absence are one source of truth across surfaces. */}
    <CondoRecordsChannelSection decision={condo}/>
    <PropertyIssuesSummary profile={profile}/>
    <nav className="architect-report-contents" aria-label="Property brief contents">
      {[["brief-facts", "Facts"], ["brief-zoning", "Zoning"], ["brief-issues", "Issues & assumptions"], ["brief-calculations", "Calculations"], ["brief-sources", "Sources"]].map(([id, text]) => <a key={id} href={`#${id}`} onClick={() => { const section = document.getElementById(id); if (section instanceof HTMLDetailsElement) section.open = true; }}>{text}</a>)}
    </nav>
    <details className="card architect-disclosure architect-report-section" id="brief-facts">
      <summary>Property facts and identity</summary>
      <PropertyFacts profile={profile} allSections/>
    </details>
    <details className="card architect-disclosure architect-report-section" id="brief-zoning">
      <summary>Zoning and mapped flags</summary>
    <ZoningSection profile={profile} byId={provenanceById(profile)}/>
    <AdditionalZoningFlags profile={profile}/>
    </details>
    <details className="card architect-disclosure architect-report-section" id="brief-issues">
      <summary>Open issues, constraints and assumptions</summary>
    <OpenIssues profile={profile}/>
    {scenario ? <>
      <ScenarioConstraints document={scenario}/>
      <ScenarioAssumptions document={scenario}/>
    </> : null}
    </details>
    <details className="card architect-disclosure architect-report-section" id="brief-calculations">
      <summary>Calculation and rule evidence</summary>
      <CalculationEvidence evaluation={evaluation} scenario={scenario}/>
    </details>
    <details className="card architect-disclosure architect-report-section" id="brief-sources">
      <summary>Source and review appendix</summary>
      <ReportSources profile={profile}/>
    </details>
    <details className="card architect-disclosure architect-audit-appendix">
      <summary>Complete audit appendix</summary>
      <p className="section-note">Available here on demand. Included in print only when the audit appendix is selected.</p>
      <CapturedRecord value={profile} label="Full property source and review records"/>
    </details>
  </div>;
}
