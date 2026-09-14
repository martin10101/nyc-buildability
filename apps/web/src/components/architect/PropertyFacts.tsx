"use client";
import { useState } from "react";
import type { PropertyProfile } from "@/lib/contract";
import { completenessDisplay } from "@/lib/coverage";
import { fieldLabel, formatValue } from "@/lib/format";
import { provenanceById } from "@/lib/provenance";
import { FactsTable } from "@/components/property/FactsTable";
import { CapturedRecord } from "./EvidenceRecord";
import { PropertyIssuesSummary } from "./PropertyOverview";

export function PropertyFacts({ profile, onInspect, allSections = false }: {
  profile: PropertyProfile;
  onInspect?: (id: string) => void;
  allSections?: boolean;
}) {
  const [group, setGroup] = useState<"lot" | "building" | "identity">("lot");
  const [query, setQuery] = useState("");
  const byId = provenanceById(profile);
  const groups = [
    { id: "lot", label: "Lot", title: "Lot facts", facts: profile.lot_facts },
    { id: "building", label: "Building", title: "Existing building facts", facts: profile.existing_building_facts },
  ] as const;
  return <>
    {!allSections ? <>
      <PropertyIssuesSummary profile={profile}/>
      <section className="card architect-fact-controls" aria-label="Property fact controls">
        <div className="architect-segments" role="group" aria-label="Property fact groups">
          {(["lot", "building", "identity"] as const).map(id => <button key={id} type="button" aria-pressed={group === id} onClick={() => { setGroup(id); setQuery(""); }}>{id === "lot" ? "Lot" : id === "building" ? "Building" : "Identity"}</button>)}
        </div>
        {group !== "identity" ? <label className="architect-fact-filter">Filter facts<input className="text-input" value={query} onChange={event => setQuery(event.target.value)} placeholder="Name, value or units…"/></label> : null}
      </section>
    </> : null}
    {groups.filter(item => allSections || item.id === group).map(item => {
      const entries = Object.entries(item.facts);
      const visible = allSections ? entries : entries.filter(([key, fact]) => `${key} ${fieldLabel(key)} ${formatValue(fact.value)} ${fact.units ?? ""}`.toLowerCase().includes(query.trim().toLowerCase()));
      return <div key={item.id}>
        {!allSections ? <p className="section-note" role="status">{visible.length} of {entries.length} {item.label.toLowerCase()} fields</p> : null}
        {visible.length || !entries.length ? <FactsTable title={item.title} facts={Object.fromEntries(visible)} byId={byId} reproducibility={profile.reproducibility} onInspect={onInspect}/> : <section className="card"><h2>{item.title}</h2><p>No facts match this filter.</p><button className="architect-text-button" onClick={() => setQuery("")}>Clear filter</button></section>}
      </div>;
    })}
    {allSections || group === "identity" ? <section className="card">
      <h2>Identity &amp; source coverage</h2>
      <dl className="architect-definition-list">
        <dt>BBL</dt><dd>{profile.identity.bbl}</dd>
        <dt>BIN</dt><dd>{profile.identity.bins?.length ? profile.identity.bins.join(", ") : "Unknown — not supplied"}</dd>
        <dt>Profile address</dt><dd>{profile.identity.address?.normalized_address ?? "Unknown — not supplied"}</dd>
        <dt>Data completeness</dt><dd>{profile.data_completeness ? completenessDisplay(profile.data_completeness).headline : "Not supplied"}</dd>
        <dt>Development intent</dt><dd>{profile.project_intent.objectives?.length ? profile.project_intent.objectives.join(", ") : "Not recorded"}</dd>
        <dt>Profile geometry</dt><dd>{profile.identity.geometry?.type ?? "Not included in this profile"}</dd>
      </dl>
      <CapturedRecord value={profile.identity} label="Full identity record"/>
      <CapturedRecord value={profile.status_dimensions} label="All source and analysis status dimensions"/>
    </section> : null}
  </>;
}
