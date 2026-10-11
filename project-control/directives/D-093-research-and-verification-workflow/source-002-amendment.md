# D-093 source-002 (amendment): the owner's answer on the always-loaded size cap: move nothing; take off the token restrictions

Captured 2026-10-11 by the orchestrator (Claude Code session 01TpXJN7hC1avVgaNN9B4fCz, model claude-opus-5-5). A script copied the raw text from the saved session transcript under `~/.claude/projects/-root-project-nyc-buildability/`; nothing was retyped, and every quoted fragment below was cut out of the message by the script.

| What | Transcript | Line | Entry uuid | Timestamp | Stored as | Raw-text SHA-256 |
|---|---|---|---|---|---|---|
| the message | `33a4b56e-2b0e-47dd-9b18-d09cf4097f56.jsonl` | 265 | none | 2026-10-11T01:31:31.363Z | queue entry holding the typed text | `f81a3b341b73a6858771eb119b8355f7c6b5ee963c6c22782ade4f9feb77f30e` |
| the message | `33a4b56e-2b0e-47dd-9b18-d09cf4097f56.jsonl` | 277 | `67c720bc-ce32-42fc-92ab-1a0856935e30` | 2026-10-11T01:31:31.362Z | attachment line holding the message as delivered to the running turn | `f81a3b341b73a6858771eb119b8355f7c6b5ee963c6c22782ade4f9feb77f30e` |

Context. Sent mid-turn at 2026-10-11 01:31 UTC while the orchestrator was surveying. The orchestrator had found that the always-loaded instructions stood at 9,941 of the 10,000-token cap (tools/context_budget_check.py; PROGRAM_KNOWLEDGE.md: 'never raise the cap again without a new owner authorization'), that moving older notes out is held by question B1, and had said it would give the new rule its own small allowance and ask.

## Owner message (verbatim)

Transcript timestamp 2026-10-11T01:31:31.363Z. 49 characters; the digest is of the raw text.

> No dont move just take of the tkoen restrictions 

## Reading

| Words of the message | Requirement |
|---|---|
| "No dont move just take of the tkoen restrictions" | R074 (authorization) |

- **My reading of 'the token restrictions':** the always-loaded instruction cap the owner was told about (the 10,000-token eager budget in tools/context_budget_check.py and the PROGRAM_KNOWLEDGE.md budget line). Sizes stay reported, not enforced. The separate size budget of the session handoff (8,000 tokens) was not raised in the question and is left as it is; the completion report says so.
- **Unchanged by this answer:** question B1 (moving instruction text) stays open; nothing moves.
- **Sentences of the message quoted by no row:** none.
- **Not claimed by this capture:** no row is verified; all 1 are pending. This capture changes no product file, no test and no instruction file.
