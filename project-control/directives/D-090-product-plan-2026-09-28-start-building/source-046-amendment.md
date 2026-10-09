# D-090 source-046 (amendment): owner message 98, 2026-10-06 - the owner's proposal that the main instruction file point to what a session must read at start instead of holding it; look it up and say whether to keep or change the structure; do not just agree; information must not get lost between sessions

Captured 2026-10-06 by the orchestrator (Claude Code session 013RaGmCmULdpmjCy58qBeMY, model claude-opus-5-5). A script copied the raw text from the saved session transcript under `~/.claude/projects/-root-project-nyc-buildability/`; nothing was retyped. Every owner fragment quoted in a requirement row was checked by the script to be an exact substring of the message.

| Message | Transcript | Line | Entry uuid | Timestamp | Stored as | Raw-text SHA-256 |
|---|---|---|---|---|---|---|
| 98 | `f9ce0b61-34ce-4930-a58a-c5acc160e5a4.jsonl` | 1007 | `56daeb72-17ba-4279-8b9b-82f6b3f71c86` | 2026-10-06T19:32:19.687Z | queued-command attachment (sent mid-turn) | `eb2f25125ca884c8c7b3fb210fecd49c7d8a4a740552767d10ec08013bfd0f49` |

The block below is byte-identical to the raw text. The message was dictated: "cloud MD" is `CLAUDE.md`, and "the cloud" is Claude (the tool's maker's guidance).

Context: the message arrived while the review register (task M4-T023) was in its independent review; the session had reported that the register's one-line standing instruction was added to `CLAUDE.md` and that the automatically loaded instructions stood at about 9,922 of 10,000 tokens.

## Owner message 98 (verbatim)

Transcript timestamp 2026-10-06T19:32:19.687Z.

> I think we're doing this wrong. I think the cloud MD just needs to tell it where it should go look for when it starts up a session to familiarize itself with this, this, and that, the most important part of the program that it's building and the rules, so on. I don't know if it's a good idea if it's injected directly into the cloud MD because the cloud recommends that cloud MD should stay as small as possible. Now, I'm not saying we need to set any limits on it. I'm just saying there might be a better approach that is safer, better for the program, will get along with every session, won't disappear, and it will do the job just as good with with a lot less tokens. If I'm wrong, let me know. I might not be right. Don't just agree with me. Look it up online, see how popular... builders are structuring it and tell me if we should leave it like that or we should change anything around the main thing is that at all times when because we make constantly new sessions the information shouldn't get lost and then the program doesn't know where it's left off or what what what happened before or you know what I mean or what we agreed on

## Reading

| Message | Words of the message | Requirement |
|---|---|---|
| 98 | "Look it up online" "tell me if we should leave it like that or we should change anything around" | R458 (return) |
| 98 | "If I'm wrong, let me know." "Don't just agree with me." | R459 (obligation) |
| 98 | "I think the cloud MD just needs to tell it where it should go look for when it starts up a session to familiarize itself with this, this, and that, the most important part of the program that it's building and the rules, so on." "I might not be right." | R460 (decision) |
| 98 | "I don't know if it's a good idea if it's injected directly into the cloud MD because the cloud recommends that cloud MD should stay as small as possible." | R461 (external_fact) |
| 98 | "Now, I'm not saying we need to set any limits on it." | R462 (prohibition) |
| 98 | "there might be a better approach that is safer, better for the program, will get along with every session, won't disappear, and it will do the job just as good with with a lot less tokens." | R463 (obligation) |
| 98 | "the main thing is that at all times when because we make constantly new sessions the information shouldn't get lost and then the program doesn't know where it's left off or what what what happened before or you know what I mean or what we agreed on" | R464 (obligation) |

- **What was read and answered (R458, R459, R461), 2026-10-06:** the maker's documentation (`code.claude.com/docs/en/memory`, `code.claude.com/docs/en/best-practices`), one article by the maker on context (`anthropic.com/engineering/effective-context-engineering-for-ai-agents`) and one widely cited practitioner guide (`humanlayer.dev/blog/writing-a-good-claude-md`). No survey of many builders was made; the answer said so. The answer: the owner is partly right. The files loaded automatically total about 480 lines (about 9,900 tokens), more than twice the documentation's 200-line target, and the largest is the 219-line file of operating notes, not the owner's guidance (24 lines). Against a pointer-only file: the documentation says a file that is only mentioned in words is read only if the session decides to open it, and the main instruction file is the one thing present at every start and re-read after compaction. Recommendation put to the owner: keep the hard rules, the start-up routine and the goal in the main file; move most operating notes to files that load on demand; have the start-of-session script print a short "where we are"; do it as one tracked, independently checked task. The owner has not answered.
- **Not decided (R460):** nothing in the instruction files is restructured on this message.
- **Not claimed by this capture:** none of R458-R464 is verified. All 7 rows are pending.
