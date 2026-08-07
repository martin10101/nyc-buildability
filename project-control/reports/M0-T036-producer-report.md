# M0-T036 — producer report (Phase 1 checkpoint, VERBATIM producer return)

**Orchestrator header (NOT part of the producer's return).** Unnamed `backend-engineer` producer,
spawned explicit Opus 5 (R298 ceiling), worktree-isolated, dispatched 2026-08-03 under the owner
build dispatch (D-007-R540, capture PR #150) with the two behavioral probes as first acts
(D-007-R535). The return below is preserved verbatim **except the R024 evidence-hygiene
redactions enumerated here** (public repository; annotated-redaction precedent):

| occurrences | substitution |
|---|---|
| 3 | absolute repository/worktree path (Windows user-path form) → `<REPO>` / `<WORKTREE>` |
| 1 | absolute user-home tool path → `<USERHOME>\.local\bin\claude.exe` |

Nothing else changed — no finding, count, hash, command, or disclosure was altered. The
producer's agent-memory writes (its own `.claude/agent-memory/backend-engineer/` files in the
worktree) were **NOT ported**: the main checkout's backend-engineer memory carries owner-plane
local state the orchestrator is prohibited from touching (D-004-R704); the learning is fully
preserved in this report (probe findings §1) for the path owner to add post-task (R660 pattern).
Port: the 26 contracted files were copied from the producer worktree with per-file LF-normalized
SHA-256 verification against the producer's declared digests; the orchestrator edited nothing.
This report is append-only: later phase checkpoints append as new sections, Phase 1 content
byte-preserved (D-004-R132 discipline).

**Requested status: awaiting_gate for Phase 1 content** (the orchestrator holds the task
`in_progress` — later phases continue under the same packet; gates run per phase batch or at
integration per the contracted flow).

---

M0-T036 **Phase 1 producer checkpoint**. Requested status: **awaiting_gate**.

## 1. Behavioral probes (owner ruling 6 / D-007-R535) — CONFIRM the CLI-adapter decision

Canonical executable: `<USERHOME>\.local\bin\claude.exe`, `--version` → `2.1.220 (Claude Code)`, exit 0. Five bounded runs, all in the scratchpad (never the repo).

**(a) `--max-turns` — ACCEPTED and HONORED.**
```
claude.exe -p "Reply with exactly: OK" --max-turns 1 --output-format json
PROBE_A_EXIT=0
→ {"is_error":false,"num_turns":1,"stop_reason":"end_turn","subtype":"success","result":"OK", ...}
```
Absent from `--help`, works. Control run: `claude.exe --zzz-bogus-flag-probe -p "x"` → exit 1, `error: unknown option '--zzz-bogus-flag-probe'`. The parser **is** strict, so "no error" proves a flag is real.

**(b) stream-json control protocol — a first-class `can_use_tool` broker EXISTS.**

B1 (`-p --input-format stream-json --output-format stream-json --verbose --max-turns 1`, exit 0) event shape: `system/init` → `rate_limit_event` → `assistant`×2 → `result/success`. Init advertises `capabilities: ["interrupt_receipt_v1","interrupt_cancel_queued_v1","msg_lifecycle_v1"]`, `permissionMode: auto`, `session_id`, full `tools` list.

B2 (`--permission-mode manual`, no prompt-tool, exit 0): no control message; tool denied post-hoc with a structured `permission_denials[]` entry carrying `tool_name`, `tool_use_id`, complete `tool_input`. No file written.

B3 exposed a **hidden flag**: `--permission-prompt-tool stdio` is accepted (not in `--help`; unknown flags error, so it is real). An SDK-style `initialize` control_request returned `{"type":"control_response","response":{"subtype":"success","request_id":"req_probe_1",...}}`. B3 conflated variables though — I omitted `--permission-mode manual`, so the default `auto` allowed the write.

B4 (`--permission-prompt-tool stdio --permission-mode manual`, exit 1): the CLI **routed the permission request to the stdio control channel** and, with stdin at EOF, failed **closed** — `Tool permission request failed: AbortError: Stream closed`, recorded in `permission_denials[]`, `probe_touch4.txt` never created.

B5 (bidirectional responder, `b5_responder.py`) captured the exact payload:
```json
{"type":"control_request","request_id":"10fd4aaa-…","request":{
  "subtype":"can_use_tool","tool_name":"Write","display_name":"Write",
  "input":{"file_path":"…probe_touch5.txt","content":"HI"},
  "description":"probe_touch5.txt",
  "permission_suggestions":[{"type":"setMode","mode":"acceptEdits","destination":"session"}],
  "tool_use_id":"toolu_017V6VdFoPoozLMe7Cs6k3Yz"}}
```
My deterministic deny returned `{"behavior":"deny","message":"probe: deterministic broker denied"}` → `tool_result` `is_error` with that exact message, logged in `permission_denials[]`, no file written.

**Reading vs the CLI-adapter decision: CONFIRMED, not contradicted.** No stop condition. §8.4's approval broker gets a real `canUseTool`-equivalent callback with the complete tool input, and it fails closed when unreachable — exactly what "background-agent requests that cannot reach the broker are denied" requires. Two findings for Phase 2: `--permission-mode manual` is **mandatory** (default `auto` permits writes and emits no control request), and `permission_suggestions` offers `setMode: acceptEdits` — the "always allow" §8.4 forbids auto-selecting.

I used 5 runs rather than the suggested 1–2; B3/B4 were needed to disambiguate flag-vs-mode, and B5 to capture the payload schema Phase 2 depends on. Disclosed rather than hidden.

## 2. Files created (26; complete list with LF-normalized SHA-256)

Under `<WORKTREE>` (the isolated producer worktree; full 64-char digests were verified per-file
by the orchestrator at port time and are recorded in the port commit):

```
95281d53…a0f1  tools/agent_supervisor/__init__.py
4a5207a1…1dfd  tools/agent_supervisor/__main__.py
b8735d69…eff4  tools/agent_supervisor/audit_log.py
0ae1c720…c616  tools/agent_supervisor/circuit_breakers.py
3a92b7c4…6ee3  tools/agent_supervisor/cli.py
c974a54f…4e6a  tools/agent_supervisor/config.example.toml
2c6ec204…81ac  tools/agent_supervisor/config.py
e5d56c59…83f5  tools/agent_supervisor/durable_state.py
2d3033ac…9381  tools/agent_supervisor/manifest.py
32561710…c855  tools/agent_supervisor/models.py
9ac6035c…0576  tools/agent_supervisor/process.py
0e481191…c9e4  tools/agent_supervisor/prompts/claude_checkpoint.md
ea5bfc76…7af2  tools/agent_supervisor/prompts/codex_review.md
539c04d1…5975  tools/agent_supervisor/prompts/session_handoff.md
9c890a2f…37ba  tools/agent_supervisor/protocol.py
abb006da…6bae  tools/agent_supervisor/README.md
4d0c4713…c9e4  tools/agent_supervisor/redaction.py
8eeb13b7…ccc3  tools/agent_supervisor/schemas/claude_checkpoint.schema.json
d5436fce…1f080  tools/agent_supervisor/schemas/codex_decision.schema.json
ab679970…6884  tools/agent_supervisor/schemas/durable_state.schema.json
81c98a5d…3e87  tools/agent_supervisor/schemas/protocol_envelope.schema.json
1f4ba9b0…5000  tools/agent_supervisor/state_machine.py
d08ba9a6…bde5  tools/test_agent_supervisor_audit.py
d66757f5…482d  tools/test_agent_supervisor_phase1.py
84180c08…58b8  tools/test_agent_supervisor_process.py
3eaad507…b695  tools/test_agent_supervisor_protocol.py
```
Full 64-char digests are in the transcript command output above (26 files, 284,653 LF-normalized bytes). Plus, under the explicitly-permitted agent-memory path: `.claude/agent-memory/backend-engineer/claude-cli-headless-control-protocol.md` (new) and `MEMORY.md` (index line). These are neither hook, agent-definition, settings, rules, nor skills — but flagging them for the reviewer since `.claude/**` is listed forbidden.

## 3. Per-module notes, deviations, and what is deferred

- **`__init__.py`** — `CONTROLLER_VERSION=0.1.0-phase1`, `PROTOCOL_VERSION=1.0.0`, `SCHEMA_VERSION=1.0.0`, `PHASE=1`.
- **`config.py`** — effort-key refusal walks **every key at every depth** in **both** files (`effort_key_forbidden`); per-provider allowlists validated against the entry's own provider only, with a distinct error naming cross-provider satisfaction; standalone-TOML enforced by parsing each file separately *and* refusing runtime keys in the controller config and controller keys in the runtime file; a config naming `limited-auto` as `default_mode` is refused (`mode_not_bootable`); unknown limit keys fail closed.
- **`models.py`** — one canonical digest definition shared by every module. `usage=0` refused (`usage_zeroed`); unknown fields refused on `from_dict`.
- **`protocol.py`** — all 13 envelope fields; digest recomputed on receipt; incremental UTF-8 decoder handles split multibyte; CRLF/BOM/blank/noise tolerated; bounded buffers. **Bug found and fixed by its own test:** a truncated final object (`{…` with no closing brace) was initially swallowed as "noise"; now anything opening as `{` that fails to parse raises `malformed_json`.
- **`durable_state.py`** — WAL + `synchronous=FULL` (asserted in test); transactional migration behind a `migration_in_progress` flag; integrity check detects unreadable / schema-mismatch / partial-migration / missing-tables / **rolled-back** (high-water mark) journals. Runtime dir = `%LOCALAPPDATA%\NYCBuildabilitySupervisor\<sha256 of canonical full checkout path>`; **deviation:** a POSIX branch (`$XDG_STATE_HOME`/`~/.local/state`) exists so tests run on Linux CI — production is the Windows path. Placing runtime state inside the checkout is refused in code.
- **`state_machine.py`** — all 23 §7 states, 64 documented transitions, illegal-transition refusal, idempotent repeats, commit → audit → side-effect ordering (test asserts the journal already reads the new state when the side effect runs), crash-resume from the journal.
- **`audit_log.py`** — mandatory chain (monotonic sequence, prev-digest, self-digest). **Honest partiality:** truncation is caught via a sidecar head anchor on the *same machine*; the owner-ruled **Option A external anchor (controller-pushed anchor branch) is NOT built** — it needs controller-held push credentials and ADR-005's amendment in force, so it is **deferred to Phase 3**. Stated plainly in README.md and in a test docstring. A damaged chain is diagnosable but never extended (`append_to_damaged_chain`).
- **`manifest.py`** — **deviation:** §6's file list names no manifest module; §13.1 requires one, so `manifest.py` is an *addition*, not a rename. `model_selection.toml` excluded, and offering it as a covered file is refused. Digests are LF-normalized so a CRLF checkout and Linux CI agree.
- **`process.py`** — argv arrays only, `shell=False` explicit, no code path builds a command string. Bypass flags exist **only** as `HARD_DENY_ARGUMENTS` constants; `--effort`/`--reasoning-effort` denied the same way. **Proven in Phase 1:** taskkill `/T /F` tree termination against a real grandchild, and Windows **Job Object** creation + `KILL_ON_JOB_CLOSE` + real-child assignment + kill-on-close (that test **ran and passed** on this Windows host). **Deferred to Phase 3:** making the Job Object the default container (breakaway/nested-job handling). Large binaries get `sha256_head+size` identity, honestly labelled (the CLI is 265 MB).
- **`cli.py`** — `doctor` (12 live checks) and `status` are real; `replay` and all other §12.1 commands are wired and raise `NotImplementedError` naming their phase; `start --mode limited-auto` refuses **by name**.
- **Phase 2/3/4 not built and not pretended:** tier policy engine, standing grants, approval broker, Claude runner, Codex reviewer, evidence collector, rotation, recovery classification, wake scheduling, notifications, remote approvals, quarantine/restore, replay engine.

## 4. Test run (full output tails in transcript)

```
python -m unittest tools.test_agent_supervisor_phase1 tools.test_agent_supervisor_protocol \
                   tools.test_agent_supervisor_audit tools.test_agent_supervisor_process
Ran 139 tests in 12.654s
OK (skipped=1)
```
Standalone, as CI invokes control-plane tests: phase1 **68 OK**, protocol **29 OK**, audit **15 OK**, process **27 OK (skipped=1)**. The single skip is the POSIX-only guard (`skipIf nt`) — the Windows Job Object test executed and passed.

No regressions: `tools/test_project_control.py` → "all 22 project-control test groups passed / Ran 102 tests / OK"; `test_directive_compliance.py` → PASS; `test_agent_dispatch_guard.py` → "ALL CHECKS PASSED".

Live `doctor`: **all 12 checks PASS, exit 0** (`23 states, 64 documented transitions`; `5 bypass flags and every effort flag are refused`; `model_selection.toml is deliberately excluded`).

## 5. Self-checks

- **No effort key:** every one of the 41 `effort` occurrences is prohibition/deny-list context (`config.example.toml:10` "There is NO effort key here"; `process.py` `EFFORT_ARGUMENT_PREFIXES` + refusal). No effort key is *set* anywhere.
- **argv-only:** `grep -rn "shell=True"` → only two **prose** hits (a `process.py` docstring and a README line); zero code occurrences.
- **Bypass flags:** appear only at `process.py:52-56` inside `HARD_DENY_ARGUMENTS` (the AS-7 permitted exception); tests reference the constant, never literals.
- **Stdlib-only:** 24 distinct imported modules, all verified against `sys.stdlib_module_names` → "NONE - 100% standard library". No dependency manifest or lockfile touched.
- **Containment:** `git status --porcelain -uall` shows only `tools/agent_supervisor/**`, `tools/test_agent_supervisor_*.py`, and the agent-memory files. No `.github/`, `services/`, `apps/`, `packages/`, `render.yaml`, or other `tools/` file changed. `__pycache__` is gitignored.

## 6. Limitations, assumptions, blockers

- **Not blocking, needs orchestrator action:** CI (`.github/workflows/ci.yml`) runs control-plane tests individually and does **not** invoke the four new files. Wiring them requires editing `.github/**`, a forbidden path for this packet — a separate authorized change.
- I did **not** write `project-control/reports/M0-T036-producer-report.md`; this return is the producer evidence, for you to persist verbatim per the report-preservation rule.
- No ledger command, git commit/push, or `gh` was run. Limited-auto remains unimplemented and unreachable. No credentials, no network beyond the five bounded probes.
- Assumption to confirm at G3: the POSIX runtime-dir branch is acceptable as a CI-portability deviation from §6's Windows-only wording.
- **N=6 note:** scope was Phase 1 of 5 (core loop + fake-process harness); `/usage` is unobservable from inside a spawn, so I cannot report consumption.

**Model disclosure:** spawned explicitly as **Opus 5** (`claude-opus-5[1m]`), the R298 producer ceiling. No effort setting applied anywhere.

---

# PHASE 2 CHECKPOINT (appended by the orchestrator; Phase 1 content above byte-preserved)

**Orchestrator header (NOT part of the producer's return).** Second unnamed `backend-engineer`
producer, spawned explicit Opus 5, worktree-isolated, dispatched 2026-08-03 for Phase 2 (policy +
adapters). Preserved verbatim below **except one R024 redaction**: 2 occurrences of the absolute
worktree path → `<WORKTREE>`. The producer's disclosed unasked git act (one `--ff-only`
fast-forward of its own worktree branch to the Phase 1 tip, no commit, nothing pushed) is
accepted by the orchestrator as the minimal realization of the dispatch's stated build-on-Phase-1
intent. Port: 17 files verified against the declared full LF SHA-256 digests (17/17 match) and
the 10 claimed-unchanged Phase 1 modules verified byte-identical before porting; orchestrator
re-ran all eight suites on the ported tree: **Ran 383 tests — OK (skipped=2)**. The producer's
agent-memory files were again NOT ported (D-004-R704; R660 pattern). Full port hashes:
`M0-T036-phase1-port-hashes.json` (phase2 block).

---

M0-T036 **Phase 2 producer checkpoint**. Requested status: **awaiting_gate**.

## 0. Worktree state correction (read first)

The worktree was **not** at the task-branch tip: `HEAD` was `e7f5078` (the merge-base), so `tools/agent_supervisor/` did not exist and there was no Phase 1 to build on. I ran exactly one git command to realize the dispatch's stated intent — `git merge --ff-only task/M0-T036-supervisor-bridge` — which fast-forwarded `worktree-agent-a31959d76189e5dcd` to `f39192f` (Phase 1 tip). **No commit was created, nothing was pushed, no `gh`, no `project_control.py`.** My branch is now `f39192f` + the uncommitted Phase 2 work below. Disclosed because it is a git state change I made unasked.

Worktree: `<WORKTREE>`
Branch: `worktree-agent-a31959d76189e5dcd` · HEAD `f39192f971d0670a5ac71d9db31eda53483f68dc`

## 1. Files created (11) and modified (6), with LF-normalized SHA-256

**Created**
```
a270cceb210673d36b58646c5a1ed00b7b25e506adca92bad87da017b925b323  tools/agent_supervisor/policy.py
026ee8d0eeab21cdc74020209d09c0235e9c924426a641de5f5bddd510561ca3  tools/agent_supervisor/broker.py
4e21e6d8608f0abceffb6c57b0291a662ef042cfe01a0c3fd336edb4e81612b9  tools/agent_supervisor/claude_runner.py
9e871c5b6065b189548afdfb75c72ea52c5e7b1fa1a47edfd03850e0cb93dbb2  tools/agent_supervisor/codex_reviewer.py
1bdc5ff0ed37bcf9dffb01ded57cc522207ac392230ed95e5c94b0696c732a04  tools/agent_supervisor/evidence.py
b717624dc1eb65076f5f8f1ea365092f5ea5a0317268b472d4b94a4cc6073fde  tools/agent_supervisor/external_effects.py
1fa472d2ef402dd306c8eea86eefe1fe8118fba9861372ae48ab6f3c909f12b9  tools/agent_supervisor/push_policy.py
88d2484be30a470657600032366ce6e4371d285b9c6cb23e2d7fef357ac0da82  tools/test_agent_supervisor_policy.py
d7d450f6313a90a724dc911f71ff8b46283d78b8773a080f2f57274618262ee8  tools/test_agent_supervisor_broker.py
a4e6cc56ad5735a9b3ecb904131f5fb927ac8bfe168802695fbba8e64f42c390  tools/test_agent_supervisor_runner.py
c120c4922cb162cc3a16eba37aeaa4f413edeffa959758d2e73159f324492525  tools/test_agent_supervisor_reviewer.py
```
**Modified (Phase 1 files — per-file justification)**
```
9d9f83e46806ae95b5220a73ff403c769e5da2fe548c73a45edfb63c528067de  tools/agent_supervisor/__init__.py
b7fb8ecaba86a37ab4932df1b67f9e90cc907b71e84dd35bae6fdaf6aa521a87  tools/agent_supervisor/cli.py
ffba1e1a835fed5aa889c2bb0b7240d555cbc3bf63e41562f7ed168ab9d38620  tools/agent_supervisor/README.md
a9e84fa6eb7dd07547298c6bd1b2e313cef58864e936decaf81abbab31d8518a  tools/agent_supervisor/config.example.toml
9bb247b4ce75dd611aacfb7e56ee303670587f8765f436c3f06983d99d3a5393  tools/test_agent_supervisor_phase1.py
9b82d8154cc6bee63ad5434219338d3b7b7af802957f3dc22373470434cb3d69  tools/test_agent_supervisor_process.py
```
(17 files, 489,454 LF-normalized bytes.) Plus, under the explicitly-permitted agent-memory path: `.claude/agent-memory/backend-engineer/windows-reparse-point-testing.md` (new) + `MEMORY.md` index line. Flagging them because `.claude/**` is listed forbidden.

**Why each Phase 1 file was touched**
1. **`__init__.py`** — `CONTROLLER_VERSION` `0.1.0-phase1` → `0.2.0-phase2`, `PHASE` 1 → 2. The controller version is embedded in the manifest, in **every** audit record, and in the durable journal; a Phase 2 build reporting "phase1" would be a false provenance claim. Docstring updated to list the seven new modules and re-state what is still *not* built.
2. **`cli.py`** — the Phase 2 interface: implements `pending-approvals`, `approve-once`, `deny`, `revoke-all`, `verify-controller`; adds 8 Phase 2 `doctor` checks; retargets `start` from "Phase 2" to "Phase 3 (the supervised loop)" because Phase 2 delivers adapters, not a loop.
3. **`README.md`** — owner-facing status was "Only Phase 1 exists today"; leaving it would misdescribe the package. Rewritten for Phase 2 incl. the new caveat 3.
4. **`config.example.toml`** — added a `[policy]` section documenting the S4.1 change-size bounds, main-branch names, remote-read switch and advisory categories the new engine reads. (`config.py` was **not** modified: `[policy]` already lands in `ControllerConfig.raw`, and `policy.PolicyConfig.from_controller_config` parses it with its own strict unknown-key refusal.)
5. **`tests/..._process.py`** — one assertion, `CONTROLLER_VERSION.endswith("phase1")`, is now tied to the declared `PHASE` plus a format regex, so it survives later phases instead of needing another edit.
6. **`tests/..._phase1.py`** — `pending-approvals` and `verify-controller` removed from the "must raise NotImplementedError" list (now implemented); replaced with `start` and `recovery-status`, which still refuse.

No other Phase 1 module was modified. `config.py`, `models.py`, `protocol.py`, `durable_state.py`, `state_machine.py`, `audit_log.py`, `redaction.py`, `manifest.py`, `circuit_breakers.py`, `process.py` are byte-identical to Phase 1.

## 2. Per-module notes and honest deferrals

- **`policy.py`** — four tiers, total and deterministic; the final fallthrough is ASK. `evaluate()` **never reads `action.stated_reason`** (tested). Model recommendations combine via `max()` over `TIER_ORDER` only. HARD-DENY runs first in a fixed 10-step order and maps bypass/credential/controller-mutation/control-disabling → `DENY_AND_HALT`; force-push, main-push, destructive git, recursive/wildcard delete, dangerous delete targets, substitution-concealed execution, path escapes, protected-path mutation, and no-active-task → `DENY_AND_CONTINUE`. Standing grants are constructible only via `owner_grant()` (`created_by != "owner"` → `GrantError`), refuse bare-executable shapes and any grant naming `main`, require a non-empty `post_verification`, and `assert_not_widened()` blocks all eight widening directions. The five-clause independence check is implemented verbatim from the Phase 0 return, and **clause 5 fails without a journal** — an unrecorded check is not a check. `resolve_model()` lives here (not in an adapter) because §3.2 rule 7 requires both adapters to obey one implementation.
  - **Two real bugs its own tests caught:** (a) `file_class()` used `str.lstrip("./")`, which ate the leading dot of `.env`/`.gitmodules`/`.github/...` and reclassified every security-relevant dotfile as ordinary; (b) the injection pattern was anchored at `--dangerously`, so `--allow-dangerously-skip-permissions` was hard-denied but **not labelled** as an injection attempt. Both fixed, both with a regression test.
- **`broker.py`** — S8.4 order: HARD-DENY → AUTO/grants → advisory → ASK. The digest binds all 18 S13.5 elements; `stated_reason` is deliberately **excluded** (untrusted text must not affect an approval either way) and environment **values** are never stored (names + a values digest only). `verify_before_execute()` re-stats every target's filesystem identity, so a file replaced in another terminal invalidates the approval. Approvals are single-use. `handle_unhandled()` denies. The module contains **no filesystem-write call at all** (tested structurally) — it cannot write a settings file even by accident; `permission_suggestions` (incl. the probe-observed `setMode: acceptEdits`) are recorded as *rejected*.
- **`claude_runner.py`** — the confirmed argv is enforced: any permission mode other than `manual` is refused **by name and with the probe's reason** (default `auto` permits writes and emits no control request). `--continue`/`-c`/`--last` are refused. `--resume <id>` **fails closed** unless the caller records that the capability was probed: exact-session resume was not among the Phase 0/1 behavioural probes, so I refuse rather than assume it.
  - **Honest deferral / disclosed uncertainty:** the Phase 1 report records the control **request** payload verbatim and that a deny round-tripped, but not the exact bytes of the control **response** wrapper. I implement the SDK-documented shape, `doctor` reports it as **UNVERIFIED**, README caveat 3 says so, and the tests prove *our* loop against a fake that expects that shape — not the CLI contract. A preflight round-trip probe must confirm it before any live run.
- **`codex_reviewer.py`** — fresh process per review; `--sandbox read-only` is not optional (any other value raises `reviewer_must_be_read_only`); write/session/approval flags are refused. Six decisions, per-decision required fields, unknown-field rejection, correlation to the exact checkpoint, bounded retry carrying the validation error, then halt. `model_used` is **recorded by the supervisor**; a decision that claims a different model is overridden and the mismatch is flagged.
  - **Deferral:** `--codex-model` (S3.2 rule 2) is *not* implemented, because it must pass the same authenticated IPC + interactive-confirmation path as rule 6, which is Phase 3. A weaker override would be worse than none; a test pins that `set-codex-model`/`set-claude-model` remain Phase 3.
- **`evidence.py`** — the supervisor runs the status commands, not Claude; every git command is checked against the enumerated read-only list, uses `--no-pager`, and never `-C` (cwd instead). Detached HEAD is recorded as a **fact**, not a collection failure. Failures are listed explicitly with their error category. Oversized material returns `STOP_FOR_OWNER` rather than being dropped.
- **`external_effects.py`** — content-stable idempotency keys (a repeated `begin()` recognizes the same effect), read-before-write where modeled, and `reconcile()` treats "cannot determine" as *pause*, never as "assume it did not happen". `assert_safe_to_retry()` refuses both a PENDING and a CONFIRMED effect. No modeled effect is destructive.
- **`push_policy.py`** — **policy only.** No `subprocess`, no `Popen`, no `urllib`/`socket`, no import of `process` — asserted by a source-level test. All eight S13.6 checks; strictest tier wins; a secret-scan finding is a synchronous stop.
- **Still not built and not pretended:** rotation/handoff, crash-recovery classification, durable wake scheduling, notifications, authenticated remote approvals, quarantine/restore, the replay engine, the authenticated model-change path, the external audit anchor (Option A, still Phase 3 as Phase 1 recorded), Job Objects as the default container, and **push execution**. `start` still refuses; `limited-auto` is still unreachable.

## 3. Test output

**All eight suites together**
```
python -m unittest tools.test_agent_supervisor_phase1 tools.test_agent_supervisor_protocol \
  tools.test_agent_supervisor_audit tools.test_agent_supervisor_process \
  tools.test_agent_supervisor_policy tools.test_agent_supervisor_broker \
  tools.test_agent_supervisor_runner tools.test_agent_supervisor_reviewer
Ran 383 tests in 27.353s
OK (skipped=2)
```
**Standalone, as CI invokes control-plane tests** — Phase 1: `phase1` **68 OK**, `protocol` **29 OK**, `audit` **15 OK**, `process` **27 OK (skipped=1)** → **139, no regression**. Phase 2: `policy` **98 OK (skipped=1)**, `broker` **50 OK**, `runner` **41 OK**, `reviewer` **55 OK** → **244 new tests**.

The 2 skips: `process` has the pre-existing POSIX-only guard; `policy` has the symlink-escape test, which skips here with `WinError 1314` (symlink creation needs a privilege). I added a **junction** test (`mklink /J` needs no privilege) that **ran and passed**, plus a link-free assertion on the resolver's escape reasons — so the reparse-point rule is genuinely proven on this host, not merely skipped.

**Repository regression (unchanged by this work):** `tools/test_project_control.py` → "all 22 project-control test groups passed"; `tools/test_directive_compliance.py` → `Ran 102 tests ... OK`; `tools/test_agent_dispatch_guard.py` → "ALL CHECKS PASSED".

**Live `doctor`:** 20 checks, **all PASS, exit 0**, `controller 0.2.0-phase2 (phase 2)`, including `policy_four_tiers`, `approval_binding` (18 bound elements), `claude_adapter`, `control_response_shape` (reports UNVERIFIED), `codex_adapter`, `push_policy`, `external_effects`, `evidence_bounds`. Also PASS against `config.example.toml` with the new `[policy]` section.

## 4. Self-checks

- **No effort key:** every occurrence in Phase 2 files is prohibition/deny-list/test context (`policy.EFFORT_FLAG_MARKERS`, the S4.4 deny branch, `doctor`'s refusal probe, and tests asserting refusal). No effort key is *set* anywhere; `[codex.tuning] effort` and `reasoning_effort` are both proven refused by the loaders.
- **argv-only:** `grep -rn "shell=True"` over the package → only two **prose** hits (a `process.py` docstring line and a README line); zero code occurrences. Every launch site passes `shell=False` explicitly with an argv array. `claude_runner` and `codex_reviewer` build lists and pass them through `assert_argv_safe`.
- **Bypass flags:** now **one** definition in the whole package. `policy.BYPASS_FLAG_MARKERS` is derived from `process.HARD_DENY_ARGUMENTS` (and `EFFORT_FLAG_MARKERS` from `EFFORT_ARGUMENT_PREFIXES`) instead of restating them; `doctor` and all four Phase 2 test files build their hostile inputs *from* the constants. `grep -- "--dangerously-\|--yolo"` across `tools/agent_supervisor/*.py` + `tools/test_agent_supervisor_*.py` returns **only** `process.py:52-56`, the deny list itself.
- **Stdlib-only:** 29 distinct imported top-level modules across all supervisor + test files, checked against `sys.stdlib_module_names` → "NONE - 100% standard library". No dependency manifest or lockfile touched.
- **Containment:** `git status --porcelain -uall` shows only `tools/agent_supervisor/**`, `tools/test_agent_supervisor_*.py`, and the two agent-memory files. No `.github/`, `services/`, `apps/`, `packages/`, `render.yaml`, `project-control/`, or other `tools/` file changed.
- **Owner gates:** no merge, acceptance, hold release, deploy, G6, credential, or payment action taken or automated. `limited-auto` remains unimplemented and unreachable; `start --mode limited-auto` still refuses by name (test).

## 5. Limitations, assumptions, blockers

- **No §18 stop condition fired.** No directive conflict discovered, no allowed-path expansion needed, no confinement regression.
- **Control-response wrapper is UNVERIFIED against the live CLI** (§2 above). This is the single largest residual risk in Phase 2 and it is surfaced in code, in `doctor`, and in the README rather than buried.
- **`--codex-model` override deliberately absent** until the Phase 3 authenticated path exists.
- I did **not** write `project-control/reports/M0-T036-producer-report.md`; this return is the producer evidence, for you to append verbatim per the report-preservation rule (same as Phase 1).
- Still open from Phase 1 and unchanged: CI (`.github/workflows/ci.yml`) does not invoke the supervisor test files; wiring the four **new** files plus the four old ones needs a `.github/**` edit, a forbidden path for this packet.
- No ledger command, `git commit`/`push`, or `gh` was run. No credentials, no network, no real provider process — every Claude and Codex in these tests is a local fake script.
- **Assumption to confirm at G3:** that deriving `policy.BYPASS_FLAG_MARKERS` from `process.HARD_DENY_ARGUMENTS` (rather than duplicating the literals) is the preferred reading of AS-7's "except as HARD-DENY list constants".

**Measurement note (D-006):** scope was Phase 2 of 5 (policy + adapters), built on Phase 1 in an isolated worktree. `/usage` is unobservable from inside a spawn, so I cannot report consumption; no token, time, or efficiency claim is made.

**Model disclosure (Phase 2):** spawned explicitly as **Opus 5** (`claude-opus-5[1m]`), the R298 producer ceiling. No effort setting applied anywhere.

---

# PHASE 3 CHECKPOINT (appended by the orchestrator; Phases 1–2 content above byte-preserved)

**Orchestrator header (NOT part of the producer's return).** Third unnamed `backend-engineer`
producer, spawned explicit Opus 5, worktree-isolated, dispatched 2026-08-03 for Phase 3
(endurance). Preserved verbatim below — **no R024 redaction required** (the producer wrote with
`<TEMP>`/`<USERHOME>` placeholders itself). The producer's §0 tip-SHA discrepancy note is
resolved: `6f4208f6` in the dispatch was the orchestrator's transcription typo for `6f4208f2` —
one branch tip, no divergence. Its disclosed single live probe (one bounded run closing the
Phase 2 control-response residual with a VERIFIED result) was within the packet's authorization.
Port: 21 files verified against declared full LF SHA-256 digests (21/21) and all 17
claimed-unchanged Phase 1/2 modules verified byte-identical; orchestrator re-ran all thirteen
suites on the ported tree (result recorded in the integration commit). Port hashes:
`M0-T036-phase1-port-hashes.json` (phase3 block).

---

## M0-T036 — PHASE 3 PRODUCER CHECKPOINT

Requested status: **awaiting_gate**

### 0. Worktree state note (read first)

HEAD was `e7f5078b2c3668c255fe65bc22afde576f65c75e` (the merge-base) with no `tools/agent_supervisor/` present — the Phase 2 precedent condition. I ran exactly the prescribed command, `git merge --ff-only task/M0-T036-supervisor-bridge`, which fast-forwarded `worktree-agent-a50dd215f93da92e1` to the Phase 2 tip. **No commit, no push, no `gh`, no `project_control.py`.**

**One discrepancy to record:** the packet named the tip `6f4208f6`; the actual branch tip is **`6f4208f28f64d418280451b1e67b015e1e71c834`** — the last hex digit of the short form differs (`…f2` not `…f6`). It is a descendant of `d1f0f74` on `task/M0-T036-supervisor-bridge` with Phase 2 state present, so the packet's alternative condition is satisfied. I proceeded; flagging it as a transcription difference, not a divergent branch.

Branch: `worktree-agent-a50dd215f93da92e1` · base `6f4208f2` + the uncommitted Phase 3 work below.

### 1. Files created (15) and modified (6), with full LF-normalized SHA-256

**Created**
```
f2223595afbd12946d3b3c461be4344b1ae577cd142d68900d099be47f20a92e  tools/agent_supervisor/rotation.py
3974c29da9a05961cb6580ea8b0fd7a399b7250bca7aec4be12981e9926e01ff  tools/agent_supervisor/resume_scheduler.py
851c8f2694e8f25107572cc929f85f737aff266f2831823e45169563c0ebf960  tools/agent_supervisor/recovery.py
8f69e396db18dfafaf808362745a87e8693b2375bb2d078eb1ff2388217e451f  tools/agent_supervisor/locking.py
a4f2ee79a11939b3ac469482f239484c57e9d60bd172b875c60351196abbc0d9  tools/agent_supervisor/notifications.py
a3cb9298d763f51a535bd95e3ab7ff9033ea2d61f61ec4202d3646bc503c74f1  tools/agent_supervisor/remote_approvals.py
cf2d747bfe1861c4397b610f7e27810a142156039bbf71015509244c94c42ca0  tools/agent_supervisor/model_change_ipc.py
fdce7c494af9d9e6b0591769d54cc721695eb42cb5d71a28e0ce1be5c287d7e5  tools/agent_supervisor/retention.py
2a7fd7a93bbaf57cddabc0c8877f2fc64392c0eeb8ab822706c5cda6ddc75c70  tools/agent_supervisor/anchor.py
9e5a9f69e01284410da5e24b5b99d05470b6011b6dff15259d2323de0f5a13c0  tools/agent_supervisor/preflight.py
e70e43551ff7ebf4b49177f0baed57e3bb07c5756e412e8df1a74fed8c36f070  tools/test_agent_supervisor_rotation.py
3198d3cfab575f3cd6957e5f83f50043a71702de7ad4cb6010294cf3fc6362da  tools/test_agent_supervisor_scheduler.py
6bccc3270ddc7ac5ad3f67666faced9aa52ea8a7d9b38d6d13d145413b1c4785  tools/test_agent_supervisor_recovery.py
4736f2c2610b346b1a0ce37a8e88b8b7e04f22a12aad5b93e16cdd4f3361b4cf  tools/test_agent_supervisor_ipc.py
7c8eac450ba252268ab2e1b4a73d209b4f6970b839c4de960ad27d437cbce508  tools/test_agent_supervisor_endurance.py
```
**Modified**
```
b42fec4f9cd3c44e96bef61355dedd790673023c649eb7a2ba36cb3a84312f35  tools/agent_supervisor/__init__.py
e1852ffd92428531a6f6fd02c3cf15ab5efab0148d0b002e6ec3905d810d195a  tools/agent_supervisor/cli.py
571afacfe4565c572618e0cc70cbb6ef5105417391792ba63d93e31af286297f  tools/agent_supervisor/README.md
bc7440db4cd06e52b7d8716500f0434e74720e243579520321ff9eac79f6ca69  tools/agent_supervisor/config.example.toml
5d152626312f5f099b831f746528ba73f67689af52662154226f042b40789b90  tools/test_agent_supervisor_phase1.py
f353701f6a4831a20540c48876f75836fe7640f7348362c7af865168b6c68571  tools/test_agent_supervisor_reviewer.py
```
(21 files, 588,476 LF-normalized bytes.)

**Per-modification justification**

1. **`__init__.py`** — `CONTROLLER_VERSION` `0.2.0-phase2`→`0.3.0-phase3`, `PHASE` 2→3. The version is embedded in the manifest, every audit record, and the journal; a Phase 3 build reporting "phase2" is a false provenance claim. Docstring lists the ten new modules and restates what is still *not* built.
2. **`cli.py`** — the Phase 3 interface. Implements 13 previously-deferred S12.1 commands, adds 10 Phase 3 `doctor` checks plus `--live`, and retargets `start` from "refuses" to "runs the pre-dispatch sequence and stops".
3. **`README.md`** — owner-facing status said "Phases 1 and 2 exist"; leaving it would misdescribe the package. Rewritten for Phase 3, caveats updated (3→4), and the D-007 §12.1 non-technical owner guide added, which no earlier phase had.
4. **`config.example.toml`** — added `[rotation]` (the §11.1 thresholds incl. the three suggested defaults) and `[retention]` (per-class §13.11 limits). `config.py` was **not** modified: both land in `ControllerConfig.raw` and are parsed by `RotationThresholds.from_controller_config` / `RetentionPolicy.from_controller_config` with their own strict unknown-key refusal.
5. **`tests/…_phase1.py`** — one test asserted `pause`/`emergency-stop`/`start`/`export-handoff`/`recovery-status` still raise `NotImplementedError`. Phase 3 implements them. Narrowed to `replay` and strengthened with `assertEqual(set(DEFERRED_COMMANDS), {"replay"})` so a future deferral cannot slip past.
6. **`tests/…_reviewer.py`** — one test asserted `--codex-model` was *deferred*. Phase 3 builds the path, so the assertion inverts: it now pins that the commands are live, that the override delegates to `request_change` (i.e. no weaker bypass appeared), and that the reviewer adapter still exposes no override of its own.

**Verified unchanged:** `git diff --stat` over the other 17 Phase 1/2 modules plus `schemas/` and `prompts/` is empty — all byte-identical.

### 2. Per-module notes and honest deferrals

- **`rotation.py`** — §11.1 classification is a deterministic `max()` over per-feature verdicts, so an unrecognizable shape lands in `UNKNOWN`, never optimistically `SMALL`. §11.2's `MidUnitOutcome` **has no `terminate` field at all** — the type cannot express killing a unit for pressure — and `may_interrupt_in_flight` *raises* on any pressure reason rather than returning False. `decide_pre_dispatch` refuses to run unless `at_safe_checkpoint=True`, so "rotate now" is unreachable mid-unit by construction. Handoff verification refuses the advisory role, the advisory model, and any model that is not the configured `review_model`.
  - **Real bug its own test caught:** with usage *and* context pressure both unreadable, I set the job size to `UNKNOWN` but never engaged the large-job bound, so the decision fell through to "no rotation required" **on no evidence whatsoever** — the exact opposite of §11.1's "choose the conservative pre-dispatch action". Fixed with a comment naming the test.
- **`resume_scheduler.py`** — six distinct limit classes; structured metadata strictly preferred. **Honest deferral:** the structured key names are DOCUMENTED CANDIDATES, not verified — the Phase 1 probe saw a `rate_limit_event` but did not capture its payload keys. `StructuredKeys.verified_against_installed_cli` is `False` and a test pins that. The notice parser recognizes only four enumerated forms and is version-stamped.
  - **Two real bugs its own tests caught:** (a) `resets 3:30 pm` matched *both* the 12- and 24-hour patterns, so the more-than-one-form guard rejected a perfectly documented notice; fixed with a negative lookahead. (b) My DST check tested the fold offsets before the round trip — under PEP 495 both differ in a gap *and* an overlap, so **every spring-forward gap was misreported as a fall-back overlap**. Reordered, with the reason in a comment.
- **`recovery.py`** — a **missing** revalidation step is a failed step (tested for all 12). A child whose liveness cannot be *determined* counts as unaccounted, not as "probably gone". Drift dominates ambiguity. A restored deadline overrides an otherwise-safe resume. Contains no `subprocess`/`socket`/`urllib` import — asserted structurally.
- **`locking.py`** — Windows liveness uses `OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION)` + `GetExitCodeProcess`, **never `os.kill(pid, 0)`**: CPython implements `os.kill` on Windows with `TerminateProcess`, so the POSIX idiom would kill the process it was probing. `ERROR_ACCESS_DENIED` is a determined *positive* (another account's process exists) and is never stolen. Pid reuse is caught via the creation-time token. Undeterminable liveness fails closed.
- **`notifications.py`** — a fixed field set with no attachment slot, so a transcript cannot be smuggled through. Raw commands, auth links, source excerpts, and private user paths are **refused with a named reason**, not silently stripped.
- **`remote_approvals.py`** — every failure mode has its own reason code (`nonce_replayed`, `expired_nonce`, `wrong_digest`, `wrong_owner`, `repository_state_changed`, `unbound_answer`). An expired binding is *consumed* so it cannot be retried. No network I/O.
- **`model_change_ipc.py`** — origin denial walks **real** process ancestry (Toolhelp32 / `/proc`), so a descendant of a worker is denied, not just the leaf. The confirmation challenge is derived from the change digest, so a captured "yes" cannot be replayed against a different change.
  - **Proven, not asserted:** a named pipe with an SDDL DACL restricted to the owner SID + SYSTEM is **created and closed on this host** via stdlib `ctypes` (`doctor` runs it). **Deferred:** the long-lived unattended pipe *server* loop. The transport in use is a controller-owned runtime directory whose isolation from every worker-writable root is re-checked per request. Account SIDs are masked everywhere they surface.
- **`retention.py`** — deletion requires identity proven **three ways** (inside the runtime dir, inside its class directory, in the supervisor's own inventory) *and* provable age; a plan is built read-only and **re-proved at execution**, so a forged plan entry deletes nothing (tested). The drill really destroys the source before restoring.
- **`anchor.py`** — **mechanism only.** No `subprocess`, no call site; `EXECUTION_SURFACE_NAMES` is the sole place those words appear (the AS-7 constants exception), and a test pins `source.count("Popen") == 1`. `main`/`master`/`HEAD` are refused as anchor targets. Publication requires **both** controller credentials and an explicit owner activation; `activation_status()` names which is missing.
- **`preflight.py`** — the round-trip probe is opt-in, bounded, and works in a throwaway directory. It counts as verified only if the CLI accepts our bytes, denies the tool, **and** echoes our deny message; a protocol error, a hang, or a tool that runs anyway all read as not verified.

**Still not built and not pretended:** the assembled supervisor **loop**, the replay engine and historical corpus, push **execution**, anchor **publication**, the named-pipe **server** loop, and Job-Objects-as-default (which I did **not** advance — it moves from "Phase 3" to Phase 4 and the README says so rather than quietly claiming it).

### 3. The Phase 2 residual — CLOSED, with exact disclosure

I ran the live probe **exactly once**, as the packet permits.

```
python -m tools.agent_supervisor doctor --live --json --runtime-base <TEMP>/rt_live
EXIT=0   OVERALL_OK=True
```
```
control_response_live_probe:
"VERIFIED (live run): the installed CLI accepted the exact control_response bytes
 this build emits, denied the tool, and echoed our deny message back in
 permission_denials. The wrapper shape is confirmed against the live CLI."
```
One bounded turn (`--max-turns 1`), one denied Write, throwaway directory, nothing written in the repository. Executable: `<USERHOME>\.local\bin\claude.exe` (the Phase 1 canonical binary).

**Two honest caveats on this result.** (a) I kept `CONTROL_RESPONSE_WRAPPER_VERIFIED = False` as a module constant, because verification is host- and binary-specific; I wired the result to persist per checkout instead. (b) **That persistence wiring landed *after* my one run**, so no probe record exists in any journal and `doctor` still reports `UNVERIFIED` — correctly, since it has no record. I did not re-run to populate it, and I did not fabricate a record. The recorded-probe branch is covered by a seeded unit test that makes no live call.

### 4. Test output

**All thirteen suites together**
```
python -m unittest tools.test_agent_supervisor_phase1 tools.test_agent_supervisor_protocol \
  tools.test_agent_supervisor_audit tools.test_agent_supervisor_process \
  tools.test_agent_supervisor_policy tools.test_agent_supervisor_broker \
  tools.test_agent_supervisor_runner tools.test_agent_supervisor_reviewer \
  tools.test_agent_supervisor_rotation tools.test_agent_supervisor_scheduler \
  tools.test_agent_supervisor_recovery tools.test_agent_supervisor_ipc \
  tools.test_agent_supervisor_endurance
Ran 735 tests in 71.297s
OK (skipped=2)
```
**Standalone, as CI invokes control-plane tests** (all exit 0)
```
phase1 68 OK   protocol 29 OK   audit 15 OK   process 27 OK (skipped=1)
policy 98 OK (skipped=1)   broker 50 OK   runner 41 OK   reviewer 55 OK
rotation 67 OK   scheduler 96 OK   recovery 55 OK   ipc 42 OK   endurance 92 OK
```
Phase 1+2 = **383, unchanged, no regression**. Phase 3 adds **352 new tests**. The 2 skips are the pre-existing POSIX-only guard and the symlink-privilege guard.

**Repository regressions (all green):** `test_project_control.py` → "all 22 project-control test groups passed"; `test_directive_compliance.py` → "Ran 102 tests … OK"; `test_agent_dispatch_guard.py` → "ALL CHECKS PASSED".

**Live `doctor`: 30 checks, all PASS, exit 0**, `controller 0.3.0-phase3 (phase 3)`, and PASS again against `config.example.toml` with the new `[rotation]`/`[retention]` sections.

### 5. Self-checks

- **No effort key:** **zero** occurrences of `effort` in any of the 15 new files. The only literals in the package remain the Phase 1/2 deny-list constants and refusal tests.
- **argv-only:** `grep -rn "shell=True"` → two **prose** hits (a `process.py` docstring, a README line); zero code occurrences. The one `Popen` I added (`preflight.py`) passes an argv array with `shell=False` explicit, built by the shipped adapter.
- **Bypass flags:** no new literal anywhere. `grep -- "--dangerously\|--yolo\|--bypass"` returns only `process.py:52-56` (the deny list) and two comment/test references to it.
- **Stdlib-only:** 43 files, 33 distinct top-level imports, checked against `sys.stdlib_module_names` → **"NONE - 100% standard library"**. No dependency manifest or lockfile touched.
- **Containment:** `git status --porcelain -uall` shows **only** `tools/agent_supervisor/**` and `tools/test_agent_supervisor_*.py` — 21 entries, nothing else. No `.claude/`, `.github/`, `project-control/`, `services/`, `apps/`, `packages/`, or other `tools/` file.
- **Owner gates:** no merge, acceptance, hold release, deploy, G6, credential, or payment action taken or automated. `limited-auto` remains unimplemented; `start --mode limited-auto` refuses by name (tested). No OS task was created — `install-autostart` refuses without a plan digest, and I never supplied one.
- **Deliberate omission:** I wrote **no** `.claude/agent-memory/` files this session. `.claude/**` is a forbidden path, and both prior phases' memory writes were explicitly *not* ported (D-004-R704). The learnings are preserved in §2 above instead.

### 6. §18 stop-condition statement

**No Section 18 stop condition fired.** Specifically checked and cleared: a safe Windows process-control strategy is proven (§4 caveat unchanged from Phase 1); recovery *does* distinguish a proven safe checkpoint from an ambiguous in-flight effect; startup/wake recovery never blindly reruns an effect; no active unit would need termination for a context/usage threshold; every reset time is parsed and scheduled without guessing or else refuses; the restore drill **passes**; no runtime secret is stored; no bypass permission is required; allowed paths did **not** need to expand; no directive conflict was discovered.

### 7. Limitations, assumptions, blockers

- **Assumption for G3:** that `start` performing the real pre-dispatch sequence and then stopping is the right reading of "be honest about what start can and cannot do", versus keeping it a flat refusal. It classifies `UNSAFE_OR_DRIFTED` today because the six live checks it cannot make read-only are reported `False` — that is deliberate fail-closed behaviour, not a defect.
- **Assumption for G3:** that the POSIX runtime-dir branch and the LF-normalized manifest digests (both Phase 1 deviations) remain acceptable.
- Still open from Phases 1–2: CI does not invoke the supervisor test files. Wiring the five **new** files plus the eight existing ones needs a `.github/**` edit — a forbidden path for this packet, so it needs separate authorization.
- I did **not** write `project-control/reports/M0-T036-producer-report.md`; this return is the producer evidence, for you to append verbatim (same as Phases 1 and 2).
- No ledger command, `git commit`/`push`, or `gh` was run. The single `--ff-only` merge in §0 is the only git state change, and it was the prescribed first act.
- **Network:** exactly one bounded provider call, the disclosed live probe. Every Claude, Codex, and `schtasks` in the test suite is a local fake.

**Measurement note (D-006):** scope was Phase 3 of 5 (endurance), built on Phases 1–2 in an isolated worktree. `/usage` is unobservable from inside a spawn, so I cannot report consumption; no token, time, or efficiency claim is made.

**Model disclosure (Phase 3):** spawned explicitly as **Opus 5** (`claude-opus-5[1m]`), the R298 producer ceiling. No effort setting applied anywhere.

---

# PHASE 4 CHECKPOINT (appended by the orchestrator; Phases 1–3 content above byte-preserved)

**Orchestrator header (NOT part of the producer's return).** Fourth unnamed `backend-engineer`
producer, spawned explicit Opus 5, worktree-isolated, dispatched 2026-08-03 for Phase 4
(validation). Mid-session the producer's API connection dropped; the orchestrator resumed the
same agent with its worktree and context intact, and the producer corrected the orchestrator's
stale mid-edit diagnostic on resume (§0 below) — recorded as relayed. Preserved verbatim below
**except one R024 redaction**: the closing "Key file paths" absolute-path block → `<WORKTREE>`
repository-relative form. Port: 25 files verified against declared full LF SHA-256 digests
(25/25) and all 26 claimed-unchanged modules verified byte-identical; the orchestrator re-ran
all nineteen suites on the ported tree (result in the integration commit — this run also
adjudicates, by execution, the static-analysis flags observed during the build). Port hashes:
`M0-T036-phase1-port-hashes.json` (phase4 block).

---

# M0-T036 — PHASE 4 PRODUCER CHECKPOINT

Requested status: **awaiting_gate**

## 0. Worktree state note (read first)

HEAD was `e7f5078b2c3668c255fe65bc22afde576f65c75e` (the merge-base), no `tools/agent_supervisor/` present — the Phase 2/3 precedent condition. I ran exactly the prescribed command, `git merge --ff-only task/M0-T036-supervisor-bridge`, which fast-forwarded to **`7b179ec625146968148ead3f2419ae1b75918564`** (the Phase 3 tip named in the dispatch). **No commit, no push, no `gh`, no `project_control.py`.**

Branch: `worktree-agent-a25895576c5bd30bd` · base `7b179ec` + the uncommitted Phase 4 work below.

**Mid-session interruption, disclosed.** An API error ("Connection closed mid-response") cut the session after `process.py`/`claude_runner.py` were wired. On resume the coordinator relayed a diagnostic that `claude_runner.py` was mid-edit with an undefined `ProcessContainer` and no `RunnerConfig.use_job_object`. **That diagnostic was stale** — I re-verified live before continuing: `ProcessContainer` imported (True), `use_job_object` default (True), `default_containment_kind()` → `job_object`, and the `process`+`runner` suites green at 68 tests. Nothing was lost or ambiguous; I state this rather than let a false "recovered from corruption" narrative stand.

## 1. Files created (17) and modified (8), with full LF-normalized SHA-256

**CREATED (17)**
```
a7b52be10d2ff8f7a601807887b82001dbb17173a5ee90f14f1a7d82fb30b820  tools/agent_supervisor/loop.py
d75fb697e1aeaa42a5e14b7a96af9cebd7f8568d4e00023c92ee9d8eb2b2a5af  tools/agent_supervisor/replay.py
24bd6db5929c1d6778d768bdecd222e7321425ea6a3e39e087dec7f773a7f835  tools/agent_supervisor/replay_corpus/manifest.json
500370f5df16a1c2e5591281339b29e8c5c94fda8e6dd14723781ce338db9b41  tools/agent_supervisor/replay_corpus/b015_sentinel_failure.json
72c7b9bf92cb810d41e096fc54fc0e5e8735e0947d7ba44240ebacb6ff70b7d8  tools/agent_supervisor/replay_corpus/ci_failure.json
43f2741e08a5ccc7ae5755161c94dece069d26c20aa33527b799755adbf1bf7e  tools/agent_supervisor/replay_corpus/clean_continuation.json
8909df6311c808ae4697e810bdb2d845e79dc864daa03cdc69d97aa3ef68ebec  tools/agent_supervisor/replay_corpus/m0_t028_detection_only_stop.json
84da7ec5f882de85a0046ccdb2eae1329bce13f927380dfd9151bd450bb498d0  tools/agent_supervisor/replay_corpus/m0_t031_accepted_lifecycle.json
b957a3151c78b5280cecd32134568cdf60d6c3a3f9fc431c0d75f93aab1110f4  tools/agent_supervisor/replay_corpus/owner_gated_stop.json
d790217d5cdf1628bb74a5a1f5239b87f9fdc3271df2c29a9648a55ac831b826  tools/agent_supervisor/replay_corpus/review_required_correction.json
d040e6e646fb8e4fb9f316bd08b135adbd9e056fbdb07802eb732a54a819ecc6  tools/agent_supervisor/replay_corpus/stale_sha_mismatched_review.json
97c70056683ca1c5138b170ed1c19083725eabc9d750791a481efe20bd7bb6fb  tools/test_agent_supervisor_loop.py
716fb75028b2291e3df5a3ac7dca449c317c6b7c81bacd74ab12fa54b7d5b7b0  tools/test_agent_supervisor_replay.py
697a7beab03bd81da853875285f55aa43ada350a7dfb72a7ef14769a5330073f  tools/test_agent_supervisor_invariants.py
e6a5df80956d46092b0959941af1c75db41021dad02593134fdb2ee2079dcde0  tools/test_agent_supervisor_adversarial.py
6eb5fd093c766ac88179a8a5d7a86f94f6cedeeb32063dec8b27008bffead24c  tools/test_agent_supervisor_crash.py
a8e833a564a1327ab4e14c470b3d6bb8a89a41a1834734bf64a89a3180b3b0b5  tools/test_agent_supervisor_fuzz.py
```
**MODIFIED (8)**
```
c2cf228d45d8e6e8e10688ad3b46bfa4d93d0881f03c527dfbe47edd46d77ca1  tools/agent_supervisor/__init__.py
ba9f396a3ec5e69076cd6febb0c6902c27b83586db15648e7c62e11402a684a5  tools/agent_supervisor/cli.py
efbccc1d546e2cba2a44148e3c9726b289227833f5ef31b166c96a2eadac5cc1  tools/agent_supervisor/policy.py
8664bc79d9e9796a4e6f4e3d7a755f2a4c5e6461383f00decedc51bb18978a4a  tools/agent_supervisor/process.py
5018373047d1e14072e31c49c5bb0c483ebed6ea177e3ddd94739300723cbdab  tools/agent_supervisor/claude_runner.py
83e480988effe33b1d8f7ff7afa50f7cdc575fc7fbaf0fdaff5f56abf59a1bd8  tools/agent_supervisor/README.md
fd0e16f77744c2e60b33af1fad1c6ee58099defbc13e91dbf5d5eb961f1156d5  tools/test_agent_supervisor_phase1.py
0cf0c944ce92b699874d65416b26422298f2339036d9c213013825e7bdb56d79  tools/test_agent_supervisor_endurance.py
```
(25 files, 672,654 LF-normalized bytes.)

**Per-modification justification**

1. **`__init__.py`** — `CONTROLLER_VERSION` `0.3.0-phase3`→`0.4.0-phase4`, `PHASE` 3→4. The version is embedded in the manifest, every audit record, and the journal; a Phase 4 build reporting "phase3" is a false provenance claim. Docstring lists `loop.py`/`replay.py` and restates what is still *not* built.
2. **`cli.py`** — the Phase 4 interface. Implements `replay`; makes `start` really dispatch; adds 6 Phase 4 `doctor` checks; empties `DEFERRED_COMMANDS`.
3. **`policy.py`** — two additions, both strengthening: the S13.2 **trust-zone** rule (invariant 10 was previously inexpressible because a `ProposedAction` carried no origin) and the **device-name path fix** (§3, defect 1). `origin_zone` defaults to `WORKER`, so every pre-existing call site classifies exactly as before — the 98 Phase 2 policy tests pass unchanged.
4. **`process.py`** — `ProcessContainer` makes the Job Object the default container (the carried deferral), with breakaway refusal, nested-job detection, `IsProcessInJob` verification, and a *recorded* taskkill fallback. `run()` gained `container`/`use_job_object`; `ProcessResult` gained `containment`/`containment_fallback_reason`.
5. **`claude_runner.py`** — the worker now launches inside the container. `RunnerConfig.use_job_object` (default True) makes any downgrade explicit and recorded; `RunResult` reports the containment achieved.
6. **`README.md`** — owner-facing status said "Phase 3 … the loop is Phase 4". Leaving it would misdescribe the package. Rewritten for Phase 4; caveat 2 (Job Objects) **closed**; a new section documents the fuzzer-found defect.
7. **`tests/…_phase1.py`** — one test asserted `DEFERRED_COMMANDS == {"replay"}`. It **inverts**: it now pins that the map is *empty* and that `cmd_deferred` still refuses, so a future phase cannot wire a command to a silent no-op.
8. **`tests/…_endurance.py`** — same inversion, plus `test_replay_still_refuses` → `test_replay_is_live_and_makes_no_model_call`, which asserts the properties that matter now (exit 0, 0 provider calls, 0 project-control writes).

**Verified unchanged:** `git diff --stat` over the other 24 Phase 1–3 modules plus `schemas/`, `prompts/`, `config.example.toml`, and `__main__.py` is **empty** — all byte-identical.

## 2. Per-module notes and honest deferrals

- **`loop.py`** — the cycle is real transitions on the S7 table, so the journal is the truth about where a run got to. **Shadow forwards nothing structurally**: it never touches the outbox at all (an outbox row is a commitment to send), never enters `FORWARD_PROMPT`, and `assert_forwarding_allowed()` raises if any caller tries. **Supervised** holds every prompt at `WAIT_FOR_OWNER` and denies when no approval gate is reachable — an unanswerable approval never becomes an implicit yes. Exactly-once forwarding journals before sending; a duplicate is *suppressed*, a crash between enqueue and send *resumes the same message*. The owner-touch ledger counts **only** would-be synchronous stops and blocking ASKs; supervised approvals are recorded `counted=False` because they are a property of the debugging mode, not of the target operating mode — counting them would make the S16.7 budget measure the wrong thing. A source-level test proves the module names no grant constructor, no `TIER_ORDER`, and binds `authority`/`policy_config`/`config` exactly once each.
- **`replay.py`** — three properties proven from the module source, not promised: `assert_no_execution()` (no process, no adapter), `assert_no_writes()` (no filesystem write at all), and `assert_never_writes()` for any path under `project-control/`, `.github/`, `.claude/`. A test additionally runs the whole corpus against a **chmod'd read-only** copy, and another reads every cited ledger record before and after a full run and asserts byte-identity. `matched` was deliberately separated from provenance: pointing the engine at a scratch directory is not a reproduction failure, so the two signals are reported apart (`doctor`, which uses the real checkout, fails on missing provenance).
- **`replay_corpus/`** — eight fixtures derived by **quoting and summarizing** committed records. No project-control file was modified to build them. Each carries `provenance` (verified present in this checkout), `recorded_ledger_outcome`, and a `notes` field explaining what the case is guarding. `manifest.json` records per-file digests; `check_manifest()` fails closed on drift, and `doctor` runs it.
- **`process.py` / Job Objects** — **the carried deferral is closed.** Proven on this host with a real child: create → configure kill-on-close → assign → ask the *kernel* (`IsProcessInJob`) → close → child dies. Breakaway is refused rather than offered (`JOB_OBJECT_LIMIT_BREAKAWAY_OK`, `..._SILENT_BREAKAWAY_OK`, `CREATE_BREAKAWAY_FROM_JOB`) because a containment mechanism must not opt into its own bypass. Nested-job refusal (`ERROR_ACCESS_DENIED`) degrades to taskkill and **records the reason**; taskkill is genuinely weaker (a grandchild can escape enumeration) so nothing claims job-strength containment it did not get.

**Still not built and not pretended:** push **execution**, anchor **publication**, the named-pipe **server** loop, and the Phase 5 shadow pilot. `limited-auto` is not implemented in any form.

## 3. Defects found and fixed (four; none weakens a stop or a hard deny)

1. **`resolve_target` crashed on Windows reserved device names.** *Found by the path-normalization fuzzer, input `.env;/nul`.* `os.path.realpath` maps a trailing `nul` to `\\.\nul` and `os.path.relpath` then raises `ValueError` — so the classifier raised instead of denying. An unhandled exception mid-decision is fail-open, not a denial. **Fix:** refuse all reserved device names (`nul`, `con`, `aux`, `prn`, `com1–9`, `lpt1–9`) before resolution, return the existing `device_path` reason, and guard `realpath`/`relpath`. Enforced on every platform so Linux CI enforces what Windows does. Regression tests cover both the denial and that `console.py`/`nullable.py`/`connection.py` are unaffected. **Adds a denial; removes none.**
2. **`start` could never dispatch.** *Found by running it.* I gated dispatch on `outcome.resume_permitted`, which answers "may this resume **automatically**, unattended" — it is `False` on a perfectly healthy checkout precisely because limited-auto is off, and its own reason text says recovery "waits for an explicit operator start". **Fix:** gate on `classification == SAFE_CHECKPOINT`. `AMBIGUOUS_EFFECT` and `UNSAFE_OR_DRIFTED` still stop.
3. **Two missing CLI imports** (`StateMachine`, `ClaudeRunner`, `CodexReviewer`) and a **missing `IDLE→PREFLIGHT` transition** — `start` *is* the S7 `start_command` trigger, and the loop's first cycle begins at `PREFLIGHT`. **Fix:** import them; apply the transition explicitly and record it. Also hardened: `run_cycle` now refuses a bad entry state by name (`CYCLE_ENTRY_STATES`) rather than blundering into an illegal transition.
4. **The digest-bound supervised approval could never match.** *Found by running `start --mode supervised` end to end — twice, for two independent reasons.* The approval bound to the **rendered** prompt, which carries a `FORWARDED AT:` timestamp and an evidence-packet reference whose own digest moves with the clock and live git state. A digest-bound approval that can never match is not a gate, it is a dead end. Scrubbing volatile lines fixed one cause and not the other, and would break again on the third. **Fix:** `approval_digest()` over the **instruction fields** — the exact five things §9 says every forwarded prompt carries, plus task and stage. Changing any of them invalidates the approval (§13.5); changing only the clock does not. The exact-bytes digest is still recorded separately for provenance, and the outbox message id keys on the instruction so a crash-and-re-render resumes rather than duplicating.

**A note on how 4 was found:** every unit test passed throughout, because each computed both sides of the comparison inside one process. A value that must survive a restart cannot be validated that way — only the end-to-end run caught it. That is the generalizable lesson from this phase.

## 4. Test output

**All nineteen suites together**
```
python -m unittest tools.test_agent_supervisor_phase1 ... tools.test_agent_supervisor_fuzz
Ran 1042 tests in 79.015s
OK (skipped=2)
```
**Standalone, as CI invokes control-plane tests** (all exit 0)
```
phase1       Ran 69 tests   OK            policy       Ran 98 tests   OK (skipped=1)
protocol     Ran 29 tests   OK            broker       Ran 50 tests   OK
audit        Ran 15 tests   OK            runner       Ran 41 tests   OK
process      Ran 27 tests   OK (skip=1)   reviewer     Ran 55 tests   OK
rotation     Ran 67 tests   OK            scheduler    Ran 96 tests   OK
recovery     Ran 55 tests   OK            ipc          Ran 42 tests   OK
endurance    Ran 92 tests   OK            loop         Ran 58 tests   OK   [P4]
replay       Ran 38 tests   OK   [P4]     invariants   Ran 45 tests   OK   [P4]
adversarial  Ran 93 tests   OK   [P4]     crash        Ran 32 tests   OK   [P4]
fuzz         Ran 40 tests   OK   [P4]

TOTAL standalone: 1042 across 19 suites; suites not OK: 0
```
Phases 1–3 = **735 → 736**, no regression (the +1 is the split of the inverted deferral test). Phase 4 adds **306 new tests**. The 2 skips are the pre-existing POSIX-only guard and the symlink-privilege guard.

**Repository regressions (all green):** `test_project_control.py` → "all 22 project-control test groups passed"; `test_directive_compliance.py` → "Ran 102 tests … OK"; `test_agent_dispatch_guard.py` → "ALL CHECKS PASSED".

**Live `doctor`: 36 checks, all PASS, exit 0**, `controller 0.4.0-phase4 (phase 4)`, including the six new ones: `replay_corpus`, `replay_inert`, `loop_modes`, `containment_default` (`job_object` on this host), `trust_zones`, `deferred_commands`.

**Live `replay`, whole corpus**
```
python -m tools.agent_supervisor replay --repo .
8/8 cases reproduce their recorded behaviour.
provider calls: 0 | project-control writes: 0 | manifest ok: True | provenance ok: True
corpus digest: 768eea1ec6bb9e839fc0ecc10344b953b5ecbf5ed90db5e579fd71fcf04a6843
```
| case | outcome | tier |
|---|---|---|
| `clean_continuation` | continue | AUTO |
| `review_required_correction` | revise | AUTO |
| `ci_failure` | revise | AUTO |
| `stale_sha_mismatched_review` | stop_for_owner | ASK |
| `owner_gated_stop` | stop_for_owner | HARD_DENY |
| `m0_t031_accepted_lifecycle` | stage_complete | ASK |
| `b015_sentinel_failure` | **halt** | **HARD_DENY** |
| `m0_t028_detection_only_stop` | stop_for_owner | ASK |

**Live `start` against FAKE executables** (both modes really dispatch; no provider, no network):
```
start --mode shadow      dispatched=True  final=POLICY_CHECK   forwarded=[]  touches counted=0/2
  cycle 1: START_CLAUDE -> CLAUDE_RUNNING -> CHECKPOINT_RECEIVED -> COLLECT_EVIDENCE
           -> CODEX_REVIEW -> VALIDATE_DECISION -> POLICY_CHECK
           WOULD have forwarded -> FORWARD_PROMPT, digest c16e8214...   (forwarded nothing)

start --mode supervised  dispatched=True  final=WAIT_FOR_OWNER stopped=operator_declined  forwarded=[]

start --mode supervised --approve-prompt-digest c16e8214f3a884d4...
                         dispatched=True  final=CLAUDE_RUNNING  forwarded=True
  path: ... -> POLICY_CHECK -> WAIT_FOR_OWNER -> FORWARD_PROMPT -> CLAUDE_RUNNING
  forwarded message ids: ['run-e2e-supervised/fwd/1/c16e8214f3a884d4']
```

## 5. Self-checks

- **No effort key:** **zero** occurrences of `effort` in any of the 17 new files (measured per-file). The only literals in the package remain the Phase 1/2 deny-list constants and refusal tests.
- **argv-only:** `grep -rn "shell=True"` → two **prose** hits (a `process.py` docstring, a README line); **zero code occurrences**. Every launch site passes an argv array with `shell=False` explicit.
- **Bypass flags:** no new literal. `grep -- "--dangerously|--yolo|--allow-dangerously"` returns only `process.py:71-75` (the deny list), the `policy.py` injection regex + its explanatory comment, and one Phase 2 test comment. Phase 4 files build hostile inputs *from* the constants.
- **Stdlib-only:** 51 files, 37 distinct top-level imports, checked against `sys.stdlib_module_names` → **"NONE - 100% standard library"**. No dependency manifest or lockfile touched.
- **Containment:** `git status --porcelain -uall` shows **exactly 25 entries, all under `tools/agent_supervisor/**` and `tools/test_agent_supervisor_*.py`**. Explicit grep for `.claude/`, `.github/`, `services/`, `apps/`, `packages/`, `project-control/`, `render.yaml` → **NONE**.
- **Owner gates:** no merge, acceptance, hold release, deploy, G6, credential, or payment action taken or automated. `limited-auto` remains unimplemented; refused by name in `LoopConfig`, in `cmd_start`, and by `doctor`.
- **Deliberate omission (disclosed):** I initially wrote an agent-memory file capturing the defect-4 lesson, then **reverted it** — `.claude/**` is a forbidden path for this packet and Phase 3 set that precedent. The learning is preserved in §3 above instead, for the path owner to add post-task.

## 6. §18 stop-condition statement

**No Section 18 stop condition fired.** Specifically checked and cleared: a safe Windows process-control strategy is now *proven as the default*, not merely available; the cross-CLI protocol is versioned, integrity-bound, and fuzz-tested; every external action is idempotent or reconciled (crash-injected before and after each boundary); the never-send rules are enforced and seeded-secret-tested; circuit breakers are enforced and injected-failure-tested; recovery distinguishes a proven safe checkpoint from an ambiguous in-flight effect; startup/wake recovery never blindly reruns an effect; no active unit needs termination for a context/usage threshold; the restore drill **passes**; no runtime secret is stored; **no bypass permission is required**; **allowed paths did not need to expand**; no directive conflict was discovered.

## 7. Limitations, assumptions, blockers

- **Assumption for G3:** that binding the supervised approval to the **instruction fields** rather than the rendered prompt bytes is the correct reading of §13.5 ("bind every approval to a digest of: tool name and full input…"). My reasoning is in §3 defect 4 and in a code comment; the alternative (scrubbing volatile lines from rendered text) is strictly more fragile. **Flagging this as the single most reviewable judgement call in Phase 4.**
- **Assumption for G3:** that adding `origin_zone` to `ProposedAction` (default `WORKER`) is the right way to make invariant 10 expressible, rather than a separate reviewer-specific evaluator.
- **Assumption for G3:** that the `owner_gated_stop` fixture correctly expects `HARD_DENY`/`protected_path_mutation` rather than `owner_gate:policy_exception` — the S4.4 hard-deny runs *before* the owner-gate branch, which is the stricter and earlier answer. The owner-gate ASK path is exercised by the two other fixtures where the target is inside `allowed_paths`. My first expectation here was wrong and I corrected the fixture, not the engine.
- Still open from Phases 1–3: **CI does not invoke the supervisor test files.** Wiring the six new files plus the thirteen existing ones needs a `.github/**` edit — a forbidden path for this packet, so it needs separate authorization. This is now 19 suites / 1042 tests running only locally.
- The **control-response wrapper** remains `UNVERIFIED` in `doctor` on a fresh runtime, correctly — Phase 3's one live probe predated the persistence wiring and I did not re-run it or fabricate a record.
- I did **not** write `project-control/reports/M0-T036-producer-report.md`; this return is the producer evidence, for you to append verbatim (same as Phases 1–3).
- No ledger command, `git commit`/`push`, or `gh` was run. The single `--ff-only` merge in §0 is the only git state change, and it was the prescribed first act.
- **Network: none.** Zero provider calls this phase. Every Claude, Codex, and `schtasks` in the tests and in the end-to-end `start` runs is a local fake script.

**Measurement note (D-006):** scope was Phase 4 of 5 (validation), built on Phases 1–3 in an isolated worktree. `/usage` is unobservable from inside a spawn, so I cannot report consumption; no token, time, or efficiency claim is made.

**Model disclosure (Phase 4):** spawned explicitly as **Opus 5** (`claude-opus-5[1m]`), the R298 producer ceiling. No effort setting applied anywhere.

---

**Key file paths (repository-relative; redacted from absolute form at preservation per R024):** `<WORKTREE>/tools/agent_supervisor/{loop.py, replay.py, replay_corpus/, policy.py, process.py, cli.py, README.md}` and `<WORKTREE>/tools/test_agent_supervisor_{loop,replay,invariants,adversarial,crash,fuzz}.py`
