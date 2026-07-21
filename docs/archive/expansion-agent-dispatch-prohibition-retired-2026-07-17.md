# ARCHIVED — Expansion-agent dispatch prohibition (RETIRED 2026-07-17)

> Historical only. This prohibition is **retired**. It does not govern current work. The active
> expansion planning hold lives in `.claude/rules/expansion-agent-dispatch-hold.md`. Kept for history.

This was §1 of `.claude/rules/expansion-agent-dispatch-hold.md` until 2026-07-21, when it was moved
here to keep the unconditional rule free of retired narrative.

---

## 1. DISPATCH PROHIBITION — RETIRED 2026-07-17

The former prohibition on dispatching `3d-massing-engineer`, `product-design-director`,
`visual-quality-reviewer`, `financial-feasibility-engineer`, `opportunity-search-engineer`
was RETIRED at M0-T013 acceptance (2026-07-17): all five agent definitions now carry the
ADR-005 protocol sections and conformant frontmatter, verified by G3 + G5 re-check
(project-control/reports/M0-T013-G3-code-review.md and M0-T013-G5-security-recheck.md),
merged at ff24147 with CI green. Blocker B-007 is `resolved`; the PreToolUse hook
`.claude/hooks/agent_dispatch_guard.py` reads that status live and now permits the five
agents. The hook and its tests stay in place as a regression backstop — do not remove or
re-scope them without a G5 review. NOTE: dispatchability does not authorize new expansion
work; the owner-review planning hold still governs planning.
