import type { Scenario } from "@/lib/scenario-contract";

const LABELS: Record<string, string> = {
  residential_far_cap: "Residential FAR cap",
  height_limit: "Height",
  setbacks_yards: "Setbacks and yards",
  lot_coverage_open_space: "Lot coverage and open space",
  street_wall_base_height: "Street wall and base height",
  parking_loading: "Parking and loading",
  use_group_overlay: "Use and overlays",
  special_districts_overlays: "Special districts and overlays",
  density_bonuses: "Density bonuses",
  higher_density_bulk_tower: "Higher-density bulk and towers",
  gross_to_net_efficiency_yield: "Gross-to-net efficiency",
};
export function AssessmentCoverage({ scenario }: { scenario: Scenario | null }) {
  if (!scenario) return <p className="section-note">Assessment coverage not supplied.</p>;
  const blockers = scenario.coverage_matrix.filter(row => row.blocks_buildable_envelope);
  return <div className="architect-assessment">
    {blockers.length ? <p className="architect-coverage-status"><strong>Envelope assessment incomplete.</strong> {blockers.length} checks remain open.</p> : null}
    <details className="provenance-details">
      <summary>Assessment coverage · {scenario.coverage_matrix.length} checks</summary>
      <div className="table-scroll"><table className="facts-table">
        <thead><tr><th scope="col">Check</th><th scope="col">Status</th></tr></thead>
        <tbody>{scenario.coverage_matrix.map((row, i) => <tr key={i}>
          <th scope="row">{LABELS[row.constraint_family] ?? row.constraint_family.replaceAll("_", " ")}<code className="architect-source-key">{row.constraint_family}</code></th>
          <td>{row.rule_status_today}{row.blocks_buildable_envelope ? " · Blocks envelope" : ""}</td>
        </tr>)}</tbody>
      </table></div>
    </details>
  </div>;
}
