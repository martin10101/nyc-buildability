// Server-read, default-off gate for the SET-ASIDE proposal editor (queue D-01,
// plan §7 "not a design tool", RECONCILIATION set-aside items #1, #2 and #8).
//
// The proposal editor, its coordinate/vertex drawing and the answer-first
// envelope panel are kept (code and tests) but are not part of the
// real-property workflow. They render only when the non-public runtime flag
// INTERNAL_PROPOSAL_EDITOR_ENABLED holds an explicit true token. Absent, empty
// or unknown -> off (fail safe). Same pattern as INTERNAL_RULE_EVAL_ENABLED
// (src/lib/rule-evaluation.ts) and INTERNAL_SURVEY_REVIEW_ENABLED
// (src/lib/surveyReview/config.ts): never prefixed NEXT_PUBLIC_, so it is
// never inlined into the browser bundle. A Server Component reads it once per
// request and passes a plain boolean into the client tree; no client value can
// turn it on.

const TRUE_TOKENS: ReadonlySet<string> = new Set(["1", "true", "yes", "on"]);

export const PROPOSAL_EDITOR_FLAG = "INTERNAL_PROPOSAL_EDITOR_ENABLED";

export function proposalEditorEnabled(
  env: Record<string, string | undefined> = process.env,
): boolean {
  const raw = env[PROPOSAL_EDITOR_FLAG];
  return typeof raw === "string" && TRUE_TOKENS.has(raw.trim().toLowerCase());
}
