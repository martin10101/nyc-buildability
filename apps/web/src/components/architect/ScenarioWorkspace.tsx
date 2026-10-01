import type { Scenario } from "@/lib/scenario-contract";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import { calculationStatus, scenarioCap } from "@/lib/architect/development-limits";
import { DraftHeadline } from "./PropertyOverview";
import { CapturedRecord } from "./EvidenceRecord";
import { TaxLotOnlyNotice } from "./TaxLotOnlyNotice";
import type { VerifiedZoningLot } from "@/lib/architect/tax-lot-scope";
import { UnusedFloorAreaSection } from "@/components/compare/UnusedFloorAreaSection";
import { UnusedFloorAreaSetAside } from "@/components/compare/UnusedFloorAreaNotAvailable";
import { ScenarioConstraints, IntegrityCheckBlock } from "@/components/compare/ScenarioConstraints";
import { CoverageMatrixSection } from "@/components/compare/CoverageMatrixSection";
import { ScenarioAssumptions } from "@/components/compare/ScenarioAssumptions";
import { NoScenarioBlock } from "@/components/compare/NoScenarioBlock";
/** `unusedFloorAreaSectionEnabled` is the server-read INTERNAL_UNUSED_FLOOR_AREA_SECTION_ENABLED
 * (D-06, plan §3 step 4); absent -> off: the set-aside section is replaced by one
 * "Not available — needs existing zoning floor area" line. */
export function ScenarioWorkspace({ document, evaluation = null, bbl, unusedFloorAreaSectionEnabled = false, zoningLot = null }: {
    document: Scenario;
    evaluation?: RuleEvaluation | null;
    bbl: string;
    unusedFloorAreaSectionEnabled?: boolean;
    /** A VERIFIED zoning-lot fact for this property (owner directive 2026-10-01); none is wired yet. */
    zoningLot?: VerifiedZoningLot | null;
}) {
    const supportedCap = scenarioCap(document, evaluation, bbl) !== null;
    const unusedFloorArea = unusedFloorAreaSectionEnabled ? <UnusedFloorAreaSection document={document}/> : <UnusedFloorAreaSetAside/>;
    return <div data-testid="scenario-result">
    <section className="card">
      <DraftHeadline scenario={document} evaluation={evaluation} bbl={bbl}/>
      {/* Owner directive 2026-10-01: the cap above is for the entered tax lot only. */}
      <TaxLotOnlyNotice bbl={bbl} zoningLot={zoningLot}/>
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
      {unusedFloorArea}
      <ScenarioConstraints document={document}/>
    </> : <details className="card architect-disclosure">
      <summary>Returned scenario figures · association not confirmed</summary>
      <p className="section-note">These are the supplied records. They are not promoted as property limits.</p>
      {unusedFloorArea}
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
