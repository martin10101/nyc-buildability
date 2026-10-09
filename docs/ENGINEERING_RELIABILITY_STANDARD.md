# Engineering Reliability Standard (canonical; M0-T078, D-023-R015)

How to debug, how to size a change, how to prove behavior, how to build async / idempotent / retrying
surfaces, how to shape errors, where to verify, how to triage findings, and what a claim must be
backed by. This is the project's own standard — no third-party framework, agent pack, or plugin is
adopted, referenced as authority, or required by it.

**Authority.** Engineering guidance only. It does not override `CLAUDE.md`, the gates
(`docs/GATES_AND_CHECKPOINTS.md`), authority and lifecycle (`docs/PROJECT_CONTROL_PROTOCOL.md`,
ADR-005/ADR-006), or any active owner hold; on conflict those win. It confers no authority to accept a
task, waive a gate, merge, or release a hold.

**Non-duplication.** Where a rule already has a canonical home, this standard cites it (§0) and adds
only the missing mechanics. Do not copy text between this file and the documents in §0.

## Trigger matrix — what your work pulls in

| If the work is… | Apply |
|---|---|
| Any behavior change to production code | §2, §3, §8, §9 |
| Debugging a defect, a flake, or an incident | §1, §3, §8, §9 |
| Async, concurrent, network, or background-job flow | §4, §5, §6, §7, §8 |
| A retry, replay, resume, or idempotency surface | §5, §6, §8 |
| Any user- or caller-visible error path | §7, §3 |
| Reviewing another identity's work | §8, §9 |
| Claiming a task is done, faster, cheaper, or more reliable | §3, §8, §10 |

## 0. Already law elsewhere — cite it, never restate it

| Rule | Canonical home |
|---|---|
| Executable acceptance examples per task; scenario shape; universal minimum set; evidence standard | `docs/ACCEPTANCE_SCENARIO_STANDARD.md` |
| Producer self-check (G2), clean-environment independent walkthrough (G3), integration/regression (G4), security/privacy (G5) | `docs/GATES_AND_CHECKPOINTS.md` |
| Producer ≠ reviewer; frozen reviewed SHA; a later commit invalidates prior reviews | `.claude/ORCHESTRATION_POLICY.md` §D; `docs/GATES_AND_CHECKPOINTS.md` "Reviewer independence" |
| Module boundaries, responsibility separation, size thresholds, facade-preserving splits, no over-fragmentation | `docs/CODE_MODULARITY_POLICY.md` §§2–4, 6, 11; `.claude/rules/code-architecture.md` |
| Short typed errors (stable code + concise message + structured metadata); abstraction only for real repetition; parameterized adversarial tests preserving every case | `docs/LEAN_OPERATING_PROCESS.md` return item 6 (B5, B8, B3, B6) and return item 8 |
| Sensitive-log redaction, secret handling, least privilege | `docs/GATES_AND_CHECKPOINTS.md` G5; `docs/SECRETS_POLICY.md` §3 |
| Jobs are DB-backed, idempotent, resumable, cancellable, with heartbeat/retry/dead-letter | `.claude/rules/backend-api.md` |
| Never guess a schema, unit, field meaning, or effective date; a missing value reads `unknown` | `CLAUDE.md` principle 3; `AGENTS.md` "Never guess" |
| Dependency admission, advisory rule, and the seven-day age gate | `docs/DEPENDENCY_SECURITY_POLICY.md`; `.claude/ORCHESTRATION_POLICY.md` §G |

This standard supplies what those do not: debugging method (§1), change sizing (§2), red/green and
mutation proof (§3), async / idempotency / retry **design** mechanics (§4–§6), error-surface shape
(§7), the verification-context checklist (§8), a defect-severity vocabulary (§9), and the
frozen-benchmark rule for improvement claims (§10).

---

## 1. Debugging discipline

1. **Reproduce before reading code.** Establish a stable reproduction — exact command, exact input,
   observed wrong output — that fails on demand. No reproduction means no diagnosis: say so, and do
   not ship a fix for a symptom you cannot summon.
