// Server-read, default-off gate for the LANE D §8a hidden-issue-flags SURFACE
// (queue D-12, plan M2-06 / L-11, §8a). New lane behaviour ships OFF in
// production (lane prompt "New behavior goes behind your lane flag").
//
// This is the WEB surface gate: it decides whether the "Hidden issues" tool
// window is shown and fetches at all. It is distinct from the server read-route
// gate INTERNAL_HIDDEN_ISSUE_FLAGS_READ_ENABLED (lane C packet W2), which the
// route itself reads; the route is not mounted yet, so even with this flag ON
// the panel gets a 404 "not connected yet" until lane C mounts it (lane C W5).
//
// The panel renders only when the non-public runtime flag
// INTERNAL_HIDDEN_ISSUE_FLAGS_UI_ENABLED holds an explicit true token. Absent,
// empty or unknown -> off (fail safe). Same pattern as
// INTERNAL_LOT_SITE_SETUP_ENABLED (src/lib/architect/lot-site-setup-flag.ts) and
// INTERNAL_PROPOSAL_EDITOR_ENABLED (src/lib/architect/proposal-editor-flag.ts):
// never prefixed NEXT_PUBLIC_, so it is never inlined into the browser bundle. A
// Server Component reads it once per request and passes a plain boolean into the
// client tree; no client value can turn it on.

const TRUE_TOKENS: ReadonlySet<string> = new Set(["1", "true", "yes", "on"]);

export const HIDDEN_ISSUE_FLAGS_UI_FLAG = "INTERNAL_HIDDEN_ISSUE_FLAGS_UI_ENABLED";

export function hiddenIssueFlagsUiEnabled(
  env: Record<string, string | undefined> = process.env,
): boolean {
  const raw = env[HIDDEN_ISSUE_FLAGS_UI_FLAG];
  return typeof raw === "string" && TRUE_TOKENS.has(raw.trim().toLowerCase());
}
