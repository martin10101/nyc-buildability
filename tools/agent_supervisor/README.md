# Agent Supervisor — Phase 4 status

This is the deterministic Codex ↔ Claude supervisor bridge described by owner
directive **D-007**. It is being built in five phases. **Phases 1, 2, 3 and 4
exist today.**

**Nothing in this package runs your project unattended.** The loop exists now,
but it only runs in the two modes that cannot act on their own: `shadow` (which
forwards *nothing*) and `supervised` (where you approve every single prompt).
There is still no push, no merge, and no acceptance. The unattended writing mode
(`limited-auto`) is not implemented at all, and turning it on later is a
separate, explicit decision that only you can make.

What Phase 4 added — *validation*, the part that proves the first three phases
actually behave:

* **the assembled loop** — the pieces Phases 1–3 built are now wired into one
  cycle (start Claude → checkpoint → collect evidence → Codex review → validate
  → policy → forward), with every step a real state-machine transition;
* **shadow mode** — runs the whole cycle against a real workflow and forwards
  nothing, recording what it *would* have done and counting how many times it
  would have had to stop and ask you;
* **supervised mode** — the same loop, except each prompt is held until you
  approve that exact prompt by its digest;
* **replay** — feeds eight real cases out of this repository's own history back
  through the policy engine and checks that it stops where the humans stopped;
* **containment** — on Windows, every process the supervisor starts now runs
  inside a Job Object, so nothing it spawns can outlive it;
* **the adversarial matrix** — several hundred tests that attack the supervisor
  the way a compromised worker or a confused CLI would.

---

## What you can actually run today

**Every** operator command from the directive. Nothing is deferred any more.

**Look at things (read-only, changes nothing):**

```
python -m tools.agent_supervisor doctor
python -m tools.agent_supervisor status
python -m tools.agent_supervisor recovery-status
python -m tools.agent_supervisor schedule-status
python -m tools.agent_supervisor verify-controller
python -m tools.agent_supervisor pending-approvals
python -m tools.agent_supervisor autostart-plan
python -m tools.agent_supervisor replay
```

`replay` is worth running first if you want to see what this thing believes.
It takes eight moments out of this repository's real history — a clean stretch of
work, a review that demanded corrections, a red CI job, a review that no longer
covered the branch head, a decision that was yours to make, M0-T031's completed
lifecycle, the B-015 sentinel failure, and M0-T028's contracted stop — and asks:
*would this supervisor have stopped where you stopped?* It calls no model and
writes nothing.

**Stop and start things:**

```
python -m tools.agent_supervisor pause
python -m tools.agent_supervisor resume
python -m tools.agent_supervisor stop
python -m tools.agent_supervisor emergency-stop
python -m tools.agent_supervisor start --mode shadow
python -m tools.agent_supervisor start --mode supervised
```

`start` runs the safety sequence first, every time — one supervisor per checkout,
the after-a-crash check, and the integrity checks on its own records. Then it
looks at whether you gave it everything it needs to actually run:

```
python -m tools.agent_supervisor start --mode shadow \
    --claude-executable <path> --codex-executable <path> \
    --task-packet project-control/tasks/M0-T036.json \
    --config <path>/config.toml --model-selection <path>/model_selection.toml
```

If any of those five is missing it stops and tells you which one. It never
searches your PATH for a tool and never picks a default that would result in
contacting a provider. In `supervised` mode it prints the exact prompt it wants
to send and stops; you re-run with `--approve-prompt-digest <digest>` if you want
that exact prompt to go out, and nothing else will.

**Answer, revoke, hand over, and change models:**

```
python -m tools.agent_supervisor approve-once <request-id> <digest>
python -m tools.agent_supervisor deny <request-id> <digest>
python -m tools.agent_supervisor revoke-all
python -m tools.agent_supervisor cancel-scheduled-resume
python -m tools.agent_supervisor export-handoff
python -m tools.agent_supervisor set-codex-model <name> --config ... --model-selection ...
python -m tools.agent_supervisor set-claude-model <name> --config ... --model-selection ...
```

