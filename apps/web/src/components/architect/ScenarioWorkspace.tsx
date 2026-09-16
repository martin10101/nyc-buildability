import type { Scenario } from "@/lib/scenario-contract";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import { calculationStatus, scenarioCap } from "@/lib/architect/development-limits";
import { DraftHeadline } from "./PropertyOverview";
import { CapturedRecord } from "./EvidenceRecord";
import { UnusedFloorAreaSection } from "@/components/compare/UnusedFloorAreaSection";
import { ScenarioConstraints, IntegrityCheckBlock } from "@/components/compare/ScenarioConstraints";
import { CoverageMatrixSection } from "@/components/compare/CoverageMatrixSection";
import { ScenarioAssumptions } from "@/components/compare/ScenarioAssumptions";
import { NoScenarioBlock } from "@/components/compare/NoScenarioBlock";
export function ScenarioWorkspace({ document, evaluation = null, bbl }: {
    document: Scenario;
    evaluation?: RuleEvaluation | null;
    bbl: string;
}) {
    const supportedCap = scenarioCap(document, evaluation, bbl) !== null;
    return <div data-testid="scenario-result">
    <section className="card">
      <DraftHeadline scenario={document} evaluation={evaluation} bbl={bbl}/>
      {!supportedCap ? <p className="section-note">{calculationStatus(evaluation, document, bbl)}</p> : null}
      <p className="section-note">One preliminary scenario is supplied. Alternative optimization, practical usable range and design selection are not available.</p>
      <p>Objective: {document.cap_provenance?.output_name ?? "No supported objective returned"}
      </p>
      {document.cap_provenance?.note ? <p className="section-note">
        {document.cap_provenance.note}
      </p> : null}
    </section>
    {document.scenario_kind !== "preliminary" ? <NoScenarioBlock document={document}/> : null}
    {supportedCap ? <>
      <UnusedFloorAreaSection document={document}/>
      <ScenarioConstraints document={document}/>
    </> : <details className="card architect-disclosure">
      <summary>Returned scenario figures · association not confirmed</summary>
      <p className="section-note">These are the supplied records. They are not promoted as property limits.</p>
      <UnusedFloorAreaSection document={document}/>
      <ScenarioConstraints document={document}/>
    </details>}
    <details className="card architect-disclosure">
      <summary>Assumptions, integrity and coverage</summary>
      <ScenarioAssumptions document={document}/>
      <IntegrityCheckBlock document={document}/>
      <CoverageMatrixSection document={document}/>
    </details>
    <section className="card">
      <h2>Source and evaluation record</h2>
      <CapturedRecord value={document.cap_provenance} label="Rule, citation snapshots and source metadata"/>
      <CapturedRecord value={document} label="Complete scenario record"/>
    </section>
  </div>;
}
