# M0-T101 — G2 self-check (producer: orchestrator)

**Frozen content commit:** `4e894af` (validator shape + tests + report). 2026-08-26 UTC.

| Check | Result |
|---|---|
| RED (pre-fix, recorded) | `test_mcp_policy.py` 5 failed / 32 passed; live `--check` → `p9 unknown settings key 'statusLine'` |
| GREEN `pytest tools/test_mcp_policy.py -q` | **42 passed / 0 failed** |
| Live `python tools/validate_mcp_policy.py --check` | **EXIT=0** |
| Mutation teeth | wrong type / swapped command / extra key each assert a `p9` error; pin-vs-committed-file drift test |
| `ruff check` both touched files | clean |
| Diff surface | exactly the 3 allowed paths; `.claude/settings.json` untouched; no MCP rule weakened (p1–p10 unchanged except the one added shape) |
| gitleaks pre-commit | no leaks found (both commits) |
| Modularity | no new file; validator grows ~20 lines (well under thresholds) |

Non-duties: no dependency change; no supervisor-tree change (freeze rule not triggered by this
task); accepted M0-T100/M0-T099 artifacts untouched.

**G2 verdict: PASS — ready for independent G5 + DCV at frozen content `4e894af`.**
