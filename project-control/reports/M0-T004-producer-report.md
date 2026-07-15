# Agent Report — M0-T004 Monorepo skeleton + GitHub Actions CI

- Task ID: M0-T004
- Agent: backend-engineer
- Worktree/branch: `.claude/worktrees/M0-T004` on `task/M0-T004-monorepo-ci` (base 59981c6)
- Requested status: **blocked**
- Progress percent: 60

## Executive summary

All file deliverables (S5) were created in the isolated worktree and verified
on disk: `apps/web` (Next.js 15 placeholder with the PRD section 29 disclaimer
rendered in the root layout), `services/api` (FastAPI health endpoint + pytest
smoke tests + ruff config), `packages/contracts` (three v1 draft JSON Schemas
+ README), `supabase/migrations/.gitkeep`, root `README.md`, and
`.github/workflows/ci.yml` (secret-free, S3). S2 (low-storage) is fully
evidenced: ~22.9 KB of new text files, no dependency/build directories, 5.20 GB
free on C:.

**Blocker:** this subagent session's permission gate auto-denies every git
write/network command (`git add`, `git commit`, `git push`, `git fetch`,
`git -C`), every `gh` command beyond `gh auth status`/`gh --version`
(including `gh run list`, which the task packet mandates), and every `python`
invocation (including `tools/project_control.py`). Only a small allowlist of
read-only local commands succeeds. Because the shell working directory is
pinned to the main checkout and resets between calls, and `git -C`
/ `--git-dir` / env-var forms are denied, there is **no permitted way to
commit in the worktree, push the branch, or watch CI**. Scenarios S1 and S4
(CI green run + deliberate-failure run) could not be executed. Exact denial
outputs are embedded below.

## Work completed (files created in the worktree)

All paths relative to `.claude/worktrees/M0-T004/`:

| File | Bytes | Purpose |
| --- | --- | --- |
| `apps/web/package.json` | 696 | Next.js 15.3.4 / React 19.1.0; scripts: lint, typecheck, build |
| `apps/web/tsconfig.json` | 602 | Strict TS config (Next 15 standard) |
| `apps/web/next.config.ts` | 130 | `reactStrictMode: true` |
| `apps/web/eslint.config.mjs` | 475 | Flat config extending `next/core-web-vitals` + `next/typescript` |
| `apps/web/src/app/layout.tsx` | 1222 | Root layout; renders required disclaimer in footer |
| `apps/web/src/app/page.tsx` | 648 | Placeholder home page |
| `apps/web/src/lib/disclaimer.ts` | 686 | `REQUIRED_DISCLAIMER` constant (PRD section 29 text) |
| `services/api/pyproject.toml` | 702 | fastapi+uvicorn; dev extras pytest+httpx+ruff; ruff/pytest config |
| `services/api/README.md` | 513 | Service README (remote-first commands) |
| `services/api/app/__init__.py` | 48 | Package marker |
| `services/api/app/main.py` | 643 | `GET /api/v1/health` returns `{"status":"ok","version":"0.1.0"}` |
| `services/api/tests/__init__.py` | 0 | Package marker |
| `services/api/tests/test_health.py` | 603 | TestClient smoke tests (health OK; unversioned path 404) |
| `packages/contracts/README.md` | 1265 | v1 drafts pending M0-T009; versioning rules |
| `packages/contracts/schemas/v1/property_profile.schema.json` | 7163 | Canonical profile draft (identity/BBL/facts/provenance/conflicts/version per PRD 9, 32.3) |
| `packages/contracts/schemas/v1/coverage_status.schema.json` | 831 | PRD 12 enum + data-completeness in `$defs` |
| `packages/contracts/schemas/v1/analysis_state.schema.json` | 831 | PRD 32.1 fourteen-state enum |
| `supabase/migrations/.gitkeep` | 0 | Migrations placeholder |
| `README.md` | 2251 | Monorepo overview, layout table, low-storage policy, CI description |
| `.github/workflows/ci.yml` | 2162 | CI: web / api / contracts jobs (details below) |
| `.github/scripts/validate_contracts.py` | 1597 | Stdlib-only schema validation for contracts job |

Total new content: **~22.9 KB** (all small text files; no binaries).

