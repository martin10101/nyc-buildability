---
name: cli-admission-recert-mechanics
description: How to run a Claude CLI admission + controller recertification (R287) from a candidate worktree without touching the live controller (M0-T159 / M0-T132 precedent)
metadata:
  type: project
---

Running an R287 CLI-admission + recertification lane (e.g. M0-T159 admitting Claude Code
2.1.281 on a worktree cut from the CERTIFIED controller commit).

**Why:** the certified controller pins ONE exact `claude.exe` identity; a CLI update (D-085)
fails every lane launch (start_gate `cli_capability_manifest` step ANDs `shell_routing`, which
is digest-keyed) until the new version is admitted. Runbook `docs/CONTROLLER_UPDATE_RUNBOOK.md`
§13 orders it: recapture fixtures -> full recert -> ONLY THEN `--repin-cli-identity`.

**How to apply (all from the candidate worktree, never the live controller):**
- Four fixtures + their instruments: `python -m tools.agent_supervisor.capability_probe --out`;
  `native_runtime.detect_native_capabilities()` + `build_detection_fixture(caps, task=...)`;
  hook catalog via curl of `code.claude.com/docs/en/hooks` (diff events vs the prior catalog —
  33 events is the current set; `TaskCreate` is a mechanism ref, not an event); shell-routing via
  an adapted copy of the M0-T132 routing-capture script (needs `PYTHONPATH=<worktree>` as a bare
  script) on the approved worker model (exact id `claude-opus-5-5`), `journal=None`.
- `record-manifest` and `verify-controller` operate on **PACKAGE_ROOT = the running module's
  tree**, so running them from the worktree records/verifies the CANDIDATE tree + the external
  `config.toml` — never the live install. Use `--out <temp>` (fail-closed refuses out==config or
  out named config.toml/model_selection.toml). Manifest covers `tools/agent_supervisor/*.py`
  (event_drift.py in-scope); fixtures + `tools/test_*.py` are OUTSIDE the manifest root.
- `doctor` (non-live): pass `--runtime-base <temp>` so its fresh empty journal lands in temp,
  NOT under `%LOCALAPPDATA%\NYCBuildabilitySupervisor` (safety). Overall PASS needs a resolvable
  runtime dir; a temp base gives a trivially-valid empty journal. `approved_models` check
  confirms the config binding (e.g. lists claude-opus-5-5 after the B-025 allowlist edit).
- Baseline reconciliation: run the WHOLE `tools/test_agent_supervisor_*.py` suite FIRST at the
  pristine tree — the CLI-drift live teeth (capability_probe `test_live_reprobe_...`, event_bus
  `test_s8_live_version_...`, native_adapter `test_live_detection_...`) are RED (installed-new vs
  fixture-old); the admission flips exactly those to GREEN, same collected count, 0 net nodes.
  Repurpose the capability "current fixture" test in place (don't add/remove nodes).
- Lane journals ( `%LOCALAPPDATA%\NYCBuildabilitySupervisor\<key>\supervisor_journal.sqlite3`)
  MUST stay byte-identical: record size+mtime before AND after every probe. See
  [[env-producer-sandbox-no-exec]] for worktree-edit / EOL discipline.
