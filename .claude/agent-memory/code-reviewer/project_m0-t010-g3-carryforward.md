---
name: m0-t010-g3-carryforward
description: M0-T010 expansion-pack integration G3 PASS 2026-07-17; residuals to enforce later (CI post-merge, agent-conformance before dispatch, GDS P1-P8 owner approval, temp cleanup)
metadata:
  type: project
---

M0-T010 (3D/UI expansion pack integration + report) G3 PASS at branch task/M0-T010-expansion-integration @ c0769ae (Phase 1 d25d2b2). All 14 pack files verified blob-identical to the owner ZIP (sha256 0C89C2B1..FB146A) via independent extraction + `git hash-object` comparison. Note: repo has `core.autocrlf=true` and NO `.gitattributes` — pack files are LF, Windows working tree shows CRLF for checked-out pre-existing files; byte-identity must be asserted at git-blob level, not raw on-disk hash.

**Why:** raw SHA256 of working-tree files falsely reported the 3 pre-existing files as DIFFERENT during this review; blob comparison resolved it.

**How to apply / residuals to recheck:**
- S4 residual: CI green post-merge not yet proven (branch-only review). Verify at G4/merge.
- The 5 pack agent files (.claude/agents/{3d-massing-engineer,product-design-director,visual-quality-reviewer,financial-feasibility-engineer,opportunity-search-engineer}.md) have verified conflicts C1–C7 (no memory/permissionMode/Skill/isolation frontmatter, no ADR-005 sections). MUST NOT be dispatched until the conformance task is accepted — flag as defect if any is dispatched first.
- GDS plan proposals P1–P8 in docs/3D_UI_EXPANSION_INTEGRATION_REPORT.md §7.2: all OLD quotes verified verbatim-applyable against docs/GENERATIVE_STRATEGY_INTEGRATION_PLAN.md on main at 2026-07-17. If the plan changes before owner approval, re-verify applyability (producer A4: apply by old-text match, not line number).
- Temp extraction dirs to clean at acceptance: %TEMP%\b005-extract, %TEMP%\g3-m0t010-extract, %TEMP%\g3-m0t010-fresh (all KB-scale).
- Report snapshot facts (18 accepted, M1-T007 at 75%) are as-of 2026-07-17T08:14Z ledger basis; M1-T007 moved to awaiting_gate/85% at 08:27Z — snapshot-labeled, not a defect.

Related: [[m1-t006-g3-carryforward]] (contract v1.1 facts reused by report §3), [[vercel-dropped]] (report correctly Render-only).
