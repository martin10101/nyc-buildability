import Link from "next/link";
import type { PropertyProfile, ConflictValue } from "@/lib/contract";
import { conflictValueDerivation } from "@/lib/contract";
import type { Scenario } from "@/lib/scenario-contract";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import { fieldLabel, formatValue } from "@/lib/format";
import { provenanceById } from "@/lib/provenance";
import { zolaLotUrl } from "@/lib/provenance-link";
import { propertyHref } from "@/lib/architect/navigation";
import { LotOutlineMap } from "@/components/address/LotOutlineMap";
import { FactsTable } from "@/components/property/FactsTable";
import { ABSENT_BBL_MAP_LINK_NOTE, ZOLA_LOT_LINK_LABEL } from "./AddressAutocomplete";
import { DevelopmentLimits } from "./DevelopmentLimits";
import { ZoningContextPanel } from "./ZoningContextPanel";
export { DraftHeadline } from "./DevelopmentLimits";
export function PropertyIssuesSummary({ profile }: {
    profile: PropertyProfile;
}) {
    const conflicts = profile.conflicts.filter(item => item.resolution === "unresolved");
    const critical = profile.missing_inputs.filter(item => item.criticality === "critical");
    return <>
    {conflicts.length > 0 ? <div className="architect-alert" role="status">
      <strong>Unresolved data conflicts</strong>
      <p>
        {conflicts.map(item => fieldLabel(item.field)).join(" · ")}
      </p>
      <Link href={propertyHref(profile.identity.bbl, "issues")}>Review conflicting source values →</Link>
    </div> : null}
    {critical.length > 0 ? <div className="architect-alert" role="status">
      <strong>Critical inputs missing</strong>
      <p>
        {critical.map(item => fieldLabel(item.field)).join(" · ")}
      </p>
      <Link href={propertyHref(profile.identity.bbl, "issues")}>Review missing inputs →</Link>
    </div> : null}
    {profile.reproducibility?.staleness?.stale ? <p className="architect-alert">The property source is stale. Captured dates and retrieval status are available in Evidence.</p> : null}
  </>;
}
// M5-T045 (D-073-R006): condo billing-BBL -> base-lot resolution presented as
// RECORDS, never allowances. This reads ONLY the existing contract-1.3.0
// channels the accepted backend seam emits (condo_resolution_report,
// services/api/app/profile/zoning_crosscheck.py) — NO invented contract field
// and NO inference from identity vs analyzed BBLs (that neutral
// entered-vs-analyzed record lives in AnalysisIdentityNotice; a differing BBL is
// never read here as a condo resolution):
//   - reproducibility.connector_notes strings prefixed `condo_resolution:` carry
//     the resolved-single / unresolved / typed-error records (the note text is
//     the backend's own human-readable record, re-presented verbatim).
//   - a conflicts entry with field `condo_base_lot_resolution` carries the
//     multi-lot case: every recorded base lot as a RECORD (never a chosen
//     answer, never a computed allowance).
// When neither channel is populated — every profile today, because the live
// route wiring that fills them is held for orchestrator disposition (see the
// M5-T045 producer report, section on the remaining live-wiring dependency) —
// this renders NOTHING, so non-condo behavior stays byte-identical.
const CONDO_RESOLUTION_FIELD = "condo_base_lot_resolution";
const CONDO_RESOLUTION_NOTE_PREFIX = "condo_resolution:";
// The backend stamps each condo_resolution note with a machine-readable outcome
// token in brackets right after the prefix — e.g.
// "condo_resolution: [resolved_single_base_lot] billing BBL ..." — from
// services/api/app/profile/zoning_crosscheck.py (_condo_note_prefix). Parsing
// the TOKEN, never the human prose, lets the display distinguish a resolved
// single base lot (the analysis ran on the substituted base lot, so its computed
// allowances are valid) from the fail-safe outcomes that must withhold every
// computed allowance. The token equals the seam's CondoResolution.outcome
// (app.connectors.condo_base_lot OUTCOME_*), so the two sides can never drift.
const CONDO_RESOLUTION_NOTE_RE = /^condo_resolution:\s*\[([a-z_]+)\]\s*/;
// The ONE condo outcome token for which computed development allowances may be
// shown: OUTCOME_RESOLVED_SINGLE (app.connectors.condo_base_lot) — the analysis
// ran on the single substituted base lot, so its allowances are valid. Every
// OTHER present condo_resolution note withholds them: the fail-safe outcomes
// (multi_lot_set / unresolved / error), a MISSING or malformed token (a legacy /
// defensive note the outcome regex could not parse -> outcome null), and any
// UNKNOWN token this build does not recognise (e.g. a future backend outcome).
// This is an allow-list, not a deny-list, so the display fails SAFE on ambiguity
// rather than open: it never shows a computed allowance for a condo billing-BBL
// resolution it cannot positively confirm ran on a single base lot (D-073-R006).
const CONDO_ALLOWANCE_OK_OUTCOME = "resolved_single_base_lot";
type CondoResolutionNote = {
    outcome: string | null;
    text: string;
};
// Parse the condo_resolution notes on a profile into {outcome token, display
// text}. A note without a token (legacy/defensive) falls back to stripping just
// the prefix, so its text still renders cleanly even though it carries no
// machine outcome.
function condoResolutionNotes(profile: PropertyProfile): CondoResolutionNote[] {
    return (profile.reproducibility?.connector_notes ?? [])
        .filter(note => note.startsWith(CONDO_RESOLUTION_NOTE_PREFIX))
        .map(note => {
        const match = CONDO_RESOLUTION_NOTE_RE.exec(note);
        return match
            ? { outcome: match[1], text: note.slice(match[0].length).trim() }
            : { outcome: null, text: note.slice(CONDO_RESOLUTION_NOTE_PREFIX.length).trim() };
    });
}
function condoHasMultiLot(profile: PropertyProfile): boolean {
    return profile.conflicts.some(conflict => conflict.field === CONDO_RESOLUTION_FIELD);
}
/**
 * True when a recorded condo billing-BBL resolution means NO computed
 * development allowance may be shown for this profile. Fail-SAFE allow-list:
 * allowances survive ONLY when every present condo_resolution note is the
 * recognised success outcome (resolved_single_base_lot — the analysis ran on the
 * substituted base lot). ANY other state withholds them — a multi-lot base-lot
 * set (a condo_base_lot_resolution conflict), an unresolved / typed-error note, a
 * note whose machine outcome token is MISSING or malformed (outcome null), or a
 * note carrying an UNKNOWN outcome token this build does not recognise. A
 * non-condo profile (no condo_resolution note and no multi-lot conflict) is
 * unaffected and returns false, so its allowances render normally and non-condo
 * behavior stays byte-identical. This is a DISPLAY fail-safe layered on top of
 * the backend live-provider fail-safe: even if a scenario or rule evaluation
 * matching this BBL is present and would otherwise be displayable, the computed
 * allowance is withheld here and only RECORDS are shown (D-073-R006).
 */
