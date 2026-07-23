// Internal-only gate for the owner dashboard. Mirrors the M4-T005 rule-eval
// pattern: a NON-public runtime env flag, read fresh each call, fail-safe OFF.
// The flag is NOT prefixed NEXT_PUBLIC_, so it is never inlined into the browser
// bundle. This is the visibility gate, not auth (the app has no auth yet).

const TRUE_TOKENS = new Set(['1', 'true', 'yes', 'on']);

export const DASHBOARD_FLAG = 'INTERNAL_OWNER_DASHBOARD_ENABLED';

export function dashboardEnabled(
  env: Record<string, string | undefined> = process.env,
): boolean {
  const raw = env[DASHBOARD_FLAG];
  if (typeof raw !== 'string') return false;
  return TRUE_TOKENS.has(raw.trim().toLowerCase());
}
