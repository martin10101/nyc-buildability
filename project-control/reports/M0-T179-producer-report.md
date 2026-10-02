# M0-T179 (D-091) — Linux recertification of the supervisor after M0-T177 and M0-T178 (supersedes M0-T174)

Producer: `backend-engineer`, in the assigned isolation worktree `/root/project/w-M0-T179`
(branch `task/M0-T179-linux-recert-2`). Round-2 work cut at the scope-corrected head
`972585a515601b3bbfcd27f472c51d2b448e345d` (worktree guard confirmed BEFORE any work:
`git rev-parse --show-toplevel` == `/root/project/w-M0-T179`, branch
`task/M0-T179-linux-recert-2`, HEAD `972585a5…`). Recipe: `docs/D091_WAVE3_WIRING_PLAN.md` §2;
precedents `project-control/reports/M0-T174-producer-report.md` (superseded) and
`M0-T159-recertification.md` (the D-024-R287 ordered-admission shape). All probes local — NO
provider call (version/help/doc-fetch only), NO systemd/config/credential/live step. Interpreter
`/root/project/lanes-runtime/venv/bin/python` (Python 3.12.3); cwd = worktree root unless noted.

## VERDICT — CERTIFIED at claude 2.1.288 (this host), subject to the independent gate wave

The supervisor controller is **recertified** on this Linux server at the tree that includes
M0-T177 (B-027 systemd control-group containment + self-kill fix) and M0-T178 (DB-103 equal-model
refusal), after admitting the host's auto-update **claude 2.1.287 → 2.1.288** (codex-cli 0.157.0
unchanged). All three live claude-version drift teeth + the codex tooth are GREEN against the
recaptured 2.1.288 fixtures; the bash shell-routing harness, the Linux containment suite (+R1/R2),
and the dual_review suite are GREEN; this host's default containment still refuses outside a
hardened service, by design. claude `--version` was `2.1.288` at the start AND at the end of the
run (stable; no mid-run change → no fail-closed STOP). Deferred items are owner-typed commissioning
(§7), unchanged. Any later `tools/agent_supervisor/**` change re-invalidates this certification.

## Round 1 — failed closed (auto-update 2.1.287 → 2.1.288)

The first run (producer commit `57f7e515`) correctly **FAILED CLOSED and did NOT claim the cert.**
It found the installed claude had auto-updated 2.1.287 → 2.1.288 after M0-T174, turning all three
claude-version drift teeth RED against the certified tree's `*_2_1_287` fixtures. capability_probe
and native_adapter were curable inside the then-`allowed_paths`, but the **event_bus S8** tooth was
not: `test_s8_live_version_matches_catalog_fixture` loads the catalog via
`ed.load_catalog_fixture()` with no path arg, which resolves `event_drift.py`'s module-level
`CATALOG_FIXTURE_PATH` — a `tools/agent_supervisor/*.py` source change was required and was
`forbidden`. Rather than make an inconsistent partial recapture or a false cert, round 1 made zero
tree edits and returned a consolidated blocker recommending the M0-T174 round-1 scope-correction
shape. The orchestrator then scope-corrected the packet (commit `9ac3b16c`; G0 re-recorded at head
`972585a5`): `allowed_paths` add `tools/agent_supervisor/event_drift.py` (the hook-catalog re-point
ONLY), with the premise flipped to "recapture ALL THREE drift families at 2.1.288, keeping every
2.1.287 fixture" — a deliberate admission event under D-024-R287. This round 2 executes that.

## 0. Producer / tree identity (round 2)
| Anchor | Value |
|---|---|
| Worktree / branch | `/root/project/w-M0-T179` / `task/M0-T179-linux-recert-2` |
| Scope-corrected base | `972585a515601b3bbfcd27f472c51d2b448e345d` |
| `tools/agent_supervisor` subtree BEFORE this round | `5d67e2e4a9b11a56cef0f65c4057ba7f22f793ac` (accepted M0-T177+M0-T178 tree) |
| **certified `tools/agent_supervisor` subtree AFTER the re-point + recapture** | **`019ecf1f7ed568942545c2e32778e0fb3acee715`** (moved by `event_drift.py` + the 3 new fixtures; the 3 test files are outside the subtree) |
| Producer commit (this round) | recorded in the ledger/return (adds the 7 files below + this report) |

