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
