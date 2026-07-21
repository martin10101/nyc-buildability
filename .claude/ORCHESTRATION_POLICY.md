# Parallel Agent Orchestration Policy

**Status:** Active (owner-authorized configuration, 2026-07-20)
**Scope:** How every future Claude lead runs safe, reusable, parallel agent execution in this repository.
**Authority:** This document is operational guidance. It does **not** override `CLAUDE.md`, `docs/PROJECT_CONTROL_PROTOCOL.md`, `docs/GATES_AND_CHECKPOINTS.md`, `docs/AGENT_OPERATING_SYSTEM.md`, ADR-005, or any active owner hold. Where it repeats those rules it is a convenience summary; the canonical documents win on any conflict. The project-control ledger plus git/CI evidence remain the single source of truth.

This policy governs *how work is parallelized and integrated*. It confers **no** authority to start product work, dispatch a held task, accept a task, change the ledger/checkpoint, or release a hold. Those remain gated by the owner and the control plane.

---

## 1. Parallel-execution mechanisms (know which one you have)

Three distinct mechanisms exist. Name the one you are using; never blur them.

1. **Agent teams (shared task list + teammate messaging).** A lead session spawns teammate sessions that share a task list (`~/.claude/tasks/<team>/`) and message each other (`SendMessage`), coordinated via `TeamCreate` / `TeamDelete`. Requires **Claude Code ≥ 2.1.178** and `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` + `teammateMode: in-process` (both pre-staged in user `settings.json`). In-process mode is the only teammate layout supported inside the Cursor / VS Code IDE extension (tmux/iTerm2 split panes are not).
2. **Background / parallel subagents (report to the lead).** The `Agent` tool spawns focused subagents in separate contexts that return a structured report to the lead. This works on the current runtime **now**. It is the default when agent teams are unavailable.
3. **Isolated worktree sessions.** A writing producer runs in its own git worktree/branch (`isolation: worktree`) so parallel writers never touch each other's files. Composes with either mechanism above.

**Current runtime status (recorded 2026-07-20):** the PATH CLI reports `2.0.11` (below the 2.1.178 team minimum), so **true agent teams require the owner to update Claude Code to ≥ 2.1.178 and restart the extension**. Until then, use mechanisms 2 + 3 (subagents + worktree isolation). The settings are already in place, so teams activate on the next update + restart with no further configuration.

### 1a. Sessions are not durable — teams are per-conversation

In-process agent-team runtime state (the team file, task list, and teammate sessions under `~/.claude/teams/` and `~/.claude/tasks/`) **does not survive a conversation resume, restart, or context compaction.** What *is* durable: the persistent agent **definitions** in `.claude/agents/`, this policy, and the project-control ledger. Therefore **every new Claude Code conversation must create a fresh runtime team** (via `TeamCreate`) when parallel execution is appropriate — never assume a prior team still exists. Let Claude Code own the runtime files under `~/.claude/teams/` and `~/.claude/tasks/`; never hand-author or pre-create them.

---

## 2. Reusable agent roster

Nine reusable roles. Seven reuse existing, owner-accepted definitions unchanged; two (`ci-evidence-verifier`, `control-plane-verifier`) were added 2026-07-20 with conformant ADR-005 frontmatter. All producers declare `isolation: worktree`; all reviewers/verifiers/auditors are read-only (no `Edit` tool) and follow the ADR-005 return-to-orchestrator protocol.

| # | Role | Agent (`.claude/agents/…`) | Kind | Isolation | Read-only |
|---|------|----------------------------|------|-----------|-----------|
| 1 | Repository auditor | `progress-auditor` | audit | — | yes |
| 2 | Backend producer | `backend-engineer` | producer | worktree | no |
| 3 | Frontend producer | `frontend-engineer` | producer | worktree | no |
| 4 | Geospatial engineer | `geospatial-engineer` | producer | worktree | no |
| 5 | Code reviewer | `code-reviewer` | review | — | yes |
| 6 | Security reviewer | `security-reviewer` | review | — | yes |
| 7 | Data-contract verifier | `data-contract-verifier` | review | — | yes |
| 8 | CI / evidence verifier | `ci-evidence-verifier` | review | — | yes |
| 9 | Control-plane verifier | `control-plane-verifier` | review | — | yes |

**Model policy.** Every definition uses `model: inherit`, i.e. the resolved lead/session model (currently Opus 4.8), for implementation and all critical review (security, data-contract, geospatial, CI/evidence, control-plane, code). A faster model may be selected **at dispatch** only for bounded, read-only inventory sweeps by the repository auditor. Never downgrade security, contract, geospatial, or acceptance-grade review to save tokens.

