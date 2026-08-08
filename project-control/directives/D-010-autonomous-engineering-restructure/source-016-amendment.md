# D-010 — source-016 (owner amendment 16, VERBATIM): skipped-test evidence for the M0-T048 gate wave

Captured per `.claude/skills/directive-compliance` §1. Channel: owner_message (typed to the
orchestrator on 2026-08-08, mid gate-rerun wave, after the orchestrator reported the supervisor
suite as "1380 passed, 2 skipped"). Base at capture: control branch `control/M0-T048-c2-close`
head `fcdef80` (frozen review identity `fee612ae724085576aad23c0fd1d387fa89e800d`).

Requirement IDs added by this amendment start at `D-010-R155`; no existing source file or
requirement row (D-010-R001..R154) is edited. Relationship to source-015: adds a bounded
gate-evidence obligation to the in-flight M0-T048 rerun wave (skip-reason transparency) and a
conditional follow-up-task decision; it does not alter the source-015 fix, boundaries, sequencing,
or the activation package.

## THE DIRECTIVE (verbatim from the owner message, 2026-08-08)

> have the orchestrator name the two skipped tests and the reason for each (pytest prints the skip reason with one flag) as part of the gate evidence. If the reasons turn out to be stale — e.g., a test that could run here but is being skipped by accident — then it'd be worth a small follow-up task to unskip them. But if they're legitimately environment-conditional, leaving them skipped is normal and safe.

## Redaction

No secrets/keys/credentials present. Verified by scan before commit.
