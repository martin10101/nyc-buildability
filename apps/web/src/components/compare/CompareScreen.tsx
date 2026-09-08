"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { validateBblInput } from "@/lib/bbl";
import {
  announcementForScenario,
  fetchScenario,
  type ScenarioOutcome,
} from "@/lib/scenario-api";
import { InternalBanner } from "@/components/property/InternalBanner";
import { OutcomeAnnouncer } from "@/components/property/OutcomeAnnouncer";
import { ScenarioResult } from "./ScenarioResult";
import { ScenarioFailureStates } from "./ScenarioFailureStates";

/**
 * Compare screen — PRODUCT_FLOW step 3 (task M5-T004).
 *
 * Consumes the accepted internal scenario endpoint
 * (GET /api/v1/properties/{bbl}/scenario, scenario@1.0.0) through the NEW
 * hardened typed client (src/lib/scenario-api.ts): exact (status, state) pair
 * matrix, runtime contract validation of every 200 body BEFORE render, bounded
 * reflected text + allowlisted correlation id, AbortController + timeout. It
 * never computes a legal value — it transports, validates, classifies, and
 * displays the server-computed scenario.
 *
 * The interaction model mirrors ConfirmScreen exactly: one persistent
 * OutcomeAnnouncer (aria-live) emits the single arrival announcement; focus
 * moves deterministically to the outcome heading on every transition; a
 * superseded request (`aborted`) is dropped; Retry re-requests recoverable
 * faults only.
 *
 * `fetchImpl` is injectable so the whole screen runs OFFLINE under vitest with
 * committed M5-T003 fixtures — no network, no Supabase, no Geoclient (AS-7).
 */
export function CompareScreen({
  bbl,
  fetchImpl,
}: {
  bbl: string;
  fetchImpl?: typeof fetch;
}) {
  const [loading, setLoading] = useState(true);
  const [outcome, setOutcome] = useState<ScenarioOutcome | null>(null);
  const [attempt, setAttempt] = useState(0);
  /** True only between a Retry activation and its outcome (focus management). */
  const [retryFocus, setRetryFocus] = useState(false);
  const requestSeq = useRef(0);
  /** Wraps the rendered outcome; arrival focus queries inside it. */
  const outcomeRef = useRef<HTMLDivElement | null>(null);
  const loadingRef = useRef<HTMLHeadingElement | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    const seq = ++requestSeq.current;
    setLoading(true);
    void fetchScenario(bbl, { signal: controller.signal, fetchImpl }).then(
      (result) => {
        if (requestSeq.current !== seq || result.kind === "aborted") {
          return;
        }
        setLoading(false);
        setRetryFocus(false);
        setOutcome(result);
      },
    );
    return () => controller.abort();
  }, [bbl, attempt, fetchImpl]);

  // When an outcome arrives (success or failure), focus moves deterministically
  // to the outcome heading so keyboard/screen-reader users land on the result.
  useEffect(() => {
    if (!loading && outcome) {
      outcomeRef.current
        ?.querySelector<HTMLElement>("[data-outcome-heading]")
        ?.focus();
    }
  }, [loading, outcome]);

  // On a Retry, focus the loading heading so it never drops to <body> when the
  // failure card (and its Retry button) unmounts.
  useEffect(() => {
    if (loading && retryFocus) {
      loadingRef.current?.focus();
    }
  }, [loading, retryFocus]);

  const retry = useCallback(() => {
    setRetryFocus(true);
    setAttempt((current) => current + 1);
  }, []);

  const announcement = !loading && outcome ? announcementForScenario(outcome) : "";

  return (
    <div data-testid="compare-screen">
      <OutcomeAnnouncer message={announcement} testId="compare-announcer" />
      <header className="confirm-header">
        <h1 className="section-title" style={{ fontSize: "1.4rem", margin: 0 }}>
          Step 3 — Compare
        </h1>
        <p className="section-note">
          Preliminary, unreviewed scenario for BBL {bbl}, built by deterministic
          code from the official record. Draft engineering only — never a
          Verified determination.
        </p>
      </header>
      {loading ? (
        <section className="card" data-testid="compare-loading">
          <h2
            className="section-title"
            tabIndex={-1}
            ref={loadingRef}
            data-testid="compare-loading-title"
          >
            Building the preliminary scenario for BBL {bbl}…
          </h2>
          <p className="section-note">
            Retrieving and validating the scenario document. Nothing is shown
            until it passes the published data contract.
          </p>
        </section>
      ) : null}
      <div ref={outcomeRef}>
        {!loading && outcome ? (
          outcome.kind === "scenario" ? (
            <ScenarioResult document={outcome.document} bbl={bbl} />
          ) : outcome.kind === "aborted" ? null : (
            <>
              <ScenarioFailureStates outcome={outcome} onRetry={retry} />
              <p className="section-note">
                <Link href={`/property/confirm?bbl=${encodeURIComponent(bbl)}`}>
                  Back to the confirmed property
                </Link>{" "}
                <Link href="/property">Back to property lookup</Link>
              </p>
            </>
          )
        ) : null}
      </div>
    </div>
  );
}

/**
 * Entry component reading ?bbl= from the URL (client-side). An absent or
 * format-invalid parameter renders an honest error card with the way back —
 * never a silent default lookup. Mirrors ConfirmEntry.
 */
export function CompareEntry() {
  const params = useSearchParams();
  const raw = params.get("bbl") ?? "";
  const validation = validateBblInput(raw);
  return (
    <div className="property-shell">
      <InternalBanner />
      {validation.ok ? (
        <CompareScreen bbl={validation.canonical} />
      ) : (
        <section className="card failure-state" data-testid="compare-bad-param">
          <h1 className="failure-title">No property selected</h1>
          <p>
            This compare screen needs a valid 10-digit BBL in its web address
            (for example <code>/property/compare?bbl=1000010010</code>).
            {raw === ""
              ? " None was provided."
              : ` The provided value is not a valid BBL: ${validation.message}`}
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
