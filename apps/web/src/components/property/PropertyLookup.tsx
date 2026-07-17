"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState, type FormEvent } from "react";
import { announcementForOutcome } from "@/lib/announce";
import { fetchPropertyProfile, type LookupOutcome } from "@/lib/api";
import { validateBblInput } from "@/lib/bbl";
import { completenessDisplay } from "@/lib/coverage";
import { urlHost } from "@/lib/format";
import { provenanceById } from "@/lib/provenance";
import type { PropertyProfile } from "@/lib/contract";
import { ConflictsSection } from "./ConflictsSection";
import { CoverageLegend } from "./CoverageLegend";
import { OutcomeFailureStates } from "./FailureState";
import { FactsTable } from "./FactsTable";
import { LoadingStages } from "./LoadingStages";
import { MissingInputsSection } from "./MissingInputsSection";
import { OutcomeAnnouncer } from "./OutcomeAnnouncer";
import { ProfessionalReviewPanel } from "./ProfessionalReviewPanel";
import { UnsupportedSection } from "./UnsupportedSection";
import { ZoningSection } from "./ZoningSection";

/**
 * Property screen state machine (tasks M2-T001/M2-T002). Purely
 * presentational workflow: idle -> loading -> one outcome. Client-side BBL
 * validation mirrors (never replaces) the server rule and runs BEFORE any
 * network call. All legal/data semantics come from the API — the frontend
 * never calculates, resolves, or fills in anything
 * (docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md).
 *
 * M2-T002 hardening:
 * - D5: a client-invalid submit AFTER a successful lookup keeps the
 *   previous result rendered with an inline error (the last good result is
 *   held separately from the form-error state), and the inline error
 *   clears as soon as the user edits the input.
 * - Cancellation: each lookup aborts the previous in-flight request
 *   (AbortController); a superseded request resolves to the `aborted`
 *   outcome and never touches the screen (plus a monotonic sequence guard).
 * - Timeout: the client request budget produces the recoverable
 *   client_timeout state (scenario S4).
 *
 * M2-T005 (visual-quality Major D1):
 * - Announcement: outcome arrivals (success and every failure state) are
 *   announced exactly once through the persistent OutcomeAnnouncer live
 *   region; the message clears while a lookup is in flight so a repeated
 *   identical outcome is re-announced.
 * - Focus: after an outcome arrives, focus moves deterministically to the
 *   outcome heading (`[data-outcome-heading]`); after a retry, focus moves
 *   to the loading card instead of dropping to `body` when the Retry
 *   button unmounts. A client-invalid submit changes no result and moves
 *   no focus (D5 behavior preserved).
 */

interface LookupResult {
  bbl: string;
  outcome: LookupOutcome;
}

function IdentityCard({ profile }: { profile: PropertyProfile }) {
  const address = profile.identity.address;
  return (
    <section className="card" data-testid="identity-card">
      {/* Success-outcome focus target (M2-T005 D1). */}
      <h2 className="section-title" tabIndex={-1} data-outcome-heading>
        BBL {profile.identity.bbl}
      </h2>
      {address?.normalized_address ? (
        <p style={{ margin: 0 }}>
          {address.normalized_address}
          {address.borough ? `, ${address.borough}` : ""}
          {address.zip_code ? ` ${address.zip_code}` : ""}
        </p>
      ) : (
        <p className="section-note">
          No address could be stated for this lot from the current official
          data (this can happen when identity fields conflict — see the data
          conflicts section).
        </p>
      )}
      {profile.reproducibility ? (
        <p className="failure-meta">
          Official source: {profile.reproducibility.source_id} · dataset{" "}
          {profile.reproducibility.dataset_id}
          {profile.reproducibility.dataset_version
            ? ` (release ${profile.reproducibility.dataset_version})`
            : " (release not published at retrieval time)"}{" "}
          · retrieved {profile.reproducibility.retrieved_at} from{" "}
          {urlHost(profile.reproducibility.request_url)} · profile reference{" "}
          <code>{profile.reproducibility.correlation_id}</code>
        </p>
      ) : null}
    </section>
  );
}

function CompletenessBanner({ profile }: { profile: PropertyProfile }) {
  if (!profile.data_completeness) return null;
  const display = completenessDisplay(profile.data_completeness);
  return (
    <div
      className="completeness-banner"
      role="status"
      data-testid="completeness-banner"
    >
      <p className="completeness-headline">
        {display.headline} (<code>{display.value}</code>)
      </p>
      <p>{display.gloss}</p>
    </div>
  );
}

function ProfileView({ profile }: { profile: PropertyProfile }) {
  const byId = provenanceById(profile);
  return (
    <div data-testid="profile-view">
      <IdentityCard profile={profile} />
      <CompletenessBanner profile={profile} />
      <CoverageLegend profile={profile} />
      <ConflictsSection conflicts={profile.conflicts} />
      <ZoningSection profile={profile} byId={byId} />
      <FactsTable
        title="Lot facts"
        note="Official lot-level facts with units, coverage status, and source."
        facts={profile.lot_facts}
        byId={byId}
        reproducibility={profile.reproducibility}
      />
      <FactsTable
        title="Existing building facts"
        note="Official facts about what stands on the lot today."
        facts={profile.existing_building_facts}
        byId={byId}
        reproducibility={profile.reproducibility}
      />
      <MissingInputsSection entries={profile.missing_inputs} />
      <UnsupportedSection profile={profile} />
      <ProfessionalReviewPanel profile={profile} />
      <section className="card next-action" data-testid="next-action">
        <h2 className="section-title">Next step</h2>
        <p className="section-note">
          Step 2 reviews this property as a compact card and lists only the
          questions the official data cannot answer.
        </p>
        <Link
          className="primary-button next-action-link"
          href={`/property/confirm?bbl=${encodeURIComponent(profile.identity.bbl)}`}
          data-testid="confirm-link"
        >
          Review and confirm this property
        </Link>
      </section>
    </div>
  );
}

