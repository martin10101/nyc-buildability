import Link from "next/link";
import { mappedFeatureView, type PropertyProfile } from "@/lib/contract";
import { completenessDisplay } from "@/lib/coverage";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import { provenanceById } from "@/lib/provenance";
import { propertyHref } from "@/lib/architect/navigation";
import { FactsTable } from "@/components/property/FactsTable";
import { ConflictsSection } from "@/components/property/ConflictsSection";
import { MissingInputsSection } from "@/components/property/MissingInputsSection";
import { UnsupportedSection } from "@/components/property/UnsupportedSection";
import { ProfessionalReviewPanel } from "@/components/property/ProfessionalReviewPanel";
import { CoverageLegend } from "@/components/property/CoverageLegend";
import { ZoningSection } from "@/components/property/ZoningSection";
import { RuleEvaluationResult } from "@/components/rule-evaluation/RuleEvaluationResult";
import { CapturedRecord } from "./EvidenceRecord";
import { PropertyIssuesSummary } from "./PropertyOverview";
export function PropertyFacts({ profile, onInspect }: {
    profile: PropertyProfile;
    onInspect?: (id: string) => void;
}) {
    const byId = provenanceById(profile);
    return <>
    <PropertyIssuesSummary profile={profile}/>
    <FactsTable title="Lot facts" facts={profile.lot_facts} byId={byId} reproducibility={profile.reproducibility} onInspect={onInspect}/>
    <FactsTable title="Existing building facts" facts={profile.existing_building_facts} byId={byId} reproducibility={profile.reproducibility} onInspect={onInspect}/>
    <section className="card">
      <h2>Identity & source coverage</h2>
      <dl className="architect-definition-list">
        <dt>BBL</dt>
        <dd>
          {profile.identity.bbl}
        </dd>
        <dt>BIN</dt>
        <dd>
          {profile.identity.bins?.length ? profile.identity.bins.join(", ") : "Unknown — not supplied"}
        </dd>
        <dt>Profile address</dt>
        <dd>
          {profile.identity.address?.normalized_address ?? "Unknown — not supplied"}
        </dd>
        <dt>Data completeness</dt>
        <dd>
          {profile.data_completeness ? completenessDisplay(profile.data_completeness).headline : "Not supplied"}
        </dd>
        <dt>Development intent</dt>
        <dd>
          {profile.project_intent.objectives?.length ? profile.project_intent.objectives.join(", ") : "Not recorded"}
        </dd>
        <dt>Profile geometry</dt>
        <dd>
          {profile.identity.geometry?.type ?? "Not included in this profile"}
        </dd>
      </dl>
      <CapturedRecord value={profile.identity} label="Full identity record"/>
      <CapturedRecord value={profile.status_dimensions} label="All source and analysis status dimensions"/>
    </section>
  </>;
}
export function ZoningView({ profile, evaluation }: {
    profile: PropertyProfile;
    evaluation: RuleEvaluation | null;
}) {
    const features = (profile.zoning.mapped_features ?? []).map(mappedFeatureView);
    const absentFlags = [["landmark", "Landmark"], ["histdist", "Historic district"], ["firm07_flag", "2007 FIRM flood flag"], ["pfirm15_flag", "2015 preliminary FIRM flood flag"]].filter(([key]) => !features.some(feature => feature.feature === key && feature.hasValue));
    return <>
    <PropertyIssuesSummary profile={profile}/>
    <ZoningSection profile={profile} byId={provenanceById(profile)}/>
    <section className="card">
      <h2>Additional flags</h2>
      <dl className="architect-definition-list">
        {absentFlags.map(([key, label]) => <div key={key}>
          <dt>
            {label}
          </dt>
          <dd>Unknown — not supplied</dd>
        </div>)}
        <dt>Pending land-use actions</dt>
        <dd>Unknown — source not connected</dd>
      </dl>
    </section>
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
    {evaluation ? <details className="card architect-disclosure">
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
