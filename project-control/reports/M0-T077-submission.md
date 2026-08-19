# M0-T077 — Producer submission (D-020 program-wide MCP default-deny)

Producer: orchestrator (per ADR-005 the orchestrator executed every write; producers of
the review verdicts are separate read-only agents). Requested status: awaiting_gate.

## G3 rework corrections (this re-submission supersedes identity 90ea22f5)

The first G3 adversarial review returned FAIL (verbatim:
`M0-T077-review-G3.md`; gate recorded FAIL). Every required correction is in this
identity:

- **F-1 (blocking, disclosure):** the subdirectory limitation — Claude Code resolves
  project settings from the session's starting directory only, so a session started
  in `<repo>/tools` gets the full ambient connector set — is now disclosed in
  `docs/MCP_DEFAULT_DENY_POLICY.md` (Honest enforcement boundary) and
  `M0-T077-fresh-session-proof.md` (Runs F/G, committed re-reproduction; §5
  corrected — the prior "sessions launched elsewhere" sentence overclaimed), with
  the supervisor-root mitigation noted and the smallest owner-gated next step
  recorded (owner-installed managed settings; explicitly not performed here).
- **F-2 (major):** validator invariant p9 — `model` must be a string,
  `fallbackModel` a list, `permissions.defaultMode` a proven enum member — because a
  schema-invalid shape makes Claude Code silently discard the ENTIRE settings file.
  Three regressions added.
- **F-3 (minor):** p7 hook preservation now requires the full
  `.claude/hooks/<script>` path inside an actual registered hook command (the
  review's echo-decoy now fails); the remaining string-level residual is documented
  in the validator itself.
- **F-4 (minor):** `allowed_paths` amended (+ recorded progress message) to include
  the standard control-CLI submission artifact `project-control/reports/M0-T077.json`.
- **F-5 (minor):** this re-submission freezes a single corrected identity; gates are
  recorded at live HEAD stamps per the CLI's fail-closed content-identity rule.
- **F-6 (minor):** the ci.yml comment no longer claims merge-blocking; it states the
  steps fail the control-plane job and that branch protection is a pre-existing
  repository setting this task does not change.

## What changed (exact files and why)

| File | Change | Why |
|---|---|---|
| `.claude/settings.json` | +19 lines / 0 deleted, purely additive merge of six policy entries (5 MCP keys + the deny-first `permissions.deny: ["mcp__*"]` rule) | The repository-level default-deny policy itself (D-020-R020..R024) |
| `tools/validate_mcp_policy.py` | new (stdlib, ~310 lines) | Fail-closed durable validation: exact policy-key values, merge preservation, and a whole-file shape assertion (p1-p9) (R029) |
| `tools/test_mcp_policy.py` | new (35 tests) | Removal/weakening regressions for the validator incl. the G3 bypass fixtures and re-review probes 59-63 (R029) |
| `.github/workflows/ci.yml` | +10 lines: two steps in the existing control-plane job | Runs the validator + tests on every push/PR so weakening fails that job visibly (R029; merge-gating is a branch-protection setting this task does not change); no other workflow/test touched |
| `docs/MCP_DEFAULT_DENY_POLICY.md` | new | The rule, per-key mechanism, inventory summary, future narrow-authorization path, honest boundary (R028) |
| `project-control/directives/D-020-program-wide-mcp-default-deny/*` | new | Verbatim capture + 34-requirement decomposition + pending verification stub (R005) |
| `project-control/directives/index.json` | +1 entry | Registry activation of D-020 |
| `project-control/tasks/M0-T077.json`, `state.json`, `gates/M0-T077-G0.json` | lifecycle | Task packet with frozen contract, G0 PASS, claim (R006-R008) |
| `project-control/reports/M0-T077-*.md` | new | G0 readiness, MCP audit, fresh-session proof, supervisor compatibility, this submission |

## Self-check results (producer, G2-class; independent gates still required)

- `python tools/validate_mcp_policy.py --check` → exit 0
- `python tools/test_mcp_policy.py` → 35/35 OK

## G5 correction (2026-08-19, after the G5 PASS-with-required-correction verdict)

- **G5 F-1 (blocking, disclosure):** per-process MCP resolution and Agent-tool
  subagent inheritance are now disclosed in the policy doc's enforcement boundary
  and the fresh-session proof §5 — a session started outside a worktree root
  (including an orchestrator session at the user-profile directory) carries the
  ambient connectors through its whole agent tree; the two sentences that narrowed
  the residual to "a HUMAN starting a session one level down" are corrected; the
  operational rule (start orchestrator/interactive sessions from a repository
  worktree root) is recorded alongside the owner-gated managed-settings close-out.
  The enforcement blob `dd11cd79…` did not change.
- **G5 F-2 (minor):** validator/test counts in this report refreshed to the shipped
  310-line validator and 35-test suite; the PR body was refreshed the same way.
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