## 1. Installed CLIs on this server (version probes only — no provider call)
| Tool | `--version` first line | M0-T174 value | Changed? | Path(s) |
|---|---|---|---|---|
| Claude Code | `2.1.288 (Claude Code)` (start AND end of run) | `2.1.287 (Claude Code)` | **YES (2.1.287 → 2.1.288, host auto-update)** | `/usr/bin/claude` (system install; probe resolved `/usr/bin/claude`, `/bin/claude`) |
| Codex CLI | `codex-cli 0.157.0` | `codex-cli 0.157.0` | no | `/opt/nyc-codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex`; also on PATH `/usr/local/bin/codex` (same digest; installed from the admitted `tools/codex_cli/package-lock.json`) |

## 2. Recaptured fixtures (old 2.1.287 / m0t174 fixtures KEPT — append-only history)
| Fixture (NEW, under `tools/agent_supervisor/fixtures/`) | Role | LF-normalized sha256 |
|---|---|---|
| `capability_probe_live_2026-10-02_m0t179_2_1_288.json` | current capability fixture (claude 2.1.288 / codex-cli 0.157.0), re-probed live | `b5950e97cac0bd57c565c246425c863895bd0124487e16775f609591abdda5d1` |
| `native_runtime_detection_2026-10-02_m0t179.json` | native-runtime-detection fixture (claude 2.1.288; background_gaps []; all 5 verbs supported) | `9c02bc9770ced548f23b389d844b3c7ee13edd56f1e55fcbdd17a891276e4da3` |
| `hook_event_catalog_2_1_288.json` | hook-event catalog (33 events, no drift vs 2.1.287) | `975a91185c7061070429ac8210fb1cca89981b29adc4830b64393414ba88dd04` |

Capture commands (cwd `/root/project/w-M0-T179`, interpreter the venv python):
- `python -m tools.agent_supervisor.capability_probe --out …m0t179_2_1_288.json` → exit 0; body
  records `claude_version.first_line "2.1.288 (Claude Code)"`, `codex_version.first_line
  "codex-cli 0.157.0"`; every claude/codex flag/verb classification identical to the 2.1.287
  predecessor (version-only drift). `probe_meta` paths are `/usr/bin/claude`, `/bin/claude`,
  `/usr/local/bin/codex` — NONE under `/home` or `/Users`; leak scan clean.
- `native_runtime.detect_native_capabilities()` → `build_detection_fixture(task="M0-T179")`
  (help/version probes only) → `claude_version "2.1.288 (Claude Code)"`, `background_gaps []`,
  verbs agents/attach/logs/stop/respawn all `supported`.
