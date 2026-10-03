# M0-T180 — registry research (dependency-security evidence)

Producer: frontend-engineer (isolated worktree, branch `producer/M0-T180`).
All facts gathered WITHOUT running npm/npx/node (thin-client rule). Sources:
`curl -s https://registry.npmjs.org/<pkg>/<ver>` (version manifest: `dist.integrity`,
`dependencies`), `curl -s https://registry.npmjs.org/<pkg>` (`.time[<ver>]` publish
timestamp), `gh api -X GET /advisories -f ecosystem=npm -f affects="<pkg>@<ver>"`
(advisory query), and `https://unpkg.com/<pkg>@<ver>/...` (package shapes).

## Research clock

- Research `NOW` (epoch, UTC): **1790999064** = 2026-10-03T03:44:24Z (`date -u +%s`).
- 7-day admission threshold = NOW − 604800 = **1790394264** = 2026-09-26T03:44:24Z.
  A version PASSES iff its registry publish epoch ≤ threshold (age ≥ 604800 s).
- Ages below only GROW by the time the generate-lockfile bot resolves + commits the
  lock; the committed-lockfile release-age gate in the workflow is the executable
  authority over the FULL regenerated tree (direct AND transitive).

## Root cause (verified, not re-derived)

`gh api -X GET /advisories -f ecosystem=npm -f affects="braces@3.0.3"` →
**GHSA-vfj7-8cjw-p6xm**, severity **high**, **first_patched_version = null** (no fix):
"braces vulnerable to stack-exhaustion denial of service through deeply nested patterns".
The lock's only path to `braces@3.0.3` is the dev chain
`eslint-config-next 15.5.21 → @next/eslint-plugin-next 15.5.21 → fast-glob 3.3.1 →
micromatch 4.0.8 → braces 3.0.3`. Confirmed from `eslint-config-next@15.5.21`
package.json (dependency `@next/eslint-plugin-next: 15.5.21`). Every 15.x/16.x
`@next/eslint-plugin-next` pins fast-glob 3.3.1; the 14.2.35 downgrade carries
glob 10.3.10 (GHSA-5j98-mcp5-4vw2). Neither an upgrade nor a downgrade is admissible,
so `eslint-config-next` is REMOVED and the flat config is replaced.

## REMOVED packages (direct devDependencies)

| package | prev version | why removed |
|---|---|---|
| `eslint-config-next` | 15.5.21 | sole path to the braces advisory chain (above); no admissible version exists. Removing it also drops its transitives `@next/eslint-plugin-next`, `@rushstack/eslint-patch`, `eslint-import-resolver-node`, `eslint-import-resolver-typescript`, `eslint-plugin-import`, `eslint-plugin-jsx-a11y`, `eslint-plugin-react@^7`, `eslint-plugin-react-hooks@^5`, and the fast-glob→micromatch→braces chain. |
| `@eslint/eslintrc` | 3.3.6 | provided `FlatCompat`, used ONLY to load the eslintrc-style `next/*` presets. The new config is native flat config; FlatCompat is no longer imported, so this dep is no longer needed. |

## ADMITTED packages (added direct devDependencies)

Advisory query for every row returned `EMPTY` (no advisories) — command shown per row.
Integrity = the registry `dist.integrity` (sha512) of the admitted version.

### `@eslint/js` 9.39.5
- publish: 2026-07-10T20:16:17.272Z | epoch 1783714577 | age 7284487 s → **PASS** (≥604800)
- integrity: `sha512-QywQuszQh77pIXCsq998c8hbhSTI/azTty1Z6N53dmAudKHhy573j3yvRLsX2BSp8YpLtoCEG8E9DJe+8zUh4A==`
- dependencies: none (`"dependencies": null`)
- advisory: `gh api -X GET /advisories -f ecosystem=npm -f affects="@eslint/js@9.39.5"` → EMPTY
- rationale: core `eslint:recommended` rule set; version matches the already-pinned
  `eslint` 9.39.5 (released together). Zero transitives → no chain risk.

### `typescript-eslint` 8.70.1 (meta package)
- publish: 2026-09-21T17:07:55.524Z | epoch 1790010475 | age 988589 s → **PASS**
- integrity: `sha512-AcWG7KDjZ2THNXsgwttMaGmzVi0VFRlFYfqFHYQRbDpF3owuYbuiL8c7UUrd2k8s3PoSfIQrWfrGXfcElrWLYA==`
- dependencies (all 8.70.1): `@typescript-eslint/utils`, `@typescript-eslint/parser`,
  `@typescript-eslint/eslint-plugin`, `@typescript-eslint/typescript-estree`
