---
name: dispatch-brief
description: Turn the orchestrator's question or task into a well-scoped helper brief before dispatching any subagent (reviewer, researcher, planner or builder). Use every time a helper is sent work, so the helper knows the exact answer needed, the exact scope, what evidence could change the answer, what stays unknown and how deep to go, and returns a reply that leads with the answer.
---

# Helper brief (owner, D-094 R307-R315)

A short question to a helper gets a shallow answer. Before any dispatch, rewrite the question as a
brief with the five parts below, then add the return contract and the standing clauses. Do this
internally: the brief goes to the helper, never to the owner. Keep the helper's intent narrow: do
not turn a simple lookup into a broad assignment, and do not add work the question did not ask for.

## The five parts

1. **The answer needed.** The exact question, the deliverable (a verdict, a spec, a commit, a
   finding list) and the decision it serves ("so that I can contract X", "so that the PR body is
   true"). Say what a good answer looks like in one line.
2. **The exact scope.** Repository, branch, pinned commit (full or 8-character SHA), the files,
   records, reference cases and prior returns to open; which files are the helper's alone and which
   it must not touch. Name the worktree rule for builders.
3. **Evidence that could change the answer.** What to open first (primary sources: the code at the
   pinned commit, the captured law, the official site, the rendered output), what would reverse a
   first conclusion, and one disconfirming check to run. Repeats of one source are not independent.
4. **What is unknown.** The facts not established, which must stay unknown in the answer (never
   turned into zero, a default or a guess), each with the exact missing item and a next step.
5. **Depth and stopping point.** Lookup (answer and verify), evaluation (the material
   considerations and alternatives) or decision (deeper checks, downside cases, what would change
   the recommendation). Say when to stop: when more work is unlikely to change the answer.

## The return contract (append to every brief)

- Lead with the answer (or the conditional answer) and the main reason, in plain words.
- Tie each material finding to its evidence (file and line, record, URL with section, command
  output) and to what it changes for the task.
- Keep apart: verified facts (evidence inspected), reported claims (a record, a helper or a
  producer says so), inferences, assumptions, and unknowns. Mark an interpretation as one.
- Say what was not checked and why. "Not found in what was checked" is not "does not exist".
- Reviews: numbered findings, each REQUIRED or ADVISORY with a concrete correction.
- All parts in ONE hand-back (a hand-back ends the run); end with the line END-OF-REPORT.

## Standing clauses (this project; include the ones that apply)

- Research and verification (D-093): follow `.claude/rules/research-and-verification.md` and
  `docs/RESEARCH_AND_VERIFICATION.md`; read the affected evidence records first; name the settled
  readings in `docs/reference-cases/R6B/cases/`; an engine output is not independent verification.
- Read-only helpers: no repository write, no commit, no push, no ledger command except `status`, no
  agent memory. Builders: own worktree reset to the named head, only their packet's allowed paths,
  never push, one commit with their producer report.
- Never use ports 3000, 3001 or 8000 or stop the owner's preview; heavy runs (multi-file pytest,
  vitest, Playwright, report prints) under `flock /root/project/lanes-runtime/heavy-run.lock`.
- Dispatch with a roster type from `.claude/agents/` and no model parameter (helpers stay on the
  owner's chosen model); unnamed spawns for writers.

## Before sending

Check the brief against the five parts; cut anything the helper does not need; save the brief as a
file in the session folder when it is long, and point the helper at it.