- Hook-event catalog: re-fetched the official docs `curl -sS -L -A "Mozilla/5.0 (recert-probe)"
  https://code.claude.com/docs/en/hooks` on **2026-10-02**, **HTTP 200**, **2,915,734 bytes**
  (M0-T174's 2.1.287 fetch was 2,919,589; ~3.8 KB prose shrink). **Event count 33, no drift vs
  2.1.287** — all 33 known events present as their documented lowercase id-anchor sections; the
  only extra PascalCase tokens carrying a doc id-anchor are `AskUserQuestion` (a tool) and
  `PowerShell` (a shell name), not hook events (carries M0-T174's triage that `AskUserQuestion`,
  `SubagentHandback`, `TaskUpdate` are tools). The recorded drift `added=[PostModelSwitch,
  PreModelSwitch], removed=[]` matches `event_drift.catalog_drift()` (verified).

## 3. The one allowed `.py` source change (hook-catalog re-point ONLY)
`tools/agent_supervisor/event_drift.py` `CATALOG_FIXTURE_PATH`:
`…/fixtures/hook_event_catalog_2_1_287.json` → `…/fixtures/hook_event_catalog_2_1_288.json`
(plus the adjacent comment). No logic change; no other `tools/agent_supervisor/*.py` touched.
This is exactly the M0-T159 / M0-T174 recertification precedent and the one exception the
scope-corrected `forbidden_paths` permits. The three re-baseline test files
(`test_agent_supervisor_capability_probe.py`, `_native_adapter.py`, `_event_bus.py`) were
repointed to the new fixtures and their version-pinned invariants updated to 2.1.288 / task
M0-T179 (the capability invariant renamed `…_2_1_287_…` → `…_2_1_288_…`, filename-id `m0t179`).

## 4. Teeth — each run with command, cwd, interpreter, exit code, result (all GREEN)
cwd `/root/project/w-M0-T179`; pytest via the venv python; harness via `/usr/bin/bash`.

| Tooth | Command | Result |
|---|---|---|
| capability_probe — live claude reprobe | `pytest …capability_probe.py::test_live_reprobe_claude_version_matches_fixture` | **PASS** (2.1.288 == fixture) |
| capability_probe — live codex reprobe | `…::test_live_reprobe_codex_version_matches_fixture` | **PASS** (0.157.0) |
| capability_probe — 2.1.288 re-baseline invariant | `…::test_current_fixture_records_claude_2_1_288_masked_and_shaped` | **PASS** |
| native_adapter — live detection | `…native_adapter.py::test_live_detection_matches_committed_fixture` | **PASS** (2.1.288) |
| event_bus — S8 live version | `…event_bus.py::test_s8_live_version_matches_catalog_fixture` | **PASS** (2.1.288) |
| event_bus — S8 catalog valid+masked / recorded-drift | `…::test_s8_catalog_fixture_valid_and_masked`, `…::test_s8_recorded_drift_matches_computed_drift` | **PASS** (task M0-T179, 33 events, drift reconciled) |
| three recapture suites together | `pytest capability_probe.py native_adapter.py event_bus.py` | **115 passed, 0 skipped** (0 skips ⇒ all live teeth RAN with claude+codex present) |
| bash shell-routing harness + mutants | `bash tools/agent_supervisor/linux/sh_tests/run_sh_tests.sh` (direct exit) | **PASS, exit 0** — `3 test file(s) passed`; 3 mutants detected (`pipe_tee`→0, `dollar_q`→0, `grep_pipe`→1; control raw 7 preserved) + the start-gate-refusal removal detected |
| Linux containment suite (no R3) | `pytest …linux_containment.py -k "not R3"` | **PASS** — `42 passed, 1 deselected` |
| containment R1 (single id) | `…::LinuxContainmentRealProcessTests::test_R1_timeout_kill_spares_the_harness_and_worker_has_its_own_group` | **PASS** — `1 passed` (3.23 s) |
| containment R2 (single id) | `…::LinuxContainmentRealProcessTests::test_R2_group_kill_of_harness_leaves_a_setsid_grandchild_alive` | **PASS** — `1 passed` (1.97 s) |
| dual_review suite (M0-T178 DB-103) | `pytest …dual_review.py` | **PASS** — `21 passed` |

Self-checks: `ruff check` on the 4 edited files → **All checks passed** (exit 0; ruff is not
configured for `tools/` — advisory, default settings). `python3 tools/modularity_check.py --check`
→ exit 0 (event_drift.py not flagged; the one-line re-point + comment did not grow it). R3
(`R3RealSystemdUnitTests::test_R3_…`) and whole `RealProcess` classes and the whole `model_chain.py`
were **NOT run on this host** (packet-forbidden; R1/R2 by single id only).

## 5. Containment on this host + CI real-unit R3 proof
- `python3 -c "from tools.agent_supervisor import process; print(process.default_containment_kind())"`
  → **`process_group`** (start and end). Correct by design (M0-T177 B-027): on this box euid is 0
  and the cgroup is a `.scope`, so the systemd-service proof refuses and the loop would REFUSE to
  dispatch outside a hardened `.service` — nothing is newly enabled here. The suite's
  `process_group`/`taskkill` refusal teeth are among the 42 that pass.
- Real-unit R3 proof (cited; not run here): the additive `supervisor-linux-containment` ubuntu CI
  job ran `test_R3_kill_of_main_pid_reaps_the_whole_control_group` GREEN — **run 37072153749, job
  111053843200 at 8fc412e0**; the orchestrator confirmed the same job GREEN on the merged heads of
  **PR #344 and PR #345** (both PRs' CI fully green before merge).

## 6. Supervisor-freeze baseline (cited; not run here — host safety)
The whole supervisor glob was deliberately NOT run on this Linux host (documented exit-137 history
on the whole-suite single process; packet host-safety bound). The freeze baseline is re-established
by CI **`supervisor-bridge` (windows-latest, the whole supervisor glob)** GREEN on the merged heads
of **PR #344 and PR #345** (orchestrator-attested; the ≥1165-test freeze baseline is a CI
responsibility, `.claude/rules/supervisor-freeze.md` §4). After this task lands, the freeze suite
re-baselines against the new subtree `019ecf1f…` under the standard gates.

