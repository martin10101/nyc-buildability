"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { OutcomeAnnouncer } from "@/components/property/OutcomeAnnouncer";
import { announcementForScenario, fetchScenario, type ScenarioOutcome } from "@/lib/scenario";
import { ScenarioFailure } from "./ScenarioFailure";
import { ScenarioResult } from "./ScenarioResult";

/**
 * Draft scenario surface orchestrator (task M5-T002), mirroring
 * components/rule-evaluation/RuleEvaluationPanel.tsx guarantee-for-guarantee.
 *
 * OPTIONAL ENRICHMENT: this panel loads INDEPENDENTLY of the property profile.
 * It is only ever mounted when the Server Component decided the surface is
 * enabled (the frontend feature flag is on and opted in for the request), so
 * when the flag is OFF this component never renders and never issues the fetch —
 * the defense-in-depth no-call guarantee. If the scenario fails, the
 * already-rendered property profile stays fully usable; this panel never blocks
 * or unmounts it.
 *
 * State machine mirrors PropertyLookup: idle -> loading -> one outcome, with a
 * monotonic sequence guard + AbortController supersession so a stale response
 * can never overwrite a newer one, and a superseded request resolves to
 * `aborted` and is dropped before render.
 *
 * FOCUS DISCIPLINE (deliberately different from PropertyLookup): on the initial
 * BACKGROUND load the panel does NOT move document focus — it announces politely
 * through its own live region and leaves the property-profile focus flow
 * untouched. Focus is moved to this panel's heading ONLY after a user-initiated
 * Retry.
 */

function ScenarioLoading({ focusOnMount }: { focusOnMount: boolean }) {
  const ref = useRef<HTMLElement | null>(null);
  useEffect(() => {
    if (focusOnMount) ref.current?.focus();
  }, [focusOnMount]);
  return (
    <section ref={ref} tabIndex={-1} className="card" aria-live="polite" data-testid="scenario-loading">
      <h3 className="section-title">Assembling a draft scenario for this property…</h3>
      <ol className="loading-stages">
        <li className="stage-done">
          <span aria-hidden="true">✓</span> Official property facts retrieved
        </li>
        <li className="stage-done">
          <span aria-hidden="true">✓</span> Draft rules evaluated over the official facts
        </li>
        <li className="stage-active">
          <span aria-hidden="true">…</span> Assembling the coverage-aware draft scenario
        </li>
      </ol>
    </section>
  );
}

export function ScenarioPanel({
  bbl,
  fetchImpl,
  timeoutMs,
}: {
  bbl: string;
  /** Injection point for tests; defaults to the global fetch (via the client). */
  fetchImpl?: typeof fetch;
  timeoutMs?: number;
}) {
  const [loading, setLoading] = useState(true);
  const [outcome, setOutcome] = useState<ScenarioOutcome | null>(null);
  /** True only between a Retry activation and its outcome (focus management). */
  const [retryFocus, setRetryFocus] = useState(false);
  const requestSeq = useRef(0);
  const abortRef = useRef<AbortController | null>(null);
  const surfaceRef = useRef<HTMLDivElement | null>(null);
  /** Set on a user Retry; consumed on the next arrival to move focus. */
  const pendingFocus = useRef(false);

  const run = useCallback(async () => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    const seq = ++requestSeq.current;
    setLoading(true);
    const result = await fetchScenario(bbl, {
      fetchImpl,
      timeoutMs,
      signal: controller.signal,
    });
    if (requestSeq.current !== seq || result.kind === "aborted") {
      // Superseded (bbl changed / unmount): the newer request owns the surface.
      return;
    }
    setLoading(false);
    setRetryFocus(false);
    setOutcome(result);
  }, [bbl, fetchImpl, timeoutMs]);

  // Load on mount and whenever the BBL changes; abort any in-flight request on
  // unmount or supersession.
  useEffect(() => {
    void run();
    return () => abortRef.current?.abort();
  }, [run]);

  // Move focus to this panel's heading ONLY after a user-initiated retry.
  useEffect(() => {
    if (outcome && pendingFocus.current) {
      pendingFocus.current = false;
      surfaceRef.current?.querySelector<HTMLElement>("[data-scenario-heading]")?.focus();
    }
  }, [outcome]);

  const retry = useCallback(() => {
    pendingFocus.current = true;
    setRetryFocus(true);
    void run();
  }, [run]);

  // Cleared while loading so a repeated identical outcome re-announces.
  const announcement = loading ? "" : outcome ? announcementForScenario(outcome) : "";

  return (
    <div data-testid="scenario-panel" ref={surfaceRef}>
      <OutcomeAnnouncer testId="scenario-announcer" message={announcement} />
      <section className="card" data-testid="scenario-intro">
        <h2 className="section-title">Draft scenario (internal)</h2>
        <p className="section-note">
          An experimental, unreviewed draft scenario for this property. It surfaces a draft
          zoning-floor-area cap where a draft rule applies, is never a final determination or a
          buildable envelope, and does not change the official facts above. This section loads on its
          own — if it fails, the property profile stays fully usable.
        </p>
      </section>
      {loading ? (
        <ScenarioLoading focusOnMount={retryFocus} />
      ) : outcome ? (
        outcome.kind === "scenario" ? (
          <ScenarioResult document={outcome.document} />
        ) : (
          <ScenarioFailure outcome={outcome} onRetry={retry} />
        )
      ) : null}
    </div>
  );
}
