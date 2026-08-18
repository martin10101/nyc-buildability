# M0-T066 Unit C G0 readiness — versioned deterministic subsystem/ontology resolver

Recorded by the orchestrator (G0 administrative). Branch
`task/M0-T066-subsystem-resolver`, stacked on accepted Unit B (M0-T065) merged to
main (merge commit 1d159a8).

## Checks (6/6 PASS)
1. **Packet complete** — objective, gates G0/G3/G4/G5, reviewers, 9 allowed_paths,
   21 forbidden_paths, 6 acceptance scenarios (AS-1..AS-6), named output
   deliverables, documented_test_commands.
2. **Governing directive active** — D-013 (rows applicable to Unit C: closed
   vocabulary R008, no-LLM structural decisions R009, honest graph kinds R018,
   version binding R028/R044, sequencing R043, derived parents R045, two-pass
   R046) + D-001; validator run at claim.
3. **Dependencies accepted** — M0-T065 (Unit B) accepted and merged to main
   (PR #232, 1d159a8); A1/A2 index modules (`repo_index_incremental`,
   `code_graph/query`) consumed strictly read-only (all listed forbidden).
4. **Scope resolvable** — a NEW versioned mapping file whose subsystem ids ARE
   existing repo path prefixes (closed vocabulary = existing paths, satisfying
   R008 by construction), a deterministic resolver (ordered longest-prefix match,
   fail-closed load, RESOLVER_VERSION + map digest export for R028/R044 binding),
   deterministic entity existence validation against the authoritative
   project-control indexes (task/requirement/directive/milestone), and the R046
   two-pass extract→resolve API with machine-readable unresolved_links. No memory
   digests are implemented (that is Unit D, sequenced after this unit per R043).
5. **Modularity path** — three new focused modules (map JSON, resolver, entity
   validation) each well under the 600-SLOC warn line; no existing module grows;
   `tools/modularity_baseline.json` untouched.
6. **No concurrent overlap** — Unit C creates only new files plus its own reports
   and one new doc; no other open task touches these paths.

Conclusion: backlog → ready for claim by the orchestrator.
