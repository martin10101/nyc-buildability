// Server-read, default-off gate for the RESULTS panel — the "Results" tool window
// (task M5-T140, Part B of the R6B results connection; ruling R1).
//
// This is the WEB surface gate: it decides whether the Results tool is offered and
// whether the panel is shown at all. It is DISTINCT from the server's read-route gate
// INTERNAL_RESULTS_ENABLED (services/api results_read.py), which the route itself reads;
// so even with this flag ON the panel gets a 404 "not connected yet" card until the
// server route is mounted and enabled.
//
// The panel renders only when the non-public runtime flag INTERNAL_RESULTS_UI_ENABLED
// holds an explicit true token. Absent, empty or unknown -> off (fail safe). Same pattern
// as INTERNAL_PARITY_UI_ENABLED (parity-panel-ui-flag.ts) and
// INTERNAL_PROPOSAL_EDITOR_ENABLED (proposal-editor-flag.ts): never prefixed
// NEXT_PUBLIC_, so it is never inlined into the browser bundle. A Server Component reads
// it once per request and passes a plain boolean into the client tree; no client value
// can turn it on.

const TRUE_TOKENS: ReadonlySet<string> = new Set(["1", "true", "yes", "on"]);

export const RESULTS_UI_FLAG = "INTERNAL_RESULTS_UI_ENABLED";

export function resultsUiEnabled(
  env: Record<string, string | undefined> = process.env,
): boolean {
  const raw = env[RESULTS_UI_FLAG];
  return typeof raw === "string" && TRUE_TOKENS.has(raw.trim().toLowerCase());
}
