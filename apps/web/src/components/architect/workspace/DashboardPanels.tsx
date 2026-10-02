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
import { NOT_CONFIRMED, ZONING_LOT_ROW_REASONS, ZONING_LOT_ROWS, type VerifiedZoningLot } from "@/lib/architect/tax-lot-scope";
import type { CondoSurfaceDecision } from "../CondoRecordsSection";
import { TaxLotOnlyEstimate, TaxLotOnlyNotice } from "../TaxLotOnlyNotice";
import { DashboardStatusStrip } from "./DashboardStatusStrip";
import {
  NO_RESULTS_REASON,
  SITE_REVIEW_REASON,
  bulkReason,
  calculationReason,
  dashboardNotices,
  dashboardStatus,
  notAvailable,
  referenceReason,
} from "./dashboard-status";
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
  /** Server-read INTERNAL_PROPOSAL_EDITOR_ENABLED (D-01, plan §7). Absent -> off:
   * the "Envelope" and "Draw a proposal" entries are hidden. */
  proposalEditorEnabled?: boolean;
  /** Server-read INTERNAL_LOT_SITE_SETUP_ENABLED (D-04, plan M1-13). Absent -> off:
   * the "Lot & site setup" entry is hidden. */
  lotSiteSetupEnabled?: boolean;
  /** Why the entry passes no rule results, when it knows (still loading, or returned for another
   * property); from `analysisReason`. Absent or null: the guard's own status gives the reason. */
  resultsReason?: string | null;
  /** A VERIFIED zoning-lot fact for this property (owner directive 2026-10-01). None is wired
   * yet: absent, the warning reads the generic tax-lot-only text. */
  zoningLot?: VerifiedZoningLot | null;
}

/** Plan §5a item 3: beside a value, only an exception that changes how to read it. The usual
 * "Conditional" coverage of every unreviewed city record is not repeated on each row. */
const FACT_EXCEPTIONS: Partial<Record<CoverageStatus, string>> = {
  professional_review_required: "Needs review",
  unsupported: "Not supported",
  not_applicable: "Not applicable",
};
/** Dashboard wording where the shared source label would mislead (plan §3 step 4: city-recorded
 * building area is not zoning floor area). The lot-type code is left to the property-facts tool:
 * its city code list is not extracted with a citation yet (docs/research/pluto-mappluto-2026-07-16.md,
 * OQ-5 residual), so the dashboard would show a bare number (plan §5a item 5). */
const DASHBOARD_LABELS: Record<string, string> = { bldgarea: "City-recorded building area (not zoning floor area)" };
const LOT_FIELDS = ["lotarea", "lotfront", "lotdepth", "irrlotcode", "easements"];
const BUILDING_FIELDS = ["bldgarea", "builtfar", "numfloors", "unitsres", "yearbuilt"];

function farValue(value: number) {
  return value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 20 });
}

function unitSuffix(units: string | undefined) {
  return units ? ` ${units === "square feet" ? "sq ft" : units === "feet" ? "ft" : units}` : "";
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
    || records.some(record => record.conflict_status === "conflicting") || records.length > 1
    || fact?.coverage_status === "data_conflict";
  const label = DASHBOARD_LABELS[field] ?? fieldLabel(field);
  let text = "Unknown";
  let exception: string | null = null;
  if (conflict) text = notAvailable("the records disagree");
  else if (fact && fact.value != null) {
    text = `${formatValue(fact.value)}${unitSuffix(fact.units)}`;
    exception = !records.length ? "No source record" : fact.coverage_status ? FACT_EXCEPTIONS[fact.coverage_status] ?? null : null;
  }
  return <tr>
    <th scope="row">{label}</th>
    <td>
      <button type="button" className="bd-fact-value" aria-label={`${label}: ${text}${exception ? ` (${exception})` : ""}. Show source`}
        onClick={() => records.length === 1 ? onInspect(records[0].provenance_id) : onOpen("facts")}>{text}</button>
      {exception ? <span className="bd-exception">{exception}</span> : null}
    </td>
  </tr>;
}

