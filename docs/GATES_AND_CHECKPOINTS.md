# Gates and Checkpoints

## Principle

No producer approves its own work. A task becomes accepted only after its required gates pass and the orchestrator records the acceptance.

## Task lifecycle

`backlog → ready → claimed → in_progress → self_check → awaiting_gate → accepted`

Failure paths:

- `awaiting_gate → rework → in_progress`
- Any active state → `blocked`
- Superseded work → `canceled`

## Gate catalog

### G0 — Definition-of-ready gate

Before coding:

- Objective is unambiguous.
- Dependencies are accepted or explicitly mocked behind contracts.
- File scope is exclusive.
- Inputs and outputs are defined.
- Acceptance scenarios exist.
- Required source documentation is available.
- Required credentials are available or a blocker is recorded.
- Required gates are assigned.
- Execution location and expected disk usage are documented.
- The owner’s low-storage PC remains within the approved budget, or the task is assigned to a cloud environment.
- Temporary-file cleanup and durable cloud-storage routing are defined.

### G1 — Source and data-contract gate

Required for government connectors, datasets, schemas, and field mappings.

Reviewer verifies:

- Official source identity
- Current endpoint/dataset identifier
- Authentication and rate limits
- Pagination/update behavior
- Actual response fixture
- Field mapping and units
- Null/unknown semantics
- Retrieval/version timestamps
- Provenance persistence
- Schema-drift handling
- Cross-check against a second official presentation where feasible

A connector cannot pass using screenshots alone when structured data exists.

### G2 — Producer self-check gate

The producer runs all task-specific acceptance scenarios and records exact commands and outputs. G2 only permits submission; it does not accept the task.

### G3 — Independent human-style walkthrough gate

A reviewer who did not implement the work:

1. Starts from a clean environment or isolated worktree.
2. Reads acceptance criteria, not the producer’s conclusions.
3. Performs the workflow as a real user or downstream service would.
4. Records input, expected result, actual result, and evidence.
5. Tests at least one normal, one boundary, one missing/ambiguous, and one failure case.
6. Checks clarity, recovery, and absence of hidden assumptions.
7. Issues `PASS`, `FAIL`, or `BLOCKED` with defects.
8. Verifies that no large or persistent artifacts are unexpectedly written to the owner's PC.

For UI work, this includes real browser interaction, not only component tests.

### G4 — Integration and regression gate

Required after accepted task work is integrated:

- Full build/lint/type-check/test suite
- Contract compatibility
- Database migration forward and rollback behavior
- Existing golden-property regression suite
- Job idempotency/retry behavior where relevant
- No duplicate or contradictory implementations
- Performance within agreed budgets
- Low-storage policy and temporary-file cleanup behavior

### G5 — Security and privacy gate

Required for auth, tenancy, storage, uploads, external calls, secrets, logs, deployment, and administrative functions.

Must verify:

- RLS and cross-tenant isolation
- Service-role secrecy
- Input validation
- SSRF/injection defenses
- Upload controls
- Prompt-injection defenses
- Private storage
- Sensitive-log redaction
- Least privilege
- Dependency vulnerabilities

### G6 — Legal/rule publication gate

Required for any machine rule or result labeled `verified`.

Agents prepare:

- Exact official source and version
- Structured rule interpretation
- Applicability conditions
- Override/exception relationships
- Positive, negative, boundary, and exception tests
- Evaluation traces
- Independent reviewer findings
- Change comparison against previous rule version

A qualified human zoning reviewer must approve publication. Agent consensus cannot substitute for this gate.

### G7 — Release gate

Required for production release:

- All release tasks accepted
- No open critical/high defects
- Deployment and rollback tested
- Monitoring and alerts enabled
- Source freshness visible
- Reports reproducible
- Security review passed
- Legal coverage clearly disclosed
- User-facing disclaimer present
- Human production approval recorded

## Checkpoint requirements

Create a checkpoint:

- After each accepted or failed gate
- Before and after a migration
- Before merging a worktree
- After integrating a task
- When a blocker changes the critical path
- At the end of every meaningful work session

Each checkpoint records:

- Repository commit and branch
- Active milestone
- Accepted tasks
- Tasks in progress
- Gate results
- Tests run
- Deployment state
- Decisions
- Blockers
- Risks
- Next ready tasks

## Reviewer independence

- Producer and G3 reviewer must be different agent identities.
- Security-sensitive work requires `security-reviewer` even if QA passed.
- API connectors require `data-contract-verifier` even if backend tests passed.
- Legal rules require a human publication approval.
- The orchestrator may not waive a failed gate; it must create a documented exception approved by the human owner, with scope and expiration.
