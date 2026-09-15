import type { PropertyProfile } from "@/lib/contract";
import { fieldLabel, formatValue } from "@/lib/format";
import { sourceFactLinks } from "@/lib/provenance-link";
export function ReportSources({ profile }: {
    profile: PropertyProfile;
}) {
    return <section className="card architect-report-sources">
    <h2>Source and review appendix</h2>
    <p className="section-note">Profile revision {profile.profile_version.profile_revision} · Generated {profile.profile_version.generated_at}. Current records may differ from the captured evidence shown here.</p>
    <div className="table-scroll">
      <table className="facts-table">
        <thead>
          <tr>
            <th>Fact / captured values</th>
            <th>Official links / captured source</th>
            <th>Dates / review</th>
          </tr>
        </thead>
        <tbody>
          {profile.provenance.map(record => {
            const links = sourceFactLinks(record, profile.reproducibility, profile.identity);
            return <tr key={record.provenance_id}>
            <th scope="row">
              {fieldLabel(record.original_field_name)}
              <br /><code className="section-note">{record.original_field_name}</code>
              <p>Original: {formatValue(record.original_value)}
                <br />Normalized: {formatValue(record.normalized_value)}
                {record.units ? ` ${record.units}` : ""}
              </p>
            </th>
            <td>
              {links.currentRecordUrl ? <><a href={links.currentRecordUrl} target="_blank" rel="noopener noreferrer">Current PLUTO record (JSON)</a><br /></> : null}
              {links.datasetUrl ? <><a className="section-note" href={links.datasetUrl} target="_blank" rel="noopener noreferrer">About this dataset</a><br /></> : null}
              {record.source_id}
              <br />
              {record.dataset_version}
              <p className="section-note">
                {record.provenance_id}
              </p>
            </td>
            <td>Captured {record.retrieved_at}
              <br />Effective {record.effective_date ?? "not published"}
              <br />Review: {record.user_confirmed_or_overridden}
              <br />Conflict: {record.conflict_status}
            </td>
          </tr>;
        })}
        </tbody>
      </table>
    </div>
    <h3>Recorded confirmations and overrides</h3>
    {profile.user_confirmations.length ? <ul>
      {profile.user_confirmations.map((item, index) => <li key={index}>
        {fieldLabel(item.field)} · {item.action}
        {item.override_value !== undefined ? `: ${formatValue(item.override_value)}` : ""} · {item.confirmed_by ?? "Reviewer not supplied"} · {item.confirmed_at ?? "Date not supplied"}
      </li>)}
    </ul> : <p>No recorded confirmations or overrides were supplied.</p>}
  </section>;
}
