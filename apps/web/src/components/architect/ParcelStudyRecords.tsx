"use client";

import type { LookupOutcome } from "@/lib/api";
import type { PropertyProfile } from "@/lib/contract";
import type { LotOutlineOutcome } from "@/lib/lot-geometry-api";
import type { ParcelStudyRecord } from "@/lib/architect/use-parcel-study-records";
import { residentialReference } from "@/lib/architect/development-limits";
import { fieldLabel, formatValue } from "@/lib/format";
import { provenanceById } from "@/lib/provenance";
import { FactsTable } from "@/components/property/FactsTable";
import { ProvenanceDisclosure } from "@/components/property/ProvenanceDisclosure";

function profileStatus(outcome: LookupOutcome | null): string {
  if (!outcome) return "Loading property records";
  switch (outcome.kind) {
    case "profile": return "City record";
    case "no_match": return "No property record found";
    case "client_timeout": return "Property lookup timed out";
    case "validation_failure": return "Property record requires review";
    case "aborted": return "Property lookup cancelled";
    default: return "Property records unavailable";
  }
}

function outlineStatus(outcome: LotOutlineOutcome | null): string {
  if (!outcome) return "Loading outline";
  if (outcome.kind === "document") {
    if (outcome.view.geometryUnusable) return "Outline unusable";
    switch (outcome.view.outcome) {
      case "single_lot": return outcome.view.reviewRequired ? "Outline needs review" : "Display outline available";
      case "multiple_features": return "Multiple outline records";
      case "invalid_geometry": return "Outline invalid";
      case "no_outline": return "No outline found";
    }
  }
  if (outcome.kind === "error" && outcome.state === "result_mismatch") return "Outline identity mismatch";
  return outcome.kind === "route_absent" ? "Outline service unavailable" : "Outline unavailable";
}

function LookupDetail({ outcome }: { outcome: LookupOutcome | LotOutlineOutcome | null }) {
  if (!outcome || outcome.kind === "profile" || outcome.kind === "document") return null;
  return <details className="architect-disclosure parcel-study-record-detail">
    <summary>Lookup details</summary>
    {"message" in outcome ? <p>{outcome.message}</p> : null}
    {"problems" in outcome ? <ul>{outcome.problems.map((problem, index) => <li key={index}>{problem}</li>)}</ul> : null}
    {"timeoutMs" in outcome ? <p>Time budget: {outcome.timeoutMs} ms. This lookup is safe to retry.</p> : null}
    {"correlationId" in outcome && outcome.correlationId ? <p>Reference: {outcome.correlationId}</p> : null}
    {"receivedState" in outcome ? <p>Unexpected response: HTTP {outcome.httpStatus}; state {outcome.receivedState ?? "absent"}.</p> : null}
    {"state" in outcome ? <p>Reported state: {outcome.state}</p> : null}
  </details>;
}

function RecordedFact({ profile, field }: { profile: PropertyProfile; field: string }) {
  const fact = profile.lot_facts[field];
  const records = fact ? profile.provenance.filter(item => item.provenance_id === fact.provenance_ref) : [];
  const conflict = records.some(item => item.conflict_status === "conflicting")
    || profile.conflicts.some(item => item.field === field && item.resolution === "unresolved");
  return <div>
    <dt>{fieldLabel(field)} · recorded</dt>
    <dd>{fact?.value == null ? "Unknown" : <>{formatValue(fact.value)}{fact.units ? ` ${fact.units}` : ""}</>}</dd>
    {conflict ? <span className="parcel-study-badge">Conflicting records</span> : null}
    {fact && records.length === 0 ? <span className="parcel-study-badge">Source link missing</span> : null}
  </div>;
}

function ProfileSources({ profile }: { profile: PropertyProfile }) {
  const metadata = profile.reproducibility;
  return <details className="architect-disclosure parcel-study-record-detail">
    <summary>Sources and record limits</summary>
    <p className="section-note">Recorded lot dimensions are not buildable dimensions. Recorded zoning is not a zoning-boundary determination. PLUTO FAR is a source reference, not an evaluated development allowance.</p>
    <dl>
      <dt>Retrieved</dt><dd>{metadata?.retrieved_at ?? "Unknown"}</dd>
      <dt>Dataset version</dt><dd>{metadata?.dataset_version ?? "Unknown"}</dd>
      <dt>Source freshness</dt><dd>{metadata?.staleness ? (metadata.staleness.stale ? "Stale source record" : "Not marked stale by the source service") : "Not supplied"}</dd>
    </dl>
    {profile.conflicts.length > 0 ? <details className="architect-disclosure">
      <summary>Source conflicts ({profile.conflicts.length})</summary>
      <ul>{profile.conflicts.map((conflict, index) => <li key={index}>
        <strong>{fieldLabel(conflict.field)}</strong> · {conflict.resolution}
        <ul>{conflict.values.map((entry, valueIndex) => <li key={valueIndex}>{entry.source_id}: {formatValue(entry.value)}</li>)}</ul>
      </li>)}</ul>
    </details> : null}
    {profile.missing_inputs.length > 0 ? <details className="architect-disclosure">
      <summary>Missing source inputs ({profile.missing_inputs.length})</summary>
      <ul>{profile.missing_inputs.map((input, index) => <li key={index}>
        {fieldLabel(input.field)} · {input.criticality}{input.reason ? ` · ${input.reason}` : ""}
      </li>)}</ul>
    </details> : null}
    <ProvenanceDisclosure records={profile.provenance} reproducibility={metadata} label="Captured sources and values" />
    <details className="architect-disclosure">
      <summary>All recorded lot facts</summary>
      <FactsTable title="Recorded lot facts" facts={profile.lot_facts} byId={provenanceById(profile)} reproducibility={metadata} />
    </details>
  </details>;
}

