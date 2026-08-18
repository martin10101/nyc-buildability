# M0-T070 — Producer report (G2 self-check evidence)

Producer: orchestrator (session 2026-08-18). Branch
`task/M0-T070-supervisor-authority-repair`, worktree `wt-m0t070`, base
`de2f224a7db16405edfc0e2f2f0902f5164819a0` (tip of
`control/context-intelligence-init`). Directive regime: `D-001:ALL; D-014:ALL`
(resolver-verified: no other directive applicable to this scope).

Qualifying evidence (supervisor-freeze §2, cited here and in the commit):
**reproduced defect + inability to complete an authorized product task** —
run_M0_T063_A1 fail-closed stop, documented with audit/journal citations in
`M0-T070-incident-evidence.md`.

## Files changed (implementation)

| file | change |
|---|---|
| `tools/agent_supervisor/policy.py` | + `DOCUMENTED_TEST_COMMANDS_KEY`, bounds, closed character profile, and `validate_documented_test_commands` (deterministic, fail-closed; AS-1/AS-3). No classification rule changed; `_auto_test_command`, `_shape_matches`, tiers, and `POLICY_VERSION` untouched. |
| `tools/agent_supervisor/schemas/task_packet_commands.schema.json` | NEW — machine-readable contract for the canonical field; lockstep with the validator asserted by test (AS-1). |
| `tools/agent_supervisor/cli.py` | + `production_task_authority` (THE production authority constructor, loads validated packet commands — AS-2); `_run_loop` now builds authority only through it; `cmd_status` reconciles queued asks against approval-record state read-only (`open_asks` vs new `resolved_asks`; AS-8). Imports: `APPROVAL_PREFIX`, `STATUS_PENDING`, `validate_documented_test_commands`, `Mapping`. |
| `tools/agent_supervisor/broker.py` | `revoke_all` now durably resolves each revoked request's `ask_<request_id>` row (`resolve_ask`), preserving it as history (AS-8). |
| `tools/agent_supervisor/durable_state.py` | + `DurableJournal.resolve_ask` — the first and only writer of `queued_asks.answered_at_utc`; UPDATE-only, never DELETE. |
| `tools/agent_supervisor/fixtures/m0_t063_documented_test_command.json` | NEW — the exact M0-T063 baseline/test-command need + 13 adversarial variants (AS-10). Deliberately NOT in `replay_corpus/` (the replay suite pins exactly 8 cases). |
| `tools/test_agent_supervisor_command_authority.py` | NEW — 29 tests covering AS-1..AS-10 including the AST production-wiring pin (AS-7), the executable BEFORE-reproduction, and the pre-fix-journal read-only status test. |

Control plane: D-014 capture (`project-control/directives/D-014-…/`, 39
requirements, source SHA-256
`7628740e1a19ee1cf7424c42d1af00c4feeb2c9fbf4f2ad804bf101bb59596f6`),
M0-T070 packet + G0 + this report set.

## Design decisions

- **Fail closed at load, not silently empty:** a malformed
  `documented_test_commands` raises `PolicyError` and refuses the run.
  Silently dropping entries would reproduce defect A behind a validator.
- **Absence confers nothing:** no key → `()` → the documented-test tier stays
  unreachable for that task. No default, no fallback list.
- **Existing tier, not a new one:** AS-4 authorization flows through the
  unmodified S4.1 `_auto_test_command`/`_shape_matches`; the repair only makes
  the packet's commands reach it. No new AUTO path exists (AS-6).
- **Two-layer defect-B fix:** `revoke_all` resolves rows durably going
  forward; `cmd_status` also reconciles at read time so the untouchable live
  A1 journal (D-014 prohibition 3) reports truthfully. Loop-origin asks
  (rotation pause, model-chain stop) have no approval record and stay open.
- **History preserved:** ask rows are UPDATEd with an answer, never deleted;
  approval records keep `revoked_reason`; the audit chain is untouched.

## Self-check results (local, Python 3.11.9 / pytest 8.4.2)

| suite | result |
|---|---|
| `tools/test_agent_supervisor_command_authority.py` (new) | **29 passed** (0.87 s) |
| full supervisor: `pytest tools/test_agent_supervisor_*.py` | **1557 passed, 2 skipped, 0 failed** (118 s) — M0-T039 freeze baseline (≥1165, 0 failures) re-established |
| `tools/test_project_control.py` + `tools/test_directive_compliance.py` + `tools/test_directive_reminder.py` | **155 passed, 0 failed** (661 s) |
| `python tools/validate_directive_compliance.py --check` | registry VALID (D-001..D-014) |
| `ruff check` on the five changed/added Python files | 4 findings, **all pre-existing on base cli.py** (unused imports); zero new findings from this diff |

## D-014 evidence map (task-bound requirements)

| requirement | evidence |
|---|---|
| R009/R010/R012 (one corrective task/worktree/branch; incident evidence; repair only in corrective worktree) | this packet, `wt-m0t070`, branch above; `M0-T070-incident-evidence.md`; `git status` clean outside scope |
| R013/R014/R015 (tests+gates; commit/push/PR; stop before merge) | suite table above; gate reports `M0-T070-G2/G3/G5-*`; PR opened and left unmerged |
| R016, R029–R036, R039 (prohibitions) | no change outside allowed_paths; A1 journal byte-identical (read-only opens only); no reset/clean/force-push in `git reflog`; no controller/config path touched; A1/M0-T063 not started |
| R017–R026 (AS-1..AS-10) | `test_agent_supervisor_command_authority.py` (29 tests, class-per-AS mapping in module docstring) + schema + fixture |
| R027 (AS-11) | suite table above |
| R028 (AS-12) | `M0-T070-before-after-evidence.md` |
| R037 (rollback) | branch/worktree removal instructions in the PR body and return report |

Independent verification (producer ≠ verifier) is owed by code-reviewer (G3),
security-reviewer (G5), and directive-compliance-verifier before any
completion claim; this report claims none.
