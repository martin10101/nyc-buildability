# M0-T132 — G2 producer self-check (orchestrator-captured)

Producer: `orchestrator-admission-runner`. Recorded by the orchestrator. **This is a producer
self-check (G2); it does not satisfy an independent gate.** Frozen identity: see the commit that
bundles this report (branch `control/D-024-fable-codex-loop`).

## 1. What changed (the 2.1.252 admission delta)
- **New measured fixtures at 2.1.252** (bounded no-write probes; old 2_1_251 pack kept append-only):
  - `capability_probe_live_2026-09-01_m0t132_2_1_252.json` — `python -m tools.agent_supervisor.capability_probe`; `claude --help` sha256 **UNCHANGED** `83af8a9a7edc`, flags/codex identical, no FAILED rows; only the version string moved (`2.1.251`→`2.1.252`).
  - `hook_event_catalog_2_1_252.json` — official docs (`code.claude.com/docs/en/hooks`, re-fetched 2026-09-01): **same 33 events** as 2.1.251, no drift; the +2 vs 2.1.220 baseline (PreModelSwitch/PostModelSwitch) carries unchanged.
  - `native_runtime_detection_2026-09-01_m0t132.json` — `native_runtime.detect_native_capabilities()`; flags/verbs/`background_host_ready`/gaps identical to 2.1.251.
  - `shell_routing_2026-09-01_m0t132_2_1_252.json` — bounded routing probe at the SAME installed `claude.exe` (`cli_identity e713c5a6`), measured on the approved worker model **`claude-opus-4-8`** (Fable 5 under its seven-day cap; opus-4-8 is the model the loop runs under — D-024 R220/R221/R447/R448). Verdict **`native_preferred`**, 3 native tool uses, 0 shell, no worker file write. Reproducible via `project-control/reports/M0-T132-routing-capture.py`.
- **Re-pointed consumers:** `event_drift.py` `CATALOG_FIXTURE_PATH` → 2_1_252 (the only manifest-tracked change; fixtures + `tools/test_*.py` are outside the manifest root). Test pointers/assertions updated in `test_agent_supervisor_event_bus.py`, `_capability_probe.py`, `_native_adapter.py`, `_routing_probe.py`.

## 2. Teeth (green + removal-sensitive)
| Pack | Result |
|---|---|
| Golden certification pack (`test_agent_supervisor_golden_run.py`) | **42 passed** (30.09s) |
| Four re-pointed packs (event_bus, capability_probe, native_adapter, routing_probe) | **150 passed** (7.96s) |
| Affected packs (recovery_probes, process, claude_runner_env, operator_channel, bounded_mode, start_reentry) | **291 passed, 1 skipped** (138.09s) |
| WHOLE supervisor suite (`tools/test_agent_supervisor_*.py`, one process) | **3,043 passed, 2 skipped, 0 failed** (3,045 collected; 628s) |

**Baseline reconciliation (freeze rule, exact):** M0-T130 recert baseline 3,039 passed / 2 skipped
(3,041 collected) → M0-T131 added 4 test nodes (reviewer stdin contract) = 3,045 collected, and
M0-T131 was accepted showing **3,040 passed / 2 skipped / 3 FAILED** — the 3 failures being EXACTLY
the CLI-drift live teeth (`capability_probe::test_live_reprobe_claude_version_matches_fixture`,
`event_bus::test_s8_live_version_matches_catalog_fixture`,
`native_adapter::test_live_detection_matches_committed_fixture`) stuck on
`'2.1.252 (Claude Code)' == '2.1.251 (Claude Code)'` (the un-admitted drift; M0-T131 could not
recert, R431). **This M0-T132 admission RESOLVES all three**: 3,040 + 3 = **3,043 passed, 0 failed**,
same 3,045 collected, 2 skipped. No test removed, no unexplained drift; my changes add 0 nodes.

Removal-sensitivity proven inline during development: re-pointing `FIXTURE_PATH` to the new 2_1_252
routing fixture made `test_the_committed_package_fixture_matches_the_installed_version` RED until its
probe version was moved 2.1.251→2.1.252 (the tooth bites version drift); the live version teeth
(S8 event catalog, capability re-probe, native detection) match the installed 2.1.252 and would go
RED at any other installed version.

## 3. Control-plane teeth
- `ruff check` on all touched files: **All checks passed** (exit 0).
- `modularity_check.py --check`: **exit 0** (only pre-existing warns on files this task did not touch; `event_drift.py` not flagged).
- `supervisor_command_doc_check.py`: **12 commands checked, 0 failures** (exit 0).
- Registry validator (`validate_directive_compliance.py --check`): re-run after the DCV writes the M0-T132 row (recorded at the gate seam).

## 4. Scope + preservation
- Writes confined to packet `allowed_paths` (event_drift.py, four 2_1_252 fixtures, four fixture-consuming test files, the two reports, the routing-capture script). No `.claude/**`, no control CLIs, no journal writes.
- Journal HALTED and untouched (the CLI-identity repin is a per-launch act on the owner-typed start via `--repin-cli-identity`, R285 precedent — NOT done here). wt-m0t107/wt-m0t109, budgets, owner-touch, PR #241 preserved.
