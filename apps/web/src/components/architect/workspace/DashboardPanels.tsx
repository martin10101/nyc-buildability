"use client";

import type { ReactNode } from "react";
import type { CoverageStatus, FactValue, PropertyProfile } from "@/lib/contract";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import type { Scenario } from "@/lib/scenario-contract";
import { fieldLabel, formatValue } from "@/lib/format";
import {
  BULK_ROWS,
  analysisRecordsDiffer,
  bulkRow,
  calculationStatus,
  evaluatedResidentialFar,
  residentialReference,
  scenarioBlocksPromotion,
  scenarioCap,
} from "@/lib/architect/development-limits";
import type { CondoSurfaceDecision } from "../CondoRecordsSection";
import type { DashboardTool } from "./types";

export interface DashboardPanelsProps {
  profile: PropertyProfile;
  scenario: Scenario | null;
  evaluation: RuleEvaluation | null;
  condo: CondoSurfaceDecision;
  label: string;
  /** The existing, BBL-bound map component, never a reference illustration. */
  map: ReactNode;
  onOpen: (tool: DashboardTool) => void;
  onInspect: (id: string) => void;
}

const COVERAGE: Record<CoverageStatus, string> = {
  verified: "Verified",
  conditional: "Conditional",
  professional_review_required: "Review required",
  data_conflict: "Data conflict",
  unsupported: "Unsupported",
  not_applicable: "Not applicable",
};
const LOT_FIELDS = ["lotarea", "lotfront", "lotdepth", "irrlotcode", "lottype", "easements"];
const BUILDING_FIELDS = ["bldgarea", "builtfar", "numfloors", "unitsres", "yearbuilt"];

function farValue(value: number) {
  return value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 20 });
}

function DashboardFact({ field, fact, profile, onInspect, onOpen }: {
  field: string;
  fact: FactValue | undefined;
  profile: PropertyProfile;
  onInspect: DashboardPanelsProps["onInspect"];
  onOpen: DashboardPanelsProps["onOpen"];
}) {
  const records = fact ? profile.provenance.filter(record => record.provenance_id === fact.provenance_ref) : [];
  const conflict = profile.conflicts.some(item => item.field === field && item.resolution === "unresolved")
    || records.some(record => record.conflict_status === "conflicting");
  const sourceAmbiguous = records.length > 1;
  const status = conflict ? "Conflicting records" : sourceAmbiguous ? "Conflicting source links"
    : fact?.value == null ? "Unknown" : !records.length ? "Source unavailable"
      : fact.coverage_status ? COVERAGE[fact.coverage_status] : "Not labeled";
  return <tr>
    <th scope="row">{fieldLabel(field)}</th>
    <td>
      <span className="bd-fact-value">{fact?.value != null ? <>{formatValue(fact.value)}{fact.units ? ` ${fact.units}` : ""}</> : "Unknown"}</span>
      <button type="button" className={`bd-source-status${conflict || sourceAmbiguous ? " bd-source-conflict" : ""}`}
        aria-label={`${fieldLabel(field)}: ${status}; inspect source`}
        onClick={() => records.length === 1 ? onInspect(records[0].provenance_id) : onOpen("facts")}>{status} <span aria-hidden="true">↗</span></button>
    </td>
  </tr>;
}

/** A display of existing records and guarded outputs. No FAR arithmetic, parcel
 * union, inferred dimensional limit or new legal decision lives in this view. */
