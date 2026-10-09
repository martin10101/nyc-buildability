"use client";

import { FailureNoticeCard } from "./DashboardFailureNotice";
import {
  enrichmentFailureNotice,
  type EnrichmentFailureOutcome,
  type EnrichmentSurface,
} from "./dashboard-enrichment-failure";

/**
 * One plain §5a notice for a failed OPTIONAL analysis enrichment — the scenario comparison or the
 * draft rule evaluation — on the single-page dashboard (queue D-03, M1-17). It replaces the old
 * `<details>` wrapper: the failure now reads as plain English in the analysis region, with every
 * internal code behind a closed "Technical details". `surface` supplies the plain subject nouns
 * and the testid prefix. The heading is an `h2` (the property heading above owns the `h1`) and is
 * not a focus target, so this secondary notice never competes with the property's focus flow. A
 * superseded (`aborted`) outcome renders nothing.
 */
export function DashboardEnrichmentNotice({
  outcome,
  surface,
  onRetry,
}: {
  outcome: EnrichmentFailureOutcome;
  surface: EnrichmentSurface;
  onRetry: () => void;
}) {
  const notice = enrichmentFailureNotice(outcome, surface);
  if (!notice) return null;
  return (
    <FailureNoticeCard model={notice} onRetry={onRetry} heading="h2" testId={surface.testId} />
  );
}
