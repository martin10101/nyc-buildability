# M0-T199 registry research — web lock advisory repair (B-032 web half)

Independent second reading by the producer (frontend-engineer), ROUND 1. Every value below was read
on the day (2026-10-27) from the official sources named — `registry.npmjs.org` and the GitHub
advisory database (`api.github.com/advisories`, which `npm audit` consumes) — not copied from the
task packet, the B-032 blocker, the orchestrator's objective figures, or agent memory.

- **Reading clocks (authoritative, UTC):** package ages use the registry's own `Date` response
  header captured at the start of the fetch: **`Tue, 27 Oct 2026 04:27:49 GMT`**
  (`registry.npmjs.org`). The advisory reads were taken at **`Tue, 27 Oct 2026 04:29:22 GMT`**
  (`api.github.com`). The policy clock is the registry's UTC clock, not the local/CI clock.
- **Source of ages:** `(registry Date header 04:27:49Z) − time["<new>"]` in whole seconds, from each
  package's `registry.npmjs.org/<pkg>` `time` map.
- **Old locked versions:** read from `apps/web/package-lock.json` (lockfileVersion 3): `next`,
  `@next/env` and the eight `@next/swc-*` are locked at `15.5.27`; `vitest`, `@vitest/expect`,
  `@vitest/mocker`, `@vitest/pretty-format`, `@vitest/runner`, `@vitest/snapshot`, `@vitest/spy`,
  `@vitest/utils` at `4.1.11`; `vite` at `7.3.6`; `zod` at `4.6.5`. `launch-editor` is **not** a
  separate lock entry — it is vendored (bundled) inside vite's published tarball, so its advisories
  reach the tree through the `vite` package, not a standalone node.

## Outcome: PROCEED (no STOP condition)

Every one of the 20 packages whose locked version changes is at least 604800 s old (youngest:
`vitest` 4.1.12 at 999,384 s ≈ 11.6 days — ~394,584 s above the floor), each from
`registry.npmjs.org` with a known `dist.integrity`, and each advisory-free at every severity for its
new version. No package NAME is new to the lock, so no §5 / D-009-R005 provenance admission is
triggered. The locked `sharp` 0.35.5 still satisfies next's new optional range. The declared pins in
`apps/web/package.json` move `next` 15.5.27 → 15.5.28 and `vitest` 4.1.11 → 4.1.12, and two exact
overrides are added: `"vite": "7.3.7"`, `"zod": "4.6.6"`. The repair needs no exception, waiver,
exclusion, `.npmrc` change or gate change. The machine gates (the workflow's `npm audit` total == 0
at every severity, the committed-lock age gate, the npm-CLI advisory check) decide at run time; if
any reports a finding or an under-age package the task STOPs (S6).

## The ten advisories (read at `api.github.com/advisories`, 04:29:22Z)

Each new version is outside its advisory's vulnerable range. `first_patched` is the advisory's own
field. `npm audit` prints `medium` as `moderate`.

| GHSA | CVE | severity | package | vulnerable range (relevant line) | first patched | published_at (GitHub DB) |
|---|---|---|---|---|---|---|
| GHSA-2464-fhr4-w9xw | (none assigned) | critical | next | `>= 10.0.0, <= 15.5.27` | 15.5.28 | 2026-10-22T15:52:53Z |
| GHSA-p3m5-59mp-jv5r | CVE-2026-94482 | high | next | `>= 13.0.0, <= 15.5.27` | 15.5.28 | 2026-10-22T15:50:34Z |
| GHSA-qxg6-89mg-rqv8 | CVE-2026-112949 | medium | @vitest/mocker | `>= 2.1.0-beta.7, < 4.1.12` | 4.1.12 | 2026-10-21T19:54:26Z |
| GHSA-xp26-3454-mjgp | CVE-2026-112950 | medium | @vitest/mocker | `>= 4.1.11, < 4.1.12` | 4.1.12 | 2026-10-21T19:48:38Z |
| GHSA-9jrq-w75r-8gcw | CVE-2026-112945 | low | vite | `>= 7.0.0, <= 7.3.6` | 7.3.7 | 2026-10-21T16:48:14Z |
| GHSA-rq7h-c2jc-7f22 | CVE-2026-112946 | medium | vite | `>= 7.0.0, <= 7.3.6` | 7.3.7 | 2026-10-21T16:47:42Z |
| GHSA-698v-4r3x-3vcv | CVE-2026-112943 | medium | launch-editor / vite | vite `>= 7.0.0, <= 7.3.6` (launch-editor `<= 2.14.1`) | vite 7.3.7 (launch-editor 2.14.2) | 2026-10-20T18:30:24Z |
| GHSA-r825-w8mm-5pxw | CVE-2026-112944 | medium | launch-editor / vite | vite `>= 7.0.0, <= 7.3.6` (launch-editor `<= 2.14.1`) | vite 7.3.7 (launch-editor 2.14.2) | 2026-10-20T19:51:52Z |
| GHSA-587h-7wmj-h5pm | CVE-2026-112942 | high | launch-editor / vite | vite `>= 7.0.0, <= 7.3.6` (launch-editor `<= 2.14.1`) | vite 7.3.7 (launch-editor 2.14.2) | 2026-10-20T19:48:25Z |
| GHSA-mrhx-c7xc-m3w5 | CVE-2023-54404 | high | zod | `< 4.6.6` | 4.6.6 | 2026-10-01T18:32:46Z (github_reviewed 2026-10-23T18:26:50Z) |

