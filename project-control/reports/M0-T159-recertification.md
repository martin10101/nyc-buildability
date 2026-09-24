# M0-T159 — 2.1.281 admission + one recertification at the frozen candidate (B-026 remedy)

Producer: `backend-engineer`, in the isolation worktree `wt-m0t159` (branch
`task/M0-T159-cli-2-1-281-admission`), cut from the CERTIFIED controller commit
`a5886dab`. B-026 remedy per `docs/CONTROLLER_UPDATE_RUNBOOK.md` section 13 (R287 ordered
admission) and the M0-T132 (2.1.251->2.1.252) precedent. All commands recorded with an
explicit cwd. The stored activation-manifest overwrite, the controller re-point to the
admitted commit, and the per-lane `--repin-cli-identity` stay OWNER-TYPED commissioning
steps (section 5 below) — presented, never run.

## 1. The frozen candidate identity
| Anchor | Value |
|---|---|
| Material commit | the ONE commit bundling this unit (branch `task/M0-T159-cli-2-1-281-admission`; base `a5886dab`) |
| Provider CLI (ADMITTED) | Claude Code **2.1.281**, executable digest **`92af58066c9cad103ff93c0b8dcf0599e96e26feea5bee45561d06ba579f4a2c`** (`sha256_head+size`), on-disk size **240,767,648 B**, at `C:\Users\MLFLL\.local\bin\claude.exe`; old **`e713c5a6…` (2.1.252)** retired |
| Codex CLI | **codex-cli 0.153.4 UNCHANGED** (the D-032 admission carries; only claude moved) |
| `tools/agent_supervisor` manifest | **147 files**, digest **`55dc71350b9f6b0a57e8e4121c62a9d2a4fe8914eea8bcd1ca4acdddbcec74b9`** (from the TEMP-recorded candidate manifest); the ONE manifest-tracked change is `event_drift.py` (digest `e85c775c3aa7769680d908bfbe8110cf87e20859556038507b9d655e4eb1f30d`, the catalog re-point) — fixtures + `tools/test_*.py` are OUTSIDE the manifest root |
| External config bound | `config.toml` LF-normalized digest **`34f4fe90a1ecc2f4544b4ca7ff33fd08af0923cdf3c96d8c462acb8fe7b2a62e`** (the CURRENT B-025-edited config at `C:\Program Files\SupervisorConfig\config.toml`; its `[approved_models]` now lists `claude-opus-5-5`) |

## 2. Test evidence at the frozen candidate (one process, worktree root)
| Pack | Result |
|---|---|
| Golden certification pack (`test_agent_supervisor_golden_run.py`) | **42 passed** (159.88s) |
| Four re-pointed packs (event_bus, capability_probe, native_adapter, routing_probe) | **150 passed** (45.23s) |
| WHOLE supervisor suite (`python -m pytest tools/test_agent_supervisor_*.py -q`, one process, cwd = worktree root) | **3,662 passed, 2 skipped, 0 failed** (3,664 collected; 1,194.97s) |

**Baseline reconciliation (freeze rule, exact).** The a5886dab tree's OWN count, measured
first (installed CLI already at 2.1.281, fixtures still at 2.1.252): **3 failed, 3659
passed, 2 skipped (3664 collected), 939.62s**. The 3 failures were EXACTLY the CLI-drift
live teeth stuck on `'2.1.281 (Claude Code)' == '2.1.252 (Claude Code)'`:
`capability_probe::test_live_reprobe_claude_version_matches_fixture`,
`event_bus::test_s8_live_version_matches_catalog_fixture`,
`native_adapter::test_live_detection_matches_committed_fixture`. **This admission RESOLVES
all three**: 3659 + 3 = **3,662** passed, 0 failed, same 3664 collected, 2 skipped. No
test removed; the capability current-fixture test was repurposed in place (net 0 nodes).

## 3. R282-style admission pass-list (2.1.281)
| Item | Evidence |
|---|---|
| Fixtures | Four measured 2.1.281 fixtures — `capability_probe_live_2026-09-24_m0t159_2_1_281.json`, `hook_event_catalog_2_1_281.json` (33 events, docs re-fetched 2026-09-24, no drift), `native_runtime_detection_2026-09-24_m0t159.json`, `shell_routing_2026-09-24_m0t159_2_1_281.json`; the 2_1_252 / m0t132 / d032 pack kept append-only |
| Drift teeth | The version teeth **GREEN at 2.1.281** and removal-sensitive (section 4); S8/capability/native live teeth match the installed 2.1.281 |
| Live probes | capability + native probes measured live (bounded `--version`/`--help`, no provider); **shell-routing measured live at digest `92af5806…` on the approved worker model `claude-opus-5-5`** — verdict `native_preferred`, 3 native / 0 shell, 0 worker file write, 3 provider calls, deny-everything handler |
| Golden suites | **42 passed** (159.88s) at this identity |
| Manifest binding | 147-file manifest `55dc71350b…` recorded to a TEMP path, external `config.toml` bound, round-trip verified; **`verify-controller` PASS**; **non-live `doctor` overall PASS (41 checks, 0 failed)** |
| Admission scope | ONLY `event_drift.py` (catalog re-point) is manifest-tracked; four fixtures + four fixture-consuming test files are outside the manifest root |

