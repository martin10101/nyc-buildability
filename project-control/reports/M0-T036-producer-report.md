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
