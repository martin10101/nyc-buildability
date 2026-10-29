# M0-T199 producer report — web lock advisory repair (B-032 web half)

Producer: frontend-engineer. Rounds: round 1 moved the `apps/web/package.json` pins + overrides and
wrote the registry research; the orchestrator pushed that commit, dispatched the
`generate-lockfile` workflow on `task/wave29-scenario-drawings`, and pulled the bot's lock commit.
**Round 2 (this report)** compares the base lock with the workflow-regenerated lock entry by entry,
classifies every change, and records the on-server functional check. No `npm install` was run to
produce the lock — the generate-lockfile workflow is its only writer (D-009-R017). This task does
not edit `apps/web/package.json` or `apps/web/package-lock.json`.

## Headline

- **The regenerated lock is fully explained.** 397 → 395 nodes; **76 changed entries** (75 version
  moves + the root `""` node), **3 added**, **5 removed**. Every version move is classified
  **FORCED (20)** / **FORCED by a re-resolved parent's exact pin (51)** / **RE-RESOLVED (4)**; the 3
  added and 5 removed nodes are the fdir/picomatch hoist plus the one new name. Nothing is
  unexplained; nothing resolves anywhere but `registry.npmjs.org`; all 78 moved+added entries are
  integrity-matched to the registry and ≥ 604800 s old; all new versions are advisory-free.