export function condoWithholdsAllowances(profile: PropertyProfile): boolean {
    if (condoHasMultiLot(profile))
        return true;
    // Withhold on ANY note that is not positively the recognised success outcome
    // — a missing/malformed token (outcome null) or an unknown token both fail
    // this check, so an unparseable or future outcome withholds, never shows.
    return condoResolutionNotes(profile).some(note => note.outcome !== CONDO_ALLOWANCE_OK_OUTCOME);
}
// Recorded zoning for a multi-lot base-lot record, read from the EXISTING
// conflict-value channel (open-schema `recorded_zoning` key, same pattern as
// conflictValueDerivation). Absent or blank -> null so the display preserves
// UNKNOWN zoning honestly, never fabricating a district. Populating this per
// base lot in production is the out-of-scope live-propagation change routed to
// the orchestrator (see the M5-T045 producer report).
function conflictValueRecordedZoning(value: ConflictValue): string | null {
    const record = value as Record<string, unknown>;
    const zoning = record.recorded_zoning;
    return typeof zoning === "string" && zoning.trim() !== "" ? zoning.trim() : null;
}
export function CondoResolutionRecords({ profile }: {
    profile: PropertyProfile;
}) {
    const notes = condoResolutionNotes(profile);
    const multiLot = profile.conflicts.filter(conflict => conflict.field === CONDO_RESOLUTION_FIELD);
    if (notes.length === 0 && multiLot.length === 0)
        return null;
    return <section className="card architect-condo-records" role="group" aria-label="Condo billing lot resolution record" data-testid="condo-resolution-records">
    <strong>Condo billing lot — recorded base lot(s)</strong>
    <p className="section-note">This records how the condo billing lot you entered maps to its recorded base tax lot(s). It is a record, not a computed development allowance — allowances are calculated only for an established base lot and are shown separately.</p>
    {notes.map((note, index) => <p key={`note-${index}`} className="architect-condo-record" data-testid="condo-resolution-note">{note.text}</p>)}
    {multiLot.map((conflict, index) => <div key={`multilot-${index}`} className="architect-condo-multilot" data-testid="condo-resolution-multilot">
      <strong>Multiple recorded base lots — no computed allowance</strong>
      <ul>
        {conflict.values.map((entry, valueIndex) => {
        const derivation = conflictValueDerivation(entry);
        const zoning = conflictValueRecordedZoning(entry);
        return <li key={`base-${valueIndex}`} data-testid="condo-base-lot-record">Recorded base lot {formatValue(entry.value)} <span className="section-note">(source {entry.source_id})</span> <span className="section-note" data-testid="condo-base-lot-zoning">— recorded zoning: {zoning ?? "not recorded (unknown)"}</span>{derivation ? <span className="section-note"> — {derivation}</span> : null}</li>;
    })}
      </ul>
      <p className="section-note">Divergent zoning across a condo&apos;s base lots is a qualified-human legal question; no single base lot is presented as the answer and no allowance is computed here.</p>
    </div>)}
  </section>;
}
export function PropertyOverview({ profile, scenario, evaluation = null, onInspect }: {
    profile: PropertyProfile;
    scenario: Scenario | null;
    evaluation?: RuleEvaluation | null;
    onInspect: (id: string) => void;
}) {
    const bbl = profile.identity.bbl;
    // DB-005: the only ZoLa link on this surface goes through the validated
    // helper (null on a non-canonical BBL -> render NO link, never a raw
    // template string). Same discipline as the accepted M5-T032 work.
    const siteZolaUrl = zolaLotUrl(bbl);
    // D-073-R006: a multi-lot / unresolved condo billing-BBL profile withholds
    // EVERY computed development allowance — even when a scenario or rule
    // evaluation matching this BBL is present and would otherwise be displayable.
    // Only RECORDS (CondoResolutionRecords) are shown. A resolved single base lot
    // and a non-condo profile are unaffected, so their allowances render normally.
    const withholdAllowances = condoWithholdsAllowances(profile);
    const shownScenario = withholdAllowances ? null : scenario;
    const shownEvaluation = withholdAllowances ? null : evaluation;
    return <>
    <PropertyIssuesSummary profile={profile}/>
    <CondoResolutionRecords profile={profile}/>
    <div className="architect-overview-grid">
      <div>
        <DevelopmentLimits profile={profile} scenario={shownScenario} evaluation={shownEvaluation} onInspect={onInspect}/>
        <Link className="primary-button" href={propertyHref(bbl, "zoning")}>View zoning details <span aria-hidden="true">→</span></Link>
      </div>
      <section className="card architect-map-card">
        <div className="architect-panel-heading">
          <h2>Site context</h2>
          {siteZolaUrl ? (
            <a href={siteZolaUrl} target="_blank" rel="noopener noreferrer" data-testid="site-zola-link">{ZOLA_LOT_LINK_LABEL} <span aria-hidden="true">↗</span></a>
          ) : (
            // DB-019b/DB-024(b): honest absence when there is no canonical BBL,
            // rendered from the single shared ABSENT_BBL_MAP_LINK_NOTE constant so
            // this note stays byte-identical to the AddressConfirmCard and
            // ZoningContextPanel notes. Never a raw template-string URL for a lot
            // the source did not identify.
            <span className="section-note" data-testid="site-zola-absent">{ABSENT_BBL_MAP_LINK_NOTE}</span>
          )}
        </div>
        <LotOutlineMap bbl={bbl} context/>
      </section>
    </div>
    <ZoningContextPanel profile={profile}/>
    <details className="card architect-disclosure architect-existing-building">
      <summary>Existing building information</summary>
      <FactsTable title="Existing building facts" facts={profile.existing_building_facts} byId={provenanceById(profile)} reproducibility={profile.reproducibility} onInspect={onInspect}/>
      <Link href={propertyHref(bbl, "facts")}>All property facts →</Link>
    </details>
  </>;
}