**ADMITTED (candidate): Claude Code `2.1.281` (executable digest `92af5806…`; codex-cli
0.153.4 unchanged).** The one-time `--repin-cli-identity` on the next certified start
completes the admission at the journal level (a per-launch owner act, deferred — section 5).

## 4. Removal-sensitivity (AS-3), recorded
The baseline run above IS a recorded removal-sensitivity demonstration: with the pointers at
2.1.252 and the installed CLI at 2.1.281, the 3 version teeth are RED. Additionally, an
explicit focused run pointed the catalog tooth back at `hook_event_catalog_2_1_252.json`
and ran the two S8 teeth:
```
FAILED tools/test_agent_supervisor_event_bus.py::test_s8_live_version_matches_catalog_fixture
FAILED tools/test_agent_supervisor_event_bus.py::test_s8_catalog_fixture_valid_and_masked
2 failed in 0.85s
```
(the second on `assert 'M0-T132' == 'M0-T159'`). The pointer was restored to
`hook_event_catalog_2_1_281.json`; the same two teeth then passed (`2 passed in 0.25s`).

## 5. Deferred to owner-typed commissioning (NOT done here)
These run against the LIVE controller and are owner/orchestrator commissioning acts,
presented per runbook sections 4->5->6->7->13.4 and the M0-T132 section-5 precedent. `<admitted-commit>`
= this unit's integrated commit sha (filled by the orchestrator at acceptance).

**(a) Re-point / install the controller from the admitted candidate** (runbook §4; the
installer binds an immutable full-SHA via `tools/controller_update/source_binding.json`,
which the orchestrator updates to `<admitted-commit>` under review, then):
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\controller_update\update_controller_from_candidate.ps1 -Phase install
```

**(b) Re-record the ACTIVATION manifest** binding the current config (runbook §5), then
verify (runbook §6):
```powershell
Set-Location C:\SupervisorController
python -m tools.agent_supervisor record-manifest `
  --config "C:\Program Files\SupervisorConfig\config.toml" `
  --out "$env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json"
python -m tools.agent_supervisor verify-controller `
  --manifest "$env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json" `
  --config "C:\Program Files\SupervisorConfig\config.toml"
```

**(c) Clear lane-1 recovery, then relaunch each lane once with `--repin-cli-identity`**
(runbook §13 step 4 — repin LAST, never first; per the MRL launch runbook, staggered). The
repin verifies the new executable digest `92af5806…` at PREFLIGHT:
```powershell
python -m tools.agent_supervisor clear-recovery --checkout <lane-1 checkout>
python -m tools.agent_supervisor start --launch-manifest <lane launch_manifest.json> --checkout <lane checkout> --mode <authorized-mode> --max-cycles 1 --repin-cli-identity
```

## 6. Preservation (safety)
Every lane journal is byte-untouched — before AND after all probes (size+mtime identical):
`9aca7075…`=17,080,320/1790236111, `cfdedc11…`=5,689,344/1790144402,
`9df5e3ba…`=3,526,656/1790143705. No supervisor verb was run against the live controller;
`record-manifest`/`doctor` wrote only under `%TEMP%\m0t159\` (doctor `--runtime-base` a temp
dir, so its fresh empty journal landed in temp, not `%LOCALAPPDATA%`). No write outside the
worktree allowed_paths and the temp dir. `C:\SupervisorController*`, `wt-controller-src`,
`C:\Program Files\SupervisorConfig`, and `%LOCALAPPDATA%\NYCBuildabilitySupervisor` were
read-only throughout.

## 7. Verdict
Recertification: **PASS at the one frozen candidate** (manifest `55dc71350b…`; admitted CLI
`2.1.281`/`92af5806…`; config `34f4fe90…`), subject to the independent G3/G4 + DCV wave. Any
supervisor/operator-channel change after this point re-invalidates certification and
re-triggers the recert.
