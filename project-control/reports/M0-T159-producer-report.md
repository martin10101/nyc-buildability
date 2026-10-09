# M0-T159 — producer report (Claude Code 2.1.281 admission + recertification; B-026 remedy)

Producer: `backend-engineer`, isolation worktree
`C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t159` (branch
`task/M0-T159-cli-2-1-281-admission`, base `a5886dab`). Evidence-status form:
[OBSERVED] = run and recorded here. Companion: `M0-T159-recertification.md` (frozen-candidate
identity, pass-list, deferred owner commissioning). Reference files, not long embeds.

## Preflight (AS-1) [OBSERVED]
- `claude --version` (cwd `wt-m0t159`) = **`2.1.281 (Claude Code)`**, exit 0.
- Executable identity via `tools/agent_supervisor/process.py::executable_identity`
  (`C:/Users/MLFLL/.local/bin/claude.exe`): digest
  **`92af58066c9cad103ff93c0b8dcf0599e96e26feea5bee45561d06ba579f4a2c`**, kind
  `sha256_head+size`, on-disk size **240,767,648 B**.
- Retired: the 2.1.252 identity **`e713c5a6c8bc71af…`** (size 217,406,624 B).
- codex-cli = **0.153.4** (unchanged; only claude moved).

## Fixture pack (AS-2) — four fixtures captured LIVE [OBSERVED]
All four written under `tools/agent_supervisor/fixtures/`; older fixtures untouched
(append-only). Each diff vs its 2.1.252 predecessor:

| Fixture | Instrument | Diff vs 2.1.252 |
|---|---|---|
| `capability_probe_live_2026-09-24_m0t159_2_1_281.json` | `python -m tools.agent_supervisor.capability_probe --out …` | **claude_flags / codex_flags / interactive_only / python_runtime ALL identical**; only `claude_version` (2.1.252->2.1.281) and the raw `claude --help` sha256 (`83af8a9a…`->`2569232a…`) moved. Usage first-line + every probed flag token still `supported` -> **no capability drift** (slightly stronger than the 2.1.252 bump, whose help sha was identical). codex probes all unchanged. [CORRECTED per M0-T159-G3 F5] One more diff, previously undisclosed: `probe_meta.claude_binaries` went from 3 entries (`[HOME]\.local\bin\claude.EXE`, `[HOME]\AppData\Roaming\npm\claude`, `[HOME]\AppData\Roaming\npm\claude.cmd`) to 1 (`[HOME]\.local\bin\claude.EXE`). Cause: the npm `claude` / `claude.cmd` shims are gone from `%APPDATA%\npm` (only `codex`, `codex.cmd`, `codex.ps1` remain; listed read-only). Benign: it removes a PATH-shadowing candidate; `codex_binaries` is unchanged. |
| `hook_event_catalog_2_1_281.json` | official docs re-fetched with curl (`code.claude.com/docs/en/hooks`, HTTP 200, 2,900,678 B) | **Same 33 events as 2.1.252**; all 33 present, none missing; no new hook-event token (the only PascalCase-near-hook candidates were HTML/tool/verb noise, e.g. `TaskCreate` is the *mechanism* "a task is created via TaskCreate", not an event). **No hook-event drift.** |
| `native_runtime_detection_2026-09-24_m0t159.json` | `native_runtime.detect_native_capabilities()` (bounded --version/--help) | flags/verbs/`background_host_ready=True`/`background_gaps=()` **identical**; only `claude_version` moved. **Version-only drift.** |
| `shell_routing_2026-09-24_m0t159_2_1_281.json` | `project-control/reports/M0-T159-routing-capture.py` (adapted M0-T132 instrument) on **`claude-opus-5-5`** | Measured LIVE, deny-everything handler: verdict **`native_preferred`**, native 3 / shell 0, 0 worker file write, 3 provider calls; `cli_identity` = the installed 2.1.281 digest `92af5806…`. Reproduces the M0-T120/M0-T132 verdict. [CORRECTED per M0-T159-G3 F5] Diff vs the M0-T132 fixture, stated in full: `assistant_events` dropped 2 -> 1 (assignment 0) and 3 -> 2 (assignment 1), which is stream granularity only; `argv_shape` differs only in `--model` (`claude-opus-4-8` -> `claude-opus-5-5`); `capture_model`, `capture_note`, `claude_version`, `claude_version_line`, `cli_identity`, `requirement` and `task` carry the new admission; `tool_use_stream`, `brokered_denials`, `routing_summary`, `provider_calls_made`, `no_worker_file_write_observed` and `error` are identical. |

