// Internal-only visibility gate for the survey-review screens (task M2-T016).
// Mirrors the dashboard / rule-eval pattern: a NON-public runtime env flag,
// read fresh each call, fail-safe OFF, never prefixed NEXT_PUBLIC_ so it is
// never inlined into the browser bundle. This is a visibility gate, not auth
// (the app has no auth yet — B-001); the backend re-enforces every action.

const TRUE_TOKENS = new Set(["1", "true", "yes", "on"]);

export const SURVEY_REVIEW_FLAG = "INTERNAL_SURVEY_REVIEW_ENABLED";

export function surveyReviewEnabled(
  env: Record<string, string | undefined> = process.env,
): boolean {
  const raw = env[SURVEY_REVIEW_FLAG];
  if (typeof raw !== "string") return false;
  return TRUE_TOKENS.has(raw.trim().toLowerCase());
}
