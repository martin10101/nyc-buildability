# D-024-R162/R183 statusLine live-payload deferral discharge — observed identity 2.1.247

Orchestrator-recorded evidence (campaign seq-11 first action; M0-T103 G5 report §6 preconditions
1–2). Author: Fable 5 orchestrator, 2026-08-27 UTC. Governing owner rules: D-024 Amendment 4
(R192–R199), Amendment 5 (R200–R206), Amendment 6 (R207–R219). Owner labeling rule D-024-R208:
every conclusion here binds to the **actual observed 2.1.247** identity; the `slcap246`
scratch-directory name is historical only. M0-T103 remains ACCEPTED and untouched; this discharge
is procedure-level evidence, not a task reopen.

## 1. Deliverables

| Artifact | Path |
|---|---|
| Masked live fixture (both rounds; shape-validated) | `tools/agent_supervisor/fixtures/statusline_live_2026-08-27_2_1_247_r162_discharge.json` |
| This discharge report | `project-control/reports/M0-T103-R162-discharge-2.1.247.md` |

## 2. Procedure (both rounds owner-approved at the exact-command gate)

Two live interactive Claude Code TUI canaries in the isolated `slcap246` scratch project (cwd
outside the repository — zero repo files readable, R196), launched `--strict-mcp-config` (zero MCP
servers, R193) and `--tools Agent` (Agent-only built-ins, syntax verified against the installed
binary's own `--help`, R194), **no permission flags**. Scratch project settings (pre-verified
regular file, sha256 `4bdcf973…`, only statusLine/subagentStatusLine/UserPromptSubmit tee wiring,
R195) teed every raw stdin payload to append-only files.

- **Round 1** (launched 2026-08-27T01:05:14Z, PID 9488, binary 2.1.246): **FAILED TRANSPORT** —
  the prompt argument truncated at its first embedded double quote (CommandLineToArgvW); the
  canary's own hook capture records the received prompt ending exactly at `prompt = Without`.
  No subagent spawned. Classified per owner rule R201 as a transport failure, **not** a capability
  failure; its 7 statusLine payloads (all `version: 2.1.246`) and hook payload
  (`permission_mode: "auto"`) are valid partial captures, preserved separately (R210) in the
  fixture and in `slcap246/.claude/raw_*_round1_failed_transport.jsonl`.
- **Round 2** (launched 2026-08-27T01:25:01Z, PID 14956): corrected transport — 287-char prompt
  with zero quotation marks, pre-validated end-to-end through the identical Start-Process
  construction into an argv probe (arrived as exactly one argument, byte-identical, R203).
  Captured 7 statusLine + 7 subagentStatusLine + 2 UserPromptSubmit hook payloads — **all
  reporting `version: 2.1.247`**. Owner-observed behavioral PASS (R207): exactly one Haiku
  subagent launched, completed naturally, main session returned exactly `CANARY-DONE`.

## 3. Version drift (R208)

The official binary auto-updated **2.1.246 → 2.1.247 between the two launches**
(`claude --version` after round 2: `2.1.247 (Claude Code)`). Round-1 evidence is genuine 2.1.246;
the full capture and every capability conclusion are stamped 2.1.247. The committed capability
probe fixture remains 2.1.246: the probe pack's drift tooth **fired RED as designed**
(`test_live_reprobe_claude_version_matches_fixture`: `2.1.247 (Claude Code)` ≠
`2.1.246 (Claude Code)`; 17/18 other probe tests pass). CI is unaffected (the live re-probe test
skips cleanly on claude-absent runners — the M0-T103 G3 skipif fix). A 2.1.247 re-probe +
tooth re-baseline is owed to the next capability-touching task (carried in the campaign NEXT).

## 4. Findings discharged

1. **statusLine no-leak re-proof (R162/R183, G5 precondition 1):** live primary payloads captured
   on 2.1.246 and 2.1.247; live subagentStatusLine payload captured on 2.1.247 (documented
   fields present incl. the v2.1.205+ `model`/`contextWindowSize` pair; task row:
   `claude-haiku-4-5-20251001`, `status: completed`, `tokenCount: 4666`,
   `contextWindowSize: 200000`). Payload content is machine/session telemetry (context window,
   cost, model, workspace paths, rate-limit windows) — **no secrets, credentials, or tokens**;
   all user paths masked to `[HOME]` in the fixture (77 redactions; 16/16 shape checks;
   final-bytes no-leak scan CLEAN — needles: username, slash/dash user-path shapes, Bearer/ghp_,
   key-shaped `sk-…` runs, email, raw session UUIDs).
