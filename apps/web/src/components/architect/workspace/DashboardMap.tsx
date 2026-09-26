"use client";
import { zolaLotUrl } from "@/lib/provenance-link";
import { LotOutlineMap } from "@/components/address/LotOutlineMap";
import { ParcelStudyMap } from "../ParcelStudyMap";
import type { CondoSurfaceDecision } from "../CondoRecordsSection";
import { deriveParcelStudyScope } from "@/lib/architect/parcel-study";
import { useParcelStudyRecords } from "@/lib/architect/use-parcel-study-records";

function BaseParcelMap({ bbls, compact }: { bbls: readonly string[]; compact: boolean }) {
  const source = useParcelStudyRecords(bbls);
  return <><ParcelStudyMap compact={compact} arrangement="compare" outlines={source.records.map(record => ({ bbl: record.bbl, outcome: record.outlineOutcome, loading: record.outlineOutcome === null }))}/>
    <button type="button" className="architect-text-button" onClick={source.retry} disabled={source.loading}>Refresh parcel outlines</button></>;
}
/** Only city geometry is rendered. The billing record is never added as land. */
export function DashboardMap({ bbl, condo, compact = false }: { bbl: string; condo: CondoSurfaceDecision; compact?: boolean }) {
  const records = condo.recordsView;
  if (records?.outcome === "multi_lot_set") {
    const scope = deriveParcelStudyScope({ enteredBbl: records.enteredBbl, billingBbl: records.billingBbl, baseLots: records.baseLots });
    if (!scope.ok || condo.conflict || records.enteredBbl !== bbl || records.studyIdentityIntegrity !== true) {
      return <p role="status">Parcel identities need review before these outlines can be displayed.</p>;
    }
    return <BaseParcelMap key={scope.scope.key} bbls={scope.scope.baseBbls} compact={compact}/>;
  }
  const zola = zolaLotUrl(bbl);
  return <>{zola ? <a className="dashboard-map-zola" href={zola} target="_blank" rel="noopener noreferrer">View this lot on ZoLa ↗</a> : null}<LotOutlineMap key={bbl} bbl={bbl} context/></>;
}
