# D-007 amendment 14 - owner M0-T036 close-out decision (verbatim capture)

- Captured: 2026-08-05T18:43:54+00:00 (session-local)
- Channel: owner decision selection (this session), in reply to the orchestrator's close-out question
- Base SHA at capture: d5d9b506c8be63eafd00ad92bd2d3dab2012d067 (origin/main); task branch task/M0-T036-supervisor-bridge
- Amends: source-014-amendment.md

## Context (orchestrator note, not owner text)

The independent 577-requirement directive-compliance verification of M0-T036 at content identity
08f8db0e...cabc49 (9-cluster parallel wave, claude-opus-4-8 xhigh; report
project-control/reports/M0-T036-D007-verification-577.json) returned 575 PASS and TWO UNVERIFIABLE
gating requirements:
- D-007-R207 (obligation): the enumerated bounded fail-closed resource-limit set is only partially
  built - per-day model-call cap, per-day external-write cap, and CPU/memory limits are absent (the
  build is candid and fail-closed, does not falsely claim them).
- D-007-R593 (evidence): the V1.2 acceptance evidence required THREE live legs; two pass (live allow
  round-trip; live model-mismatch detection) but the context-threshold rotation SEAM ACTUATION was
  never exercised live (unit- and real-process-proven only; a structural block in the synthetic live
  environment was honestly disclosed).

Presented with build / scope-to-activation / park, the owner chose:

## The owner decision - verbatim

Build the 2 missing pieces. I spin up a small follow-up task: add the missing per-day/CPU/memory limit knobs (R207) and build a test harness that live-exercises the rotation seam (R593). Re-verify just those 2, then accept clean.

## Decomposition (this amendment)

- R615 completes D-007-R207 (build the missing limit knobs).
- R616 completes D-007-R593 (live-exercise the rotation seam; STOP-and-report if structurally infeasible).
- R617 the sequencing: after the fixes, re-gate the delta + re-verify at the NEW content identity
  (producer != verifier), then hand the owner the accept line; nothing accepts without the owner's typed line.
