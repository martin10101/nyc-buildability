import type { Scenario } from "@/lib/scenario-contract";
import { DraftHeadline } from "./PropertyOverview";
import { CapturedRecord } from "./EvidenceRecord";
import { UnusedFloorAreaSection } from "@/components/compare/UnusedFloorAreaSection";
import { ScenarioConstraints, IntegrityCheckBlock } from "@/components/compare/ScenarioConstraints";
import { CoverageMatrixSection } from "@/components/compare/CoverageMatrixSection";
import { ScenarioAssumptions } from "@/components/compare/ScenarioAssumptions";
import { NoScenarioBlock } from "@/components/compare/NoScenarioBlock";
export function ScenarioWorkspace({ document }: {
    document: Scenario;
}) {
    return <div data-testid="scenario-result">
    <section className="card">
      <DraftHeadline scenario={document}/>
      <p className="section-note">One preliminary scenario is supplied. Alternative optimization, practical usable range and design selection are not available.</p>
      <p>Objective: {document.cap_provenance?.output_name ?? "No supported objective returned"}
      </p>
      {document.cap_provenance?.note ? <p className="section-note">
        {document.cap_provenance.note}
      </p> : null}
    </section>
    {document.scenario_kind !== "preliminary" ? <NoScenarioBlock document={document}/> : null}
    <UnusedFloorAreaSection document={document}/>
    <ScenarioConstraints document={document}/>
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
