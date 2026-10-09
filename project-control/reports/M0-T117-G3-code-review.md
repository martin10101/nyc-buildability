<!-- Saved VERBATIM by the orchestrator from the G3 code-reviewer agent-return channel
     (transport entity-decoding only). Review head 0324342, material identity fa16560. -->

I have completed my independent analysis. All evidence is gathered and the key completeness gap is mechanically proven. Here is my G3 gate report.

---

# G3 Independent Code Review — M0-T117

**Task:** M0-T117 — D-024 Amendment 13 unit Q: forced `DISABLE_AUTOUPDATER=1` on controller-launched Claude workers + admission-event discipline
**Reviewed identity:** control-branch head `0324342`, material-identity commit `fa16560`
**Checkout:** `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24` (branch `control/D-024-fable-codex-loop`)
**Reviewer:** independent, read-only. No files modified; no write-producing commands run.
**Directive regime:** `directive_refs = D-024 ALL`; R278/R280/R286/R287/R288 are the governing requirements.

## Commands run (read-only)

1. `git show --stat fa16560` → 8 files, +598/-3 (matches the packet).
2. `git diff 4083132 fa16560 -- tools/agent_supervisor/process.py tools/agent_supervisor/claude_runner.py tools/test_agent_supervisor_process.py` (+ doc/report diffs).
3. `git show fa16560:tools/test_agent_supervisor_claude_runner_env.py`.
4. Grep `Popen|subprocess.run|subprocess.call|os.spawn|check_output|check_call` across `tools/agent_supervisor/**`.
5. Read `preflight.py`, `native_runtime.py`, `capability_probe.py`, `turnover_adapters.py`, `turnover_controller.py`, `codex_channel.py`, `cli.py` launch sites, `process.py`.
6. `python -m pytest tools/test_agent_supervisor_claude_runner_env.py tools/test_agent_supervisor_process.py -q`
   → **`38 passed, 1 skipped in 9.41s`** (independently reproduces the report's GREEN claim exactly).

---

## Findings

### 1. INFO — Injection correctness at the two covered seams is sound (item 1)
`process.py:225` `claude_child_env()` calls `minimal_env(extra, allowlist)` then `env.update(FORCED_CLAUDE_CHILD_ENV)` **last** (`process.py:243`). Because the forced pair is applied after both the allowlist filter and the `extra_env` merge, `DISABLE_AUTOUPDATER=1` is guaranteed regardless of parent env, allowlist membership, or a conflicting `extra_env["DISABLE_AUTOUPDATER"]` value. AS-6 "forced pair wins" is a defensible fail-closed choice and is honestly documented (`process.py:233-247`). `minimal_env` (`process.py:200-210`) is byte-for-byte unchanged, so every other caller's contract is preserved. Both `claude_runner.py` seams were correctly switched: worker `run_unit` env at `claude_runner.py:1102` and probe `probe_model_launch` env at `claude_runner.py:1548` (Popen at 1126 / 1557). **Correct for what it covers.**

### 2. MAJOR — Uncovered live Claude launch: preflight `control_response_round_trip` / `doctor --live` (item 2) — REQUIRED
`tools/agent_supervisor/preflight.py:126` launches the **real canonical claude executable** via `subprocess.Popen` with `env=minimal_env()` (`preflight.py:136`) — **not** `claude_child_env()`. The caller `cli.py:1314-1319` resolves `executable = ... or resolve_canonical_claude()` and calls `control_response_round_trip(executable, live=True)`, so this is unambiguously a claude launch. It is the `doctor --live` probe that is an explicit step of the R276 certification sequence (handoff: "verify → doctor → doctor --live → full preflight"), i.e. it runs live **inside the exact certification window** R278 protects. This launch has `DISABLE_AUTOUPDATER=1` neither forced nor inherited (see Finding 4). An uncovered claude launch path is, per the review charter, a MAJOR finding — and this one directly defeats R278's stated purpose ("so the CLI cannot change again while certification is running"). **REQUIRED:** route the preflight live-probe env through `claude_child_env()`.

### 3. MAJOR — Uncovered Claude launch: turnover successor `SupervisorLauncher` (item 2) — REQUIRED
`tools/agent_supervisor/turnover_adapters.py:397` builds the successor invocation env with `env = minimal_env({...})` — not `claude_child_env`. For `TurnoverLayer.WORKER` the argv is a **confirmed Claude worker argv** from `build_argv(config)` with `config.executable = self._targets.claude_executable` (`turnover_adapters.py:427-437`); the invocation is then launched for real via `_process.run(..., env=dict(invocation.env))` (`turnover_adapters.py:475-479`). This launcher is production-wired: `cli.py:2586` passes `make_subprocess_command_runner(...)` into `run_orchestrator_watchdog` (the R595 orchestrator-turnover path, per the comment at `cli.py:2597`). So a turnover/rotation successor claude process launches with `DISABLE_AUTOUPDATER` stripped. Caveat for the orchestrator: the orchestrator-turnover firing is R595-gated, so live-fire depends on activation state — but it is certified-run machinery and contradicts the "every controller-launched claude child" guarantee. **REQUIRED:** route the WORKER-layer (and orchestrator-layer) successor env through `claude_child_env()`.

### 4. MAJOR — The owner machine-scope belt does NOT reach the `minimal_env` launch paths (root cause; item 1/6) — reproducible
`DEFAULT_ENV_ALLOWLIST` (`process.py:104-108`) does **not** contain `DISABLE_AUTOUPDATER` (the producer's own test asserts this: `test_agent_supervisor_claude_runner_env.py:78`). `minimal_env` inherits only allowlisted names (`process.py:207-208`), so it **strips** any inherited `DISABLE_AUTOUPDATER` — including the owner's machine-scope var from R288. Consequence: for Findings 2 and 3 (both `minimal_env`-based), **neither** the forced injection **nor** the R288 owner belt delivers the control. The evidence report (line 166-167) and both doc sections describe the owner var as belt-and-braces "so no terminal anywhere can trigger a background update while certification runs," but the supervisor's own `minimal_env`-based claude launches contradict that. This is the mechanical proof underlying the FAIL: it is not speculative — the allowlist filtering is provable from source.

### 5. MINOR — `claude --version` / `--help` probes rely solely on parent-env inheritance (item 2)
`capability_probe.py:99` (`subprocess.run([exe, *argv[1:]], ...)`, no `env=`) and `native_runtime.py:101` (`env=dict(env) if env is not None else None`, default `None`) launch `claude --version` / `claude --help` / `claude <verb> --help` live, inheriting the full parent environment. These ARE covered by the R288 owner machine-scope belt (full inheritance, no allowlist strip), but NOT by the forced injection — which R278 says the control must not depend on ("NOT dependent on parent-environment inheritance"). `native_runtime.py:183` documents that "the binary auto-updates itself (observed 2.1.246 → 2.1.247 mid-session)", i.e. any claude invocation can trigger the updater, so these probes are a real, if belt-mitigated, surface. These overlap the drift-teeth (M0-T118 scope) and I do not count their pre-existing test failures against this task, but the injection-coverage gap is worth recording.

### 6. INFO — Codex scope correctly untouched (item 3)
`codex_channel.py:45` imports only `minimal_env` from `.process` and uses it at `codex_channel.py:404`; it does not import `claude_child_env`. `minimal_env` is unchanged. Codex children are verifiably untouched. AS-5 is satisfied.

### 7. INFO — Test quality is good for the covered seams; blind to the gaps (item 4)
AS-1/AS-2 (`test_agent_supervisor_claude_runner_env.py:76-97`) patch the real `subprocess.Popen` and drive the real production entrypoints (`cr.ClaudeRunner(...).run_unit(...)`, `cr.probe_model_launch(...)`), capturing the exact `env` the production seam constructs — these intercept the real launch seam, not a reimplementation. Removal-sensitivity is genuine (report's AS-4 shows a `KeyError`/`None != '1'` when `env.update` is removed; I independently reproduced the GREEN state). AS-3 uses `minimal_env` as the oracle (`==` on the full dict minus one key) — non-tautological. The one limitation: the test suite only exercises the two `claude_runner` seams, so it structurally cannot catch Findings 2/3 — the test-completeness gap mirrors the code-completeness gap. `test_as5_codex_channel_still_uses_the_uninjected_builder` is a weak identity guard but acceptable.

### 8. MAJOR — Overstated completeness claim in report + docs (item 6) — REQUIRED
`M0-T117-autoupdater-evidence.md:8-9` ("forces `DISABLE_AUTOUPDATER=1` into the environment of **every** controller-launched CLAUDE child"), `M0-T117-producer-report.md:16-17` (same), and both doc sections (`README.md` "Every controller-launched claude child", runbook §13) assert a guarantee the code does not deliver (Findings 2/3/4). The red/green pytest claims themselves are accurate and reproducible; the completeness/scope framing is not. **REQUIRED:** correct the "every controller-launched claude child" claim to name the actual covered set, or (preferred) extend coverage to make the claim true.

### 9. INFO — Modularity fine (item 5)
`claude_child_env` is placed directly adjacent to `minimal_env` in `process.py` (correct owning module for env construction), reuses `minimal_env` with no duplicated logic, and is well-commented. `claude_runner.py` grew by ~5 lines (one import swap + two comment lines + two call swaps). No threshold concerns introduced. Producer's disclosed pre-existing `F401 import json` at `test_agent_supervisor_process.py:18` is not introduced here and is not CI-gated (tools/ outside the ruff working-dir); I did not independently lint but the disclosure is consistent with the diff.

---

## Verdict rationale

The delivered change is correct, well-tested, modular, and codex-safe **for the two `claude_runner` seams it covers**. However, the task's governing requirement R278 is "the controller-launched Claude processes **and the certification window** so the CLI cannot change again while certification is running," and the deliverables (report + code + docs) claim coverage of "**every** controller-launched claude child." At least two additional live claude launch surfaces — the `doctor --live` preflight probe (unconditionally part of the R276 certification sequence) and the turnover successor launcher — launch the real claude executable through `minimal_env`, which (mechanically proven, Finding 4) strips `DISABLE_AUTOUPDATER` even when the owner sets the R288 machine-scope belt. The primary objective is therefore not met and the completeness claim is inaccurate.

Relevant absolute paths:
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/preflight.py` (line 126/136)
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/turnover_adapters.py` (line 397/427-437/475-479)
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/process.py` (allowlist 104-108; helper 213-244)
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/claude_runner.py` (line 1102/1548)
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/cli.py` (1314-1319; 2586-2601)
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/native_runtime.py` (line 101), `.../capability_probe.py` (line 99)
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/reports/M0-T117-autoupdater-evidence.md` (line 8-9), `.../M0-T117-producer-report.md` (line 16-17)

**G3 VERDICT: FAIL** — two live Claude launch surfaces (preflight `doctor --live` and the turnover successor launcher) run during the certification window via `minimal_env`, which provably strips `DISABLE_AUTOUPDATER` even under the R288 owner belt, so R278's drift-proof guarantee and the "every controller-launched claude child" claim are not satisfied; route both through `claude_child_env()` (Findings 2, 3) and correct the completeness claims (Finding 8) to pass.
