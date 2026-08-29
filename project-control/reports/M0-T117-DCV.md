<!-- Saved VERBATIM by the orchestrator from the directive-compliance-verifier agent-return
     channel (transport entity-decoding only). Verified at HEAD 50d1d31, material identity
     d6a2ac8. -->

Full supervisor suite complete: `3 failed, 2721 passed, 2 skipped` — the 3 failures are exactly the three drift teeth (2.1.251 vs 2.1.248), confirming no regression from this change. I have now personally reproduced every load-bearing fact. Here is my report.

---

# DCV Report — M0-T117 (D-024 Amendment-13), frozen material identity `d6a2ac8`

**Reviewer:** directive-compliance-verifier (independent, read-only). **Producer ≠ verifier.**
**Checkout:** `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, branch `control/D-024-fable-codex-loop`, HEAD `50d1d31`.
**Content identity:** `git diff --name-only d6a2ac8..HEAD` → control-plane files only (gates/reports/state/task); production code is frozen at `d6a2ac8`. Gate head `6037570` has an empty production diff vs `d6a2ac8` (`git diff --name-only d6a2ac8 6037570 -- tools/ docs/ apps/ services/` returns nothing), so the recorded gates reviewed the same production code.
**Applicable set (7 rows where `M0-T117` ∈ requirement `applicability.task_ids`):** R277, R278, R279, R280, R286, R287, R288. Verified against `requirements.json` — matches the packet. `validate_directive_compliance.py --check` → EXIT=0 (source digests match, Amendment-13 reflected, `amendment_sequence:13` on all rows).

## Per-requirement verdicts

**D-024-R277 — Option-A authorization umbrella — PASS**
Primary evidence: `requirements.json` R277 `applicability.task_ids = [M0-T113, M0-T117, M0-T118, M0-T119]`, classification `authorization`. This unit delivers the first chain element (the DISABLE_AUTOUPDATER control / "before recapture" precondition), and the remaining elements are individually bound: R281 (recapture)→M0-T118 (status `backlog`), R283 (recert)→M0-T119 (`backlog`), R284 (rerun R276)→M0-T113/M0-T119, R285 (repin)→M0-T113 (`in_progress`). All three downstream task packets exist. Binding structure supports the chain exactly as the amendment's forward trace states. No discrepancy.

**D-024-R278 — establish+verify DISABLE_AUTOUPDATER=1, BOTH scopes — PASS**
Code scope — all four supervisor-constructed claude env seams personally read and confirmed to route through the forced helper:
- `tools/agent_supervisor/process.py:245-246` — `claude_child_env` = `minimal_env(...)` then `env.update(FORCED_CLAUDE_CHILD_ENV)` (`{"DISABLE_AUTOUPDATER":"1"}` at line 221) applied LAST, unconditional (overrides allowlist + extra_env).
- `claude_runner.py:1103` (worker `run_unit`) and `claude_runner.py:1549` (`probe_model_launch`) — both `env = claude_child_env(...)`.
- `preflight.py:139` — `doctor --live` control-response probe Popen uses `env=claude_child_env()`.
- `turnover_adapters.py:401` — successor launch (both WORKER and ORCHESTRATOR layers share this `env = claude_child_env({...})`).
Removal-sensitive tests reproduced green: `python -m pytest tools/test_agent_supervisor_claude_runner_env.py tools/test_agent_supervisor_process.py -q` → **42 passed, 1 skipped** (12 env-module incl. G4-F6 allowlist-re-enable + preflight + both successor-layer seam tests; 30 process). Two exclusions honestly recorded and independently confirmed: `capability_probe.py:99-102` (`subprocess.run([exe,...])`, no `env=`) and `native_runtime.py:101-105` (`env=dict(env) if env is not None else None`) inherit the full parent env; documented in `README.md:412-421` and runbook `:241-248`.
Workstation scope — independent read-only re-verification: `reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v DISABLE_AUTOUPDATER` → `DISABLE_AUTOUPDATER  REG_SZ  1`. Both scopes established and verified. No discrepancy.

**D-024-R279 — control established BEFORE recapture — PASS**
`M0-T118.json` status = `backlog`, worktree `None`; directory `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t118` does not exist; no `*_2_1_251.json` fixtures in `tools/agent_supervisor/fixtures/` (grep exit 1, no matches). M0-T118 dependency on M0-T117 enforces the order. Recapture has not begun. No discrepancy.

**D-024-R280 — prohibitions (no DISABLE_UPDATES / no downgrade / no unrelated global config) — PASS**
`git diff dca3817..d6a2ac8 -- '*.py'` added-line grep for `DISABLE_UPDATES` → single hit at `process.py` comment explaining it is deliberately NOT used (documentary, not an applied control). `claude --version` → `2.1.251 (Claude Code)` — not downgraded (matches the admission target, not the certified 2.1.248). `git diff --name-only dca3817..d6a2ac8` production/doc files (`process.py`, `claude_runner.py`, `preflight.py`, `turnover_adapters.py`, `test_agent_supervisor_claude_runner_env.py`, `test_agent_supervisor_process.py`, `README.md`, `CONTROLLER_UPDATE_RUNBOOK.md`) are all inside the packet `allowed_paths` (incl. the recorded scope extension); the remaining diff entries are orchestrator-owned control-plane records. No unrelated global config change. No discrepancy.

**D-024-R286 — background updates disabled for controller-launched workers (standing) — PASS**
Code-enforced by the four unconditional seams above; removal-sensitivity proven (AS-4 red/green in the evidence report and reproduced by my 42-pass run — reverting `env.update(FORCED_CLAUDE_CHILD_ENV)` makes the seam tests fail `None != '1'` / `KeyError`). Documented as standing policy in `README.md:388-410` and `CONTROLLER_UPDATE_RUNBOOK.md §13 (225-239)`. No discrepancy.

**D-024-R287 — upgrades are deliberate admission events, no silent drift — PASS**
`README.md:430-435` and `CONTROLLER_UPDATE_RUNBOOK.md:256-263` both document the ordered discipline with the correct sequence: update intentionally → recapture fixtures → run full recertification → **only then** repin (`--repin-cli-identity`); "Never repin first; never silently accept version drift." No discrepancy.

**D-024-R288 — owner-side Windows action: stop + deliver exact commands — PASS**
No agent-executed environment mutation in the diff or tests: grep for `SetEnvironmentVariable|setx|reg add|winreg` across all 8 changed source files → the only hit is `CONTROLLER_UPDATE_RUNBOOK.md:273` (documented owner command). The five `os.environ["DISABLE_AUTOUPDATER"]=...` writes are all in `test_agent_supervisor_claude_runner_env.py` (lines 71/146/157/174/203) as transient in-process save/restore fixtures (setUp/tearDown + try/finally), not persistent Windows actions. The exact administrator PowerShell command plus stored-value and inheritance verification commands are recorded verbatim in `M0-T117-autoupdater-evidence.md:254-268`, labeled owner-executed, closing with "None of the above owner-side commands were executed by this producer." No discrepancy.

## Supporting confirmations
- Gate records: G0 PASS (`dca3817`, orchestrator), G2 PASS (`fa16560`, orchestrator), G3 PASS (`6037570`, code-reviewer), G4 PASS (`6037570`, qa-engineer), G5 PASS (`6037570`, security-reviewer). Delta re-attestation reports all record "VERDICT: PASS at d6a2ac8."
- Full suite `python -m pytest tools/test_agent_supervisor_*.py -q` → **3 failed, 2721 passed, 2 skipped** (2726 collected). The three failures are exactly the pre-existing drift teeth, each asserting `'2.1.251 (Claude Code)' == '2.1.248 (Claude Code)'`: `test_agent_supervisor_capability_probe.py::test_live_reprobe_claude_version_matches_fixture`, `test_agent_supervisor_event_bus.py::test_s8_live_version_matches_catalog_fixture`, `test_agent_supervisor_native_adapter.py::test_live_detection_matches_committed_fixture` — M0-T118 fixture-recapture scope, not env-building regressions.
- Prohibited-action evidence: nothing merged/accepted/dispatched/deployed/purchased/closed by this task; M0-T118 unstarted; the 2.1.251 CLI was already installed (admission pending, not caused here); no agent-side env mutation; R288 owner action was owner-executed.

Relevant paths (all absolute): `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/process.py`, `.../claude_runner.py`, `.../preflight.py`, `.../turnover_adapters.py`, `.../capability_probe.py`, `.../native_runtime.py`, `.../README.md`, `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/docs/CONTROLLER_UPDATE_RUNBOOK.md`, `.../tools/test_agent_supervisor_claude_runner_env.py`, `.../project-control/reports/M0-T117-autoupdater-evidence.md`, `.../project-control/tasks/M0-T117.json`, `.../project-control/directives/D-024-fable-codex-loop/{source-013-amendment.md,requirements.json}`.

All 7 applicable rows PASS. No VIOLATED / UNVERIFIABLE / BLOCKED rows.

**DCV VERDICT: PASS at d6a2ac8**
