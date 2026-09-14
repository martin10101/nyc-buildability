"use client";
import { useState } from "react";
import type { PropertyProfile } from "@/lib/contract";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import type { Scenario } from "@/lib/scenario-contract";
import type { SelectedAddress } from "@/lib/architect/selected-address";
import { fieldLabel } from "@/lib/format";
import { CapturedRecord, EvidenceRecord } from "./EvidenceRecord";
import { CalculationEvidence } from "./CalculationEvidence";
export function EvidenceWorkspace({ profile, evaluation, scenario, address, selection, onSelect }: {
    profile: PropertyProfile;
    evaluation: RuleEvaluation | null;
    scenario: Scenario | null;
    address: SelectedAddress | null;
    selection: string;
    onSelect: (id: string) => void;
}) {
    const [query, setQuery] = useState("");
    const records = profile.provenance.filter(record => `${record.original_field_name} ${record.source_id}`.toLowerCase().includes(query.toLowerCase()));
    const record = profile.provenance.find(item => item.provenance_id === selection);
    return <div className="architect-evidence-layout">
    <section className="card architect-evidence-list" aria-label="Evidence index">
      <h2>Evidence</h2>
      <label className="visually-hidden" htmlFor="evidence-search">Search evidence</label>
      <input id="evidence-search" className="text-input" placeholder="Search evidence…" value={query} onChange={event => setQuery(event.target.value)}/>
      <button className="architect-evidence-choice" aria-pressed={selection === "calculation"} onClick={() => onSelect("calculation")}>Calculation and rule trace</button>
      <button className="architect-evidence-choice" aria-pressed={selection === "profile"} onClick={() => onSelect("profile")}>Full property and review record</button>
      {address ? <button className="architect-evidence-choice" aria-pressed={selection === "address"} onClick={() => onSelect("address")}>Confirmed address match</button> : null}
      <p className="architect-eyebrow">Source facts · {records.length}
      </p>
      {records.map(item => <button className="architect-evidence-choice" key={item.provenance_id} aria-pressed={item.provenance_id === selection} onClick={() => onSelect(item.provenance_id)}>
        {fieldLabel(item.original_field_name)}
      </button>)}
      {records.length === 0 ? <p className="section-note">No matching source facts.</p> : null}
    </section>
    <section className="card architect-evidence-detail" aria-label="Selected evidence">
      {record ? <EvidenceRecord record={record} profile={profile}/> : selection === "profile" ? <>
        <h2>Complete property record</h2>
        <p>Every supplied field, source, conflict and review record is included below.</p>
        <CapturedRecord value={profile.profile_version} label="Profile version and generated date"/>
        <CapturedRecord value={profile.reproducibility} label="Retrieval, source version and staleness"/>
        <CapturedRecord value={profile.user_confirmations} label="All recorded confirmations and overrides"/>
        <CapturedRecord value={profile.project_intent} label="Recorded development intent"/>
        <CapturedRecord value={profile} label="Complete property source record"/>
      </> : selection === "address" && address ? <>
        <h2>Confirmed address match</h2>
        <p>
          {address.label}
        </p>
        <p className="section-note">Selected in this browser session at {address.confirmedAt}. BBL {address.bbl} remains the property identity.</p>
        <CapturedRecord value={address.sourceRecord} label="Original address match and source facts"/>
      </> : <CalculationEvidence evaluation={evaluation} scenario={scenario}/>}
    </section>
  </div>;
}
