# M0-T003 — Independent Review of Bootstrap Plan

- **Task:** M0-T003 "Independent review of bootstrap plan"
- **Reviewer (producer of this review):** cloud-architect (did not produce the bootstrap work)
- **Date:** 2026-07-14
- **Method:** Direct repository/git/disk verification. No bootstrap claim was accepted without evidence. Read-only except this report.

## 1. Evidence base

Commands and artifacts inspected (all from project root):

| Check | Command / file | Result |
|---|---|---|
| Git history | `git log --oneline` | Single commit `8ba7278` "Bootstrap: planning and control package for NYC Buildability" |
| Branch/remote | `git branch -vv`, `git remote -v` | `main` tracking `origin/main`; origin `https://github.com/martin10101/nyc-buildability.git` |
| Remote state | `gh repo view martin10101/nyc-buildability --json name,visibility,defaultBranchRef,pushedAt` | `visibility: PRIVATE`, default branch `main`, `pushedAt 2026-07-14T21:08:41Z` (matches local commit time) |
| Working tree | `git status --short` | 10 untracked files: `project-control/tasks/M0-T00{1,2,3}.json`, `project-control/gates/M0-T00{1,2,3}-G0.json`, `project-control/reports/M0-T00{1,2,3}-G0-readiness.json`, `tools/enrich_bootstrap_tasks.py` |
| Disk space | `Get-PSDrive C` | Free = 6,349,840,384 bytes ≈ 5.91 GiB (≈ 6.35 GB decimal) |
| Repo footprint | recursive size measurement | Working tree ≈ 0.1 MB; `.git` ≈ 0.1 MB (total ≈ 0.2 MB) |
| BOM fix | `tools/project_control.py` line 11 | `def load(path): return json.loads(path.read_text(encoding="utf-8-sig"))` — present and committed in `8ba7278` |
| M0-T000 lifecycle | `project-control/tasks/M0-T000.json`, gates `M0-T000-G0.json`/`M0-T000-G3.json`, reports `M0-T000-G0-evidence.json`, `M0-T000-G3-fail-evidence.json`, `M0-T000-G3-pass-evidence.json`, `M0-T000-producer-report.json`, checkpoints CP-0001/CP-0002 | Status `accepted`, `accepted_by: orchestrator`; intentional G3 FAIL (rejection path) then PASS; all committed |
| Control state | `project-control/state.json`, `master_plan.json`, `config.json` | `state.json`: `accepted_tasks: []`, `active_tasks: []` (see defect D2) |
| Blockers | `project-control/blockers/` | **Empty** (see defect D1) |
| MCP config | Glob for `.mcp.json`, `.claude/**/*.json` | No project-level MCP configuration file in the repo |
| CI / code | `Test-Path .github`, `Test-Path src`, `Test-Path docs/research` | All absent (nothing implemented yet — expected at this stage, tracked as gaps) |

## 2. Element-by-element verdicts (S1)

### E1 — Git repo on `main`, initial commit, pushed to private GitHub: **SOUND (verified), with one hygiene defect**
Verified directly: single commit `8ba7278` on `main`, remote `martin10101/nyc-buildability`, confirmed **PRIVATE** via `gh repo view`, push timestamp matches. Repo is source-only and tiny (≈0.2 MB), consistent with the low-storage policy.
Defect: 10 control-plane files created after the commit (task packets M0-T001/2/3, their G0 gates and readiness reports, `tools/enrich_bootstrap_tasks.py`) are **untracked and exist only on the owner's PC**. This violates `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md` ("The local PC must never be the only location of code, configuration, source documents, reports, or project data") and undermines `docs/PROJECT_CONTROL_PROTOCOL.md` (the ledger is the source of truth; an unpushed ledger is not durable).

### E2 — `project_control.py` lifecycle verified via M0-T000; BOM fix: **SOUND (verified), with minor evidence-quality caveats**
Verified: M0-T000 is `accepted` with `accepted_by: orchestrator`; the rejection path was exercised (`M0-T000-G3-fail-evidence.json` FAIL, then rework, then PASS); CP-0001/CP-0002 recorded; the `utf-8-sig` fix is in `load()` and committed.
Caveats (minor, do not invalidate the verification):
- `M0-T000.json` has empty `acceptance_scenarios` — tension with CLAUDE.md principle 8 and the G0 requirement "Acceptance scenarios exist" (`docs/GATES_AND_CHECKPOINTS.md`, G0). Tolerable for the lifecycle smoke test itself; must not recur.
- The producer report is one line ("commands executed with recorded outputs") without the actual outputs — G2 requires "exact commands and outputs" (`docs/GATES_AND_CHECKPOINTS.md`, G2) and the return packet of `docs/AGENT_OPERATING_SYSTEM.md` §6. Future producer reports must include real command output.
- CP-0001/CP-0002 record `"commit": "none-pre-git"` — checkpoints must record real commit hashes now that git exists (`docs/GATES_AND_CHECKPOINTS.md`, "Each checkpoint records: Repository commit and branch").

