"use client";
import { useEffect, useRef } from "react";
import type { PropertyProfile } from "@/lib/contract";
import { datasetLandingUrl, plutoRecordUrl } from "@/lib/provenance-link";
import { CapturedRecord, EvidenceRecord } from "./EvidenceRecord";
export function EvidenceInspector({ profile, selected, onClose, onEvidence }: {
    profile: PropertyProfile;
    selected: string | null;
    onClose: () => void;
    onEvidence: () => void;
}) {
    const panelRef = useRef<HTMLElement | null>(null);
    useEffect(() => {
        if (!selected)
            return;
        const trigger = document.activeElement as HTMLElement | null;
        const panel = panelRef.current;
        panel?.focus();
        const handleEscape = (event: KeyboardEvent) => { if (event.key === "Escape")
            onClose(); };
        panel?.addEventListener("keydown", handleEscape);
        return () => { panel?.removeEventListener("keydown", handleEscape); trigger?.focus(); };
    }, [selected, onClose]);
    const record = profile.provenance.find(item => item.provenance_id === selected);
    const source = profile.reproducibility;
    const link = datasetLandingUrl(source?.dataset_id);
    const currentRecordUrl = plutoRecordUrl(source?.source_id, source?.dataset_id, profile.identity.bbl);
    return <aside ref={panelRef} tabIndex={-1} className={`architect-inspector ${selected ? "has-selection" : ""}`} aria-label="Contextual evidence inspector">
    <div className="architect-inspector-heading">
      <h2>
        {selected ? record ? "Fact evidence" : "Source record unavailable" : "Sources & review"}
      </h2>
      {selected ? <button type="button" className="architect-text-button" onClick={onClose}>Close</button> : null}
    </div>
    {record ? <EvidenceRecord record={record} profile={profile}/> : selected ? <p role="status">The source record for reference <code>{selected}</code> was not supplied with this property.</p> : <>
      <p className="architect-eyebrow">Captured property record</p>
      <h3>
        {source?.source_id ?? "Source not supplied"}
      </h3>
      <p>
        {currentRecordUrl ? <><a href={currentRecordUrl} target="_blank" rel="noopener noreferrer">Current PLUTO record (JSON)</a><br /></> : null}
        {link ? <a className="section-note" href={link} target="_blank" rel="noopener noreferrer">About this dataset</a> : <span className="section-note">Official dataset link not supplied.</span>}
      </p>
      {currentRecordUrl ? <p className="section-note">Current records may differ from the captured evidence shown here.</p> : null}
      <dl className="architect-definition-list">
        <dt>Release</dt>
        <dd>
          {source?.dataset_version ?? "Not published"}
        </dd>
        <dt>Captured</dt>
        <dd>
          {source?.retrieved_at ?? "Not supplied"}
        </dd>
        <dt>Profile version</dt>
        <dd>
          {profile.profile_version.contract_version}
        </dd>
      </dl>
      <CapturedRecord value={source} label="Full captured source metadata"/>
      {source?.staleness?.stale ? <p className="architect-alert">Cached source is stale. Review retrieval details before using these facts.</p> : null}
      <hr />
      <h3>Review</h3>
      <p>Draft analysis · Professional review required</p>
      <p className="section-note">Recorded confirmations: {profile.user_confirmations.length}
      </p>
      <button type="button" className="architect-text-button" onClick={onEvidence}>Open evidence and review history →</button>
    </>}
  </aside>;
}
