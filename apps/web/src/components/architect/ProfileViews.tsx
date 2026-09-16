import Link from "next/link";
import type { PropertyProfile } from "@/lib/contract";
import type { Scenario } from "@/lib/scenario-contract";
import { DevelopmentLimits, IncompleteEvaluationNotice } from "./DevelopmentLimits";
import { evaluationIsInspectable } from "@/lib/architect/development-limits";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import { provenanceById } from "@/lib/provenance";
import { propertyHref } from "@/lib/architect/navigation";
import { ConflictsSection } from "@/components/property/ConflictsSection";
import { MissingInputsSection } from "@/components/property/MissingInputsSection";
import { UnsupportedSection } from "@/components/property/UnsupportedSection";
import { ProfessionalReviewPanel } from "@/components/property/ProfessionalReviewPanel";
import { CoverageLegend } from "@/components/property/CoverageLegend";
import { ZoningSection } from "@/components/property/ZoningSection";
import { RuleEvaluationResult } from "@/components/rule-evaluation/RuleEvaluationResult";
import { CapturedRecord } from "./EvidenceRecord";
import { AdditionalZoningFlags } from "./AdditionalZoningFlags";
import { PropertyIssuesSummary } from "./PropertyOverview";
export { PropertyFacts } from "./PropertyFacts";
export function ZoningView({ profile, evaluation, scenario = null, onInspect }: {
    profile: PropertyProfile;
    evaluation: RuleEvaluation | null;
    scenario?: Scenario | null;
    onInspect?: (id: string) => void;
}) {
    return <>
    <PropertyIssuesSummary profile={profile}/>
    <DevelopmentLimits profile={profile} evaluation={evaluation} scenario={scenario} onInspect={onInspect}/>
    <ZoningSection profile={profile} byId={provenanceById(profile)}/>
    <AdditionalZoningFlags profile={profile}/>
    <section className="card">
      <h2>Spatial evidence</h2>
      <p className="section-note">Map boundaries provide context. Canonical intersection results and uncertainty are preserved below.</p>
      {profile.spatial_intersection ? <>
        <p>
          {profile.spatial_intersection.coverage_note}
        </p>
        <ul className="architect-issue-list">
          {profile.spatial_intersection.review_reasons?.map((reason, i) => <li key={i}>
            {reason}
          </li>)}
        </ul>
        <CapturedRecord value={profile.spatial_intersection} label="Full spatial-intersection result"/>
      </> : <p>Spatial-intersection evidence is not included in this profile.</p>}
      <CapturedRecord value={profile.zoning_features} label="Zoning feature layers and provenance"/>
      <CapturedRecord value={profile.lot_geometry} label="Lot geometry status and provenance"/>
    </section>
    <IncompleteEvaluationNotice evaluation={evaluation}/>
    {evaluation && evaluationIsInspectable(evaluation) ? <details className="card architect-disclosure">
      <summary>Draft rule result, conflicts and applicability</summary>
      <RuleEvaluationResult document={evaluation}/>
    </details> : null}
    <Link className="primary-button" href={propertyHref(profile.identity.bbl, "evidence")}>Inspect calculation evidence →</Link>
  </>;
}
export function OpenIssues({ profile }: {
    profile: PropertyProfile;
}) {
    return <>
    <ConflictsSection conflicts={profile.conflicts}/>
    <MissingInputsSection entries={profile.missing_inputs}/>
    <UnsupportedSection profile={profile}/>
    <ProfessionalReviewPanel profile={profile}/>
    <section className="card">
      <h2>Confirmations and overrides</h2>
      <p className="section-note">Property confirmations cannot be saved in this version. Survey decisions use their separate, authorized review workflow.</p>
      {profile.user_confirmations.length ? <CapturedRecord value={profile.user_confirmations} label="Recorded review history"/> : <p>No recorded confirmations or overrides were supplied.</p>}
    </section>
    <details className="card architect-disclosure">
      <summary>Coverage definitions and source policy</summary>
      <CoverageLegend profile={profile}/>
    </details>
  </>;
}
export function PlannedView({ label }: {
    label: string;
}) {
    return <section className="card architect-empty">
    <p className="architect-eyebrow">Planned capability</p>
    <h2>
      {label} is not available in this version</h2>
    <p>No {label.toLowerCase()} model or calculation is connected. The property facts, current draft evaluation and complete evidence remain available in the workspace.</p>
  </section>;
}
