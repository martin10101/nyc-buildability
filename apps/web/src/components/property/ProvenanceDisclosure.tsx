import { formatValue, urlHost } from "@/lib/format";
import type { ProvenanceRecord, Reproducibility } from "@/lib/property-profile";

/**
 * Per-fact provenance drill-down (PRD sections 9/19; task M2-T001 output 2).
 *
 * Uses a native <details> disclosure: keyboard-accessible without JS.
 * Renders ONLY documented source_fact keys from the record; the dataset id
 * and request-URL host come from the documented profile-level
 * `reproducibility` object (the per-record dataset_id/request_url keys the
 * builder also emits are NOT documented in source_fact.schema.json and are
 * deliberately not consumed).
 */
export function ProvenanceDisclosure({
  records,
  reproducibility,
  label,
  joinNote,
}: {
  records: ProvenanceRecord[];
  reproducibility?: Reproducibility;
  /** Accessible name for the disclosure, e.g. "Source for Lot area". */
  label: string;
  /** Optional note about how the join was made (D5 fallback labeling). */
  joinNote?: string;
}) {
  if (records.length === 0) {
    return (
      <p className="provenance-details">
        Provenance not linkable for this value — the profile carries no
        resolvable provenance record. This gap is shown, never hidden.
      </p>
    );
  }
  return (
    <details className="provenance-details">
      <summary>{label}</summary>
      {joinNote ? <p className="section-note">{joinNote}</p> : null}
      {records.map((record) => (
        <div className="provenance-body" key={record.provenance_id}>
          <dl>
            <dt>Source</dt>
            <dd>{record.source_id}</dd>
            <dt>Original field</dt>
            <dd>{record.original_field_name}</dd>
            <dt>Original value</dt>
            <dd>{formatValue(record.original_value)}</dd>
            <dt>Normalized value</dt>
            <dd>{formatValue(record.normalized_value)}</dd>
            {record.units != null ? (
              <>
                <dt>Units</dt>
                <dd>{record.units}</dd>
              </>
            ) : null}
            <dt>Dataset version</dt>
            <dd>{record.dataset_version}</dd>
            <dt>Retrieved at</dt>
            <dd>{record.retrieved_at}</dd>
            <dt>Effective date</dt>
            <dd>
              {record.effective_date ??
                "not published by the source (shown explicitly, not omitted)"}
            </dd>
            <dt>Conflict status</dt>
            <dd>{record.conflict_status}</dd>
            {reproducibility ? (
              <>
                <dt>Dataset id</dt>
                <dd>{reproducibility.dataset_id}</dd>
                <dt>Retrieved from</dt>
                <dd>{urlHost(reproducibility.request_url)}</dd>
              </>
            ) : null}
          </dl>
        </div>
      ))}
    </details>
  );
}
