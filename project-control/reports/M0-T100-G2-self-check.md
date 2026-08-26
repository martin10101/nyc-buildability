# M0-T100 — G2 self-check (producer: orchestrator)

**Frozen content commit:** `a0b945e` (wiring + activation report). 2026-08-26 UTC.

## 1. Deliverables present (packet outputs)

- `.gitignore` telemetry-ignore rule — in `a0b945e`; `git check-ignore -v` matches
  `.claude/telemetry/statusline_sidecar.json` against the new rule.
- `.claude/settings.json` statusLine block — in `a0b945e`; exact §4 command + documented
  `--journal` option; diff is 4 added lines, no other key touched.
- `project-control/reports/M0-T100-statusline-activation.md` — in `a0b945e`; contains the live
  two-output proof, masking scan, precedence check, prohibition attestations.

## 2. Executable checks (all run at the wired tree, foreground)

| Check | Result |
|---|---|
| `pytest tools/test_agent_supervisor_statusline_handler.py -q` | **23 passed / 0 failed** (0.31 s) |
| Exact wired command on REAL captured payload (scratch sidecar/journal) | exit 0; row + sidecar from one invocation |
| Live TUI pickup (running session) | sidecar + 33-record journal written 05:52–05:54Z, ticking |
| Sensitive scans over live sidecar + full journal | 0 hits (`MLFLL`/`Users`/`C:\`/`C--`/`ghp_`/`sk-`/`Bearer`) |
| Global `~/.claude/settings.json` integrity | untouched: sha256 `32c6fb00…6afa7`, mtime 04:29:57Z < first write 05:48Z |
| `python tools/validate_directive_compliance.py --check` | **EXIT=0** (completed 2026-08-26 ~05:57Z, after D-027 capture + M0-T100 claim) |
| gitleaks pre-commit on both commits | no leaks found |

## 3. Non-duties confirmed

- No production code changed → no modularity/ruff duties; supervisor tree untouched → freeze
  rule not triggered, no suite-baseline re-establishment (M0-T099 baseline 2595/3/0 stands).
- No dependencies added (dependency-security policy not engaged).
- Accepted M0-T099 artifacts untouched (identity preservation, D-027-R002).
- Campaign record `D-024-fable-codex-loop.json` untouched (NEXT remains M0-T090).

## 4. Known limitations (declared, not hidden)

- The live TUI's displayed row is not screen-capturable from this harness; the report proves the
  row via (a) the single-invocation demo on the REAL payload and (b) deterministic
  reconstruction from the live journal tail record (same pure formatting function).
- The runtime sidecar/journal retain session/transcript UUIDs by design (monitoring key) —
  explicitly dispositioned in activation report §4; local-only, gitignored, never committed.

**G2 self-check verdict: PASS — ready for independent G5 + directive-compliance verification at
frozen content `a0b945e`.**
