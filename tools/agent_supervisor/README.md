# Agent Supervisor — Phase 2 status

This is the deterministic Codex ↔ Claude supervisor bridge described by owner
directive **D-007**. It is being built in five phases. **Phases 1 and 2 exist
today.**

**Nothing in this package runs your project unattended.** There is still no loop
that starts Claude on its own, no push, no merge, and no acceptance. The
unattended writing mode (`limited-auto`) is not implemented at all, and turning
it on later is a separate, explicit decision that only you can make.

What Phase 2 added: the deterministic four-tier decision engine, the approval
broker, the Claude and Codex adapters (both driven by fake executables in the
tests), the evidence collector, the external-effect journal, and the push safety
checks — **checks only; this phase never pushes.**

---

## What you can actually run today

Seven commands. Five read-only, two that record your answer to a queued question.

```
python -m tools.agent_supervisor doctor
python -m tools.agent_supervisor status
python -m tools.agent_supervisor verify-controller
python -m tools.agent_supervisor pending-approvals
python -m tools.agent_supervisor approve-once <request-id> <digest>
python -m tools.agent_supervisor deny <request-id> <digest>
python -m tools.agent_supervisor revoke-all
```

### Answering a queued question

`pending-approvals` prints each waiting request with an exact digest. To answer,
quote that digest back:

```
python -m tools.agent_supervisor approve-once req_4f2c... 9a1b3c...
```

The digest is not decoration. It binds the answer to the exact command,
arguments, target files (and their filesystem identities), task, branch,
worktree, repository HEAD, policy version, and permission mode. If anything at
all has changed by the time the action would run, the approval is dead and the
supervisor asks again. An approval is also **single-use**: one approval, one
execution.

`revoke-all` cancels every waiting and unconsumed approval immediately.

### `doctor`

Checks that the pieces built so far are healthy, and prints a PASS/FAIL line for
each. It writes nothing except creating its own runtime folder and an empty
journal if they do not exist yet. Add `--json` for machine-readable output.

It checks:

| Check | What it means |
|---|---|
| `python_version` | Python 3.11+ (needed for the stdlib TOML reader) |
| `schemas_present` | the four JSON schemas exist and parse |
| `prompts_present` | the three prompt templates exist |
| `state_machine` | all 23 states exist and every one is reachable |
| `protocol_roundtrip` | a valid message is accepted and a tampered one is refused |
| `hard_deny_enforced` | every bypass flag and every effort flag is actually refused |
| `circuit_breakers` | a counter at its hard limit really trips |
| `controller_manifest` | the supervisor's own files hash to their recorded digests |
| `runtime_dir` | runtime state resolves OUTSIDE the repository |
| `journal_integrity` | the durable database opens and passes its integrity check |
| `audit_chain` | the audit log's hash chain verifies end to end |
| `policy_four_tiers` | a bypass flag halts, a push to `main` is denied, an in-scope edit is automatic, an unknown request queues, and no model can loosen any of it |
| `approval_binding` | a changed argument changes the approval digest, and the model's stated reason is outside the binding |
| `claude_adapter` | the confirmed CLI shape is enforced; a non-manual permission mode and an unverified session resume are refused |
| `control_response_shape` | reports the honest verification status of the control-response wrapper |
| `codex_adapter` | the reviewer is read-only by construction; a writable sandbox is refused |
| `push_policy` | `main` and force pushes are denied, and nothing is executed |
| `external_effects` | idempotency keys are stable and unmodeled external writes are refused |
| `evidence_bounds` | truncation is explicit and oversized material stops for you |
| `controller_config` / `model_selection` | only when you pass `--config` and `--model-selection` |

Optional arguments:

```
python -m tools.agent_supervisor doctor \
    --config <path to config.toml> \
    --model-selection <path to model_selection.toml> \
    --manifest <path to a recorded controller_manifest.json>
```

`doctor` exits `0` when everything passes and `1` when anything fails.

### `status`

Renders the durable journal: current state, pending external effects, queued
questions, and whether the audit chain still verifies. It reads; it never writes.

### Everything else

Every other operator command from the directive is *wired* — it exists, and it
refuses clearly, naming the phase that will implement it:

```
replay start pause resume stop emergency-stop recovery-status schedule-status
cancel-scheduled-resume autostart-plan install-autostart uninstall-autostart
set-codex-model set-claude-model export-handoff
```

`start --mode limited-auto` refuses *by name*, not merely as "unimplemented".

---

## What exists, module by module

