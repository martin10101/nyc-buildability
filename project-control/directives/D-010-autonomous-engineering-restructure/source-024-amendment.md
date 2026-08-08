# D-010 — source-024 (owner amendment 24, VERBATIM): B-018 Option A approved + START_CLAUDE recovery-window defect fix ordered

Captured per `.claude/skills/directive-compliance` §1. Channel: owner_message (typed to the
orchestrator on 2026-08-08, in reply to the B-018 blocker report). Frozen base at capture:
`origin/main` = `de2e64732f6774412fb040e423488da1e6c7b844`.

Requirement IDs added by this amendment start at `D-010-R236`; no existing source file or
requirement row (D-010-R001..R235) is edited. Relationship to source-023: resolves B-018 by
Option A (the fresh `--runtime-base` continuation the orchestrator proposed) and adds a bounded
defect-fix obligation for the stranded-START_CLAUDE recovery window discovered by the first live
supervised run (AD-093 qualifying evidence class: unresolved crash/recovery problem;
`.claude/rules/supervisor-freeze.md` §2). Anchors: `#option-a-approval`, `#defect-fix-order`.

## THE DIRECTIVE (verbatim from the owner message, 2026-08-08)

> Approved: resume supervised runs on --runtime-base C:/Users/MLFLL/AppData/Local/NYCBuildabilitySupervisor-r2
>
> Also treat B-018 as a real supervised-runtime reliability defect, not merely a one-time incident. After safely resuming M2-T015, determine the narrow root cause of the stranded START_CLAUDE recovery window and implement/test the smallest durable fix so that a future claude_start_failed event can recover through an authorized deterministic path without requiring me each time. Do not broaden this into supervisor redesign, and do not interrupt M2-T015 unnecessarily if the fix can be handled at the proper bounded checkpoint.

## Redaction

No secrets/keys/credentials present. Verified by scan before commit.
