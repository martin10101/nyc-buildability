// Server-read, default-off gate for moving surfaces onto the shared study store
// (task C-05, plan M1-10). The store itself changes no behavior: nothing reads
// it until a surface adopts it, and each adopting surface keeps its current
// local state unless INTERNAL_SHARED_STUDY_STORE_ENABLED holds an explicit true
// token. Absent, empty or unknown -> off (fail safe). Same pattern as
// INTERNAL_PROPOSAL_EDITOR_ENABLED (src/lib/architect/proposal-editor-flag.ts):
// never prefixed NEXT_PUBLIC_, so it is never inlined into the browser bundle; a
// Server Component reads it per request and passes a plain boolean down.

const TRUE_TOKENS: ReadonlySet<string> = new Set(["1", "true", "yes", "on"]);

export const SHARED_STUDY_STORE_FLAG = "INTERNAL_SHARED_STUDY_STORE_ENABLED";

export function sharedStudyStoreEnabled(
  env: Record<string, string | undefined> = process.env,
): boolean {
  const raw = env[SHARED_STUDY_STORE_FLAG];
  return typeof raw === "string" && TRUE_TOKENS.has(raw.trim().toLowerCase());
}
