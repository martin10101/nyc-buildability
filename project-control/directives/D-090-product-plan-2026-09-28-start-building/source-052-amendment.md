# D-090 source-052 (amendment): owner messages 107 and 108, 2026-10-07 - run several independent parts at once, about five helpers, never on the same file

Captured 2026-10-07 by the orchestrator (Claude Code session 013RaGmCmULdpmjCy58qBeMY, model claude-opus-5-5). A script copied each raw text from the saved session transcript under `~/.claude/projects/-root-project-nyc-buildability/`; nothing was retyped. Every owner fragment quoted in a requirement row was checked by the script to be an exact substring of its own message.

| Message | Transcript | Line | Entry uuid | Timestamp | Stored as | Raw-text SHA-256 |
|---|---|---|---|---|---|---|
| 107 | `a20527ef-f7ab-4a57-9f9b-d1cde1c2de3e.jsonl` | 768 | `7cecfc6a-489e-48bb-83c1-b0df9c43da4b` | 2026-10-07T04:44:33.277Z | user line | `fbf5acdf672ebeaa88ed3c86856a2e8f18dd4dd1bd2b3f87bbb5ea38ea39813c` |
| 108 | `a20527ef-f7ab-4a57-9f9b-d1cde1c2de3e.jsonl` | 776 | `8e56ee09-4f6c-4cf7-b336-310d9e9b2009` | 2026-10-07T04:44:57.955Z | queued-command attachment (sent mid-turn) | `12aa3d95880110d72aee42d3e8da44a4e9ef361d51db370f99465dfd6a0d7035` |

Both blocks below hold the raw texts unchanged (message 108's raw text ends with one space, which the quote block does not show; the digest is of the raw text).

Context: the messages arrived while the rule check of the law-text captures (task M4-T025) was running. The orchestrator's reply (line 808, uuid `e43f8130-534e-4144-887a-12630d183c09`, 2026-10-07T04:46:42.280Z) told the owner how it read the two messages ("Up to five helpers at once, on pieces that share no files. Of those, at most three build at the same time; that is the project's own written limit.") and ended that reading with "Tell me if you meant something different." It also said that nothing would start under them before the captures had merged and the two messages were recorded. They were recorded here, on the next branch, because the branch of the captures was frozen for its rule check when they arrived.

## Owner message 107 (verbatim)

Transcript timestamp 2026-10-07T04:44:33.277Z.

> Why dont u run a few difrint parts of the program at once to speed it up obviously not anything that will collide with each other or work on the same file

## Owner message 108 (verbatim)

Transcript timestamp 2026-10-07T04:44:57.955Z.

> Like spine up 5 subagents 

## Reading

| Message | Words of the message | Requirement |
|---|---|---|
| 107 | "Why dont u run a few difrint parts of the program at once to speed it up" | R493 (return) |
| 107 | "run a few difrint parts of the program at once to speed it up" | R494 (authorization) |
| 107 | "obviously not anything that will collide with each other or work on the same file" | R495 (prohibition) |
| 108 | "Like spine up 5 subagents" | R496 (authorization) |
| 108 | "Like spine up 5 subagents " | R497 (hold) |

- **What changes (R494, R496):** more than one piece may be in work at once, with at most five helpers, of which at most three build and at most four review. Before this the limit was one helper at a time (R211, R314), then one builder with one research helper (R488), and one piece at a time (R308).
- **A tension the record states and does not hide:** the owner's working guidance in `CLAUDE.md` still reads "Finish one implementation piece at a time and obtain independent review" (R308) and "Do not add a swarm or increase concurrency without my approval" (R316). These two messages are that approval, for independent pieces. The guidance text is the owner's and is not edited by this record.
- **What does not change (R495, R497):** no two pieces on the same file; heavy test runs one at a time; merges one at a time, in order, on a fully green run; nothing built on unmerged work; every piece independently reviewed.
- **Not claimed by this capture:** none of R493-R497 is verified. All 5 rows are pending.