| Module | Status |
|---|---|
| `config.py` | **complete for Phase 1.** Parses the immutable `config.toml` and the runtime `model_selection.toml`, enforces per-provider allowlists, refuses cross-provider satisfaction, validates fallback chains, refuses any effort key at any depth in either file, and refuses a config that tries to boot into limited-auto. |
| `models.py` | **complete for Phase 1.** Records for checkpoints, decisions, envelopes, audit events, journal rows, plus the single canonical-digest definition every other module shares. |
| `protocol.py` | **complete for Phase 1.** Versioned envelope, digest validation, incremental JSONL framing (fragments, CRLF, BOM, split multibyte, blank lines, stderr noise, bounded buffers), and sequence/idempotency enforcement. |
| `durable_state.py` | **complete for Phase 1.** SQLite journal with WAL + `synchronous=FULL`, transactional schema versioning, startup integrity check, before/after external-effect records, transactional outbox/inbox, queued-ASK storage, and a tested backup/restore path. |
| `state_machine.py` | **complete for Phase 1.** All 23 states, 64 documented transitions, illegal-transition refusal, idempotent repeats, and commit-before-side-effect ordering. What each state *does* is Phases 2–3. |
| `audit_log.py` | **complete for Phase 1**, except the external anchor (below). Append-only JSONL with the mandatory hash chain. |
| `redaction.py` | **complete for Phase 1.** Pattern- and key-based redaction before anything is persisted, with a reported count. |
| `manifest.py` | **complete for Phase 1.** Controller manifest generation and verification; halts on any change. `model_selection.toml` is deliberately excluded. |
| `circuit_breakers.py` | **complete for Phase 1.** Counter and gauge breakers with warn (notify) and trip (pause) verdicts. Wiring them to live resource sampling is Phase 2/3. |
| `process.py` | **mostly complete.** Argv-array-only execution, hard-deny argument refusal, minimal child environment, per-process timeouts, process-tree termination, executable identity and repo-shadow refusal. See the Windows note below. |
| `policy.py` | **complete for Phase 2.** The four-tier engine: HARD-DENY (with `DENY_AND_CONTINUE` vs `DENY_AND_HALT`), AUTO, NOTIFY (notify-exactly-once ledger), ASK. Owner standing grants, per-provider model selection, the five-clause independence check, injection labelling, and path canonicalization. A model recommendation may only *stricten*. |
| `broker.py` | **complete for Phase 2.** Digest-bound approvals over the full Section 13.5 binding, recompute-before-execute invalidation, single-use approvals, the queue, the Codex advisory step bounded to pre-marked categories, and `revoke-all`. Never selects "always allow"; contains no file-write path at all. |
| `claude_runner.py` | **complete for Phase 2.** The confirmed CLI shape, tolerant stream parsing, checkpoint extraction and validation, and the `can_use_tool` control loop wired to the broker. See the caveat below about the response wrapper. |
| `codex_reviewer.py` | **complete for Phase 2.** A fresh read-only process per review, the Section 9 decision rules, a bounded schema retry then halt, and model selection with fallback. |
| `evidence.py` | **complete for Phase 2.** The deterministic collector (the supervisor runs the status commands, not Claude) and the bounded packet builder with explicit truncation, explicit failed collections, and a STOP_FOR_OWNER path when material will not fit. |
| `external_effects.py` | **complete for Phase 2.** Stable idempotency keys, before/after records, reconciliation before any retry, and a refusal to retry anything ambiguous. |
| `push_policy.py` | **checks only.** Every Section 13.6 question is answered; **no push is executed in this phase**, and the module contains no subprocess call at all. |
| `cli.py` | **`doctor`, `status`, `verify-controller`, `pending-approvals`, `approve-once`, `deny`, `revoke-all` live**; everything else refuses by name. |

### Not built yet (and not pretended)

Session rotation, crash-recovery classification, usage-limit wake scheduling,
notifications, authenticated remote approvals, quarantine/restore, the replay
engine, the authenticated model-change path (`set-codex-model` /
`set-claude-model`), and push EXECUTION are **Phases 3–4**. There is no
supervisor loop yet: `start` still refuses.

---

## Three honest caveats

### 1. The external audit anchor is not built yet

The audit log's hash chain is complete and detects tampering, truncation, and
reordering (there are seeded tests for all three). Truncation is caught using a
small sidecar "head" file recorded next to the log.

That sidecar sits on the same machine as the log, so it is a **weaker** anchor
than the directive ultimately requires. You chose **Option A** at dispatch: the
controller pushes the chain head to a dedicated anchor branch that the worker
cannot touch. That needs controller-held push credentials and the ADR-005
amendment to be in force, so it is scheduled for **Phase 3**. Until then, the
anchor is local-only, and this file says so rather than implying otherwise.