Summaries: GHSA-2464 = unauthenticated remote code execution in the Image Optimization API with SVG
files; GHSA-p3m5 = denial of service in the App Router with Server Actions; GHSA-qxg6 = code
injection via unauthenticated manual mock registration; GHSA-xp26 = Windows backslash traversal
bypassing the @vitest/mocker allowlist fix; GHSA-9jrq = cross-origin script execution via Vite custom
middleware; GHSA-rq7h = files outside `server.fs.allow` served when project paths match system paths;
the three launch-editor advisories are Windows command-execution / existence-check / `%`-escaping
flaws in launch-editor, which vite bundles; GHSA-mrhx = zod memory exhaustion validating oversized
constrained collections.

The three launch-editor advisories each list two npm packages — `launch-editor` itself (`<= 2.14.1`,
patched 2.14.2) and `vite` (`>= 7.0.0, <= 7.3.6`, patched 7.3.7). Because launch-editor is bundled
inside vite, only the `vite` line is relevant to this lock, and 7.3.7 is its fixed version.

## Disconfirming check — are the new versions clean and the oldest on-line fix?

Queried the GitHub advisory database for each new version (`GET
/advisories?ecosystem=npm&affects=<pkg>@<version>`, HTTP 200 each):

| query | result |
|---|---|
| `next@15.5.28` | `[]` — 0 advisories |
| `vitest@4.1.12` | `[]` — 0 advisories |
| `@vitest/mocker@4.1.12` | `[]` — 0 advisories |
| `vite@7.3.7` | `[]` — 0 advisories |
| `zod@4.6.6` | `[]` — 0 advisories |

Control (confirms the query discriminates): `vite@7.3.6` → 5 advisories
(GHSA-587h-7wmj-h5pm, GHSA-698v-4r3x-3vcv, GHSA-9jrq-w75r-8gcw, GHSA-r825-w8mm-5pxw,
GHSA-rq7h-c2jc-7f22). So moving vite 7.3.6 → 7.3.7 clears exactly the five vite-line advisories, and
7.3.7 carries none.

**Oldest fix on each line.** 15.5.28, 4.1.12, 7.3.7, 4.6.6 are each the immediate next patch release
after the last vulnerable version, and each advisory's own `first_patched` names exactly that version
on the relevant major line — so each is the oldest advisory-free version on its line (no intermediate
patch exists between the last vulnerable and the fix).

**Not inside any other advisory's range.** The `affects=<pkg>@<new>` queries returning `[]` prove none
of the four new versions sits inside any other advisory's range. One extra launch-editor advisory,
GHSA-v6wh-96g9-6wx3 (medium, NTLMv2 hash disclosure via UNC paths on Windows), surfaced in a
`launch-editor@*` probe; its vite line is `>= 7.0.0, <= 7.3.4` (patched 7.3.5), so it never affected
the locked 7.3.6 and does not affect 7.3.7. No STOP condition found.

## The 20 packages whose locked version changes

Ages computed against the registry Date header `04:27:49Z`. Every age ≥ 604800 s.

### next family (10 packages): 15.5.27 → 15.5.28

