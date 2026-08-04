# D-004 amendment 24 — owner message (verbatim capture)

- Captured: 2026-08-04T17:05:00+00:00 (approx; session-local)
- Channel: owner chat message (this session)
- Base SHA at capture: cb9a9995da213f33d70e467773d595b3dfea0b57 (origin/main); task branch 8b1b386
- Amends: source-023-amendment.md (extends the V1.2 model-identity unit authorized by R739;
  SAME unit, not a new one)

## The owner message

V1.2 scope extension (amends the model-identity unit already authorized for after the doctor --live probe; same unit, not a new one). Add context-threshold rotation for orchestrator-role sessions: the supervisor tracks context usage from the stream; when usage crosses the owner-set threshold — set it at 400k tokens, configurable in the supervisor config — it treats this exactly like a detected downgrade: dispatch nothing new, let in-flight subagents and the current unit finish bounded, refresh SESSION_HANDOFF, rotate via the existing rotation path, relaunch pinned on Fable 5. Rotation fires only at a seam, never mid-unit. The unit's acceptance must include at least one live-exercised rotation (closing QA gap 4) and one live-detected model mismatch, both evidenced — the mismatch may be induced deliberately for the test. Capture this message verbatim.