function ProfileFacts({ profile }: { profile: PropertyProfile }) {
  const reference = residentialReference(profile);
  const unresolved = profile.conflicts.filter(item => item.resolution === "unresolved").length;
  const sourceConflict = profile.provenance.some(item => item.conflict_status === "conflicting");
  return <>
    <div className="parcel-study-record-status">
      <span className="parcel-study-badge">City record</span>
      {profile.reproducibility?.staleness?.stale ? <span className="parcel-study-badge">Stale source</span> : null}
      {unresolved > 0 || sourceConflict ? <span className="parcel-study-badge">Source conflicts</span> : null}
      {profile.missing_inputs.length > 0 ? <span className="parcel-study-badge">Missing inputs</span> : null}
    </div>
    <dl className="parcel-study-facts">
      <RecordedFact profile={profile} field="lotarea" />
      <RecordedFact profile={profile} field="lotfront" />
      <RecordedFact profile={profile} field="lotdepth" />
      <div><dt>Zoning · city record</dt><dd>{profile.zoning.districts?.length ? profile.zoning.districts.join(" / ") : "Unknown"}</dd></div>
      <div><dt>Residential FAR · PLUTO reference</dt><dd>{reference.value === null ? reference.status : formatValue(reference.value)}</dd></div>
    </dl>
    <ProfileSources profile={profile} />
    <details className="architect-disclosure parcel-study-record-detail">
      <summary>Existing building information</summary>
      <p className="section-note">Source records only. These values are not a calculation of zoning floor area used or development rights remaining.</p>
      <FactsTable title="Recorded existing building facts" facts={profile.existing_building_facts} byId={provenanceById(profile)} reproducibility={profile.reproducibility} />
    </details>
  </>;
}

function OutlineSources({ outcome }: { outcome: LotOutlineOutcome | null }) {
  if (outcome?.kind !== "document") return <LookupDetail outcome={outcome} />;
  const { view } = outcome;
  return <details className="architect-disclosure parcel-study-record-detail">
    <summary>Outline source and accuracy</summary>
    <p>{view.accuracyNote}</p>
    <p>{view.disclaimer}</p>
    <p>{view.attribution}</p>
    <dl>
      <dt>Source</dt><dd>{view.source.sourceId ?? "Unknown"}</dd>
      <dt>Dataset version</dt><dd>{view.source.datasetVersion ?? "Unknown"}</dd>
      <dt>Retrieved</dt><dd>{view.source.retrievedAt ?? "Unknown"}</dd>
      <dt>Review required</dt><dd>{view.reviewRequired ? "Yes" : "No"}</dd>
      <dt>Condo classification</dt><dd>{view.condoClassification.classification}</dd>
    </dl>
    {view.condoClassification.note ? <p>{view.condoClassification.note}</p> : null}
    {view.noOutlineReason ? <p>Outline absence: {view.noOutlineReason}</p> : null}
    {view.notes.length > 0 ? <ul>{view.notes.map((note, index) => <li key={index}>{note}</li>)}</ul> : null}
  </details>;
}

/** No totals, derived dimensions, or development allowances on this surface. */
export function ParcelStudyRecords({ records }: { records: readonly ParcelStudyRecord[] }) {
  return <section className="parcel-study-records" aria-label="Source records for the study parcels">
    <h3>Parcel records</h3>
    <p className="section-note">Recorded dimensions and FAR references · not buildable dimensions or development allowances.</p>
    <div className="parcel-study-record-grid">
      {records.map(record => {
        const profile = record.profileOutcome?.kind === "profile" && record.profileOutcome.profile.identity.bbl === record.bbl
          ? record.profileOutcome.profile : null;
        const outline = record.outlineOutcome?.kind === "document" && record.outlineOutcome.view.bbl !== record.bbl
          ? null : record.outlineOutcome;
        const wrongProfile = record.profileOutcome?.kind === "profile" && !profile;
        const wrongOutline = record.outlineOutcome?.kind === "document" && !outline;
        return <article className="parcel-study-record card" key={record.bbl} aria-label={`Source records for BBL ${record.bbl}`} aria-busy={record.loading}>
          <h4>BBL {record.bbl}</h4>
          {profile ? <ProfileFacts profile={profile} /> : <>
            <p role="status">{wrongProfile ? "Property identity mismatch" : profileStatus(record.profileOutcome)}</p>
            <LookupDetail outcome={record.profileOutcome} />
          </>}
          <p className="parcel-study-record-outline">{wrongOutline ? "Outline identity mismatch" : outlineStatus(outline)}</p>
          <OutlineSources outcome={outline} />
        </article>;
      })}
    </div>
  </section>;
}
