OWNER AUTHORIZATION — 2026-08-18

PR #221 is merged into main at:
5c71fe0e08c8717cc20ac232d8bd0d8a328525e1

I authorize the context-intelligence initiative to begin after the completed Codex go-live runway.

Owner decisions:

1. Capture this initiative under the next available directive ID, expected to be D-013. Verify availability before using it.
2. Approve the recommended A1/A2 split.
3. Unit A1 covers the baseline, telemetry, repository fingerprint contract, persisted per-file manifest contract, cache-generation design, task packet, tests, and rollback plan.
4. Unit A2 will implement incremental indexing and invalidation after A1 is reviewed and accepted.
5. Keep the accepted canonical-path checkout identity for the cache namespace. Add HEAD, dirty-state digest, configuration versions, and per-file content digests to the snapshot/manifest identity.
6. Require byte-identical output between incremental and clean full index generation.
7. Defer the proposed 5K–8K context tier to Unit B as an explicit amendment to the existing context-budget contract.
8. Keep the existing accepted code-graph eligibility roots for Unit A. Do not widen the repository census yet.
9. Do not modify tools/agent_supervisor/** as part of this initiative.
10. Use the verified repository gate profile and exact allowed paths determined during task capture.

This first session is bootstrap-only:

- Capture the directive.
- Create and validate the A1 task packet and dependent A2–F roadmap.
- Commit and push the bootstrap control-plane work on this non-main branch according to repository policy.
- Resolve the exact Claude executable, Codex executable, task-packet, supervisor config, and model-selection paths.
- Generate the exact PowerShell command that starts A1 through the supervised Codex–Claude loop.
- Do not implement A1 code yet.
- Stop with the marker READY_FOR_SUPERVISOR_START.
