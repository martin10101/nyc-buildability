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
| `capability_probe_live_2026-09-24_m0t159_2_1_281.json` | `python -m tools.agent_supervisor.capability_probe --out …` | **claude_flags / codex_flags / interactive_only / python_runtime ALL identical**; only `claude_version` (2.1.252->2.1.281) and the raw `claude --help` sha256 (`83af8a9a…`->`2569232a…`) moved. Usage first-line + every probed flag token still `supported` -> **no capability drift** (slightly stronger than the 2.1.252 bump, whose help sha was identical). codex probes all unchanged. |
| `hook_event_catalog_2_1_281.json` | official docs re-fetched with curl (`code.claude.com/docs/en/hooks`, HTTP 200, 2,900,678 B) | **Same 33 events as 2.1.252**; all 33 present, none missing; no new hook-event token (the only PascalCase-near-hook candidates were HTML/tool/verb noise, e.g. `TaskCreate` is the *mechanism* "a task is created via TaskCreate", not an event). **No hook-event drift.** |
| `native_runtime_detection_2026-09-24_m0t159.json` | `native_runtime.detect_native_capabilities()` (bounded --version/--help) | flags/verbs/`background_host_ready=True`/`background_gaps=()` **identical**; only `claude_version` moved. **Version-only drift.** |
| `shell_routing_2026-09-24_m0t159_2_1_281.json` | `project-control/reports/M0-T159-routing-capture.py` (adapted M0-T132 instrument) on **`claude-opus-5-5`** | Measured LIVE, deny-everything handler: verdict **`native_preferred`**, native 3 / shell 0, 0 worker file write, 3 provider calls; `cli_identity` = the installed 2.1.281 digest `92af5806…`. Reproduces the M0-T120/M0-T132 verdict. |

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
- **Limitation (out of scope, disclosed):** several `mrl_*` modules/tests carry measured-live
  behavioral facts pinned to "2.1.252" (dontAsk read-only execution; `--json-schema` Draft-7;
  provider-schema exit-1). Those are a DIFFERENT measured-behavior set, not part of the R287
  four-fixture pack, and were NOT re-measured on 2.1.281 (they are mocked logic tests +
  historical comments, not live teeth — the recert confirms none is a live tooth). If the
  owner wants those behaviors re-attested at 2.1.281 that is a separate task.
- Routing-capture script needs `PYTHONPATH=<worktree>` when run as a bare script (the M0-T132
  invocation ran from a checkout with the root already importable).
