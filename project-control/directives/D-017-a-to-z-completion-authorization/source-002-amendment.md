please add this to the work
PERMANENT SOFTWARE-ENGINEERING ENFORCEMENT

The modularity and code-organization requirements are permanent repository rules, not instructions that apply only during this initiative.

Implement all of the following:

1. ROOT CLAUDE INSTRUCTION

Add a concise permanent principle to the root CLAUDE.md stating:

- Design production code around clear responsibilities and stable module boundaries.
- Do not place unrelated domain logic, storage, serialization, external I/O, CLI/API wiring, and presentation into one large file.
- Before substantially growing an existing file, inspect its current size, responsibilities, and dependencies.
- Prefer focused modules with explicit interfaces and focused tests.
- Preserve public imports through compatibility facades when splitting existing code.
- New oversized handwritten files and unjustified growth of existing oversized files are prohibited by the repository’s modularity policy and CI.
- Read docs/CODE_MODULARITY_POLICY.md and the applicable path-scoped rule whenever creating, substantially expanding, or decomposing production source code.

Keep this CLAUDE.md addition concise so it does not materially increase every session’s base context.

2. CODEX INSTRUCTION

Add the equivalent concise rule to the root AGENTS.md so Codex checks modularity during planning and review.

Codex must treat unjustified responsibility mixing, excessive module growth, giant functions, hidden coupling, and giant generic utility modules as review findings.

3. PATH-SCOPED CLAUDE RULE

Create .claude/rules/code-architecture.md with path frontmatter covering handwritten production source, including applicable Python, TypeScript, and TSX source paths.

This rule must automatically load when Claude edits production code and require it to:

- Inspect the target file before adding substantial code.
- Identify the correct responsibility and module boundary.
- Avoid appending unrelated behavior merely because a convenient file already exists.
- Separate domain logic, persistence, serialization, external I/O, API/CLI wiring, and presentation when they change for different reasons.
- Add focused tests for extracted behavior.
- Preserve existing public interfaces where appropriate.
- Avoid circular dependencies.
- Avoid giant utils.py, helpers.py, common.ts, or miscellaneous dumping grounds.
- Report why a file remains cohesive when it crosses a review threshold.
- Run the modularity checker before submitting a checkpoint.

Keep the auto-loaded path rule focused and compact. Put explanations and examples in the on-demand policy document instead of bloating every coding context.

4. FULL POLICY DOCUMENT

Create docs/CODE_MODULARITY_POLICY.md as the detailed source of truth.

Include:

- Responsibility and cohesion rules.
- Module-boundary examples for Python, TypeScript, React, API, storage, and deterministic rule-engine code.
- Soft and hard size thresholds.
- Function and class complexity guidance.
- Public-interface preservation.
- Circular-dependency prevention.
- Testing requirements before extraction.
- Exceptions for generated code, schemas, migrations, fixtures, and inherently data-driven files.
- The reviewed-exception process.
- How to refactor an existing large file safely.
- How to avoid meaningless over-fragmentation.
- How the policy is measured and enforced.

5. MACHINE ENFORCEMENT

Create a deterministic repository modularity checker and wire it into CI.

The checker must:

- Examine handwritten production files only.
- Exclude generated, vendored, lock, schema, migration, and approved fixture paths.
- Fail on newly introduced handwritten production files above the hard threshold without a reviewed exception.
- Fail when an already oversized file grows materially without an exception.
- Report files above the warning threshold.
- Detect excessive top-level symbol counts where reliable.
- Use a versioned, reviewed baseline for existing legacy debt.
- Prevent the baseline from being casually regenerated to hide regressions.
- Produce deterministic output.
- Require explicit, expiring, path-specific exceptions with owner, reason, and review evidence.
- Never treat line count alone as proof that architecture is bad.
- Never allow a passing line count to excuse responsibility mixing or excessive coupling.

6. TASK AND REVIEW INTEGRATION

Update the appropriate task-packet templates, coding workflow, and code-review checklist so every production-code task answers:

- Which responsibility owns this change?
- Which existing module should contain it?
- Is the target already above a warning threshold?
- Should behavior be extracted before adding more?
- What public interface must remain stable?
- Which focused tests protect the boundary?
- Did the modularity CI check pass?

Independent code review must check these answers against the actual diff.

7. CONTINUING ENFORCEMENT

This system must continue operating after the context-intelligence initiative finishes.

Every future source-code PR must run the modularity CI check. Every future Claude coding session receives the concise root instruction. Every future Codex review receives the AGENTS.md rule. The detailed path-scoped instruction loads when production source is touched.

Prove the mechanism with tests showing:

- A normal focused module passes.
- A new unjustifiably oversized module fails.
- Growth of a grandfathered oversized file fails.
- An excluded generated file does not fail.
- A valid reviewed exception is narrow and temporary.
- An expired, broadened, or incorrectly targeted exception fails.
- Regenerating the baseline cannot silently erase existing debt.
STAGE — DETERMINISTIC COMPLEXITY-BASED MODEL ROUTING

Implement a model-routing layer that chooses a model based on measured task complexity, risk, and required capability—not based on a model freely choosing itself.

The router must classify work into:

- LOW: repository census, formatting, mechanical documentation, deterministic lookups, simple isolated tests.
- MEDIUM: bounded single-subsystem implementation, ordinary debugging, focused refactoring, test creation.
- HIGH: cross-subsystem architecture, difficult debugging, migrations, concurrency, performance, graph/schema changes.
- CRITICAL: security, authorization, protected configuration, legal/numeric correctness, destructive operations, control-plane changes, and final independent acceptance.

Use deterministic signals including:

- Number of files and subsystems affected.
- Dependency-graph spread.
- Security and authorization impact.
- External side effects.
- Schema or migration impact.
- Ambiguity and missing evidence.
- Whether previous attempts failed.
- Required reviewer roles.
- Estimated context size.
- Task-packet risk classification.

Rules:

- Route only to models already permitted by the protected controller configuration.
- Never let a worker add or authorize a model.
- Never silently modify config.toml or model_selection.toml.
- If only one Claude model is authorized, report that adaptive Claude routing is unavailable rather than pretending selection occurred.
- Use the lower-cost permitted model for LOW work.
- Use the stronger permitted model for HIGH and CRITICAL work.
- Security and directive-compliance verification must use the strongest permitted independent reviewer.
- Failed LOW/MEDIUM work may escalate one level with the reason recorded.
- HIGH or CRITICAL work must never be silently downgraded to save tokens.
- Quota fallback and complexity routing are separate decisions and must be recorded separately.
- Every routing decision records task ID, complexity band, determining signals, chosen model, permitted-model evidence, fallback status, context size, result, and cost/token telemetry when available.
- Build a frozen routing test corpus proving that simple tasks stay inexpensive and critical tasks cannot be routed to weaker models.
- Add CI tests preventing an unauthorized model, self-selected model, unrecorded fallback, or ungrounded complexity classification.
- If enabling meaningful Claude routing requires a protected allowlist change, finish all repository implementation first and return one consolidated OWNER_ACTION_BUNDLE using the established protected-config update procedure.