export function PropertyLookup() {
  const [bblInput, setBblInput] = useState("");
  const [formError, setFormError] = useState<string | null>(null);
  /** BBL currently being fetched, or null when no request is in flight. */
  const [loadingBbl, setLoadingBbl] = useState<string | null>(null);
  /** Last completed lookup — SURVIVES a later client-invalid submit (D5). */
  const [result, setResult] = useState<LookupResult | null>(null);
  /** True only between a Retry activation and its outcome (D1 focus). */
  const [retryFocus, setRetryFocus] = useState(false);
  // Monotonic id + abort controller: a stale response can never overwrite
  // a newer lookup, and superseded requests are actively cancelled.
  const requestSeq = useRef(0);
  const abortRef = useRef<AbortController | null>(null);
  /** Wraps the rendered outcome; arrival focus queries inside it (D1). */
  const outcomeRef = useRef<HTMLDivElement | null>(null);

  // Cancel any in-flight request on unmount.
  useEffect(() => () => abortRef.current?.abort(), []);

  // D1 (M2-T005): after an outcome arrives, move focus to the outcome
  // heading. `result` changes ONLY on arrival (a client-invalid submit
  // never calls setResult), so this can never steal focus mid-form-edit.
  useEffect(() => {
    if (result) {
      outcomeRef.current
        ?.querySelector<HTMLElement>("[data-outcome-heading]")
        ?.focus();
    }
  }, [result]);

  const runLookup = useCallback(async (canonical: string) => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    const seq = ++requestSeq.current;
    setLoadingBbl(canonical);
    const outcome = await fetchPropertyProfile(canonical, {
      signal: controller.signal,
    });
    if (requestSeq.current !== seq || outcome.kind === "aborted") {
      // Superseded: the newer lookup owns the screen.
      return;
    }
    setLoadingBbl(null);
    setRetryFocus(false);
    setResult({ bbl: canonical, outcome });
  }, []);

  const onSubmit = useCallback(
    (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      const validation = validateBblInput(bblInput);
      if (!validation.ok) {
        // Client-side mirror of the server rule: no network call is made,
        // and the PREVIOUS result stays rendered below the inline error.
        setFormError(validation.message);
        return;
      }
      setFormError(null);
      void runLookup(validation.canonical);
    },
    [bblInput, runLookup],
  );

  const retry = useCallback(() => {
    if (result) {
      // D1: the Retry button is about to unmount with the failure card;
      // the loading card takes focus so it never drops to <body>.
      setRetryFocus(true);
      void runLookup(result.bbl);
    }
  }, [result, runLookup]);

  // D1: the single outcome announcement — cleared while loading so that a
  // repeated identical outcome (e.g. retry fails the same way) announces.
  const announcement =
    loadingBbl !== null ? "" : result ? announcementForOutcome(result.outcome) : "";

  return (
    <div>
      <OutcomeAnnouncer message={announcement} />
      <section className="card">
        <h1 className="section-title" style={{ fontSize: "1.4rem" }}>
          Property lookup
        </h1>
        <p className="section-note">
          Enter a 10-digit BBL (borough–block–lot) to retrieve the official
          property profile.
        </p>
        <form className="bbl-form" onSubmit={onSubmit} noValidate>
          <div className="field-group">
            <label className="field-label" htmlFor="bbl-input">
              BBL
            </label>
            <input
              id="bbl-input"
              name="bbl"
              className="text-input"
              inputMode="numeric"
              autoComplete="off"
              placeholder="e.g. 1000010010"
              value={bblInput}
              onChange={(event) => {
                setBblInput(event.target.value);
                // D5: the inline error clears as soon as the user edits.
                setFormError(null);
              }}
              aria-describedby="bbl-hint bbl-error"
            />
            <span className="field-hint" id="bbl-hint">
              Borough digit (1–5), 5-digit block, 4-digit lot.
            </span>
          </div>
          <button type="submit" className="primary-button">
            Look up property
          </button>
        </form>
        <div id="bbl-error" aria-live="polite">
          {formError ? (
            <p className="inline-error" data-testid="client-validation-error">
              {formError}
            </p>
          ) : null}
        </div>
        <div className="field-group" style={{ marginTop: "1rem" }}>
          <label className="field-label" htmlFor="address-input">
            Address (not yet available)
          </label>
          <input
            id="address-input"
            className="text-input"
            disabled
            placeholder="Address search is not available yet"
            aria-describedby="address-hint"
          />
          <span className="field-hint" id="address-hint" data-testid="address-disabled-copy">
            Address search requires the NYC Geoclient connector, whose
            credentials are still pending. Until then, lookups work by BBL
            only — this screen will not pretend to resolve addresses.
          </span>
        </div>
      </section>

      {loadingBbl !== null ? (
        <LoadingStages bbl={loadingBbl} focusOnMount={retryFocus} />
      ) : null}

      <div ref={outcomeRef}>
        {loadingBbl === null && result ? (
          result.outcome.kind === "profile" ? (
            <ProfileView profile={result.outcome.profile} />
          ) : (
            <OutcomeFailureStates outcome={result.outcome} onRetry={retry} />
          )
        ) : null}
      </div>
    </div>
  );
}