- **Provenance verdict on the one new name (`@napi-rs/lzma-linux-x64-gnu@1.5.1`): admit.** It is a
  prebuilt linux-x64-glibc LZMA native addon from the napi-rs project (`github.com/Brooooooklyn/lzma`),
  MIT, ~105 days old, integrity-matched, advisory-free, **published via GitHub Actions OIDC trusted
  publishing with an SLSA v1 provenance attestation + registry signatures**, and has **no lifecycle
  scripts**. It entered the tree only because rollup re-resolved (4.62.2 → 4.64.10) and rollup declares
  it in `optionalDependencies` as a *build-time* cross-compile aid (rollup's own package.json comment,
  ref #6461 / the 4.62.4 glibc-compat fix); rollup's runtime loader (`native.js`) never `require()`s
  it, so nothing in our `vite build` / `vitest` path executes or loads it.
- **Functional check on this Linux server (exit codes):** `npm ci` **0** (311 packages), `npm run
  lint` **0** (2 pre-existing warnings, unrelated), `npm run typecheck` **0**, `vitest run` **0**
  (134 files / 2767 tests passed).

## Files changed by this task

- `project-control/reports/M0-T199-producer-report.md` — this report (replaces the placeholder).
- `project-control/reports/M0-T199-registry-research.md` — a round-2 section appended (round 1 kept verbatim).
- `apps/web/package.json` — changed in **round 1** (commit `03052939`), not here. The four changes
  (next 15.5.27→15.5.28, vitest 4.1.11→4.1.12, overrides +vite 7.3.7 +zod 4.6.6) remain exactly as
  round 1 left them; no package.json change in round 2.
- `apps/web/package-lock.json` — written by the **generate-lockfile workflow** bot commit
  `989e7ac0` (author `github-actions[bot]`), not by this task.

## Lock comparison — base `03052939` vs regenerated `989e7ac0` (entry by entry)

Method: both `packages` maps read straight from the git objects (`git show <sha>:apps/web/package-lock.json`),
compared key by key in Python — no install. lockfileVersion 3 both sides.

- base lock blob `f2c107923913be5d6d300b9b2e18cee09ea418a5`; new lock blob
  `14e9f52e61ffda9a71a9de6f258d713e5501d159` (= the file analysed, `git hash-object` equal).
- packages: **397 → 395**. Changed **76** (75 version moves + root). Added **3**. Removed **5**.
- **Resolved host:** all 78 added+moved entries resolve to `registry.npmjs.org` (0 with any other host, 0 missing a resolved URL).
- **Integrity:** all 78 moved+added `integrity` values equal the registry `dist.integrity` (0 mismatches).

### FORCED — directly by this task's targeted change (20)

| package(s) | move | cause |
|---|---|---|
| `next` | 15.5.27 → 15.5.28 | root `dependencies` pin (package.json, round 1) |
| `@next/env`, `@next/swc-*` (×9: darwin-arm64/x64, linux-arm64-gnu/musl, linux-x64-gnu/musl, win32-arm64-msvc/x64-msvc) | 15.5.27 → 15.5.28 | exact pins by `next@15.5.28` (deps + optionalDeps) |
| `vitest` | 4.1.11 → 4.1.12 | root `devDependencies` pin (package.json, round 1) |
| `@vitest/expect`, `@vitest/mocker`, `@vitest/pretty-format`, `@vitest/runner`, `@vitest/snapshot`, `@vitest/spy`, `@vitest/utils` (×7) | 4.1.11 → 4.1.12 | exact pins by `vitest@4.1.12` |
| `vite` | 7.3.6 → 7.3.7 | `overrides.vite` pin (package.json, round 1) |
| `zod` | 4.6.5 → 4.6.6 | `overrides.zod` pin (package.json, round 1) |

### FORCED — by a re-resolved parent's exact optional pin (51)

The old platform binary no longer satisfies the new exact pin, so it is forced; the *parent* that
sets that pin was itself re-resolved (next row).

| package(s) | move | cause |
|---|---|---|
| `@esbuild/*` (×26, all platforms) | 0.28.1 → 0.28.2 | exact pin by `esbuild@0.28.2` `optionalDependencies` (parent `esbuild` RE-RESOLVED under `vite`) |
| `@rollup/rollup-*` (×25, all platforms) | 4.62.2 → 4.64.10 | exact pin by `rollup@4.64.10` `optionalDependencies` (parent `rollup` RE-RESOLVED under `vite`) |

### RE-RESOLVED — old version still satisfied every requiring range; npm recomputed the replaced subtree (4)

| package | move | parent replaced → range the old version still satisfied |
|---|---|---|
| `esbuild` | 0.28.1 → 0.28.2 | `vite` (`esbuild: ^0.27.0 \|\| ^0.28.0`; 0.28.1 satisfied) |
| `rollup` | 4.62.2 → 4.64.10 | `vite` (`rollup: ^4.43.0`; 4.62.2 satisfied) |
| `chai` | 6.2.2 → 6.3.0 | `@vitest/expect` (`chai: ^6.2.2`; 6.2.2 satisfied) |
| `tinyrainbow` | 3.1.1 → 3.2.0 | `vitest` + `@vitest/expect`/`pretty-format`/`utils` (`tinyrainbow: ^3.1.0`; 3.1.1 satisfied) |

npm regenerates the whole subtree of any replaced node, so replacing `vite` (override) and the
`vitest` family (pin) let npm pick newer-but-still-satisfying `esbuild`/`rollup`/`chai`/`tinyrainbow`.
None was required to move by a range; each is a satisfied re-resolution.

### ADDED (3) and REMOVED (5) — the fdir/picomatch hoist + the one new name

- **Added** `node_modules/fdir@6.5.0` and `node_modules/picomatch@4.0.7` (both top-level, `dev`):
  the regenerated tree **hoists/de-duplicates** fdir and picomatch to single top-level nodes. `fdir`
  stays `6.5.0` (pure hoist); `picomatch` moves `4.0.5 → 4.0.7` while hoisting (a satisfied
  re-resolution: `vite ^4.0.3`, `vitest ^4.0.3`, `tinyglobby ^4.0.4`, `fdir` peer `^3 || ^4` — 4.0.5
  satisfied all). `tinyglobby` (0.2.17), `postcss` (8.5.23), `fsevents` (2.3.2 / nested vite 2.3.3)
  are byte-identical between the locks.
- **Removed** the 5 nested copies the hoist replaced: `fdir@6.5.0` under `tinyglobby` and `vite`;
  `picomatch@4.0.5` under `tinyglobby`, `vite` and `vitest`.
- **Added** `node_modules/@napi-rs/lzma-linux-x64-gnu@1.5.1` (`dev`, `optional`, os linux / cpu x64 /
  libc glibc) — the one new package **name**. Cause: `rollup@4.64.10` declares it at exact `1.5.1` in
  `optionalDependencies` (first declared in rollup 4.62.4; absent in the old locked rollup 4.62.2), and
  on this platform the optional dep installs. Full G5 provenance review is in the registry-research
  round-2 section; verdict **admit**.

### Root `""` node

Only `dependencies.next` 15.5.27→15.5.28 and `devDependencies.vitest` 4.1.11→4.1.12 changed (mirroring
the package.json pins). `overrides` are not stored verbatim in the lock root node, so no other root
change. No scripts, no other field moved.

### Statement of completeness

Every one of the 76 changed entries, 3 added, and 5 removed is accounted for by the four targeted
moves and the re-resolution/hoist cascade they trigger. **No entry differs for any other reason**; no
entry resolves to a non-registry host; no integrity diverges from the registry.

## Checks (direct exit codes, this worktree, Linux dev server)

Reset: `git reset --hard 989e7ac088c7268cfbcb2aff7811338078b2bacf` (HEAD = bot lock commit; parent = round-1 pin `03052939`).

| check | command | exit | result |
|---|---|---|---|
| lane coverage | `python3 scripts/lanes/check_lane_paths.py --coverage` | 0 | LANE COVERAGE PASS |
| modularity | `python tools/modularity_check.py --check` | 0 | 0 failures (no production source touched) |
| research records | `python3 tools/research_record_check.py --check` | 0 | PASS |
| install | `npx --yes npm@11.18.0 ci --no-audit --no-fund` (apps/web) | 0 | added 311 packages; only install hook = esbuild@0.28.2 `postinstall node install.js` (allow-scripts did NOT run it); `@napi-rs/lzma` has no scripts |
| lint | `npm run lint` (apps/web) | 0 | 0 errors, 2 pre-existing warnings (unused `waitFor` / `DRIFTED_BLOCKED_OUTPUTS` in test files — not my change) |
| typecheck | `npm run typecheck` (apps/web) | 0 | clean (`tsc --noEmit`) |
| web unit tests | `flock …/heavy-run.lock npx vitest run` (apps/web) | 0 | **134 test files passed (134); 2767 tests passed (2767)** |

ruff not run: no `services/api` / Python production change. The generate-lockfile workflow (the lock's
only writer) was run by the orchestrator, not here.

## Disconfirming check (brief 3.d)

- **Lock identity (proven here, git):** the lock I analysed is byte-identical to the one the bot
  committed — `git hash-object` of the analysed file = `14e9f52e61ffda9a71a9de6f258d713e5501d159` =
  `git rev-parse 989e7ac0:apps/web/package-lock.json`. The bot commit `989e7ac0` is authored by
  `github-actions[bot]`, subject "chore(web): regenerate package-lock.json (M0-T019 security tree,
  validated)". So this analysis describes exactly the committed lock.
