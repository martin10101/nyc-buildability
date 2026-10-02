// Server-read, default-off gate for the LANE D lot-choice + site-facts setup
// surface (queue D-04, plan M1-13, §3 steps 2-3). New lane behaviour ships OFF
// in production (lane prompt "New behavior goes behind your lane flag").
//
// The panel renders only when the non-public runtime flag
// INTERNAL_LOT_SITE_SETUP_ENABLED holds an explicit true token. Absent, empty
// or unknown -> off (fail safe). Same pattern as INTERNAL_PROPOSAL_EDITOR_ENABLED
// (src/lib/architect/proposal-editor-flag.ts) and
// INTERNAL_SHARED_STUDY_STORE_ENABLED (src/lib/study/shared-study-flag.ts):
// never prefixed NEXT_PUBLIC_, so it is never inlined into the browser bundle. A
// Server Component reads it once per request and passes a plain boolean into the
// client tree; no client value can turn it on.

const TRUE_TOKENS: ReadonlySet<string> = new Set(["1", "true", "yes", "on"]);

export const LOT_SITE_SETUP_FLAG = "INTERNAL_LOT_SITE_SETUP_ENABLED";

export function lotSiteSetupEnabled(
  env: Record<string, string | undefined> = process.env,
): boolean {
  const raw = env[LOT_SITE_SETUP_FLAG];
  return typeof raw === "string" && TRUE_TOKENS.has(raw.trim().toLowerCase());
}