### E3 — Supabase MCP configured; management API unauthorized; "recorded as human action": **PARTIALLY UNSOUND as executed**
The Supabase MCP server is registered in the agent environment (tools are present), but:
1. **No blocker record exists.** `project-control/blockers/` is empty and no grep hit for `SUPABASE_ACCESS_TOKEN` exists anywhere in `project-control/`. CLAUDE.md principle 13 requires: "Stop and create a blocker when a legal interpretation, secret, payment, production approval, or unavailable credential requires a human." G0 requires "Required credentials are available or a blocker is recorded." The claim "recorded as human action" is **not supported by repository evidence** — this is exactly the class of unsupported claim the control system exists to prevent.
2. The MCP configuration is user-level only; no project-level `.mcp.json` (or documented equivalent) is committed, so the environment is not reproducible from the repo. Document the MCP server configuration (without secrets) in the repo.

### E4 — Render not connected; human action "to be recorded": **UNSOUND as executed (same defect)**
No blocker file exists for Render either. Vercel connection state is likewise unrecorded. Since M0's exit criteria include the Supabase/Render/Vercel environment plans and deployment procedures (`docs/IMPLEMENTATION_SEQUENCE.md`, M0; PRD §26 Phase 0), the unavailable credentials are on the critical path and **must** be tracked as formal blockers, not narrative intentions.

### E5 — Planned architecture (Supabase / Render / Vercel / GitHub Actions; owner PC as thin client): **SOUND (plan matches governing documents)**
The planned provider split matches PRD §14.1 exactly (Supabase: Postgres/PostGIS/Auth/RLS/Storage/pgvector/migrations/audit; Render: FastAPI + workers + scheduled jobs; Vercel: Next.js + previews; GitHub: code/CI). It matches `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md` (mandatory cloud architecture) and CLAUDE.md principle 5. Treating the PC as a thin client with a 4 GB floor matches PRD §35 and CLAUDE.md principle 14. The cloud-architect preference for a modular monorepo, one FastAPI web service, and scalable Render workers (`.claude/agents/cloud-architect.md`) is consistent with PRD §14.2 (workers separate from Edge Functions).
Caveat: it is **only a plan**. Nothing of Phase 0 exists yet: no monorepo skeleton, no `.github/workflows` CI, no `supabase/` migrations dir, no `.env.example` (the `.gitignore` whitelists `!.env.example` but none exists), no ADRs, no environment separation, no RLS baseline. These are tracked below as gaps, not contradictions.

### E6 — `.gitignore`: **SOUND**
Covers every category required by the policy's "Repository hygiene" list: `node_modules/`, venvs, `.next!/build/coverage/caches`, local DBs and `.supabase/`, datasets/GIS exports (`data/`, `*.shp`, `*.gpkg`, `*.parquet`, ...), source snapshots, generated reports, test recordings, worktrees, `.env*` with `!.env.example`. No gaps found against `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md` §"Repository hygiene".

## 3. Low-storage verdict (S2)

**Verdict: the planned local footprint respects the 4 GB floor — with thin headroom that must be actively managed.**

- Measured now: **6,349,840,384 bytes free ≈ 5.91 GiB (6.35 GB decimal)** on C:. Bootstrap reported "~6.1 GB free"; the figure is consistent within unit ambiguity (GB vs GiB) and normal drift. No evidence bootstrap consumed meaningful space: the entire repo including `.git` is ≈ 0.2 MB, and this review adds < 1 MB.
- Headroom above the 4 GB floor is ≈ **1.9–2.35 GB**, i.e. **less than the 2 GB discretionary budget** in the policy. Practical consequence: the "do not intentionally consume more than 2 GB" allowance can never be fully used — the binding constraint is the 4 GB floor, so the true local budget is ≈ 1.9 GB. A single local `npm install` of a Next.js app or a Python venv with GIS wheels could consume most of it.
- Therefore the plan is compliant **only if** enforced as written: no local Docker/Supabase/Postgres, no dataset downloads, dependency installation and builds/tests in GitHub Actions/Codespaces, migrations run against remote Supabase (policy §"Prohibited local operations" and §"Required implementation behavior"). Every G0 must keep documenting execution location and expected disk use, as the three bootstrap G0 readiness reports correctly did (each states "local text only, <1 MB disk").

