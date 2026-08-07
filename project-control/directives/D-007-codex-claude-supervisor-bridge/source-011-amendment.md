# D-007 amendment 10 — owner message (verbatim capture)

- Captured: 2026-08-04T18:00:00+00:00 (approx; session-local)
- Channel: owner chat message (this session)
- Base SHA at capture: cb9a9995da213f33d70e467773d595b3dfea0b57 (origin/main); task branch 58d036f
- Amends: source-010-amendment.md (probe decision + V1.2 contract/dispatch)

## The owner message

Decision on the probe: the deny-leg verification satisfies the R739/R582 gate — the allow leg has no code path until the broker is wired (G3 V-1), so requiring it first would be circular, and surfacing that rather than fabricating an allow result was correct. Contract and dispatch the V1.2 unit now with scope: the model-identity discipline as bound, context-threshold rotation as bound (R743–R745), and the approval-broker wiring (G3 V-1). Acceptance evidence must include, all preserved verbatim: one live allow round-trip through the wired broker in which an in-scope tool is permitted and actually executes (closing QA gap 1), one live-exercised rotation (closing QA gap 4), and one live-detected model mismatch (may be induced for the test). All live exercises use synthetic probe units only — shadow-only remains in force and nothing forwards to any real task. The supervised single-forward rehearsal remains NOT authorized; it returns to me after the V1.2 delta re-gate. The Fable-5-pinned reviews — the V1.2 delta re-gate and the held G2 wave — run after I say my window has reset. Capture this message verbatim.