2. **Record determinism.** If it reproduces intermittently, record the observed rate over a stated
   number of runs and treat it as a concurrency, ordering, or stale-state defect (§4, §8.3, §8.5)
   until proven otherwise.
3. **Check recent change first.** Before theorizing, identify what changed nearest the symptom —
   `git log` / `git blame` on the implicated paths, recent merges, recent dependency, config, schema,
   or data changes. Record the candidate change, or record that none exists.
4. **Trace the data.** Follow the actual value from entry point to wrong output, naming each boundary
   it crosses (parse → validate → compute → persist → serialize → render) and its value at each.
   Identify the **first** boundary where the value is already wrong. That boundary owns the defect.
5. **Write exactly ONE root-cause hypothesis before any fix** — one sentence naming the mechanism,
   plus the specific observation that would falsify it. One, not a list of possibilities.
6. **Falsify cheaply, then fix.** Confirm or kill the hypothesis with a targeted observation (focused
   test, assertion, log, bisect). If killed, write the next single hypothesis. Never keep a dead
   hypothesis alive with patches.
7. **No shotgun fixes.** Changing several things at once, adding defensive branches, widening a
   `try`, adding a retry, or raising a timeout so the symptom disappears is not a fix. If the
   mechanism was never identified, the defect is still open — record that, do not close it.
8. Record the reproduction, the recent-change finding, and the confirmed mechanism in the task
   evidence. A defect fix with no recorded mechanism does not pass G2.

## 2. Smallest fitting change

1. Fix the cause at the boundary that owns it (§1.4), inside the module that already owns that
   responsibility (`docs/CODE_MODULARITY_POLICY.md` §2). Never patch a symptom downstream of it.
2. Prefer, in order: correct an existing function; correct an existing module's internals; add a
   focused function to the owning module; add a new module with an explicit interface. Skip a level
   only with a recorded reason.
3. **No speculative framework.** Do not add an abstraction layer, plugin system, registry, generic
   "manager", config surface, or option flag for a case that does not exist today. One caller is not
   a framework requirement (`docs/LEAN_OPERATING_PROCESS.md` return item 6, B3/B8).
4. **Do not widen scope silently.** Renames, reformatting, reorganization, dependency bumps, and
   drive-by cleanups do not belong in a defect fix or a feature diff. Raise them as separate work;
   the packet's `allowed_paths` is the boundary.
5. **Do not add a second implementation.** If the behavior already exists, change it. A parallel path
   duplicating it is a defect (G4, "No duplicate or contradictory implementations").
6. Deleting code is a behavior change. Prove nothing depended on it (§3), rather than observing that
   nothing appeared to.
7. If the smallest fitting change would break a public interface, preserve it behind a compatibility
   facade (`docs/CODE_MODULARITY_POLICY.md` §6) or raise the break as its own decision.

## 3. Behavior proof

1. **Red before green.** Every behavior change ships a test observed FAILING against the unchanged
   code and PASSING after. Record both observations with exact command and output. A test written
   only after the fix proves the test runs — not that it detects the defect.
2. **Prove behavior, not implementation.** Assert on observable output, contract, or persisted state
   — never on internal call counts, ordering, or private structure. An implementation-shaped test
   passes a broken rewrite and fails a correct one.
3. A defect fix needs a test that would have caught the original defect. Name the defect in the test.
4. **Mutation or revert proof for critical regressions.** For a fix to a security, tenancy,
   legal-rule, provenance, money, or data-loss defect, additionally prove the new test *detects* the
   regression: revert the fix (or mutate the corrected line), record the test failing, restore, and
   record it passing. Cite that recorded pair in the evidence.
5. **Never weaken a test to make it pass.** Widening a tolerance, relaxing an assertion, marking
   `skip`/`xfail`, or deleting a case to turn a suite green is a must-fix finding (§9), not a fix.
   Merging materially different safety cases is prohibited (`docs/LEAN_OPERATING_PROCESS.md` return
   item 8).
