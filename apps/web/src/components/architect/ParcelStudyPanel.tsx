"use client";

import { useRef, useState } from "react";
import type { CondoRecordsView } from "@/lib/condo-records";
import {
  createParcelStudy, deriveParcelStudyScope, deriveParcelStudyScenarios,
  exportParcelStudy, importParcelStudy,
  type ParcelStudyDraft, type ParcelStudyScope,
} from "@/lib/architect/parcel-study";
import { useParcelStudyRecords } from "@/lib/architect/use-parcel-study-records";
import { ParcelStudyMap } from "./ParcelStudyMap";
import { ParcelStudyRecords } from "./ParcelStudyRecords";

const ARRANGEMENTS = [
  ["together", "Together", "One proposed zoning lot"],
  ["separate", "Separately", "One proposed site per parcel"],
  ["compare", "Compare", "Both arrangements side by side"],
] as const;

function lotName(bbl: string) { return `Lot ${Number(bbl.slice(6))}`; }

/** Planning form only. This component never requests an allowance, writes a
 * site-definition confirmation, or supplies a grouping to the rule engine. */
export function ParcelStudyPanel({ requestedBbl, records, recordsConflict = false }: {
  requestedBbl: string;
  records: CondoRecordsView;
  recordsConflict?: boolean;
}) {
  if (records.outcome !== "multi_lot_set") return null;
  const result = deriveParcelStudyScope({
    enteredBbl: records.enteredBbl, billingBbl: records.billingBbl, baseLots: records.baseLots,
  });
  if (records.enteredBbl !== requestedBbl || recordsConflict || records.studyIdentityIntegrity !== true || !result.ok) {
    return <section className="card parcel-study" aria-label="Parcel study">
      <h2>Parcel study needs matching records</h2>
      <p role="status">{!result.ok ? result.message : records.studyIdentityIntegrity !== true
        ? "The complete source parcel identities could not be validated. A study cannot use a partial or altered parcel set."
        : "The property and condo records disagree. A study cannot use this parcel set."}</p>
      <a href="#condo-records">Inspect the recorded parcel identities</a>
    </section>;
  }
  // Identity/membership changes unmount the draft, pending imports and source
  // requests; a choice made for one property never appears on another.
  return <StudyWorkspace key={result.scope.key} scope={result.scope} records={records}/>;
}

