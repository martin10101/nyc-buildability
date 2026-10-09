# M0-T180 — producer report

Task: remove the braces advisory chain (GHSA-vfj7-8cjw-p6xm) from `apps/web` by
removing `eslint-config-next` and replacing the ESLint config with an admitted flat
config; restore a meaningful `npm run lint`. Producer = frontend-engineer, isolated
worktree, branch `producer/M0-T180` off contract head
`daaf891e6cddf052ca3e17fa097cb574805fd4ca`.

Per-package registry/age/advisory/integrity evidence: `M0-T180-registry-research.md`.

## Files changed (scope = 4 allowed files)

1. `apps/web/package.json` — devDependencies only (see below). Nothing else changed:
   `dependencies`, `scripts`, `overrides` (postcss, sharp, brace-expansion, js-yaml,
   nanoid, baseline-browser-mapping, browserslist) are byte-identical.
2. `apps/web/eslint.config.mjs` — rewritten as native flat config (no FlatCompat).
3. `project-control/reports/M0-T180-registry-research.md` — replaced placeholder.
4. `project-control/reports/M0-T180-producer-report.md` — this file.

`apps/web/package-lock.json` is **NOT** touched by the producer (thin-client rule); the
generate-lockfile workflow bot regenerates it after the producer commit is integrated.
No file under `apps/web/src`, `apps/web/e2e`, `apps/web/scripts`, `.github`, `services`,
`packages`, `tools`, `docs`, or other `project-control` paths was touched.

### devDependencies delta

REMOVED: `@eslint/eslintrc` 3.3.6 (FlatCompat, no longer used);
`eslint-config-next` 15.5.21 (sole path to the braces chain).
ADDED (exact-pinned): `@eslint/js` 9.39.5; `eslint-plugin-react-hooks` 7.1.1;
`globals` 17.12.0; `typescript-eslint` 8.70.1.
Unchanged kept: `@playwright/test` 1.61.1, `@testing-library/dom` 10.4.1,
`@testing-library/jest-dom` 6.9.1, `@testing-library/react` 16.3.2, `@types/node`
22.20.1, `@types/react` 19.2.17, `@types/react-dom` 19.2.3, `@vitejs/plugin-react`
4.7.0, `eslint` 9.39.5, `jsdom` 26.1.0, `typescript` 5.9.3, `vitest` 4.1.11.

## Before → after dependency chain

BEFORE (dev): `eslint-config-next 15.5.21`
→ `@next/eslint-plugin-next 15.5.21` → `fast-glob 3.3.1` → `micromatch 4.0.8`
→ **`braces 3.0.3`** (GHSA-vfj7-8cjw-p6xm, high, no patch). `eslint-config-next` also
pulled `@rushstack/eslint-patch`, `eslint-import-resolver-node`,
`eslint-import-resolver-typescript`, `eslint-plugin-import`, `eslint-plugin-jsx-a11y`,
`eslint-plugin-react@^7`, `eslint-plugin-react-hooks@^5`, `@typescript-eslint/*`.

AFTER (dev): direct `@eslint/js 9.39.5` (0 deps); `typescript-eslint 8.70.1`
→ `@typescript-eslint/{utils,parser,eslint-plugin,typescript-estree}@8.70.1`
→ `typescript-estree` uses **`tinyglobby`** + **`minimatch@^10`** (NOT
fast-glob/micromatch/braces); `eslint-plugin-react-hooks 7.1.1`
→ `@babel/core`, `@babel/parser`, `hermes-parser`, `zod`, `zod-validation-error`
(no micromatch/braces/fast-glob/glob); `globals 17.12.0` (0 deps). The
fast-glob→micromatch→braces chain is gone; the only `glob`-family resolver now present
is `minimatch@^10`, which is not the advisory-affected `braces`/`glob<10.5`.

## Old → new rule-set mapping

Former `eslint-config-next` config (verified from the published 15.5.21 `index.js`,
`core-web-vitals.js`, `typescript.js`):

