import { CoverageBadge } from "./CoverageBadge";
import { ProvenanceDisclosure } from "./ProvenanceDisclosure";
import { fieldLabel, formatValue } from "@/lib/format";
import { resolveFactProvenance } from "@/lib/provenance";
import type {
  FactValue,
  Reproducibility,
  SourceFact,
} from "@/lib/contract";

/**
 * Confirmed official facts: value + units + per-fact coverage status +
 * provenance drill-down (task M2-T001 output 1). Values are rendered
 * verbatim from the canonical profile — no computation, no defaults.
 */
export function FactsTable({
  title,
  note,
  facts,
  byId,
  reproducibility,
}: {
  title: string;
  note?: string;
  facts: Record<string, FactValue>;
  byId: Map<string, SourceFact>;
  reproducibility?: Reproducibility;
}) {
  const entries = Object.entries(facts);
  if (entries.length === 0) {
    return (
      <section className="card">
        <h2 className="section-title">{title}</h2>
        <p className="section-note">
          The official record contains no facts in this group for this
          property.
        </p>
      </section>
    );
  }
  return (
    <section className="card">
      <h2 className="section-title">{title}</h2>
      {note ? <p className="section-note">{note}</p> : null}
      <div className="table-scroll">
      <table className="facts-table">
        <thead>
          <tr>
            <th scope="col">Fact</th>
            <th scope="col">Value</th>
            <th scope="col">Coverage status</th>
            <th scope="col">Source</th>
          </tr>
        </thead>
        <tbody>
          {entries.map(([field, fact]) => {
            const record = resolveFactProvenance(fact.provenance_ref, byId);
            return (
              <tr key={field}>
                <th scope="row" style={{ textTransform: "none", fontSize: "0.92rem" }}>
                  {fieldLabel(field)}
                </th>
                <td>
                  <span className="fact-value">{formatValue(fact.value)}</span>
                  {fact.units ? (
                    <span className="fact-units"> {fact.units}</span>
                  ) : null}
                </td>
                <td>
                  {fact.coverage_status ? (
                    <CoverageBadge status={fact.coverage_status} />
                  ) : (
                    <span className="section-note">not labeled</span>
                  )}
                </td>
                <td>
                  <ProvenanceDisclosure
                    records={record ? [record] : []}
                    reproducibility={reproducibility}
                    label={`Source for ${fieldLabel(field)}`}
                  />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      </div>
    </section>
  );
}
