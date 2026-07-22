"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { OutcomeAnnouncer } from "@/components/property/OutcomeAnnouncer";
import {
  announcementForRuleEvaluation,
  fetchRuleEvaluation,
  type RuleEvaluationOutcome,
} from "@/lib/rule-evaluation";
import { RuleEvaluationFailure } from "./RuleEvaluationFailure";
import { RuleEvaluationResult } from "./RuleEvaluationResult";

/**
 * Draft rule-evaluation surface orchestrator (task M4-T005 phase 3).
 *
 * OPTIONAL ENRICHMENT: this panel loads INDEPENDENTLY of the property profile.
 * It is only ever mounted when the Server Component decided the surface is
 * enabled (the frontend feature flag is on and not killed for the request), so
 * when the flag is OFF this component never renders and never issues the
 * fetch — the defense-in-depth no-call guarantee. If the evaluation fails, the
 * already-rendered property profile stays fully usable; this panel never blocks
 * or unmounts it.
 *
 * State machine mirrors PropertyLookup: idle -> loading -> one outcome, with a
 * monotonic sequence guard + AbortController supersession so a stale response
 * can never overwrite a newer one, and a superseded request resolves to
 * `aborted` and is dropped before render.
 *
 * FOCUS DISCIPLINE (deliberately different from PropertyLookup): on the initial
 * BACKGROUND load the panel does NOT move document focus — it announces
 * politely through its own live region and leaves the property-profile focus
 * flow untouched. Focus is moved to this panel's heading ONLY after a
 * user-initiated Retry (so a keyboard user who clicked Retry is carried to the
 * fresh result, while a background arrival never hijacks focus).
 */

function RuleEvalLoading({ focusOnMount }: { focusOnMount: boolean }) {
  const ref = useRef<HTMLElement | null>(null);
  useEffect(() => {
    if (focusOnMount) ref.current?.focus();
  }, [focusOnMount]);
  return (
    <section
      ref={ref}
      tabIndex={-1}
      className="card"
      aria-live="polite"
      data-testid="rule-eval-loading"
    >
      <h3 className="section-title">Evaluating draft rules for this property…</h3>
      <ol className="loading-stages">
        <li className="stage-done">
          <span aria-hidden="true">✓</span> Official property facts retrieved
        </li>
        <li className="stage-active">
          <span aria-hidden="true">…</span> Running the deterministic draft rule
          evaluator over the official facts
        </li>
        <li className="stage-pending">Rendering the draft result</li>
      </ol>
    </section>
  );
}

export function RuleEvaluationPanel({
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
  const [outcome, setOutcome] = useState<RuleEvaluationOutcome | null>(null);
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
    const result = await fetchRuleEvaluation(bbl, {
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
      surfaceRef.current
        ?.querySelector<HTMLElement>("[data-rule-eval-heading]")
        ?.focus();
    }
  }, [outcome]);

  const retry = useCallback(() => {
    pendingFocus.current = true;
    setRetryFocus(true);
    void run();
  }, [run]);

  // Cleared while loading so a repeated identical outcome re-announces.
  const announcement = loading
    ? ""
    : outcome
      ? announcementForRuleEvaluation(outcome)
      : "";

  return (
    <div data-testid="rule-eval-panel" ref={surfaceRef}>
      <OutcomeAnnouncer testId="rule-eval-announcer" message={announcement} />
      <section className="card" data-testid="rule-eval-intro">
        <h2 className="section-title">Draft rule evaluation (internal)</h2>
        <p className="section-note">
          An experimental, unreviewed draft rule result for this property. It is
          never a final determination, and it does not change the official facts
          above. This section loads on its own — if it fails, the property profile
          stays fully usable.
        </p>
      </section>
      {loading ? (
        <RuleEvalLoading focusOnMount={retryFocus} />
      ) : outcome ? (
        outcome.kind === "evaluation" ? (
          <RuleEvaluationResult document={outcome.document} />
        ) : (
          <RuleEvaluationFailure outcome={outcome} onRetry={retry} />
        )
      ) : null}
    </div>
  );
}
