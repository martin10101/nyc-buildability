<!-- Saved VERBATIM by the orchestrator from the G3 code-reviewer agent-return channel
     (delta re-attestation; transport entity-decoding only). Corrected identity d6a2ac8,
     control head 0a647cd. -->

All targeted modules green (12 passed for the env module including the 4 new seam tests; 60 passed / 1 skipped across env + process + turnover_adapters). Here is my delta report.

---

# G3 DELTA Re-attestation — M0-T117 at `d6a2ac8`

**Reviewed delta:** `fa16560` (my original review) → `d6a2ac8` (control head `0a647cd`), same checkout.
**Scope:** closure of my prior findings only, read-only.

## Commands run (read-only)
- `git show --stat d6a2ac8` — 7 files, matches the rework description.
- `git diff fa16560 d6a2ac8 -- preflight.py turnover_adapters.py` — both seams re-routed.
- `grep -rnE "minimal_env" tools/agent_supervisor/*.py` — enumerated all residual callers.
- `python -m pytest tools/test_agent_supervisor_claude_runner_env.py -q` → **`12 passed`** (matches expected).
- `python -m pytest .../claude_runner_env.py .../process.py .../turnover_adapters.py -q` → **`60 passed, 1 skipped`**.

## Per-finding closure

**Finding 2 (preflight `doctor --live` seam) — CLOSED.** `preflight.py:45` now imports `claude_child_env`; `control_response_round_trip` builds `env=claude_child_env()` (`preflight.py:139`) with an explanatory comment. New `DoctorLiveProbeEnvTests.test_control_response_round_trip_injects_the_control` intercepts the **real** `subprocess.Popen` seam, drives `preflight.control_response_round_trip("claude", live=True)`, and asserts `DISABLE_AUTOUPDATER=="1"` with the parent env popped and the allowlist omitting the key — removal-sensitive (reverting to `minimal_env` yields `None != '1'`, as the report's RED capture shows).

**Finding 3 (turnover successor, both layers) — CLOSED.** `turnover_adapters.py:53` now imports `claude_child_env`; `_build_invocation` builds `env=claude_child_env({SUPERVISOR_SUCCESSOR_EFFORT, SUPERVISOR_SESSION_ROLE})` (`turnover_adapters.py:398`). This is the single env-build path for both `TurnoverLayer.WORKER` and `ORCHESTRATOR`, so both layers are covered. New `TurnoverSuccessorEnvTests` asserts `DISABLE_AUTOUPDATER=="1"` for **both** layers and additionally verifies the pre-existing effort/role pairs survive (`claude_child_env` applies `extra` then forces the control pair last) — confirming no collateral regression to the effort/role metadata.

**Finding 8 (claim accuracy) — CLOSED.** The evidence report, README, and runbook now enumerate the exact **four** injection-forced seams (worker `run_unit`, model probe, `preflight.control_response_round_trip`, `turnover_adapters.SupervisorLauncher._build_invocation`) and honestly name the **two** NOT-injection-forced bare probe seams (`capability_probe.py::_run` ~L99, `native_runtime.py::_run`) that inherit the full parent env and rely on the R288 owner machine-scope belt. My Finding-4 fact is recorded verbatim: `minimal_env`'s allowlist strips `DISABLE_AUTOUPDATER` (absent from `DEFAULT_ENV_ALLOWLIST`), which is why the code-side injection is necessary and why the belt/injection are complementary. The overstated "every controller-launched claude child" wording is gone.

**Finding 5 (bare `claude --version`/`--help` probes; documented exclusion, not code-changed) — DISPOSITION ACCEPTABLE at MINOR.** `capability_probe.py`/`native_runtime.py` remain outside `allowed_paths` and unmodified. This is acceptable because those two seams invoke the CLI with `env=None` (full parent-environment inheritance, no `minimal_env` allowlist strip), so — unlike the four constructed-env seams — the R288 owner machine-scope belt genuinely reaches them; they are read-only capability/version probes (and are themselves the drift-teeth that detect drift); and the exclusion plus its rationale is now recorded honestly. R278's "not dependent on parent-environment inheritance" is fully satisfied for the four agent/probe-launch seams; leaving the two bare probes belt-covered by design avoids unjustified scope expansion. I concur with the disposition.

## Completeness re-check
Re-enumerated every residual `minimal_env` caller in `tools/agent_supervisor/*.py`: `codex_channel.py:404`, `codex_reviewer.py:593`, `operator_ask.py:311` all launch **codex** (codex `build_argv` with schema_path/output_path signature; operator_ask imports `build_argv` from `codex_reviewer`); `evidence.py:189` is explicitly "not Claude" (launches `git`/`python`); `process.py:744` is the generic runner default. **No uncovered claude launch via `minimal_env` remains.** All four claude executable launch seams that build their env from the supervisor now use `claude_child_env`. No new findings introduced by the delta; the +4 tests are removal-sensitive and non-tautological (the G4-F6 test first proves `minimal_env` would admit a parent `"0"`, then proves `claude_child_env` forces `"1"`).

## Suite state
Coordinator-reported full suite at the delta: 2726 collected (2712 + 14), 2721 passed, 2 skipped, 3 failed (the three pre-existing `2.1.251`-vs-`2.1.248` drift teeth — out of scope, M0-T118). My targeted runs corroborate: touched env module 12/12, and env+process+turnover_adapters 60 passed/1 skipped, with no failures outside the known drift teeth.

**G3 DELTA VERDICT: PASS at d6a2ac8** — Findings 2, 3, and 8 are closed with reproducible real-seam tests and precise documentation; Finding 5's documented-exclusion disposition is acceptable at MINOR; all four supervisor-constructed claude env seams now force `DISABLE_AUTOUPDATER=1` and no uncovered `minimal_env` claude launch remains.
