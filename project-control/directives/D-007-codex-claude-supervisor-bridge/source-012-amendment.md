# D-007 amendment 11 — owner message (verbatim capture)

- Captured: 2026-08-04T19:05:00+00:00 (approx; session-local)
- Channel: owner chat message (this session)
- Base SHA at capture: cb9a9995da213f33d70e467773d595b3dfea0b57 (origin/main); task branch b16d502
- Amends: source-011-amendment.md (V1.2 contract/dispatch + live-exercise authorization)
- Cross-registry note: the same owner message is captured verbatim as D-004 amendment 26
  (D-004-agent-teams-runtime-adoption/source-026-amendment.md); model-governance requirement IDs
  live there (D-004-R746..R750), supervisor-unit and sequencing requirement IDs live here
  (D-007-R597..R602). Item (3) M0-T034 is decomposed on the D-004 side (dispatch policy scope).

## The owner message

Resume from docs/SESSION_HANDOFF.md — verify the live repo state yourself before acting, per standing practice. Then execute this evening authorization, unattended, stopping at every owner gate as always. (1) Model-policy correction, folded into the V1.2 unit with its own test before the freeze: when the orchestrator-role pinned model (Fable 5) is unavailable because quota is exhausted, the supervisor relaunches explicitly on claude-opus-4-8, records the substitution as a first-class event, and returns to Fable 5 at the next seam once available — never silent, orchestrator-role only; reviewer pins unchanged, reviews wait for Fable 5 rather than fall back. (2) My Fable 5 window is live now — the wait-for-reset hold is lifted: after the three live exercises complete and the SHA freezes, dispatch the V1.2 delta re-gate AND the held G2 wave immediately, Fable-5-pinned as recorded. (3) Product work: dispatch M0-T034 drive-to-submit as a normal unit under standard gates; it queues at submit for my return; nothing merges, nothing is accepted, no owner gate closes in my absence. (4) The supervised single-forward rehearsal and all activation remain NOT authORIZED; shadow-only stays in force for real work. Refresh SESSION_HANDOFF once tonight's returns land. Capture this message verbatim.
