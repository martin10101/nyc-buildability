# D-079 source 001 — owner directive, interactive chat, 2026-09-20 (verbatim)

## Owner message (verbatim; delivered with a /session-handoff invocation mid-turn)

> Make sure in the season handle that it tells exactly for the next program where to find all the MD files for the research, for everything that needs to be, you know, added throughout the conversation. And make sure that it has the minimum amount to get started the continue the loops. Keep the loops running in between season handles even when I clear it so the loops continue running. And I want the new season to um, to start up right away being able to jump right in. I don't want them to need to do a million checks because we're technically already, you know, um, everything is going good so it doesn't need to run rechecks. You should like just let him know where things are up to and he should right away you know, continue on.

## Context (orchestrator interpretation notes; the owner text above is the authority)

Delivered 2026-09-20 ~07:05 UTC (~03:05 New York) as a `/session-handoff` invocation with
spoken-style instructions ("season handle/handles" = session handoff(s); "the next
program" = the successor session). Read in-channel, four requirements on HANDOFF
DISCIPLINE from this point forward:

1. The handoff document must carry an EXACT FILE MAP — where every markdown/knowledge/
   record file added through the work lives (research briefs, recon reports, backlog,
   working knowledge, gate/wave records, directives), so the successor never hunts.
2. The handoff must state the MINIMUM needed to continue the loops (per-lane: packet,
   worktree, launcher, run-id, state) — lean, not exhaustive.
3. Loops KEEP RUNNING across handoffs and /clear: the supervisors are detached OS
   processes independent of the chat session; a handoff never stops them, and the
   successor must not disturb live lanes (no audit-writing verbs against a live loop —
   the standing rule) — it picks up monitoring and seam work around them.
4. Fast resume: the successor starts working IMMEDIATELY from the handoff's state
   summary — no full re-verification sweep when the handoff attests a clean, current
   state. The successor still runs the cheap identity check (cwd/branch/HEAD) and
   TRUSTS the handoff for the rest unless something contradicts it; full reconciliation
   is reserved for crash/forced turnover or visible contradiction (the D-070
   crash-fallback), not the planned path.

This ADJUSTS the D-070 finished-seam preference: a planned handoff may now leave lanes
LIVE (the owner explicitly wants continuity over seam-first), with the successor
verifying identity only and continuing. Gates, holds, Tier D stops, review independence,
and the ledger's authority are unchanged; the ledger still wins over handoff prose.
