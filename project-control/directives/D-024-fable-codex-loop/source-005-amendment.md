# D-024 Amendment 5 — Failed transport canary + corrected relaunch rules (owner instruction 2026-08-27)

Captured: 2026-08-27 UTC by the orchestrator (Fable 5), verbatim from the owner's mid-turn
interactive message during the approved round-1 canary run (channel: Claude Code interactive
session, user message delivered mid-turn). Base identity at capture: branch
`control/D-024-fable-codex-loop`, HEAD `9c1d266` == origin tip, tree clean.
Amends: `source-001.md` (owner directive v4). Requirement IDs assigned: D-024-R200..D-024-R206.

Context (reverse trace): round 1 of the Amendment-4-hardened canary (owner-approved option (a),
launched 2026-08-27T01:05:14Z, PID 9488, scratch project `slcap246`) suffered an argument-transport
failure: the launch prompt contained embedded double-quote characters, and Windows argument parsing
(CommandLineToArgvW semantics) terminated the argument at the first inner quote. The canary's own
UserPromptSubmit hook capture (preserved at
`slcap246/.claude/raw_hook_round1_failed_transport.jsonl`) records the received prompt verbatim,
ending exactly at `prompt = Without`. Consequently no subagent was spawned and no
subagentStatusLine payload was captured. The 7 captured statusLine payloads all report version
2.1.246 and the hook records `permission_mode: "auto"` (not bypassPermissions) — valid partial
captures from a failed-transport round, per the owner's classification below. The canary process
had already exited when termination ran (0 descendants); residue/git proofs recorded in-session
and owed to the discharge report.

---VERBATIM-BEGIN---
The 2.1.246 canary failed safely: its launch prompt was truncated at “prompt = Without,” so no subagent was created and no subagentStatusLine fixture was captured.

Terminate this canary PID and all descendants now. Record this as a failed transport canary, not a capability failure.

Prove the PID is gone, no canary agent or shell remains, Git is clean, and no repository files changed.

Then prepare a corrected relaunch using a shorter prompt with no embedded quotation marks, passed as one validated CLI argument. Preserve --strict-mcp-config, the Agent-only tool restriction, the isolated slcap246 scratch workspace, and all cleanup requirements. Show me the complete revised command before launching it. Do not ask me to type the missing task manually inside the canary.
---VERBATIM-END---

Forward trace (every instruction → requirement ID):
- "Terminate this canary PID and all descendants now." → D-024-R200.
- "Record this as a failed transport canary, not a capability failure." → D-024-R201.
- "Prove the PID is gone, no canary agent or shell remains, Git is clean, and no repository
  files changed." → D-024-R202.
- "corrected relaunch using a shorter prompt with no embedded quotation marks, passed as one
  validated CLI argument" → D-024-R203.
- "Preserve --strict-mcp-config, the Agent-only tool restriction, the isolated slcap246 scratch
  workspace, and all cleanup requirements." → D-024-R204.
- "Show me the complete revised command before launching it." → D-024-R205.
- "Do not ask me to type the missing task manually inside the canary." → D-024-R206.