## 4. Contradictions with PRD/policy (S3)

| ID | Finding | Contradicts |
|---|---|---|
| C1 | Missing SUPABASE_ACCESS_TOKEN and unconnected Render/Vercel are not recorded as blockers; `project-control/blockers/` is empty | CLAUDE.md principle 13; `docs/GATES_AND_CHECKPOINTS.md` G0 ("Required credentials are available or a blocker is recorded") |
| C2 | 10 control-plane files (tasks/gates/reports for M0-T001..003, `tools/enrich_bootstrap_tasks.py`) exist only on the local PC, uncommitted and unpushed | `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md` ("local PC must never be the only location of code, configuration ... or project data"); `docs/PROJECT_CONTROL_PROTOCOL.md` (ledger = source of truth) |
| C3 | `state.json` shows `accepted_tasks: []` and `active_tasks: []` despite M0-T000 `accepted` and M0-T001/2/3 `claimed` — the CLI's accept/claim paths do not maintain the state rosters | `docs/PROJECT_CONTROL_PROTOCOL.md` ("Every status transition must be recorded"); CLAUDE.md start-of-session routine relies on `state.json` being truthful |
| C4 | `M0-T000.json` has empty `acceptance_scenarios` | CLAUDE.md principle 8; `docs/GATES_AND_CHECKPOINTS.md` G0; `docs/PROJECT_CONTROL_PROTOCOL.md` task-packet fields |
| C5 | CP-0001/CP-0002 record `commit: "none-pre-git"` (no usable commit reference) | `docs/GATES_AND_CHECKPOINTS.md` checkpoint requirements ("Repository commit and branch") |
| C6 | Three parallel tasks claimed with `worktree: "local"` on `main`, no `task/<task-id>` branches | `docs/PROJECT_CONTROL_PROTOCOL.md` worktree/branch convention; CLAUDE.md principle 10. Mitigated: all three are read-mostly with disjoint single-file outputs, so overlap risk is low — but the convention should be followed or a documented exception recorded |
| C7 | Producer evidence for M0-T000 lacks actual command outputs | `docs/GATES_AND_CHECKPOINTS.md` G2; `docs/AGENT_OPERATING_SYSTEM.md` §6 ("A subagent report is not proof. Executable evidence is proof.") |

No element of the bootstrap **plan** itself contradicts PRD §14/§15/§26/§32 — the contradictions above are all execution/recording defects, not architectural ones.

## 5. Gaps and risks in the M0→M1 plan (prioritized)