Shell-routing capture model rationale: the owner switched the loop to Opus 5.5 (D-085-R004)
and asked for the lane capacity ramp (D-087-R001), so `claude-opus-5-5` is the model the
lanes run under — the correct capture model (exact id `claude-opus-5-5`). This is a
deliberate measurement, not a cap workaround. Fixture files leak-checked (no `MLFLL`, no
`:/Users/`, `[HOME]`-masked binaries).

## Teeth re-pointed + removal-sensitive (AS-3) [OBSERVED]
Re-pointed (exactly the allowed_paths): `event_drift.py` `CATALOG_FIXTURE_PATH` -> 2_1_281;
test pointers/assertions in `test_agent_supervisor_{event_bus,capability_probe,
native_adapter,routing_probe}.py`. The capability current-fixture test was repurposed in
place (`…records_codex_0_153_4…` -> `…records_claude_2_1_281…`; net 0 test nodes). `ruff
check` on all touched files: **All checks passed**. `py_compile`: OK.

Removal-sensitivity: the baseline run (pointers at 2.1.252, installed 2.1.281) had the 3
version teeth RED. Explicit focused proof — catalog pointer reverted to 2_1_252:
```
FAILED …event_bus.py::test_s8_live_version_matches_catalog_fixture
FAILED …event_bus.py::test_s8_catalog_fixture_valid_and_masked   (assert 'M0-T132' == 'M0-T159')
2 failed in 0.85s
```
Pointer restored -> `2 passed in 0.25s`. Tree restored byte-clean (git status = only intended
allowed_paths changes).

## Recertification (AS-4) [OBSERVED]
ONE run, one process, cwd = worktree root: `python -m pytest tools/test_agent_supervisor_*.py -q`.
- **Baseline (a5886dab own count, measured first):** 3 failed, 3659 passed, 2 skipped (3664
  collected), 939.62s. The 3 failures = exactly the CLI-drift live teeth.
- **Recert (frozen candidate):** **3,662 passed, 2 skipped, 0 failed** (3,664 collected), 1,194.97s
- Golden pack: **42 passed** (159.88s). Four re-pointed packs: **150 passed** (45.23s).
- Reconciliation: 3659 + 3 (teeth resolved) = 3,662 passed, 0 failed, same
  3664 collected, 2 skipped. **No test removed; net 0 nodes added.**
- `record-manifest --config "C:\Program Files\SupervisorConfig\config.toml" --out %TEMP%\m0t159\manifest\controller_manifest.json`
  (cwd worktree, PYTHONPATH=worktree): recorded **147 files**, digest **`55dc71350b9f6b0a…`**,
  binding external `config.toml`, round-trip verification passed.
- `verify-controller --manifest <temp> --config <config.toml>`: **"controller verified,
  including the external config.toml binding."**
- non-live `doctor --config <config.toml> --manifest <temp> --runtime-base %TEMP%\m0t159\runtime_base`:
  **overall PASS, 41 checks, 0 failed**. `controller_manifest`: 147 files vs `55dc71350b…` incl
  config binding. `approved_models`: `[claude-fable-5, claude-opus-4-8, claude-opus-5-5]`
  (confirms the B-025 opus-5-5 allowlist binding — the config the candidate manifest binds).
  `control_response_live_probe`: UNVERIFIED (no live call, correct for non-live).

## Safety + scope (AS-5) [OBSERVED]
- Three lane journals byte-untouched, before AND after every probe (identical size+mtime):
  `9aca7075…`=17,080,320/1790236111; `cfdedc11…`=5,689,344/1790144402;
  `9df5e3ba…`=3,526,656/1790143705.
