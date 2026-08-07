# D-007 amendment 15 - owner R593 close-out decision (Option A, verbatim)

- Captured: 2026-08-06T19:41:13+00:00 (session-local)
- Channel: owner decision message (this session)
- Base SHA at capture: d5d9b506c8be63eafd00ad92bd2d3dab2012d067 (origin/main); task branch task/M0-T036-supervisor-bridge
- Amends: source-015-amendment.md

## The owner decision - verbatim

OWNER DECISION - R593

Choose Option A. Record QA-gap-4 as an explicitly accepted residual deferred to the R595 supervised rehearsal. This decision does not waive or remove the live-rotation requirement. It changes when that evidence must be produced.

Required conditions:
1. M0-T036 may complete and be accepted without manufacturing substitute evidence for the unprovable live-rotation leg.
2. The supervisor must remain shadow-only.
3. R595 supervised rehearsal becomes a mandatory blocking prerequisite before: supervised-auto activation; limited-auto activation; automatic product-task execution; or any claim that live session rotation has been proven.
4. The residual must be visible in: M0-T036 task state; acceptance evidence; SESSION_HANDOFF.md; the relevant gate/evidence map; and the activation checklist.
5. Do not represent R593 as fully live-proven.
6. Re-run all evidence that is now provable at the current repository identity, including: R207; evidence-map review; directive/registry validation; current-HEAD verification; and the final M0-T036 acceptance checks.
7. If all remaining checks pass: complete and accept M0-T036; commit the decision and evidence; push only the exact task/M0-T036-supervisor-bridge branch; update or create the appropriate pull request; complete ordinary integration permitted by current repository policy; do not activate anything beyond shadow mode.
8. Leave no active children, writable subprocesses, unresolved Git effects, or uncommitted M0-T036 deliverables.
9. Update SESSION_HANDOFF.md with the exact final state.
10. Return a final clean-stop report (branch; HEAD; pushed remote SHA; PR and merge state; M0-T036 acceptance state; R595 blocking condition; remaining uncommitted files; worktrees; active children = none; exact next project action).

Proceed without asking for another routine approval.
