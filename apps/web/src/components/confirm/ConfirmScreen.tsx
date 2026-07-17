"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { fetchPropertyProfile, type LookupOutcome } from "@/lib/api";
import { validateBblInput } from "@/lib/bbl";
import { completenessDisplay } from "@/lib/coverage";
import {
  mappedFeatureView,
  type FactValue,
  type MappedFeatureView,
  type PropertyProfile,
  type SourceFact,
} from "@/lib/contract";
import { fieldLabel, formatValue } from "@/lib/format";
import { provenanceById } from "@/lib/provenance";
import { ConflictsSection } from "@/components/property/ConflictsSection";
import { CoverageBadge } from "@/components/property/CoverageBadge";
import { CoverageLegend } from "@/components/property/CoverageLegend";
import { OutcomeFailureStates } from "@/components/property/FailureState";
import { InternalBanner } from "@/components/property/InternalBanner";
import { LoadingStages } from "@/components/property/LoadingStages";
import { ProvenanceDisclosure } from "@/components/property/ProvenanceDisclosure";
import { ZoningSection } from "@/components/property/ZoningSection";

/**
 * Confirm screen — PRODUCT_FLOW step 2 (task M2-T002 output B).
 *
 * Presents the compact property card: canonical address, BBL/BIN, lot
 * summary, existing-building facts, zoning districts/overlays/special
 * districts, landmark/flood/pending flags, data conflicts, and ONLY the
 * questions government data cannot answer.
 *
 * HONESTY RULES APPLIED HERE:
 * - Confirm/override affordances are labeled for what the API provides
 *   TODAY: the canonical contract defines `user_confirmations`, but no
 *   endpoint accepts them yet, so nothing is persisted and the controls
 *   say so explicitly (no pretend persistence; depends on the
 *   analysis-run work of a later milestone).
 * - Absent flags are shown as UNKNOWN, never assumed "no" (SODA
 *   null-omission semantics).
 * - Pending land-use actions have no connector yet and are declared
 *   unknown rather than silently omitted.
 * - No silent defaults; plain language first; status never by color alone.
 *
 * Data flows through the SAME hardened client as the Property screen
 * (exact pair matrix, runtime contract validation, bounded reflection,
 * cancellation/timeout).
 */

const LOT_SUMMARY_FIELDS = ["lotarea", "lotfront", "lotdepth", "lottype", "irrlotcode"] as const;
const BUILDING_SUMMARY_FIELDS = [
  "bldgarea",
  "numfloors",
  "unitsres",
  "unitstotal",
  "yearbuilt",
  "bldgclass",
] as const;
const FLAG_FEATURES = [
  { field: "landmark", label: "Landmark" },
  { field: "histdist", label: "Historic district" },
  { field: "firm07_flag", label: "2007 FIRM flood flag" },
  { field: "pfirm15_flag", label: "2015 preliminary FIRM flood flag" },
] as const;

function FactRow({
  field,
  fact,
  byId,
  profile,
  missingFields,
}: {
  field: string;
  fact: FactValue | undefined;
  byId: Map<string, SourceFact>;
  profile: PropertyProfile;
  missingFields: Set<string>;
}) {
  if (!fact) {
    return (
      <div className="confirm-row">
        <dt>{fieldLabel(field)}</dt>
        <dd className="section-note">
          {missingFields.has(field)
            ? "Not in the official record — listed under missing inputs (unknown, never guessed)."
            : "Not present in this profile (unknown, never guessed)."}
        </dd>
      </div>
    );
  }
  const record = byId.get(fact.provenance_ref) ?? null;
  return (
    <div className="confirm-row">
      <dt>{fieldLabel(field)}</dt>
      <dd>
        <span className="fact-value">{formatValue(fact.value)}</span>
        {fact.units ? <span className="fact-units"> {fact.units}</span> : null}{" "}
        {fact.coverage_status ? <CoverageBadge status={fact.coverage_status} /> : null}
        <ProvenanceDisclosure
          records={record ? [record] : []}
          reproducibility={profile.reproducibility}
          label={`Source for ${fieldLabel(field)}`}
        />
      </dd>
    </div>
  );
}

function FlagRow({
  label,
  view,
  byId,
  profile,
  missing,
}: {
  label: string;
  view: MappedFeatureView | undefined;
  byId: Map<string, SourceFact>;
  profile: PropertyProfile;
  missing: boolean;
}) {
  if (!view || !view.hasValue) {
    return (
      <div className="confirm-row">
        <dt>{label}</dt>
        <dd className="section-note">
          {missing
            ? "Not in the official record — unknown, never assumed absent."
            : "Not present in this profile — unknown, never assumed absent."}
        </dd>
      </div>
    );
  }
  const record = view.provenanceRef !== null ? byId.get(view.provenanceRef) ?? null : null;
  return (
    <div className="confirm-row">
      <dt>{label}</dt>
      <dd>
        <span className="fact-value">{formatValue(view.value)}</span>{" "}
        {view.coverageStatus ? <CoverageBadge status={view.coverageStatus} /> : null}
        <ProvenanceDisclosure
          records={record ? [record] : []}
          reproducibility={profile.reproducibility}
          label={`Source for ${label}`}
        />
      </dd>
    </div>
  );
}

