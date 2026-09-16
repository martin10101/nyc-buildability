import Link from "next/link";
import type { PropertyProfile } from "@/lib/contract";
import type { Scenario } from "@/lib/scenario-contract";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import { fieldLabel } from "@/lib/format";
import { provenanceById } from "@/lib/provenance";
import { propertyHref } from "@/lib/architect/navigation";
import { LotOutlineMap } from "@/components/address/LotOutlineMap";
import { FactsTable } from "@/components/property/FactsTable";
import { DevelopmentLimits } from "./DevelopmentLimits";
export { DraftHeadline } from "./DevelopmentLimits";
export function PropertyIssuesSummary({ profile }: {
    profile: PropertyProfile;
}) {
    const conflicts = profile.conflicts.filter(item => item.resolution === "unresolved");
    const critical = profile.missing_inputs.filter(item => item.criticality === "critical");
    return <>
    {conflicts.length > 0 ? <div className="architect-alert" role="status">
      <strong>Unresolved data conflicts</strong>
      <p>
        {conflicts.map(item => fieldLabel(item.field)).join(" · ")}
      </p>
      <Link href={propertyHref(profile.identity.bbl, "issues")}>Review conflicting source values →</Link>
    </div> : null}
    {critical.length > 0 ? <div className="architect-alert" role="status">
      <strong>Critical inputs missing</strong>
      <p>
        {critical.map(item => fieldLabel(item.field)).join(" · ")}
      </p>
      <Link href={propertyHref(profile.identity.bbl, "issues")}>Review missing inputs →</Link>
    </div> : null}
    {profile.reproducibility?.staleness?.stale ? <p className="architect-alert">The property source is stale. Captured dates and retrieval status are available in Evidence.</p> : null}
  </>;
}
export function PropertyOverview({ profile, scenario, evaluation = null, onInspect }: {
    profile: PropertyProfile;
    scenario: Scenario | null;
    evaluation?: RuleEvaluation | null;
    onInspect: (id: string) => void;
}) {
    const bbl = profile.identity.bbl;
    return <>
    <PropertyIssuesSummary profile={profile}/>
    <div className="architect-overview-grid">
      <div>
        <DevelopmentLimits profile={profile} scenario={scenario} evaluation={evaluation} onInspect={onInspect}/>
        <Link className="primary-button" href={propertyHref(bbl, "zoning")}>View zoning details <span aria-hidden="true">→</span></Link>
      </div>
      <section className="card architect-map-card">
        <div className="architect-panel-heading">
          <h2>Site context</h2>
          <a href={`https://zola.planning.nyc.gov/bbl/${bbl}`} target="_blank" rel="noopener noreferrer">Open ZoLa ↗</a>
        </div>
        <LotOutlineMap bbl={bbl} context/>
      </section>
    </div>
    <details className="card architect-disclosure architect-existing-building">
      <summary>Existing building information</summary>
      <FactsTable title="Existing building facts" facts={profile.existing_building_facts} byId={provenanceById(profile)} reproducibility={profile.reproducibility} onInspect={onInspect}/>
      <Link href={propertyHref(bbl, "facts")}>All property facts →</Link>
    </details>
  </>;
}
