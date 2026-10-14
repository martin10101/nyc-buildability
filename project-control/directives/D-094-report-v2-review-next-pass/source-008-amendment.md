# D-094 source-008 (amendment): the owner's correction: keep the same copy-in prompt and the full saved handoff; drop only the checks

Captured 2026-10-11 by the orchestrator (Claude Code session 01TpXJN7hC1avVgaNN9B4fCz, model claude-opus-5-5). A script copied the raw text from the saved session transcript under `~/.claude/projects/-root-project-nyc-buildability/`; nothing was retyped, and every quoted fragment below was cut out of the message by the script.

| What | Transcript | Line | Entry uuid | Timestamp | Stored as | Raw-text SHA-256 |
|---|---|---|---|---|---|---|
| the message | `0dfe2ecc-524d-46d3-b648-aedd812b04de.jsonl` | 581 | none | 2026-10-11T19:13:57.475Z | queue entry holding the typed text | `fbaf77c6c1fb134215fdef351c73895e0d827abdf70db23cc7f081bb8597e742` |
| the message | `0dfe2ecc-524d-46d3-b648-aedd812b04de.jsonl` | 583 | `de77050e-dbdc-4ee3-9579-c4b8cf769598` | 2026-10-11T19:13:57.539Z | user line holding the message as delivered | `fbaf77c6c1fb134215fdef351c73895e0d827abdf70db23cc7f081bb8597e742` |

Context. The owner's reply (2026-10-11, 19:13 UTC) to the orchestrator's answer to source-007, which had proposed a shorter copy-in prompt and a handoff naming only the lines the next step needs.

## Owner message (verbatim)

Transcript timestamp 2026-10-11T19:13:57.475Z. 384 characters; the digest is of the raw text.

> No, you should still give the same prompt. My point was that the saving of the file, so you get the information, so you know everything, where everything is in the new session, that needs to stay. You need to be able to quickly jump back in and know exactly where everything is, how to proceed. But the checks, just you don't have to do, since we literally go from session to session.

## Reading

| Words of the message | Requirement |
|---|---|
| "No, you should still give the same prompt." "My point was that the saving of the file, so you get the information, so you know everything, where everything is in the new session, that needs to stay." "You need to be able to quickly jump back in and know exactly where everything is, how to proceed." | R112 (decision) |
| "But the checks, just you don't have to do, since we literally go from session to session." | R113 (prohibition) |

- **Corrects** the orchestrator's proposal recorded with source-007 (its bullet 'Fewer tokens: ... a short copy-in prompt' and the chat answer 'Shorter text for you to paste' and 'point only to the few lines the next step needs'): withdrawn. Rows R109 and R110 are re-read in the same commit to match (their requirement text is resynced; see the manifest's audit log).
- **What stays:** the handoff file, the session brief and notes, and the copy-in prompt carry everything (what is built, where everything is, how to proceed, what is missing), as before.
- **What goes:** the read-only resume checks and tests at the start of a session after a planned handoff, and the READY TO RESUME round that waits on them.
- **Sentences of the message quoted by no row:** none.
- **Not claimed by this capture:** no row is verified; all 2 are pending. This capture changes no product file, no test and no instruction file.