- **Workflow audit + age gate (run `40450612409`):** confirming "npm audit total 0 at every severity"
  and "committed-lock age gate PASS" from the workflow log requires `gh run view 40450612409 --log`.
  `gh` is reserved to the orchestrator under the ledger/integration protocol (ADR-005), so this
  producer did not run it — **requested as an orchestrator-captured evidence item.** Independent
  reconfirmation of the same facts was performed here without the workflow log: (a) `npm ci` from this
  exact lock succeeded (exit 0); (b) all 78 moved+added entries read ≥ 604800 s old from
  `registry.npmjs.org` (min 774259 s); (c) every moved/added new version returned 0 advisories from
  `api.github.com/advisories` (control `esbuild@0.24.0` → 2, so the query discriminates).

## Evidence-based view on the re-resolved moves (the reviewers'/orchestrator's call)

**Keep the regenerated lock as-is; no pin-backs.** The 4 re-resolved packages and their 51 forced
platform binaries, plus the one new name, are all advisory-free, ≥ 7 days old (min ≈ 8.96 days),
integrity-matched, and carry no changed/added install-time behaviour (esbuild's `postinstall` is
byte-identical; `@napi-rs/lzma` has no scripts and is not loaded at runtime). They are the natural
output of npm regenerating the subtrees of the replaced `vite`/`vitest` nodes. Pinning them back
would add `overrides` surface, diverge from what the generator produces, and require another workflow
run — for no security gain. This is my evidence-based view; the gate records the decision.

## Kept apart — unknowns / not checked

- **Facts:** everything in the two tables above (versions, hosts, integrity, ages, advisory counts,
  scripts, provenance) is read from `registry.npmjs.org`, `api.github.com`, the rollup repository, and
  the two lock git objects on 2026-10-27.
- **Inference:** that rollup never loads `@napi-rs/lzma` at runtime is inferred from `native.js`
  (v4.64.10) containing no lzma/napi reference + the package.json comment marking it a build-time
  cross-compile aid; I did not trace every rollup code path, only the native loader.
- **Unknown / not mine:** the browser e2e (Playwright) result and the full CI rollup on the post-lock
  head — the orchestrator reads CI (S7). The `exact-production-install` job stays red until the
  separate api-tooling repair lands (M0-T200, not this task). The workflow-log audit/age-gate
  confirmation for run `40450612409` needs orchestrator `gh` capture (above). No web behaviour is
  called verified from reasoning; the on-server `vitest` run is the functional evidence this task
  provides.
