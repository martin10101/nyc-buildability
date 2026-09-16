# D-063 work allocation

| Task | Dependency | Producer | Branch / isolated worktree | Write scope | Shared writes | Gates | Integration order |
|---|---|---|---|---|---|---|---|
| M5-T031 | M5-T030 accepted | feedback_frontend_producer / frontend-engineer | task/M5-T031-ui / m5t031-ui | Exact frontend files, tests and producer report in task packet | None | G0–G5 + independent DCV | Second |
| M4-T022 | M4-T009 accepted | feedback_source_producer / official-source-researcher | task/M4-T022-validation / m4t022-validation | Exact audit helper, tests, fixtures and reports in task packet | None | G0–G4 + independent DCV | First |

Both worktrees started at dd22b95. Producer scopes prohibit backend/rule, contract, configuration and dependency changes, control-plane mutations and git operations. The orchestrator alone integrates and records evidence. Stop conditions are a concrete scope conflict, missing credentials, or a decision requiring legal or production authority; routine source research and engineering checks do not require another architect benchmark sheet. Reviewers receive bounded packets at frozen content identities and return reports without edits.

Frontend delivery uses the owner's existing instruction to build, push and show the site live on candidate/D-024-mrl-option-b. This does not authorize backend deployment, service configuration changes, new infrastructure, legal rule publication, changes to main, or merging PR 241. The existing Render service is manual-deploy; delivery follows successful required checks and review.

### V2 bounded test-readiness allocation

The frontend producer may additionally edit `apps/web/src/components/address/__tests__/lot-outline-map.test.tsx` solely to wait for rendered map readiness before firing the existing mocked error event. Root inspected the failing log and asynchronous setup. All existing fallback assertions stay intact; no production map change or timeout increase is authorized. This is a frontend test within the existing user scope.