| package | published 15.5.28 (UTC) | age at reading (s) | ≥604800 | dist.integrity (registry) |
|---|---|---|---|---|
| next | 2026-10-14T17:36:08.917Z | 1075900 | yes | `sha512-JjhLBBY1PNnuwPtcZ7t8yxVeJVYvD2Jyp633J+gRCNbzSt7N0E+xqCf6uQiff3+3qmUkwcF/ksfSsK1xsZ76Tw==` |
| @next/env | 2026-10-14T17:31:22.465Z | 1076186 | yes | `sha512-xxW5EBI8fMPuVTPBW7LL980IRbuDXlbkUAwp9DDhtb4Lnich3nJ13uYpvrX4VE74hWPf6AvHHAMmGCidcHjbfg==` |
| @next/swc-darwin-arm64 | 2026-10-14T17:29:45.081Z | 1076283 | yes | `sha512-dPoQYXcfSIqx5o+TOXVXO7kONK5qbtNRDeiTfII0bT3puGIT6VF5e0QwmxNZfEZ5Zety5f3m9P/p4xqwfiLlPg==` |
| @next/swc-darwin-x64 | 2026-10-14T17:30:01.869Z | 1076267 | yes | `sha512-RgCJ7buBivTH+6sddqaVm+/v8kwMHlFkobvdt3DfETutws5HrxnToMIWSN9X3MZ3aAi7BbKrGZZWUDQLEycXqw==` |
| @next/swc-linux-arm64-gnu | 2026-10-14T17:29:11.719Z | 1076317 | yes | `sha512-OHXQe13olE59aKe++zHavGcJPh5SLHXi6Anret3BBeq1+qhSuOJDNAli/EDDfxs6UTqA4Qddo4uyYry2slyjiQ==` |
| @next/swc-linux-arm64-musl | 2026-10-14T17:32:29.845Z | 1076119 | yes | `sha512-nTB7bB6vfn4ezCJNYP43ukt2o8L3+WxKF/sTcTxepdXsJh3SM9RhlU7wrZYbH7L4HO5M87dqDTwm8587vAkCiw==` |
| @next/swc-linux-x64-gnu | 2026-10-14T17:29:50.018Z | 1076278 | yes | `sha512-WXCfVI32rW3xCusoUX1RpZKtyChWU2Zwe27JUDmM3KrXwcDNc9vV4zEq0GKFAURnuQ/Ouo/XqPvB0yh445XZCg==` |
| @next/swc-linux-x64-musl | 2026-10-14T17:30:51.586Z | 1076217 | yes | `sha512-Miq+NDb/HWsXuxseYxMM6fuEOQXgTziarkKIRpVKCn8W69cEfhQaQr+90pO+u4q2CbJR2wzXmUuCFyZaJs/Nng==` |
| @next/swc-win32-arm64-msvc | 2026-10-14T17:34:27.498Z | 1076001 | yes | `sha512-5LR79lemgDlgxvG7MQJ+zHCkVcrUoQuO7CiIvq3I58vNW4goSOE2b+19Z6FujRWMouvni4gvudYFuFuNxolGWA==` |
| @next/swc-win32-x64-msvc | 2026-10-14T17:30:01.408Z | 1076267 | yes | `sha512-GNipvXUYROSTf4PXEyH95FrWImIB5zdaK6uEOg0RP1/X2drnvoMwiBkJ0VWdzX7w3iiBm3y5g2TxkKDGVTOQcg==` |

**next 15.5.28 vs 15.5.27 — declared-dependency changes (registry):** `dependencies` — only
`@next/env` `15.5.27` → `15.5.28` (the other declared deps — `@swc/helpers`, `caniuse-lite`,
`postcss`, `styled-jsx` — are byte-identical). `optionalDependencies` — the eight `@next/swc-*`
`15.5.27` → `15.5.28`, and the `sharp` range `^0.34.3 || ^0.35.4` → `^0.34.3 || ^0.35.5`.
`peerDependencies`, `engines` — **unchanged** (`engines.node` stays `^18.18.0 || ^19.8.0 || >=
20.0.0`). The nine sub-packages (`@next/env` + eight `@next/swc-*`) have **no** dep/engine change
between 15.5.27 and 15.5.28. **sharp:** the lock pins `sharp` 0.35.5 (an `overrides` entry);
`0.35.5` satisfies the new optional range `^0.35.5` (`>=0.35.5 <0.36.0`), so the sharp-range change
requires no sharp move and introduces no conflict.

### vitest family (8 packages): 4.1.11 → 4.1.12

