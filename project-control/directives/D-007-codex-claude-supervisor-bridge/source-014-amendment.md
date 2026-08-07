# D-007 amendment 13 - owner message (verbatim capture)

- Captured: 2026-08-05T14:28:24+00:00 (session-local)
- Channel: owner chat message (this session, fresh session 2026-08-05)
- Base SHA at capture: d5d9b506c8be63eafd00ad92bd2d3dab2012d067 (origin/main); task branch task/M0-T036-supervisor-bridge @ 7ad26d4
- Amends: source-013-amendment.md (three-part model-chain correction)

## ORCHESTRATOR NOTE (not owner text)

This one owner message spans two directives on two branches. It is captured verbatim in full below.
Its requirements are decomposed by home directive:

- **D-007 (here, this branch):** the M0-T036 / supervisor-bridge items -> new rows D-007-R609..R614.
  - R609 records the owner OVERRIDE that LIFTS the D-007-R607 Fable-5 "wait-for-Thursday" hold for
    M0-T036's held reviews ONLY, authorizing them NOW on claude-opus-4-8 effort xhigh (the proven
    reviewer-model fallback). R607's text is unchanged and remains the standing hold for any OTHER
    Fable-5-pinned review; R609 supersedes it for M0-T036 only (append-only supersession, mirroring
    how source-013 part B superseded part A item (2) via new rows).
- **D-009 (batch branch control/D-009-depsec-and-m0t019-dispatch):** Task 1's M0-T019 remediation
  items are decomposed there, bound to M0-T019 (see the cross-registry pointer row D-007-R614). They
  are NOT decomposed here because M0-T019, D-009, and blocker B-017 all live on the batch branch.

## The owner message - verbatim

Fresh session - verify repo state first; last session's safety classifier was blocking writes (false positive on malware-research content), nothing lost, all critical work pushed to 9d9e55b.

Decision on M0-T036's held reviews: use Opus 4.8 xhigh now, overriding the Fable-5 wait-for-Thursday pin for THIS task only. Fallback exists and is proven, and the code's been frozen for days - no reason to wait. Capture this override.

Then do two things in order:

1. Apply the M0-T019 remediation the producer already validated (32->40 tests): the sharp 0.35.3 + brace-expansion 1.1.18 overrides, the age-gate comment, the stricter total==0 audit step, the 8 new age-gate tests, and the producer-report subsection. Spawn the producer UNNAMED (named spawns get read-only'd by the guard - that was last night's bug). Run node --test, commit locally, do NOT push yet. Do NOT change the FE-S9 age threshold and do NOT regenerate the lockfile - those wait on my pending A/B age decision.

2. Run M0-T036's final Fable-5 delta re-review + the held G2 wave at frozen b95ebf7, on Opus 4.8 xhigh. Record every verdict verbatim. Hand me the accept line for M0-T036 when the gates pass - but do NOT activate limited-auto; activation stays my separate decision and the packet's recommendation is keep-shadow-only.

Keep building per D-008 and last night's rules: batch commits locally, one larger push after real work lands, no push-per-step. Reviewers on Opus 4.8 xhigh while Fable's out. Stop only at a true gate - accept, merge, credentials, legal sign-off, or genuine contradiction. Nothing merges or accepts without my typed line.
