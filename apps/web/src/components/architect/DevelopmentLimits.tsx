import Link from "next/link";
import type { PropertyProfile } from "@/lib/contract";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import type { Scenario } from "@/lib/scenario-contract";
import { formatValue } from "@/lib/format";
import { propertyHref } from "@/lib/architect/navigation";
import { BULK_ROWS, analysisRecordsDiffer, bulkRow, calculationStatus, evaluatedResidentialFar, evaluationIsInspectable, residentialReference, scenarioBlocksPromotion, scenarioCap } from "@/lib/architect/development-limits";
import { AssessmentCoverage } from "./AssessmentCoverage";
import { CapturedRecord } from "./EvidenceRecord";

function farValue(value: number) {
  return value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 20 });
}

const STATUS_LABELS: Record<Scenario["coverage_status"], string> = {
  conditional: "Conditional",
  professional_review_required: "Professional review required",
  data_conflict: "Data conflict",
  unsupported: "Unsupported",
  not_applicable: "Not applicable",
};

export function IncompleteEvaluationNotice({ evaluation }: { evaluation: RuleEvaluation | null }) {
  if (!evaluation || evaluationIsInspectable(evaluation)) return null;
  return <section className="card" role="status">
    <h2>Rule details incomplete</h2>
    <p className="section-note">Numerical summaries are unavailable. The returned record is preserved below.</p>
    <CapturedRecord value={evaluation} label="Captured unusable rule-evaluation record"/>
  </section>;
}

export function DraftHeadline({ scenario, evaluation = null, bbl = "" }: { scenario: Scenario | null; evaluation?: RuleEvaluation | null; bbl?: string }) {
  const cap = scenarioCap(scenario, evaluation, bbl);
  return <div className="architect-draft-headline" data-testid="architect-cap">
    <h2>Draft zoning floor-area cap</h2>
    <p className="architect-metric">{cap != null ? <>{formatValue(cap)}<span> sq ft</span></> : "Not calculated"}</p>
    <p className="section-note">FAR only · Buildable envelope not assessed</p>
    {scenario ? <>
      <span className="architect-status">{STATUS_LABELS[scenario.coverage_status]}</span>
      <details className="provenance-details architect-result-scope">
        <summary>Result scope and source wording</summary>
        <p className="section-note">Recorded coverage: <code>{scenario.coverage_status}</code></p>
        <p>{scenario.cap_label}</p>
        {scenario.reasons.length ? <ul className="architect-issue-list">{scenario.reasons.map((reason, i) => <li key={i}>{reason}</li>)}</ul> : null}
      </details>
    </> : null}
  </div>;
}

/**
 * The wide-street conditional-FAR result (rule_evaluation 1.1.0 optional block).
 * Answer-first and calm: WHAT was calculated (the conditional FAR row), its
 * UNITS (a dimensionless ratio; floor area is FAR × lot area in sq ft), the
 * CONDITIONS under which it applies (within 100 ft of a wide street; DRAFT
 * pending qualified legal review), and a link to its SOURCES (the D-052
 * provenance summary rendered in CalculationEvidence). professional_review_
 * required is shown as the honest escalation it is — the higher wide-street FAR
 * is never presented as the computed result on uncertainty (D-051/D-073-R003).
 * Renders NOTHING when the document carries no block (a 1.0.0-shaped body), so
 * no value is invented.
 */
function WideStreetResult({ evaluation, evidenceHref }: { evaluation: RuleEvaluation | null; evidenceHref: string }) {
  const wide = evaluation?.wide_street;
  if (!wide) return null;
  const review = wide.determination_state === "professional_review_required";
  const within = wide.determination_state === "within_100ft_of_wide_street";
  return <section className="architect-wide-street" data-testid="development-wide-street" aria-label="Wide-street conditional FAR">
    <div className="architect-panel-heading"><h3>Wide-street conditional FAR</h3><span className="architect-status">Draft</span></div>
    {review
      ? <p className="architect-development-status" data-testid="wide-street-result">Professional review required — the higher wide-street floor-area ratio is withheld until a qualified reviewer confirms the determination.</p>
      : <>
          <p className="architect-development-value" data-testid="wide-street-result">{wide.governing_max_residential_far != null ? farValue(wide.governing_max_residential_far) : "Not calculated"}</p>
          <p className="section-note">Wide-street conditional FAR — a dimensionless ratio. Floor area = FAR × zoning-lot area (sq ft).</p>
          <p className="section-note">{within ? "Applies within 100 ft of a wide street." : "Outside 100 ft of a wide street; the conservative floor-area ratio governs."}</p>
        </>}
    {/* [ORCH-CORRECTED per M5-T037 HJ F2] The primary panel keeps only clean,
        human-phrased text. The server's raw draft_label / reason /
        fallback_direction_note strings carry internal identifiers and engine
        phrasing; they stay available verbatim behind the evidence disclosure
        (CalculationEvidence), never on the calm answer-first surface. */}
    <p className="section-note" data-testid="wide-street-draft">Draft — pending qualified legal review (not verified).</p>
    <Link href={evidenceHref}>Wide-street sources and provenance →</Link>
  </section>;
}

export function DevelopmentLimits({ profile, scenario, evaluation, onInspect }: {
  profile: PropertyProfile;
  scenario: Scenario | null;
  evaluation: RuleEvaluation | null;
  onInspect?: (id: string) => void;
}) {
  const bbl = profile.identity.bbl;
  const source = residentialReference(profile);
  const matchedScenario = scenario?.evaluated_input.bbl === bbl ? scenario : null;
  const recordsDiffer = scenario !== null && analysisRecordsDiffer(evaluation, scenario);
  const far = recordsDiffer || scenarioBlocksPromotion(scenario) ? null : evaluatedResidentialFar(evaluation, bbl);
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
    <DraftHeadline scenario={matchedScenario} evaluation={evaluation} bbl={bbl}/>
    <WideStreetResult evaluation={evaluation} evidenceHref={evidenceHref}/>
    <dl className="architect-bulk-rows">
      {BULK_ROWS.map(([key, label]) => {
        const row = bulkRow(matchedScenario, key, evaluation);
        return <div key={key}><dt>{label}</dt><dd>{row.status}<small><Link href={evidenceHref} aria-label={`Evidence for ${label}`}>Evidence</Link></small></dd></div>;
      })}
      <div><dt>Lot area</dt><dd>{lot?.value != null ? <>{formatValue(lot.value)} {lot.units}</> : "Unknown"}{lot && onInspect ? <button type="button" className="architect-text-button" aria-label="Source for Lot area" onClick={() => onInspect(lot.provenance_ref)}>Source</button> : null}</dd></div>
    </dl>
    <AssessmentCoverage scenario={matchedScenario}/>
  </section>;
}
