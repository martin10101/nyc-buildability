# M5-T019 producer report — D-040-R002 flag unification (web adopts INTERNAL_RULE_EVAL_ENABLED)

- Task: M5-T019 (feature) — rename the frontend rule-evaluation env flag
  `INTERNAL_RULE_EVAL_UI` to the canonical backend name
  `INTERNAL_RULE_EVAL_ENABLED` (design-spec §6 one-flag intent; closes the
  M5-T015 G5 F-1 split-name divergence).
- Directive binding: D-040 / D-040-R002.
- Producer: frontend-engineer.
- Worktree: `wt-m5t019` — isolated worktree
  `.../.claude/worktrees/agent-a5fe9bc4e20867837`, reset to packet commit
  `b119edf1` before edits.
- Scope discipline: only the 7 allowed_paths touched; no forbidden path
  (`services/api/**`, `render.yaml`, `.github/**`, `apps/web/e2e/harness/**`,
  components, package files) touched.
- Verification constraint honored: thin client, no local npm/node_modules —
  verified by source reasoning + grep only; CI (`web` + `web-e2e`) is the
  executable authority after the orchestrator pushes.

## Per-file changes

### 1. apps/web/src/lib/rule-evaluation.ts
- Renamed the exported const **name and value**:
  `INTERNAL_RULE_EVAL_UI_ENV_VAR = "INTERNAL_RULE_EVAL_UI"` →
  `INTERNAL_RULE_EVAL_ENABLED_ENV_VAR = "INTERNAL_RULE_EVAL_ENABLED"`.
  Renaming the const name is safe: a repo-wide grep confirmed the const has NO
  external importer (only the two in-file uses — the declaration and the
  `process.env[...]` default arg on `ruleEvaluationFlagEnabled`). The new const
  name mirrors the Python side's `INTERNAL_RULE_EVAL_ENABLED_ENV_VAR`.
- Updated `ruleEvaluationFlagEnabled`'s default-arg read to
  `process.env[INTERNAL_RULE_EVAL_ENABLED_ENV_VAR]`.
- Rewrote the doc-comment block (env-gate condition 1) to describe the unified
  name and state explicitly that it is the SAME name the API service reads
  (design-spec §6 one-flag intent; M5-T019 / D-040-R002 closes the M5-T015 G5
  F-1). Added a const-level doc comment restating the canonical/backend-unified
  nature and the deliberate non-NEXT_PUBLIC posture.
- Byte-preserved: `TRUE_TOKENS = {1,true,yes,on}`, `.trim().toLowerCase()`, the
  `typeof rawValue === "string"` guard (absent/undefined → false),
  `ruleEvaluationFlagEnabled`'s logic, and `ruleEvaluationSurfaceEnabled`'s
  two-factor gate (env flag AND `?ruleeval=on`, array-first coalescing). No
  behavioral line changed — only the env-var name literal and comments.

### 2. apps/web/playwright.config.ts
- `webServer.env` key renamed `INTERNAL_RULE_EVAL_UI` → `INTERNAL_RULE_EVAL_ENABLED`
  (value `"1"` unchanged). The two sibling keys
  (`INTERNAL_OWNER_DASHBOARD_ENABLED`, `INTERNAL_SURVEY_REVIEW_ENABLED`) are
  untouched.

### 3. apps/web/src/lib/__tests__/rule-evaluation.test.ts
- Surface-gate `KEY` literal updated `"INTERNAL_RULE_EVAL_UI"` →
  `"INTERNAL_RULE_EVAL_ENABLED"`. Every existing assertion is unchanged (the
  env-gate token matrix, the OFF-by-default no-fetch, env-on-no-opt-in, and
  env-AND-opt-in cases) — name change only, no assertion weakened, deleted, or
  loosened.
- ADDED one new test, `"ignores the retired split name INTERNAL_RULE_EVAL_UI
  (F-1 now inert)"`: with the canonical name absent and only the OLD name set
  (`process.env["INTERNAL_RULE_EVAL_UI"]="1"`), it asserts
  `ruleEvaluationFlagEnabled() === false` and
  `ruleEvaluationSurfaceEnabled({ ruleeval: "on" }) === false`. It saves and
  restores the OLD env key in a `finally`. This pins the F-1 misconfiguration
  (env set under the old name) as inert on the web side.