- peer: `eslint ^8.57.0 || ^9.0.0 || ^10.0.0` (satisfied by eslint 9.39.5),
  `typescript >=4.8.4 <6.1.0` (satisfied by typescript 5.9.3)
- advisory: `...affects="typescript-eslint@8.70.1"` → EMPTY
- rejected: 8.71.0 (publish 2026-09-28; age < 604800 at research time → TOO YOUNG).

### `eslint-plugin-react-hooks` 7.1.1
- publish: 2026-04-17T18:03:19.591Z | epoch 1776448999 | age 14550065 s → **PASS**
- integrity: `sha512-f2I7Gw6JbvCexzIInuSbZpfdQ44D7iqdWX01FKLvrPgqxoE7oMj8clOfto8U6vYiz4yd5oKu39rRSVOe1zRu0g==`
- direct dependencies: `zod ^3.25.0 || ^4.0.0`, `@babel/core ^7.24.4`,
  `@babel/parser ^7.24.4`, `hermes-parser ^0.25.1`, `zod-validation-error ^3.5.0 || ^4.0.0`
- peer: `eslint ... || ^9.0.0 || ^10.0.0` (satisfied)
- advisory: `...affects="eslint-plugin-react-hooks@7.1.1"` → EMPTY
- note: this package pulls the largest transitive sub-tree (the @babel toolchain +
  hermes-parser + zod). None of those is micromatch/braces/fast-glob/glob. Their exact
  resolved versions come from the regenerated lock and are gated by the workflow's
  committed-lock age gate + blocking audit (the executable authority). See risks.

### `globals` 17.12.0
- publish: 2026-09-01T11:00:43.545Z | epoch 1788260443 | age 2738621 s → **PASS**
- integrity: `sha512-cezEd/DTyyht9cvSSURyygXPfy04GtWO/5e6ZPvH7fCtjKz9PYOmuawphw1Ctd1f6C+5JypXfGD7ahNMXvevBA==`
- dependencies: none; keys `node`, `browser`, `nodeBuiltin` present (verified
  `globals.json`: `.node` includes console/process/URL/fetch/setTimeout/Buffer).
- advisory: `...affects="globals@17.12.0"` → EMPTY
- rejected: 17.13.0 (TOO YOUNG). Needed ONLY to supply Node/browser globals to core
  `no-undef` on the plain `.mjs` tooling files (`eslint.config.mjs`, `scripts/*.mjs`),
  which @eslint/js recommended now lints (previously the chain never enabled no-undef).

## KEPT packages (unchanged; relevant to lint)

- `eslint` 9.39.5 (unchanged) — peer-compatible with every admitted package above.
- `typescript` 5.9.3 (unchanged) — within typescript-eslint's `>=4.8.4 <6.1.0` peer.
- `@vitejs/plugin-react`, `@testing-library/*`, `@types/*`, `jsdom`, `vitest`,
  `@playwright/test` — unchanged. `next`, `react`, `react-dom`, `three`, `maplibre-gl`,
  `@react-three/fiber` (runtime deps) and the `overrides` block — UNCHANGED (S6).

## Transitive verification — no reintroduction of micromatch/braces/fast-glob/glob<10.5

