# D-004 — source-003 (owner amendment 2, verbatim)

Captured verbatim per `.claude/skills/directive-compliance` §1 (amendments are new append-only
files; committed sources are never edited). Channel: owner_message. Amends `source-001.md`.
Frozen baseline unchanged: `origin/main` = `421265709f81a40e20f3d890609907ed932967dd`.
Requirement IDs added by this amendment start at `D-004-R096`; no existing row is edited.

---

Acknowledged on the amendment and validator result. Decisions:

1. EFFORT: do NOT apply any effort setting anywhere. Hold the item-3
   findings as an open decision item in your scratchpad/agent-memory
   (no new tracked files); I will decide next session.
2. FLAG ③: option (a) — M0-T027 gets contracted on my Step-1 GO and
   the capture + packet commit together, next session.
3. MACHINE BUG: every hook on this machine is failing non-blocking
   because the project path contains a space ("nyc zoning") and hook
   commands word-split on it. I am fixing the path owner-side now.
   Note two ride-along items for M0-T028's future scope: quote all
   project-path references in every hook command so the repo is
   space-safe on any machine, and add .claude/settings.local.json to
   the repo .gitignore.
4. Do NOT start Step 1 in this session. Confirm the uncommitted D-004
   capture files are intact in the working tree, then stop. I will
   relaunch from the renamed path; that will be a fresh conversation
   and a fresh team by design.
