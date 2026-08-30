# D-024 Amendment 18 — producer model-identity evidence before M0-T121 acceptance (owner instruction 2026-08-30)

Captured: 2026-08-30 UTC by the orchestrator (Fable 5), verbatim from the owner's message
(typed while the M0-T121 producer runs in its isolated worktree; per the instruction itself
and R318 the producer is NOT interrupted — this capture and the evidence gathering are
read-only with respect to the producer). Base identity at capture: branch
`control/D-024-fable-codex-loop`, HEAD `04216dd5c9f6ef415c445471abacf6d854dcd917`
(local == origin; tree clean). Amends: `source-001.md` (owner directive v4). Requirement IDs
assigned: D-024-R323..D-024-R326.

Reconciliation: the owner requires, BEFORE M0-T121 acceptance, a durable record of (a) the
producer's ACTUAL model identity (observed evidence, not configuration alone) and (b) the
durable authority under which Opus 4.8 is used (R323). The running producer is not
interrupted (R324 — broader than R318's capture-timing rule: no interruption for any
reason short of unresponsive/unsafe behavior, per the standing agent-lease rules). If
Opus 4.8 turns out to be an unauthorized substitution or fallback rather than an explicitly
permitted bounded subagent assignment, acceptance fails closed and the owner dispositions
it first (R325). Allowlisting alone is never treated as authorization (R326 — consistent
with the standing allowlist-is-not-authorization principle, D-010). Rows bind M0-T121
(acceptance-gating evidence). Relevant durable authority of record: the resolved D-004
model-assignment decision (2026-08-04, commit 8b1b386) pinning the five gate reviewers +
orchestrator to Fable 5 and assigning the other 19 agent definitions
`model: claude-opus-4-8` + `effort: high` — the producer agent type used for M0-T121
(backend-engineer) is inside that 19-agent set; verification against live evidence is the
R323 deliverable, not this note.

Forward trace: sentence 1 ("Before accepting M0-T121, record the producer's actual model
identity and the durable authority for using Opus 4.8.") → R323; sentence 2 ("Do not
interrupt the running producer.") → R324; sentence 3 ("If Opus 4.8 was used as an
unauthorized substitution or fallback rather than an explicitly permitted bounded subagent
assignment, fail closed and disposition it before acceptance.") → R325; sentence 4 ("Do not
silently treat allowlisting alone as authorization.") → R326.

Anchors: #model-identity-evidence (s1), #no-interrupt (s2), #fail-closed-disposition (s3),
#allowlist-not-authorization (s4).

---VERBATIM-BEGIN---
Before accepting M0-T121, record the producer’s actual model identity and the durable authority for using Opus 4.8. Do not interrupt the running producer. If Opus 4.8 was used as an unauthorized substitution or fallback rather than an explicitly permitted bounded subagent assignment, fail closed and disposition it before acceptance. Do not silently treat allowlisting alone as authorization.
---VERBATIM-END---
