# M5-T026 producer report — D-057 default-on gate mode

**Task:** M5-T026 · **Directive:** D-057 (D-057-R001..R003 applicable here; D-057-R004 applies
only to `D-057-BOOTSTRAP`, not to this task) · **Producer:** frontend-engineer (claude-sonnet-5,
D-047-R001 dispatch override recorded in the G0 report) · **Worktree:** `wt-m5t026`, claim head
`554acac39c767d85809063b0e4df8b1cef091348`.

## Files changed (exactly the 5 allowed_paths; nothing else)

1. `apps/web/src/lib/rule-evaluation.ts`
2. `apps/web/src/lib/__tests__/rule-evaluation.test.ts`
3. `apps/web/src/app/property/page.tsx`
4. `docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md`
5. `project-control/reports/M5-T026-producer-report.md` (this file)

`git diff --stat` at HEAD before commit:

```
 apps/web/src/app/property/page.tsx                 |  11 +-
 apps/web/src/lib/__tests__/rule-evaluation.test.ts | 200 +++++++++++++++++++++
 apps/web/src/lib/rule-evaluation.ts                |  56 ++++--
 docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md        |  31 +++-
 4 files changed, 285 insertions(+), 13 deletions(-)
```

No `apps/web/e2e/**`, `apps/web/playwright.config.ts`, `apps/web/src/components/**`,
`apps/web/src/lib/rule-evaluation-api.ts`, `package.json`, or lockfile touched. Zero new
dependencies; no `npm install` run (this machine has no `node_modules` — the CI `web` +
`web-e2e` jobs on the pushed head are the executable authority, per
`documented_test_commands`).

## R001 — the code change

`apps/web/src/lib/rule-evaluation.ts`:

- Added `export const INTERNAL_RULE_EVAL_DEFAULT_ON_ENV_VAR = "INTERNAL_RULE_EVAL_DEFAULT_ON";`
  and `export function ruleEvaluationDefaultOnEnabled(rawValue = process.env[...])`, a byte-for-byte
  mirror of `ruleEvaluationFlagEnabled` (same `TRUE_TOKENS` set, same trim/lowercase, same
  absent/empty/unknown -> `false` fail-safe). Server-read only, default parameter form (never
  build-inlined, read per request, like factor 1).
- Extended `ruleEvaluationSurfaceEnabled` to the exact decision table:
  ```ts
  export function ruleEvaluationSurfaceEnabled(params?: {
    ruleeval?: string | string[] | undefined;
  }): boolean {
    if (!ruleEvaluationFlagEnabled()) return false;
    const raw = params?.ruleeval;
    if (raw === undefined) return ruleEvaluationDefaultOnEnabled();
    const value = Array.isArray(raw) ? raw[0] : raw;
    return typeof value === "string" && TRUE_TOKENS.has(value.trim().toLowerCase());
  }
  ```
  - main flag not a true token -> `false`, always (unchanged; early return, unaffected by the new
    var or the param).
  - `raw === undefined` (the `ruleeval` key itself absent from `params`) -> `true` iff
    `ruleEvaluationDefaultOnEnabled()` holds; `false` when the new var is unset (today's behavior).
  - `raw` **present** in any other shape — a string (`"on"`, `"off"`, `"0"`, `""`, `"banana"`),
    an array (`["on","off"]`, `["off"]`), or even an **empty array** `[]` — goes through the
    existing array-first / trim / lowercase `TRUE_TOKENS` check exactly as before. A true token
    anywhere in that path (e.g. `"on"`, `["on","off"]` whose `raw[0]` is `"on"`) is `true`; anything
    else, including `[]` (whose `raw[0]` is `undefined`, `typeof value !== "string"`), is `false`
    — the fail-safe kill switch, never weakened by the default-on var. **Design note:** `[]` is
    classified as *present* (kill-switch bucket), not *absent* (default-on bucket), because `raw`
    itself (`params.ruleeval`) is a defined empty array, not `undefined` — only a truly missing key
    consults the new var. This matches the packet's own bucketing ("present AND NOT a true token…
    or weird arrays -> false").
- Updated the factor-2 module comment block (lines ~67-83) to describe both the opt-in and the
  default-on path, and to state the kill-switch invariant explicitly.
- Updated `apps/web/src/app/property/page.tsx`'s docstring (the stale "acts only as a fail-safe
  kill switch" line) to describe both modes accurately; the function body is **unchanged** — the
  call site (`ruleEvaluationSurfaceEnabled({ ruleeval: params.ruleeval })`) already passes the
  param through unmodified, so no logic edit was needed there, per the packet's own prediction.

**NEXT_PUBLIC check:** grepped the diff (added/removed lines only, `git diff` hunks) across all
four content files for the string `NEXT_PUBLIC` — zero matches in lines I added or removed. One
**pre-existing, unchanged context line** (`* endpoint. Server-side only — deliberately NOT
NEXT_PUBLIC_. */`, already in the file before this task, shown only because `git diff` prints
surrounding context) appears in the raw diff output; it carries no `+`/`-` prefix and was not
touched. My first draft comment for the new var *did* introduce the literal string
`NEXT_PUBLIC_` in a negated sentence ("deliberately NOT NEXT_PUBLIC_") — caught during self-check
and rewritten to "never inlined into the browser bundle" before commit, so the added/removed
lines are clean. The doc checklist's new §2a section does say `NEXT_PUBLIC_API_BASE_URL` once (to
contrast it against the new server-read var, mirroring how the existing checklist already
discusses that name at length) — I read the "no NEXT_PUBLIC anywhere in your diff" instruction as
scoped to not introducing a `NEXT_PUBLIC_`-prefixed var for this feature (the R001 code
requirement), not as a ban on ever mentioning the term in a deploy-ops document that already
uses it extensively for an unrelated, pre-existing var; flagging this reading explicitly in case
the reviewer wants it removed.