| package | published 4.1.12 (UTC) | age at reading (s) | ≥604800 | dist.integrity (registry) |
|---|---|---|---|---|
| vitest | 2026-10-15T14:51:24.991Z | 999384 | yes | `sha512-5eWdz2yb3ajxWF3C8C4TjkXl7FGm3n2E/VlazALrQHzK7nYMSGFnCZto0bbPNl77AwkOZVLk0YnBAejUu0NiWA==` |
| @vitest/expect | 2026-10-15T14:40:54.660Z | 1000014 | yes | `sha512-vFlTt+YEu9WBpNjdGayNmlMVzrWPi1+sv853/7t2FU7hpO5gAFBKHzQmkCq5Xjpr+evegF2994LQT3hF3mRlqQ==` |
| @vitest/mocker | 2026-10-15T14:40:12.730Z | 1000056 | yes | `sha512-fKShNpKZzupWZuY0z7egydvL0sqW4INEZBEExMBMAa6izlENEVHwoXgdaTCaBZ5fwlr4xf2o1wXC83n9RpO+NA==` |
| @vitest/pretty-format | 2026-10-15T14:42:05.550Z | 999943 | yes | `sha512-XW9O8+Mxx4VpCtkYdMJLZQQwsVryP9wk7cPKDxtXFfwSak6yRh5+2fep/Y0XF/ElBvJHq8bcYdi6aeuai0opZA==` |
| @vitest/runner | 2026-10-15T14:40:03.289Z | 1000065 | yes | `sha512-NKlVKCr5QnCe8jijdMnmkpHHU+WTqiLFR6G0pHji9uRjXK9xJl1k1nTw6F3pOOj2PDcsDt2GKQMI7wIsaT491w==` |
| @vitest/snapshot | 2026-10-15T14:40:35.044Z | 1000033 | yes | `sha512-ko1y1Qgb/slzQ9mr+b89Cuqud8WG1TKtsPD8r7ZUBdvVOGt85Af2HwCqHujrhwJq95hs/9RM7fcAPg57o1vlzw==` |
| @vitest/spy | 2026-10-15T14:41:54.167Z | 999954 | yes | `sha512-RGq9x4JNGNTZHEJxvN0oSiJjeSCExm0n2gZKKJZHY9cX5AVA6M7VJILBT3ZJ/tJ/0J9uWT7fETV9/btoi//vSg==` |
| @vitest/utils | 2026-10-15T14:41:14.210Z | 999994 | yes | `sha512-Q3awXrwOfEV+qc3WmO5ONyE0yO7Q1gQ9/oyHxGLZ/pl7N3NO/ZztqQwKLuwMkV+CA1JYSIeO3gkHnRDIo4AVaA==` |

**vitest 4.1.12 vs 4.1.11 — declared-dependency changes (registry):** `vitest`'s `dependencies`
bump the seven `@vitest/*` packages above `4.1.11` → `4.1.12`; its optional peer entries
(`@vitest/browser-*`, `@vitest/coverage-*`, `@vitest/ui`) also move to `4.1.12` (one,
`@vitest/browser-webdriverio`, became `^4.1.11`) — these are optional `peerDependencies`, not
installed in this project, so they add no lock node. Inside the family: `@vitest/expect` → `@vitest/spy`,
`@vitest/utils`; `@vitest/mocker` → `@vitest/spy`; `@vitest/runner` → `@vitest/utils`; `@vitest/snapshot`
→ `@vitest/pretty-format`, `@vitest/utils`; `@vitest/utils` → `@vitest/pretty-format` (all `4.1.11` →
`4.1.12`). `@vitest/pretty-format` and `@vitest/spy` are leaves (no dep change). All stay within the
family already in the lock. (`@vitest/runner`'s npm `latest` dist-tag still points to 4.1.11, but
4.1.12 is published — age above — and is what vitest 4.1.12 pins.)

### vite and zod (overrides)

| package | old → new | published new (UTC) | age at reading (s) | ≥604800 | dist.integrity (registry) |
|---|---|---|---|---|---|
| vite | 7.3.6 → 7.3.7 | 2026-10-06T05:11:19.017Z | 1811789 | yes | `sha512-AHEzTORMbi7/7aXp7w7KZ5+DCUdSeLsJz0grY8xHpc9DHdYb0vQu6DqJfm2tOw3gDExNgPgnJTXxM6syYFHaCA==` |
| zod | 4.6.5 → 4.6.6 | 2026-10-11T16:18:23.878Z | 1339765 | yes | `sha512-4UmzQUF5fxvfcYHlbjBmejU+w+hbDnWFx4aS8kBx7nPBHcO2SqPbpAG8snbdg+Xse4pRefR98hgjFgIMCI/UhA==` |

**vite 7.3.7 vs 7.3.6 — declared deps are byte-identical:** `dependencies` = `fdir ^6.5.0`,
`rollup ^4.43.0`, `esbuild ^0.27.0 || ^0.28.0`, `postcss ^8.5.6`, `picomatch ^4.0.3`, `tinyglobby
^0.2.15`; `optionalDependencies` = `fsevents ~2.3.3`; peers unchanged. The 7.3.7 fix is contained in
vite's own tarball (which bundles the patched launch-editor), so vite's transitive subtree
(`rollup`, `esbuild`, `fdir`, `picomatch`, `tinyglobby`, `postcss`, `fsevents`) should not move.
**zod 4.6.6 vs 4.6.5** is a leaf (no runtime dependencies), used transitively by
`eslint-plugin-react-hooks` and `zod-validation-error`; the override pins it everywhere.