| former source | what it enabled | new coverage |
|---|---|---|
| `next/core-web-vitals` → `plugin:react-hooks/recommended` (react-hooks ^5) | `react-hooks/rules-of-hooks` (error), `react-hooks/exhaustive-deps` (warn) | **PRESERVED** — eslint-plugin-react-hooks 7.1.1, exactly these two rules |
| `next/typescript` → `plugin:@typescript-eslint/recommended` + overrides (`no-unused-vars`=warn, `no-unused-expressions`=warn) | `@typescript-eslint/recommended` correctness rules (no-explicit-any error, no-empty-object-type error, no-unsafe-function-type error, ban-ts-comment error, no-require-imports error, ...); unused-vars/expressions downgraded to warn | **PRESERVED** — typescript-eslint 8.70.1 `recommended`, with the SAME two severities re-applied as warn (see below) |
| (none — next never extended `eslint:recommended`) | — | **ADDED** — `@eslint/js` recommended core correctness rules (new coverage; see S3) |
| `next/core-web-vitals` → `plugin:react/recommended` + `plugin:@next/next/*` + `eslint-plugin-import` + `eslint-plugin-jsx-a11y` | react/*, @next/next/*, import/*, jsx-a11y/* rules | **LOST** (accepted, recorded below) |

### Rules intentionally NOT re-enabled (accepted, recorded loss)

Removing `eslint-config-next` drops the Next/React/import/a11y plugin rules. None is a
correctness gate that CI type-check/build/tests already cover, and re-adding those
plugins would enlarge the G5 provenance surface and (for `@next/eslint-plugin-next`)
reintroduce the fast-glob→braces chain. Lost rules include:

- `@next/next/*`: e.g. `@next/next/no-img-element` (warn), `@next/next/no-html-link-for-pages`,
  `@next/next/no-sync-scripts`, `@next/next/google-font-display`, etc. — Next best-practice
  lints. (`@next/eslint-plugin-next` is the advisory carrier; it cannot be re-added.)
- `eslint-plugin-react` recommended + next overrides: `react/jsx-key`,
  `react/no-children-prop`, `react/no-unescaped-entities`, `react/display-name`, etc.
  (next explicitly turned OFF `react/react-in-jsx-scope`, `react/prop-types`,
  `react/no-unknown-property`, `react/jsx-no-target-blank`).
- `eslint-plugin-jsx-a11y`: `jsx-a11y/alt-text` (warn), `aria-props`, `aria-proptypes`,
  `role-has-required-aria-props`, `role-supports-aria-props` (all warn in next's config).
- `eslint-plugin-import`: `import/no-anonymous-default-export` (warn) + import resolvers.

None of these were ERRORS in the former config except where `plugin:react/recommended`
set them; TypeScript + the typecheck job cover the type-level subset. This loss is an
accepted, recorded consequence of removing the advisory carrier (approved scope: remove
the chain and keep lint meaningful). If the orchestrator later wants the a11y/react/next
lints back, that is a separate admitted-package decision (each would need its own G5 and
must not reintroduce `@next/eslint-plugin-next`).

## no-undef / globals consideration

`npm run lint` = `eslint .`. With the SAME six global ignores (`node_modules/**`,
`.next/**`, `out/**`, `next-env.d.ts`, `playwright-report/**`, `test-results/**`),
`eslint .` lints: all `src/**` TS/TSX, all `e2e/**` TS, and the non-TS/root files
`eslint.config.mjs`, `scripts/dependency_age_gate.mjs`,
`scripts/tests/dependency_age_gate.test.mjs`, and the TS config files
(`next.config.ts`, `playwright.config.ts`, `vitest.config.ts`, `vitest.setup.ts`).

- TS/TSX/MTS/CTS files: core `no-undef` is turned OFF by typescript-eslint's bundled
  `eslint-recommended` compat layer (verified in `eslint-recommended-raw.js`: scopes to
  `**/*.{ts,tsx,mts,cts}` and sets `no-undef: 'off'`, plus `no-redeclare`,
  `no-unreachable`, `no-dupe-*`, etc.). So TS files need no `globals`.
- Plain `.js/.mjs/.cjs` first-party files: core `no-undef` IS active (via @eslint/js
  recommended). To prevent false positives on Node/browser globals the tooling scripts
  use, the `**/*.{js,mjs,cjs}` config block sets
  `languageOptions.globals = { ...globals.node, ...globals.browser }`, mirroring the
  former `env: { browser: true, node: true }`. Verified `globals.node` includes
  `console`, `process`, `URL`, `fetch`, `setTimeout`, `Buffer`. The age-gate script
  imports its Node APIs explicitly (`node:fs`, `node:https`, `node:process`,
  `node:timers/promises`, `node:url`) and all five imports are used (readFileSync×2,
  https×5, process×11, sleep×2, fileURLToPath×2), so `no-unused-vars` and `no-undef`
  have low risk there.

### Vendored minified bundles (`public/maplibre/6.7.0/*.mjs`)

`eslint .` also walks `public/` (not in the global ignores). The two maplibre `.mjs`
files are minified third-party bundles (492 KB / 19 KB, 5 lines each). The FORMER config
left them unflagged only because it never enabled `eslint:recommended`; `@eslint/js`
recommended WOULD flag minified code (no-cond-assign, no-empty, no-control-regex,
no-undef on worker globals, ...). To preserve behavior WITHOUT changing the global
`ignores` list, each rule-bearing config block carries a per-object `ignores:
["public/**"]`. Result: `public/maplibre/*.mjs` match no rule-bearing object and lint
with zero active rules → zero problems, exactly as before. This is a per-object scope
exclusion, not an addition to the global `ignores` block (which is byte-identical: same
six entries).

## S3 — lint equivalence / new-rule risk assessment (NO src edits)

Two preserved rule sets match prior behavior (react-hooks two rules; typescript-eslint
recommended with the same `no-unused-vars`/`no-unused-expressions` = warn overrides next
used — so unused vars that the old config tolerated as warnings are still only warnings,
not newly-failing errors). `npm run lint` is `eslint .` with no `--max-warnings`, so
warnings do NOT fail CI; only errors do.

The genuinely NEW surface is **`@eslint/js` recommended** (next never enabled
`eslint:recommended`). I could not run eslint (thin client), so I grepped the linted
files for the core rules most likely to fire. Findings:

CONFIRMED new ERRORS (CI will prove; I did NOT edit src and did NOT disable the rule):
- `no-control-regex` at **`src/lib/architect/source-links.ts:3`** — regex literal
  `/[\u0000- \u007f\\]/` (intentional control-char rejection of a URL).
- `no-control-regex` at **`src/lib/address-search.ts:56`** — regex literal
  `/[\u0000-\u001f\u007f]/.test(value)` (intentional control-char rejection).
Both are legitimate input-sanitization regexes; `no-control-regex` flags the control-char
ranges. Per S3 I did not touch them. Suggested bounded correction (orchestrator's call,
separate from this packet): an inline `// eslint-disable-next-line no-control-regex --
intentional control-character rejection` at each site (a src edit outside this task's
scope). Control-char ESCAPES elsewhere are in STRING literals, not regexes, and are NOT
flagged: `src/lib/__tests__/condo-study-identity.test.ts:50,69,74`,
`src/lib/__tests__/api.test.ts:159`.

CHECKED and CLEAR (no hits in src):
- `no-empty`: 0 empty `catch` blocks and 0 real empty control blocks (the 55 `catch {`
  sites all have bodies; empty arrow-function bodies `=> {}` are not flagged by no-empty).
- `no-prototype-builtins` (`.hasOwnProperty(`): 0.
- `no-constant-condition`: 0 `while(true)`; the two `for (;;)` loops are not flagged
  (no test expression).
- `no-case-declarations`: 0 `case ...: const/let` without a block (313 case labels, none
  with an immediate lexical declaration).
- `no-debugger`: 0. `no-useless-escape`: the regex `\/` escapes (source-links.ts:9) are
  inside `/.../ ` literals where `\/` is required → not flagged.

RESIDUAL (could not be fully proven by grep; CI is the arbiter): `no-misleading-character-class`,
`no-empty-character-class`, `no-regex-spaces`, `no-irregular-whitespace`, `no-sparse-arrays`,
`no-unexpected-multiline`, `no-fallthrough` in the 40 switch statements. I judge these low
risk for this codebase but cannot prove green without running eslint.

Honest conclusion: the web `lint` job is likely RED on the two `no-control-regex`
findings until the orchestrator applies a bounded correction. These are a lint-rule-scope
consequence of the REQUIRED `@eslint/js` recommended, NOT dependency-security issues; the
dependency-security repair (S1/S2/S4/S5-audit/S7) stands independently. Per S3 the
orchestrator handles the lint fallout as a separate bounded correction.

### Why react-hooks is only the two classic rules (installed-shape finding)

eslint-plugin-react-hooks 7.1.1's `configs.flat.recommended` is NOT just rules-of-hooks +
exhaustive-deps. Verified from the compiled plugin: `configs.flat.recommended.rules =
{ ...basicRuleConfigs, ...recommendedCompilerRuleConfigs }`, where `basicRuleConfigs =
{ 'react-hooks/rules-of-hooks':'error', 'react-hooks/exhaustive-deps':'warn' }` and
`recommendedCompilerRuleConfigs` are the React-Compiler rules whose `preset ===
Recommended` — namely `config`, `set-state-in-effect`, `error-boundaries`, `gating`,
`globals`, `immutability`, `preserve-manual-memoization`, `purity`, `refs`,
`set-state-in-render`, `static-components`, `use-memo` (all **error**),
`unsupported-syntax`/`incompatible-library` (warn). The prior config used
react-hooks ^5, whose recommended is ONLY the two classic rules. Enabling the 7.x
compiler rules as errors on a codebase not written under them (e.g. `set-state-in-effect`
fires on the common setState-in-useEffect pattern) would produce a large RED baseline and
demand extensive src rework — the opposite of "restore the green baseline / zero src
edits". The task defines react-hooks recommended as exactly `(rules-of-hooks: error,
exhaustive-deps: warn)`; the config enables exactly those two via the plugin, matching
both the task definition and prior behavior. This is documented in the config header.

## Self-checks (direct exit codes)

- `python3 -c "import json;json.load(open('apps/web/package.json'))"` → `JSON_EXIT=0`
- `python3 scripts/lanes/check_lane_paths.py` → `LANE_EXIT=0`
  (output: "LANE PATH CHECK SKIPPED: 'producer/M0-T180' is not a lane-<x>/ branch." —
  informational. `apps/web/package.json` is a Lane C hot file, but this is an
  orchestrator-contracted ledger task; reported, not "fixed".)
- `python tools/modularity_check.py --check` → `MODULARITY_EXIT=0`
  (676 files selected, 0 failures, 29 pre-existing warnings; none for the two edited
  files.)
- `git diff --stat HEAD` (HEAD = contract head daaf891e) → only
  `apps/web/eslint.config.mjs` and `apps/web/package.json` differ; `git status --short`
  shows exactly ` M apps/web/eslint.config.mjs` and ` M apps/web/package.json` before the
  two reports were written.

I did NOT run npm, npx, or node anywhere (thin-client rule). All registry facts came from
`curl`/`gh api`/`unpkg`.

## Explicit statement

**No file under `apps/web/src` changed.** (Nor under `apps/web/e2e`,
`apps/web/scripts`, `.github`, `services`, `packages`, `tools`, `docs`, or other
`project-control` paths.)

## S1–S7 status (what the producer proved vs what CI/workflow must prove)

- **S1 chain_removed** — PROVEN at the package.json level: `eslint-config-next` removed
  from devDependencies. Lock-level proof (no `node_modules/braces`, `/micromatch`,
  `/fast-glob`, `/@next/eslint-plugin-next`, `/eslint-config-next` entries) must be
  confirmed by a lock parse of the BOT-regenerated `package-lock.json` (producer cannot
  generate the lock). The removed chain and the tinyglobby+minimatch replacement are
  documented.
- **S2 replacement_admitted** — PROVEN at research time for every added direct dep and
  the @typescript-eslint sub-tree (exact pin, ≥604800 s, advisory EMPTY, integrity
  recorded). The committed-lock age gate over the FULL regenerated tree (incl. the
  react-hooks @babel/hermes/zod sub-tree) is the executable authority in the workflow.
- **S3 lint_equivalence_no_src_edits** — PRESERVED for react-hooks + typescript-eslint
  (with matching severities). Two confirmed new `no-control-regex` errors reported above;
  NO src edited, NO rule disabled. CI web `lint` job is the arbiter.
- **S4 workflow_proven_lock** — NOT run by the producer (thin client). The orchestrator
  dispatches generate-lockfile; its run id + bot commit sha are the evidence.
- **S5 ci_green_on_final_head** — to be proven by ci.yml on the post-lock head
  (`web-dependency-security` audit step that failed on run 37089049103 must pass; `web`
  lint subject to the S3 finding above).
- **S6 no_scope_creep** — PROVEN: `dependencies`, `scripts`, `overrides` unchanged; only
  the 4 devDependency lines changed (2 removed, 4 added). Runtime deps untouched.
- **S7 fail_closed** — an admitted replacement set EXISTS (above), so NOT blocked. No
  waiver, no `--omit=dev`, no audit-level change, no npm-audit ignore, no fork override
  anywhere.

## Next step for the orchestrator

1. Cherry-pick the producer commit (`producer/M0-T180`, sha in the producer return) onto
   `task/M0-T180-web-lint-chain-braces`; verify sha256 of the 4 files with LF
   normalization (see return).
2. Dispatch `.github/workflows/generate-lockfile.yml` (workflow_dispatch) on
   `task/M0-T180-web-lint-chain-braces`. It regenerates `apps/web/package-lock.json`,
   PROVES it (npm ci + blocking audit + JSON-total-0 + committed-lock age gate + npm-CLI
   advisory) and the bot commits the lock. Record the run id + bot commit sha.
3. Because bot lock pushes do not trigger CI (M5-T021 note), push an EMPTY follow-up
   commit to run ci.yml on the post-lock head. Confirm `web` (lint+typecheck+build),
   `web-e2e`, `web-dependency-security` status.
4. If `web` lint is RED only on the two `no-control-regex` findings, apply the bounded
   correction (inline eslint-disable-next-line with justification at
   `src/lib/architect/source-links.ts:3` and `src/lib/address-search.ts:56`) as a
   separate scoped change — a src edit outside this packet.
5. Resolve B-028 in the acceptance seam once `web-dependency-security` is green.
