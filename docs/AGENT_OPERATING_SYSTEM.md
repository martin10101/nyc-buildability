# Agent Operating System

## Purpose

This document defines how the main Claude agent and project subagents cooperate like a disciplined construction-management team. The goal is continuous progress without context overload, duplicated work, silent assumptions, or self-approved defects.

## 1. Organizational model

### 1.1 Lead orchestrator

The lead orchestrator acts as project executive, construction manager, and integration owner. It does not attempt to personally perform every specialist task.

Only the orchestrator may:

- Change `project-control/master_plan.json`
- Change milestone status
- Move a task to `accepted`
- Unlock dependent tasks
- Reassign or split tasks
- Approve integration into the main branch
- Decide which specialist receives the next task
- Change task scope after work has started

The orchestrator must continually convert new evidence into a revised plan rather than blindly following the original sequence.

### 1.2 Producer agents

Producer agents research, design, or implement within a narrow contract. They may submit a task for review but cannot approve it.

Each producer receives:

- Task ID and objective
- Exact inputs
- Expected outputs
- Allowed files
- Forbidden files
- Dependencies
- Required gates
- Acceptance scenarios
- Completion evidence requirements

### 1.3 Independent reviewers

A reviewer must be different from the producer. The reviewer begins from the acceptance criteria and runnable system, not from the producer’s explanation.

The reviewer must independently answer:

- Does it work from a clean state?
- Does it return the correct data?
- Is the result traceable?
- Does it behave correctly on normal, boundary, ambiguous, missing, conflicting, and failure cases?
- Did it damage unrelated behavior?
- Can a real user understand and complete the flow?

### 1.4 Domain gates

Security, data-contract, geospatial, and legal-rule work requires a domain-specific reviewer in addition to general QA.

### 1.5 Human authority

A qualified human remains the final authority for publishing legal interpretations and for production/business approvals. Agents may prepare complete evidence packets so human review is narrow and efficient.

## 2. The continuous management loop

The orchestrator repeats this loop until the release definition of done is satisfied:

1. **Inspect** — read project state, active tasks, reports, gates, blockers, git status, tests, and deployment health.
2. **Reconcile** — compare recorded progress with actual code and artifacts.
3. **Plan** — identify ready tasks and critical path.
4. **Contract** — create precise task packets and acceptance scenarios.
5. **Isolate** — give writing agents non-overlapping scopes, preferably isolated worktrees.
6. **Delegate** — run the best specialist agents; parallelize only independent work.
7. **Collect** — require structured subagent reports and evidence.
8. **Verify** — assign independent gates; reviewers rerun tests and user journeys.
9. **Decide** — accept, rework, block, split, or discard.
10. **Integrate** — merge only accepted work; run integration and regression gates.
11. **Checkpoint** — update state, progress, decisions, defects, and next-ready work.
12. **Replan** — redistribute work based on what was learned.

## 3. Work delegation rules

- One task has one accountable producer at a time.
- Every write task has an exclusive file scope.
- Parallel tasks may not share migrations, common contracts, or the same implementation files unless sequenced.
- Research can run in parallel and returns concise evidence documents.
- A subagent report is not proof. Executable evidence is proof.
- The producer must disclose assumptions, skipped items, uncertainty, and incomplete tests.
- A failed gate creates a tracked defect or rework task; it does not get explained away in chat.
- If the original design is invalid, create a decision record and replan rather than patching around it.

## 4. Context-control strategy

Keep the main orchestrator’s context focused on:

- Current architecture
- Master plan
- Active dependencies
- Gate outcomes
- Important decisions
- Blockers
- Release risks

Use subagents for high-volume API research, logs, source documents, migrations, implementation, and test output. Subagents return structured summaries and save detailed evidence in the repository.

Long procedures live in skills and documents, not in the root `CLAUDE.md`.

## 5. Parallelism modes

### Default: named subagents

Use project subagents for focused research, implementation, and review. They work in separate contexts and report back to the orchestrator.

### Parallel code changes: worktree isolation

Use isolated worktrees for agents that edit code in parallel. Each worktree owns a task and branch. The orchestrator merges only after gate acceptance.

### Large repeated analysis: dynamic workflow

When available and appropriate, use a reviewable dynamic-workflow script for many independent searches or cross-checks. The script must still write results into the project-control system and may not bypass gates.

### Experimental agent teams

Agent teams are optional and must not be a dependency of the project. If enabled, the team lead still follows this file-based control plane because experimental session coordination is not the source of truth.

## 6. Required subagent return packet

Every producer returns:

- Task ID
- Status requested: `awaiting_gate`, `blocked`, or `needs_split`
- Files changed
- Contracts/schema changed
- Acceptance scenarios created
- Commands run
- Test results
- Expected versus actual results
- Source/API evidence
- Assumptions and defaults
- Known limitations
- Security/provenance impact
- New risks or dependencies
- Recommended next tasks
- Exact report path

The orchestrator must reject vague returns such as “done,” “looks good,” or “tests pass” without reproducible commands and evidence.

## 7. Agent memory

Specialist agents may maintain concise project-scoped memory about stable patterns, locations, and recurring defects. Memory is not authoritative project status. The authoritative status is always `project-control/` plus git and CI evidence.


## 8. Low-storage execution discipline

The owner’s PC has approximately 7 GB free and is a thin client. The orchestrator must route dependency-heavy development, tests, GIS/data imports, document ingestion, builds, and report generation to cloud execution. Every task packet must identify execution location, expected disk use, persistent storage destination, and cleanup. A producer must stop and report a blocker if its task would violate the local disk budget. Reviewers must test cleanup and verify that durable artifacts are uploaded to approved cloud services.
