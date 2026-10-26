# Back and forth: owner ↔ developer (AI), 2026-10-15 to 2026-10-17

A shortened record of the owner's questions about building the app in this session (status questions stay in chat
only: D-094 R128-R130), what was answered, and what was built. Status words: **DONE**, **RECORDED**, **TO DO**,
**OPEN**, **ANSWERED** (as in the 2026-10-11 file).

## 1. How the AI should ask its helpers questions (2026-10-15)

- **Asked:** the owner attached a "full picture" prompt they use for their own work and asked: "Can u implemented this
  skill to use yourself when u have a question to ask a agent ... tell me the approach that we should use ... what I
  want is for you to promote the agent similar to this".
- **Answered:** a short briefing method the AI runs before sending any helper a question: name the exact answer
  needed and the decision it serves; the exact scope (branch, commit, files, records); the evidence that could change
  the answer; what is unknown and must stay unknown; how deep to go and when to stop. Helpers must answer first, tie
  each finding to its evidence, and keep facts, claims, guesses and unknowns apart. The owner's attached prompt stays
  private (referenced by its path and fingerprint only; never copied into the public repository).
  - **RECORDED:** D-094 R307-R311 (source-029, source-030).

## 2. Making it carry over to later sessions (2026-10-15)

- **Asked:** "how do you make sure that it carries over to the other conversations", then: "I meant carry over the
  fact that the program itself will use the style of the skill to ask the agents questions in another sessions, and I
  don't need to tell you again".
- **Answered:** an always-loaded project instruction (`.claude/rules/helper-briefing.md`, no path filter, so every
  session and every helper loads it) names the briefing method (`.claude/skills/dispatch-brief/SKILL.md`) and the
  helper answer standard. Nothing depends on chat history or one session's memory.
  - **RECORDED:** D-094 R312-R315 (source-031, source-032).
  - **DONE (on the work branch):** task M0-T198 built both files and was accepted on 2026-10-16 after an independent
    code review and a directive check.
  - **TO DO:** it reaches brand-new sessions only after the wave-29 work branch is merged into main.

## 3. Is it in use? (2026-10-17)

- **Asked:** "did you implement the system, full picture skill ... within the way you're going to talk to the sub
  agents?"
- **Answered:** yes. Every helper brief of this session follows the five parts and the answer standard (the brief
  files are in the session folder, `prompt-*.md`). The resumed session keeps it because it is in the conversation;
  new sessions get it automatically once wave 29 merges.