export function DashboardPanels({ profile, scenario, evaluation, condo, label, map, onOpen, onInspect }: DashboardPanelsProps) {
  const bbl = profile.identity.bbl;
  // Keep the accepted condo guard monotonic on every computed summary, including
  // the bulk/status rows. A fetched scenario can never override this decision.
  const shownScenario = condo.withholdAllowances ? null : scenario;
  const shownEvaluation = condo.withholdAllowances ? null : evaluation;
  const matchedScenario = shownScenario?.evaluated_input.bbl === bbl ? shownScenario : null;
  const recordsDiffer = shownScenario !== null && analysisRecordsDiffer(shownEvaluation, shownScenario);
  const far = recordsDiffer || scenarioBlocksPromotion(shownScenario) ? null : evaluatedResidentialFar(shownEvaluation, bbl);
  const cap = scenarioCap(matchedScenario, shownEvaluation, bbl);
  const reference = residentialReference(profile);
  const sourceAction = () => reference.records.length === 1 && reference.status !== "Conflicting records"
    ? onInspect(reference.records[0].provenance_id) : onOpen("evidence");
  const status = condo.withholdAllowances ? "Site definition requires review · allowances withheld"
    : calculationStatus(shownEvaluation, matchedScenario, bbl);
  const conflicts = profile.conflicts.filter(item => item.resolution === "unresolved");
  const critical = profile.missing_inputs.filter(item => item.criticality === "critical");
  const records = condo.recordsView;
  const multiLot = records?.outcome === "multi_lot_set";
  const hasDistricts = !!(profile.zoning.districts?.length || profile.zoning.commercial_overlays?.length || profile.zoning.special_districts?.length);
  const stale = profile.reproducibility?.staleness?.stale;
  const reviewItems: { text: string; tool: DashboardTool }[] = [];
  if (condo.withholdAllowances) reviewItems.push({ text: "Site definition · allowances withheld", tool: "records" });
  if (condo.conflict) reviewItems.push({ text: "Condo records disagree", tool: "records" });
  if (conflicts.length) reviewItems.push({ text: `${conflicts.length} unresolved source conflict${conflicts.length === 1 ? "" : "s"}`, tool: "issues" });
  if (profile.missing_inputs.length) reviewItems.push({ text: `${profile.missing_inputs.length} missing input${profile.missing_inputs.length === 1 ? "" : "s"}${critical.length ? ` · ${critical.length} critical` : ""}`, tool: "issues" });
  if (stale) reviewItems.push({ text: "Stale property source", tool: "evidence" });
  if (profile.spatial_intersection?.professional_review_required || profile.lot_geometry?.review_required) reviewItems.push({ text: "Lot geometry requires professional review", tool: "zoning" });

  return <div className="buildability-dashboard" data-testid="buildability-dashboard">
    <div className="bd-column bd-property-column">
      <section className="bd-card bd-property" aria-label="Property and map">
        <div className="bd-map-slot">{map}</div>
        <div className="bd-card-body">
          <h1 tabIndex={-1} className="bd-property-title">{label}</h1>
          <p className="bd-meta">{profile.identity.address?.borough ? `${profile.identity.address.borough} · ` : ""}BBL {bbl}</p>
          <div className="bd-inline-actions">
            <button type="button" onClick={() => onOpen("map")}>Open map <span aria-hidden="true">↗</span></button>
            <button type="button" onClick={() => onOpen("facts")}>Property facts <span aria-hidden="true">↗</span></button>
            <button type="button" onClick={() => onOpen("evidence")}>Sources <span aria-hidden="true">↗</span></button>
          </div>
          {multiLot ? <button type="button" className="bd-parcel-summary" onClick={() => onOpen("study")}>
            <span>{records.baseLots.length} base parcel records</span><span>Review parcels <span aria-hidden="true">→</span></span>
          </button> : null}
        </div>
      </section>

      <section className="bd-card" aria-label="Recorded zoning districts">
        <div className="bd-card-heading"><h2>Zoning districts</h2><button type="button" className="bd-text-button" onClick={() => onOpen("zoning")}>Details <span aria-hidden="true">↗</span></button></div>
        <div className="bd-card-body bd-zoning-body">
          <div className="bd-tags">
            {profile.zoning.districts?.map((district, index) => <button type="button" key={`district-${index}`} className="bd-tag bd-district-tag" onClick={() => onOpen("zoning")} aria-label={`Recorded zoning district ${district}; details`}>{district}</button>)}
            {profile.zoning.commercial_overlays?.map((overlay, index) => <button type="button" key={`overlay-${index}`} className="bd-tag bd-overlay-tag" onClick={() => onOpen("zoning")} aria-label={`Recorded commercial overlay ${overlay}; details`}>{overlay}</button>)}
            {profile.zoning.special_districts?.map((district, index) => <button type="button" key={`special-${index}`} className="bd-tag bd-special-tag" onClick={() => onOpen("zoning")} aria-label={`Recorded special district ${district}; details`}>{district}</button>)}
            {!hasDistricts ? <span className="bd-muted">Not supplied</span> : null}
          </div>
          <p className="bd-meta">Source record · applicability in zoning details</p>
        </div>
      </section>

      <section className="bd-card" aria-label="Recorded lot details">
        <div className="bd-card-heading"><h2>Lot details</h2><span className="bd-record-label">Source record</span></div>
        <p className="bd-record-scope">{multiLot ? "Entered condo lot · identity reference, not additional land" : `Record for BBL ${bbl}`}</p>
        <table className="bd-table bd-facts-table"><caption className="bd-sr-only">Recorded lot facts and their source status</caption><tbody>
          {LOT_FIELDS.map(field => <DashboardFact key={field} field={field} fact={profile.lot_facts[field]} profile={profile} onInspect={onInspect} onOpen={onOpen}/>)}
        </tbody></table>
        <button type="button" className="bd-card-link" onClick={() => onOpen("facts")}>All property facts <span aria-hidden="true">→</span></button>
        <details className="bd-building-details"><summary>Existing building information</summary>
          <table className="bd-table bd-facts-table"><caption className="bd-sr-only">Recorded existing building facts</caption><tbody>
            {BUILDING_FIELDS.map(field => <DashboardFact key={field} field={field} fact={profile.existing_building_facts[field]} profile={profile} onInspect={onInspect} onOpen={onOpen}/>)}
          </tbody></table>
        </details>
      </section>
    </div>

    <div className="bd-column bd-analysis-column">
      <section className="bd-card bd-calculation" aria-label="Development limits summary">
        <div className="bd-card-heading bd-blue-heading"><h2>Development limits</h2><span className="bd-draft">DRAFT</span></div>
        <div className="bd-detail-shortcuts" role="group" aria-label="Development details">
          <button type="button" onClick={() => onOpen("zoning")}>FAR &amp; rules</button>
          <button type="button" onClick={() => onOpen("zoning")}>Height &amp; yards</button>
          <button type="button" onClick={() => onOpen("envelope")}>Envelope</button>
          <button type="button" onClick={() => onOpen("units")}>Units</button>
        </div>
        <button type="button" className="bd-assessment-note" onClick={() => onOpen("zoning")}><span aria-hidden="true">△</span> {status} <span aria-hidden="true">↗</span></button>
        <table className="bd-table bd-results-table"><caption className="bd-sr-only">Source residential FAR, evaluated residential FAR and draft floor-area cap</caption>
          <thead><tr><th scope="col">Measure</th><th scope="col">Value</th><th scope="col">Basis</th></tr></thead>
          <tbody>
            <tr><th scope="row">Residential FAR</th><td data-testid="dashboard-reference-far">{reference.value != null ? farValue(reference.value) : reference.status}</td><td><button type="button" className="bd-table-link" onClick={sourceAction}>City record <span aria-hidden="true">↗</span></button></td></tr>
            <tr><th scope="row">Evaluated residential FAR</th><td data-testid="dashboard-evaluated-far">{far ? farValue(far.value) : "Not calculated"}</td><td><button type="button" className="bd-table-link" onClick={() => onOpen("zoning")}>{far ? "Draft rule" : "Why?"} <span aria-hidden="true">↗</span></button></td></tr>
            <tr className={cap != null ? "bd-cap-row" : undefined}><th scope="row">Draft zoning floor-area cap</th><td data-testid="dashboard-cap">{cap != null ? `${formatValue(cap)} sq ft` : "Not calculated"}</td><td><button type="button" className="bd-table-link" onClick={() => onOpen("zoning")}>{cap != null && matchedScenario ? COVERAGE[matchedScenario.coverage_status] : "Why?"} <span aria-hidden="true">↗</span></button></td></tr>
          </tbody>
        </table>
        <p className="bd-result-scope">FAR only · Buildable envelope not assessed</p>
        {shownEvaluation?.wide_street ? <button type="button" className="bd-wide-street" onClick={() => onOpen("zoning")}>Wide-street determination <span>{shownEvaluation.wide_street.determination_state === "professional_review_required" ? "Professional review required" : "Draft details"} <span aria-hidden="true">↗</span></span></button> : null}
        <div className="bd-bulk-list" role="group" aria-label="Dimensional limits">
          {BULK_ROWS.map(([key, title]) => <button type="button" key={key} className="bd-bulk-row" onClick={() => onOpen("zoning")}><span>{title}</span><span>{condo.withholdAllowances ? "Withheld · site review" : bulkRow(matchedScenario, key, shownEvaluation).status} <span aria-hidden="true">↗</span></span></button>)}
        </div>
        <div className="bd-inline-actions bd-calculation-links"><button type="button" onClick={() => onOpen("evidence")}>Calculation evidence <span aria-hidden="true">↗</span></button><button type="button" onClick={() => onOpen("zoning")}>Full scope &amp; limitations <span aria-hidden="true">↗</span></button></div>
      </section>

      <section className={`bd-card bd-review${reviewItems.length ? " bd-review-needed" : ""}`} aria-label="Items to review">
        <div className="bd-card-heading"><h2>Items to review</h2><button type="button" className="bd-text-button" onClick={() => onOpen("issues")}>View all <span aria-hidden="true">↗</span></button></div>
        <ul className="bd-review-list">
          {reviewItems.map((item, index) => <li key={index}><button type="button" onClick={() => onOpen(item.tool)}><span className="bd-review-symbol" aria-hidden="true">!</span><span>{item.text}</span><span aria-hidden="true">↗</span></button></li>)}
          <li><button type="button" onClick={() => onOpen("zoning")}><span className="bd-review-symbol" aria-hidden="true">i</span><span>Draft assessment · not an approval</span><span aria-hidden="true">↗</span></button></li>
        </ul>
      </section>

      <div className="bd-resource-grid">
        <section className="bd-card" aria-label="Rules and calculations"><div className="bd-card-heading"><h2>Rules &amp; calculations</h2></div><div className="bd-resource-links">
          <button type="button" onClick={() => onOpen("zoning")}>Zoning sections <span aria-hidden="true">↗</span></button>
          <button type="button" onClick={() => onOpen("evidence")}>Sources &amp; provenance <span aria-hidden="true">↗</span></button>
          <button type="button" onClick={() => onOpen("scenarios")}>Draft scenario <span aria-hidden="true">↗</span></button>
        </div></section>
        <section className="bd-card" aria-label="Property resources"><div className="bd-card-heading"><h2>Property resources</h2></div><div className="bd-resource-links">
          <button type="button" onClick={() => onOpen("records")}>Condo &amp; land records <span aria-hidden="true">↗</span></button>
          <button type="button" onClick={() => onOpen("documents")}>Documents <span aria-hidden="true">↗</span></button>
          <button type="button" onClick={() => onOpen("facts")}>Existing building facts <span aria-hidden="true">↗</span></button>
        </div></section>
      </div>
    </div>

    <div className="bd-column bd-actions-column">
      <section className="bd-card" aria-label="Quick actions"><div className="bd-card-heading"><h2>Quick actions</h2></div><div className="bd-actions">
        <button type="button" className="bd-primary-action" onClick={() => onOpen("report")}><span aria-hidden="true">▤</span> Report preview</button>
        <button type="button" onClick={() => onOpen("map")}><span aria-hidden="true">⌖</span> Open map</button>
        <button type="button" onClick={() => onOpen("proposal")}><span aria-hidden="true">◇</span> Draw a proposal</button>
        <button type="button" onClick={() => onOpen("study")}><span aria-hidden="true">▦</span> Parcel study</button>
        <button type="button" onClick={() => onOpen("scenarios")}><span aria-hidden="true">▥</span> Scenarios</button>
      </div></section>

      <section className="bd-card" aria-label="Analysis status"><div className="bd-card-heading"><h2>Analysis status</h2></div><ul className="bd-status-list">
        <li><span className="bd-status-dot bd-status-record" aria-hidden="true"/><button type="button" onClick={() => onOpen("facts")}>Property record<span>Loaded</span></button></li>
        <li><span className={`bd-status-dot${stale ? " bd-status-review" : ""}`} aria-hidden="true"/><button type="button" onClick={() => onOpen("evidence")}>Source freshness<span>{stale ? "Stale" : profile.reproducibility?.staleness ? "Not flagged stale" : "Not supplied"}</span></button></li>
        <li><span className="bd-status-dot bd-status-review" aria-hidden="true"/><button type="button" onClick={() => onOpen("zoning")}>FAR calculation<span>{condo.withholdAllowances ? "Withheld" : far ? "Draft result" : "Not calculated"}</span></button></li>
        <li><span className="bd-status-dot" aria-hidden="true"/><button type="button" onClick={() => onOpen("envelope")}>Buildable envelope<span>Not assessed</span></button></li>
        <li><span className="bd-status-dot" aria-hidden="true"/><button type="button" onClick={() => onOpen("units")}>Unit estimate<span>Not calculated</span></button></li>
      </ul></section>

      <section className="bd-card" aria-label="Site study"><div className="bd-card-heading"><h2>Site study</h2></div><div className="bd-card-body bd-study-body">
        <p className="bd-study-count">{records?.baseLots.length ? <><strong>{records.baseLots.length}</strong> base parcel record{records.baseLots.length === 1 ? "" : "s"}</> : "Parcel records not supplied"}</p>
        <button type="button" className="bd-secondary-action" onClick={() => onOpen("study")}>Choose parcels &amp; study mode <span aria-hidden="true">↗</span></button>
        <button type="button" className="bd-text-button" onClick={() => onOpen("records")}>Site definition &amp; record status <span aria-hidden="true">↗</span></button>
      </div></section>
    </div>
  </div>;
}