### 2. Windows process control — what is proven vs deferred

Proven now, with tests that spawn real processes:

* terminating a process **and its descendants** (`taskkill /T /F`, invoked as an
  argument array, never a shell string);
* creating a Windows **Job Object**, configuring it to kill everything on close,
  assigning a real child to it, and confirming the child dies when the job
  closes.

Deferred to **Phase 3**: making the Job Object the *default* container for every
launched worker — that needs breakaway handling and compatibility with hosts that
already place the shell inside a job. Phase 1 uses the taskkill path by default
and keeps the proven Job Object available.

### 3. One byte-level detail of the Claude control protocol is still unverified

The Phase 1 probes captured the permission *request* the CLI sends, verbatim, and
proved that a deterministic deny round-trips and that the CLI fails **closed**
when nobody answers. What the probe report does not record is the exact byte
shape of the *response* wrapper we send back.

`claude_runner.py` therefore builds the wrapper the SDK documents, and `doctor`
reports it as **UNVERIFIED** against the live CLI. The tests here prove the loop
using a fake executable that expects that shape — they prove our side, not the
CLI's. A short preflight round-trip probe against the real binary must confirm it
before any live worker run. This is stated rather than assumed.

---

## Where runtime state lives

Never in the repository. Keyed by a SHA-256 of the **full canonical checkout
path** (not the folder name), so two checkouts never share state:

```
Windows:  %LOCALAPPDATA%\NYCBuildabilitySupervisor\<sha256-of-checkout-path>\
POSIX:    $XDG_STATE_HOME (or ~/.local/state)/NYCBuildabilitySupervisor/<sha256>/
```

The POSIX path is a deliberate addition so the tests run on Linux CI; production
is the Windows path. The folder holds the SQLite journal and the audit log.
Refusing to place runtime state inside the checkout is enforced in code and
tested.

---

## Configuration

Two files, on purpose:

* **`config.toml`** — immutable, covered by the controller manifest. Policy,
  limits, and the per-provider lists of models you permit **at all**. Changing it
  invalidates the manifest and follows the full controller-update process.
* **`model_selection.toml`** — runtime, deliberately **outside** the manifest.
  Which permitted model is currently active. Changing a model must never
  invalidate the controller, and a test proves it does not.

`config.example.toml` contains placeholders only — no secrets, no real model
names, and **no effort key**. There must never be an effort key in any
configuration file, prompt, or command line; the loaders refuse one at any depth
and `process.py` refuses an `--effort` flag like a bypass flag.

Each provider's list is checked against **itself only**: a Codex model can never
satisfy a Claude role and vice versa.

---

## Tests

```
python -m unittest tools.test_agent_supervisor_phase1
python -m unittest tools.test_agent_supervisor_protocol
python -m unittest tools.test_agent_supervisor_audit
python -m unittest tools.test_agent_supervisor_process
python -m unittest tools.test_agent_supervisor_policy
python -m unittest tools.test_agent_supervisor_broker
python -m unittest tools.test_agent_supervisor_runner
python -m unittest tools.test_agent_supervisor_reviewer
```

Standard-library `unittest` only — no new dependency anywhere in this package.
The provider executables in the tests are **fake** local scripts. No test makes a
network call, uses a token, or touches your real runtime directory.

---

## The safety rules this code is built around

* No `shell=True`, ever, and no command strings — argument arrays only.
* Bypass flags and effort flags are refused as constants, not as policy.
* Nothing is persisted before it passes redaction.
* The journal commits before any side effect runs.
* An unreadable, rolled-back, or partially migrated journal is refused, not
  guessed at.
* A damaged audit chain is never silently extended or repaired.
* Any change to the controller's own files halts it.
* `limited-auto` cannot be reached from a default, a missing config, a parse
  error, a migration, or a downgrade.
* Every approval is bound to a digest of the whole request and is recomputed
  immediately before execution; nothing survives a change.
* An approval is single-use. An unhandled request is denied, never left hanging.
* A model's opinion can only make a decision *stricter*, never looser — including
  a hard deny, which neither Claude nor Codex can move.
* Text from a model, a log, a PR comment, or a test run is data. It is labelled
  when it tries to give instructions, and it never changes a tier.
* Standing grants come from you, cover one exact operation shape, and expire with
  the task. Nothing in the code can create or widen one.
* An external action that might have happened is reconciled from read-only
  evidence, never retried on a guess.
