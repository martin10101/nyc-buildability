# D-082 source 001 — owner directive, interactive chat, 2026-09-20 (verbatim)

## Owner message (verbatim)

> Go ahead and build it but take in account that the architect would also want first and
> formust the AI should calculate what's the Max? Height width and so on that it can build
> before it even looks at the way the designer is going to calculate basically the AI needs
> to do the smartest, you know, calculation first. So to measure the best approach, the
> maximum approach possible. It's a calculate with all the rules included. So it should know
> the rules, it should know that a wall's movement and stuff like that. Now if the designer
> wants to do it manually, that's an option that he can do, but the a i's answer should
> always be. The designers in terms of usability and so on

## Context (orchestrator interpretation notes; the owner text above is the authority)

Delivered 2026-09-20 ~22:55 UTC at the D-076-R003 NAMED POST-B3 OWNER-REVIEW CHECKPOINT,
immediately after: (1) M5-T060 (phase B3 slice 2, the numeric proposal editor) was ACCEPTED
as the 244th acceptance with five PASS verdicts and the checkpoint queued; (2) the
orchestrator's plain-English explanation that typing coordinates is the engine-facing
foundation and that map drawing / PDF import are the natural next stages; (3) the
orchestrator's closing question "Want me to make map-drawing the first priority of the next
phase?"; and (4) the owner's own probing question ("how does he know height or width if he
didn't design the building yet") answered with the test-guesses-cheaply framing.

Reading in-channel:
- "Go ahead and build it" = the owner PASSES the post-B3 checkpoint for the named
  continuation: the map-drawing input slice (the B3-deferred outline drawing on the lot map
  + the 4326-to-2263 bridge) — the specific thing the orchestrator proposed and the owner
  was asked to approve.
- "first and formust the AI should calculate what's the Max? Height width and so on ...
  before it even looks at the way the designer is going to calculate ... the maximum
  approach possible ... with all the rules included ... it should know the rules, it should
  know that a wall's movement and stuff like that" = a NEW, PRIORITY-LEADING capability:
  the system computes the maximum buildable envelope for the lot (height, footprint/width,
  floor area, and the shape constraints the rules impose — setbacks/yard/wall placement
  classes) under ALL applicable rules, BEFORE any designer input, as the smartest first
  answer.
- "if the designer wants to do it manually, that's an option" + "the a i's answer should
  always be. The designers in terms of usability" = the computed maximum LEADS the
  experience (the default answer the designer sees and starts from); manual entry stays
  available as an option.

Permanent-principle mapping (recorded so no packet misreads "AI calculates"): under
permanent principle 1, DETERMINISTIC CODE calculates — the owner's "AI should calculate"
is implemented as the deterministic rules/scenario engine computing the envelope with full
provenance (which rule binds each dimension), with honest COULD_NOT_CHECK-class gaps where a
rule cannot be computed; LLM/AI components may explain and assist recognition but never
invent a legal value. This directive grants the named continuation only: phase C (assisted
PDF import) and phase D stay at their own gates; the expansion/3D hold (section 2 minus the
D-040/D-076 scoped releases), Tier D / Section 20, PR #241, dependency security, and every
G0-G7 gate stand unchanged. Scenario emission/persistence remains deferred per the recorded
B3 posture unless a later owner directive releases it — the computed maximum is presented
and checked live, not silently persisted as a scenario document.
