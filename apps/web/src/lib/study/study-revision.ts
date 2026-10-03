/**
 * Study revisions and the late-response rule (task C-06, plan M1-11; plan
 * section 9 "Dependency-based invalidation": "Late responses never overwrite
 * newer ones"). Browser memory only: pure, no clock, no network, no storage.
 *
 * Every change to a study is a new revision (study.schema.json revision.number:
 * an integer that starts at 1 and only increases). A compute request for an
 * option carries that number as a monotonic token; the response echoes it. When
 * the response returns, its token is compared with the option's current
 * revision:
 *  - equal   -> the response is for the current study and may be applied;
 *  - older   -> a stale response; it is dropped and recorded as ignored;
 *  - newer   -> fail closed: a response can never be for a future revision, so
 *               it is dropped too (never applied).
 *
 * This is the same comparison the store already keeps in
 * study-operations.markOptionResultsCurrent; this module states the rule once so
 * the C-06 result model (study-invalidation) and that store path cannot drift.
 *
 * Slice-1 note: the token is the WHOLE-study revision (study-store.ts keeps one
 * monotonic counter per study), so a change to any option advances every
 * option's token. That is intentionally conservative - it never applies a
 * possibly stale result; at worst it forces a redundant recompute. A per-option
 * token (so an unrelated option's change does not drop an in-flight response) is
 * a slice-2 refinement that waits on durable storage (B-001 / Q7).
 */

/** A monotonic study revision used as a request/response token (study.schema.json revision.number). */
export type RevisionToken = number;

/** Whether a computed response may be applied, and why not when it may not. */
export type ResponseDecision =
  | { readonly apply: true }
  | {
      readonly apply: false;
      /** stale_response = older token; revision_mismatch = a token newer than current (fail closed). */
      readonly ignored: "stale_response" | "revision_mismatch";
      readonly responseRevision: RevisionToken;
      readonly currentRevision: RevisionToken;
    };

/**
 * Classify a computed response against the option's current revision. A response
 * is applied ONLY when its token equals the current revision; any other token is
 * dropped and recorded as ignored, never applied (plan section 9).
 */
export function classifyResponse(
  responseRevision: RevisionToken,
  currentRevision: RevisionToken,
): ResponseDecision {
  if (responseRevision === currentRevision) return { apply: true };
  const ignored = responseRevision < currentRevision ? "stale_response" : "revision_mismatch";
  return { apply: false, ignored, responseRevision, currentRevision };
}

/** True only when a response's token is exactly the current revision. */
export function isResponseCurrent(
  responseRevision: RevisionToken,
  currentRevision: RevisionToken,
): boolean {
  return classifyResponse(responseRevision, currentRevision).apply;
}
