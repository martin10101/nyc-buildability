import { mappedFeatureView, type PropertyProfile } from "@/lib/contract";

/** Share the same explicit source gaps between the workspace and printed brief. */
export function AdditionalZoningFlags({ profile }: { profile: PropertyProfile }) {
  const features = (profile.zoning.mapped_features ?? []).map(mappedFeatureView);
  const absent = [
    ["landmark", "Landmark"], ["histdist", "Historic district"],
    ["firm07_flag", "2007 FIRM flood flag"], ["pfirm15_flag", "2015 preliminary FIRM flood flag"],
  ].filter(([key]) => !features.some(feature => feature.feature === key && feature.hasValue));
  return <section className="card">
    <h2>Additional flags</h2>
    <dl className="architect-definition-list">
      {absent.map(([key, label]) => <div key={key}><dt>{label}</dt><dd>Unknown — not supplied</dd></div>)}
      <dt>Pending land-use actions</dt><dd>Unknown — source not connected</dd>
    </dl>
  </section>;
}