**Read-only enforcement (reviewers/verifiers/auditors).** Enforced exactly as the repository's five pre-existing accepted reviewers: no `Edit` tool; the ADR-005 "Gate reporting protocol" section requires them to *return* report content with a PASS / FAIL / BLOCKED verdict rather than write ledger/git; the orchestrator is the sole ledger/git/gh writer; any file write is confined to the agent's own `.claude/agent-memory/<name>/`. A reviewer never repairs the producer branch and then approves its own repair.

**Producer confinement.** Producers work only inside their task packet's allowed paths in their own worktree. They do not run `tools/project_control.py`, `git push`, `gh`, or accept/checkpoint anything (ADR-005). They return files-changed + real command output + requested status (`awaiting_gate` | `blocked` | `needs_split`).

---

## A. Lead-only authority

Only the lead/orchestrator (the main Claude Code session) controls: `main`/`origin/main` reconciliation; dispatch; task assignment; ledger changes; checkpoint changes; merges; acceptance control PRs; hold releases; and final synthesis. The lead coordinates *while* teammates work and does not compete with a producer by editing the same task's files. This mirrors ADR-005 (main session is the sole runner of `project_control.py`, git integration, and `gh`).

## B. Concurrency limits

Normal maximum: **three** concurrent writing producers; **four** concurrent independent reviewers/verifiers. Add agents beyond this only for genuinely independent, read-only work. Do not spawn many agents merely to look fast — raise concurrency only when tasks have independent dependencies and non-overlapping write paths.

## C. Concurrency matrix (required before every parallel implementation wave)

Before dispatching a parallel writing wave, the lead records a matrix with, per task: task ID; dependency state; assigned producer; branch + worktree; allowed paths; forbidden paths; expected shared files; required gates; stop conditions; proposed merge order. **Tasks that overlap on production code, schema, workflow, lockfile, ledger, checkpoint, task-packet, or handoff paths cannot be concurrent writers** — sequence them instead.

## D. Review independence (frozen SHA)

Producer and reviewer must be different identities. Once a task PR head is frozen, the applicable independent reviews run in parallel. **Every review names the exact reviewed SHA.** Any commit after review invalidates all reviews bound to the prior SHA, and they must be re-run against the new head. Reviewers report defects; they never silently fix producer code and approve their own fix.

## E. Rolling pipeline

While CI runs, agents may do authorized **read-only** preparation for future work — dependency mapping, fixture review, official-source verification, test planning, packet inspection. Read-only preparation never releases a hold or authorizes implementation.

## F. Sequential integration

Parallel production does **not** authorize parallel merging. Merge one eligible PR at a time; reconcile `main`; re-run the required combined gates; confirm the next PR is still valid against the new `main` before merging it. (Protected-main workflow: task/control branch → push → `gh pr create` → wait checks green → `gh pr merge --merge --delete-branch --match-head-commit <full-40-char-SHA>` → `git fetch` + `git merge --ff-only origin/main` → verify.)

## G. Dependency security policy (permanent, no waiver)

Across production, development, build, lock-generation, audit, and package-manager tooling:

- No known advisory at **any** severity.
- Every admitted version must be **at least seven complete days old**: exactly **604800 seconds passes, 604799 fails**, measured against official registry publish timestamps in UTC.
- Require official registry timestamps **and** integrity evidence (e.g. registry `dist.integrity` matching the committed lock).
- **Fail closed** on unavailable, missing, malformed, ambiguous, or unmatched registry/integrity evidence.
- No agent waiver. No unlocked bootstrap tool. No dynamic dependency download outside an explicitly reviewed lock.

This is the same machine-enforced rule implemented for the Python locks (M0-T020, `dependency_age_gate.py`) and the committed npm lockfile (M0-T019 correction, in flight). It is enforcement policy, not advisory.

## H. Owner boundary (stop before these)

Unless the owner explicitly authorizes otherwise, **stop and return to the owner before**: merging a task PR; recording acceptance; advancing or creating a checkpoint; changing a public schema or contract; making a security/policy exception; modifying a forbidden path; releasing an existing hold; or dispatching a held task. When a legal interpretation, secret, payment, production approval, or unavailable credential is required, create a blocker rather than guessing.

---

## 3. Alignment references

- Authority + lifecycle: `docs/PROJECT_CONTROL_PROTOCOL.md`, `docs/AGENT_OPERATING_SYSTEM.md`.
- Gates G0–G7 and reviewer independence: `docs/GATES_AND_CHECKPOINTS.md`.
- Orchestrator-only writes, producer/reviewer protocol, agent-memory scope: ADR-005 (`docs/adr/ADR-005-agent-permission-and-gate-workflow.md`) and `.claude/rules/project-control.md`.
- Low-storage / thin-client execution: `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md`.
- Expansion-agent dispatch history + still-active planning hold: `.claude/rules/expansion-agent-dispatch-hold.md`.
