import { fieldLabel, formatValue } from "@/lib/format";
import { sourceFactLinks } from "@/lib/provenance-link";
import type { PropertyProfile, SourceFact } from "@/lib/contract";
/** All record fields stay accessible as escaped text; source URLs never become arbitrary hrefs. */
export function CapturedRecord({ value, label = "Full captured record" }: {
    value: unknown;
    label?: string;
}) {
    return <details className="provenance-details architect-raw">
    <summary>
      {label}
    </summary>
    <pre>
      {JSON.stringify(value, null, 2) ?? "Unknown — no record supplied"}
    </pre>
  </details>;
}
export function EvidenceRecord({ record, profile }: {
    record: SourceFact;
    profile: PropertyProfile;
}) {
    const links = sourceFactLinks(record, profile.reproducibility, profile.identity);
    const confirmations = profile.user_confirmations.filter(item => item.field === record.original_field_name || item.field === record.fact_key);
    return <div className="architect-evidence-record">
    <p className="architect-eyebrow">Captured source fact</p>
    <h3>
      {fieldLabel(record.original_field_name)}
    </h3>
    <p>
      {links.currentRecordUrl ? <><a href={links.currentRecordUrl} target="_blank" rel="noopener noreferrer">Current PLUTO record (JSON)</a><br /></> : null}
      {links.datasetUrl ? <a className="section-note" href={links.datasetUrl} target="_blank" rel="noopener noreferrer">About this dataset</a> : <span className="section-note">No safe official dataset link is available in this record.</span>}
    </p>
    {links.currentRecordUrl ? <p className="section-note">Current records may differ from the captured evidence shown here.</p> : null}
    <dl className="architect-definition-list">
      <dt>Original field</dt>
      <dd><code>{record.original_field_name}</code></dd>
      <dt>Original value</dt>
      <dd>
        {formatValue(record.original_value)}
      </dd>
      <dt>Normalized value</dt>
      <dd>
        {formatValue(record.normalized_value)}
      </dd>
      <dt>Units</dt>
      <dd>
        {record.units ?? "Not supplied"}
      </dd>
      <dt>Transformation</dt>
      <dd>No transformation steps recorded. Original and normalized values are shown above.</dd>
      <dt>Source</dt>
      <dd>
        {record.source_id}
      </dd>
      <dt>Version</dt>
      <dd>
        {record.dataset_version}
      </dd>
      <dt>Captured</dt>
      <dd>
        {record.retrieved_at}
      </dd>
      <dt>Effective date</dt>
      <dd>
        {record.effective_date ?? "Not published by the source"}
      </dd>
      <dt>Source conflict</dt>
      <dd>
        {record.conflict_status}
      </dd>
      <dt>Fact review</dt>
      <dd>
        {record.user_confirmed_or_overridden}
      </dd>
    </dl>
    <details className="provenance-details">
      <summary>Review history</summary>
      {confirmations.length ? <CapturedRecord value={confirmations} label="Recorded confirmations and overrides"/> : <p className="section-note">No confirmation or override history is supplied for this fact.</p>}
    </details>
    <CapturedRecord value={record} label="Full captured source record"/>
  </div>;
}
