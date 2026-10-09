# D-090 source-073 (amendment): the owner approves the minimal local checkpoint hook with corrections, 2026-10-09

Captured 2026-10-09 by the orchestrator (Claude Code session 013RaGmCmULdpmjCy58qBeMY, model claude-opus-5-5). A script copied the raw text from the saved session transcript under `~/.claude/projects/-root-project-nyc-buildability/`; nothing was retyped, and every quoted fragment below was cut out of the message by the script.

| What | Transcript | Line | Entry uuid | Timestamp | Stored as | Raw-text SHA-256 |
|---|---|---|---|---|---|---|
| the message | `f3a4a686-fb58-4cf9-9dc1-56dcc8d8fba7.jsonl` | 1146 | none | 2026-10-09T06:30:03.045Z | queue entry holding the typed text | `18c5d99a0c94ee46abe2d9a19b535d02c5b90b7060c4d098f554c7f2293e9c23` |
| the message | `f3a4a686-fb58-4cf9-9dc1-56dcc8d8fba7.jsonl` | 1148 | `ff0dd3dd-16d9-4ce7-83eb-9c641b29af66` | 2026-10-09T06:30:03.236Z | user line holding the message as delivered | `18c5d99a0c94ee46abe2d9a19b535d02c5b90b7060c4d098f554c7f2293e9c23` |

Context. The session had brought the exact settings lines and the script for approval. The builder of task M4-T037 was making one correcting commit. Recorded on the branch of wave 17; registry files only; not pushed.

## Owner message (verbatim)

Transcript timestamp 2026-10-09T06:30:03.045Z. 950 characters; the digest is of the raw text.

> Approve the minimal local checkpoint hook once these corrections are made:
>
> - Add only the compact-matched hook. Existing hooks merge across settings levels; do not copy the reminder or overwrite existing settings.
> - Select this session’s notes explicitly, rather than whichever notes file was modified most recently.
> - Include the checkpoint’s source path and timestamp. Do not silently cut off essential information; clearly identify missing or shortened content and its source.
> - Correct the record: current Claude documentation says native background helpers survive compaction. Identify any limitation specific to our setup before imposing a restriction.
>
> Check the script’s actual output for the correct session and its handling of missing or oversized checkpoints. Include the final script and one sample output with the next normal update.
>
> Keep this bounded, then continue the building-option work. No additional audit or workflow framework.

## Reading

| Words of the message | Requirement |
|---|---|
| "Approve the minimal local checkpoint hook once these corrections are made:" | R758 (authorization) |
| "Add only the compact-matched hook." | R759 (obligation) |
| "Existing hooks merge across settings levels; do not copy the reminder or overwrite existing settings." | R760 (external_fact) |
| "Existing hooks merge across settings levels; do not copy the reminder or overwrite existing settings." | R761 (prohibition) |
| "Select this session’s notes explicitly, rather than whichever notes file was modified most recently." | R762 (obligation) |
| "Include the checkpoint’s source path and timestamp." | R763 (obligation) |
| "Do not silently cut off essential information; clearly identify missing or shortened content and its source." | R764 (prohibition) |
| "Correct the record: current Claude documentation says native background helpers survive compaction." | R765 (obligation) |
| "Identify any limitation specific to our setup before imposing a restriction." | R766 (sequencing) |
| "Check the script’s actual output for the correct session and its handling of missing or oversized checkpoints." | R767 (evidence) |
| "Include the final script and one sample output with the next normal update." | R768 (return) |
| "Keep this bounded, then continue the building-option work." "No additional audit or workflow framework." | R769 (prohibition) |
| "Keep this bounded, then continue the building-option work." | R770 (authorization) |

- **Approved once corrected (R758): only the one hook, nothing copied or overwritten (R759 to R761); this session's notes, with path and time, nothing cut silently (R762 to R764).**
- **The record corrected; no restriction without a named limitation of this setup (R765, R766).**
- **Checked by trial; script and sample with the next normal update; bounded; on with the building option (R767 to R770).**
- **Sentences of the message quoted by no row:** none.
- **Not claimed by this capture:** no row is verified; all 13 are pending. This capture changes no product file, no test and no instruction file.
