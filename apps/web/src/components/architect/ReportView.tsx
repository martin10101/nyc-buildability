"use client";
import { useState } from "react";
import type { PropertyProfile } from "@/lib/contract";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import type { Scenario } from "@/lib/scenario-contract";
import { provenanceById } from "@/lib/provenance";
import { ZoningSection } from "@/components/property/ZoningSection";
import { ScenarioConstraints } from "@/components/compare/ScenarioConstraints";
import { ScenarioAssumptions } from "@/components/compare/ScenarioAssumptions";
import { PropertyFacts, OpenIssues } from "./ProfileViews";
import { DraftHeadline } from "./PropertyOverview";
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
    const print = () => {
        const details = Array.from(document.querySelectorAll<HTMLDetailsElement>(".architect-report details"));
        const states = details.map(item => item.open);
        details.forEach(item => { item.open = auditAppendix || !item.classList.contains("architect-raw"); });
        const restore = () => { details.forEach((item, index) => { item.open = states[index]; }); window.removeEventListener("afterprint", restore); };
        window.addEventListener("afterprint", restore);
        window.print();
    };
    return <div className={`architect-report ${auditAppendix ? "includes-audit" : ""}`}>
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
    </section>
    <PropertyFacts profile={profile}/>
    <ZoningSection profile={profile} byId={provenanceById(profile)}/>
    <section className="card">
      <h2>Pending land-use actions</h2>
      <p>Unknown — source not connected</p>
    </section>
    <OpenIssues profile={profile}/>
    {scenario ? <>
      <ScenarioConstraints document={scenario}/>
      <ScenarioAssumptions document={scenario}/>
    </> : null}
    <section className="card">
      <CalculationEvidence evaluation={evaluation} scenario={scenario}/>
    </section>
    <ReportSources profile={profile}/>
    <section className="card architect-audit-appendix">
      <h2>Complete audit appendix</h2>
      <p className="section-note">Available here on demand. Included in print only when the audit appendix is selected.</p>
      <CapturedRecord value={profile} label="Full property source and review records"/>
    </section>
  </div>;
}
