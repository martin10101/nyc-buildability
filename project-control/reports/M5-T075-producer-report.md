# M5-T075 — producer report (DB-045(i) outline-bridge client browser-fault tests)

- Task: M5-T075 · directive D-084-R001 · producer qa-engineer
- Scope (test-only): `apps/web/src/lib/__tests__/outline-bridge-api.test.ts` (additions only)
- Production client UNDER TEST (READ-ONLY here): `apps/web/src/lib/outline-bridge-api.ts`
- Content identity bound by the orchestrator at the submit/commit seam (git blob sha of the one
  edited test file); no production file changed.

## What was added

One new `describe` block, "fetchOutlineBridge — browser-fault branches (DB-045(i))", appended after
the existing suites (test file lines 263–385), plus one import symbol (`MAX_RESPONSE_BYTES`) and three
local fetch-stub helpers (`rejectingFetch`, `abortAwareFetch`, `runWith`) mirroring the file's existing
`stub`/`run` idioms. Five specs, one per client browser-fault branch. Every existing assertion is
byte-unchanged; zero production edits (AS-4).

### D-084 lane-1 re-feed revision (this checkpoint)

Two changes on top of the increment above, both inside the one allowed test file; no production code
touched, no pre-existing assertion changed or removed:

1. The three nonempty announcement assertions (network, timeout, over-budget) now ALSO assert the
   COMPLETE bounded copy with `.toBe(<literal>)`, the literal copied verbatim from the client's
   `announcementForOutlineBridge` arms — not a substring and not a value re-derived from production at
   runtime. The pre-existing `.toContain(...)` substring checks are kept alongside them.
2. The mid-flight caller-abort mutation prediction is corrected (AS-3 #4 below) after rechecking the
   full catch condition; a clarifying comment was added to the mid-flight spec explaining that the
   caller abort also aborts the client's internal controller, so the whole `aborted` guard — not the
   external-signal operand alone — is the load-bearing mutation target.

The fault classes exercised map to the client branches in `outline-bridge-api.ts`:

| Spec (test line) | Client branch (source line) | Asserted typed outcome |
|---|---|---|
| network TypeError (319) | fetch-catch fallthrough `outline-bridge-api.ts:382–387` | `network_error` |
| timeout AbortError (329) | `if (timedOut)` in fetch-catch `:380` | `client_timeout` (timeoutMs carried) |
| pre-flight caller abort (341) | early `if (externalSignal?.aborted)` `:359–361` | `aborted` (fetch NOT called) |
| mid-flight caller abort (358) | `externalSignal?.aborted` in fetch-catch `:381` | `aborted` |
| over-budget Content-Length (370) | size-bound-before-parse `:399–401` | `unexpected_response` (status 200, state null) |

## AS coverage

- AS-1 (fault typing): each spec asserts the EXACT outcome `kind` and, for the three nonempty
  announcements, the COMPLETE bounded copy via `.toBe(...)` against the literal string copied from the
  client's `announcementForOutlineBridge` arm (`outline-bridge-api.ts:549–556`) — not just a substring
  and not a value re-derived from production at runtime:
  - network → `"Outline not converted: the bridge service could not be reached."`
  - timeout → `"Outline not converted: the request took too long and was cancelled."`
  - over-budget → `"Outline not converted: unexpected response from the platform API."`
  The retained `.toContain(...)` substring checks are preserved alongside the new complete-copy `.toBe`
  (no pre-existing assertion removed). Both `aborted` paths assert `.toBe("")` (announces nothing). The
  two caller-abort paths (pre-flight early return and mid-flight catch) are distinct client branches
  proven separately though they share the `aborted` outcome; the pre-flight spec also asserts
  `fetchCalls === 0` (the request never leaves the client).
- AS-2 (never laundered): every spec asserts `REFUSAL_OR_BRIDGED_KINDS.has(outcome.kind) === false`
  — no fault is ever a bridged coordinate or any typed refusal (payload/invalid/out-of-neighborhood/
  correspondence/residual/feature). Network and timeout additionally assert
  `outlineBridgeOutcomeIsRecoverable === true` (a Retry is meaningful); refusals would be non-recoverable.
- AS-3 (mutation sensitivity) — the single client mutation predicted to redden each spec (CI proves
  green; nothing run locally):
  1. network → change the `:382` `network_error` return to any refusal/`aborted` → `toBe("network_error")` reddens.
  2. timeout → delete the `:380` `if (timedOut) return client_timeout` guard → falls to `aborted` → reddens.
  3. pre-flight abort → remove the `:359–361` early return → `fetchImpl` runs (`fetchCalls === 1`) → reddens.
  4. mid-flight abort → CORRECTED after rechecking the full catch condition. The caller abort
     propagates into the client's INTERNAL controller (`onExternalAbort` at `:363`), so at `:381` BOTH
     `controller.signal.aborted` AND `externalSignal?.aborted` are true. Dropping only
     `|| externalSignal?.aborted` is therefore INEFFECTIVE (the first operand still returns `aborted`;
     the spec stays green), and dropping only `controller.signal.aborted` is equally ineffective. The
     single mutation that actually reddens THIS fixture is deleting the whole
     `if (controller.signal.aborted || externalSignal?.aborted) return { kind: "aborted" }` guard at
     `:381`: the mid-flight fixture then falls to `network_error`, so `expect(outcome.kind).toBe("aborted")`
     and the empty-announcement `expect(...).toBe("")` both redden. (The prior report claimed the
     single-operand drop; that prediction was wrong and is superseded here.)
  5. over-budget → flip `:399` `declaredLength > MAX_RESPONSE_BYTES` to `<` → body is parsed → `bridged` → reddens (AS-2 negative also reddens).
- AS-4 (no scope creep): additions confined to the one allowed test file; production
  `outline-bridge-api.ts` untouched (READ-ONLY per the packet + code-graph note). No production fix was
  needed — no finding routed to the orchestrator.

## Evidence status

- [OBSERVED, prior increment] `python tools/modularity_check.py --check` → `selected 475 files;
  failures 0; warnings 22`. All 22 warnings are pre-existing production modules; the edited test file is
  not among them. The re-feed revision is test-only (added `.toBe` complete-copy assertions and
  comments), so the module surface is unchanged; definitive re-run is part of orchestrator CI.
- [PREDICTED / route-to-CI] vitest suite `apps/web/src/lib/__tests__/outline-bridge-api.test.ts` green
  on the pushed head. THIN CLIENT: web tests are NOT run locally (no npm/npx/node); the suite proves
  only in CI on the seam-push. Determinism basis (static): jsdom env with real timers
  (`apps/web/vitest.config.ts`; no global `vi.useFakeTimers`), so the timeout spec's 10 ms internal
  timer fires against a never-settling fetch; caller-abort listeners attach synchronously before the
  test's `abort()`; the over-budget spec reads `Content-Length` before parse so no large body is needed.
- [OBSERVED] Static self-review: import extended by one symbol (no duplicate-import); no production
  import edited; existing assertions unchanged; TS strictness (Set type arg pinned, `as typeof fetch`
  stub casts mirror the existing `stub`) reviewed.

## Notes

- No blockers. No owner decision required. No new dependency.