**Owner-approved changes to your machine (these show you exactly what they would
do and refuse until you quote the plan digest back):**

```
python -m tools.agent_supervisor install-autostart --confirm-plan-digest <digest>
python -m tools.agent_supervisor uninstall-autostart --confirm-plan-digest <digest>
```

### What `start` does, and what it does not

`start --mode shadow` (or `--mode supervised`) takes the single-instance lock,
runs the full after-a-crash recovery algorithm, checks the journal and the audit
chain, tells you the classification — and then **stops without contacting any
provider.** It cannot run the loop, because the loop is Phase 4, and it says so
in its own output rather than implying otherwise.

`start --mode limited-auto` refuses *by name*.

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
| `rotation_invariants` | context/usage pressure can never interrupt a running unit, and the rotation decision is unreachable mid-unit |
| `reset_parser` | documented reset notices parse; adversarial, expired, implausible, ambiguous and DST-undefined times all refuse |
| `fixed_scheduler_action` | a scheduled task can only ever run the fixed launcher with its fixed arguments |
| `recovery_classification` | safe / ambiguous / unsafe classify correctly, and a *missing* check counts as a failed one |
| `single_instance_lock` | a live lock is never stolen, and a reused process id is detected |
| `model_change_ipc` | the model-change endpoint is controller-owned and the confirmation cannot be replayed |
| `retention_policy` | every artifact class has limits and deletion needs proven identity |
| `audit_anchor_option_a` | the anchor mechanism exists, refuses `main`, and is not active |
| `notification_hygiene` | a notification carrying a command, an auth link, or a source excerpt is refused |
| `control_response_live_probe` | the live-CLI verification status of the control protocol (see caveat 3) |
| `controller_config` / `model_selection` | only when you pass `--config` and `--model-selection` |

Optional arguments:

```
python -m tools.agent_supervisor doctor \
    --config <path to config.toml> \
    --model-selection <path to model_selection.toml> \
    --manifest <path to a recorded controller_manifest.json> \
    --live          # ONE short real call to Claude; see caveat 3
```

`--live` is the only thing in this whole package that talks to a provider. It
runs at most one bounded turn, works in a throwaway folder, and is off by
default. Its result is recorded per checkout, so later `doctor` runs report it
without calling again — and you should re-run it after any CLI upgrade.

`doctor` exits `0` when everything passes and `1` when anything fails.

### `status`

Renders the durable journal: current state, pending external effects, queued
questions, and whether the audit chain still verifies. It reads; it never writes.

### Everything else

