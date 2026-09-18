import { ZoningValueList } from "@/components/property/ZoningSection";
import { ProvenanceDisclosure } from "@/components/property/ProvenanceDisclosure";
import { CoverageBadge } from "@/components/property/CoverageBadge";
import { mappedFeatureView, type PropertyProfile } from "@/lib/contract";
import { provenanceById, resolveFactProvenance } from "@/lib/provenance";
import { formatValue } from "@/lib/format";
import { zolaLotUrl } from "@/lib/provenance-link";
import { ABSENT_BBL_MAP_LINK_NOTE, ZOLA_LOT_LINK_LABEL } from "./AddressAutocomplete";

/**
 * DB-016 zoning-context panel (task M5-T036). Surfaces the official
 * designations the client-side PropertyProfile ALREADY carries — zoning
 * districts (split lots included), commercial overlays, special districts and
 * landmark/historic status — alongside the computed development answers, so
 * the architect surface no longer shows only FAR while ZoLa displays the
 * richer per-lot context our connectors already fetch.
 *
 * LABEL DISPLAY ONLY (owner ruling 2026-09-17): nothing here is computed,
 * inferred, or defaulted. Every value is read straight from the profile with
 * the SAME per-value provenance discipline and honest absent/Unknown states
 * as the reference components (components/property/ZoningSection via the
 * shared ZoningValueList; architect/AdditionalZoningFlags for the flag rows).
 * The computed-answer engine (Development limits) remains the differentiator.
 *
 * The single official link is the human-readable ZoLa lot page built ONLY
 * through the validated zolaLotUrl helper (DB-005): it returns null for a
 * non-canonical BBL, and we then render NO link — honest absence, never a
 * raw template-string URL.
 */

/** Landmark/historic designations surfaced here (source column -> label). */
const DESIGNATION_FLAGS: ReadonlyArray<readonly [string, string]> = [
  ["landmark", "Landmark"],
  ["histdist", "Historic district"],
];

export function ZoningContextPanel({ profile }: { profile: PropertyProfile }) {
  const byId = provenanceById(profile);
  const zolaUrl = zolaLotUrl(profile.identity.bbl);
  const features = (profile.zoning.mapped_features ?? []).map(mappedFeatureView);

  return (
    <section
      className="card"
      aria-labelledby="zoning-context-title"
      data-testid="zoning-context-panel"
    >
      <div className="architect-panel-heading">
        <h2 className="section-title" id="zoning-context-title">
          Zoning context
        </h2>
        {zolaUrl ? (
          <a
            href={zolaUrl}
            target="_blank"
            rel="noopener noreferrer"
            data-testid="zoning-context-zola-link"
          >
            {ZOLA_LOT_LINK_LABEL} <span aria-hidden="true">↗</span>
          </a>
        ) : (
          <span className="section-note" data-testid="zoning-context-zola-absent">
            {ABSENT_BBL_MAP_LINK_NOTE}
          </span>
        )}
      </div>
      <p className="section-note">
        Official designations as recorded by the source, shown next to the
        computed answers. Multiple districts on one lot (a split zoning lot) are
        all shown. Nothing here is computed — the calculated result stays in
        Development limits.
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
        Landmark and historic status
      </h3>
      <dl
        className="architect-definition-list"
        data-testid="zoning-context-designations"
      >
        {DESIGNATION_FLAGS.map(([key, label]) => {
          const view = features.find(
            (feature) => feature.feature === key && feature.hasValue,
          );
          const record =
            view && view.provenanceRef !== null
              ? resolveFactProvenance(view.provenanceRef, byId)
              : null;
          return (
            <div key={key}>
              <dt>{label}</dt>
              <dd>
                <span className="fact-value">
                  {view ? formatValue(view.value) : "Unknown — not supplied"}
                </span>
                {/* DB-019c: surface the mapped feature's own coverage_status on
                    the row, display-only (nothing computed) and never by colour
                    alone — the same CoverageBadge the reference ZoningSection
                    rows use. The full coverage table stays on the zoning tab. */}
                {view && view.coverageStatus ? (
                  <CoverageBadge status={view.coverageStatus} />
                ) : null}
                {view ? (
                  <ProvenanceDisclosure
                    records={record ? [record] : []}
                    reproducibility={profile.reproducibility}
                    label={`Source for ${label}`}
                  />
                ) : null}
              </dd>
            </div>
          );
        })}
      </dl>
    </section>
  );
}
