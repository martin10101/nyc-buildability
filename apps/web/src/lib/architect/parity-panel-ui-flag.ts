// Server-read, default-off gate for the LANE D parity SURFACE — the
// "Comparable sales & floor area" tool window (queue D-15, plan §11b, B-11).
// New lane behaviour ships OFF in production (lane prompt "New behavior goes
// behind your lane flag").
//
// This is the WEB surface gate: it decides whether the parity tool window is
// shown and fetches at all. It is DISTINCT from lane C's server read-route gate
// INTERNAL_PARITY_READ_ENABLED (services/api parity_read.py), which the route
// itself reads; so even with this flag ON the panel gets a 404 "not connected
// yet" card until lane C mounts and enables the read route.
//
// The panel renders only when the non-public runtime flag
// INTERNAL_PARITY_UI_ENABLED holds an explicit true token. Absent, empty or
// unknown -> off (fail safe). Same pattern as
// INTERNAL_HIDDEN_ISSUE_FLAGS_UI_ENABLED (hidden-issue-flags-ui-flag.ts): never
// prefixed NEXT_PUBLIC_, so it is never inlined into the browser bundle. A
// Server Component reads it once per request and passes a plain boolean into the
// client tree; no client value can turn it on.

const TRUE_TOKENS: ReadonlySet<string> = new Set(["1", "true", "yes", "on"]);

export const PARITY_UI_FLAG = "INTERNAL_PARITY_UI_ENABLED";

export function parityUiEnabled(
  env: Record<string, string | undefined> = process.env,
): boolean {
  const raw = env[PARITY_UI_FLAG];
  return typeof raw === "string" && TRUE_TOKENS.has(raw.trim().toLowerCase());
}
