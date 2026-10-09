# M0-T136 G0 readiness record (administrative; recorded at review time)

Recorded by the orchestrator/verifier session on 2026-09-02, at the independent
review wave (the gate was not recorded at claim time; this record documents the
readiness facts verified from durable evidence, per ADR-005 administrative-gate
semantics). Nothing here is an independent review; G3/G4/DCV are recorded
separately.

## Readiness facts (verified)

1. **Authorization.** D-024 Amendment 40 (source-040-amendment.md, R516) authorizes
   exactly ONE bounded Tranche-B producer workflow; R517 lifts R513 for it only.
   The packet's business_reason cites the supervisor-freeze qualifying evidence
   rows (R516/R558/R562/R567/R581/R586).
2. **Packet.** project-control/tasks/M0-T136.json is tightly scoped: named
   requirement range (R515-R598), explicit allowed_paths and forbidden_paths,
   ten acceptance scenarios (AS-B0-1..AS-NEG), required gates G0/G2/G3/G4,
   producer `mrl-tranche-b-producer`, three named reviewer agents, dependency
   M0-T134 (accepted).
3. **Bootstrap Gate 0 (D-024-R125..R128).** Verifier session start: primary cwd
   IS the worktree root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`
   (`git rev-parse --show-toplevel`), and `/mcp` is empty (no MCP tools loaded
   in-session; validate_mcp_policy rc 0).
4. **Branch identity.** `candidate/D-024-mrl-option-b` from exact base `6f5d12a6`
   (= origin/control/D-024-fable-codex-loop, ancestor of HEAD), LOCAL ONLY (no
   upstream, no remote candidate ref); archive `stabilization/D-024-mrl`
   unchanged at `76c4edff`.
5. **In-regime binding.** directive_refs D-024:ALL; derived applicable set = 82
   rows (R516 + R518..R598), equal to the submit-time record in
   project-control/reports/M0-T136.json; content identity `edd514d2...` stable
   from submit through review.

Result: PASS (administrative readiness).