1. **Cloud credentials untracked (C1)** — Supabase management token, Render, and Vercel access gate every remaining M0 deliverable (environments, auth, RLS, deploy/rollback procedures). Currently invisible to the control plane.
2. **No CI** — no `.github/workflows`. PRD §26 Phase 0 requires CI, and the low-storage policy requires builds/tests to run in GitHub Actions rather than locally. Until CI exists there is no compliant place to run test suites.
3. **Control-plane integrity (C2 + C3)** — unpushed ledger plus a `state.json` that under-reports status will corrupt the mandatory start-of-session reconciliation and any `/status-board` or `/replan-project` output. Fix the CLI state-sync defect and adopt a commit-after-transition cadence.
4. **No monorepo skeleton** — PRD §26 Phase 0 and `docs/IMPLEMENTATION_SEQUENCE.md` M0 require the monorepo. Decide and record the layout (suggested, per cloud-architect charter: `apps/web` (Next.js), `services/api` (FastAPI), `services/workers`, `packages/contracts` (canonical property-profile contract per PRD §32.3), `supabase/migrations`, `docs/adr/`).
5. **Secrets handling undefined** — no `.env.example`, no ADR/document mapping which secret lives where (GitHub Actions secrets, Render env groups, Vercel env vars, Supabase vault), no statement of the PRD §31 rule that service-role keys never reach the frontend. Required before any service code lands (G5 scope).
6. **Dev/staging/prod separation undefined** — PRD §26 Phase 0 and M0 exit criteria require it; the low-storage policy additionally requires remote dev/staging Supabase projects for migrations. Needs an ADR: three Supabase projects (or branching), matching Render services and Vercel environments, and promotion rules.
7. **RLS baseline absent** — CLAUDE.md principle 11 ("All exposed Supabase tables use tested RLS") and M0 scope ("authentication, organizations, RLS baseline"). Must land with the first migration (organizations/organization_members/user_profiles per PRD §15), with RLS tests as G5 evidence — blocked on credentials (item 1).
8. **Disk headroom thinner than the nominal budget** — effective local budget ≈ 1.9 GB, not 2 GB (see §3). Any local dependency install should be treated as prohibited-by-default; add a disk check to the session routine.
9. **Environment reproducibility** — Supabase MCP configuration is user-level only; document it (tokenless) in the repo so a rebuilt machine or second operator can restore the toolchain.
10. **Direct task-file mutation via one-off script** — `tools/enrich_bootstrap_tasks.py` edits task packets outside `project_control.py` transitions. Acceptable as an orchestrator bootstrap action, but the pattern weakens the "recorded by tools/project_control.py" rule; fold packet-enrichment into the CLI or delete the script after committing it for the record.
11. **No ADRs yet** — the provider selection and monorepo decision are material architecture decisions; the cloud-architect charter requires ADRs. Record ADR-0001 (cloud architecture) and ADR-0002 (environment separation) so M1+ agents inherit decisions rather than re-deriving them.

## 6. Single highest-risk item

**C1 — unrecorded cloud-credential blockers (Supabase management token; Render and Vercel not connected).** It is the critical path for every remaining M0 deliverable, and because no blocker exists, the control plane currently reports an unobstructed project while the true state is "cloud foundation blocked on human action." This combines a schedule risk with a control-integrity risk: the exact failure mode (unsupported narrative claims about project state) that the gate system was built to prevent. Remediation is cheap: record the blockers now and hand the owner a one-page checklist (create/confirm Supabase org + `SUPABASE_ACCESS_TOKEN`, Render account + API key, Vercel account/team, GitHub Actions secrets).

## 7. Recommended next tasks for M0

| Proposed task | Producer | Gates | Notes |
|---|---|---|---|
| M0-T004 Record credential blockers + owner action checklist (Supabase token, Render, Vercel, GH Actions secrets) | orchestrator | G0 | Unblocks visibility immediately; human performs only the account/secret actions (CLAUDE.md "Human-only actions") |
| M0-T005 Fix `project_control.py` state-sync (accepted/active/blocked rosters in `state.json`) + negative tests | backend-engineer | G0,G3 | Addresses C3; small, testable |
| M0-T006 Commit/push untracked ledger files; adopt commit-after-transition cadence rule | orchestrator | G0 | Addresses C2; near-zero effort |
| M0-T007 Monorepo skeleton + GitHub Actions CI (lint/type-check/test on PR; path filters; no local installs) | backend-engineer / frontend-engineer | G0,G3,G4 | Runs in Actions per low-storage policy; local checkout stays source-only |
| M0-T008 Secrets policy + `.env.example` set + secret-store mapping doc | cloud-architect (producer) → security-reviewer (gate) | G0,G3,G5 | PRD §31, §14.3 |
| M0-T009 ADR-0001 cloud architecture + ADR-0002 dev/staging/prod separation + deployment/rollback procedures | cloud-architect | G0,G3 | M0 exit criterion ("Record deployment and rollback procedures") |
| M0-T010 Auth + organizations + RLS baseline (remote migrations, RLS tests) | supabase-engineer | G0,G3,G4,G5 | Depends on M0-T004 clearing; first PRD §15 identity/tenancy tables |

## 8. Reviewer disclosure

- I verified every bootstrap claim independently from git, `gh`, the filesystem, and PowerShell disk measurement; I did not rely on the bootstrap narrative.
- Not re-verified (out of allowed scope/network): the live "unauthorized" state of the Supabase management API (would require a network call beyond git/gh), and any user-level MCP configuration outside the repo. Both are noted where relevant.
- This review wrote exactly one file (this report, < 25 KB) and used CLI transitions only (`claim`, `progress`, `submit`). No implementation or control files were modified.
- Per CLAUDE.md principle 7, this task is submitted for independent gate review and is **not** self-accepted.
