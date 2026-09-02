# M0-T141 — frozen corrected controller candidate (D-024 Amendment 44, R678)

The Draft-7 provider-schema hotfix supersedes the M0-T136 Tranche-B candidate as the
controller install source. The installer's printed identity must equal this record.

| Identity | Value |
|---|---|
| Frozen corrected candidate commit | `2245de74232947be919b555fd061ba8a6e6438de` |
| Commit tree | `63119a9a362be69799fc705d4f4acbb5d0f3030d` |
| `tools/agent_supervisor` subtree tree | `edf026b375089a59b3134378204682c4db473f29` |
| Supersedes (install source only) | `1489879e1f6787a9d53ed74db4524b24039e03a2` (subtree `79af11a2`) |
| Branch | `candidate/D-024-mrl-option-b` (local only; nothing pushed, R520/R521) |

## Delta from the superseded candidate (the ONLY subtree changes)

- `tools/agent_supervisor/mrl_provider_schema.py` — NEW: Draft-7 provider-schema
  projection (deep copy; explicit `http://json-schema.org/draft-07/schema#`
  declaration; fail-closed same-meaning keyword allowlist; ContractError on any
  unknown / newer-draft-only / draft-divergent keyword).
- `tools/agent_supervisor/mrl_one_shot.py` — the single `--json-schema` call site
  serializes the projection instead of the canonical schema. No other change.

`tools/agent_supervisor/schemas/` (including the canonical
`worker_result.schema.json`) is byte-identical to the superseded candidate; the
controller-side enforcer (`mrl_worker_result.py`) is untouched (R666).

## Suite baseline re-established at this identity (supervisor-freeze §4)

- Full supervisor suite `python -m pytest tools/test_agent_supervisor*.py`:
  **3566 passed, 2 skipped, 0 failed** (raw exit 0, 2026-09-02, this worktree).
- Focused files: `test_agent_supervisor_mrl_provider_schema.py` +
  `test_agent_supervisor_mrl_one_shot.py`: 89 passed.
- Mutation proof (AS-DS-6): M1 wiring-reverted (canonical serialized directly) →
  argv test FAILS with the 2020-12-vs-draft-07 diff; module mutants
  M2 (keep canonical declaration), M3 (unknown keyword passes), M4 (refused table
  ignored), M5 (shallow copy), M6 (array-form items accepted) — **all DETECTED**;
  module restored byte-identical; suite re-run green.
- `ruff check` on the four changed files: clean. `modularity_check --check`:
  0 failures. `validate_directive_compliance.py --check`: exit 0.

## Source binding rebind (this reviewed commit)

`tools/controller_update/source_binding.json` pins the three SHAs above and adds the
two changed modules to `required_modules`; `docs/CONTROLLER_UPDATE_RUNBOOK.md` §4 and
`tools/controller_update/ps_tests/test_runbook_parse.ps1` `$pinnedSha` carry the same
commit (the binding's checked consistency teeth). Long hashes live only here and in
the binding contract — never retyped into owner commands (R636).

Qualifying evidence (supervisor-freeze AD-093, cited in packet + commit): reproduced
defect + provider CLI drift + D-024-R664..R683 — preserved failed-run record
`project-control/reports/M0-T141-canary-b502-schema-failure-evidence.md`
(provider-contact count zero).
