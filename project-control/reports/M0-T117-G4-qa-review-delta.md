<!-- Saved VERBATIM by the orchestrator from the G4 qa-engineer agent-return channel
     (delta re-attestation; transport entity-decoding only). Corrected identity d6a2ac8,
     control head 0a647cd. -->

All four delta items verified, and the README documents the precise covered/uncovered set. Here is my delta report.

---

# G4 DELTA Re-Attestation — M0-T117 at `d6a2ac8`

**Reviewer:** qa-engineer (independent, read-only). **Corrected identity:** material `d6a2ac8` / control head `0a647cd`, files at `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`. **Method:** git-free file-read + pytest against the `ctl24` files (worktree-isolation guard still blocks git; same method as my `fa16560` review). **Delta reviewed vs `fa16560`**, not the whole task.

## Commands (exact) and result lines

| # | Command (absolute `ctl24` paths) | Result |
|---|---|---|
| D1 | `pytest .../test_agent_supervisor_claude_runner_env.py .../process.py .../recovery_probes.py .../turnover_live_seam.py -q` | **`221 passed, 1 skipped in 22.68s`** (matches expected) |
| D2 | `pytest ctl24/tools/test_agent_supervisor_*.py -q` | **`3 failed, 2721 passed, 2 skipped in 190.23s`** (2726 collected) — 3 failures = the same three drift teeth |

## Delta verification (four requested items)

**(1) F6 allowlist re-enable vector — CLOSED with a genuine removal-sensitive test.** `test_g4f6_allowlist_reenable_vector_is_overridden` (env module lines 140-157) sets the parent env `DISABLE_AUTOUPDATER="0"`, widens the allowlist to admit it, first **asserts `minimal_env(...)["DISABLE_AUTOUPDATER"]=="0"`** (self-validating that the re-enable vector is real, not vacuous), then asserts `claude_child_env(...)` forces `"1"`. If the last-write injection line were removed, `claude_child_env` would inherit `"0"` and the `== "1"` assertion would fail — genuinely removal-sensitive. Exactly the test my F6 asked for.

**(2) New seam tests intercept the REAL production seams (AS-1/AS-2 standard).**
- `test_control_response_round_trip_injects_the_control` mocks the **real `subprocess.Popen`** (same `_capturing_popen` used by AS-1/AS-2) and calls `preflight.control_response_round_trip("claude", live=True)`, capturing the env the production Popen at `preflight.py:139` (`env=claude_child_env()`) constructs. Confirmed the seam is code-fixed at source.
- `test_worker_successor_env_injects_and_preserves_existing_pairs` / `test_orchestrator_successor_env_injects_the_control` call the **real** `SupervisorLauncher._build_invocation(...)` and read its constructed `inv.env`. Verified at source that `_build_invocation` (turnover_adapters.py:401) builds `env = claude_child_env({SUPERVISOR_SUCCESSOR_EFFORT, SUPERVISOR_SESSION_ROLE})` (forced pair applied last) and that this env is what the launch consumes (`env=dict(invocation.env)` at :482). The worker test additionally asserts the pre-existing effort (`xhigh`) and role (`worker`) pairs survive — proving the forced pair does not clobber legitimate extras. Both are real-seam captures, not helper-only assertions.

**(3) Rework red/green consistent with the test design.** Recorded pre-fix RED = 3 failed: `None != '1'` at the real preflight Popen (pre-fix used `minimal_env()`, so the captured env lacked the key → `env.get(...)==None`) and `KeyError: 'DISABLE_AUTOUPDATER'` on both turnover invocations (pre-fix `inv.env` lacked the key). Post-fix GREEN = 3 passed. This matches the seam behavior exactly and mirrors the AS-1/AS-2 (`None != '1'`) and AS-6/process (`KeyError`) failure shapes I derived in round 1.

**(4) Count reconciliation — independently reproduced.** My D2 run: **2726 collected = 2721 passed + 2 skipped + 3 failed**. `2726 = 2712 baseline + 14` (10 round-1: 8 injection module + 2 process; + 4 rework: F6 + preflight + worker-successor + orchestrator-successor). Passed moved `2717 → 2721` (the 4 new tests), skipped unchanged at 2, failed unchanged at 3 — and the 3 are the identical drift teeth (`capability_probe::test_live_reprobe_claude_version_matches_fixture`, `event_bus::test_s8_live_version_matches_catalog_fixture`, `native_adapter::test_live_detection_matches_committed_fixture`), all asserting `2.1.251 == 2.1.248` and untouched by this env-construction change (M0-T118 scope).

## F5 disposition — SATISFIED

My round-1 F5 (MAJOR) recommended confirming R278 coverage for the non-worker claude launch paths and/or routing them through `claude_child_env` for machine-var-independent defense in depth. The disposition resolves it well:
- The two **constructed-env** claude seams — the **live** `preflight.control_response_round_trip` (my primary concern: a live claude child inside the certification/`--live` window) and the `turnover_adapters` successor launcher (worker **and** orchestrator layers) — are now **fixed in code** and no longer depend on parent-env inheritance.
- The two **bare** `claude --version`/`--help` probes (`capability_probe.py::_run` ~L99, no `env=`; `native_runtime.py` ~L101, `env=None`) are documented (README §"Claude Code version admission events" lines 408-429) as deliberately **not** env-stripped — with a sound rationale (env-stripping a bare version/help probe is itself a riskier behavior change) — and covered by the owner **machine-scope** `DISABLE_AUTOUPDATER` belt (R288, already required by the amendment). The covered/uncovered set is stated precisely in the doc.

This is exactly the "code-fix where clean, documented owner-belt exclusion where a code fix would be a riskier behavior change" outcome my F5 pointed toward. My primary risk (live preflight child) is eliminated in code. (Trivial doc nit, non-blocking: README line 416 calls the `native_runtime` function `_run`; its actual name is `run_command` — the `~line 101` / `env=None` facts are correct.)

Round-1 F7 (optional AS-5 codex live-capture hardening) was never required and remains a non-blocking suggestion.

**G4 DELTA VERDICT: PASS at d6a2ac8** — the four delta items independently reproduce (F6 closed by a genuine removal-sensitive test; both new seam tests capture the real production seams; rework red/green matches the design; 2726/2721/2/3 reconciles to the same three out-of-scope drift teeth), and the F5 MAJOR is satisfactorily dispositioned by fixing the two constructed-env seams in code and documenting the two bare-probe exclusions as owner-machine-var covered.
