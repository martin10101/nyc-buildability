# M0-T196 producer report (orchestrator; governance; owner D-094 R117, question L1)

## What changed
- New always-loaded rule `.claude/rules/living-files.md` (no paths frontmatter): every file Claude keeps up to date,
  what goes in it, and the moment it must be updated (the questionnaire; the question-and-answer log and its private copy;
  the directive registry; the research records, the zoning-rule review register and the owner research queue; the
  discovery backlog; the master plan; the program and coding lessons and working knowledge; the session notes; the
  handoff and the session brief).
- `.claude/rules/PROGRAM_KNOWLEDGE.md`: removed the one-liners the map now carries: the backlog duty (D-069), the owner
  research queue (D-050), the owner-invoked handoff (D-090 R941), the planned handoff (D-070, D-094 R109-R113); the
  header's append duty is folded into the map; the loop-run pointer is shortened to one line. Nothing else changed.
- `.claude/session-handoff-profile.md`: a living-files checklist, one item per map line, confirmed before HANDOFF READY.
- Outside the repository: the orchestrator's memory index line for the questionnaire shortened (107 bytes) to point at
  the map.

## Session-start size (the owner was told it would not grow)
- Eager project instructions before (claim head): `---- eager total: 44767B  515L  ~11135 tok`
- After: `---- eager total: 44872B  516L  ~11163 tok  (no cap: owner D-093-R074)`
- Difference: +105 bytes in the eager project instructions; the memory index line shortened by 107 bytes
  (outside the repository) brings the whole session start to -2 bytes: it does not grow.

## Where each removed line went (nothing dropped)
- Backlog (D-069): the map's DISCOVERY_BACKLOG line, now with "and replan" and "never duplicating ledger/blockers".
- Owner research (D-050 R002/R005/R006): the map's research line, incl. commit+push same step, seam line + PushNotification.
- Owner-invoked handoff (D-090 R941) and planned handoff (D-070): short form in the map's handoff line; the two original
  lines word for word in `.claude/session-handoff-profile.md` ("Handoff rules carried here"), read at every handoff.
- Append duty in the PROGRAM_KNOWLEDGE header: the map's lessons line.
- Loop-run pointer: shortened, same target (`docs/WORKING_KNOWLEDGE.md`).

## Checks
- `python3 tools/context_budget_check.py` exit 0 (no retired/superseded section; no duplicate).
- Validator and lane coverage: run by the seam (see the seam log).
- Owner-worded texts (CLAUDE.md, the D-093 rule, the owner's working guidance) are untouched (not in the allowed paths).