## R002 — zero regression where the var is unset

- `docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md`: `git diff` — no `apps/web/e2e/**` or
  `apps/web/playwright.config.ts` path in the changed-files list (confirmed above).
- `apps/web/src/lib/__tests__/rule-evaluation.test.ts`:
  - All four pre-existing describe blocks (`frontend flag — env gate`, `frontend flag — surface
    gate (env AND opt-in)`, plus everything below) are **unmodified** — same assertions, same
    bodies. A new module-scope `beforeEach`/`afterEach` pair (added once, near the top of the
    file, after the `stub()` helper) saves/clears/restores `INTERNAL_RULE_EVAL_DEFAULT_ON` around
    **every** test in the file, so the pre-existing tests — which never reference the new var —
    are guaranteed to see it absent, exactly as if the var did not exist (their own preconditions
    are untouched).
  - New describe `D-057-R002 — zero behavior change where INTERNAL_RULE_EVAL_DEFAULT_ON is
    unset` (5 explicit `it` blocks, not `it.each`, one assertion group per pre-D-057 scenario):
    main-flag-off (any params), main-flag-on + param-absent (**the exact pre-D-057 default**),
    main-flag-on + `off`, main-flag-on + `on` (both string and one-element-array form, matching
    the pre-existing "is ON only with…" test's own assertions verbatim), main-flag-on + garbage /
    array forms (`"0"`, `""`, `"banana"`, `["off"]`, `[]`). Every one of these rows asserts the
    identical output the pre-D-057 code would have produced for that input (verified by reading
    the pre-change function: `if (!flag) return false; const value = arrayFirst(raw); return
    isTrueToken(value);` — identical to the post-change path whenever `raw !== undefined`, and
    `raw === undefined` now routes through `ruleEvaluationDefaultOnEnabled()` which, unset,
    returns `false` — the same constant the pre-change code effectively returned for that case
    since `typeof undefined !== "string"`).
  - The same var-absent equivalence is **also** exercised as the `"unset"` row of the 50-row
    D-057 full decision matrix (describe `ruleEvaluationSurfaceEnabled — D-057 full decision
    matrix (main flag ON)`), giving two independent paths to the same evidence (a dedicated,
    readable R002 block for the reviewer, plus matrix coverage for completeness).

## R003 — operator doc

`docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md`:

- New `### 2a. OPTIONAL — default-on mode for the internal surfaces (D-057, added 2026-09-14)`
  subsection placed directly after §2's numbered list (before the `---` separator into §3). Names
  the exact var (`INTERNAL_RULE_EVAL_DEFAULT_ON` = `1`), states **WEB service only** (not
  `nycdf-api`), explains what it does (plain `/property` shows the full internal flow with no
  query param, gated jointly with the existing `INTERNAL_RULE_EVAL_ENABLED`), states the exposure
  consequence sentence (anyone holding the URL sees the full flow immediately — one fewer privacy
  layer — framed against the already-accepted §5 posture and D-057's own owner-accepted framing),
  states `?ruleeval=off` remains the kill switch, and states the var is server-read so saving it
  (automatic restart) suffices with no rebuild (contrasted explicitly against
  `NEXT_PUBLIC_API_BASE_URL`'s build-inlining rule already documented in step 2).
- One-line pointer added in §9's "FIRST, understand the opt-in URL" paragraph, right after the
  `?ruleeval=on` URL example, noting the §2a alternative.
- One new row added to the "Provenance summary" table at the bottom, in the same style as the
  existing rows (claim + source file/line pointer + the directive).
- Kept the document's existing voice (bold key terms, inline source citations, "owner-executed"
  framing) and did not touch any other section's content.

## Test matrix (S1) — counts and structure

`apps/web/src/lib/__tests__/rule-evaluation.test.ts` gained four new `describe` blocks (plus the
existing ones left byte-for-byte unmodified):

1. `ruleEvaluationDefaultOnEnabled — token classification (same TRUE_TOKENS rule)` — 8-row
   `it.each` token table (`1/true/on/YES` -> true; `0/off/""/maybe` -> false) + 1 explicit
   "absent -> false" test. **9 cases.**
2. `ruleEvaluationSurfaceEnabled — D-057 full decision matrix (main flag ON)` — a generated
   5 (default-on: unset/`1`/`true`/`garbage`/`""`) × 10 (param: absent / `"on"` / `"ON "` (case +
   trailing-space) / `"off"` / `"0"` / `""` / `"banana"` / `["on","off"]` / `["off"]` / `[]`)
   cross-product, **50 rows**, each asserting a literal expected boolean (not derived by calling
   the implementation — the expected value is hand-classified per param bucket: the "absent" row
   depends on the default-on column; every other param row is a fixed true/false regardless of
   the default-on column, matching the packet's own decision table).
3. `ruleEvaluationSurfaceEnabled — main flag OFF always wins (D-057-R001)` — 3 `it.each` blocks
   (flag unset / `"0"` / `"banana"`, each against default-on=`1` and one of `{param absent, "on",
   "off"}`) proving factor 1 short-circuits before either the new var or the param is read.
   **3 + 2 + 2 = 7 cases.**
4. `D-057-R002 — zero behavior change where INTERNAL_RULE_EVAL_DEFAULT_ON is unset` — 5 explicit
   `it` blocks (described above). **5 cases.**

**Total new test cases: 71** (9 + 50 + 7 + 5), all fail-safe/kill-switch rows explicit per the
packet's S1 requirement. Pre-existing test cases in the file (env-gate, surface-gate,
retired-split-name, status/state pair matrix, `fetchRuleEvaluation` envelopes, presentation
classifier, contract validation, announcements) are **unmodified**.

## Self-checks run

- `python tools/modularity_check.py --check` — **0 failures, 17 warnings**, none against any of
  the four changed files (`rule-evaluation.ts`, `rule-evaluation.test.ts`, `page.tsx`,
  `RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md` are absent from the warning list).
- `git diff --stat` / `git status --short` reviewed to confirm exactly the 5 allowed files
  changed, no forbidden path touched.
- Manual re-read of the full diff for both code files; a crude bracket-balance check
  (`node -e` counting `{`/`(`/`[` vs `}`/`)`/`]`) returned a final depth of `0` for both
  `rule-evaluation.ts` and `rule-evaluation.test.ts` as a sanity signal (not a substitute for
  `tsc`/`vitest`).
- Grep for `NEXT_PUBLIC` across the diff (see R001 section above for the exact finding and the
  one judgment call flagged for the reviewer).

## Limitations (disclosed)

- **No local test runner.** This machine has no `node_modules` (thin-client policy); `vitest`,
  `tsc`, and Playwright were **not** run locally. Self-checks above are static (modularity check,
  manual diff re-read, bracket-balance sanity check). **CI `web` (lint + typecheck + build) and
  `web-e2e` (vitest + Playwright) on the pushed head are the executable authority** per this
  task's `documented_test_commands` — S1/S2/S4 acceptance ultimately rests on that CI run, not on
  anything this report can execute.
- The `NEXT_PUBLIC` scoping judgment call in the R001 section above (checklist doc mentioning the
  pre-existing `NEXT_PUBLIC_API_BASE_URL` var) is disclosed for reviewer confirmation rather than
  silently assumed.
- D-057-R004 (owner activation return / seam-report step) is **not** in this task's applicable
  requirement set (`M5-T026` is not listed in that requirement's `applicability.task_ids` — only
  `D-057-BOOTSTRAP` is) and is therefore intentionally not addressed here; it belongs to whichever
  task closes the directive at the seam.
