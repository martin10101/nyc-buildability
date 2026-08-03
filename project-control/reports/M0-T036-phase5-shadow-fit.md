# M0-T036 Phase 5 — §17 fit assessment for the shadow-pilot lifecycle (D-007-R553)

- Recorded: 2026-08-03T23:10+00:00, orchestrator
- Authority: owner message 2026-08-03 (D-007 amendment 2, source-003-amendment.md, R552–R555)
- Criteria applied: D-007-R331 (observe a real workflow; forward nothing; count would-be stops),
  D-007-R473 / packet AS-6 (at least one real controlled-task lifecycle; ≤2 would-be synchronous
  stops excluding activation; every excess stop dispositioned; the run ends AT the merge/acceptance
  gate, never past it), D-007-R505 (one controlled live task in shadow mode, owner-touch count vs
  budget).

## Selected lifecycle: M0-T035 acceptance run

M0-T035 (`awaiting_gate`; G0/G2/G3/G5 all PASS at the frozen reviewed SHA) has exactly one
lifecycle act remaining: the acceptance run. The owner's Part 2 message names it a natural
candidate "if it qualifies — the §17 fit rules, not convenience."

### Fit against each criterion

1. **Real workflow (R331):** PASS — a genuine pending ledger lifecycle with real consequences
   (acceptance record, checkpoint, dependent unlocks), not a synthetic exercise.
2. **Completes a real controlled-task lifecycle (R473/AS-6):** PASS — the observed run carries
   M0-T035 to lifecycle completion (acceptance), the ledger's terminal producer-side state.
3. **Ends AT the merge/acceptance gate, never past it (AS-6):** STRUCTURALLY EXACT — the
   remaining span of M0-T035 *is* the approach to the acceptance gate. The shadow run observes
   acceptance preparation (re-verify the four gate verdicts against the frozen reviewed SHA,
   assemble acceptance evidence) and ends at the acceptance decision; the actual acceptance is
   then executed by the orchestrator through `tools/project_control.py` as normal, and any merge
   queues for the owner (D-004-R721). The supervisor never acts past the gate.
4. **Owner-touch budget ≤2 (R473):** EXPECTED WITHIN BUDGET — preparation acts are read-only
   (AUTO tier); the expected would-be synchronous stops are the terminal acceptance-gate stop
   (the boundary where the run ends) and at most one ASK during verification. Actual counts are
   measured by the run and reported in the decision packet, with every excess stop dispositioned.

### Honest limitation

The observed span exercises mostly read-only classification plus the terminal gate stop; it does
not exercise live write-path tiers (worktree edits, standing-grant test execution, grant-(b) push).
Those surfaces are covered by the Phase 4 §15 matrices and the 8/8 historical replay corpus, and
§17 requires one real lifecycle, not maximal surface. The alternative — routing the pending
secret-scan fixture-fix unit through the pilot instead — was rejected because it would couple
Part 1's CI-green requirement (R548) to pilot launch prerequisites that carry owner-touch setup
(controller checkout), inverting the owner's written Part 1 → Part 2 order. That is a §17 fit
judgment, not convenience: M0-T035 satisfies every stated criterion; the fixture-fix unit would
violate the directed sequencing.

### Launch prerequisites (per `start --mode shadow`; nothing defaulted)

- Named canonical Claude executable and Codex executable (Phase 0 baseline).
- Controller config + model_selection.toml (to be authored; doctor validates on supply).
- **Controller location = dedicated read-only checkout outside every Claude-writable path
  (D-007 fixed decision)** — creating this checkout is outside the session's writable scope and
  therefore requires an owner-side step (or an owner-approved permission grant). Surfaced in the
  Phase 5 return; the pilot cannot launch until it exists.
- Task packet input for the loop naming the M0-T035 acceptance-run unit.

Sequencing note (D-007-R554): the pilot may run once prerequisites exist; the **decision packet**
is assembled only after the Part 1 CI PR is merged and green.