function StudyWorkspace({ scope, records }: { scope: ParcelStudyScope; records: CondoRecordsView }) {
  const [draft, setDraft] = useState<ParcelStudyDraft>(() => createParcelStudy(scope));
  const [transferMessage, setTransferMessage] = useState("");
  const [importError, setImportError] = useState("");
  const fileInput = useRef<HTMLInputElement>(null);
  const basisDetails = useRef<HTMLDetailsElement>(null);
  const importSequence = useRef(0);
  const source = useParcelStudyRecords(scope.baseBbls, scope.billingBbl);
  const scenarios = deriveParcelStudyScenarios(draft);
  const outlines = source.records.map(record => ({ bbl: record.bbl, outcome: record.outlineOutcome, loading: record.outlineOutcome === null }));
  const confirmation = records.siteDefinition?.activeConfirmation;

  function download() {
    const result = exportParcelStudy(draft, scope);
    if (!result.ok) { setImportError(result.message); return; }
    const url = URL.createObjectURL(new Blob([result.json], { type: "application/json" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = `parcel-study-${scope.enteredBbl}.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    // Give the browser a turn to consume the download before releasing it.
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    setImportError("");
    setTransferMessage("Study choices downloaded. Source records and legal status are not included.");
  }

  async function restore(file: File | undefined) {
    if (!file) return;
    const sequence = ++importSequence.current;
    setTransferMessage("");
    setImportError("");
    if (file.size > 65_536) { setImportError("Choose a study file smaller than 64 KiB."); return; }
    try {
      const result = importParcelStudy(await file.text(), scope);
      if (sequence !== importSequence.current) return;
      if (!result.ok) { setImportError(result.message); return; }
      setDraft(result.draft);
      setTransferMessage("Study choices restored. Current source records remain unchanged.");
    } catch {
      if (sequence === importSequence.current) setImportError("The study file could not be read.");
    }
  }

  return <section className="card parcel-study" aria-labelledby="parcel-study-title" data-testid="parcel-study">
    <div className="architect-panel-heading">
      <div><p className="architect-eyebrow">{scope.baseBbls.length} recorded base parcels</p><h2 id="parcel-study-title">How would you use this land?</h2></div>
      <span className="architect-status">Hypothetical study</span>
    </div>
    <p className="parcel-study-boundary">Legal zoning-lot arrangement: <strong>Not established here</strong> <a href="#parcel-study-basis" onClick={() => { if (basisDetails.current) basisDetails.current.open = true; }}>Why?</a></p>
    <fieldset className="parcel-study-options">
      <legend>Study arrangement</legend>
      {ARRANGEMENTS.map(([value, label, description]) => <label key={value} className={draft.arrangement === value ? "is-selected" : ""}>
        <input type="radio" name="parcel-study-arrangement" value={value} checked={draft.arrangement === value} onChange={() => setDraft({ ...draft, arrangement: value })}/>
        <span><strong>{label}</strong><small>{description}</small></span>
      </label>)}
    </fieldset>
    <div className="parcel-study-canvas">
      <ParcelStudyMap outlines={outlines} contextOutline={source.contextOutline} arrangement={draft.arrangement}/>
      <div className="parcel-study-decisions">
        {draft.arrangement !== "separate" ? <fieldset>
          <legend>Buildings on the combined site</legend>
          {([ ["undecided", "Not decided"], ["one", "One building"], ["multiple", "Multiple buildings"] ] as const).map(([value, label]) => <label className="parcel-study-radio" key={value}>
            <input type="radio" name="parcel-study-buildings" value={value} checked={draft.buildingScheme === value} onChange={() => setDraft({ ...draft, buildingScheme: value })}/>{label}
          </label>)}
          <p className="section-note">Multiple buildings can share one proposed site.</p>
        </fieldset> : null}
        <fieldset>
          <legend>Existing buildings — your study assumption</legend>
          {draft.existingBuildings.map(item => <label className="parcel-study-intent" key={item.bbl}>
            <span>{lotName(item.bbl)} <small>{item.bbl}</small></span>
            <select aria-label={`Existing buildings on ${lotName(item.bbl)}`} value={item.intent} onChange={event => {
              const intent = event.target.value as typeof item.intent;
              setDraft({ ...draft, existingBuildings: draft.existingBuildings.map(record => record.bbl === item.bbl ? { ...record, intent } : record) });
            }}>
              <option value="undecided">Not decided</option><option value="retain">Retain</option><option value="alter">Alter</option><option value="demolish">Demolish</option>
            </select>
          </label>)}
          <small className="section-note">Parcel-level intent only. Buildings spanning parcels and available rights still need review.</small>
        </fieldset>
      </div>
    </div>
    <div className="parcel-study-comparison" role="region" aria-label="Study comparison" aria-live="polite">
      {scenarios.map(scenario => <article key={scenario.id} className="parcel-study-scenario">
        <div className="architect-panel-heading"><h3>{scenario.id === "combined" ? "Together" : "Separately"}</h3><span className="architect-status">Assumed arrangement</span></div>
        <p className="parcel-study-site-count">{scenario.sites.length} proposed {scenario.sites.length === 1 ? "site" : "sites"}</p>
        <ul className="parcel-study-sites">{scenario.sites.map(site => <li key={site.id}>{site.baseBbls.map(lotName).join(" + ")}</li>)}</ul>
        <p>{scenario.id === "combined"
          ? draft.buildingScheme === "one" ? "One proposed building · shared site allowance" : draft.buildingScheme === "multiple" ? "Multiple proposed buildings · shared site allowance" : "Building count not decided · shared site allowance"
          : "Independent allowances would require independently valid zoning lots."}</p>
        <dl className="parcel-study-limit-status">
          <div><dt>Height</dt><dd>Not calculated</dd></div>
          <div><dt>Buildable width / depth</dt><dd>Not calculated</dd></div>
          <div><dt>Available floor area</dt><dd>Not calculated</dd></div>
        </dl>
        <p className="section-note">{scenario.id === "combined" ? "Combined treatment has not been established." : "Separate development rights have not been established."}</p>
      </article>)}
    </div>
    <div className="architect-panel-heading parcel-study-records-heading"><h3>Each parcel’s city records</h3><button type="button" className="architect-text-button" onClick={source.retry} disabled={source.loading}>{source.loading ? "Loading records…" : "Refresh records"}</button></div>
    <ParcelStudyRecords records={source.records}/>
    <details ref={basisDetails} id="parcel-study-basis" className="provenance-details">
      <summary>Why limits are unavailable · site status and sources</summary>
      <dl className="parcel-study-basis">
        <div><dt>Site identity</dt><dd>The condo record links tax parcels. It does not establish a legal zoning lot. A study choice does not combine or separate property legally.</dd></div>
        <div><dt>Recorded confirmation</dt><dd>{confirmation ? "A site confirmation is recorded; it is not used to authorize this study or its calculations." : "No active site confirmation is supplied."} <a href="#condo-records">Inspect confirmation status and parcel discrepancies</a></dd></div>
        <div><dt>Geometry and rules</dt><dd>The outlines are display-only. This study does not run a combined-site or separate-site envelope calculation. Height, yards, coverage and footprint dimensions need supported rules and the relevant measured inputs.</dd></div>
        <div><dt>Existing rights</dt><dd>Retained floor area, recorded allocations and buildings spanning parcels must be reconciled. Selecting demolition does not prove additional rights are available.</dd></div>
        <div><dt>Zoning districts</dt><dd>Each parcel’s recorded districts remain visible. This study does not average FAR, choose a higher district, add allowances, or count the condo billing record as another land parcel.</dd></div>
        <div><dt>Condo source</dt><dd>{records.provenance.sourceId ?? "Unknown source"} · retrieved {records.provenance.retrievedAt ?? "at an unknown time"}. <a href="#condo-records">All captured condo records</a></dd></div>
      </dl>
    </details>
    <div className="parcel-study-transfer">
      <button type="button" className="secondary-button" onClick={download}>Download study choices</button>
      <button type="button" className="secondary-button" onClick={() => fileInput.current?.click()}>Restore study choices</button>
      <input ref={fileInput} type="file" accept=".json,application/json" aria-label="Restore parcel study file" hidden onChange={event => { void restore(event.target.files?.[0]); event.target.value = ""; }}/>
      <small>Choices stay in this page until downloaded. No property record is changed.</small>
    </div>
    {transferMessage ? <p role="status">{transferMessage}</p> : null}
    {importError ? <p role="alert">{importError}</p> : null}
  </section>;
}