## 7. What remains owner-typed (unchanged; commissioning = M0-T175)
None performed; each is owner-typed, not agent-executable:
- create the root-owned `/etc/nyc-supervisor/config.toml`;
- Codex sign-in (and therefore the live shell-routing / routing_probe fixture, which needs a
  provider round-trip) — deferred to commissioning;
- `record-manifest` + `verify-controller` / `verify-manifest` on the installed tree (note: the
  activation-manifest digest moves by exactly the one manifest-covered `*.py` file `event_drift.py`
  — the M0-T159/M0-T174 pattern; the 3 fixtures and the `tools/test_*.py` files are not
  manifest-covered);
- systemd unit install and the live `start`;
- the activation-PIN amendment **D-091-R009** is owner-applied.
`tools/controller_update/source_binding.json` re-pin is likewise outside this packet (Windows-path /
owner B-026 decision).

## 8. Preservation / safety
No provider/model request (only `--version`/`--help` probes and one public docs `curl` GET). No
`/etc/nyc-supervisor/config.toml`, no systemd unit, no `systemd-run`, no live loop, no codex login,
no credential touched, no supervisor killed. R3 / whole `RealProcess` / whole `model_chain.py` NOT
run here. The ONLY `tools/agent_supervisor/*.py` edit is the authorized `event_drift.py`
hook-catalog re-point; no other supervisor source changed. Writes outside `tools/agent_supervisor/`
are the 3 re-baseline test files and this report, all in `allowed_paths`; scratch scripts/outputs
only under the session scratchpad. Nothing pushed; no `tools/project_control.py` run
(orchestrator-only, ADR-005).

## 9. Acceptance scenarios (packet) — status
- identity: **HOLDS** — certified subtree `019ecf1f…` pinned; CLIs recorded (claude 2.1.288, codex
  0.157.0); recaptured per the scope-corrected premise (versions changed).
- teeth: **HOLDS** — all three claude-version drift teeth + codex tooth GREEN at 2.1.288 (§4).
- shell harness: **HOLDS** — passes, every mutant detected (§4).
- containment: **HOLDS** — suite green here (42 + R1 + R2), default kind `process_group` (refusal
  by design), real-unit R3 cited from CI (§5).
- baseline: **HOLDS (cited)** — `supervisor-bridge` windows-latest green on #344/#345 merged heads
  (§6); re-baselines at `019ecf1f…` under the gates.
- failure: **HONORED** — round 1 failed closed and did not claim the cert; round 2 claims it only
  after every tooth is green.

Subject to the independent G0/G2/G3/G4/G5 review wave (control-plane-verifier, security-reviewer,
directive-compliance-verifier) and the orchestrator-recorded manifest/binding steps at the
integrated candidate. Any further `tools/agent_supervisor/**` change re-invalidates this cert.

END-OF-REPORT