- No supervisor verb run against the live controller; `record-manifest`/`doctor` wrote only
  under `%TEMP%\m0t159\` (doctor `--runtime-base` = temp, so its fresh empty journal landed
  in temp, NOT `%LOCALAPPDATA%`). `C:\SupervisorController*`, `wt-controller-src`,
  `C:\Program Files\SupervisorConfig`, `%LOCALAPPDATA%\NYCBuildabilitySupervisor` read-only.
- Writes confined to the packet allowed_paths (4 fixtures, event_drift.py, 4 test files, 3
  reports incl the routing-capture script). No `.claude/**`, no control CLIs, no journal writes.
- Owner-typed commissioning commands (controller re-point/install, activation-manifest
  re-record + verify, per-lane `--repin-cli-identity`) presented in `M0-T159-recertification.md`
  section 5 — NOT run.

## Deviations / discoveries
- **Deviation (disclosed):** 2.1.281's raw `claude --help` sha256 changed vs 2.1.252 (the
  2.1.252 bump had an identical help sha). The material capability surface is unchanged (every
  probed flag/verb still `supported`; usage first-line identical), so it is still a benign
  admission — recorded in the capability fixture + catalog `source` note, not hidden.
- **[CORRECTED per M0-T159-G3 F5/F6] 2.1.281 `--help` check of the flags the live launch paths
  use** (read-only, 2026-09-24; `claude --version` = `2.1.281 (Claude Code)`). The capability
  probe's 12 flags and the native detection list do not cover these, so they were checked
  directly. Re-running the probe's own capture (`capability_probe._run(['claude','--help'])`)
  gave exit 0 and `output_sha256` `2569232a…`, identical to the fixture, so the help text is
  stable since the capture. Presence in that output:
  - MRL launch-manifest path (`mrl_subagent_contract.py:426-436`, `mrl_one_shot.py:268`):
    `--restricted`, `--json-schema`, `--allowedTools`, `--disallowedTools`, `--agents`,
    `--tools`, `--settings`, `--strict-mcp-config`, `--permission-mode`: all PRESENT.
    `--permission-mode` choices: `acceptEdits`, `auto`, `bypassPermissions`, `manual`,
    `dontAsk`, `plan` (so `dontAsk` and `manual` are both still offered).
  - Legacy path (`claude_runner.build_argv`, which the lane autostart wrappers use):
    `--input-format`, `--output-format`, `--verbose`, `--model`, `--resume`: PRESENT.
    `--max-turns` has NO help line, and `--permission-prompt-tool` appears only inside the
    description of the `--permission-prompts <target>` flag (choices `host`, `none`). Both
    were still ACCEPTED live at 2.1.281: the shell-routing capture ran exactly that argv (3
    provider calls, brokered denials, verdict `native_preferred`). A help-text probe could not
    see either flag being removed; only a live run can.
  - Presence in `--help` is not live behavior: `--restricted`, `dontAsk` and `--json-schema`
    stay unexercised live at 2.1.281. This is the named residual risk in
    `M0-T159-recertification.md` 5.12, and the first lane launch is a supervised one-cycle canary.
- **Limitation (out of scope, disclosed):** several `mrl_*` modules/tests carry measured-live
  behavioral facts pinned to "2.1.252" (dontAsk read-only execution; `--json-schema` Draft-7;
  provider-schema exit-1). Those are a DIFFERENT measured-behavior set, not part of the R287
  four-fixture pack, and were NOT re-measured on 2.1.281 (they are mocked logic tests +
  historical comments, not live teeth — the recert confirms none is a live tooth). If the
  owner wants those behaviors re-attested at 2.1.281 that is a separate task.
- Routing-capture script needs `PYTHONPATH=<worktree>` when run as a bare script (the M0-T132
  invocation ran from a checkout with the root already importable).

## Correction note: G3 rework (cr-m0, PASS with required corrections F1-F3; F4/F5 folded)
[CORRECTED per M0-T159-G3 F1-F7] Documentation only. Two files changed: this report and
`M0-T159-recertification.md`. No code, fixture or test changed; the candidate `a3f24ff3` is
byte-identical under `tools/` (the tree was clean before and after every check).
- **F1:** recertification section 1 and section 5.0 now name the candidate: commit
  `a3f24ff3825c126c038f59b1ea6d2352f29d724a`, commit_tree `82432361540c3c2a11c55ffa3d6d485426cd45f7`,
  subtree `9c0b14eaa56ce32d241c77f789266035b584380c` (all three re-read with `git rev-parse`).
  They say plainly that `cfc3d22c` (subtree `11d43515…`, carrying the uncertified
  M0-T149/M0-T152 `cli.py` / `evidence.py` / `policy.py` / `gate_wave.py` changes) must not be
  the install source. They add the STOP condition (147 files, digest `55dc7135…74b9`, re-derived
  in-process from the `a3f24ff3` tree plus the live `config.toml`) and the orchestrator re-pin of
  `source_binding.json` before step 5.2.
- **F2:** section 5 is now the full ordered runbook sequence with exact commands: section 2,
  section 3 `-Phase backup` (needed: the bound 2026-09-06 backup evidence no longer matches the
  live controller in 3 files, so install would refuse `backup_stale`), the section 4
  `source_worktree_exists` refusal and the runbook's exact removal command, install, section 5,
  section 5a `-Phase verify-manifest`, section 6, section 7, section 8 (RUN, with reasons), and
  section 9.
- **F3 (new fact, changes the picture):** all three lane launchers (`autostart-launch.ps1` in
  `C:\SupervisorController`, `…2`, `…3`) start Python with working directory
  `C:\Users\MLFLL\Downloads\nyc-zoning\wt-controller-src`. That is the installer's detached
  source worktree, so every lane loads its code from there, not from its own instance copy. Lane
  tracebacks in the autostart logs confirm the path. Two consequences, both written into
  section 5: (a) re-creating `wt-controller-src` at `a3f24ff3` (install) is what moves the
  launchers onto the certified code; (b) runbook section 5a's "the source worktree may be
  removed after sections 6-8" would leave all three lanes with no code, so section 5.5 says do
  not remove it. The `C:\SupervisorController2` / `3` copies (200 files, byte-identical to
  instance 1 and to `a5886dab`; no 2.1.281 routing fixture) still get a verified robocopy
  propagation plus a bidirectional SHA-256 hash-list compare plus verify-controller, because the
  MRL-form launch in 5.11 runs with those folders as the working directory.
- **F4:** 5.11 gives per-lane `Set-Location`, `status`, `clear-recovery` (only on
  `PAUSED_RECOVERY`; lane 1 per B-026), a FRESH launch manifest drafted with the exact MRL
  runbook section 1 command, a check that it binds `2.1.281` / `946eb509…bfff1`, then `start`
  with `--repin-cli-identity` LAST. All six existing `mrl\*_launch_manifest.json` files in the
  three instances pin `2.1.252` (read-only check). The wrappers' legacy form (no launch manifest)
  is stated separately.
- **G3 condition (6):** the residual risk (`--restricted`, `dontAsk`, `--json-schema` not
  exercised live at 2.1.281) and the supervised one-cycle canary with its audit watch-list and
  stop rule are in recertification 5.12.
- **F5 / F6:** disclosed above (capability `probe_meta.claude_binaries` 3 -> 1; routing
  `assistant_events` 2 -> 1 and 3 -> 2) and the `--help` flag-presence record.
- **F7:** wording fixed. The fixtures are inside the manifest root but match none of its covered
  patterns.
- **For the orchestrator (discovery-backlog candidates, not acted on here):** (1) G3 F7: the
  routing drift tooth is version-hardcoded, and `fixtures/*.json` are not manifest-covered
  although the start gate trusts `fixtures/shell_routing_*.json`. (2) G3 F4 side note:
  `MRL_LAUNCH_RUNBOOK.md` lines 71-75 and 90 say `--repin-cli-identity` cures
  `claude_version_mismatch`; in code that refusal comes only from the launch-manifest pin, while
  the repin cures `provider_cli_drift`. (3) The lanes execute from the installer's transient
  source worktree, not the installed controller, and runbook section 5a permits removing it.
  (4) At 2.1.281, `--max-turns` and `--permission-prompt-tool` (legacy lane argv) are missing
  from `--help` as their own flags but still accepted live. (5) Runbook section 1's expected
  `config.toml` hashes are stale since B-025. (6) Requested follow-up (G3 condition 6): add the
  MRL flags to the capability probe and re-measure the M0-T140..M0-T142 canary facts at 2.1.281.

Requested status: awaiting_gate (a re-freeze and a delta attestation from cr-m0 are needed).
