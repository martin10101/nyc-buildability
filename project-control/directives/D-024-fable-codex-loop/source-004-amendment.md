# D-024 Amendment 4 — Hardened statusLine canary launch (owner instruction 2026-08-26)

Captured: 2026-08-26 UTC by the orchestrator (Fable 5), verbatim from the owner's interactive
steering prompt issued immediately after the owner REJECTED the orchestrator's first canary-launch
tool call (channel: Claude Code interactive session, tool-use rejection followed by typed
instruction). Base identity at capture: branch `control/D-024-fable-codex-loop`, HEAD
`19a57d72197ad7ce54a25ffc6771ca8d3687c87e` == origin tip (`origin/main` = `d8b3899`), tree clean,
MCP-clean (no `mcp__*` tools exposed in the session tool list), Bootstrap Gate 0 PASS (primary cwd
IS the worktree root). Session-binary note: this orchestrator session's own process runs claude
2.1.220 (live statusLine-journal proof, session `00d5186f…`, entries seconds-fresh at check); the
on-disk binary is 2.1.246, so a child process launches 2.1.246 — the sanctioned
"unit-C canary" discharge path from the M0-T103 G5 report.
Amends: `source-001.md` (owner directive v4). Requirement IDs assigned: D-024-R192..D-024-R199.

Context (reverse trace): this instruction governs the campaign seq-11 FIRST action — the M0-T103
R162 deferral discharge (live 2.1.246 statusLine/subagentStatusLine payload fixture + no-leak
re-proof + explicit permission-mode=default proof, citing D-024-R162/R183). The REJECTED launch
was: `Start-Process claude` in the trusted repo root with `--settings` pointing at an isolated
scratch tee-settings file (chosen to avoid the folder-trust dialog after the auto-mode classifier
denied editing `~/.claude.json`). The owner's hardening below replaces that plan. No ledger task
binds this procedure (orchestrator-recorded discharge per campaign seq 11); accepted work is
immutable and NOT reopened; no new requirement ID binds to any already-gated or accepted task.

---VERBATIM-BEGIN---
Reissue the same bounded 2.1.246 statusLine canary, but harden the child launch:

1. Add --strict-mcp-config so the child has zero MCP servers.
2. Restrict the model-visible built-in tools to Agent only, using the exact syntax supported by the installed 2.1.246 binary.
3. Verify the scratch settings file exists, is a regular file, and contains only the intended canary/statusLine configuration.
4. Do not read or modify repository files.
5. Show me the revised exact command for approval.
6. After capture, terminate the launched PID and its descendants.
7. Prove zero remaining canary agents or shells, Git remains clean, and all created artifacts are confined to the authorized temporary scratch directory.
---VERBATIM-END---

Forward trace (every source item → requirement ID):
- Preamble sentence ("Reissue the same bounded 2.1.246 statusLine canary, but harden the child
  launch") → D-024-R192.
- Item 1 → D-024-R193. Item 2 → D-024-R194. Item 3 → D-024-R195. Item 4 → D-024-R196.
- Item 5 → D-024-R197. Item 6 → D-024-R198. Item 7 → D-024-R199.

Interpretation notes recorded at capture (owner may veto at the R197 approval step):
- Item 4 is read as scoping the canary procedure: the child runs with cwd OUTSIDE the repository
  (the scratch project), and the orchestrator's canary-side steps read/modify nothing in the
  repository. It does not revoke the separately-standing seq-11 deliverable (the masked fixture +
  discharge report committed to the repository afterward) nor the owner-required proofs of item 7
  (a `git status` cleanliness check is itself owner-mandated evidence).
- Item 7 "artifacts confined to the authorized temporary scratch directory" is read as governing
  the canary RUN's side effects (raw captures, tee outputs, temp files); the durable masked
  fixture/report remain the authorized later deliverable unless the owner says otherwise.
