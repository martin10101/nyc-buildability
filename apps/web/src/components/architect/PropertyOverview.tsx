"use client";
import type { ReactNode } from "react";
import Link from "next/link";
import type { PropertyProfile } from "@/lib/contract";
import type { Scenario } from "@/lib/scenario-contract";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import { fieldLabel } from "@/lib/format";
import { provenanceById } from "@/lib/provenance";
import { zolaLotUrl } from "@/lib/provenance-link";
import { propertyHref } from "@/lib/architect/navigation";
import { useCondoRecords } from "@/lib/condo-records";
import { LotOutlineMap } from "@/components/address/LotOutlineMap";
import { FactsTable } from "@/components/property/FactsTable";
import { ABSENT_BBL_MAP_LINK_NOTE, ZOLA_LOT_LINK_LABEL } from "./AddressAutocomplete";
import { DevelopmentLimits } from "./DevelopmentLimits";
import { OverviewExceptionStrip } from "./OverviewExceptionStrip";
import { ZoningContextPanel } from "./ZoningContextPanel";
import { ParcelStudyPanel } from "./ParcelStudyPanel";
// M5-T122 (D-086 P3b, AS-2): the condo RECORDS surface moved to
// CondoRecordsSection.tsx. PropertyOverview stays a compatibility FACADE for every
// public condo name other modules import from it today — ReportView.tsx imports
// CondoRecordsChannelSection + deriveCondoSurface; the tests import those plus
// PropertyOverview; deriveCondoDisplay + condoWithholdsAllowances stay part of the
// public surface — so NO importer is edited. One import (used locally by
// PropertyOverview) plus a local re-export keeps the facade with no duplicate-module
// import statement.
import {
    deriveCondoSurface,
    CondoRecordsChannelSection,
    deriveCondoDisplay,
    condoWithholdsAllowances,
    type CondoDisplayState,
    type CondoSurfaceDecision,
} from "./CondoRecordsSection";
export { DraftHeadline } from "./DevelopmentLimits";
export {
    CondoRecordsChannelSection,
    deriveCondoSurface,
    deriveCondoDisplay,
    condoWithholdsAllowances,
};
export type { CondoDisplayState, CondoSurfaceDecision };
function OverviewRecordDetails({ multiLot, children }: { multiLot: boolean; children: ReactNode }) {
    return multiLot ? <details className="parcel-study-source-summary">
      <summary>Entered lot record and development-limit status</summary>{children}
    </details> : <>{children}</>;
}
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
    // DB-005: the only ZoLa link on this surface goes through the validated
    // helper (null on a non-canonical BBL -> render NO link, never a raw
    // template string). Same discipline as the accepted M5-T032 work.
    const siteZolaUrl = zolaLotUrl(bbl);
    // M5-T052 (D-073-R006): the production per-BBL condo-records channel and the
    // accepted profile fail-safe guard fold into ONE decision (deriveCondoSurface,
    // now in CondoRecordsSection), so the fail-safe guard, the records section, and
    // the substitution explanation can never disagree. A multi-lot / unresolved /
    // typed-error condo withholds EVERY computed development allowance — even when a
    // scenario or rule evaluation matching this BBL is present and would otherwise
    // be displayable. A resolved single base lot (allow path) and a non-condo
    // property are unaffected, so their allowances render normally; the records
    // section renders UNDER the professional-review fail-safe, never instead of it.
    const condoRecordsOutcome = useCondoRecords(bbl);
    const condo = deriveCondoSurface(profile, condoRecordsOutcome);
    const withholdAllowances = condo.withholdAllowances;
    const shownScenario = withholdAllowances ? null : scenario;
    const shownEvaluation = withholdAllowances ? null : evaluation;
    const studyRecords = condo.recordsView?.outcome === "multi_lot_set" ? condo.recordsView : null;
    return <>
    <OverviewExceptionStrip profile={profile}/>
    {studyRecords ? <ParcelStudyPanel requestedBbl={bbl} records={studyRecords} recordsConflict={condo.conflict}/> : null}
    {/* M5-T119 (D-086 P3a, spec §5.3 / frame O-D): the two-column overview
        canvas. The site map/context is the wider (~55%) LEFT column and the
        limit matrix the ~45% RIGHT column, stacking to a single column at
        ≤950px (architect.css .architect-overview-grid). The former separate
        conflict/missing/stale alerts now fold into OverviewExceptionStrip
        above; PropertyIssuesSummary stays byte-identical for the printed brief
        (ReportView) and the scenarios view. */}
    <OverviewRecordDetails multiLot={!!studyRecords}>
    <div className="architect-overview-grid">
      <section className="card architect-map-card">
        <div className="architect-panel-heading">
          <h2>Site context</h2>
          {siteZolaUrl ? (
            <a href={siteZolaUrl} target="_blank" rel="noopener noreferrer" data-testid="site-zola-link">{ZOLA_LOT_LINK_LABEL} <span aria-hidden="true">↗</span></a>
          ) : (
            // DB-019b/DB-024(b): honest absence when there is no canonical BBL,
            // rendered from the single shared ABSENT_BBL_MAP_LINK_NOTE constant so
            // this note stays byte-identical to the AddressConfirmCard and
            // ZoningContextPanel notes. Never a raw template-string URL for a lot
            // the source did not identify.
            <span className="section-note" data-testid="site-zola-absent">{ABSENT_BBL_MAP_LINK_NOTE}</span>
          )}
        </div>
        {studyRecords ? <p className="section-note">The study above displays the recorded base parcels. This entered condo lot is an identity reference, not additional land.</p> : <LotOutlineMap bbl={bbl} context/>}
      </section>
      <div>
        <DevelopmentLimits profile={profile} scenario={shownScenario} evaluation={shownEvaluation} onInspect={onInspect}/>
        <Link className="primary-button" href={propertyHref(bbl, "zoning")}>View zoning details <span aria-hidden="true">→</span></Link>
      </div>
    </div>
    </OverviewRecordDetails>
    <div id="condo-records"><CondoRecordsChannelSection decision={condo}/></div>
    <ZoningContextPanel profile={profile}/>
    <details className="card architect-disclosure architect-existing-building">
      <summary>Existing building information</summary>
      <FactsTable title="Existing building facts" facts={profile.existing_building_facts} byId={provenanceById(profile)} reproducibility={profile.reproducibility} onInspect={onInspect}/>
      <Link href={propertyHref(bbl, "facts")}>All property facts →</Link>
    </details>
  </>;
}
