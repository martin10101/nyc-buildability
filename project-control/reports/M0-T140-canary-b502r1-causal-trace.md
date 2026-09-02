# M0-T140 — causal trace of the canary-b5-02r1 settlement failure (read-only, 2026-09-02)

Produced under the owner's mid-turn stop-order (D-024 Amendment 45, R684): analysis ONLY,
from durable artifacts — `mrl\canary-b5-02r1\one_shot_unit.json` + `subagent_ledger.json` +
`launch_verification.json`, controller audit records 27–36, the child session transcript
`%USERPROFILE%\.claude\projects\C--Users-MLFLL-Downloads-nyc-zoning-ctl24\7a8f8a17-11b0-4f36-aa25-89bfb41b834d.jsonl`
(+ its `subagents\agent-a18c50fd….jsonl` / `agent-a7a3b2f8….jsonl` sidechains), the launched
`mrl_settings_profile.json`, and `C:\SupervisorController\model_selection.toml`. Returned to
the owner ending `LIVE_FAILURE_CAUSAL_TRACE_READY`; nothing was modified.

## Launch facts

argv: `claude.exe -p --output-format json --max-turns 12 --model claude-opus-4-8
--json-schema <draft-07 WorkerResult> --restricted --permission-mode dontAsk
--tools Bash,Read,Grep,Glob,Agent --strict-mcp-config --settings <run profile>
--agents {Explore: claude-opus-4-8} --allowedTools Read Grep Glob Agent
--disallowedTools mcp__*`. Draft-07 argument carried no 2020-12 string (M0-T141 hotfix
proven live). Exit code 0; wall-clock cap 900 s not reached; `timed_out`/`cancelled`/
`tree_terminated` all false; termination = natural completion (`StructuredOutput` tool call
20:15:45.489Z). stdout/stderr tails not durably persisted by the controller (unit record
omits `result_text`/`stderr_tail`; exit 0); the result substance is durable in the
transcript (final text + `structured_output` attachment).

## Timeline (UTC, launch → settlement)

20:12:46.748 launched (audit 32; budget started 46.004) · 48.4 prompt delivered ·
51.4 assistant(opus-4-8) → **Bash `python --version`** · 52.87 **executed**, stdout
`Python 3.11.9`, no permission event · 57.08 Agent Explore#1 (docs; hook success) ·
13:48.11 Explore#1 completed (19 sidechain turns, all opus-4-8) · 13:51.77 Agent Explore#2
(tools; hook success) · 15:16.57 Explore#2 completed (34 turns, all opus-4-8; 205 KB) ·
15:20.16 Agent Explore#3 (project-control) · 15:20.37 **PreToolUse mrl_subagent_hook
DENIED** "total limit 2 reached (2 issued) (R567)" (tool_result err=True; recorded by the
CLI result as `tool_name: "Task"`) · 15:25 worker acknowledges denial → Glob, Glob ·
15:30.48 **Bash `ls -1 …\project-control`** → **executed**, no permission event ·
15:41.18 final text summary · 15:45.49 `StructuredOutput
{outcome: COMPLETED, summary: 824 ch, requested_next_action: 181 ch}` ("provided
successfully") · 15:45.905 `mrl_one_shot_settled` REFUSED
`contract_violation: runtime reported no model; fail closed` · 15:45.96 S4.5
`unsafe_condition` → `owner_touch no_valid_checkpoint` → PAUSED_RECOVERY.

"180.0 s" = display rounding: budget 20:12:46.004 → close 20:15:45.96 = 179.96 s (`.1f`).

## Model attribution

`modelUsage` = {`claude-opus-4-8`, `claude-haiku-4-5-20251001`, `claude-opus-4-8[1m]`} —
a session-wide billing aggregate. **Every assistant turn — main 15/15, sidechains 34/34 +
19/19 = 68/68 — reports exactly `claude-opus-4-8`** (the pin). haiku = CLI-internal helper
calls (`ai-title` events observed in-transcript). `[1m]` = the 1M-context tier key of the
SAME pinned id (the 205 KB tools-survey sidechain is the plausible long-context source).
`observed_model_from_result` (mrl_exec_chain.py:276) requires EXACTLY ONE `modelUsage` key
→ returned "" → `verify_runtime_identity` failed closed; `inspect_stream` flagged
`model_mismatch=True` on the extra aggregate keys. Primary identity was in fact intact.

## Bash finding

With `permissions.allow=[Read,Grep,Glob,Agent]`, `defaultMode: dontAsk`, Bash in neither
allow nor deny: 2.1.252 EXECUTED two read-only Bash commands with no ask and no denial.
The reviewed assumption "in inventory but not allowed ⇒ dontAsk denial" does not hold.
Artifacts cannot discriminate dontAsk-auto-allow vs safe/read-only auto-approval; only
benign read-only commands were attempted; MCP stayed denied; the subagent cap held;
nothing wrote.

## Adjudicated rows

1/2/5/9 PASS (real) · 3 = Claude auth PASS (session `7a8f8a17…`, 68 live turns) + Codex
NOT_RUN (never invoked; script row = evidence-interpretation fault) · 4 = controller-side
evidence-interpretation fault (aggregate misread; `[1m]` decoration unstripped; primary
correct 68/68) · 6 = REAL enforcement/design drift (Bash executed, never denied) ·
7 = the PRIMARY failure (settlement identity seam; a schema-valid WorkerResult existed and
was never read — extraction runs after the identity check) · 8 = reached AND satisfied on
the merits (ledger issued 2, denied 1 R567, processes_total 3; script row read the wrong
artifact/shape) · 10 not reached.

## Clusters (3) and the one minimal repair boundary

- **A (PRIMARY, controller settlement identity seam):** exactly-one-`modelUsage`-key
  assumption + any-extra-key mismatch flag vs the real 2.1.252 aggregate → every live run
  fails closed at settlement. Caused 7 and 4; cascaded 3-Codex and 10.
- **B (REAL drift, CLI permission surface):** unlisted Bash executes under dontAsk;
  item 6's provocation and the profile's deny posture must be re-based on measured
  semantics (explicit deny, not absence-from-allow).
- **C (evidence interpretation only, external script):** rows 3/8 misread durable
  artifacts. No product defect.

Repair boundary (one): the run-settlement identity seam + the restricted profile's
explicit Bash posture + the script's readout rows. No accepted task reopened; no schema
change; no launch-transport change. Model pin confirmed `claude-opus-4-8` at analysis time
(untouched; the owner's Fable switch is a separate owner-typed act — Amendment 45 R697).