Nothing is deferred. Every command in the directive's list is implemented.

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
| `process.py` | **complete for Phase 4.** Argv-array-only execution, hard-deny argument refusal, minimal child environment, per-process timeouts, executable identity and repo-shadow refusal, and `ProcessContainer` — the Job Object is now the DEFAULT container on Windows, with breakaway flags refused, nested-job failure detected, and the taskkill fallback recorded rather than silently taken. |
| `policy.py` | **complete for Phase 2.** The four-tier engine: HARD-DENY (with `DENY_AND_CONTINUE` vs `DENY_AND_HALT`), AUTO, NOTIFY (notify-exactly-once ledger), ASK. Owner standing grants, per-provider model selection, the five-clause independence check, injection labelling, and path canonicalization. A model recommendation may only *stricten*. |
| `broker.py` | **complete for Phase 2.** Digest-bound approvals over the full Section 13.5 binding, recompute-before-execute invalidation, single-use approvals, the queue, the Codex advisory step bounded to pre-marked categories, and `revoke-all`. Never selects "always allow"; contains no file-write path at all. |
| `claude_runner.py` | **complete for Phase 2.** The confirmed CLI shape, tolerant stream parsing, checkpoint extraction and validation, and the `can_use_tool` control loop wired to the broker. See the caveat below about the response wrapper. |
| `codex_reviewer.py` | **complete for Phase 2.** A fresh read-only process per review, the Section 9 decision rules, a bounded schema retry then halt, and model selection with fallback. |
| `evidence.py` | **complete for Phase 2.** The deterministic collector (the supervisor runs the status commands, not Claude) and the bounded packet builder with explicit truncation, explicit failed collections, and a STOP_FOR_OWNER path when material will not fit. |
| `external_effects.py` | **complete for Phase 2.** Stable idempotency keys, before/after records, reconciliation before any retry, and a refusal to retry anything ambiguous. |
| `push_policy.py` | **checks only.** Every Section 13.6 question is answered; **no push is executed in this phase**, and the module contains no subprocess call at all. |
| `rotation.py` | **complete for Phase 3.** The pre-dispatch decision (SMALL/MEDIUM/LARGE/UNKNOWN from objective features, the two usage thresholds, compaction/checkpoint-count/adherence/oversized signals, and the conservative choice when usage is unreadable); the finish-the-unit invariant; the unsafe-moment refusal list; the handoff schema, its validation, and `review_model`-only verification. |
| `resume_scheduler.py` | **complete for Phase 3.** Six distinct limit classes; structured metadata preferred over a strict, version-stamped notice parser; 12/24-hour, rollover, DST, timezone and clock-jump handling; the durable record; the one named wake task with its exact `schtasks` argv and XML; the fixed-action rule; monotonic leases. |
| `recovery.py` | **complete for Phase 3.** The `RECOVER_BOOT` algorithm, the three classifications, child accounting, competing-writer detection, the durable stop/pause flags, external-effect reconciliation, and the interrupted-turn capability gate. |
| `locking.py` | **complete for Phase 3.** One supervisor per checkout, with liveness probed through `OpenProcess`/`GetExitCodeProcess` (never `os.kill`, which *terminates* on Windows) and pid-reuse detection. |
| `notifications.py` | **complete for Phase 3.** A fixed, redacted, bounded field set. Raw commands, auth links, source excerpts and private paths are refused rather than stripped. A failed delivery leaves the item queued. |
| `remote_approvals.py` | **complete for Phase 3.** Owner identity + request digest + one-time nonce + expiry + task/branch/SHA, approve-once or deny, replay-resistant, plus `revoke-all`. No network I/O in this build. |
| `model_change_ipc.py` | **complete for Phase 3** apart from the pipe *server* loop (below). Origin denial by real process ancestry, endpoint isolation, a confirmation challenge bound to the exact change, checkpoint-boundary application, the full audit record, and out-of-band tamper detection. |
| `retention.py` | **complete for Phase 3.** Pre-operation manifests, quarantine copies verified by hash, per-class retention limits, deletion only of artifacts whose identity is proven three ways, and a restore drill that really destroys and restores a file. |
| `anchor.py` | **mechanism only, by design.** Produces the anchor content and the exact push argv for the dedicated anchor branch. Executes nothing (see caveat 1). |
| `preflight.py` | **complete for Phase 3.** Capability probes, including the opt-in live control-response round trip. |
| `loop.py` | **complete for Phase 4.** The assembled cycle over the real S7 table. Shadow forwards nothing and cannot be made to (`assert_forwarding_allowed` raises). Supervised holds every prompt at `WAIT_FOR_OWNER` until an operator approves that exact digest, and denies when no approval path is reachable. Exactly-once forwarding through the transactional outbox, including the crash window between enqueue and send. The owner-touch ledger counts would-be synchronous stops and can widen nothing. |
| `replay.py` | **complete for Phase 4.** The replay engine over `replay_corpus/`. No process launch, no provider adapter, no filesystem write — all three proven from the module source. Corpus integrity is checked against a manifest of per-file digests. |
| `cli.py` | **every S12.1 command is live; `DEFERRED_COMMANDS` is empty.** `start` always runs the pre-dispatch sequence and dispatches only when every input is named explicitly; `limited-auto` refuses by name. |

### Not built yet (and not pretended)

* **Push EXECUTION.** The push *checks* are complete; no push happens.
* **Anchor publication.** The mechanism exists; publishing is gated (caveat 1).
* **The named-pipe server loop.** Creating a properly restricted pipe is proven;
  running a long-lived unattended pipe server is not built (caveat 4).
* **The Phase 5 shadow pilot** — one real controlled task run in shadow mode,
  measured against the owner-touch budget, ending in a decision packet.
