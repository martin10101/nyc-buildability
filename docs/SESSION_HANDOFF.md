# Session Handoff — resume state as of 2026-07-15

Written by the orchestrator at the end of the bootstrap/M0 session. The new session MUST be opened with this folder (`nyc-development-feasibility-claude-pack`) as the workspace root, then follow CLAUDE.md's start-of-session routine. This file is the conversation-independent resume point; the ledger (`project-control/`) remains the source of truth.

## Paste-ready prompt for the new session

> Read CLAUDE.md and docs/SESSION_HANDOFF.md, run `python tools/project_control.py status`, reconcile with git, then resume the pending work in SESSION_HANDOFF.md section "Immediate queue" top to bottom. Follow ADR-005: producers and reviewers return evidence; only you (orchestrator, main session) run project_control.py, git integration, and gh. Continue autonomously; pause only for secrets, production approvals, or professional legal review.

## Where the project stands

- Accepted tasks: M0-T000, M0-T001, M0-T002, M0-T003 (see `docs/IMPLEMENTATION_STATUS.md`).
- ~5% of the full production scope done; the control plane, CI, and architecture foundation are proven.
- Repo: private `martin10101/nyc-buildability`, branch `main` + task branch `task/M0-T004-monorepo-ci` (head a0d8f3a, CI fully green incl. run 29382502616 after review doc-fixes).
- CI proven end-to-end including deliberate-failure recovery (S4): fail run 29372258042, recovery 29372297441.
- Process model: ADR-005 (orchestrator-only ledger writes; reviewers return reports; regression test `tools/test_project_control.py` runs locally and as the CI `control-plane` job).

## Immediate queue (in order)

1. **M0-T004** (awaiting_gate; G0/G2/G3 PASS recorded): launch security-reviewer for **G5** on the worktree branch head (read-only, report-return). On PASS: merge `task/M0-T004-monorepo-ci` into main (--no-ff), confirm main CI green, record **G4** (reviewer: qa-engineer identity validating the main CI run + regression suite), then accept M0-T004 and remove the worktree.
2. **M0-T006** (awaiting_gate; G0 PASS): launch code-reviewer for **G3** over docs/adr/ADR-001..003, render.yaml, DEPLOYMENT_AND_ROLLBACK.md (scenarios S1–S5 in the task packet; includes ADR-004 amendment-feasibility assessment). On PASS: accept.
3. Checkpoint CP-0004 after both acceptances; update IMPLEMENTATION_STATUS.
4. **M0-T011 / ADR-004**: owner decision of 2026-07-14 — DROP Vercel, serve the Next.js frontend from Render. Producer cloud-architect; amends ADR-001/002/003 + render.yaml + root README deploy-target lines; verify Render Next.js + preview-environment claims from official docs.
5. **Render services**: owner's API key was provided via chat (TEMPORARY — never write it to disk; owner will revoke). If still valid after M0-T004 merge: create the project's web service (services/api) per render.yaml in workspace "My Workspace" (`tea-d37n4vje5dus739gucd0`) — NEVER touch the 4 pre-existing unrelated services (invitebot, polymarket-paper-bot, textai-sms-bot, nyc-ami-calculator). If revoked, request a fresh key or use the dashboard Blueprint flow (blocker B-002 has details).
6. **M0-T005** (secrets policy + CI secret scan) and **M0-T009** (contracts v1 — MUST fix G3 defects D1/D2/D3 recorded in `project-control/reports/M0-T004-G3-review.md`).
7. **M1 research fan-out**: one official-source-researcher task per remaining mandatory source family (PLUTO/MapPLUTO, Zoning Tax Lot DB, GIS zoning features, Zoning Resolution, DOB NOW, BIS, COs, DOB violations, ACRIS, landmarks, flood, pending land use, DOB bulletins/codes, NYS MDL), pattern = M0-T002; G1 by data-contract-verifier.

## Blocked on the owner (details in docs/HUMAN_ACTIONS_REQUIRED.md)

- B-001 SUPABASE_ACCESS_TOKEN → unblocks M0-T007/T008 (config lives in `C:\Users\MLFLL\.mcp.json`, env key `SUPABASE_ACCESS_TOKEN`, server pinned to project-ref `dyiviaalkqxeyyxotvvh` — owner must confirm this project or supply a new ref).
- B-004 Geoclient subscription key.
- B-005 3D/UI expansion pack incomplete (4 docs + 5 agent files missing) → M0-T010 blocked.

## Known environment facts for the new session

- Windows PowerShell 5.1 writes BOM via Set-Content — agents must use the Write tool; control plane tolerates BOM (utf-8-sig).
- Background subagents auto-deny permission prompts — give them only pre-allowed/read-only work (ADR-005).
- Session-level permission allowlist lives in the OLD workspace root (`Downloads/nyc zoning/.claude/settings.local.json`); when reopening at the pack root, Claude Code will use THIS folder's `.claude/` — re-approve or re-add the narrow allow rules on first use (python tools/project_control.py *, git add/commit/push origin *, gh run/workflow *; never destructive commands).
- Owner PC disk floor: keep ≥ 4 GB free; ~5.2 GB free at handoff; no local installs ever (docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md).
