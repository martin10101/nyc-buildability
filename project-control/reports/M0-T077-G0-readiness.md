# M0-T077 — G0 readiness (D-020 program-wide MCP default-deny)

Administrative G0 record by the orchestrator. Everything below was verified against the
LIVE repository before any file was created (owner directive D-020 §1).

## 1. Live reconciliation (read-only, 2026-08-19)

| Checkpoint item | Reported | Live | Match |
|---|---|---|---|
| origin/main | 31c50a09bd1671d111f21923c6a2d739f51187dd | 31c50a09bd1671d111f21923c6a2d739f51187dd | YES |
| PR #239 | MERGED | MERGED 2026-08-19T16:59:26Z, head 93c80fb6ed47237f4808eebdf0ebf2458c07d6ed, merge 31c50a09 | YES |
| M0-T076 | accepted | `status: accepted`, in `state.json accepted_tasks` | YES |
| Accepted count | 99 | 99 | YES |
| D-019/M0-T076 lifecycle | closed | D-019 registered/active with M0-T076 accepted; verification recorded at 4c5607d1 | YES |
| Post-merge CI | green | CI / secret-scan / context-budget all `success` at 31c50a09 | YES |
| D-013-R060 | PENDING | verification evidence records "PENDING owner/control-plane decision (D-013-R060)"; no later decision exists | YES |
| Controller bundle | not run | no execution record; runbook untouched outside repo | YES |
| Supervisor packet consumption | not enabled | owner-gated boundary intact (D-018 record) | YES |
| limited-auto | disabled | `broker.py` asserts `limited_auto_enabled: False`; CLI refuses by name | YES |
| Program-wide MCP policy | not implemented | checked-in `.claude/settings.json` at 31c50a09 contains no MCP key; no repo `.mcp.json` | YES |

web-e2e note: post-merge runs at 31c50a09 concluded `success`; the reported stuck-runner
occurrences left no failed conclusion on main. Treated as infrastructure delay, read-only,
per §1 — no product defect recorded.

No material discrepancy: proceed (no STOP condition).

## 2. Identifier resolution from the live registry/ledger

- Directive registry ends at D-019 (`index.json`; `PENDING-CAPTURE-…` breadcrumb carries NO
  directive ID by design) → next valid directive: **D-020**.
- Task ledger ends at M0-T076; M0-T077 absent from `tasks/`, `state.json`, and all branches
  → next valid task: **M0-T077**.
- Branch: `task/M0-T077-mcp-default-deny` created from origin/main 31c50a09 (one task, one
  branch, one PR).

## 3. Capture + contract freeze

- D-020 captured verbatim (`source-001.md`, sha256 `bf418f3a812d6f30…`), decomposed into
  34 requirements (11 D-020-BOOTSTRAP session-governance + 23 M0-T077 task rows), registry
  entry active, verification stub pending (producer ≠ verifier).
- M0-T077 packet frozen BEFORE implementation: 27 allowed paths (the checked-in
  `.claude/settings.json` is specifically included after the audit, per D-020 §10), 18
  forbidden paths, 8 acceptance scenarios, documented test commands.

## 4. Pre-implementation evidence already in hand

- Read-only MCP audit complete (four external servers visible in fresh repo sessions:
  claude.ai Airtable, claude.ai Microsoft 365, pencil, supabase; sources identified;
  secrets redacted). To be committed as `M0-T077-mcp-audit.md`.
- Official mechanism confirmation: `disableClaudeAiConnectors` (v2.1.182+; CLI 2.1.220
  installed), `allowedMcpServers`/`deniedMcpServers`, `disabledMcpjsonServers`,
  `enableAllProjectMcpServers` (claude-code-settings schema + code.claude.com docs).
- Fresh-process mechanism probes in an ISOLATED scratch project (no repo/global change):
  full policy ⇒ `No MCP servers configured`; per-key ablations recorded.

## 5. G0 verdict

READY — implementation may begin inside the frozen contract only.