* **`limited-auto`.** Not implemented at all, in any form.

---

## Four honest caveats

### 1. The external audit anchor exists as a mechanism, but has never been published

The audit log's hash chain is complete and detects tampering, truncation, and
reordering (there are seeded tests for all three). Truncation is caught using a
small sidecar "head" file recorded next to the log.

That sidecar sits on the same machine as the log, so it is a **weaker** anchor
than the directive ultimately requires. You chose **Option A** at dispatch: the
controller pushes the chain head to a dedicated anchor branch (`audit/supervisor-anchors`)
that the worker cannot touch.

Phase 3 builds the **mechanism**: at each checkpoint the supervisor produces the
anchor content and the exact `git` argv that would publish it, and stores both
locally. It **publishes nothing**, and `anchor.py` has no execution surface at
all — no `subprocess`, no call site, asserted by a test.

Publication needs **both** of:

1. controller-held push credentials existing (the controller pushes; the worker
   never does), and
2. an explicit activation **you** perform, recorded through directive compliance.

Neither is assumed. Until both hold, the honest statement is: *anchors are
produced locally and detect a rewritten or truncated log on this machine only.*
`doctor` and `activation_status()` both say so.

### 2. Windows process control — the Job Object is now the default

This caveat is **closed** in Phase 4. The Job Object is no longer an opt-in
mechanism; it is the container every launched child gets on Windows, through
`ProcessContainer`. Proven with tests that spawn real processes:

* creating a Windows **Job Object**, configuring it to kill everything on close,
  assigning a real child, asking the *kernel* (`IsProcessInJob`) whether the
  child is really inside it, and confirming the child dies when the job closes;
* terminating a process **and its descendants** via the fallback path
  (`taskkill /T /F`, invoked as an argument array, never a shell string).

Two things worth knowing about how it behaves:

* **Breakaway is refused, deliberately.** `JOB_OBJECT_LIMIT_BREAKAWAY_OK`,
  `JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK`, and `CREATE_BREAKAWAY_FROM_JOB` all
  exist to let a child *escape* the job. A containment mechanism must not offer
  its own bypass, so `assert_no_breakaway()` refuses all three.
* **The fallback is recorded, never silent.** If a host refuses to create a job,
  or refuses to nest ours inside one the process is already in (pre-Windows-8
  behaviour), the container degrades to `taskkill` and writes the reason into
  `ContainmentReport.fallback_reason`. `taskkill` is genuinely weaker — a
  grandchild spawned between enumeration and kill can escape it, where it could
  not escape a job — so nothing is allowed to claim job-strength containment it
  did not actually get. `doctor`'s `containment_default` check reports which one
  this host gives you.

### 3. The Claude control protocol — now verified, but verify it again after an upgrade

The Phase 1 probes captured the permission *request* the CLI sends, verbatim, and
proved that a deterministic deny round-trips and that the CLI fails **closed**
when nobody answers. What they did not record was the exact byte shape of the
*response* wrapper we send back, so through Phase 2 that was the single largest
open risk in the package.

Phase 3 closes it. `doctor --live` runs one bounded turn against the real
executable, answers the permission request with the exact bytes
`claude_runner.build_control_response` produces, and checks the CLI's own
reaction. It counts as verified **only** if the CLI accepts the response, denies
the tool, and echoes our deny message back in `permission_denials`; a protocol
error, a hang, or a tool that runs anyway all read as *not* verified.

Two things to keep in mind:

* Verification is **host- and binary-specific**, so it is recorded in that
  checkout's journal rather than baked into the code. A fresh machine, or a fresh
  checkout, reports `UNVERIFIED` until you run `doctor --live` there.
* **Re-run it after any CLI upgrade.** A new version may change the protocol, and
  a stale "verified" would be worse than an honest "unverified".

### 4. The model-change endpoint: what is proven and what is deferred

Changing a model at runtime has to go through a channel the worker cannot reach.
On Windows that means a named pipe whose permissions admit only your account and
SYSTEM.

**Proven** (measured, not asserted — `doctor` runs it): such a pipe, with a
restrictive DACL, can be created and closed on this host through the standard
library alone.

