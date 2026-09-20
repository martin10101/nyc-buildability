"use client";
import Link from "next/link";
import type { PropertyProfile } from "@/lib/contract";
import type { Scenario } from "@/lib/scenario-contract";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import { fieldLabel } from "@/lib/format";
import { provenanceById } from "@/lib/provenance";
import { zolaLotUrl } from "@/lib/provenance-link";
import { propertyHref } from "@/lib/architect/navigation";
import {
  CONDO_OUTCOME_RESOLVED_SINGLE,
  channelWithholdsAllowances,
  deriveCondoChannelState,
  useCondoRecords,
  type CondoChannelState,
  type CondoRecordsOutcome,
  type CondoRecordsView,
} from "@/lib/condo-records";
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
//
// M5-T052 (DB-031, the T045 G3-A2 answer): the OK token is imported from the
// condo-records client, which owns the ONE outcome-token vocabulary the api
// (app.connectors.condo_base_lot OUTCOME_*), this fail-safe guard, and the new
// per-BBL records channel all share. api and web are pinned to the same literal
// by tests on BOTH sides, so the guard and the records channel can never
// classify the same resolution differently.
const CONDO_ALLOWANCE_OK_OUTCOME = CONDO_OUTCOME_RESOLVED_SINGLE;
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
// The PROFILE half of the condo fail-safe (the accepted M5-T045 allow-list). It
// derives, from the profile channels alone, whether the accepted guard withholds
// allowances (condoWithholdsAllowances reads exactly this). It is folded together
// with the live per-BBL records channel by deriveCondoSurface below into the ONE
// shared surface decision that BOTH the screen (PropertyOverview) and the printed
// brief (ReportView) consume — so the guard, the records section, the
// substitution explanation, and a profile/channel disagreement can never differ
// across the two surfaces (the T045 G3-A2 single-source-of-truth answer). This
// profile derivation is byte-unchanged from M5-T045: the channel may only ADD
// withholding, never remove it (records never unlock allowances).
export type CondoDisplayState = {
    // Any condo channel is populated (a resolution note or a multi-lot conflict).
    present: boolean;
    // The fail-safe result: NO computed development allowance may be shown.
    withholdsAllowances: boolean;
    notes: CondoResolutionNote[];
    multiLot: PropertyProfile["conflicts"];
};
/**
 * Derive the single condo-display state from a profile. Fail-SAFE allow-list:
 * allowances survive ONLY when every present condo_resolution note is the
 * recognised success outcome (resolved_single_base_lot — the analysis ran on the
 * substituted base lot). ANY other state withholds them — a multi-lot base-lot
 * set (a condo_base_lot_resolution conflict), an unresolved / typed-error note, a
 * note whose machine outcome token is MISSING or malformed (outcome null), or a
 * note carrying an UNKNOWN outcome token this build does not recognise. A
 * non-condo profile (no condo_resolution note and no multi-lot conflict) is
 * unaffected (withholdsAllowances false), so its allowances render normally and
 * non-condo behavior stays byte-identical.
 */
export function deriveCondoDisplay(profile: PropertyProfile): CondoDisplayState {
    const notes = condoResolutionNotes(profile);
    const multiLot = profile.conflicts.filter(conflict => conflict.field === CONDO_RESOLUTION_FIELD);
    const present = notes.length > 0 || multiLot.length > 0;
    // Withhold on a multi-lot conflict OR on ANY note that is not positively the
    // recognised success outcome — a missing/malformed token (outcome null) or an
    // unknown token both fail this check, so an unparseable or future outcome
    // withholds, never shows.
    const withholdsAllowances =
        multiLot.length > 0 ||
        notes.some(note => note.outcome !== CONDO_ALLOWANCE_OK_OUTCOME);
    return { present, withholdsAllowances, notes, multiLot };
}
/**
 * True when a recorded condo billing-BBL resolution means NO computed
 * development allowance may be shown for this profile. A thin reader of the ONE
 * derived state (deriveCondoDisplay), so this fail-safe guard and the records
 * section can never diverge. This is a DISPLAY fail-safe layered on top of the
 * backend live-provider fail-safe: even if a scenario or rule evaluation matching
 * this BBL is present and would otherwise be displayable, the computed allowance
 * is withheld here and only RECORDS are shown (D-073-R006).
 */
