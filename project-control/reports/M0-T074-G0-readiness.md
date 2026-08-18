# M0-T074 G0 readiness — deterministic complexity-based model routing

Recorded by the orchestrator (G0 administrative class) at branch
`task/M0-T074-model-routing`, base `6bfc60a` (stacked on task/M0-T073-modularity-enforcement).

## Checks (6/6 PASS)

1. **Packet completeness — PASS.** Objective (D-017-R114..R123), business reason, gates
   (G0/G2/G3/G4/G5), four reviewers, allowed/forbidden paths, risks populated in
   `project-control/tasks/M0-T074.json`.
2. **Governing directive active — PASS.** D-017 rows R114..R123 bind M0-T074; validator
   exit 0; capture independently CONFIRMed.
3. **Scope resolvable — PASS.** `.github/workflows/ci.yml` tracked at HEAD (c17);
   `tools/model_routing.py`, `tools/test_model_routing.py`,
   `tools/model_routing_corpus.json`, `docs/MODEL_ROUTING_POLICY.md`, and the two
   report files are declared additions.
4. **Sequencing/overlap — PASS with protocol.** M0-T073 and M0-T074 both edit
   `ci.yml`; to honor the no-concurrent-overlap rule this branch is STACKED on
   task/M0-T073-modularity-enforcement (sequential, single writer), its ci.yml change
   is one additive `model-routing` job appended after the `modularity` job, and its PR
   merges only after M0-T073's.
5. **Protected-boundary posture — PASS.** The router READS the protected controller
   config allowlist through the frozen supervisor's own loader (import only;
   `tools/agent_supervisor/` is a forbidden write path); it never writes config.toml
   or model_selection.toml; single-Claude honesty (D-017-R118) is a hard requirement:
   the active allowlist (claude: claude-opus-4-8 only) means adaptive Claude routing
   is REPORTED UNAVAILABLE, never simulated.
6. **Dependencies clear — PASS.** No ledger dependencies; operational sequencing after
   M0-T073 via the stacked branch.

Conclusion: task moves backlog → ready for claim by the orchestrator.
