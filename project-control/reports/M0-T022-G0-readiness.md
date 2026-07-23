# M0-T022 — G0 Definition-of-Ready (orchestrator, administrative)

**Task:** Owner Mission-Control dashboard — read-only observability layer over project-control (V1)
**Branch/worktree:** `task/M0-T022-owner-dashboard` @ `.claude/worktrees/M0-T022-dashboard` (off `origin/main` `0a61b7d`)
**Verdict:** PASS (ready to claim)

## Definition-of-ready checklist

- [x] **Objective is bounded and testable.** Read-only observability dashboard at `/dashboard`; no control-plane mutation.
- [x] **Requirements referenced.** Owner directive 2026-07-22 (dashboard spec); CLAUDE.md #6/#9/#14/#26; product-flow + gates docs.
- [x] **Owner decisions captured.** Light theme (match product tokens); built-in SVG/CSS map (zero new deps); public-repo GitHub reads (no secret). Recorded 2026-07-23.
- [x] **File scope fenced.** `allowed_paths`/`forbidden_paths` set; existing product screens, contracts, services/api, package.json, master_plan, and the control CLI are forbidden.
- [x] **Acceptance scenarios written first (15).** Contract (AS-1), determinism (AS-2/5/6/10), mapping (AS-3/4/7), blockers/launch (AS-8/9), GitHub/stale (AS-11), fail-safe (AS-12), security/read-only (AS-13), human-journey/a11y/honesty (AS-14), regression/zero-deps (AS-15).
- [x] **Gates + independent reviewers rostered.** G0(orch), G1(data-contract-verifier), G2(orch self-check), G3(code-reviewer), G4(qa-engineer + human-journey-reviewer), G5(security-reviewer). No reviewer equals the producer.
- [x] **No dependency blocks start.** `dependencies: []` — the dashboard observes existing committed ledger state; nothing must complete first.
- [x] **Holds honored.** Read-only observer; expansion/GDS and 3D holds untouched; nothing Published/Verified; M4 rules reported honestly as draft.
- [x] **Thin-client feasible.** python stdlib validation + JSON locally; web build/tests in CI; zero new npm dependencies; negligible disk.
- [x] **Architecture pre-audited.** 7-brief read-only audit (control-plane CLI/state, task/gate/blocker schemas, CI/GitHub, apps/web stack, deployment, product architecture) completed 2026-07-23; design derived from repository reality, not assumptions.

## Notes
- Source of truth stays `project-control/` + git + CI. The one NEW artifact is `project-control/product-map.json` (metadata mapping engineering tasks to product systems + explicit weights), guarded by a schema + validator + CI job so it can never silently drift from the ledger.
- The dashboard reads files and the public GitHub REST API only; it invokes no `project_control.py` write subcommand and holds no secret.