### CI workflow design (`.github/workflows/ci.yml`)

- Triggers: `push` + `pull_request`; `permissions: contents: read`;
  concurrency group cancels superseded runs.
- Job `web`: `actions/setup-node@v4` Node 22 with npm cache keyed on
  `apps/web/package.json`; `npm install --no-audit --no-fund`; `npm run lint`
  (eslint flat config); `npm run typecheck` (`tsc --noEmit`); `npm run build`
  (`next build`, telemetry disabled).
- Job `api`: `actions/setup-python@v5` Python 3.12 with pip cache keyed on
  `services/api/pyproject.toml`; `pip install .[dev]`; `ruff check .`;
  `pytest -q`.
- Job `contracts`: runner's preinstalled `python3` runs
  `.github/scripts/validate_contracts.py` (stdlib only, zero installs) which
  fails the job if any schema does not parse or lacks
  `$schema`/`$id`/`title`/`description`.
- `npm install` (not `npm ci`) is used deliberately: no `package-lock.json`
  exists because generating one requires npm locally, which is prohibited by
  the low-storage policy and was also permission-denied in this session.
  Tracked follow-up below.

## Commands and actual outputs

### Environment / read-only commands (ALLOWED by the permission gate)

`git worktree list`
```
C:/Users/MLFLL/Downloads/nyc zoning/nyc-development-feasibility-claude-pack                            3f16326 [main]
C:/Users/MLFLL/Downloads/nyc zoning/nyc-development-feasibility-claude-pack/.claude/worktrees/M0-T004  59981c6 [task/M0-T004-monorepo-ci]
```

`git status` (main checkout — clean; worktree contents are isolated behind its `.git` file)
```
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

`git remote -v`
```
origin	https://github.com/martin10101/nyc-buildability.git (fetch)
origin	https://github.com/martin10101/nyc-buildability.git (push)
```

`gh auth status`
```
github.com
  ✓ Logged in to github.com account martin10101 (keyring)
  - Active account: true
  - Git operations protocol: https
  - Token: gho_************************************
  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'
