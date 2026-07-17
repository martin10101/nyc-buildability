import { CoverageBadge } from "./CoverageBadge";
import { ProvenanceDisclosure } from "./ProvenanceDisclosure";
import {
  mappedFeatureView,
  type PropertyProfile,
  type SourceFact,
} from "@/lib/contract";
import { fieldLabel, formatValue } from "@/lib/format";
import {
  resolveDistrictProvenance,
  resolveFactProvenance,
  type ZoningArrayName,
} from "@/lib/provenance";

const JOIN_NOTES: Record<string, string | undefined> = {
  provenance_map: undefined,
  original_field_name_fallback:
    "Linked by source column name (this profile carries no direct " +
    "district-provenance map — the documented contract-1.0.0 situation).",
  none: undefined,
};

export function ZoningValueList({
  profile,
  byId,
  arrayName,
  heading,
  emptyText,
}: {
  profile: PropertyProfile;
  byId: Map<string, SourceFact>;
  arrayName: ZoningArrayName;
  heading: string;
  emptyText: string;
}) {
  const values = profile.zoning[arrayName] ?? [];
  return (
    <div>
      <h3 style={{ fontSize: "0.95rem", margin: "1rem 0 0.25rem" }}>{heading}</h3>
      {values.length === 0 ? (
        <p className="section-note">{emptyText}</p>
      ) : (
        <div className="zoning-values">
          {values.map((value) => {
            const provenance = resolveDistrictProvenance(
              profile,
              arrayName,
              value,
              byId,
            );
            return (
              <div className="zoning-chip" key={value}>
                <div className="zoning-chip-code">{value}</div>
                <ProvenanceDisclosure
                  records={provenance.records}
                  reproducibility={profile.reproducibility}
                  label={`Source for ${value}`}
                  joinNote={JOIN_NOTES[provenance.joinedVia]}
                />
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

/**
 * Zoning districts, overlays, special districts, and mapped features, each
 * with provenance (map join when present, D5 fallback join otherwise —
 * never assuming full map coverage). Mapped-feature entries are OPEN
 * contract objects; every key is read through the runtime narrowing helper
 * in src/lib/contract.ts, never asserted.
 */
export function ZoningSection({
  profile,
  byId,
}: {
  profile: PropertyProfile;
  byId: Map<string, SourceFact>;
}) {
  const mappedFeatures = (profile.zoning.mapped_features ?? []).map(mappedFeatureView);
  return (
    <section className="card" aria-labelledby="zoning-title">
      <h2 className="section-title" id="zoning-title">
        Zoning
      </h2>
      <p className="section-note">
        District designations as recorded by the official source. Multiple
        districts on one lot (a split zoning lot) are all shown.
      </p>
      <ZoningValueList
        profile={profile}
        byId={byId}
        arrayName="districts"
        heading="Zoning districts"
        emptyText="No zoning district is present in the official record for this lot."
      />
      <ZoningValueList
        profile={profile}
        byId={byId}
        arrayName="commercial_overlays"
        heading="Commercial overlays"
        emptyText="No commercial overlay is present in the official record for this lot."
      />
      <ZoningValueList
        profile={profile}
        byId={byId}
        arrayName="special_districts"
        heading="Special districts"
        emptyText="No special district is present in the official record for this lot."
      />
      <h3 style={{ fontSize: "0.95rem", margin: "1rem 0 0.25rem" }}>
        Mapped features and flags
      </h3>
      {mappedFeatures.length === 0 ? (
        <p className="section-note">
          No mapped features are present in the official record for this lot.
        </p>
      ) : (
        <div className="table-scroll">
        <table className="facts-table">
          <thead>
            <tr>
              <th scope="col">Feature</th>
              <th scope="col">Value</th>
              <th scope="col">Coverage status</th>
              <th scope="col">Source</th>
            </tr>
          </thead>
          <tbody>
            {mappedFeatures.map((view, index) => {
              const record =
                view.provenanceRef !== null
                  ? resolveFactProvenance(view.provenanceRef, byId)
                  : null;
              const name = view.feature ?? `feature ${index + 1}`;
              return (
                <tr key={name}>
                  <th scope="row" style={{ textTransform: "none", fontSize: "0.92rem" }}>
                    {fieldLabel(name)}
                  </th>
                  <td>
                    <span className="fact-value">{formatValue(view.value)}</span>
                  </td>
                  <td>
                    {view.coverageStatus ? (
                      <CoverageBadge status={view.coverageStatus} />
                    ) : (
                      <span className="section-note">not labeled</span>
                    )}
                  </td>
                  <td>
                    <ProvenanceDisclosure
                      records={record ? [record] : []}
                      reproducibility={profile.reproducibility}
                      label={`Source for ${fieldLabel(name)}`}
                    />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        </div>
      )}
    </section>
  );
}
