# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, and workflow routes live in `CLAUDE.md`.

## Where main is
- **Accepted-task count = 49** (last two: M0-T030, M0-T031 — the D-005 code-navigation-graph lane).
  Latest checkpoints CP-0032/CP-0033. Main advanced through PRs #112–#118 this window
  (D-005 capture/amendments, M0-T030 implementation+acceptance, M0-T031 implementation+acceptance).
- On resume `git fetch` and take the current `origin/main`.

## Active directives (regime ON — every new/reclaimed task must cite directive_refs)
- **D-001** active — Owner Directive Compliance System.
- **D-002 / D-003** active — first wave complete and integrated (M2-T017, M4-T007, M3-T001 accepted);
  the **second wave is intentionally NOT contracted** (owner decides).
- **D-004** active — Agent-Teams runtime adoption, STAGED. Step 1 done (evidence accepted as-is),
  Step 2 probe done; **M0-T027 blocked** pending the on-policy re-run after the B-015 fix;
  **M0-T028** (B-015 diagnosis/fix) packet presented — **must NOT start before owner reviews it**;
  Steps 3–5 each need an explicit owner GO. Spawn rule: explicit model per teammate spawn
  (Fable 5 gate-class reviewers / Opus 4.8 producers). **Never write an effort key anywhere**
  (permanent owner hold; session effort stays xhigh, global).
- **D-005** active — codebase knowledge graph. **Graphify = owner-ratified WAIT (do not install,
  do not reopen).** In-house graph BUILT and accepted instead (M0-T030), hardened + routing-guided
  (M0-T031). Owner decision on the packet: **GO WITH CONDITIONS — SELECTIVE use, never universal
  graph-first; no token/time-savings claims without new measured evidence.** Reserved surfaces
  (Mission Control map, layer-B project graph, six-PRD audit usage, NYC Evidence KG, any Agent-Teams
  auto-injection) each need a separate owner GO.

## What now works (new since last handoff)
- **Code-navigation graph** (`tools/code_graph/`): stdlib-only deterministic index of
  services/api + apps/web/src + packages/contracts + tools. Bounded query CLI
  (`python tools/code_graph/query.py --limit N <find|file|module|upstream|downstream|neighbors|contracts|path|impact>`;
  `--limit` also accepted after the subcommand). Artifacts are NEVER committed — out-of-repo cache,
  fingerprint + graph_sha256 verified on every load (tamper/corruption ⇒ regenerate or refuse).
  Selective-routing rules: `tools/code_graph/README.md` (decision model + when-to/when-not lists).
  Benchmark truth: improves correctness/completeness (18/18 vs 15/18), does NOT reduce operations.
  CI job `code-graph` proves determinism on every push.
- First-wave deliverables unchanged: M2-T017 closed contracts + frozen (unwired) serializer;
  M4-T007 exact legal arithmetic (B-014 resolved); M3-T001 legal-source authority pack (unlocks M3-T002).

## Milestone reality
- **M0** active — accepted through M0-T031 except: M0-T025 (LOW-1 backlog), M0-T026 (D-003 anchor,
  backlog), M0-T027 (blocked, D-004), M0-T028 (backlog, awaiting owner packet review), M0-T019
  (HELD — B-013 owner declined the age exception; check ledger for current eligibility; PR #64),
  M0-T007/T008 (blocked by B-001). M0-T029 reserved for D-004 Step 5.
- **M1** complete. **M2** active (M2-T014/15/16 survey HELD). **M3** planned — M3-T002 is the next
  lane, blocked by B-001 + durable-storage acceptance path. **M4** active — T001..T006 merged DRAFT,
  G6-gated (0 published). **M5/M6/M7** planned.

## Holds / blockers (ALL still standing unless the ledger says otherwise)
- **G6** legal approval blocks all M4 rule acceptance/publication. **B-001** Supabase token
  (M0-T007/T008, M3-T002/T003/T005, auth/RLS). **B-002** Render. **B-004** Geoclient. **B-010**
  benchmark. **B-011** construction-code scope (owner-controlled). **B-012** deploy hold. **B-013**
  frontend age exception DECLINED. **B-015 OPEN** — teammate readonly-guard bypass (fix = M0-T028;
  do not trust hook confinement for Agent-Teams teammates). **LOW-1** (M0-T025). Expansion-planning
  hold (`.claude/rules/expansion-agent-dispatch-hold.md` §2) + survey hold remain. Graphify WAIT.

## Non-blocking follow-ups (logged, not tasked)
- M4-T007 G5 LOW (bound to_exact/quantize exponents); M2-T017 G5 LOW (bound input_vintages when
  wired); stale source_fact comments in pluto_soda/ztldb_soda; M3-T001 check-script docstring path.
- Code-graph INFO items (G3/G5, M0-T031 reports): missing-graph_sha256 fixture test; query.py
  docstring headline; 33 orphaned `.claude/worktrees` husks (cleanup NOT authorized — separate
  owner proposal).

## Next action
Owner's call among: (a) D-004 Step 3 — review the M0-T028 packet and GO; (b) second-wave lanes
(M2-T017 serializer wiring; DF-6 hardening; M3-T002 if B-001 resolves); (c) any code-graph reserved
surface (each a separate GO); (d) unblock items requiring owner-only authority (B-001/B-002/B-011,
G6 reviewer). Do not begin untracked work; contract via `/start-controlled-task` with directive_refs.
