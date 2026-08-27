# D-024 Amendment 6 — Round-2 behavioral PASS, 2.1.247 labeling, bounded landing (owner instruction 2026-08-27)

Captured: 2026-08-27 UTC by the orchestrator (Fable 5), verbatim from the owner's mid-turn
interactive message during the round-2 canary landing (channel: Claude Code interactive session,
user message delivered mid-turn; the harness's standard mid-turn delivery note is framing, not
owner text, and is excluded from the verbatim block). Base identity at capture: branch
`control/D-024-fable-codex-loop`, HEAD `3ca0026` == origin tip, tree clean except in-progress
scratch work outside the repository.
Amends: `source-001.md` (owner directive v4). Requirement IDs assigned: D-024-R207..D-024-R219.

Context (reverse trace): round 2 (owner-approved, launched 2026-08-27T01:25:01Z, PID 14956,
quote-free transport-validated prompt per Amendment 5) captured 7 statusLine payloads, 7
subagentStatusLine payloads, and 2 UserPromptSubmit hook payloads; all round-2 payloads report
version **2.1.247** — the official binary auto-updated from 2.1.246 between rounds (round-1
payloads remain genuine 2.1.246 captures). The owner observed the TUI directly and reports the
behavioral result below. The inherited CHILD_SESSION transcript warning is explained by measured
evidence: the orchestrator shell exports `CLAUDE_CODE_CHILD_SESSION=1` (with CLAUDECODE=1,
CLAUDE_CODE_SESSION_ID, and related session env), which Start-Process children inherit, so both
canaries ran flagged as child sessions and saved no transcript (both payload `transcript_path`
files verifiably absent). PID 14956 + descendant 24480 were terminated with zero-residue,
git-clean, and confinement proofs recorded in-session before this instruction arrived;
re-verification is owed under the landing checklist below.

---VERBATIM-BEGIN---
Round-2 behavioral canary PASS: exactly one Haiku subagent launched, completed naturally, and the main session returned exactly CANARY-DONE.

Important version drift: the live canary header reports Claude Code 2.1.247, not 2.1.246. Preserve the slcap246 directory name as historical only, but label every fixture, report, capability conclusion, digest, and installed-version record with the actual observed 2.1.247 identity. Do not mislabel this evidence as 2.1.246.

Now complete the bounded landing:

1. Capture and validate the genuine primary statusLine and subagentStatusLine payloads.
2. Preserve the round-1 failed-transport evidence separately.
3. Record the inherited CHILD_SESSION transcript-saving warning honestly; do not treat a missing transcript as fixture evidence.
4. Terminate the canary PID and every descendant.
5. Prove zero remaining canary processes, agents, tasks, or shells.
6. Verify all canary artifacts remain confined to the authorized scratch directory.
7. Scan and mask the saved fixtures according to policy.
8. Verify Git is clean except for the deliberately prepared fixture/report changes.
9. Run the applicable tests and full registry validator.
10. Commit and push only after the frozen evidence passes.
11. Report final PASS, PARTIAL, or FAIL with the frozen commit and exact remaining campaign NEXT action.
---VERBATIM-END---

Forward trace (every instruction → requirement ID):
- Behavioral-PASS statement (para 1) → D-024-R207 (record as owner-observed evidence).
- Version-drift labeling rule (para 2) → D-024-R208.
- Item 1 → D-024-R209. Item 2 → D-024-R210. Item 3 → D-024-R211. Item 4 → D-024-R212.
- Item 5 → D-024-R213. Item 6 → D-024-R214. Item 7 → D-024-R215. Item 8 → D-024-R216.
- Item 9 → D-024-R217. Item 10 → D-024-R218. Item 11 → D-024-R219.
