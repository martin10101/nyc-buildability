# Producer report — M0-T167 (D-091 T4): admit the Codex CLI (@openai/codex)

Producer: cloud-architect. Worktree: /root/project/w-M0-T167.
Branch: task/M0-T167-codex-cli-admission. Claim-seam HEAD: 1d22a07a0514126eb8b1386f53d9c7b8534247da.
Directive refs: D-091-R001, D-091-R005. Platform: Linux cloud server (Ubuntu, 4 CPU / 8 GB).

## Outcome summary

- Admitted `@openai/codex@0.157.0` — the newest STABLE X.Y.Z at least 604800 s old at admission.
- Release-age gate (repo's own `apps/web/scripts/dependency_age_gate.mjs`): PASS, exit 0, 7/7 packages.
- npm audit (all severities): 0 vulnerabilities, exit 0; JSON total == 0.
- Integrity: every resolved tarball matches the official registry `dist.integrity`; all resolve to registry.npmjs.org.
- Lifecycle scripts: none (`{}`) on every package.
- Reviewer flags: all present in `codex exec --help` (v0.157.0); none missing.
- CI gap: no workflow covers `tools/codex_cli/` today (documented; CI change out of scope).
- No sign-in, no credential touched, no global install.

## 1. Guard

```
git -C /root/project/w-M0-T167 rev-parse --show-toplevel  -> /root/project/w-M0-T167
git -C /root/project/w-M0-T167 rev-parse --abbrev-ref HEAD -> task/M0-T167-codex-cli-admission
git -C /root/project/w-M0-T167 rev-parse HEAD              -> 1d22a07a0514126eb8b1386f53d9c7b8534247da
```
Matches the dispatch. No reset needed. Toplevel is the task worktree (not the primary checkout).

## 2. Toolchain available

```
node --version -> v22.23.3
npm  --version -> 10.9.9   (/usr/bin/npm)
npm config get registry -> https://registry.npmjs.org/   (official)
```
Note: CI pins npm 11.18.0 (FE-S4); locally only 10.9.9 is present and I must not install globally,
so the lock was generated/installed under 10.9.9. The AUTHORITATIVE age gate uses Node built-ins
only (independent of npm), and npm audit queries the registry advisory DB, so the npm minor does
not change the admission verdict. The follow-up CI job should run under pinned 11.18.0 (see §9).

## 3. Version selection (registry clock = authoritative)

Fetched `https://registry.npmjs.org/@openai/codex` (16,829,412 bytes). Registry `Date` header at
fetch: `Fri, 02 Oct 2026 05:35:18 GMT`. Computed age per STABLE X.Y.Z against that clock
(MIN = 604800 s; 604800 PASSES, 604799 FAILS):

```
latest dist-tag: 0.160.0
0.155.0   age 1232175s (14.26d) PASS
0.155.1   age 1157154s (13.39d) PASS
0.156.0   age  812380s ( 9.40d) PASS
0.156.1   age  787792s ( 9.12d) PASS
0.157.0   age  615598s ( 7.13d) PASS   <- newest stable >= 7 days
0.157.1   age  534500s ( 6.19d) FAIL
0.158.0   age  346977s ( 4.02d) FAIL
0.159.0 .. 0.160.0  all < 4d   FAIL
```
Chosen: **0.157.0** (publish 2026-09-25T02:35:19.752Z). Boundary acceptance scenario satisfied:
0.157.1 at 534500 s (< 604800) is refused; 0.157.0 is the newest stable that clears 7 days; no
alpha/beta/rc or hourly prerelease considered. The design doc's earlier candidate (0.156.1) was
superseded because 0.157.0 crossed 7 days between the design fetch and admission.

## 4. Platform binaries (optionalDependencies)

0.157.0 has `dependencies: {}` and six os/cpu-restricted optional platform binaries, each an alias
`npm:@openai/codex@0.157.0-<platform>` in the SAME packument. All six publish empty `scripts` and
all six are >= 604800 s old:

```
0.157.0-linux-x64    pub 2026-09-25T02:36:28.955Z  age 615529s (7.124d) PASS  scripts={}
0.157.0-win32-x64    pub 2026-09-25T02:45:10.914Z  age 615007s (7.118d) PASS  scripts={}
0.157.0-darwin-x64   pub 2026-09-25T02:36:13.518Z  age 615544s (7.124d) PASS  scripts={}
0.157.0-linux-arm64  pub 2026-09-25T02:36:53.523Z  age 615504s (7.124d) PASS  scripts={}
0.157.0-win32-arm64  pub 2026-09-25T02:38:31.569Z  age 615406s (7.123d) PASS  scripts={}
0.157.0-darwin-arm64 pub 2026-09-25T02:39:39.490Z  age 615338s (7.122d) PASS  scripts={}
```
On this linux/x64 host, `npm ci` installs only `@openai/codex` + `@openai/codex-linux-x64`.

## 5. Files written (allowed_paths only: tools/codex_cli/)

- `tools/codex_cli/package.json` — private, exact pin `"@openai/codex": "0.157.0"` (no ^/~).
- `tools/codex_cli/.gitignore` — `node_modules/`.
- `tools/codex_cli/package-lock.json` — generated with
  `npm install --ignore-scripts --package-lock-only --no-audit --no-fund` (exit 0, "up to date in 3s").
  lockfileVersion 3; 7 unique registry packages; every entry resolved=registry.npmjs.org with a
  registry-matching integrity.
- `tools/codex_cli/README.md` — full G5 provenance record (replaces the placeholder).

## 6. Release-age gate (repo's existing FE-S9 tool, reused)

```
node apps/web/scripts/dependency_age_gate.mjs tools/codex_cli/package-lock.json
Committed-lockfile release-age gate  (now=2026-10-02T05:37:52.000Z, min_age=604800s)
== tools/codex_cli/package-lock.json  (7 unique registry packages) ==
  PASS  @openai/codex@0.157.0              uploaded=2026-09-25T02:35:19.752Z  age=615752s (7.13d)
  PASS  @openai/codex@0.157.0-darwin-arm64 uploaded=2026-09-25T02:39:39.490Z  age=615492s (7.12d)
  PASS  @openai/codex@0.157.0-darwin-x64   uploaded=2026-09-25T02:36:13.518Z  age=615698s (7.13d)
  PASS  @openai/codex@0.157.0-linux-arm64  uploaded=2026-09-25T02:36:53.523Z  age=615658s (7.13d)
  PASS  @openai/codex@0.157.0-linux-x64    uploaded=2026-09-25T02:36:28.955Z  age=615683s (7.13d)
  PASS  @openai/codex@0.157.0-win32-arm64  uploaded=2026-09-25T02:38:31.569Z  age=615560s (7.12d)
  PASS  @openai/codex@0.157.0-win32-x64    uploaded=2026-09-25T02:45:10.914Z  age=615161s (7.12d)
RESULT: PASS — every committed registry package is >= 7 days old and integrity-verified
EXIT 0
```
The gate independently re-fetched each packument: every integrity matched the registry
`dist.integrity`, every host was registry.npmjs.org, no outage/malformed/ambiguous condition.

## 7. Advisory audit (FE-S2 equivalents)

```
npm audit --audit-level=low     -> "found 0 vulnerabilities"   EXIT 0
npm audit --json (metadata.vulnerabilities) -> {info:0,low:0,moderate:0,high:0,critical:0,total:0}
JSON total across all severities == 0   EXIT 0
```

## 8. Deterministic install + binary verification (no sign-in, no network model calls)

```
npm ci --ignore-scripts --no-audit --no-fund   -> "added 2 packages in 10s"  EXIT 0
  installed: node_modules/@openai/codex, node_modules/@openai/codex-linux-x64
  node_modules/.bin/codex -> ../@openai/codex/bin/codex.js
installed package.json scripts: @openai/codex {} ; @openai/codex-linux-x64 {}
node node_modules/@openai/codex/bin/codex.js --version   -> codex-cli 0.157.0   EXIT 0
node node_modules/@openai/codex/bin/codex.js exec --help -> EXIT 0
```
node_modules is git-ignored (git check-ignore confirmed) and 374 MB (local only; never committed).
Env: DISABLE_AUTOUPDATER=1 CODEX_DISABLE_UPDATE_CHECK=1. No `codex login` run; no credential touched.

Reviewer flags from `codex_reviewer.py:build_argv` vs `codex exec --help` (v0.157.0):

| token | present |
|---|---|
| exec subcommand | yes |
| -C, --cd | yes |
| -m, --model | yes |
| --ephemeral | yes |
| --ignore-user-config | yes |
| --strict-config | yes |
| -s, --sandbox (value read-only) | yes (read-only listed) |
| --json | yes |
| --output-schema | yes |
| -o, --output-last-message | yes |
| -c, --config (model_reasoning_effort=...) | yes |
| - (stdin prompt) | yes |

ALL present; none missing. Runtime caveat (not a flag): the reviewer's measured sandbox boundary
was last captured on codex-cli 0.153.4 (M0-T147). Re-measuring the boundary and recapturing
fixtures against 0.157.0 is the D-091 recertification task's job, not this admission task's.

## 9. CI coverage gap (CI change is out of scope)

No workflow references `tools/codex_cli`. `web-dependency-security` (ci.yml) and
`scheduled-web-audit.yml` are scoped to `apps/web/package-lock.json` only (working-directory
apps/web; path filters apps/web/**). So this lock is gated at admission (this report) but NOT
continuously re-audited, which policy §1.5 requires. Needed follow-up (orchestrator-owned,
touches .github/): a CI job + scheduled-audit entry that, from tools/codex_cli/ under pinned npm
11.18.0, runs `npm ci --ignore-scripts --no-audit`, `npm audit --audit-level=low` + JSON total==0,
and `node ../../apps/web/scripts/dependency_age_gate.mjs tools/codex_cli/package-lock.json`,
fail-closed, path filters on tools/codex_cli/package*.json.

## 10. Owner sign-in location (confirmed from official docs)

`https://developers.openai.com/codex/auth` (fetched 2026-10-02, HTTP 200): credentials cache to
`~/.codex/auth.json` (plaintext) or the OS keyring; file storage is `auth.json` under `CODEX_HOME`
(defaults to `~/.codex`). Owner runs `codex login` once on the server; the file lives outside the
repo and outside git. Orchestrator never handles it; the reviewer passes `--ignore-user-config`
(auth still resolves via CODEX_HOME per the CLI help).

## 11. Acceptance scenarios

- primary: 0.157.0 is >= 604800 s old, integrity matches registry, npm audit 0 advisories — MET.
- boundary: 0.157.1 (534500 s) refused; newest stable >= 7 days chosen, no alpha — MET.
- missing/ambiguous: gate/audit fail closed on outage/malformed; none occurred, both ran clean — MET (fail-closed behavior is in the reused tool; not forced in this run).
- failure: a lifecycle script or advisory would stop admission — none found (scripts {}, 0 advisories), so admission proceeds — MET.
- flags: every codex exec flag the reviewer uses is present in --help — MET.

## 12. Scope / rules compliance

Edited only tools/codex_cli/ (4 files). No project-control/, .github/, .claude/, other lockfiles,
services/**, apps/** source, or tools/agent_supervisor/** touched. npm used only inside
tools/codex_cli/ and only with --ignore-scripts. No global install. No git push / merge / gh /
project_control.py run. This report lives in the scratchpad per dispatch step 6; the orchestrator
transplants it to project-control/reports/M0-T167-producer-report.md (step 5 forbids me writing
under project-control/).

## 13. Commit

Committed to the task branch (for orchestrator cherry-pick): package.json, package-lock.json,
.gitignore, README.md. node_modules excluded by .gitignore. Commit sha reported in the return.

## Assumptions / limitations

- Lock generated under npm 10.9.9 (no global install allowed); CI pins 11.18.0. lockfileVersion 3
  is compatible; the follow-up CI job should still run under 11.18.0 for exact parity.
- "Recent ownership change" cannot be fully ruled out from packument metadata (no change-log);
  mitigated by OIDC trusted-publisher signal + scheduled re-audit.
- Sandbox-boundary behavior of 0.157.0 not measured here (recertification task owns that).

---

## REWORK ADDENDUM (G5 B1: continuous-audit CI coverage) — HEAD cbe0b3ea

G5 (project-control/reports/M0-T167-G5.md) passed every provenance check but FAILED admission on
B1: no CI job re-audited tools/codex_cli, so policy §1 rule 5 ("audited on every change AND on a
schedule") was unmet. The packet was scope-corrected to also allow `.github/workflows/ci.yml` and
`.github/workflows/scheduled-web-audit.yml`. Rework base HEAD ab1dfabc; new commit cbe0b3ea (worked
on top, no reset).

Files changed (3, all in allowed scope): `.github/workflows/ci.yml`,
`.github/workflows/scheduled-web-audit.yml`, `tools/codex_cli/README.md`. Both workflow edits are
purely additive (no deletions; no existing job/trigger/permission/pin changed) — mirror the web
dependency-security jobs, same SHA-pinned `actions/checkout@34e1148...` and
`actions/setup-node@49933ea...`, same pinned npm `11.18.0`, reuse the web age gate.

ci.yml — new job **`codex-cli-dependency-security`** (always-run on push/PR, like
web-dependency-security), working-directory `tools/codex_cli`. Steps:
1. `actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1`
2. `actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020 # v4.4.0` (cache-dependency-path tools/codex_cli/package-lock.json)
3. `Pin npm CLI to 11.18.0`
4. `Deterministic install (npm ci --ignore-scripts; lockfile + integrity verified)` → `npm ci --ignore-scripts --no-audit --no-fund`
5. `Blocking npm audit (--audit-level=low)`
6. `Blocking npm audit (JSON total vulnerabilities must be 0)`
7. `Committed-lockfile release-age gate (>= 7 days, fail-closed)` → `node ../../apps/web/scripts/dependency_age_gate.mjs package-lock.json`

scheduled-web-audit.yml — new job **`codex-audit`** (runs on the workflow's existing daily cron
`41 6 * * *` + workflow_dispatch; trigger block untouched), working-directory `tools/codex_cli`,
with the identical 7 steps above. The existing `audit` job is unchanged.

Every added step fails closed (a finding, too-new package, integrity mismatch, unexpected host, or
registry outage fails the build); no allowlist/suppression/warning-only step.

README.md CI-coverage section rewritten from "does not cover / needed follow-up" to record the two
jobs now exist; N3 cosmetic fix applied (auth URL 308-redirects then resolves 200).

Validation / tests run:
- `python -c yaml.safe_load` on both workflow files → PARSED OK; ci.yml jobs now include
  `codex-cli-dependency-security`, scheduled now includes `codex-audit`; new-job working-dirs and
  step names asserted (lanes venv python).
- `tools/validate_mcp_policy.py --check` → EXIT 0 (ci.yml still contains the two required p10
  control-plane steps; my additive job did not disturb them).
- `tools/test_mcp_policy.py` → Ran 42 tests, OK, EXIT 0 (the "policy INVALID" line is a
  negative-path fixture's own stdout, not a suite failure).

Limitations: workflows are YAML-validated and guard-checked locally; the jobs themselves only
execute on GitHub runners (thin-client / no act here), so first green is proven in CI on the pushed
head. The scheduled-audit PR trigger still lists only apps/web paths (I did not modify the existing
trigger per the "change nothing else" rule); per-change coverage of tools/codex_cli is provided by
the always-run ci.yml job, and the daily cron covers the scheduled re-audit.

END-OF-REPORT