## New package NAME check and provenance (D-009-R005 / §5)

**No new package name** is introduced by any of the four moves. Every name the new versions reference
(`next`, `@next/env`, the eight `@next/swc-*`, `sharp`, `@swc/helpers`, `caniuse-lite`, `postcss`,
`styled-jsx`, `vitest`, the seven `@vitest/*`, `vite`, `rollup`, `esbuild`, `fdir`, `picomatch`,
`tinyglobby`, `fsevents`, `zod`) already exists in the current lock. No name is removed at these
tiers (the eight swc binaries and the seven `@vitest/*` all persist, bumped). So no §5 / D-009-R005
provenance admission is triggered for this round. For completeness, the moved package names stay on
their established publishers and repositories, and none adds an install-time lifecycle hook vs the
old version (same name, patch bump):

- next / @next/env / @next/swc-* — maintainers include `vercel-release-bot`, `matt.straka`,
  `matheuss`, `zeit-bot`; repo `github.com/vercel/next.js`; manifest `scripts` carry no
  install/postinstall hook (swc binaries are prebuilt natives).
- vitest / @vitest/* — maintainers `ariperkkio`, `antfu`, `hiogawa`, `oreanno`, `yyx990803`; repo
  `github.com/vitest-dev/vitest`; no install hook.
- vite — maintainers `yyx990803`, `vitebot`; repo `github.com/vitejs/vite`; no install hook.
- zod — maintainer `colinhacks`; repo `github.com/colinhacks/zod`; no install hook.

## Predicted lock changes (S4) — to be confirmed in round 2 against the regenerated lock

- **next family (10 nodes):** version `15.5.27` → `15.5.28`, each with a new resolved URL and the
  registry integrity listed above. (`next`, `@next/env`, eight optional `@next/swc-*`.)
- **vitest family (8 nodes):** version `4.1.11` → `4.1.12` (`vitest` + seven `@vitest/*`), new
  resolved URL + integrity above.
- **vite (1 node):** `7.3.6` → `7.3.7`.
- **zod (1 node):** `4.6.5` → `4.6.6`.
- **root `""` node:** `dependencies.next`, `devDependencies.vitest`, and the two new `overrides`
  (`vite`, `zod`) strings updated to match package.json.
- **expected NOT to move:** `sharp` (0.35.5 still satisfies next's new `^0.35.5`); vite's transitive
  subtree (`rollup`, `esbuild`, `fdir`, `picomatch`, `tinyglobby`, `postcss`, `fsevents`); every
  other package in the lock. No name added, none removed.

The round-2 entry-by-entry lock comparison (base lock vs the workflow-regenerated lock) will confirm
only these nodes differ and trace any additional change to one of the four moves; a new name would
STOP for a G5 provenance review.

## What this shows and what it does not

**Shows:** on `registry.npmjs.org` (reads at `04:27:49Z`) and the GitHub advisory database (reads at
`04:29:22Z`), moving the `next` pin to 15.5.28, the `vitest` pin to 4.1.12, and adding exact
overrides `vite` 7.3.7 and `zod` 4.6.6 points the lock at versions that are each advisory-free at
every severity, each ≥ 604800 s old, each from the registry with a known `dist.integrity`; it
introduces no new package name and removes none at these tiers; and the ten reddening advisories are
all out of range at the new versions. So the repair needs no exception, waiver, exclusion or gate
change.

**Does not show / out of scope this round:** this is a reading of registry and advisory metadata, not
a proof of the regenerated lock. Round 1 did not run `npm install`/`npm ci` and does not write
`apps/web/package-lock.json` — the GitHub generate-lockfile workflow is its only writer (D-009-R017),
and round 2 compares the locks. It cannot guarantee the registry state at the moment the workflow
runs, nor that the regeneration touches only the predicted nodes. Whether the browser tests pass on
next 15.5.28 / vitest 4.1.12 is decided by CI (S7), not by reasoning. The workflow's blocking
`npm audit` (total == 0 at every severity), the committed-lock age gate, the npm-CLI advisory check,
and the round-2 lock comparison are the authorities that decide at run time. If any reports a finding,
an under-age package, a new name, or a registry outage, the task STOPs and reports — no waiver, no
gate change (S6).