/** A display of existing records and guarded outputs. No FAR arithmetic, parcel
 * union, inferred dimensional limit or new legal decision lives in this view.
 * Plan §5a: one status strip on top of the results, standing notices behind it, and
 * "Not available — <reason>" in place of any number the guards withhold.
 * Owner directive 2026-10-01 (overrides §5a items 2 and 3 for this one fact): the tax-lot-only
 * warning shows on the results without a tap, the cap value carries a plain-text
 * "Tax-lot-only estimate" line (not a chip), and the combined-zoning-lot rows read "Not confirmed". */
export function DashboardPanels({ profile, scenario, evaluation, condo, label, map, onOpen, onInspect, proposalEditorEnabled = false, lotSiteSetupEnabled = false, resultsReason = null, zoningLot = null }: DashboardPanelsProps) {
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
  // The withheld reason is the true one: the site review first, then what the entry knows
  // (loading, another property), then the guard's own status; a scenario for another record set
  // names that mismatch rather than a generic "not calculated".
  const reason = condo.withholdAllowances ? SITE_REVIEW_REASON : resultsReason ?? (!shownEvaluation ? NO_RESULTS_REASON
    : calculationReason(calculationStatus(shownEvaluation, shownScenario, bbl)));
  const records = condo.recordsView;
  const multiLot = records?.outcome === "multi_lot_set";
  const hasDistricts = !!(profile.zoning.districts?.length || profile.zoning.commercial_overlays?.length || profile.zoning.special_districts?.length);
  const status = dashboardStatus({ withheld: condo.withholdAllowances, calculated: far !== null || cap !== null, multiLot, baseLots: records?.baseLots.length ?? 0 });
  const notices = dashboardNotices(profile, condo, shownEvaluation);
  const referenceText = reference.value != null ? farValue(reference.value) : notAvailable(referenceReason(reference.status));

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
            {!hasDistricts ? <span>None in city records</span> : null}
          </div>
        </div>
      </section>

      <section className="bd-card" aria-label="Recorded lot details">
        <div className="bd-card-heading"><h2>Lot details</h2></div>
        {multiLot ? <p className="bd-record-scope">Entered condo lot · identity reference, not additional land</p> : null}
        <table className="bd-table bd-facts-table"><caption className="bd-sr-only">Recorded lot facts; select a value to see its source</caption><tbody>
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
      <DashboardStatusStrip status={status} notices={notices} onOpen={onOpen}/>

      <section className="bd-card bd-calculation" aria-label="Development limits summary">
        <div className="bd-card-heading bd-blue-heading"><h2>Development limits</h2></div>
        <div className="bd-detail-shortcuts" role="group" aria-label="Development details">
          <button type="button" onClick={() => onOpen("zoning")}>FAR &amp; rules</button>
          <button type="button" onClick={() => onOpen("zoning")}>Height &amp; yards</button>
          {proposalEditorEnabled ? <button type="button" onClick={() => onOpen("envelope")}>Envelope</button> : null}
          <button type="button" onClick={() => onOpen("units")}>Units</button>
        </div>
        <TaxLotOnlyNotice bbl={bbl} zoningLot={zoningLot}/>
        <div className="bd-headline">
          <p className="bd-headline-label">Maximum residential floor area</p>
          <p className={`bd-headline-value${cap != null ? "" : " bd-not-available"}`} data-testid="dashboard-cap">{cap != null ? `${formatValue(cap)} sq ft` : notAvailable(reason)}</p>
          {cap != null ? <TaxLotOnlyEstimate testId="dashboard-cap-scope"/> : null}
        </div>
        <table className="bd-table bd-results-table"><caption className="bd-sr-only">Residential FAR, dimensional limits and combined zoning lot results</caption>
          <tbody>
            <tr><th scope="row">Maximum residential FAR</th><td data-testid="dashboard-evaluated-far">{far ? farValue(far.value) : notAvailable(reason)}</td></tr>
            <tr><th scope="row">City-listed residential FAR</th><td data-testid="dashboard-reference-far">
              <button type="button" className="bd-fact-value" aria-label={`City-listed residential FAR: ${referenceText}. Show source`} onClick={sourceAction}>{referenceText}</button>
            </td></tr>
            {BULK_ROWS.map(([key, title]) => <tr key={key}><th scope="row">{title}</th>
              <td>{notAvailable(condo.withholdAllowances ? SITE_REVIEW_REASON : bulkReason(bulkRow(matchedScenario, key, shownEvaluation).status))}</td></tr>)}
            {ZONING_LOT_ROWS.map(([key, title]) => <tr key={key}><th scope="row">{title}</th><td data-testid={`dashboard-zoning-lot-${key}`}>{NOT_CONFIRMED}
              {ZONING_LOT_ROW_REASONS[key] ? <>{" "}<span className="bd-row-reason" data-testid={`dashboard-zoning-lot-${key}-reason`}>{ZONING_LOT_ROW_REASONS[key]}</span></> : null}</td></tr>)}
          </tbody>
        </table>
        <div className="bd-inline-actions bd-calculation-links"><button type="button" onClick={() => onOpen("evidence")}>How this was calculated <span aria-hidden="true">↗</span></button></div>
      </section>

      <div className="bd-resource-grid">
        <section className="bd-card" aria-label="Rules and calculations"><div className="bd-card-heading"><h2>Rules &amp; calculations</h2></div><div className="bd-resource-links">
          <button type="button" onClick={() => onOpen("zoning")}>Zoning sections <span aria-hidden="true">↗</span></button>
          <button type="button" onClick={() => onOpen("evidence")}>Data sources <span aria-hidden="true">↗</span></button>
          <button type="button" onClick={() => onOpen("scenarios")}>Scenario <span aria-hidden="true">↗</span></button>
        </div></section>
        <section className="bd-card" aria-label="Property resources"><div className="bd-card-heading"><h2>Property resources</h2></div><div className="bd-resource-links">
          <button type="button" onClick={() => onOpen("records")}>Condo &amp; land records <span aria-hidden="true">↗</span></button>
          <button type="button" onClick={() => onOpen("documents")}>Documents <span aria-hidden="true">↗</span></button>
          <button type="button" onClick={() => onOpen("issues")}>Items to review <span aria-hidden="true">↗</span></button>
        </div></section>
      </div>
    </div>

    <div className="bd-column bd-actions-column">
      <section className="bd-card" aria-label="Quick actions"><div className="bd-card-heading"><h2>Quick actions</h2></div><div className="bd-actions">
        <button type="button" className="bd-primary-action" onClick={() => onOpen("report")}><span aria-hidden="true">▤</span> Report preview</button>
        <button type="button" onClick={() => onOpen("map")}><span aria-hidden="true">⌖</span> Open map</button>
        {proposalEditorEnabled ? <button type="button" onClick={() => onOpen("proposal")}><span aria-hidden="true">◇</span> Draw a proposal</button> : null}
        <button type="button" onClick={() => onOpen("study")}><span aria-hidden="true">▦</span> Parcel study</button>
        <button type="button" onClick={() => onOpen("scenarios")}><span aria-hidden="true">▥</span> Scenarios</button>
      </div></section>

      <section className="bd-card" aria-label="Site study"><div className="bd-card-heading"><h2>Site study</h2></div><div className="bd-card-body bd-study-body">
        <p className="bd-study-count">{records?.baseLots.length ? <><strong>{records.baseLots.length}</strong> base parcel record{records.baseLots.length === 1 ? "" : "s"}</> : "Parcel records not supplied"}</p>
        {lotSiteSetupEnabled ? <button type="button" className="bd-secondary-action" onClick={() => onOpen("lotsite")}>Lot &amp; site setup <span aria-hidden="true">↗</span></button> : null}
        <button type="button" className="bd-secondary-action" onClick={() => onOpen("study")}>Choose parcels &amp; study mode <span aria-hidden="true">↗</span></button>
        <button type="button" className="bd-text-button" onClick={() => onOpen("records")}>Site definition &amp; record status <span aria-hidden="true">↗</span></button>
      </div></section>
    </div>
  </div>;
}
