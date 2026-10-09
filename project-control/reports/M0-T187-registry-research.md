# M0-T187 registry research — next 15.5.24 -> 15.5.27

Independent second reading by the producer (frontend-engineer). Every value below was read on the
day from the official sources named — `registry.npmjs.org` and the GitHub advisory / repo-advisory
APIs — not copied from the task packet, the G0 report, the B-031 blocker, or agent memory.

- **Reading clocks (authoritative, UTC):** each value's age uses that document's own
  `registry.npmjs.org` / `api.github.com` `Date` response header (the policy clock is the
  registry's own UTC clock, not the local/CI clock). The registry reads fell in the window
  `Thu, 08 Oct 2026 00:40:00 GMT` (`next`) through `Thu, 08 Oct 2026 00:40:30 GMT` (last swc
  package); the advisory reads at `Thu, 08 Oct 2026 00:42:46–00:43:25 GMT`.
- **Source of ages:** `(that document's Date header) - time["15.5.27"]` in whole seconds, per
  `registry.npmjs.org/<pkg>` `time` fields.
- **Old locked versions:** read from `apps/web/package-lock.json` (lockfileVersion 3) — `next`,
  `@next/env` and the eight `@next/swc-*` packages are all locked at `15.5.24` today; the eight
  `@next/swc-*` are `optional: true` with `cpu`/`os` guards.

## Outcome: proceed (no STOP condition)

Every one of the ten packages at `15.5.27` is at least 604800 s old, no package NAME would be new
to the lock, the locked `sharp` 0.35.5 still satisfies next's new optional range, and no advisory
affects any new version. The declared pin in `apps/web/package.json` is moved `15.5.24` -> `15.5.27`
(exact, no range). The repair needs no exception, waiver, exclusion or gate change.

## The two advisories (read at source)

Each advisory was read twice: the maintainer's own publication time from the vercel repo endpoint
(`https://api.github.com/repos/vercel/next.js/security-advisories/<id>`, HTTP 200) and the global
GitHub advisory-database entry (`https://api.github.com/advisories/<id>`, HTTP 200) that `npm audit`
consumes. Both are **medium** severity (npm audit prints this as `moderate`). They are **not**
"published today": the maintainer published both on 2026-09-30; they entered GitHub's global
database on 2026-10-07, which is why CI began flagging them on the night of 2026-10-07/08.

| field | GHSA-4jqv-mc3x-m676 | GHSA-mcj8-r9mp-w47p |
|---|---|---|
| cve_id | CVE-2026-94543 | CVE-2026-94484 |
| severity | medium | medium |
| summary | Next.js has cache poisoning of SSG and ISR pages in self-hosted applications | Next.js has cache poisoning in SSG/ISR rendering that leads to cross-user content substitution and persistent denial of service |
| maintainer published (vercel repo API) | 2026-09-30T16:14:22Z | 2026-09-30T16:14:19Z |
| entered GitHub DB (advisories API `published_at` = `github_reviewed_at`) | 2026-10-07T20:32:06Z | 2026-10-07T20:31:13Z |
| NVD published (`nvd_published_at`) | 2026-10-02T16:16:52Z | 2026-10-02T16:16:51Z |
| vulnerable range (next) | `>= 15.0.0, < 15.5.27` (and `>= 16.0.0, < 16.3.8`) | `>= 15.0.0, < 15.5.27` (and `>= 16.0.0, < 16.3.8`) |
| first patched (next) | 15.5.27 (and 16.3.8 on the 16.x line) | 15.5.27 (and 16.3.8 on the 16.x line) |

`15.5.27` is outside the vulnerable range `>= 15.0.0, < 15.5.27` for both — it is the first patched
version on the 15.x line.

## next 15.5.27 vs 15.5.24 — dependency lists (from the registry document)

- `dependencies`: the only change is `@next/env` `15.5.24` -> `15.5.27`. The other three stay
  byte-identical: `@swc/helpers` `0.5.15`, `caniuse-lite` `^1.0.30001579`, `postcss` `8.4.31`,
  `styled-jsx` `5.1.6`.
- `optionalDependencies`: the eight `@next/swc-*` move `15.5.24` -> `15.5.27`, and the `sharp`
  range changes `^0.34.3 || ^0.35.3` -> `^0.34.3 || ^0.35.4`.
- `peerDependencies`, `peerDependenciesMeta`, `engines`: **unchanged** (`engines.node` stays
  `^18.18.0 || ^19.8.0 || >= 20.0.0`).
- The nine sub-packages (`@next/env` + eight `@next/swc-*`): **no change** in
  `dependencies`/`optionalDependencies`/`peerDependencies`/`engines` between 15.5.24 and 15.5.27.

**sharp range:** the lock pins `sharp` at `0.35.5` (also an `overrides` entry in
`apps/web/package.json`). `0.35.5` satisfies the new optional range `^0.35.4` (i.e. `>=0.35.4
<0.36.0`); it also satisfied the old `^0.35.3`. So the sharp-range change requires no sharp bump and
introduces no conflict.

**New package NAME?** None. Every name next@15.5.27 references in `dependencies` /
`optionalDependencies` already exists in the current lock (`next`, `@next/env`, the eight
`@next/swc-*`, `sharp`, `@swc/helpers`, `caniuse-lite`, `postcss`, `styled-jsx`). No §5 provenance
admission is triggered. (If a new name had appeared this report would STOP; it does not.)

## The ten packages at 15.5.27

| package | old -> new | published 15.5.27 (UTC) | age at reading (s) | >= 604800 | dist.integrity (registry) |
|---|---|---|---|---|---|
| `next` | 15.5.24 -> 15.5.27 | 2026-09-30T16:19:50.862Z | 634809 | yes | `sha512-F82CrlPZ8GRxBH9RIIoR3qU1t5RT3dv1K8moe8SjlDEquiFipvEI13R1Om90TaUOEwShkWCMlg8+gvTNzfMhvg==` |
| `@next/env` | 15.5.24 -> 15.5.27 | 2026-09-30T16:08:30.736Z | 635507 | yes | `sha512-WC5hvVqiuFOcRyz6gKPeJkiVvSMf3scNeAV49CdWtVqxmUlzh8UKR6YHt9yiNkh8LngtzqSlVz07/Ma3ZAzchA==` |
| `@next/swc-darwin-arm64` | 15.5.24 -> 15.5.27 | 2026-09-30T16:04:51.500Z | 635726 | yes | `sha512-fBA9QurmK4+uj4wNhmRTuO5zMVRaBHCvp6H93zTG/5i6Yi6TewbvbesXB8YQNj8T99Cwrow87hHiFV6wL/hyMA==` |
| `@next/swc-darwin-x64` | 15.5.24 -> 15.5.27 | 2026-09-30T16:06:49.162Z | 635608 | yes | `sha512-FGZwJwry8qZNHxD/nfwrCwCHHrqx6epqItkkxbYcBQEQ2uw5S43bY83fQB5zbAsZE7TELMjoYkbhsQ4oKM7wwg==` |
| `@next/swc-linux-arm64-gnu` | 15.5.24 -> 15.5.27 | 2026-09-30T16:05:10.117Z | 635708 | yes | `sha512-GQulAaJYNF1RYuatlsw9/uzbKz4if2V7Ic9nVO+P0ljYPm4yBRTFIl6g5YkKTw40lMLbpy9edLoH44g3jSHMYA==` |
| `@next/swc-linux-arm64-musl` | 15.5.24 -> 15.5.27 | 2026-09-30T16:04:32.507Z | 635756 | yes | `sha512-URFFsUmu8Pi0/1qdnUI7tx7keZw1Mt5zHfrIX1RfDG9Nih8DYxK54WZsDJUX2ZTlii1jgotL7qcbwKnSAES6xQ==` |
| `@next/swc-linux-x64-gnu` | 15.5.24 -> 15.5.27 | 2026-09-30T16:05:49.960Z | 635679 | yes | `sha512-aJp74z7uvU5jQhyH7lyk+4qSRcTdKbKT9NQE3jiO9kWYkoHZjKi0zzHDbCoZ+v2sJDEiJ/z58R0UlWMGWNF3HA==` |
| `@next/swc-linux-x64-musl` | 15.5.24 -> 15.5.27 | 2026-09-30T16:05:24.969Z | 635704 | yes | `sha512-ILl2bQ8MbpvyMpY8AXljb3BXs0MJSC8HXZ6QV5AWpVS7ZELqNPtrHvhUk+SNarvjvICXX8bCS287TCi+gUFVYg==` |
| `@next/swc-win32-arm64-msvc` | 15.5.24 -> 15.5.27 | 2026-09-30T16:05:00.192Z | 635728 | yes | `sha512-1MB9Rh5y8TOPN2x7naNTJNkCZQav9c70AI7EBYXxsEewwOffC4DjjwBwKf20NBvcA+u+5jDv7nVmHxunlP2d7Q==` |
| `@next/swc-win32-x64-msvc` | 15.5.24 -> 15.5.27 | 2026-09-30T16:06:43.442Z | 635626 | yes | `sha512-XtYgpGOswgnyBWXzOEG6q9RhvnSw0CEZ0MbWqCsl5PISgt9EzvJvNW5mU5n1PsphX/lnamzxjgQXH2GUJL8nqg==` |

- **Count:** 10 (`next` + `@next/env` + eight `@next/swc-*`). All move `15.5.24` -> `15.5.27`.
- **Youngest:** `next` itself at `15.5.27`, 634809 s old (> 604800 by ~30009 s, i.e. ~8.3 h over
  the 7-day floor). **Oldest:** `@next/swc-linux-arm64-musl`, 635756 s. Every one of the ten meets
  the 604800 s rule.
- Each `dist.integrity` above is the registry's own value for that exact version; the
  lockfile-regeneration workflow's committed-lock age gate (`apps/web/scripts/dependency_age_gate.mjs`)
  independently re-checks lock integrity == registry integrity and age at run time.

## Name-set comparison with the current lock (`apps/web/package-lock.json`)

- Names 15.5.27 brings that are **absent from the current lock**: none. (No new package name -> no
  §5 provenance admission needed.)
- Names in the current lock that 15.5.27 **no longer lists**: none at this tier — the eight
  `@next/swc-*` platform binaries and `@next/env` all persist, bumped `15.5.24` -> `15.5.27`.

## Any other advisory against the new versions

Queried the GitHub advisory database (HTTP 200 each, empty body `[]`):

1. `GET https://api.github.com/advisories?ecosystem=npm&affects=next@15.5.27` -> `[]` (no advisory
   affects `next` at 15.5.27).
2. `GET https://api.github.com/advisories?ecosystem=npm&affects=@next/env@15.5.27` -> `[]` (no
   advisory affects `@next/env` at 15.5.27).

Both returned HTTP 200 with an empty array. No query failed; nothing was assumed. The two reddening
advisories (GHSA-4jqv-mc3x-m676, GHSA-mcj8-r9mp-w47p) both list `next` vulnerable `< 15.5.27` on the
15.x line, so 15.5.27 is out of range.

## Other places in the repository that name `15.5.24`

Grep for `15.5.24` across the worktree (excluding `package-lock.json` and `.git/`) returns, besides
my edit target `apps/web/package.json`, only **prose / records** — documentation, the B-022 / B-030
/ B-031 blockers, the D-009 / D-040 / D-042 / D-043 directive files + `directives/index.json`, the
M0-T185 / M0-T182 / M0-T187 / M5-T021 / M5-T022 / M5-T090 reports, and the M0-T185 / M0-T187 /
M5-T021 / M5-T024 task packets. None of these is a resolvable version pin: the only declaration that
CI resolves is `apps/web/package.json` (and the regenerated lock). I changed **nothing** outside my
two files; those historical records correctly reference the pre-upgrade state.

## What this shows and what it does not

**Shows:** on the registry and advisory databases as read in the window `Thu, 08 Oct 2026
00:40:00–00:43:25 GMT`, pinning `next` to exactly `15.5.27` moves ten packages to versions that are
each advisory-free at every severity, each at least 604800 s old, each from `registry.npmjs.org`,
and each with a known `dist.integrity`; it introduces no new package name and removes none at this
tier; the locked `sharp` 0.35.5 still satisfies next's new optional range; and the two advisories
that currently redden the web-dependency gate do not apply to 15.5.27. So the repair needs no
exception, waiver, exclusion or gate change.

**Does not show / out of scope here:** this is a reading of registry and advisory metadata, not a
proof of the regenerated lock. It does not run `npm install`/`npm ci`/`npx` and does not itself write
`apps/web/package-lock.json` (only the GitHub lockfile-regeneration workflow does, after this commit).
It cannot guarantee the registry state at the moment the workflow runs, nor that the regeneration
touches only these ten entries. The workflow's blocking `npm audit` (total == 0 at every severity),
the committed-lock age gate, the npm-CLI advisory check, and the entry-by-entry lock comparison are
the authorities that decide at run time. If any of them reports a finding, an under-age package, a
new name, or a registry outage, the task stops and reports — no waiver, no gate change.
