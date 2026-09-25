"use client";
import Link from "next/link";
import type { PropertyProfile } from "@/lib/contract";
import { fieldLabel } from "@/lib/format";
import { propertyHref } from "@/lib/architect/navigation";

/**
 * M5-T119 (D-086 P3a, spec §5.3 / ledger A04): the ONE overview exception strip.
 *
 * Folds today's separate conflict + critical-missing + stale alerts (the three
 * blocks PropertyIssuesSummary renders — kept byte-identical for the printed
 * brief and the scenarios view) into ONE `role="status"` region that lists only
 * the ACTIVE profile-derived issues. Each active issue names its critical
 * field(s), states the effect it blocks, and keeps its original link and
 * wording meaning. It renders NOTHING when no issue is active (no empty strip),
 * so a clean profile is unchanged.
 *
 * Deliberately NOT folded here (see the M5-T119 producer report for the full
 * placement rationale):
 *   - Identity mismatch (ledger A15) stays in AnalysisIdentityNotice, which is
 *     `role="alert"`. The task KEY RULE keeps identity withhold at role=alert;
 *     folding it into this role=status strip would DOWNGRADE it.
 *   - Incomplete assessment (ledger A05) stays in IncompleteEvaluationNotice
 *     (`role="status"`), rendered with the raw returned document.
 * Both are rendered by ArchitectEntry directly ABOVE this strip, and
 * LoadedWorkspace nulls a mismatched or non-inspectable evaluation before
 * PropertyOverview ever sees it, so this component structurally cannot (and must
 * not) re-surface them. Together the dedicated regions plus this strip cover the
 * §5.3 "active issues" set without a second live region for one event
 * (LS-P16 / A04: one strip = one status region).
 */
export function OverviewExceptionStrip({ profile }: { profile: PropertyProfile }) {
  const bbl = profile.identity.bbl;
  const conflicts = profile.conflicts.filter(item => item.resolution === "unresolved");
  const critical = profile.missing_inputs.filter(item => item.criticality === "critical");
  const stale = !!profile.reproducibility?.staleness?.stale;
  // No active issue → no strip at all (never an empty "no issues" card).
  if (conflicts.length === 0 && critical.length === 0 && !stale) return null;
  const issuesHref = propertyHref(bbl, "issues");
  return (
    <div
      className="architect-exception-strip"
      role="status"
      aria-label="Active issues"
      data-testid="overview-exception-strip"
    >
      <p className="architect-exception-title">Active issues</p>
      {conflicts.length > 0 ? (
        <div className="architect-exception-row" data-testid="exception-issue-conflict">
          <strong>Unresolved data conflicts</strong>
          <p>
            <span className="architect-exception-fields">
              {conflicts.map(item => fieldLabel(item.field)).join(" · ")}
            </span>{" "}
            — official sources disagree on these; a reliable value is withheld until the conflict is
            reviewed.
          </p>
          <Link href={issuesHref}>Review conflicting source values →</Link>
        </div>
      ) : null}
      {critical.length > 0 ? (
        <div className="architect-exception-row" data-testid="exception-issue-missing">
          <strong>Critical inputs missing</strong>
          <p>
            <span className="architect-exception-fields">
              {critical.map(item => fieldLabel(item.field)).join(" · ")}
            </span>{" "}
            — a draft limit that depends on these cannot be relied on until they are supplied.
          </p>
          <Link href={issuesHref}>Review missing inputs →</Link>
        </div>
      ) : null}
      {stale ? (
        <div className="architect-exception-row" data-testid="exception-issue-stale">
          <strong>Stale source</strong>
          <p>
            The property source is stale. Captured dates and retrieval status are available in
            Evidence. Review the retrieval dates before relying on these figures.
          </p>
        </div>
      ) : null}
    </div>
  );
}
