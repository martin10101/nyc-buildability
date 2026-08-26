# M0-T101 — MCP-policy validator: strict `statusLine` shape (D-027 follow-up)

**Producer:** orchestrator · 2026-08-26 UTC · branch `control/D-024-fable-codex-loop`
**Class:** defect repair (post-acceptance discovery from accepted M0-T100; new bounded task —
accepted work untouched).

## 1. Defect (reproduced RED before the fix)

During the M0-T090 supervisor-freeze baseline run, `tools/test_mcp_policy.py` failed 5 tests
(`test_committed_settings_pass`, `test_extra_deny_rules_alongside_wildcard_pass`,
`test_intact_fixture_passes_in_temp_dir`, `test_main_check_exit_zero`,
`test_valid_default_mode_passes`; chunk figure 5 failed / 2523 passed / 3 skipped), and the live
check reproduced independently:

```
$ python tools/validate_mcp_policy.py --check
MCP default-deny policy INVALID (1 error(s)):
  - p9 unknown settings key 'statusLine' (fail closed: ... extend KNOWN_KEY_SHAPES in the
    same reviewed change that adds a key)
```

Root cause: M0-T100 (owner-authorized D-027 wiring) added `statusLine` to
`.claude/settings.json`; the D-020 validator's p9 whole-file shape check fails closed on any
unrecognized key, and its docstring prescribes exactly this repair path ("adding a genuinely
new setting to the checked-in file therefore requires extending KNOWN_KEY_SHAPES in the same
reviewed change — intended visibility"). The wiring change missed that same-change duty; this
reviewed task restores it.

## 2. Fix (strict, fail-closed, exact-identifier discipline)

`tools/validate_mcp_policy.py`:

- `EXPECTED_STATUSLINE_COMMAND` — the exact D-027-authorized command string
  (`python -m tools.agent_supervisor.telemetry_statusline --journal
  .claude/telemetry/statusline_journal.jsonl`). The statusLine command executes on every TUI
  refresh tick, so a swapped/mistyped command is an execution vector; pinning mirrors the
  validator's existing exact-identifier discipline (`DENIED_SERVER_NAMES`, hook commands).
- `_is_statusline_shape` — exactly `{"type": "command", "command": <the pinned string>}`.
  Extra keys (even legitimate Claude options like `refreshInterval`), another `type`, or any
  other command fail closed and require their own reviewed validator change. ABSENCE of the
  whole key remains valid: activation stays owner-optional; this validator enforces MCP
  default-deny plus settings-shape integrity, not telemetry presence.
- One `KNOWN_KEY_SHAPES` entry wiring the shape in.

**No MCP rule weakened:** deny lists, allowlist emptiness, hooks, permissions, and every other
p1–p10 check are byte-identical; the diff adds one shape helper + one table entry only.

## 3. Tests (GREEN after; mutation-style)

New in `tools/test_mcp_policy.py` (§ statusLine shape):

| Test | Proves |
|---|---|
| `test_statusline_absent_still_passes` | key removal stays valid (owner-optional activation) |
| `test_statusline_wrong_type_fails_closed` | string instead of object → p9 |
| `test_statusline_different_command_fails_closed` | swapped command (`powershell -c calc`) → p9 |
| `test_statusline_extra_key_fails_closed` | added `refreshInterval` → p9 (closed shape) |
| `test_statusline_command_pinned_to_committed_settings` | pin and committed file cannot drift silently |

Results: `pytest tools/test_mcp_policy.py -q` → **42 passed / 0 failed** (was 32 passed /
5 failed); live `python tools/validate_mcp_policy.py --check` → EXIT=0; `ruff check` both
files → clean. The five pre-fix failures are the red half of the red/green proof; the four
fail-closed cases fail on any permissive mutant of the new shape.

## 4. Scope and conduct

Diff surface: exactly the packet's allowed paths (`tools/validate_mcp_policy.py`,
`tools/test_mcp_policy.py`, this report). Accepted M0-T100/M0-T099 artifacts untouched;
`.claude/settings.json` untouched by this task; no dependency added; no supervisor-tree change
(freeze rule not triggered by THIS task). Citations `D-020:ALL;D-027:ALL` (evaluate ok,
applicable set empty — rows bind their original tasks; empty-set rows recorded at DCV).
Unblocks the M0-T090 full-suite baseline duty.
