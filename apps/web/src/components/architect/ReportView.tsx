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
import { DraftHeadline, PropertyIssuesSummary } from "./PropertyOverview";
import { AssessmentCoverage } from "./AssessmentCoverage";
import { AdditionalZoningFlags } from "./AdditionalZoningFlags";
import { CapturedRecord } from "./EvidenceRecord";
import { CalculationEvidence } from "./CalculationEvidence";
import { ReportSources } from "./ReportSources";
export function ReportView({ profile, scenario, evaluation, label }: {
    profile: PropertyProfile;
    scenario: Scenario | null;
    evaluation: RuleEvaluation | null;
    label: string;
}) {
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
    <section className="card">
      <DraftHeadline scenario={scenario}/>
      <AssessmentCoverage scenario={scenario}/>
    </section>
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
