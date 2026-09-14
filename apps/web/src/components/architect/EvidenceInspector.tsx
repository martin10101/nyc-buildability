"use client";
import { useEffect, useRef } from "react";
import type { PropertyProfile } from "@/lib/contract";
import { datasetLandingUrl } from "@/lib/provenance-link";
import { EvidenceRecord } from "./EvidenceRecord";
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
    return <aside ref={panelRef} tabIndex={-1} className={`architect-inspector ${selected ? "has-selection" : ""}`} aria-label="Contextual evidence inspector">
    <div className="architect-inspector-heading">
      <h2>
        {record ? "Fact evidence" : "Sources & review"}
      </h2>
      {record ? <button type="button" className="architect-text-button" onClick={onClose}>Close</button> : null}
    </div>
    {record ? <EvidenceRecord record={record} profile={profile}/> : <>
      <p className="architect-eyebrow">Property record</p>
      <h3>
        {source?.source_id ?? "Source not supplied"}
      </h3>
      {link ? <a href={link} target="_blank" rel="noopener noreferrer">Open official dataset ↗</a> : <p className="section-note">Official dataset link not supplied.</p>}
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
