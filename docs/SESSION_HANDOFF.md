# Session Handoff — resume state as of 2026-07-20 (session 16: M0-T020 ACCEPTED 39th; M0-T019 DISPATCHED to frontend-engineer)

> **P0 DEPENDENCY-SECURITY WAVE — M0-T020 ACCEPTED (39th, live on main); M0-T019 DISPATCHED.** PR #62 (M0-T020 acceptance control) merged to main at `9391bb09cf491570e5fb5b5c8e17b2d2ba6b2195`; M0-T020 is the 39th accepted task, live on main. M0-T019 (frontend Next/React security upgrade + permanent npm dependency-admission policy) has been dispatched to **frontend-engineer** (G0 PASS + claim recorded via this M0-T019 dispatch control PR); it is the active P0 task. **>>> RESUME POINT: M0-T019 implementation is IN FLIGHT under owner authorization 2026-07-20 (dispatch → implement → CI → independent review). The authorization ENDS at an open, fully-checked, independently-reviewed M0-T019 TASK PR + return packet — the task PR is NOT to be merged, M0-T019 is NOT to be accepted, and NO acceptance gates/checkpoint are recorded without a separate owner instruction.** Checkpoint remains `CP-0031` (next checkpoint deferred). Do NOT merge the M0-T019 task PR, accept M0-T019, create a checkpoint, run Phase 2c, dispatch M2-T013/M2-T014 or any held task, or release any hold WITHOUT explicit owner authorization. The ledger (`project-control/`) is the source of truth; this file is the conversation-independent resume pointer.

Written by the orchestrator. Open this folder (`nyc-development-feasibility-claude-pack`) as the workspace root, then follow CLAUDE.md's start-of-session routine.

## Checkpoint rule (approved M0-T020 packet — do not violate)

Per `project-control/tasks/M0-T020.json` (SEQUENCING + CHECKPOINT): **NO checkpoint is recorded from M0-T020 alone.** The next checkpoint follows ONLY after ALL of: (1) M0-T020 accepted ✓, (2) M0-T019 accepted, (3) Phase 2c reconciliation complete, and (4) complete Python AND npm audits green on reconciled main. Until then, `state.json last_checkpoint` stays **CP-0031**.

## Paste-ready prompt for the new session

