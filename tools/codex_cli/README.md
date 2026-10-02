# Codex CLI admission — G5 provenance record (D-091, ledger task M0-T167)

This directory admits the OpenAI Codex CLI as a dependency-gated, repo-local tool for the
D-091 cloud review loop. It follows `docs/DEPENDENCY_SECURITY_POLICY.md` in full: exact pin,
integrity matched to the official registry, advisory-free at every severity, every package
(including the platform binary) at least 604800 seconds old, lifecycle scripts reviewed, and
no global install. Only `package.json`, `package-lock.json`, `.gitignore` and this `README.md`
are committed; `node_modules/` is git-ignored and reproducible from the committed lock.

All figures below are from the official npm registry (`https://registry.npmjs.org/@openai/codex`)
and the installed binary, measured on this Linux cloud server on 2026-10-02 (registry UTC clock).

## Package

- **Name:** `@openai/codex` (scoped to the official OpenAI org — not a typosquat; the binary it
  provides is `codex`). Admitted via npm so the dependency gate can exact-pin and
  integrity-match it (per policy §1.3).
- **Admitted version:** `0.157.0` (exact pin, no `^`/`~`). This is the newest **stable**
  `X.Y.Z` release that was at least 604800 s old at admission time. The `latest` dist-tag
  (`0.160.0`, published 2026-10-01) and every release newer than `0.157.0` were **too new**
  and were rejected. Alpha/beta/rc and the hourly prerelease builds are never considered.
- **Registry origin:** every resolved package is `https://registry.npmjs.org/...` (the official
  registry). An unexpected host fails closed; none was found.
- **License:** Apache-2.0.

## Version, publish time, and age (7-day rule, 604800 s PASSES / 604799 s FAILS)

Measured against the registry's own UTC `Date` clock (never the local clock).

| Package (unique in lock) | Published (UTC) | Age at admission | Verdict |
|---|---|---|---|
| `@openai/codex@0.157.0` | 2026-09-25T02:35:19.752Z | 615752 s (7.13 d) | PASS |
| `@openai/codex@0.157.0-linux-x64` | 2026-09-25T02:36:28.955Z | 615683 s (7.13 d) | PASS |
| `@openai/codex@0.157.0-darwin-x64` | 2026-09-25T02:36:13.518Z | 615698 s (7.13 d) | PASS |
| `@openai/codex@0.157.0-linux-arm64` | 2026-09-25T02:36:53.523Z | 615658 s (7.13 d) | PASS |
| `@openai/codex@0.157.0-darwin-arm64` | 2026-09-25T02:39:39.490Z | 615492 s (7.12 d) | PASS |
| `@openai/codex@0.157.0-win32-arm64` | 2026-09-25T02:38:31.569Z | 615560 s (7.12 d) | PASS |
| `@openai/codex@0.157.0-win32-x64` | 2026-09-25T02:45:10.914Z | 615161 s (7.12 d) | PASS |

Boundary confirmation: the next stable release `0.157.1` was 534500 s (6.19 d) old at admission
and is correctly **rejected** by the 7-day rule; `0.157.0` passes with ~10900 s of margin. Only
`@openai/codex` and `@openai/codex-linux-x64` install on this `linux/x64` host; the other five
platform binaries are os/cpu-restricted optional packages that the lock records and the age gate
still verifies, but `npm ci` does not install them here.

## Integrity (must match the official registry `dist.integrity`)

The committed lock carries a registry-matching `integrity` for every tarball; the repo's
release-age gate independently re-fetched each packument and confirmed every hash matches:

- `@openai/codex@0.157.0` → `sha512-st1R2MhP3ndngOqj2SVh1qk6ED1lpgtlDxipDUyxlKfbsna0imwU2FdTnCjohFQpVh4bR5D5m1hA05AuW2v8Xg==`
- `@openai/codex-linux-x64` (`0.157.0-linux-x64`) → `sha512-3TEPslRaNmlgJST5xMJJ9ZWXW1hr4RlVEpF0tO4NULNGj4b5naWlHa6PlSRiDpnMz322aJkz0uvyyKqc37rLJQ==`

