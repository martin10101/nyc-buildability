"use client";

import { documentStateDisplay } from "@/lib/surveyReview/labels";
import type { TransitionRecord } from "@/lib/surveyReview/types";

/**
 * Append-only document lifecycle audit trail (task M2-T016; workflow §8).
 * Every transition is attributed, timestamped, and reasoned where required —
 * the history replays uploaded → … → current. Progressive disclosure: it lives
 * behind a summary so it never clutters the main decision surface.
 */
export function StateHistory({ history }: { history: TransitionRecord[] }) {
  return (
    <details className="sr-state-history" data-testid="state-history">
      <summary>Document audit trail ({history.length} transition{history.length === 1 ? "" : "s"})</summary>
      <table className="facts-table">
        <caption>State transitions (oldest first)</caption>
        <thead>
          <tr>
            <th scope="col">When</th>
            <th scope="col">From → To</th>
            <th scope="col">Actor</th>
            <th scope="col">Reason</th>
          </tr>
        </thead>
        <tbody>
          {history.map((record, index) => (
            <tr key={`${record.occurred_at}-${index}`} data-testid={`transition-${index}`}>
              <td>{record.occurred_at}</td>
              <td>
                {record.from_state ? documentStateDisplay(record.from_state).label : "—"} →{" "}
                {documentStateDisplay(record.to_state).label}
              </td>
              <td>
                {record.actor_kind}
                {record.actor_id ? ` (${record.actor_id})` : ""}
              </td>
              <td>{record.reason ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </details>
  );
}
