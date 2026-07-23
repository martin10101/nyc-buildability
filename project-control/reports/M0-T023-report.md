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
`locked_requirement_ids` + id digest + `requirements_content_digest_sha256`) and by independent
review + git history, not by a stateless single-commit validator. Semantic completeness of directive
decomposition is independently reviewed, not machine-proven. Additional documented limitations:
- **F4 (multi-task-per-directive):** `verification.json` carries a single `reviewed_manifest_sha256`;
  a directive cited by two tasks with different `allowed_paths` would hit a content-identity mismatch
  at accept. Not reachable for D-001 (one task, M0-T023); a limitation for future multi-task directives.
- **F7 (`.gitattributes` scope):** the registry is LF-pinned; the broader content-manifest'd work
  product (`CLAUDE.md`, `tools/`, `.claude/`, `.github/`) is not eol-normalized. Acceptance runs on the
  single orchestrator machine, so submit/accept content-manifests are self-consistent; cross-platform
  re-derivation is the documented residual.
- **D2 (GitHub CI):** local suites are reproduced green; the GitHub Actions conclusion for the frozen
  head is captured separately via `gh` (local vs remote CI stated separately in the return).

## Independent review and corrections

The frozen-head review found: G4-control PASS, G5-security PASS (2 Low: L1 resolver path-containment,
L2 reminder read-cap), G4-directive PASS ×2 (all 89 requirements SATISFIED), **G3-code FAIL** (F1 a c15
check that would break CI on M0-T023 acceptance; F2 a rule-doc sentence contradicting `accept()`; F3
the requirements.json body outside the frozen identity). All were corrected before re-review: c15 now
flags only retroactive/non-consensual binding (+test); the two-lane wording now accurately states
`accept()` reads `verification.json` as blocking evidence; a `requirements_content_digest_sha256`
locks the matrix body (+test); L1/L2/F5/F6 applied; real R001/R002 regressions added; `required_harness`
relabeled to real runnable files. This is the directive-compliance protocol operating on its own
implementation (FAIL → correct → re-verify).

## Security and provenance impact

Reminder hook treats registry text as inert data (injection-safe), is non-blocking, and never emits a
permissionDecision. `agent_dispatch_guard.py`/`readonly_agent_guard.py` behavior and their tests are
preserved (roster append only). No secrets, no external calls, no dependencies.

## New risks/dependencies

None. No package installed; all new tooling is Python stdlib.

## Recommended next tasks

Owner review of this PR. On approval + merge: adopt `/directive-compliance` for the next substantive
directive; contract future in-regime tasks with `--directive-refs`.