**Deferred**: the long-lived unattended pipe *server* (overlapped I/O,
per-connection impersonation, reconnect handling). Until that exists, the channel
actually in use is a controller-owned directory inside the runtime folder, and
every request re-checks that it lies outside every worker-writable path.

Either way, the gates that matter are the same and all run today: the caller's
real process ancestry is walked and anything descending from a worker or reviewer
is denied; the change is displayed in full and needs a confirmation token derived
from that exact change; it applies only at a checkpoint boundary; and it writes a
complete audit record.

---

## If you are not the person who wrote this

This section is the plain-language guide D-007 §12.1 asks for. No code editing is
needed for anything in it.

**Which terminal, which command.** Open Windows Terminal or PowerShell. Change to
the controller folder. Everything starts with
`python -m tools.agent_supervisor` followed by a command name. If you only ever
remember one, remember `status`.

**How to pause immediately.** `pause`. It takes effect at once, survives a
reboot, and blocks any scheduled wake-up. `resume` undoes it. If something feels
genuinely wrong, use `emergency-stop` instead: it kills any child processes,
cancels scheduled wake-ups, revokes every pending approval, and sets a flag that
*nothing* clears by itself — not a restart, not a scheduled task, not recovery.
To clear it you must deliberately run `stop --clear`.

**What the statuses mean.**

| You see | It means |
|---|---|
| `IDLE` | nothing is running |
| `CLAUDE_RUNNING` | a bounded unit of work is in progress |
| `ROTATION_PENDING` | a threshold was crossed; the current unit will **finish** first, then hand over to a fresh session |
| `WAIT_FOR_OWNER` | a question is queued for you |
| `USAGE_LIMIT_WAIT` / `SCHEDULED_RESUME` | a provider limit was hit; the wake-up is scheduled |
| `PAUSED_RECOVERY` | something could not be verified after an interruption; it is waiting for you |
| `EMERGENCY_STOPPED` / `HALTED` | stopped deliberately; only you restart it |

**Where queued questions are, and how to answer.** `pending-approvals` lists
them, each with a long digest. Answer with `approve-once <id> <digest>` or
`deny <id> <digest>`. Copy the digest exactly — it is what ties your answer to
that one request. Answering remotely is possible only through an authenticated,
digest-bound, single-use, expiring link; a plain "yes" in a message is **not** an
approval and will be refused.

**How to restart after a crash.** Just run `start --mode shadow` again. It works
out what happened before doing anything, and it will not resume anything it
cannot verify.

**Verified recovery vs. an ambiguous pause — the important distinction.**

* *Verified safe*: the last action definitely finished, and everything still
  matches. Even then, this build does **not** continue on its own, because
  unattended mode has never been switched on.
* *Ambiguous*: an action may or may not have gone through — say a pull request
  that might already have been created. The supervisor will **not** guess and
  will **not** retry. It checks read-only evidence to prove which happened; if it
  cannot prove it, it stops and asks you. That is the pause you should read
  carefully.

**Inspecting or cancelling a wake-up.** `schedule-status` shows the limit class,
the deadline, and whether a wake task is scheduled. `cancel-scheduled-resume`
removes the schedule. Removing the operating-system task itself is a separate,
explicit act: `autostart-plan` shows exactly what would be created (it changes
nothing), and `uninstall-autostart` removes it once you quote the plan digest.

**What can and cannot resume by itself.**

| Machine state | What happens |
|---|---|
| Awake | a scheduled task fires at the deadline |
| Asleep or hibernating | possible *only* if you approved a wake task and your hardware supports it |
| Fully powered off | **software cannot switch your computer on.** A logon task starts the supervisor at your next sign-in, and it resumes then if the deadline has passed |

Nobody here will ever claim your machine can wake itself from off.

**Which model is running.** `status` and the audit log record the provider, the
model name, and the digest of the model selection in force for every decision.
Changing a model needs `set-codex-model` / `set-claude-model`, which shows you the
old and new values and requires a confirmation token unique to that change.