6. **A flaky test is an open defect** (§1.2), never a rerun. Re-running until green is not a pass.
7. Scenario coverage, shape, and evidence format stay governed by
   `docs/ACCEPTANCE_SCENARIO_STANDARD.md`; this section adds only the red/green and mutation-proof
   obligations.

## 4. Async flows

1. **Four explicit states.** Every async operation models `pending`, `success`, `error`, and
   `cancelled`. All four exist, are reachable, and are represented in the caller's contract or the
   UI. "Not pending" is not a state; a missing `cancelled` is a defect.
2. **Identity, not a boolean.** Track the in-flight operation by a stable identity (request / job /
   correlation ID), never by an `isLoading` flag. Two overlapping operations need two identities.
3. **Supersession is decided before the code exists.** When a newer operation supersedes an older one
   for the same target, record which wins — last-issued (typical for user-driven queries) or
   first-issued (typical for a claimed job) — and apply it by identity, not by arrival order.
4. **Cancel what is superseded.** Superseding cancels: abort the transport, stop the work, release
   the claim. The superseded operation transitions to `cancelled`, never silently to `error`.
5. **A stale response never writes.** Before applying a result, compare its operation identity to the
   current one. A non-current response is discarded and recorded — never merged, rendered, cached, or
   persisted. Arrival order is not evidence of recency.
6. **Deduplicate on meaning, not on shape.** Two operations are the same only when caller, operation,
   and semantically normalized payload match (§5.1) *and* the results would be identical. Never
   collapse distinct user intents because their serialized payloads happen to be equal, and never
   treat a retry of a failed operation as a duplicate of that failure.
7. For background jobs, the properties required by `.claude/rules/backend-api.md` are the
   requirement; §5 and §6 are how to satisfy them.
8. A single-threaded pass proves nothing here — verify under §8.3.

## 5. Idempotency

1. **Key on caller + operation + payload.** An idempotency key binds the calling identity, the
   operation name, and a canonical (stably ordered, normalized) payload digest. A client-supplied key
   alone is insufficient; a key omitting the caller lets one tenant's retry collide with another's
   request.
2. **Claim atomically.** First writer wins through one atomic operation — a unique-constraint insert
   or a conditional update — never read-then-write. A concurrent second caller observes the existing
   claim; it does not create a second effect.
3. **Return the SAME response, not merely a success.** A duplicate call returns the stored result and
   the stored job/effect identity of the original, so the retrying caller can correlate. A fresh
   success with a new job ID is a defect.
4. **Record before acting; record what happened.** Persist the claim before the external effect;
   persist the effect's identity (charge ID, message ID, job ID, row ID) when it returns. An effect
   with no persisted identity cannot be reconciled.
5. **Bound the lifecycle explicitly.** State the key retention window, what happens after it expires
   (the operation becomes newly executable), and what happens when the same key arrives with a
   **different** payload — that is a conflict and a typed error (§7.1), never a silent replay of the
   old result.
6. **Reconcile after a crash.** For every in-flight claim, define how a restart decides whether the
   effect happened: query the downstream by the recorded identity, or read a durable local record.
   Never resolve an ambiguous claim by assuming it failed and re-running.
7. **Retry safety is a property of the effect, not of the caller's intention.** Classify every write
   path as idempotent or not. A non-idempotent effect behind a retrying caller (§6) is a defect no
   matter how careful that caller is.
8. `docs/ACCEPTANCE_SCENARIO_STANDARD.md` requires a retry/idempotency scenario and G4 checks job
   idempotency at integration; this section defines what those verify.

## 6. Retries

1. **Transient failures only.** Retry timeouts, connection resets, HTTP 429, documented-retryable
   5xx, and explicit try-again signals. Never retry 4xx validation / authorization / not-found,
   schema mismatch, or any deterministic failure — that converts a fast error into a slow one.
