# M0-T198 producer report (orchestrator, session 2026-10-15c)

Producer: the orchestrator (governance task, M0-T193 precedent). Owner rows: D-094 R307-R315 (sources 029-032).

## What changed
- `.claude/skills/dispatch-brief/SKILL.md` (new): the helper-briefing skill. Five brief parts (the answer needed and the decision it serves; the exact scope with the pinned commit; evidence that could change the answer, with one disconfirming check; what stays unknown; depth and stopping point), the return contract (answer first; finding to evidence to consequence; facts, claims, inferences, assumptions and unknowns apart; what was not checked; one hand-back; END-OF-REPORT) and the standing clauses (D-093, reference cases, read-only and builder limits, ports, heavy-run lock, roster types and no model parameter).
- `.claude/rules/helper-briefing.md` (new): always-loaded (no paths frontmatter) rule with the main-session half (every helper question goes through /dispatch-brief) and the helper half (the answer standard).

## How it carries over (R314)
Rules under `.claude/rules/` without a `paths:` frontmatter load into every session's and every subagent's start-time instructions; the skill is listed for every session in this repository. Once merged to main, a fresh session follows both without the owner repeating them. This session's helpers dispatched before the change see it only through their briefs (a subagent inherits its parent's start-time snapshot).

## Checks
- context_budget_check and lane coverage: see the commit's check log in the session notes.
- No other file changed; CLAUDE.md, agents, hooks and settings untouched.

## Not done here
- An automatic dispatch check (a hook refusing a brief without the five parts) was offered to the owner as a later option; it would touch the dispatch guard and needs its own G5 review.
