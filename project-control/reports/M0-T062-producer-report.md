# M0-T062 — Producer report (governance; orchestrator-produced)

**Task:** Directive-compliance follow-up hygiene — (a) drain the now-inert `M0-T056` entry from
`validate_directive_compliance.py::_EMPTY_IDENTITY_GRANDFATHERED`; (b) add O1 regression tests
asserting `path_free_opt_in` fails closed on empty-string, whitespace-only, and non-string
`path_free_justification`.

**Directive-compliance:** in-regime, `D-001:ALL`. Applicable D-001 requirement set derives EMPTY at
this identity (D-001 rows scope to the D-001 regime tasks, chiefly M0-T023, not to every in-regime
packet — M0-T057/M2-T014/M0-T033 precedent). Independent DCV records the empty-set row (verifier ≠
producer). Substance is the G3 code-review + control-plane-verifier review + the required `control-plane`
CI check.

**Producer:** orchestrator (matches the M0-T057 precedent for a governance edit to the same two files,
worktree `.claude/worktrees/session15-acc`). Reviewers are independent: `code-reviewer` (G3) and
`control-plane-verifier` (integrity + DCV row).

## Change (a) — drain inert M0-T056 grandfather entry

`tools/validate_directive_compliance.py`: removed `"M0-T056"` from `_EMPTY_IDENTITY_GRANDFATHERED`
(now `M0-T026, M0-T032, M0-T054, M3-T002..T005`) and updated the comment to record the drain.

**Why safe (provable):** the c17 empty-identity guard only consults the grandfather set on the branch
where a task's `allowed_paths` resolve to ZERO tracked files at HEAD (`if entries or cp_entries or
opted_in: continue` precedes the membership test). M0-T056's packet now carries 7 real allowed_paths,
all tracked at HEAD:
```
tools/agent_supervisor/worker_turnover.py      TRACKED
tools/agent_supervisor/turnover_controller.py  TRACKED
tools/agent_supervisor/turnover_adapters.py    TRACKED
tools/agent_supervisor/model_turnover.py        TRACKED
tools/agent_supervisor/loop.py                  TRACKED
tools/agent_supervisor/cli.py                   TRACKED
tools/test_agent_supervisor_model_turnover.py   TRACKED
```
So M0-T056 resolves NON-EMPTY and never reaches the membership test — the entry was inert
(control-plane-verifier flagged the stale membership). Draining it changes no behavior for M0-T056 and
leaves c17 to fail closed on M0-T056 live if its paths were ever emptied. This mirrors the session-16
M0-T055 drain. `sorted(_EMPTY_IDENTITY_GRANDFATHERED)[0]` stays `M0-T026` (M0-T056 was never the min),
so the grandfather test's fixture selection is unchanged.

## Change (b) — O1 fail-closed regression tests

`tools/test_directive_compliance.py`: added three tests next to the existing marker-semantics tests —
`test_empty_string_justification_is_refused`, `test_whitespace_only_justification_is_refused`,
`test_non_string_justification_is_refused` (covers int/0/bool/None/list/dict). These assert the
EXISTING behavior: `path_free_opt_in` refuses (returns `(False, <err naming path_free_justification>)`)
for every non-usable justification shape when the marker is `True`. Code already fails closed via
`not isinstance(just, str) or not just.strip()`; this is pure regression coverage, no production change.

## Self-check evidence

- Targeted subset (all `path_free`/`grandfather`/`optin`/`empty_identity`/`justification` tests):
  **18 passed** (was 15 before the +3 O1 tests). Full `tools/test_directive_compliance.py` re-run for
  the gate (see G2 self-check).
- `python tools/validate_directive_compliance.py --check` → **exit 0** (registry still valid after the drain).
- Required CI `control-plane` job runs BOTH `validate_directive_compliance.py --check` and
  `test_directive_compliance.py` on the PR — independent merge-gating verification of both changes.
- No production/runtime code path changed; `additionalProperties` on the task packet is untouched.