**Confirming unattended mode is off.** `status`, `doctor`, and `recovery-status`
all print it. It reads `limited-auto: disabled` and it cannot read anything else,
because this build contains no code that can enable it.

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
python -m unittest tools.test_agent_supervisor_rotation
python -m unittest tools.test_agent_supervisor_scheduler
python -m unittest tools.test_agent_supervisor_recovery
python -m unittest tools.test_agent_supervisor_ipc
python -m unittest tools.test_agent_supervisor_endurance
python -m unittest tools.test_agent_supervisor_loop
python -m unittest tools.test_agent_supervisor_replay
python -m unittest tools.test_agent_supervisor_invariants
python -m unittest tools.test_agent_supervisor_adversarial
python -m unittest tools.test_agent_supervisor_crash
python -m unittest tools.test_agent_supervisor_fuzz
```

The last six are Phase 4's. Three of them are worth explaining:

* **`invariants`** is a register: each of the fifteen executable invariants in
  the directive has a test whose *name* carries its number, and a meta-test
  fails if any invariant loses its coverage.
* **`crash`** kills the journal handle and reopens it at every external-effect
  and journal boundary — before and after each one — and checks that the run
  either resumes exactly or refuses, never repeating a performed effect.
* **`fuzz`** is seeded (`SEED = 20260803`), so it fuzzes the same corpus on every
  machine. A fuzz test that only sometimes finds a defect is not evidence. It
  found a real one: see "a defect this phase found and fixed", below.

Standard-library `unittest` only — no new dependency anywhere in this package.
The provider executables in the tests are **fake** local scripts, and `schtasks`
is a fake too — the real Windows Task Scheduler is never touched. No test makes a
network call, uses a token, or touches your real runtime directory.

The only code path in the package that contacts a provider is `doctor --live`,
which is opt-in, bounded to one turn, and never runs during the test suite.

---

## A defect this phase found and fixed

The path-normalization fuzzer generated `.env;/nul` and **crashed the policy
engine**. On Windows, `os.path.realpath` maps a trailing `nul` to the device
`\\.\nul`, and `os.path.relpath` then raises `ValueError` rather than returning a
path. `resolve_target` promises never to raise and always to return a named
reason; instead it propagated an exception out of the classifier.

That is a fail-open shape: an unhandled exception in the middle of a policy
decision is not a denial, it is a crash whose consequences depend entirely on who
catches it. The fix refuses every Windows reserved device name (`nul`, `con`,
`aux`, `prn`, `com1`–`com9`, `lpt1`–`lpt9`) *before* resolution is attempted,
returns the existing `device_path` reason, and additionally guards the
`realpath`/`relpath` calls so a cross-mount comparison degrades to a refusal
instead of an exception.

The check runs on every platform, not just Windows, so a Linux CI run enforces
the same rule a Windows host does. Ordinary names that merely *contain* a device
word — `console.py`, `nullable.py`, `connection.py` — are unaffected, and there is
a test for that too. The fix only ever adds a denial; it removes none.

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
* A unit that has been dispatched is never killed because a token or context
  threshold was crossed. The flag is set, the unit finishes, and rotation happens
  before the next one. The type that carries that decision cannot even express
  "terminate".
* A unit's limits are fixed before it starts and cannot be raised while it runs.
* A reset time is never invented. Ambiguous, implausible, expired, unparseable,
  or DST-undefined all become a question for you.
* Nothing contacts a provider before a recorded deadline — not a retry, not a
  poll, and certainly not a model asked whether it is time yet.
* A durable stop or pause beats every scheduled task and every autostart.
* A scheduled task can only ever run one fixed launcher with fixed arguments.
* One supervisor per checkout. A lock whose owner is alive is never taken.
* A backup is not permission to delete: recovery must be *verified* first, and
  cleanup only ever touches artifacts whose identity is proven three ways.
* A notification carries no secret, no raw command, no auth link, and no source
  excerpt — it points you at where to look instead.
* A remote approval is bound to your identity, the exact request, a one-time
  nonce, and an expiry. A bare "yes" is not an approval.
* A model change needs a confirmation token derived from that exact change, and
  applies only at a checkpoint boundary.
