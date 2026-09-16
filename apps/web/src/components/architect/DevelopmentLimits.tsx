import Link from "next/link";
import type { PropertyProfile } from "@/lib/contract";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import type { Scenario } from "@/lib/scenario-contract";
import { formatValue } from "@/lib/format";
import { propertyHref } from "@/lib/architect/navigation";
import { BULK_ROWS, analysisRecordsDiffer, bulkRow, calculationStatus, evaluatedResidentialFar, presentableScenario, residentialReference, scenarioCap } from "@/lib/architect/development-limits";
import { CoverageBadge } from "@/components/property/CoverageBadge";
import { AssessmentCoverage } from "./AssessmentCoverage";

function farValue(value: number) {
  return value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 20 });
}

export function DraftHeadline({ scenario }: { scenario: Scenario | null }) {
  const cap = scenarioCap(scenario);
  return <div className="architect-draft-headline" data-testid="architect-cap">
    <h2>Draft zoning floor-area cap</h2>
    <p className="architect-metric">{cap != null ? <>{formatValue(cap)}<span> sq ft</span></> : "Not calculated"}</p>
    <p className="section-note">FAR only · Buildable envelope not assessed</p>
    {scenario ? <>
      <CoverageBadge status={scenario.coverage_status}/>
      <details className="provenance-details architect-result-scope">
        <summary>Result scope and source wording</summary>
        <p>{scenario.cap_label}</p>
        {scenario.reasons.length ? <ul className="architect-issue-list">{scenario.reasons.map((reason, i) => <li key={i}>{reason}</li>)}</ul> : null}
      </details>
    </> : null}
  </div>;
}

export function DevelopmentLimits({ profile, scenario, evaluation, onInspect }: {
  profile: PropertyProfile;
  scenario: Scenario | null;
  evaluation: RuleEvaluation | null;
  onInspect?: (id: string) => void;
}) {
  const bbl = profile.identity.bbl;
  const source = residentialReference(profile);
  const matchedScenario = presentableScenario(scenario, bbl);
  const recordsDiffer = analysisRecordsDiffer(evaluation, matchedScenario);
  const summaryScenario = recordsDiffer ? null : matchedScenario;
  const far = recordsDiffer ? null : evaluatedResidentialFar(evaluation, bbl);
  const lot = profile.lot_facts.lotarea;
  const evidenceHref = propertyHref(bbl, "evidence");
  return <section className="card architect-development" aria-label="Development limits">
    <div className="architect-panel-heading"><h2>Development limits</h2><span className="architect-status">Draft</span></div>
    <p className="architect-development-status">{calculationStatus(evaluation, matchedScenario, bbl)}</p>
    <div className="architect-far-grid">
      <div className="architect-far-reference">
        <h3>Residential FAR · city record</h3>
        <p className="architect-development-value" data-testid="development-reference-far">{source.value != null ? farValue(source.value) : source.status}</p>
        <p className="section-note">PLUTO reference{source.records.length === 1 && source.records[0].dataset_version ? ` · ${source.records[0].dataset_version}` : ""}</p>
        {source.records.length === 1 && source.status !== "Conflicting records" && onInspect ? <button type="button" className="architect-text-button" onClick={() => onInspect(source.records[0].provenance_id)}>Source for residential FAR</button> : <Link href={evidenceHref}>View source records →</Link>}
      </div>
      <div>
        <h3>Evaluated residential FAR</h3>
        <p className="architect-development-value" data-testid="development-evaluated-far">{far ? farValue(far.value) : "Not calculated"}</p>
        <p className="section-note">{far ? "Draft rule result" : "No supported rule result supplied"}</p>
        <Link href={evidenceHref}>Rules and calculation →</Link>
      </div>
    </div>
    <DraftHeadline scenario={summaryScenario}/>
    <dl className="architect-bulk-rows">
      {BULK_ROWS.map(([key, label]) => {
        const row = bulkRow(summaryScenario, key, evaluation?.evaluated_input.bbl === bbl ? evaluation : null);
        return <div key={key}><dt>{label}</dt><dd>{row.value != null ? <>{formatValue(row.value)} {row.unit}<small>{row.status} · <Link href={evidenceHref} aria-label={`Evidence for ${label}`}>Evidence</Link></small></> : row.status}</dd></div>;
      })}
      <div><dt>Lot area</dt><dd>{lot?.value != null ? <>{formatValue(lot.value)} {lot.units}</> : "Unknown"}{lot && onInspect ? <button type="button" className="architect-text-button" aria-label="Source for Lot area" onClick={() => onInspect(lot.provenance_ref)}>Source</button> : null}</dd></div>
    </dl>
    <AssessmentCoverage scenario={matchedScenario}/>
  </section>;
}
