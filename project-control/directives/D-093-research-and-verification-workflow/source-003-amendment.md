# D-093 source-003 (amendment): the owner's correction: fix the research-record check's review-date defect permanently instead of logging it

Captured 2026-10-11 by the orchestrator (Claude Code session 01TpXJN7hC1avVgaNN9B4fCz, model claude-opus-5-5). A script copied the raw text from the saved session transcript under `~/.claude/projects/-root-project-nyc-buildability/`; nothing was retyped, and every quoted fragment below was cut out of the message by the script.

| What | Transcript | Line | Entry uuid | Timestamp | Stored as | Raw-text SHA-256 |
|---|---|---|---|---|---|---|
| the message | `72bfc3c3-0b4e-4095-b46f-c2182facd54a.jsonl` | 1677 | none | 2026-10-11T07:42:10.959Z | queue entry holding the typed text | `4105dddbaa9897605d6918855be5a2f2bf0850b0cba498f56a81dea0695435c1` |
| the message | `72bfc3c3-0b4e-4095-b46f-c2182facd54a.jsonl` | 1680 | `ecf93b34-41a2-4177-ab63-8adec21a0c19` | 2026-10-11T07:42:11.070Z | user line holding the message as delivered | `4105dddbaa9897605d6918855be5a2f2bf0850b0cba498f56a81dea0695435c1` |

Context. Sent at about 07:45 UTC, after the orchestrator reported that tools/research_record_check.py picks the latest agent review by comparing date strings (a date-only entry sorts before an earlier same-day entry carrying a time; seen on NB-01), worked around it by stamping the NB-01 revision-3 entry with its return time, and logged the defect in backlog row DB-238 (WATCH).

## Owner message (verbatim)

Transcript timestamp 2026-10-11T07:42:10.959Z. 42 characters; the digest is of the raw text.

> I logged it why cant u fix it permanently?

## Reading

| Words of the message | Requirement |
|---|---|
| "I logged it why cant u fix it permanently?" | R075 (obligation) |

- **My reading of 'I logged it':** the owner refers to the orchestrator's report that it had logged the defect in the backlog; the owner wants the defect fixed in the check itself, not logged.
- **Related rows:** the structural promotion check (D-093 R052, R070); backlog DB-238 is updated when the fix lands.
- **Sentences of the message quoted by no row:** none.
- **Not claimed by this capture:** no row is verified; all 1 are pending. This capture changes no product file, no test and no instruction file.
