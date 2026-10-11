# D-090 source-084 (amendment): the owner's correction after handoff seq 158: at a handoff nothing keeps running

Captured 2026-10-11 by the orchestrator (Claude Code session 01TpXJN7hC1avVgaNN9B4fCz, model claude-opus-5-5). A script copied the raw text from the saved session transcript under `~/.claude/projects/-root-project-nyc-buildability/`; nothing was retyped, and every quoted fragment below was cut out of the message by the script.

| What | Transcript | Line | Entry uuid | Timestamp | Stored as | Raw-text SHA-256 |
|---|---|---|---|---|---|---|
| the message | `33a4b56e-2b0e-47dd-9b18-d09cf4097f56.jsonl` | 1883 | none | 2026-10-11T04:23:11.215Z | queue entry holding the typed text | `9521581362c5fc25c9a352f46758710c41bda16238ac8dc32d8cd00770c96f7d` |
| the message | `33a4b56e-2b0e-47dd-9b18-d09cf4097f56.jsonl` | 1886 | `42a0f079-0f84-4e27-977a-4c352dba09e7` | 2026-10-11T04:23:11.414Z | user line holding the message as delivered | `9521581362c5fc25c9a352f46758710c41bda16238ac8dc32d8cd00770c96f7d` |

Context. Sent at 2026-10-11 04:23 UTC to session 33a4b56e, about 75 minutes after the owner invoked /session-handoff (03:08 UTC). The orchestrator had written handoff seq 158 but let three helpers (the M5-T157 builder, the M0-T191 code review, the DB-232 planner) keep running, following the session-handoff skill's text on healthy helpers. Two had returned; the builder was still running. That session then saved the builder's unfinished changes (session-2026-10-11a/T157-builder-unfinished-0423.patch), stopped it and updated the handoff.

## Owner message (verbatim)

Transcript timestamp 2026-10-11T04:23:11.215Z. 55 characters; the digest is of the raw text.

> I told u to do a handoff why is 2 thinks still running 

## Reading

| Words of the message | Requirement |
|---|---|
| "I told u to do a handoff why is 2 thinks still running" | R941 (obligation) |

- **Related rows:** the lighter routine handoff, rows R617 to R625 (source-062).
- **My reading, not the owner's words:** 'nothing keeps running' covers builders, reviewers, planners and background commands started by the session; it does not cover the owner's own preview server.
- **Sentences of the message quoted by no row:** none.
- **Not claimed by this capture:** no row is verified; all 1 are pending. This capture changes no product file, no test and no instruction file.