```

`Get-PSDrive C` (S2 storage evidence)
```
Name           Used (GB)     Free (GB) Provider      Root
----           ---------     --------- --------      ----
C                 231.94          5.20 FileSystem    C:\
```

### Required commands (DENIED by the permission gate)

Every one of the following returned the identical denial (verbatim, truncated
to first sentence for repeats):

```
Permission to use PowerShell has been denied. IMPORTANT: You *may* attempt to
accomplish this action using other tools that might naturally be used to
accomplish this goal... If you believe this capability is essential to
complete the user's request, STOP and explain to the user what you were trying
to do and why you need this permission. Let the user decide how to proceed.
```

Denied commands (each attempted individually; Bash tool denials were
identical):

1. `git add -A`
2. `git push -u origin task/M0-T004-monorepo-ci` (the exact command required by the task packet)
3. `git push --dry-run origin main`
4. `git fetch origin`
5. `git -C "<worktree>" status` (and `git -C "<main root>" rev-parse` — the `-C` form itself is denied)
6. `git --git-dir=".git\worktrees\M0-T004" --work-tree=".claude\worktrees\M0-T004" status`
7. `$env:GIT_DIR=...; $env:GIT_WORK_TREE=...; git status` (env-prefixed form)
8. `Set-Location <worktree>; git status` (cd-compound form; standalone `Set-Location` succeeds but cwd resets to the pinned main root between calls — verified with `Get-Location`)
9. `gh run list --branch task/M0-T004-monorepo-ci --limit 5` (also denied with sandbox override)
10. `gh api repos/martin10101/nyc-buildability ...`
11. `python --version` and `python tools/project_control.py --help`
12. `bash: cd <worktree> && git status`
13. `python tools/project_control.py progress --task-id M0-T004 --agent backend-engineer --percent 60 --status blocked --message "Skeleton files complete in worktree; commit/push/CI blocked by session permission gate (git/gh/python denied)"`
14. `python tools/project_control.py submit --task-id M0-T004 --agent backend-engineer --report project-control/reports/M0-T004-producer-report.md --requested-status blocked`

Items 13-14 mean the control-plane state for M0-T004 could **not** be updated
by this agent; the orchestrator must run the `progress` and `submit` commands
(or grant `python tools/project_control.py *`). The producer report file
itself was written successfully via the file tools (allowed path
`project-control/reports/M0-T004-*`). Task JSON was NOT edited directly —
`project-control/tasks/**` is a forbidden path and bypassing the CLI would
violate the control protocol.

Worktree-entry tools were also unavailable:

- `EnterWorktree(path=<worktree>)` → "Cannot enter worktree: the current
  working directory ... is the repository root, not an isolated worktree —
  switching is only available to sessions whose working directory is inside a
  worktree of this repository."
- `EnterWorktree(name=...)` → "EnterWorktree cannot create a worktree from a
  subagent with a cwd override (isolation: "worktree" or explicit cwd) — it
  would mutate the parent session's process-wide working directory. To work in
  a different directory (including a worktree), spawn an Agent with `cwd` set
  to it."

Conclusion: the subagent was launched with cwd pinned to the **main checkout**
rather than the worktree, and the permission allowlist covers only read-only
local commands. Commit/push/CI-watch is impossible from this session. I did
not use monitoring/test tools to smuggle side-effect commands past the gate.

## Acceptance scenarios

| Scenario | Status | Evidence |
| --- | --- | --- |
| S1 (CI runs and passes on push) | **NOT EXECUTED — blocked** | `git push` and `gh run list` denied (outputs above). Workflow file is authored and ready. |
| S2 (no local artifacts; growth < 1 MB; free-space preserved) | **PASS** | Tree listing below: only text files, ~22.9 KB total. Glob for `**/node_modules/**` and `**/{.venv,venv,.next,dist,build,__pycache__}/**` in the worktree: `No files found`. `Get-PSDrive C`: 5.20 GB free (unchanged by this task; note the 7 GB figure in the policy doc predates other machine usage — this task added ~23 KB). |
| S3 (CI green without secrets; none referenced) | **PASS (static)** | `grep -i "secret|token|password|credential"` over `.github/`: only match is the comment "No secrets are referenced anywhere in this workflow (scenario S3)". Grep for `secrets\.` across all `yml/yaml/json/ts/tsx/py/toml/mjs` in the worktree: `No matches found`. Runtime half depends on S1. |
| S4 (deliberate failure run + revert run) | **NOT EXECUTED — blocked** | Requires commit/push/CI, all denied. |
| S5 (repo tree structure) | **PASS (files on disk, uncommitted)** | Listing below. |

### S5 tree listing (from `Get-ChildItem -Recurse`, worktree)

```
apps/web/package.json                 696
apps/web/tsconfig.json                602
apps/web/next.config.ts               130
apps/web/eslint.config.mjs            475
apps/web/src/app/layout.tsx          1222
apps/web/src/app/page.tsx             648
apps/web/src/lib/disclaimer.ts        686
services/api/pyproject.toml           702
services/api/README.md                513
services/api/app/__init__.py           48
services/api/app/main.py              643
services/api/tests/__init__.py          0
services/api/tests/test_health.py     603
packages/contracts/README.md         1265
packages/contracts/schemas/v1/analysis_state.schema.json    831
packages/contracts/schemas/v1/coverage_status.schema.json   831
packages/contracts/schemas/v1/property_profile.schema.json 7163
supabase/migrations/.gitkeep            0
.github/workflows/ci.yml             2162
.github/scripts/validate_contracts.py 1597
README.md                            2251
```

## CI run URLs

None — commit/push/`gh run` were permission-denied (S1/S4 blocked). No run was
triggered.

## Assumptions and defaults

1. Pinned `next@15.3.4` / `eslint-config-next@15.3.4` / `react@19.1.0`; caret
   ranges for type packages and eslint to avoid nonexistent-pin install
   failures in the absence of a lockfile.
2. Web has no unit test: any test runner (vitest/jest) is a heavy dependency;
   per task packet, web quality gate is lint + typecheck + build only.
3. Disclaimer text uses a straight apostrophe (`platform's`) instead of the
   PRD's typographic apostrophe; wording is otherwise verbatim.
4. `REQUIRED_DISCLAIMER` lives in `src/lib/disclaimer.ts` (not exported from
   `layout.tsx`) because Next.js build-time type validation rejects unknown
   exports from route entries.
5. No root `package.json` workspaces file was added: with no root lockfile,
   npm workspace resolution would complicate the per-app `npm install` in CI.
   CI operates directly in `apps/web`. Revisit when a lockfile lands.
6. `coverage_status.schema.json` carries the data-completeness enum in
   `$defs` rather than a fourth schema file (both statuses are defined in PRD
   section 12).

## Known limitations

- Worktree changes are **uncommitted** (cannot run `git add`/`git commit`).
- CI workflow is authored but **never executed**; web job in particular has
  the usual first-run risk (dependency resolution without a lockfile).
- `npm install` instead of `npm ci` until a lockfile is generated remotely.
- FastAPI TestClient needs `httpx` — included in `[dev]` extras; CI installs
  `.[dev]`.

## Security and provenance impact

- No secrets referenced in workflow or code; workflow permission scope is
  `contents: read` only.
- No external data fetched; no provenance-bearing data created.

## New risks / blockers

- **BLOCKER (session permissions):** subagent cannot execute git write,
  network, `gh`, or `python` commands; cwd pinned to main checkout so
  worktree-scoped git is unreachable (`-C`/`--git-dir`/env/cd-compound forms
  all denied; EnterWorktree unavailable to cwd-pinned subagents). Resolution
  options: (a) relaunch the subagent with cwd set to the worktree and an
  allowlist covering `git add/commit/push`, `gh run *`, and
  `python tools/project_control.py *`; or (b) orchestrator performs
  commit/push/CI-watch on the prepared worktree.

## Recommended next tasks / follow-ups

1. Re-run M0-T004 finishing steps with corrected permissions: commit, push
   `task/M0-T004-monorepo-ci`, watch CI, execute S4 (scratch lint/type error
   commit → failing run URL → `git revert` → passing run URL), append run URLs
   to this report.
2. Generate `apps/web/package-lock.json` in CI or Codespaces, commit it
   remotely, and switch the web job to `npm ci` (determinism follow-up noted
   in `ci.yml`).
3. M0-T009: finalize the canonical contracts; replace the v1 draft field
   lists; add contract tests binding `services/api` responses to the schemas.
4. Clean-up: none needed locally — no temporary files, caches, or installs
   were created (only small text files inside the worktree plus this report).


---

## Orchestrator integration evidence (appended per ADR-005; producer content above unmodified)

Executed by the main-session orchestrator because the producer sandbox denied git/gh/python (see ADR-005).

| Step | Evidence |
|---|---|
| Worktree inspection | `git status --short`: only the 6 intended untracked paths; no tracked files modified |
| Commit | `0da9575` on `task/M0-T004-monorepo-ci` (21 files, 700 insertions); pushed |
| S1 initial CI | Run 29371615952 — SUCCESS (web, api, contracts) https://github.com/martin10101/nyc-buildability/actions/runs/29371615952 |
| Merge main into branch | `ba05bb9` (ADR-005 correction + regression test) |
| control-plane CI job added | `682ae43`; run 29372083661 — SUCCESS (4 jobs) |
| Remote lockfile generation | `generate-lockfile.yml` dispatched on branch; run 29372113001 — SUCCESS; bot commit `05c19ae` added apps/web/package-lock.json (5,558 lines); zero local npm usage |
| npm ci switch | `e4e57a0`; run 29372179826 — SUCCESS (all 4 jobs) https://github.com/martin10101/nyc-buildability/actions/runs/29372179826 |
| S4 deliberate failure | `9aec6b4` (unused variable); run 29372258042 — FAILURE isolated to web job as expected https://github.com/martin10101/nyc-buildability/actions/runs/29372258042 |
| S4 recovery | revert `429c575`; run 29372297441 — SUCCESS https://github.com/martin10101/nyc-buildability/actions/runs/29372297441 |
| S2 storage | 5.19 GB free after all steps (floor 4 GB); no node_modules/venv/build dirs locally; lockfile is a ~250 KB text file |

Scenario verdicts: S1 PASS, S2 PASS, S3 PASS (producer grep + `permissions: contents: read`), S4 PASS, S5 PASS (tree per producer listing, verified at commit 0da9575).
