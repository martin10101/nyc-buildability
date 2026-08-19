# M0-T077 — Producer submission (D-020 program-wide MCP default-deny)

Producer: orchestrator (per ADR-005 the orchestrator executed every write; producers of
the review verdicts are separate read-only agents). Requested status: awaiting_gate.

## What changed (exact files and why)

| File | Change | Why |
|---|---|---|
| `.claude/settings.json` | +24 lines, purely additive merge of 5 MCP keys + 1 deny-first `permissions.deny: ["mcp__*"]` rule | The repository-level default-deny policy itself (D-020-R020..R024) |
| `tools/validate_mcp_policy.py` | new (stdlib, ~165 lines) | Fail-closed durable validation of every policy invariant (p1-p8) incl. merge-preservation (R029) |
| `tools/test_mcp_policy.py` | new (22 tests) | Removal/weakening regressions for the validator (R029) |
| `.github/workflows/ci.yml` | +8 lines: two steps in the existing required control-plane job | Runs the validator + tests on every push/PR so weakening blocks merge (R029); no other workflow/test touched |
| `docs/MCP_DEFAULT_DENY_POLICY.md` | new | The rule, per-key mechanism, inventory summary, future narrow-authorization path, honest boundary (R028) |
| `project-control/directives/D-020-program-wide-mcp-default-deny/*` | new | Verbatim capture + 34-requirement decomposition + pending verification stub (R005) |
| `project-control/directives/index.json` | +1 entry | Registry activation of D-020 |
| `project-control/tasks/M0-T077.json`, `state.json`, `gates/M0-T077-G0.json` | lifecycle | Task packet with frozen contract, G0 PASS, claim (R006-R008) |
| `project-control/reports/M0-T077-*.md` | new | G0 readiness, MCP audit, fresh-session proof, supervisor compatibility, this submission |

## Self-check results (producer, G2-class; independent gates still required)

- `python tools/validate_mcp_policy.py --check` → exit 0
- `python tools/test_mcp_policy.py` → 22/22 OK
- `python tools/validate_directive_compliance.py --check` → exit 0 (D-020 registered)
- `python tools/modularity_check.py --check` → PASS (only pre-existing warnings on
  legacy files; both new modules are small and single-purpose)
- Control-plane suites (`test_project_control`, `test_directive_compliance`,
  `test_directive_reminder`, `test_readonly_agent_guard`, `test_agent_dispatch_guard`)
  → all exit 0 at the frozen head
- Fresh-session proofs: see `M0-T077-fresh-session-proof.md` (clean-worktree runs
  return `No MCP servers configured`; non-repo control retains all connectors; global
  digests byte-identical)

## Explicitly NOT done (honest boundary, per D-020)

- No merge of the PR (owner authorization required); no controller bundle; no
  D-013-R060 decision; no supervisor file touched; no live supervised probe (owner
  gated — see `M0-T077-supervisor-compatibility.md` for the smallest proposed
  owner-present checklist line); no global/user/account configuration modified.
- Residual honest limits are recorded in `M0-T077-fresh-session-proof.md` §5
  (repository-scope authority only; explicit interactive user action is out of scope
  of a default-deny; local-settings overrides are explicit user action, with the
  audited identifiers still deny-pinned even then).