2. **Permission-mode proof (G5 precondition 2):** both rounds' hook payloads record
   `permission_mode: "auto"` for sessions launched with no permission flags. On the installed
   binary the `--permission-mode` enum is `acceptEdits, auto, bypassPermissions, manual, dontAsk,
   plan` — there is **no literal `default` mode**; the unflagged default resolves to the
   classifier-guarded `auto`, and is **not** `bypassPermissions`. This satisfies the precondition's
   intent (restarted-daemon dispatches are not in bypass mode) and is recorded as a
   capability-matrix nuance for unit C.
3. **CHILD_SESSION transcript warning (R211):** both canaries inherited
   `CLAUDE_CODE_CHILD_SESSION=1` (with `CLAUDECODE=1`, `CLAUDE_CODE_SESSION_ID`, etc.) from the
   orchestrator shell via Start-Process; they ran flagged as child sessions, displayed the
   transcript-saving warning, and **both payload `transcript_path` files are verifiably absent**
   (measured 01:38Z). The fixture's evidentiary basis is exclusively the tee-captured stdin
   payloads; the missing transcripts are an inherited-environment launch artifact, not evidence.
   Unit-C note: native background dispatch from an orchestrator session inherits session env —
   the adapter must control the child environment explicitly.

## 5. Termination + residue proofs (R198/R199/R200/R202/R212–R214)

- Round 1: PID 9488 found already exited at termination; 0 descendants; no `slcap246` processes.
- Round 2: PID 14956 + descendant 24480 stopped (child-first walk over Win32_Process
  ParentProcessId); post-kill probe: no process with either PID; no process whose command line
  references `slcap246`.
- `claude agents --json` after each round: **zero** canary entries; the parked owner session
  `777b09da` untouched (`waiting`) and the three sibling-project sessions unmodified.
- Artifact confinement (R214): full recursive inventory of `slcap246` = 12 files (settings, 3 tee
  scripts, auto-setup marker, argv probe + result, round-1 preserved captures, round-2 captures);
  nothing written anywhere else; `git status --porcelain` empty at every checkpoint until the
  deliberately prepared deliverables of this landing (R216).

## 6. Tests + validation (R217)

- statusLine handler pack: **23/23 PASS**.
- Capability probe pack: **17 PASS + 1 expected RED** (drift tooth, §3 — the detection working).
- Full registry validator (`validate_directive_compliance.py --check`): **EXIT=0** at the landing
  identity (run recorded with the commit that freezes this report).

## 7. Requirement evidence map (procedure rows, sentinel `D-024-R162-DISCHARGE`)

R192 canary reissued through approval gates ✓ (§2) · R193 strict-mcp-config ✓ · R194 Agent-only
tools ✓ · R195 settings pre-verification ✓ · R196 no repo reads/writes by the canary procedure ✓
(cwd outside repo; orchestrator steps confined to scratch + owner-mandated git/process checks) ·
R197/R205 exact-command owner approvals BEFORE each launch ✓ ("approve (a)", "approve") · R198/
R200/R212 termination ✓ (§5) · R199/R202/R213/R214 residue/confinement/git proofs ✓ (§5) ·
R201/R210 failed-transport classification + separate preservation ✓ (§2, fixture) · R203
quote-free single validated argument ✓ · R204 hardening preserved ✓ · R206 no manual owner typing
✓ (transport fixed instead) · R207 behavioral PASS recorded ✓ · R208 2.1.247 labeling ✓
(fixture + this report) · R209 payloads captured + shape-validated ✓ (16 checks) · R211 transcript
honesty ✓ (§4.3) · R215 masking + no-leak scan ✓ (§4.1) · R216 git-clean-except-deliverables ✓ ·
R217 tests + validator ✓ (§6) · R218 commit only after evidence passes ✓ (this report commits
with the passing evidence) · R219 final report duty ✓ (orchestrator turn report + this file).

## 8. Advisories carried forward (non-blocking)

1. 2.1.247 capability re-probe + drift-tooth re-baseline owed to the next capability-touching
   task (campaign NEXT carries it; M0-T104 unit C is the natural home).
2. Auto-update cadence observation: the binary updated itself mid-procedure (~20 min window).
   Unit C's runtime adapter must treat installed-version as measured-at-use, never cached.
3. Unit-C environment-inheritance precondition: explicitly control child env
   (`CLAUDE_CODE_CHILD_SESSION` et al.) for background dispatches (§4.3).
4. `permission_mode` vocabulary: matrices/tests should accept `auto` as the unflagged default
   (no literal `default` mode on 2.1.246/2.1.247).