(The remaining four platform binaries' hashes are in `package-lock.json` and were all verified.)

## Lifecycle scripts

**None.** `@openai/codex@0.157.0` and every platform binary package publish an empty `scripts`
object (`{}`) — no `preinstall`/`install`/`postinstall`. Verified both in the registry metadata
and in the installed `node_modules/@openai/codex/package.json` and
`node_modules/@openai/codex-linux-x64/package.json`. The install was still run with
`--ignore-scripts` as defense in depth.

## Maintainers and ownership

- `0.157.0` was published by the trusted-publisher OIDC pipeline `GitHub Actions`
  (`npm-oidc-no-reply@github.com`, `trustedPublisher: github`) — not a personal token.
- 18 maintainers are listed; all use `@openai.com` addresses except `aibrahim-openai`
  (`ahmedibrhm32@gmail.com`), the one personal-email account — noted, not blocking.
- Residual: the packument does not expose a timestamped maintainer-change log, so a *recent*
  ownership change cannot be fully ruled out from registry metadata alone. The scheduled
  re-audit plus the OIDC trusted-publisher signal are the ongoing guard.

## Audit result (advisory-free at every severity)

- `npm audit --audit-level=low` → `found 0 vulnerabilities` (exit 0).
- `npm audit --json` → `{info:0, low:0, moderate:0, high:0, critical:0, total:0}` — total across
  every severity is 0.

## Release-age gate result

Run with the repo's existing, authoritative gate `apps/web/scripts/dependency_age_gate.mjs`
(the same tool CI uses for FE-S9) against this lockfile:

```
node apps/web/scripts/dependency_age_gate.mjs tools/codex_cli/package-lock.json
RESULT: PASS — every committed registry package is >= 7 days old and integrity-verified
(exit 0; 7 unique registry packages; now=2026-10-02T05:37:52Z)
```

The gate fails closed on any outage, missing/malformed timestamp, missing/mismatched integrity,
or unexpected host; none occurred.

## Necessity

D-091 moves the Codex/Claude review loop to this Linux cloud server. The existing supervisor
adapter `tools/agent_supervisor/codex_reviewer.py` invokes the Codex CLI (`codex exec ...`) as
the independent read-only reviewer. No already-admitted dependency or stdlib provides that CLI;
the loop cannot run without it. See `docs/D091_CLOUD_LOOP_DESIGN.md` section 3.

## Verified reviewer flags

The reviewer builds this argv (`codex_reviewer.py:build_argv`): `exec`, `-C`, `-m`,
`--ephemeral`, `--ignore-user-config`, `--strict-config`, `--sandbox read-only`, `--json`,
`--output-schema`, `--output-last-message`, optional `-c model_reasoning_effort=<tier>`, and the
`-` stdin positional. Against the installed `codex exec --help` (v0.157.0), **every one is
present**:

| Reviewer token | In `exec --help`? |
|---|---|
| `exec` subcommand | yes |
| `-C, --cd <DIR>` | yes |
| `-m, --model <MODEL>` | yes |
| `--ephemeral` | yes |
| `--ignore-user-config` | yes |
| `--strict-config` | yes |
| `-s, --sandbox <MODE>` (value `read-only`) | yes (`read-only` is a listed value) |
| `--json` | yes |
| `--output-schema <FILE>` | yes |
| `-o, --output-last-message <FILE>` | yes |
| `-c, --config <key=value>` | yes |
| `-` stdin prompt | yes (prompt reads from stdin when `-` is used) |

**No reviewer flag is missing.** `codex --version` → `codex-cli 0.157.0`. Runtime note (not a
flag issue): the reviewer docstring records the *sandbox boundary* was last measured on
codex-cli 0.153.4 (M0-T147); the D-091 recertification task must re-measure that boundary and
recapture fixtures against 0.157.0 before live use. This admission task only certifies the flags.

## How to reinstall

From this directory (`tools/codex_cli/`), deterministically from the committed lock, never
globally:

```
npm ci --ignore-scripts        # installs into ./node_modules only (git-ignored)
node node_modules/@openai/codex/bin/codex.js --version   # -> codex-cli 0.157.0
# the launchable binary is also node_modules/.bin/codex
```

To re-verify before trusting it: run the age gate and audit shown above; both must exit 0.

## Where the owner's sign-in lives (outside the repo, outside git)

Confirmed from OpenAI's official Codex docs, <https://developers.openai.com/codex/auth>
(fetched 2026-10-02, HTTP 200): "Codex caches login details locally in a plaintext file at
`~/.codex/auth.json` or in your OS-specific credential store... file stores credentials in
`auth.json` under `CODEX_HOME` (defaults to `~/.codex`)." So the credential is
**`~/.codex/auth.json`** (or the OS keyring), under `CODEX_HOME`, in the owner's home — never in
this repo and never in git. The owner runs `codex login` (Sign in with ChatGPT, or an API key)
once on the server; the orchestrator never handles the credential. The supervisor reviewer
already passes `--ignore-user-config`, so the owner's personal `~/.codex/config.toml` never
leaks into a review (`codex_reviewer.py:8,17`); note that `--ignore-user-config` disables the
user *config* but, per the same CLI help, auth still resolves via `CODEX_HOME`.

## CI coverage today, and the needed follow-up (CI changes are out of this task's scope)

**CI does not cover `tools/codex_cli/` today.** The `web-dependency-security` job and the
`scheduled-web-audit.yml` re-audit in `.github/workflows/` are both scoped to
`apps/web/package-lock.json` (working-directory `apps/web`; path filters list only `apps/web/**`).
No workflow references `tools/codex_cli`. So this lock is dependency-gated at admission by the
commands above, but it is **not** continuously re-audited by CI, which the policy requires
(§1.5: audit on every change AND on a schedule).

Needed follow-up (separate, orchestrator-owned task touching `.github/`): add a CI job (and a
scheduled-audit entry) that, from `tools/codex_cli/`, runs under the pinned npm CLI (11.18.0):
`npm ci --ignore-scripts --no-audit`, `npm audit --audit-level=low` plus the JSON-total==0 check,
and `node ../../apps/web/scripts/dependency_age_gate.mjs tools/codex_cli/package-lock.json`,
fail-closed, with path filters covering `tools/codex_cli/package*.json`. Until that lands, an
advisory disclosed against this lock after merge would not turn CI red on its own.
