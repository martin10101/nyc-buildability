# D-007 amendment 2 — owner message (verbatim capture)

- Captured: 2026-08-03T22:52:13+00:00
- Channel: owner chat message (this session)
- Base SHA at capture: e7f5078b2c3668c255fe65bc22afde576f65c75e (origin/main)
- Amends: source-001.md (via source-002-amendment.md)

## The owner message

OWNER MESSAGE — CI grant + Phase 5 GO. Capture this message verbatim first;
it contains one grant and one dispatch decision — decompose per the intake
standard, then execute in the order written.

PART 1 — GRANT, one-time, exact-shape CI wiring: amend the existing GitHub
Actions workflow(s) under .github/workflows/ to invoke the supervisor test
suite (pytest tools/test_agent_supervisor_*.py) as an additional step or
job. Additive only: no existing step, trigger, permission, or protection
may be removed, weakened, or reordered; no new secrets, tokens, or
external actions introduced; diff confined to the minimal invocation
change. Route it as a normal PR — it queues for my merge under R721, with
CI green on the PR proving the new step itself runs. Report before/after
of the changed workflow section. Grant covers exactly this edit and
expires on completion.

Also, for the record: state which review satisfied standing grant (b)'s
"after a passing review" condition for the phase pushes to
task/M0-T036-supervisor-bridge, citing where each verdict is preserved.

PART 2 — PHASE 5 GO: proceed with the shadow pilot per D-007 §17 and the
task packet. Choose a real controlled-task lifecycle that satisfies §17's
criteria; M0-T035's pending acceptance run is a natural candidate if it
qualifies — the §17 fit rules, not convenience. Sequencing constraint:
assemble the decision packet only after the Part 1 CI PR is merged and
green, so the packet's CI section reflects the suite actually running.
The packet then STOPS for my activation decision per R541. Limited-auto
is never enabled by this task; every merge continues to queue for me.