> Read CLAUDE.md, docs/SESSION_HANDOFF.md, and the always-loaded rules (.claude/rules/expansion-agent-dispatch-hold.md + 3d-ui-expansion.md attach unconditionally; project-control.md attaches on project-control reads). Run `python tools/project_control.py status`; reconcile with git (`git status -sb` + `git ls-remote origin refs/heads/main`). Expected: ledger 39 accepted / 2 blocked (M0-T007/T008) / 7 backlog / 1 claimed (M0-T019); checkpoint CP-0031; main at the M0-T019 dispatch control PR merge SHA (advanced from `9391bb0` = the PR #62 / M0-T020 acceptance merge). M0-T019 is `claimed` by frontend-engineer. If an M0-T019 **task PR** is open, it is the in-flight implementation — do NOT merge it or accept M0-T019 without explicit owner authorization. HARD RULES: (1) protected-main PR workflow — NEVER push to main; task/control branch → push → `gh pr create --head <branch>` → wait checks green (FOREGROUND polls) → `gh pr merge --merge --delete-branch --match-head-commit <SHA>` → `git fetch` + `git merge --ff-only origin/main` → verify ls-remote AND remote-branch deletion. (2) HARDENED project_control.py — G0 PASS moves backlog→ready; claim needs `ready`; submit reaches `awaiting_gate`; G2 = `--reviewer orchestrator` self_check; independent gates (G3/G4/G5) need a rostered reviewer ≠ producer; orchestrator REJECTED in independent rosters; accepted tasks IMMUTABLE; report paths must EXIST in the checkout when the CLI runs (record acceptance gates AFTER the task PR merges, in a later acceptance control PR). (3) ADR-005 — only the orchestrator runs project_control.py/git/gh; producers edit files + return a report (no git); reviewer returns preserved VERBATIM. (4) THIN-CLIENT — no local node_modules/npm on the owner PC; the web lockfile regenerates on a GitHub runner via `.github/workflows/generate-lockfile.yml` (workflow_dispatch). SHELL: Bash and PowerShell SHARE a persisted cwd — after any `cd`, run `cd "$(git rev-parse --show-toplevel)"` before relative-path CLI reads, or use `git -C`. TEXT: the tool-call JSON layer decodes backslash-u escapes into literal bytes — write word forms. IDE: background-task completion does NOT re-invoke the session — run CI waits in the FOREGROUND (bounded polls in-turn). Permission posture: auto mode, ask only for deletions. Pause only for secrets, billing, production approvals, professional legal review, or pending owner decisions.

## Exact repository state

- **main = remote main** at the **M0-T019 dispatch control PR merge** (advanced from `9391bb09cf491570e5fb5b5c8e17b2d2ba6b2195`, the PR #62 M0-T020-acceptance merge; parents `4693ca4` + `9bddf82`). During M0-T019 Phase 3 an **M0-T019 task PR** is opened and left OPEN + independently reviewed (not merged).
- **Ledger: 39 accepted / 2 blocked / 7 backlog / 1 claimed (M0-T019).** Before the M0-T019 dispatch it was 39/2/8/0. **Checkpoint remains CP-0031** (next checkpoint deferred per the packet rule above).
- **M0-T020 — ACCEPTED (39th), live on main** via PR #62 (`9391bb0`). Reviewed task PR #60 head `9da5449` merged at `4693ca4`; gates G0/G2 orchestrator + G3/G4 code-reviewer + G5 security-reviewer PASS. Python dependency-policy enforcement (hash-pinned tooling lock + machine release-age gate + CI hardening); production lock `requirements.txt` byte-identical; 3 non-blocking observations dispositioned. **Immutable — do not reopen.**
- **M0-T019 — CLAIMED by frontend-engineer; dispatched; implementation IN FLIGHT.** Frontend Next/React security upgrade + permanent npm dependency-admission policy (`project-control/tasks/M0-T019.json`); deps [M0-T018 ✓, M0-T020 ✓]. Targets (PROVISIONAL — re-verified live at implementation): next==15.5.20, react==19.1.2, react-dom==19.1.2, eslint-config-next==15.5.20, `overrides.postcss`==8.5.10; npm 11.18.0; `.npmrc` min-release-age=7 + save-exact=true; blocking `npm audit --audit-level=low` JSON total==0 (incl. dev); scheduled npm re-audit; adds `docs/DEPENDENCY_SECURITY_POLICY.md` + a concise CLAUDE.md rule. Current `apps/web/package.json`: next 15.3.4, react/react-dom 19.1.0, eslint-config-next 15.3.4 (no `overrides`, no `.npmrc`). Lock regenerates remotely via `generate-lockfile.yml`. Gates G0 (orchestrator) recorded; G2 self-check + G3/G4 code-reviewer + G5 security-reviewer pending. **The task PR stays OPEN + reviewed; acceptance gates + acceptance ride a LATER owner-authorized acceptance control PR.**
- **M0-T018 (38th, ACCEPTED, IMMUTABLE)** — backend production dependency parity + Python supply-chain enforcement (task PR #55 `7ffd542`, acceptance PR #56 `270e81b`).
- **Repo PUBLIC** (owner 2026-07-20); ruleset `protect-main` active; secret scanning + push protection ON. Blockers B-005/B-006/B-007/B-008/B-009 RESOLVED.
- **Worktrees:** M0-T019 producer works in an isolated worktree (`.claude/worktrees/M0-T019-frontend` on `task/M0-T019-frontend-security`). `agent-a501f3e0a11bdd091` (STOPPED Phase-B pre-amendment research; superseded untracked draft) still exists — later hygiene. Older harness-managed stale `agent-*` worktrees (two locked — leave them).
- **Working tree:** clean except `.claude/agent-memory/**` (permitted).

## >>> What is done and what is next

**Done:** M0-T020 accepted + live on main (PR #62 merged, main reconciled `9391bb0`). M0-T019 dispatched: G0 PASS + claim to frontend-engineer via this dispatch control PR; handoff updated. **In flight (owner-authorized Phase 3):** frontend-engineer implements the full M0-T019 packet in an isolated worktree; live npm-registry target re-verification; remote lock regen; CI npm hardening (npm 11.18.0 pin, blocking audit, scheduled npm re-audit); policy doc + CLAUDE.md pointer; task PR opened + G3/G4 code-reviewer + G5 security-reviewer against the exact task head. **The task PR is returned OPEN + reviewed, NOT merged.**

**Next (owner's SEPARATE instruction only):** owner reviews the open, reviewed M0-T019 task PR → authorizes acceptance → orchestrator merges the task PR → records acceptance gates + accept in a LATER acceptance control PR. Then **Phase 2c** (reconcile + re-run BOTH complete audits on reconciled main) → **THEN the next checkpoint** (first eligible: M0-T020 + M0-T019 accepted + Phase 2c + both audits green) → **Phase 3** feature work (M2-T013 + M2-T014) only when the owner releases those holds.

## Session 16 log (what shipped)

1. Reconciliation: remote main had advanced `0572d09`→`84a0287` via control-only PR #61 (session-15 reviewer reports onto main); benign.
2. **M0-T020 acceptance** (owner-authorized, two-step): merged reviewed task PR #60 (`9da5449`) → `4693ca4`; recorded lifecycle + gates in acceptance control PR #62. Owner correction: withdrew a premature CP-0032 (packet defers the next checkpoint); kept CP-0031; corrected a stale packet clause. Merged PR #62 → `9391bb0` (M0-T020 live, 39th).
3. **M0-T019 dispatch** (owner-authorized): preflight verified; G0 PASS + claim to frontend-engineer; this dispatch control PR updates the handoff; then Phase 3 implementation + open reviewed task PR.

## Prior sessions (condensed; full detail in git history + agent-memory)

- **S15:** M0-T020 implemented + reviewed (PASS/PASS); bounded pytest 9.0.3 amendment (PR #59).
- **S14:** accepted M0-T018 (38th) — backend production dependency parity + Python supply-chain enforcement.
- **S13:** accepted M2-T011 (36th) + M2-T010 (37th) at CP-0031.
- **S12:** accepted M2-T007 (33rd), M2-T008 (34th; repo made PUBLIC), M2-T009 (35th).

## Hardened control plane (READ BEFORE ANY LEDGER OPERATION)

G0 PASS moves backlog→ready; `claim` requires `ready` and sets `claimed`/10; `submit --requested-status awaiting_gate` reaches the acceptance-eligible state; orchestrator REJECTED in independent rosters/gates; G2 recorded `--reviewer orchestrator` (self_check); accepted tasks IMMUTABLE; `submit` writes `reports/<task-id>.json`; report paths repo-relative and MUST EXIST in the checkout when the CLI runs (acceptance gates/accept therefore record AFTER the task PR merges — the M2-T007 / M0-T018 / M0-T020 pattern). `accept` preconditions: status `awaiting_gate` + all required gates PASS (independent gates need role `independent_review`, reviewer ≠ producer) + all dependencies accepted + zero OPEN blocker references the task. `checkpoint` is recorded only when the packet's sequencing rule permits.

## Blockers

**B-001** (HIGHEST — Supabase token; blocks M0-T007/T008 + persistence/citywide-import slices), **B-002** (Render), **B-004** (Geoclient). B-003 closed; B-005/B-006/B-007/B-008/B-009 resolved.

## Owner decisions pending

1. **Review + accept the open, reviewed M0-T019 task PR** (then authorize its merge + a later acceptance control PR) — the immediate resume gate after Phase 3.
2. Release the DISPATCH HOLDS on the survey workstream (M2-T014/T015/T016), M2-T013, M4-T001.
3. Credentials when ready: B-001 (highest), B-002, B-004.
4. GDS/expansion planning review (counter-notice §2 hold).
5. CORS/proxy decision (M2-T001 D8) — deploy-blocking; no urgency while B-001 no-deploy stands.
6. M2-T016 professional-confirmation role definition.

Decisions RESOLVED 2026-07-20: next-wave approval; M2-T013 policy knobs C1–C4; first M4 rule family = R5; OQ-3 owner-deferred/non-blocking; M0-T020 pytest 9.0.3 bounded amendment; M0-T020 acceptance + PR #62 correction; **M0-T019 dispatch/implementation/CI/independent-review authorized (task PR NOT merged, no acceptance/checkpoint without a separate instruction).**

## Holds this run (do NOT dispatch / do NOT release)

M2-T012, M2-T013, M2-T014, M2-T015, M2-T016, M4-T001, M6-T001; survey Packets B/C (M2-T015/T016; B-001 still blocks production storage). M4-T001 remains R5-first but waits; M2-T012 and M4-T001 both may touch contract tooling/artifacts — never run concurrently without a later owner-approved non-overlap plan. All GDS/expansion (counter-notice §2) and 3D holds preserved. M0-T019 task PR: open + reviewed, NOT merged.

## Standing carry-forwards (non-blocking; unchanged)

M0-T020 review non-blockers (3, dispositioned — no change required). M2-T007/T008/T009 G-review LOW items; M2-T005 accessibility release carry-forwards (NVDA/VoiceOver, focus-ring pixels) + the M2-T005-era web-e2e a11y focus-race flake. Standing hygiene: `agent-a501f3e0a11bdd091` worktree removal; 4 pre-existing UTF-8-BOM `M0-T000-*` report JSONs (cosmetic, valid under utf-8-sig); 8 older remote task branches; validator-tests CI wiring (M1-T006 D1); .gitattributes CRLF determinism; Dependabot.

## Environment/process lessons (prior lists live in agent-memory `orchestration-lessons`)

- **A fresh owner instruction does not override an already-approved packet rule unless the owner says so** (the interim CP-0032 conflicted with the M0-T020 packet checkpoint rule; owner corrected to keep CP-0031). When an instruction and an approved packet conflict, surface it.
- **`gh pr merge --delete-branch` fails its LOCAL branch delete when the branch is checked out** (worktree or current branch), returning exit 1 even though the remote merge succeeded; and may leave the remote branch alive. Switch off the branch first (or remove the worktree), verify the remote merge independently, then delete local + remote explicitly.
- **Bash `cd` into a subdir persists across tool calls** and breaks later relative-path CLI reads. Always `cd "$(git rev-parse --show-toplevel)"` before `tools/project_control.py` / relative reads.
- **Thin-client npm:** the web lockfile is regenerated on a GitHub runner via `generate-lockfile.yml` (`workflow_dispatch`, `npm install --package-lock-only`, commits back to the dispatched branch), never with local npm. min-release-age / exact npm-config keys must be verified against the pinned npm 11 docs, never guessed.
- **Deferred-ledger dispatch mechanics:** create the control branch from reconciled main; author the G0-readiness note first; record acceptance gates only when the report paths already exist on main and the packet's checkpoint rule permits; stage ONLY the specific `project-control/**` + `docs/SESSION_HANDOFF.md` paths (never a broad `git add`).
