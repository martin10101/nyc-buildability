# Bootstrap Report — NYC Buildability

Date: 2026-07-14. Author: orchestrator. Companion docs: CONNECTION_AUDIT.md, STORAGE_BUDGET.md, HUMAN_ACTIONS_REQUIRED.md, MASTER_EXECUTION_PLAN.md, IMPLEMENTATION_STATUS.md, RISK_REGISTER.md.

## 1. Project root

The project root is `nyc-development-feasibility-claude-pack/` inside the owner's `nyc zoning` folder. It contains CLAUDE.md, PRD.md, README_START_HERE.md, `.claude/agents|skills|rules`, `docs/`, `tools/`, and `project-control/`. All governing documents (CLAUDE.md and all its imports, README, both changelogs) were read in full before any action.

Note: the Claude Code session is rooted one level up (`nyc zoning/`), which affected native subagent registration (see §4).

## 2. Subagent inventory (16 project agents in `.claude/agents/`)

| Subagent | Responsibility | Tools | Kind | Independent reviewer of its work |
|---|---|---|---|---|
| orchestrator | Task contracting, delegation, gate evaluation, acceptance, replanning | Read, Write, Edit, Bash, Grep, Glob, Agent, Skill | Orchestrator | Human owner (production/legal approvals); progress-auditor audits its ledger |
| backend-engineer | FastAPI, contracts, connectors, jobs, provenance, state machine | RW+Bash (worktree) | Producer | code-reviewer + qa-engineer; data-contract-verifier for connectors; security-reviewer for G5 scope |
| supabase-engineer | Postgres/PostGIS/Auth/Storage/pgvector, migrations, RLS | RW+Bash (worktree) | Producer | security-reviewer (G5) + qa-engineer |
| geospatial-engineer | PostGIS imports, CRS, lot geometry, intersections, split lots | RW+Bash (worktree) | Producer | qa-engineer + data-contract-verifier (GIS sources) |
| frontend-engineer | Property/Confirm/Compare/Evidence + admin UIs, Playwright packs | RW+Bash (worktree) | Producer | human-journey-reviewer (G3) + code-reviewer |
| rules-engineer | Rules DSL, deterministic evaluator, tests, releases | RW+Bash (worktree) | Producer | code-reviewer + qa-engineer; human zoning reviewer at G6 |
| scenario-optimization-engineer | Constraint solving, objectives, diversity, scoring | RW+Bash (worktree) | Producer | qa-engineer + code-reviewer |
| legal-corpus-engineer | Legal ingestion, hierarchy, versions, diffs, embeddings | RW+Bash+WebFetch (worktree) | Producer | data-contract-verifier + security-reviewer (injection) |
| ai-pipeline-engineer | Schema-constrained extraction, RAG, injection defenses, cost tracking | RW+Bash (worktree) | Producer | security-reviewer + qa-engineer |
| official-source-researcher | Official API/dataset research, source registry evidence | WebSearch/WebFetch + RW | Researcher | data-contract-verifier (G1) |
| cloud-architect | ADRs, service boundaries, tenancy, deployment, observability | RW+Bash (worktree) | Producer/Reviewer | code-reviewer or orchestrator (must differ from producer per task) |
| code-reviewer | Read-only senior code review | Read-only+Bash (plan mode) | Reviewer | n/a (produces gate reports only) |
| data-contract-verifier | Independent G1 verification of connectors/mappings | Web + read-only | Reviewer | n/a |
| security-reviewer | G5 security/privacy gates | Read-only+Bash | Reviewer | n/a |
| human-journey-reviewer | G3 human-style walkthroughs | Read-only+Bash | Reviewer | n/a |
| qa-engineer | Test creation + independent gates | RW+Bash (worktree) | Producer/Reviewer | May never review its own work; code-reviewer reviews its test code |
| progress-auditor | Ledger-vs-reality reconciliation | Read-only+Bash | Researcher/Reviewer | orchestrator (G3 on audit deliverables) |

All 16 files have valid frontmatter and unique names. Reviewer agents run in plan/read-only mode; producers use worktree isolation.

## 3. Control-plane verification (the requested lifecycle test)

`python tools/project_control.py` init/status ran clean. A real task (M0-T000) was pushed through the entire lifecycle: new-task → G0 → claim → progress → submit → gate FAIL → rework → resubmit → gate PASS → orchestrator accept → checkpoint. Negative authority tests all rejected correctly:
- producer setting 100% — rejected (exit 2)
- producer gating its own task — rejected (exit 2)
- non-orchestrator accepting — rejected (exit 2)
- acceptance with missing required gates — structurally impossible (gate set check)