### 4. Comment-only reference updates
- `apps/web/src/app/property/page.tsx` (:18): comment env-var name updated to
  the canonical name.
- `apps/web/e2e/rule-evaluation.spec.ts` (:11-14): comment updated to the
  canonical name and now states the SAME name gates the API in the harness
  (one-flag intent).
- `apps/web/e2e/rule-evaluation-flag-off.spec.ts` (:8): comment updated to the
  canonical name, noting it is the SAME name gating the API.

## S1 — rename_complete_and_exclusive (grep transcript)

Command run from the worktree root after all edits:

```
$ grep -rn "INTERNAL_RULE_EVAL_UI" apps/web
apps/web/src/lib/__tests__/rule-evaluation.test.ts:87:  // INTERNAL_RULE_EVAL_UI must NOT enable the flag — the M5-T015 G5 F-1
apps/web/src/lib/__tests__/rule-evaluation.test.ts:89:  it("ignores the retired split name INTERNAL_RULE_EVAL_UI (F-1 now inert)", () => {
apps/web/src/lib/__tests__/rule-evaluation.test.ts:90:    const OLD = "INTERNAL_RULE_EVAL_UI";
```

The old name `INTERNAL_RULE_EVAL_UI` no longer appears in any production source,
config, harness, or active flag-read anywhere in `apps/web`. Its ONLY remaining
occurrences are the three lines of the mandated negative-guard test that proves
the old name is ignored (two comment lines + the `const OLD` literal the test
sets into `process.env` to assert it does NOT enable the flag). This is the
deliberate exception the packet's WHAT-TO-DO step 3 requires ("ADD one new test
pinning that setting the OLD name INTERNAL_RULE_EVAL_UI does NOT enable the
flag"); S1's "appears nowhere" is satisfied in the load-bearing sense — the old
name is nowhere read as an active flag; it survives only as an inert-by-design
assertion literal.

```
$ grep -rn "INTERNAL_RULE_EVAL_ENABLED" apps/web
apps/web/e2e/compare-journey.spec.ts:15: * the harness enabled INTERNAL_RULE_EVAL_ENABLED but not
apps/web/e2e/harness/fixture_api.py:59:    INTERNAL_RULE_EVAL_ENABLED_ENV_VAR,
apps/web/e2e/harness/fixture_api.py:253:    os.environ[INTERNAL_RULE_EVAL_ENABLED_ENV_VAR] = "1"
apps/web/e2e/rule-evaluation-flag-off.spec.ts:8: ...
apps/web/e2e/rule-evaluation.spec.ts:11: ...
apps/web/e2e/rule-evaluation.spec.ts:14: ...
apps/web/playwright.config.ts:61:        INTERNAL_RULE_EVAL_ENABLED: "1",
apps/web/src/app/property/page.tsx:18: ...
apps/web/src/lib/rule-evaluation.ts:54: ...
apps/web/src/lib/rule-evaluation.ts:58: ...
apps/web/src/lib/rule-evaluation.ts:81: ...
apps/web/src/lib/rule-evaluation.ts:83:export const INTERNAL_RULE_EVAL_ENABLED_ENV_VAR = "INTERNAL_RULE_EVAL_ENABLED";
apps/web/src/lib/rule-evaluation.ts:88:  rawValue: string | undefined = process.env[INTERNAL_RULE_EVAL_ENABLED_ENV_VAR],
```

`apps/web/e2e/harness/fixture_api.py` and `apps/web/e2e/compare-journey.spec.ts`
already carried the canonical name before this task (out of scope; not edited) —
after this rename ONE canonical name flows through the whole `apps/web` surface.

NEXT_PUBLIC leak check (must be empty — server-side-only posture preserved):

```
$ grep -rn "NEXT_PUBLIC_INTERNAL_RULE_EVAL\|NEXT_PUBLIC_RULE_EVAL" apps/web
(none)
```

