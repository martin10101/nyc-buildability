import Link from "next/link";
import type { PropertyProfile } from "@/lib/contract";
import type { Scenario } from "@/lib/scenario-contract";
import { fieldLabel, formatValue } from "@/lib/format";
import { propertyHref } from "@/lib/architect/navigation";
import { LotOutlineMap } from "@/components/address/LotOutlineMap";
import { CoverageBadge } from "@/components/property/CoverageBadge";
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
export function DraftHeadline({ scenario }: {
    scenario: Scenario | null;
}) {
    const cap = scenario?.draft_zoning_floor_area_cap_sq_ft;
    return <div className="architect-draft-headline" data-testid="architect-cap">
    <p className="architect-eyebrow">Preliminary potential</p>
    <p className="architect-metric">
      {cap != null ? <>
        {formatValue(cap)}
        <span> sq ft</span>
      </> : scenario ? "No supported cap" : "—"}
    </p>
    <h2>
      {scenario?.cap_label ?? "Draft zoning floor-area cap"}
    </h2>
    <p className="section-note">FAR only · Buildable envelope not assessed</p>
    {scenario ? <>
      <CoverageBadge status={scenario.coverage_status}/>
      {scenario.reasons.length ? <ul className="architect-issue-list">
        {scenario.reasons.map((reason, i) => <li key={i}>
          {reason}
        </li>)}
      </ul> : null}
    </> : null}
  </div>;
}
export function PropertyOverview({ profile, scenario, onInspect }: {
    profile: PropertyProfile;
    scenario: Scenario | null;
    onInspect: (id: string) => void;
}) {
    const bbl = profile.identity.bbl;
    const headlineFacts = [
        ["lotarea", profile.lot_facts.lotarea],
        ["bldgarea", profile.existing_building_facts.bldgarea],
        ["numfloors", profile.existing_building_facts.numfloors],
    ] as const;
    return <>
    <PropertyIssuesSummary profile={profile}/>
    <div className="architect-overview-grid">
      <section className="card architect-map-card">
        <div className="architect-panel-heading">
          <h2>Site context</h2>
          <a href={`https://zola.planning.nyc.gov/bbl/${bbl}`} target="_blank" rel="noopener noreferrer">Open ZoLa ↗</a>
        </div>
        <LotOutlineMap bbl={bbl} context/>
      </section>
      <section className="card architect-overview-result">
        <DraftHeadline scenario={scenario}/>
        <div className="architect-fact-metrics">
          {headlineFacts.map(([field, fact]) => <div key={field}>
            <p>
              {fieldLabel(field)}
            </p>
            <strong>
              {fact ? formatValue(fact.value) : "Unknown"}
            </strong>
            {fact?.units ? <span> {fact.units}
            </span> : null}
            {fact ? <button type="button" className="architect-text-button" onClick={() => onInspect(fact.provenance_ref)}>Source</button> : null}
          </div>)}
        </div>
        <h3>Assessment coverage</h3>
        {scenario ? <div className="table-scroll">
          <table className="facts-table">
            <thead>
              <tr>
                <th scope="col">Check</th>
                <th scope="col">Status</th>
              </tr>
            </thead>
            <tbody>
              {scenario.coverage_matrix.map((row, i) => <tr key={i}>
                <th scope="row">
                  {row.constraint_family}
                </th>
                <td>
                  {row.rule_status_today}
                  {row.blocks_buildable_envelope ? " · Blocks envelope" : ""}
                </td>
              </tr>)}
            </tbody>
          </table>
        </div> : <p className="section-note">Assessment coverage is available when the scenario service returns a supported document.</p>}
        <Link className="primary-button" href={propertyHref(bbl, "zoning")}>View zoning details <span aria-hidden="true">→</span>
        </Link>
      </section>
    </div>
  </>;
}
