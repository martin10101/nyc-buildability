# Agent Supervisor — Phase 1 status

This is the deterministic Codex ↔ Claude supervisor bridge described by owner
directive **D-007**. It is being built in five phases. **Only Phase 1 exists
today.**

**Nothing in this package can run your project.** It cannot start Claude, cannot
call Codex, cannot push, cannot merge, and cannot accept anything. The unattended
writing mode (`limited-auto`) is not implemented at all, and turning it on later
is a separate, explicit decision that only you can make.

---

## What you can actually run today

Two commands, both read-only.

```
python -m tools.agent_supervisor doctor
python -m tools.agent_supervisor status
```

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
replay start pause resume stop emergency-stop verify-controller
recovery-status schedule-status cancel-scheduled-resume autostart-plan
install-autostart uninstall-autostart pending-approvals approve-once deny
revoke-all set-codex-model set-claude-model export-handoff
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
| `cli.py` | **`doctor` and `status` live**; everything else refuses by name. |

### Not built yet (and not pretended)

The four-tier policy engine, standing grants, the approval broker, the Claude
runner, the Codex reviewer, the evidence collector, session rotation, crash
recovery classification, usage-limit wake scheduling, notifications, remote
approvals, quarantine/restore, and the replay engine are **Phases 2–4**.

---

## Two honest caveats

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