2. **Bound attempts AND total time.** Every policy names a maximum attempt count and a maximum total
   elapsed time and stops at whichever comes first. Open-ended retry is a defect.
3. **Exponential backoff with jitter, always.** Fixed-interval retry across callers synchronizes into
   a thundering herd against a service that is already failing.
4. **Honor `Retry-After`** and documented rate-limit headers when present; they override the computed
   backoff. Never retry a 429 sooner than the server asked.
5. **Exactly one retry layer.** Name the layer that retries — client, service, queue, or job runner —
   and make every other layer pass the failure through. Stacked retries multiply: three layers of
   three attempts is twenty-seven calls.
6. **Never retry an ambiguous effect without reconciling first.** A timeout means *unknown*, not
   *failed*. Reconcile by the recorded effect identity (§5.4, §5.6) before re-issuing any write. This
   governs every payment, external submission, and outbound message.
7. **Give up loudly.** Exhausted retries produce a typed terminal error (§7), a record of attempts
   made and total elapsed time, and a dead-letter or blocker where the work must survive — never a
   silent success, an empty result, or a zero.
8. Never retry to paper over an undiagnosed defect (§1.7).

## 7. Errors

1. **Typed internally.** Every failure is a typed error with a stable code, a concise message, and
   structured metadata (submitted value, expected rule, failed condition) — shape per
   `docs/LEAN_OPERATING_PROCESS.md` return item 6 (B5). No bare strings; never branch on message text.
2. **Two audiences, two payloads.** The user- or caller-facing message says what happened, what it
   means for their result, and what to do next, in the product's language. Diagnostic detail — stack,
   upstream body, query, internal identifiers — goes to the log or trace only.
3. **Correlation ID on both.** Surface a correlation ID to the user and record the same ID with the
   diagnostic detail, so a report is traceable without the user pasting internals.
4. **Never leak.** No secret, credential, token, connection string, internal path, raw upstream
   response body, or other tenant's data reaches a user-visible message or client payload. Map
   upstream errors to project-typed errors; never pass them through. (G5 in
   `docs/GATES_AND_CHECKPOINTS.md`; `docs/SECRETS_POLICY.md`.)
5. **Preserve the diagnosis.** Catching to add context must chain the original (cause / `raise … from`).
   A `catch` that logs a message and discards the original destroys the trace. Never swallow an error
   to keep a flow green.
6. **Log once, at the boundary that handles it.** The layer that recovers or reports logs; layers that
   re-raise do not. Duplicate stacks for one failure make incident review guess how many failures
   occurred.
7. **An error is not a value.** Never substitute `0`, `[]`, `null`, or a default for a failed
   computation. A missing value reads `unknown` (`AGENTS.md`), and a failed legal or numeric
   computation fails closed and stays visible.
8. Every error path is a behavior change and needs its own proof (§3) — not only the happy path.

## 8. Verification contexts

Verify in every context below that applies, and record which did not apply and why. G3/G4 in
`docs/GATES_AND_CHECKPOINTS.md` define *who* verifies and with what independence; this defines *where*.

1. **Clean checkout.** Fresh clone or worktree, dependencies from the committed lock, no local build
   cache, no uncommitted file. "It works in my tree" is not evidence.
