# D-085 subagent-model deviation — seq 128, 2026-09-24 (orchestrator self-report)

## The standing instruction

D-085 scope line, reaffirmed by the owner on 2026-09-23 (source-003, verbatim): "why cant u do it
i give u permisin also sub agent stays 4.8". Every producer and reviewer agent file pins
`model: claude-opus-4-8` with `effort: xhigh` (D-064).

## What went wrong

After the seq-128 context compaction (about 08:41Z) the orchestrator passed `model: "opus"` on its
Agent dispatches. That parameter OVERRIDES the agent file's pin, and "opus" resolves to
claude-opus-5-5. Twenty dispatches between about 08:55Z and 10:05Z therefore ran on Opus 5.5 instead
of Opus 4.8. The subagent transcripts show the model id:

- Reviewers (10): dcv-cad (M5-T081/T086 DCV), dcv-t077, dcv-t083, cr-web + qa-web + hj-web
  (M5-T078/T079), cr-p0 + hj-p0 (M5-T080), cr-m0 + qa-m0 (M0-T159).
- Producers (10): M5-T088, M5-T089, M5-T090, M5-T091, M5-T092, the M5-T078 and M5-T079 reworks,
  the two M5-T080 rework halves, and the M0-T159 correction.
- Every dispatch BEFORE the compaction, and every one made without the parameter, ran on
  claude-opus-4-8 as pinned.

Detected at about 10:20Z, while writing the owner's status board, by grepping the subagent
transcripts for their model id.

## Correction

- From 10:20Z every dispatch omits the `model` parameter, so the agent files' claude-opus-4-8 xhigh
  pin applies.
- Program lesson added to .claude/rules/PROGRAM_KNOWLEDGE.md.
- Agents already running on Opus 5.5 are allowed to finish, so their in-flight work is not
  discarded. The gates do not depend on the model, and every output still passes the same
  independent reviews.
- The owner is told plainly in the next status message and may ask for any of that work to be
  redone on Opus 4.8.
