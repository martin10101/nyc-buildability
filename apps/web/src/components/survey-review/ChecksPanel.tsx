"use client";

import { StatusBadge } from "./StatusBadge";
import { checkLabel, checkStatusDisplay } from "@/lib/surveyReview/labels";
import { renderValue } from "@/lib/surveyReview/model";
import type { SurveyEvidenceFact } from "@/lib/surveyReview/types";

/**
 * Deterministic-check panel (task M2-T016; workflow §7.4, §10.2, SC-S6).
 *
 * A failing check is a CONFLICT: shown with a plain-language explanation of what
 * disagrees and by how much (using the check's expected/observed values). A
 * conflict is UNRESOLVABLE-BY-CLICK — there is deliberately NO acknowledge /
 * dismiss / ignore control. The only resolutions are Correct (with reason) or
 * Reject (with reason), offered by the focused item's action set. Passing checks
 * are shown plainly; unresolved checks are a visible fail-closed condition.
 */
export function ChecksPanel({ fact }: { fact: SurveyEvidenceFact }) {
  const checks = fact.validation_results;
  if (checks.length === 0) {
    return (
      <p className="section-note" data-testid="checks-empty">
        No deterministic check has run against this fact yet.
      </p>
    );
  }
  return (
    <ul className="sr-checks" data-testid="checks-panel">
      {checks.map((check) => {
        const display = checkStatusDisplay(check.status);
        const isConflict = check.status === "fail";
        const isUnresolved = check.status === "unresolved";
        return (
          <li
            key={`${check.check_id}-${check.status}`}
            className={`sr-check-item sr-tone-${display.tone}`}
            data-testid={`check-${check.check_id}`}
          >
            <div className="sr-check-head">
              <span className="sr-check-name">{checkLabel(check.check_id)}</span>
              <StatusBadge display={display} />
            </div>
            {check.detail ? <p className="sr-check-detail">{check.detail}</p> : null}
            {(isConflict || isUnresolved) &&
            (check.expected_value !== undefined || check.observed_value !== undefined) ? (
              <dl className="sr-check-values">
                {check.expected_value !== undefined ? (
                  <div>
                    <dt>Expected</dt>
                    <dd>{renderValue(check.expected_value)}</dd>
                  </div>
                ) : null}
                {check.observed_value !== undefined ? (
                  <div>
                    <dt>Observed</dt>
                    <dd>{renderValue(check.observed_value)}</dd>
                  </div>
                ) : null}
              </dl>
            ) : null}
            {isConflict ? (
              <p className="sr-check-resolve" data-testid={`conflict-resolve-${check.check_id}`}>
                This conflict cannot be dismissed. Resolve it by correcting the
                fact or rejecting the detection — both require a reason and are
                audited.
              </p>
            ) : null}
          </li>
        );
      })}
    </ul>
  );
}