function ConfirmCard({ profile }: { profile: PropertyProfile }) {
  const byId = provenanceById(profile);
  const address = profile.identity.address;
  const missingFields = new Set(profile.missing_inputs.map((entry) => entry.field));
  const featureViews = new Map<string, MappedFeatureView>();
  for (const feature of profile.zoning.mapped_features ?? []) {
    const view = mappedFeatureView(feature);
    if (view.feature !== null) {
      featureViews.set(view.feature, view);
    }
  }
  const criticalMissing = profile.missing_inputs.filter(
    (entry) => entry.criticality === "critical",
  );
  const unresolvedConflicts = profile.conflicts.filter(
    (conflict) => conflict.resolution === "unresolved",
  );
  const completeness = profile.data_completeness
    ? completenessDisplay(profile.data_completeness)
    : null;

  return (
    <div data-testid="confirm-card">
      {/* --- Compact property card ------------------------------------ */}
      <section className="card" data-testid="confirm-identity">
        <h2 className="section-title">BBL {profile.identity.bbl}</h2>
        {address?.normalized_address ? (
          <p style={{ margin: 0 }}>
            {address.normalized_address}
            {address.borough ? `, ${address.borough}` : ""}
            {address.zip_code ? ` ${address.zip_code}` : ""}
          </p>
        ) : (
          <p className="section-note">
            No address could be stated for this lot from the current official
            data (see the data conflicts section).
          </p>
        )}
        <dl className="confirm-grid">
          <div className="confirm-row">
            <dt>BIN</dt>
            <dd className="section-note" data-testid="confirm-bin">
              {profile.identity.bins && profile.identity.bins.length > 0
                ? profile.identity.bins.join(", ")
                : "Not yet retrieved — building identifiers arrive with the DOB/Geoclient connectors. Unknown, never guessed."}
            </dd>
          </div>
          <div className="confirm-row">
            <dt>Geometry</dt>
            <dd className="section-note" data-testid="confirm-geometry">
              {profile.identity.geometry?.type
                ? `Geometry of type ${profile.identity.geometry.type} is recorded for this lot from the official source — only recorded geometry is shown; a parcel outline is never drawn from assumptions.`
                : "No parcel geometry is included in this profile version — tax-lot geometry arrives with the MapPLUTO geometry work. Unknown, never drawn from assumptions."}
            </dd>
          </div>
          {completeness ? (
            <div className="confirm-row">
              <dt>Data completeness</dt>
              <dd>
                {completeness.headline} (<code>{completeness.value}</code>)
              </dd>
            </div>
          ) : null}
        </dl>
      </section>

      <section className="card" data-testid="confirm-lot">
        <h2 className="section-title">Lot summary</h2>
        <p className="section-note">
          Key official lot facts. The complete fact tables (every column,
          nothing hidden) remain on the Property screen — this card is a
          display summary, not a data filter.
        </p>
        <dl className="confirm-grid">
          {LOT_SUMMARY_FIELDS.map((field) => (
            <FactRow
              key={field}
              field={field}
              fact={profile.lot_facts[field]}
              byId={byId}
              profile={profile}
              missingFields={missingFields}
            />
          ))}
        </dl>
      </section>

      <section className="card" data-testid="confirm-building">
        <h2 className="section-title">Existing building</h2>
        <dl className="confirm-grid">
          {BUILDING_SUMMARY_FIELDS.map((field) => (
            <FactRow
              key={field}
              field={field}
              fact={profile.existing_building_facts[field]}
              byId={byId}
              profile={profile}
              missingFields={missingFields}
            />
          ))}
        </dl>
      </section>

      <ZoningSection profile={profile} byId={byId} />

      <section className="card" data-testid="confirm-flags">
        <h2 className="section-title">Landmark, flood, and pending flags</h2>
        <dl className="confirm-grid">
          {FLAG_FEATURES.map(({ field, label }) => (
            <FlagRow
              key={field}
              label={label}
              view={featureViews.get(field)}
              byId={byId}
              profile={profile}
              missing={missingFields.has(field)}
            />
          ))}
          <div className="confirm-row">
            <dt>Pending land-use actions</dt>
            <dd className="section-note" data-testid="confirm-pending-flag">
              Not yet retrievable — the platform has no official connector
              for pending land-use and zoning-map-change data yet. Shown as
              unknown, never assumed none.
            </dd>
          </div>
        </dl>
      </section>

      <ConflictsSection conflicts={profile.conflicts} />
      <CoverageLegend profile={profile} />

      {/* --- Only questions government data cannot answer --------------- */}
      <section className="card" data-testid="confirm-questions">
        <h2 className="section-title">
          Questions the official data cannot answer
        </h2>
        <p className="section-note">
          Everything above came from official records. Only the items below
          need you — nothing the government data already answers is asked
          again.
        </p>
        <ul className="missing-list">
          <li data-testid="question-intent">
            <strong>What do you intend to build or change?</strong>{" "}
            <span className="section-note">
              Development objectives are your choice, not a government
              record. Selecting objectives becomes available with the
              analysis-run workflow.
            </span>
          </li>
          {criticalMissing.map((entry) => (
            <li key={entry.field}>
              <strong>
                Can you provide {fieldLabel(entry.field)}?
              </strong>{" "}
              <span className="section-note">
                The official record is missing this critical input
                {entry.reason ? ` — ${entry.reason}` : ""}. It is shown as
                missing, never guessed.
              </span>
            </li>
          ))}
          {unresolvedConflicts.map((conflict) => (
            <li key={conflict.field}>
              <strong>
                Which value of {fieldLabel(conflict.field)} is correct?
              </strong>{" "}
              <span className="section-note">
                Official sources disagree (see the data conflicts section).
                Your confirmation will be recorded once the analysis-run
                workflow exists; nothing is resolved automatically.
              </span>
            </li>
          ))}
        </ul>
        {criticalMissing.length === 0 && unresolvedConflicts.length === 0 ? (
          <p className="section-note" data-testid="questions-empty-note">
            The official record leaves no critical gap and no unresolved
            conflict for this property — the only open question is your
            development intent.
          </p>
        ) : null}
        <div className="confirm-persistence">
          <button
            type="button"
            className="secondary-button"
            disabled
            data-testid="confirm-disabled-button"
          >
            Confirm facts (not yet available)
          </button>
          <p className="section-note" data-testid="confirm-persistence-note">
            Honest status: confirmations and overrides cannot be saved yet.
            The canonical contract defines <code>user_confirmations</code>,
            but no API endpoint accepts them until the analysis-run work of
            a later milestone. Nothing on this screen is persisted, and no
            fact has been auto-confirmed on your behalf.
          </p>
        </div>
      </section>

      {/* --- One clear next action -------------------------------------- */}
      <section className="card next-action" data-testid="confirm-next-action">
        <h2 className="section-title">Next step</h2>
        <p className="section-note">
          Rule evaluation and scenario comparison (steps 3–4) arrive with
          the rules and scenario milestones; this build does not pretend to
          run them.
        </p>
        <Link className="primary-button next-action-link" href="/property">
          Back to property lookup
        </Link>
      </section>
    </div>
  );
}