export function condoWithholdsAllowances(profile: PropertyProfile): boolean {
    return deriveCondoDisplay(profile).withholdsAllowances;
}
// M5-T052 reconciliation: the printed brief no longer carries a separate
// profile-only records component (the former CondoResolutionRecords, which read
// the profile multi-lot conflict alone and still spoke allowance-class wording).
// The brief (ReportView) now consumes the SAME shared surface decision
// (deriveCondoSurface) and renders the SAME CondoRecordsChannelSection the screen
// uses, so records, substitution, a profile/channel disagreement, and honest
// absence are one source of truth across both surfaces, and no allowance-class
// vocabulary lives in the printed records section (the D-073-R006 grep gate).
// ONE coherent condo-surface decision (M5-T052, the T045 G3-A2 answer). The
// architect SCREEN reads the production per-BBL records channel
// (useCondoRecords) and combines it with the ACCEPTED profile fail-safe guard
// (condoWithholdsAllowances) in exactly ONE place, so the fail-safe guard, the
// records-section eligibility, and the substitution explanation can never
// disagree. The combination is MONOTONIC: the channel may only ADD withholding
// (multi-lot / unresolved / typed resolver error), never remove it — records
// never unlock allowances (D-073-R006). A transport failure or an absent route
// is `unavailable`, which does NOT withhold on its own: a condo-records outage
// must not blank every property's allowances, so the accepted profile/backend
// fail-safes stay authoritative. `conflict` records when the profile guard and
// the channel BOTH carry a condo signal yet disagree on withholding — a
// disagreement that fails safe (withhold) and is surfaced, never hidden.
export type CondoSurfaceDecision = {
    withholdAllowances: boolean;
    showRecords: boolean;
    showSubstitution: boolean;
    conflict: boolean;
    channel: CondoChannelState;
    recordsView: CondoRecordsView | null;
};
export function deriveCondoSurface(profile: PropertyProfile, outcome: CondoRecordsOutcome | null): CondoSurfaceDecision {
    const profileState = deriveCondoDisplay(profile);
    const profileWithholds = profileState.withholdsAllowances;
    const channel = deriveCondoChannelState(outcome);
    const channelWithholds = channelWithholdsAllowances(channel);
    const channelHasSignal = channel.kind === "single" || channel.kind === "multi_lot" || channel.kind === "unresolved" || channel.kind === "resolver_error";
    // Both sides carry a condo signal but disagree on the fail-safe: withhold
    // (the OR below already guarantees it) and surface the disagreement.
    const conflict = profileState.present && channelHasSignal && profileWithholds !== channelWithholds;
    const withholdAllowances = profileWithholds || channelWithholds;
    // The records section is shown ONLY for a channel-confirmed multi-lot condo.
    const showRecords = channel.kind === "multi_lot";
    // The substitution explanation is the allow path: a channel-confirmed single
    // base lot that nothing else is withholding.
    const showSubstitution = channel.kind === "single" && !withholdAllowances;
    const recordsView = channel.kind === "multi_lot" || channel.kind === "single" ? channel.view : null;
    return { withholdAllowances, showRecords, showSubstitution, conflict, channel, recordsView };
}
// The production channel-driven condo section on the architect SCREEN. Renders
// UNDER the professional-review fail-safe (development limits), never instead of
// it. RECORDS/records-class wording ONLY — no allowance-class vocabulary lives
// inside this section (the D-073-R006 grep gate; HJ-A3 heading semantics).
export function CondoRecordsChannelSection({ decision }: {
    decision: CondoSurfaceDecision;
}) {
    const { showRecords, showSubstitution, conflict, recordsView } = decision;
    // Allow path: a single recorded base lot. The city records that the condo's
    // land is a base tax lot; the analysis runs on it. Stated as entered vs
    // analyzed — a city record of the mapping, not a computed result.
    if (showSubstitution && recordsView) {
        const sub = recordsView.substitution;
        const entered = sub?.enteredBbl ?? recordsView.enteredBbl ?? recordsView.billingBbl ?? "the condo lot you entered";
        const analyzed = sub?.analyzedBbl ?? recordsView.baseLots[0]?.bbl ?? "the recorded base lot";
        return <section className="card architect-condo-substitution" role="group" aria-label="Recorded base lot for this condo" data-testid="condo-substitution-record">
      <h2>Recorded base lot for this condo</h2>
      <p className="section-note">The analysis runs on the land parcel the city records for this condo. You entered {entered}; the city records base tax lot {analyzed} as this condo&apos;s land, and the analysis runs on that recorded base lot. This is a city record of the mapping, stated as entered versus analyzed.</p>
      <p className="section-note" data-testid="condo-substitution-provenance">Source: {recordsView.provenance.sourceId ?? "not recorded (unknown)"} · dataset(s): {recordsView.provenance.datasetIds.length ? recordsView.provenance.datasetIds.join(", ") : "not recorded (unknown)"} · dataset version: {recordsView.provenance.datasetVersion ?? "not recorded (unknown)"} · retrieved: {recordsView.provenance.retrievedAt ?? "not recorded (unknown)"}</p>
    </section>;
    }
    // Multi-lot records view (the D-073-R006 records display). The professional-
    // review fail-safe above governs; these are city records, shown for reference.
    if (showRecords && recordsView) {
        // Honest zoning gating (DB-036(e)): the divergent-zoning notice is a
        // legal question only when zoning is ACTUALLY recorded for a base lot;
        // the recorded-zoning gap note surfaces only when at least one base lot's
        // zoning is a genuine unknown. Both derive from the parsed per-lot status.
        const anyZoningRecorded = recordsView.baseLots.some(lot => lot.recordedZoningStatus === "recorded");
        const anyZoningUnknown = recordsView.baseLots.some(lot => lot.recordedZoningStatus !== "recorded");
        // DB-036(e): name the concrete lot-level zoning source in plain language
        // (the city's Zoning Tax Lot Database, ZTLDB) and scope the sentence to
        // what is actually missing. When SOME base lots already carry a recorded
        // district, the copy must NOT imply that the recorded zoning shown above is
        // unavailable — only that it is not yet shown for EVERY base lot. When NO
        // base lot carries recorded zoning the gap covers all of them.
        const zoningGapNote = anyZoningRecorded
          ? "Recorded zoning is not yet shown for every base lot above. New York City keeps lot-level zoning in a separate database — the Zoning Tax Lot Database (ZTLDB) — that is not connected here; the base lots marked not recorded are city identity records whose zoning is left as an explicit unknown rather than guessed, while the recorded districts shown above are unaffected."
          : "Recorded zoning is not yet shown for these base lots. New York City keeps lot-level zoning in a separate database — the Zoning Tax Lot Database (ZTLDB) — that is not connected here, so the base lots above are shown as city identity records only, and their zoning is left as an explicit unknown rather than guessed.";
        // Entered vs billing are DISTINCT identifiers (DB-036(b)): the entered BBL
        // is what the user typed (validated via lib/bbl.ts); the billing lot is
        // recorded only for a billing-class input and is a labelled unknown for a
        // unit-class input — never the entered unit BBL relabelled as billing.
        const enteredLot = recordsView.enteredBbl ?? "not recorded (unknown)";
        const billingLot = recordsView.billingBblStatus === "recorded" && recordsView.billingBbl
          ? recordsView.billingBbl
          : "not recorded (unknown)";
        return <section className="card architect-condo-records" role="group" aria-label="City records for this condo" data-testid="condo-resolution-records">
      <h2>City records for this condo</h2>
      <p className="section-note">These are the tax lots the city records for the condo lot you entered. They are city records of the condo&apos;s land, shown for reference under the development limits above.{conflict ? " The property record and the city records channel differ on this condo; the lots below are what the city records channel returned." : ""}</p>
      <p className="architect-condo-entered-lot section-note" data-testid="condo-entered-lot">Condo lot you entered: {enteredLot}</p>
      <p className="architect-condo-billing-lot section-note" data-testid="condo-billing-lot">Condo billing lot: {billingLot}</p>
      <ul>
        {recordsView.baseLots.map((lot, index) => <li key={`base-${index}`} className="architect-condo-record" data-testid="condo-base-lot-record">Recorded base lot {lot.bbl} <span className="section-note" data-testid="condo-base-lot-zoning">— recorded zoning: {lot.recordedZoning ?? "not recorded (unknown)"}</span></li>)}
      </ul>
      {anyZoningRecorded && recordsView.divergentZoningNotice ? <p className="section-note" data-testid="condo-divergent-notice">{recordsView.divergentZoningNotice}</p> : null}
      {anyZoningUnknown && recordsView.recordedZoningDependency ? <p className="section-note" data-testid="condo-zoning-dependency">{zoningGapNote}</p> : null}
      <p className="section-note" data-testid="condo-records-provenance">Source: {recordsView.provenance.sourceId ?? "not recorded (unknown)"} · dataset(s): {recordsView.provenance.datasetIds.length ? recordsView.provenance.datasetIds.join(", ") : "not recorded (unknown)"} · dataset version: {recordsView.provenance.datasetVersion ?? "not recorded (unknown)"} · retrieved: {recordsView.provenance.retrievedAt ?? "not recorded (unknown)"}</p>
    </section>;
    }
    // A disagreement that did not resolve to a confirmed multi-lot set (e.g. the
    // channel reports a single lot while the property record withholds): the
    // fail-safe above governs; surface the difference honestly, show no records.
    if (conflict) {
        return <section className="card architect-condo-records" role="status" data-testid="condo-records-conflict">
      <p className="section-note">The city records channel and the property record differ on this condo, so no city records are shown here. The development limits above govern.</p>
    </section>;
    }
    // loading / unavailable / unresolved / typed resolver error / non-condo:
    // honest absence — no records section (the fail-safe surface stands alone).
    return null;
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
    // M5-T052 (D-073-R006): the production per-BBL condo-records channel and the
    // accepted profile fail-safe guard fold into ONE decision (deriveCondoSurface),
    // so the fail-safe guard, the records section, and the substitution
    // explanation can never disagree. A multi-lot / unresolved / typed-error condo
    // withholds EVERY computed development allowance — even when a scenario or rule
    // evaluation matching this BBL is present and would otherwise be displayable.
    // A resolved single base lot (allow path) and a non-condo property are
    // unaffected, so their allowances render normally; the records section renders
    // UNDER the professional-review fail-safe, never instead of it.
    const condoRecordsOutcome = useCondoRecords(bbl);
    const condo = deriveCondoSurface(profile, condoRecordsOutcome);
    const withholdAllowances = condo.withholdAllowances;
    const shownScenario = withholdAllowances ? null : scenario;
    const shownEvaluation = withholdAllowances ? null : evaluation;
    return <>
    <PropertyIssuesSummary profile={profile}/>
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
    <CondoRecordsChannelSection decision={condo}/>
    <ZoningContextPanel profile={profile}/>
    <details className="card architect-disclosure architect-existing-building">
      <summary>Existing building information</summary>
      <FactsTable title="Existing building facts" facts={profile.existing_building_facts} byId={provenanceById(profile)} reproducibility={profile.reproducibility} onInspect={onInspect}/>
      <Link href={propertyHref(bbl, "facts")}>All property facts →</Link>
    </details>
  </>;
}