### Defects found in the control plane and fixed (committed)
1. **BOM crash**: `load()` used strict `utf-8`; Windows PowerShell 5.1 `Set-Content -Encoding utf8` writes a BOM → gate/accept crashed. Fixed with `utf-8-sig`. Standing rule: agents write files with the Write tool.
2. **Dead state fields** (found independently by progress-auditor and cloud-architect): `state.json` rosters were only written by `checkpoint`. Fixed with `sync_state()` called on every claim/progress/submit/gate/accept.
3. **Gate history erasure** (found by progress-auditor): re-recording a gate overwrote the previous record, erasing the FAIL trail. Fixed: prior results preserved in a `history` array.

## 4. Subagent operational proof

Native `subagent_type` resolution failed for project agents: the Agent-type registry is snapshotted at session start, and this session started from the parent folder before the pack agents existed there. **Repair applied**: all 16 agent definitions copied to the session's `.claude/agents/`; they will register natively next session. **No restart is required to continue** — the same three delegations ran as parameterized workers bound to each agent's definition file and ledger identity:

| Task | Agent identity | Result |
|---|---|---|
| M0-T001 repository/control-system audit | progress-auditor | 3 verifications, 8 discrepancies (D1–D8) with evidence paths; submitted awaiting_gate; G3 PASS; ACCEPTED |
| M0-T002 official-source discovery (address/BBL/BIN) | official-source-researcher | Geoclient v2 documented from official sources with retrieval dates; UNKNOWNs explicitly marked; 16-fixture contract-test plan; live keyless GeoSearch response captured; awaiting G1 |
| M0-T003 independent bootstrap review | cloud-architect | Element-by-element verdicts; caught 2 unrecorded credential blockers + 7 contradictions with citations; G3 PASS; ACCEPTED |

Producer/reviewer separation held throughout: producers only submitted; gates were recorded by different identities; only the orchestrator accepted. All delegations and results are in `project-control/` (tasks, reports, gates).

## 5. Connections (detail in CONNECTION_AUDIT.md)

Tested and working: terminal, file editing, Git, GitHub (gh authenticated as martin10101), web research. Authentication required: Supabase MCP (B-001). Human action required: Render (B-002), Vercel (B-003), Geoclient key (B-004). Deferred by policy: local browser automation, Docker (prohibited), local Supabase CLI. GitHub Actions: authorized (workflow scope) but unproven until the first workflow lands (M0-T004).

## 6. Git and GitHub

- Repo initialized at the project root on `main`; local identity set (martin10101 / owner email) because the global git identity was a placeholder.
- `.gitignore` verified against the low-storage policy (dependencies, datasets, GIS files, builds, local DBs, recordings, secrets, worktrees).
- Initial commit `8ba7278` pushed to **private** repo `martin10101/nyc-buildability` (visibility verified via gh).

## 7. Storage

6.09 GB free at start; ~6.35 GB (decimal) measured after bootstrap; repo footprint ≈ 0.2 MB. The binding constraint is the 4 GB floor → true discretionary headroom ≈ 1.9 GiB. All dependency-heavy work is routed to cloud (GitHub Actions/Codespaces/Render/Supabase). Details: STORAGE_BUDGET.md.

## 8. Architecture decision

The repository architecture stands: Supabase (Postgres/PostGIS/Auth/Storage/pgvector) + Render (FastAPI, workers, cron; replaces Railway) + Vercel (Next.js) + GitHub (code/CI). The cloud-architect's independent review found the plan consistent with PRD §14/§35 and the low-storage policy; no ADR proposing an alternative was warranted. ADRs formalizing environment separation and deploy/rollback are task M0-T006.

## 9. Decisions of record

1. Gate-set narrowing: task packets may narrow config-default gates when a gate family is objectively not applicable (e.g., G1 for tasks with no external source). The narrowing rationale must appear in the G0 readiness record. (Response to audit finding D1.)
2. `tools/enrich_bootstrap_tasks.py` was an authorized orchestrator edit of task packets; retained in git for the evidence trail. `forbidden_paths` bind producers, not the orchestrator. (D4.)
3. Producer reports must embed actual command outputs from now on. (D6/C7.)
4. Branch/worktree convention becomes mandatory with the first writing task (M0-T004 onward); read-only bootstrap tasks ran on `main` deliberately. (C6.)

## 10. State at end of bootstrap

3 tasks accepted, 1 awaiting G1, 4 blockers open (all with exact minimal human actions), master execution plan published, first unblocked implementation task: **M0-T004 monorepo skeleton + GitHub Actions CI**.