export function ConfirmScreen({ bbl }: { bbl: string }) {
  const [loading, setLoading] = useState(true);
  const [outcome, setOutcome] = useState<LookupOutcome | null>(null);
  const [attempt, setAttempt] = useState(0);
  const requestSeq = useRef(0);

  useEffect(() => {
    const controller = new AbortController();
    const seq = ++requestSeq.current;
    setLoading(true);
    void fetchPropertyProfile(bbl, { signal: controller.signal }).then((result) => {
      if (requestSeq.current !== seq || result.kind === "aborted") {
        return;
      }
      setLoading(false);
      setOutcome(result);
    });
    return () => controller.abort();
  }, [bbl, attempt]);

  const retry = useCallback(() => setAttempt((current) => current + 1), []);

  return (
    <div data-testid="confirm-screen">
      <header className="confirm-header">
        <h1 className="section-title" style={{ fontSize: "1.4rem", margin: 0 }}>
          Step 2 — Confirm the property
        </h1>
        <p className="section-note">
          Review the official facts for BBL {bbl} before analysis. This
          screen retrieves the same canonical profile as the Property
          screen, through the same validated contract.
        </p>
      </header>
      {loading ? <LoadingStages bbl={bbl} /> : null}
      {!loading && outcome ? (
        outcome.kind === "profile" ? (
          <ConfirmCard profile={outcome.profile} />
        ) : (
          <>
            <OutcomeFailureStates outcome={outcome} onRetry={retry} />
            <p className="section-note">
              <Link href="/property">Back to property lookup</Link>
            </p>
          </>
        )
      ) : null}
    </div>
  );
}

/**
 * Entry component reading ?bbl= from the URL (client-side). An absent or
 * format-invalid parameter renders an honest error card with the way back
 * — never a silent default lookup.
 */
export function ConfirmEntry() {
  const params = useSearchParams();
  const raw = params.get("bbl") ?? "";
  const validation = validateBblInput(raw);
  return (
    <div className="property-shell">
      <InternalBanner />
      {validation.ok ? (
        <ConfirmScreen bbl={validation.canonical} />
      ) : (
        <section className="card failure-state" data-testid="confirm-bad-param">
          <h2 className="failure-title">No property selected</h2>
          <p>
            This confirmation screen needs a valid 10-digit BBL in its web
            address (for example <code>/property/confirm?bbl=1000010010</code>).
            {raw === "" ? " None was provided." : ` The provided value is not a valid BBL: ${validation.message}`}
          </p>
          <p>
            <Link className="primary-button next-action-link" href="/property">
              Go to property lookup
            </Link>
          </p>
        </section>
      )}
    </div>
  );
}
