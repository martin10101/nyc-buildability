"use client";

import { StatusBadge } from "./StatusBadge";
import { checkSummaryDisplay } from "@/lib/surveyReview/labels";
import type { FactView } from "@/lib/surveyReview/types";

/**
 * Deterministic-check summary (task M2-T016 rework; workflow §7.4, §10.2, SC-S6).
 *
 * The backend `FactView` surfaces the check outcome as COUNTS
 * (`check_pass`/`check_fail`/`check_unresolved`) plus a plain-language
 * `downstream_impact.reason`. A failing check is a CONFLICT: shown plainly, with
 * the backend's plain-language explanation, and UNRESOLVABLE-BY-CLICK — there is
 * deliberately NO acknowledge / dismiss / ignore control. The only resolutions
 * are Correct (with reason) or Reject (with reason).
 *
 * AWAITING-BACKEND: the read model does not expose per-check `expected`/
 * `observed` values, so those numeric details are not shown here (never
 * fabricated). Recommended follow-up: surface failing-check details on FactView.
 */
export function ChecksPanel({ fact }: { fact: FactView }) {
  const total = fact.check_pass + fact.check_fail + fact.check_unresolved;
  const isConflict = fact.check_fail > 0;
  const isUnresolved = fact.check_unresolved > 0;

  if (total === 0) {
    return (
      <p className="section-note" data-testid="checks-empty">
        No deterministic check has run against this fact yet.
      </p>
    );
  }

  return (
    <div className="sr-checks" data-testid="checks-panel">
      <ul className="sr-check-counts">
        {fact.check_fail > 0 ? (
          <li className="sr-check-item sr-tone-conflict" data-testid="check-conflict">
            <span className="sr-check-name">
              {fact.check_fail} deterministic check{fact.check_fail === 1 ? "" : "s"} in conflict
            </span>
            <StatusBadge display={checkSummaryDisplay("conflict")} />
          </li>
        ) : null}
        {fact.check_unresolved > 0 ? (
          <li className="sr-check-item sr-tone-caution" data-testid="check-unresolved">
            <span className="sr-check-name">
              {fact.check_unresolved} check{fact.check_unresolved === 1 ? "" : "s"} unresolved
            </span>
            <StatusBadge display={checkSummaryDisplay("unresolved")} />
          </li>
        ) : null}
        {fact.check_pass > 0 ? (
          <li className="sr-check-item sr-tone-positive" data-testid="check-passed">
            <span className="sr-check-name">
              {fact.check_pass} check{fact.check_pass === 1 ? "" : "s"} passed
            </span>
            <StatusBadge display={checkSummaryDisplay("passed")} />
          </li>
        ) : null}
      </ul>

      {(isConflict || isUnresolved) && fact.downstream_impact ? (
        <p className="sr-check-detail" data-testid="check-reason">
          {fact.downstream_impact.reason}
        </p>
      ) : null}

      {isConflict ? (
        <p className="sr-check-resolve" data-testid="conflict-resolve">
          This conflict cannot be dismissed. Resolve it by correcting the fact or
          rejecting the detection — both require a reason and are audited.
        </p>
      ) : null}
    </div>
  );
}