The @typescript-eslint 8.70.1 sub-tree (verified via each sub-package's version manifest):

| sub-package @8.70.1 | publish (UTC) | age s | integrity (sha512) |
|---|---|---|---|
| typescript-estree | 2026-09-21T17:07:19Z | 988625 | `sha512-TU8PwyGN0PQJUcE96mw8eCQ44SmxGdQlJmlWakHaHQ15eIuuvye5yNtmh/i6oS88jzXVQB71xdNkbkB/fMwL0g==` |
| utils | 2026-09-21T17:07:54Z | 988590 | `sha512-Esgul8MsnKnRLdYU2Eb2cRV9bS5HJYtKj1ByJnOzzG2M58DGdSUQ1jUuILxipqcpB2h9WLrbD5GijIWUjX/Tqw==` |
| type-utils | 2026-09-21T17:07:39Z | 988605 | `sha512-7zKTnyvaVWqzLZHPFQtX1hVHqgkMC+WebPWakNCSyrQVbIP1AM0L0TlBZtACldIRb6PptI8Odk+jyZ5kP3B1VA==` |
| scope-manager | 2026-09-21T17:07:45Z | 988599 | `sha512-Pa0EeSeAusQc1WbjQMac+YfenewYTBu0KjgYvkUKwhXaHUKbFog23Dm/rp0DX/6tyYOQ3Xl1a+3EcFNZynGHCw==` |
| types | 2026-09-21T17:07:05Z | 988639 | `sha512-Dm1ypdhhrGCTyyehxElhgJ6kgk8MVCv5qXdoOVqPr1uqk42jX8KjrZqhROvdShczA8qrDoYiOWn1ykWlx2k81Q==` |
| visitor-keys | 2026-09-21T17:08:54Z | 988530 | `sha512-Vwj9lUIW5Xq3wQ9w6gv3R86g1hMK8f2zNOdGTAgeXUMMXFK78G9ruCjjqutHMNJc0+CH7LYRnHeUB9IT8wFmcw==` |
| tsconfig-utils | 2026-09-21T17:07:23Z | 988621 | `sha512-jumze1fPI+sDOaM2TWGQdn39PDxTr7TZGeuyLkAbNyx2vtMT3uRnVKChN0hfht5V2TugphJzF6bYXvBcE09qqg==` |
| project-service | 2026-09-21T17:07:09Z | 988635 | `sha512-62xOgboPfwc3/IgPSX/W6oQR3ZbF04194FPGUGH8HL8iLFHbt/456/8Ph1wLNUgVF+s94FlHoipBsz+v7+LMnA==` |

Dependency chains inspected (version manifests):
- `typescript-estree@8.70.1` deps: `debug ^4.4.3`, `semver ^7.7.3`, **`minimatch ^10.2.2`**,
  **`tinyglobby ^0.2.15`**, `ts-api-utils ^2.5.0`, `@typescript-eslint/types|visitor-keys|
  tsconfig-utils|project-service` — i.e. tinyglobby (fdir + picomatch) + minimatch@^10,
  **NOT** micromatch/braces/fast-glob. No reintroduction of the advisory chain.
- `@typescript-eslint/eslint-plugin@8.70.1` deps: `ignore ^7.0.5`, `ts-api-utils`,
  `natural-compare`, `@typescript-eslint/utils`, `@eslint-community/regexpp`,
  `@typescript-eslint/type-utils|visitor-keys|scope-manager` — uses `ignore`, not micromatch.
- `@typescript-eslint/parser@8.70.1` deps: `debug`, `@typescript-eslint/types|visitor-keys|
  scope-manager|typescript-estree` — no glob library of its own.

The complete regenerated tree (including the eslint-plugin-react-hooks @babel/hermes/zod
sub-tree) is re-verified end-to-end by the generate-lockfile workflow and the
`web-dependency-security` CI job: `npm ci` integrity, blocking `npm audit`
(`--audit-level=low`, dev included) AND JSON total == 0, `dependency_age_gate.mjs`
(every registry entry resolves to registry.npmjs.org, integrity matches, ≥604800 s old),
and the npm-CLI advisory check — all fail-closed. No waiver, no `--omit=dev`, no
audit-level change, no override pointing braces/micromatch at a fork.

## Rejected alternatives (summary)

- Upgrade/downgrade `eslint-config-next` / `@next/eslint-plugin-next`: every 15.x/16.x
  pins fast-glob 3.3.1 (→ braces 3.0.3); 14.2.35 carries glob 10.3.10
  (GHSA-5j98-mcp5-4vw2). No admissible version. → remove the package.
- `braces`/`micromatch` override to a non-fixed or fork version: forbidden (S7); braces
  has `first_patched_version = null`, so no fixed version exists to pin to.
- typescript-eslint 8.71.0, globals 17.13.0: TOO YOUNG (< 7 complete days at research).
- `eslint-plugin-react` (next had `eslint-plugin-react@^7`): NOT added — no concrete
  codebase-relied-upon rule could be demonstrated without running eslint, and fewer new
  packages = smaller G5 provenance surface. The react rules next enabled are recorded as
  an accepted loss in the producer report.
