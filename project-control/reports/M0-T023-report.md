# Agent Report

- Task ID: M0-T023
- Agent: orchestrator (lead-only implementation, per owner directive D-001)
- Worktree/branch: task/M0-T023-directive-compliance
- Requested status: awaiting_gate
- Progress percent: 85
- Governing directive: D-001 (all 89 requirements; `directive_refs: D-001:ALL`)
- Frozen base: origin/main = 1acb9b510541cfa87afff6b2dc197880e01a389b

## Work completed

Implemented the durable Owner Directive Compliance System (directive D-001) as a two-lane design:
a **provenance registry** (`project-control/directives/`) validated by a stdlib validator, and an
**enforcement lane** in `tools/project_control.py` that reads only task/gate/report records via a
shared read-only resolver. Covers all 10 architecture components and all 8 owner corrections.

## Files changed

Registry: `project-control/directives/{index.json, schema/v1/*.schema.json, BOOTSTRAP.md,
D-001-owner-directive-compliance-system/{source-001.md, source-002-amendment.md, manifest.json,
requirements.json, verification.json}}`. Tools: `tools/{directive_registry.py,
validate_directive_compliance.py, test_directive_compliance.py, project_control.py (additive),
test_project_control.py (+S9), test_directive_reminder.py, test_readonly_agent_guard.py (roster)}`.
Governance/context: `CLAUDE.md`, `.claude/skills/directive-compliance/SKILL.md`, 4 amended skills,
`.claude/agents/directive-compliance-verifier.md`, `.claude/hooks/{directive_reminder.py,
readonly_agent_guard.py (roster)}`, `.claude/rules/project-control.md`, `.claude/settings.json`,
`project-control/config.json`, `docs/templates/{AGENT_REPORT.md, GATE_REPORT.md}`,
`.github/workflows/ci.yml`, `project-control/tasks/M0-T023.json`.

## Contracts/migrations changed

No product schema/migration. Control-plane: `config.json` gains `directive_compliance_regime`
(version 1.0, effective 2026-07-23). Migration is regime-gated (explicit `directive_regime_version`
stamp), grandfathering all pre-regime tasks; accepted/canceled tasks immutable.

## Acceptance scenarios created

See `project-control/tasks/M0-T023.json` (AS-1..AS-9): validator clean; claim requires refs;
selective citation refused; migration/no-deadlock; bounded reminder; verifier read-only; content
identity; stdlib-only; per-requirement verification.

## Requirement-to-evidence map

Full machine map: `project-control/reports/M0-T023-evidence-map.json` (all 89 D-001 requirement IDs
→ code/test evidence). Per-requirement independent verdicts are recorded in
`project-control/directives/D-001-owner-directive-compliance-system/verification.json` by the
independent `directive-compliance-verifier` (producer ≠ verifier).

## Commands and tests run

`python tools/validate_directive_compliance.py --check` (exit 0);
`python tools/test_directive_compliance.py` (29 tests OK);
`python tools/test_project_control.py` (14 groups OK incl. 4 S9);
`python tools/test_directive_reminder.py` (12 OK);
`python tools/test_readonly_agent_guard.py`, `python tools/test_agent_dispatch_guard.py` (PASS);
`python tools/context_budget_check.py` (PASS, eager ~2253/6000);
`python tools/validate_product_map.py --check` (exit 0, M0-T023 mapped).

## Expected versus actual results

All expected: validator clean over the real registry; all adversarial negatives caught; existing
control-plane + guard + budget checks unchanged and green.

## Source/API evidence

No external/time-sensitive fact required (stdlib-only, all-internal). D-001 source captured verbatim
with SHA-256 digests recorded in `manifest.json`.

## Assumptions and defaults

Producer identity is `orchestrator` (lead-only implementation authorized by D-001). Content-manifest
identity excludes the volatile `project-control/` control-plane records (registry integrity is
enforced separately by the validator). Regime effective date = capture date 2026-07-23.

## Known limitations

Cross-commit append-only of source/requirement IDs is enforced structurally (source digests +
`locked_requirement_ids` + id digest) and by independent review + git history, not by a stateless
single-commit validator. Semantic completeness of directive decomposition is independently reviewed,
not machine-proven. See the enforcement-tier statement in the PR return.

## Security and provenance impact

Reminder hook treats registry text as inert data (injection-safe), is non-blocking, and never emits a
permissionDecision. `agent_dispatch_guard.py`/`readonly_agent_guard.py` behavior and their tests are
preserved (roster append only). No secrets, no external calls, no dependencies.

## New risks/dependencies

None. No package installed; all new tooling is Python stdlib.

## Recommended next tasks

Owner review of this PR. On approval + merge: adopt `/directive-compliance` for the next substantive
directive; contract future in-regime tasks with `--directive-refs`.