2. **Every applicable platform.** If the code runs on more than one OS, shell, or runtime version
   (the owner's Windows PC, Render Linux, CI), verify each — or state explicitly that the path is
   unsupported there and fails closed. Path separators, line endings, file locking, and signal
   handling differ.
3. **Concurrency.** For anything with shared state, a claim, a cache, or a job queue, run it
   concurrently. A single-threaded pass proves nothing about §4 or §5.
4. **Unsafe paths.** Malformed, adversarial, oversized, wrongly typed, and injected input; expired
   credentials; a downstream that is slow, down, or returning garbage. Preserve each as its own case
   (`docs/LEAN_OPERATING_PROCESS.md` return item 8).
5. **Stale state.** Old cache, old session, previous schema, partially migrated data, a key from a
   prior run, a job in flight from a prior deploy. Verify the upgrade path, not only fresh install.
6. **Integration.** Against the real neighbors it ships with, not only mocks — G4 covers the combined
   suite, contract compatibility, and migrations forward and back.
7. **Real user flow.** The entire path a user or downstream service actually takes, end to end. For
   UI that is a real browser walkthrough (G3; the UI human-journey pack).
8. **Frozen identity.** Every verification names the exact SHA or content digest it ran against; a
   later commit invalidates it and it re-runs (`.claude/ORCHESTRATION_POLICY.md` §D).
9. **Independent final review.** The producer never certifies its own work. A different identity
   re-derives the result from the acceptance criteria, not from the producer's conclusions (G3;
   `CLAUDE.md` principle 7).

## 9. Triage

Classify every finding — self-check, code review, or gate — into exactly one severity, and state it
with the finding.

| Severity | Meaning | Effect |
|---|---|---|
| **Must-fix** | Wrong output; lost or corrupted data; security or tenancy exposure; secret leakage; legal or provenance violation; broken contract; unhandled failure on a real path; violation of a rule in this standard or the gates | Blocks. The G3/G4 verdict is FAIL until fixed and re-verified. |
| **Important** | A real defect on a narrower path, missing test for shipped behavior, boundary violation, diagnosis-destroying error path, unbounded retry — costly, but not currently producing wrong output | Recorded as required rework with an owner and a task; never silently dropped. |
| **Minor** | Naming, wording, formatting, comment style, ordering, structural preference with no behavioral effect | **Never blocks.** Optional. |

1. **Cosmetics are non-blocking.** Do not hold a correct change on style preference, and do not
   promote a preference to a defect by asserting it "could" cause a problem — name the mechanism or
   file it as minor.
2. **Severity is claimed with a reason.** A must-fix names the specific consequence. Unexplained
   severity is downgraded when challenged.
3. **Do not bundle.** One finding per row, each with its own severity, location, and reproduction.
4. Severity changes no authority: the gate and the orchestrator alone decide task status
   (`docs/PROJECT_CONTROL_PROTOCOL.md`), and a failed gate is never waived by relabelling a finding
   minor (`docs/GATES_AND_CHECKPOINTS.md`, "Reviewer independence").

## 10. Measured claims only

1. **Never assert an improvement without a measurement.** Faster, cheaper, fewer tokens, less
   context, more reliable, more autonomous, higher throughput, lower latency — none may be stated in
   a report, commit message, PR, handoff, document, or answer to the owner without a recorded
   benchmark. (Standing prohibition D-023-R023, applied to engineering work.)
2. **A claim needs a FROZEN benchmark**: a committed baseline artifact recording the exact command,
   the code identity (SHA), the input set, the environment, the run count, and the raw results; the
   after-measurement re-runs the identical harness. Precedent and mechanics: the frozen end-to-end
   baseline in `docs/CONTEXT_PIPELINE_RUNBOOK.md` (M0-T076).
3. **Report the comparison honestly**: absolute before and after numbers with units, the run count,
   and the variance or range — not a lone percentage, not a best-of-N, not a single run.
4. **State the scope.** A measured improvement on one harness, one dataset, one machine is a claim
   about that harness. Never generalize it to the product, the pipeline, or "the system".
5. **Reliability claims need failure data**, not a green run: an observed failure count over a stated
   number of trials, under the §8 contexts. One successful execution measures nothing.
6. **Absent a benchmark, describe the change, not its effect.** "Adds a bounded retry with jitter" is
   reportable; "makes ingestion more reliable" is not.
7. Line-count, file-count, and diff-size reductions are never themselves evidence of improvement
   (`docs/LEAN_OPERATING_PROCESS.md` header rule).
8. **This standard makes no claim about its own effect** on defect rate, delivery speed, token use,
   or cost. It states required practice; it is not evidence of an outcome.
