"use client";

import { useCallback, useRef, useState, type FormEvent } from "react";
import { fetchPropertyProfile, type LookupOutcome } from "@/lib/api";
import { validateBblInput } from "@/lib/bbl";
import { completenessDisplay } from "@/lib/coverage";
import { urlHost } from "@/lib/format";
import { provenanceById } from "@/lib/provenance";
import type { PropertyProfile } from "@/lib/property-profile";
import { ConflictsSection } from "./ConflictsSection";
import {
  InternalErrorState,
  NetworkErrorState,
  NoMatchState,
  UnexpectedResponseState,
  UpstreamFailureState,
  ValidationErrorState,
} from "./FailureState";
import { FactsTable } from "./FactsTable";
import { LoadingStages } from "./LoadingStages";
import { MissingInputsSection } from "./MissingInputsSection";
import { ProfessionalReviewPanel } from "./ProfessionalReviewPanel";
import { UnsupportedSection } from "./UnsupportedSection";
import { ZoningSection } from "./ZoningSection";

/**
 * Property screen state machine (task M2-T001). Purely presentational
 * workflow: idle -> loading -> one outcome. Client-side BBL validation
 * mirrors (never replaces) the server rule and runs BEFORE any network
 * call. All legal/data semantics come from the API — the frontend never
 * calculates, resolves, or fills in anything
 * (docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md).
 */

type ScreenState =
  | { phase: "idle" }
  | { phase: "client_invalid"; message: string }
  | { phase: "loading"; bbl: string }
  | { phase: "done"; bbl: string; outcome: LookupOutcome };

function IdentityCard({ profile }: { profile: PropertyProfile }) {
  const address = profile.identity.address;
  return (
    <section className="card" data-testid="identity-card">
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
    </div>
  );
}

export function PropertyLookup() {
  const [bblInput, setBblInput] = useState("");
  const [screen, setScreen] = useState<ScreenState>({ phase: "idle" });
  // Monotonic id so a stale response can never overwrite a newer lookup.
  const requestSeq = useRef(0);

  const runLookup = useCallback(async (canonical: string) => {
    const seq = ++requestSeq.current;
    setScreen({ phase: "loading", bbl: canonical });
    const outcome = await fetchPropertyProfile(canonical);
    if (requestSeq.current === seq) {
      setScreen({ phase: "done", bbl: canonical, outcome });
    }
  }, []);

  const onSubmit = useCallback(
    (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      const validation = validateBblInput(bblInput);
      if (!validation.ok) {
        // Client-side mirror of the server rule: no network call is made.
        setScreen({ phase: "client_invalid", message: validation.message });
        return;
      }
      void runLookup(validation.canonical);
    },
    [bblInput, runLookup],
  );

  const retry = useCallback(() => {
    if (screen.phase === "done") {
      void runLookup(screen.bbl);
    }
  }, [screen, runLookup]);

  return (
    <div>
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
              onChange={(event) => setBblInput(event.target.value)}
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
          {screen.phase === "client_invalid" ? (
            <p className="inline-error" data-testid="client-validation-error">
              {screen.message}
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

      {screen.phase === "loading" ? <LoadingStages bbl={screen.bbl} /> : null}

      {screen.phase === "done" ? (
        screen.outcome.kind === "profile" ? (
          <ProfileView profile={screen.outcome.profile} />
        ) : screen.outcome.kind === "no_match" ? (
          <NoMatchState outcome={screen.outcome} />
        ) : screen.outcome.kind === "validation_error" ? (
          <ValidationErrorState outcome={screen.outcome} />
        ) : screen.outcome.kind === "upstream_failure" ? (
          <UpstreamFailureState outcome={screen.outcome} onRetry={retry} />
        ) : screen.outcome.kind === "internal_error" ? (
          <InternalErrorState outcome={screen.outcome} onRetry={retry} />
        ) : screen.outcome.kind === "network_error" ? (
          <NetworkErrorState outcome={screen.outcome} onRetry={retry} />
        ) : (
          <UnexpectedResponseState outcome={screen.outcome} onRetry={retry} />
        )
      ) : null}
    </div>
  );
}