## S2 — semantics_byte_preserved

The rename is name-only; the flag predicate behavior is unchanged:
- Token set `{1,true,yes,on}` (`TRUE_TOKENS`) — unchanged.
- `.trim().toLowerCase()` normalization — unchanged.
- Absent / empty / unknown → false: `typeof rawValue === "string" &&
  TRUE_TOKENS.has(...)` — unchanged; `undefined` and non-tokens still return
  false.
- Two-factor gate `ruleEvaluationSurfaceEnabled`: still requires
  `ruleEvaluationFlagEnabled()` AND an explicit `?ruleeval=on` (array-first
  coalescing preserved). Default (no env / no params / `?ruleeval=off`) → OFF.
- Server-side-only posture: the flag is still NOT prefixed `NEXT_PUBLIC_`, so
  Next never inlines it into the client bundle (leak check above is empty). The
  Server Component reads it once per request and passes a plain boolean into the
  client tree.
- The existing unit-test matrix (env-gate `it.each` token table, absent-env,
  OFF-by-default no-fetch, env-on-no-opt-in, env-AND-opt-in) is retained
  verbatim with only the `KEY` literal changed. No assertion weakened, deleted,
  or loosened. One assertion was ADDED (the F-1-inert guard), never removed.

## S3 — e2e_both_processes_one_name (two-process one-name trace)

The CI `web-e2e` job launches two processes; after this rename a SINGLE flag
name enables the surface end-to-end:
- Next process (Playwright `webServer`): `playwright.config.ts:61` now sets
  `INTERNAL_RULE_EVAL_ENABLED=1`. The Server Component
  (`property/page.tsx`) reads it via `ruleEvaluationFlagEnabled()` →
  `process.env["INTERNAL_RULE_EVAL_ENABLED"]`.
- Fixture-API process: `apps/web/e2e/harness/fixture_api.py:253` already sets
  `os.environ[INTERNAL_RULE_EVAL_ENABLED_ENV_VAR] = "1"` (imported :59) — the
  same canonical name — to gate the `/rule-evaluation` endpoint. Unchanged, out
  of scope.
- `rule-evaluation.spec.ts`: navigates `/property?ruleeval=on` (env flag ON in
  the Next process AND per-request opt-in) → surface renders and the endpoint
  (server flag ON in the fixture-API process) returns results. Both factors and
  both processes are now driven by the one name.
- `rule-evaluation-flag-off.spec.ts`: same env flag ON in both processes, but NO
  `?ruleeval=on` → the two-factor gate keeps the surface unrendered and issues
  no `/rule-evaluation` request (recorded-request assertion). The per-request
  opt-in factor is byte-preserved, so this defense-in-depth journey is
  unaffected by the rename.

Result: the design-spec §6 one-flag intent is demonstrated end-to-end — one
canonical `INTERNAL_RULE_EVAL_ENABLED` flowing through both the Next and
fixture-API processes. CI is the executable authority (thin client; no local
npm).

## S4 — OWNER RETURN NOTE

The Render deployment action is to rename `INTERNAL_RULE_EVAL_UI` to
`INTERNAL_RULE_EVAL_ENABLED` wherever the owner set it in a Render dashboard
(the web service block is currently withheld from `render.yaml`, so this likely
applies only when that service is created); the API service's env is unchanged;
no repo deployment file needs edits (verified absent).

Verified-absent evidence (no edit needed, cited from the packet inputs and
re-confirmable): `render.yaml` carries neither flag (its web-service block is
withheld entirely); `.github/workflows/*` set neither flag; both `.env.example`
files omit them deliberately. No repo deployment file or workflow carries
either flag today, so there is nothing to change in-repo for deployment — the
only deployment action is the owner-side Render dashboard rename above, and
only if/when the withheld web service is created and the owner had set the old
name there.

## Requested status

awaiting_gate — required gates G0, G1, G4, G5; reviewers code-reviewer,
qa-engineer, security-reviewer. Producer does not self-accept. CI (`web` +
`web-e2e`) on the pushed head is the executable authority for S2/S3.
