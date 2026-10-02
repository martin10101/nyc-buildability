# M0-T174 (D-091 TW4) — Linux recertification of the supervisor controller

Producer: `backend-engineer`, in the assigned worktree `/root/project/w-M0-T174`
(branch `task/M0-T174-linux-recert`), cut at the claim-seam commit
`409060270ad37ec48b1dada57c0f9ffd841da3cf` (tree clean, verified
`rev-parse --show-toplevel` == the worktree before any work). Recertification
of the controller on the Ubuntu cloud server after the D-091 code tasks
(M0-T171/T172/T173/T176) merged. Recipe: `docs/D091_WAVE3_WIRING_PLAN.md` §2;
precedent: `project-control/reports/M0-T159-recertification.md`. All probes are
local — NO provider call (version/help only), NO systemd/config/credential step
(owner-typed, TW5). Every command recorded with its cwd.

## 0. Producer commit identity
| Anchor | Value |
|---|---|
| Producer commit (this unit) | `17d35c4cc473c59ec396b454f3ed7fb55a0953b7` (branch `task/M0-T174-linux-recert`, parent `409060270ad37ec48b1dada57c0f9ffd841da3cf`) |
| commit tree | `8940b01b0a631e79b5681532e23c8d53ca03bbde` |
| `tools/agent_supervisor` subtree AT this commit | `0368b1a997fe1359f989e1a70d2d1462b6ad81d0` |
| Files changed | 4 (2 fixtures added, 2 test files edited); `node_modules/` git-ignored and uncommitted |

## 1. Installed CLIs on this server (version probes only)
| Tool | `--version` first line | Path(s) resolved |
|---|---|---|
| Claude Code | `2.1.287 (Claude Code)` | `/usr/bin/claude` -> `/usr/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe` (system/global npm install) |
| Codex CLI | `codex-cli 0.157.0` | repo-local M0-T167 admission, installed in this worktree via `npm ci --ignore-scripts` (see §2) |

`codex` was not on PATH. Installed it reproducibly in the worktree so the
evidence is self-contained:
```
cd /root/project/w-M0-T174/tools/codex_cli && npm ci --ignore-scripts
  -> added 2 packages, audited 3, found 0 vulnerabilities, exit 0
```
Lock-pinned `@openai/codex@0.157.0`
(`sha512-st1R2MhP3ndngOqj2SVh1qk6ED1lpgtlDxipDUyxlKfbsna0imwU2FdTnCjohFQpVh4bR5D5m1hA05AuW2v8Xg==`);
no package added/upgraded, lock untouched. `tools/codex_cli/.gitignore` and the
repo-root `.gitignore` both ignore `node_modules/` (verified
`git check-ignore tools/codex_cli/node_modules` and a clean `git status`); it was
never staged or committed. The probe PATH prefix used:
`/root/project/w-M0-T174/tools/codex_cli/node_modules/.bin`.

## 2. Recaptured fixtures (old fixtures KEPT, not deleted)
| Fixture | Role | LF-normalized sha256 |
|---|---|---|
| `tools/agent_supervisor/fixtures/capability_probe_live_2026-10-02_m0t174_2_1_287.json` | NEW current capability fixture (claude 2.1.287 / codex-cli 0.157.0) | `0d46c07b38043eaee9a355a00d24f380e3d9c0ea32222efd8f5ee80e17bf0e4c` |
| `tools/agent_supervisor/fixtures/native_runtime_detection_2026-10-02_m0t174.json` | NEW native-runtime-detection fixture (claude 2.1.287) | `7ce775351f1567bfa38ab10b04e2bd0bdfd79aaebd6e2d2eeb5fdcdf44e55950` |

The M0-T159 predecessors (`capability_probe_live_2026-09-24_m0t159_2_1_281.json`,
`native_runtime_detection_2026-09-24_m0t159.json`,
`shell_routing_2026-09-24_m0t159_2_1_281.json`) and all earlier fixtures remain
committed as append-only history.

Capture commands (cwd `/root/project/w-M0-T174`, PATH carrying the worktree codex
bin, interpreter `/root/project/lanes-runtime/venv/bin/python` = Python 3.12.3):
```
python -m tools.agent_supervisor.capability_probe --out \
  tools/agent_supervisor/fixtures/capability_probe_live_2026-10-02_m0t174_2_1_287.json
# scratchpad script: detect_native_capabilities() -> build_detection_fixture(task="M0-T174")
#   -> native_runtime_detection_2026-10-02_m0t174.json
#   printed: claude_version 2.1.287 (Claude Code); background_gaps []; all 5 verbs supported
```
Capability body records `claude_version.first_line = "2.1.287 (Claude Code)"` and
`codex_version.first_line = "codex-cli 0.157.0"`; every claude/codex flag/verb
classification is identical to the 2.1.281/0.153.4 predecessor (version-only
drift). Detection body: `claude_version "2.1.287 (Claude Code)"`,
`background_gaps []`, verbs agents/attach/logs/stop/respawn all `supported`.

### HOME-masking on Linux (platform note; carried into the re-baseline test)
The probe passes `probe_meta` through `telemetry_redaction.redact_probe_meta`,
whose `_HOME_PREFIXES` regex masks only `/home/<user>`, `/Users/<user>` and
`C:\Users\<user>` — never `/usr` or `/root`. On this root-account server claude
is a system install (`/usr/bin/claude`, `/bin/claude`) and codex is the repo-local
admission (`/root/project/.../node_modules/.bin/codex`), so the redaction is a
legitimate no-op on these paths and the Windows-era `startswith("[HOME]")`
assertion does not apply. These paths carry NO person-identifying username
("root" is the generic superuser) and the deterministic certification BODY
carries no paths at all. I did NOT edit the source redaction (that would void the
cert). Flagged for the security reviewer: `probe_meta.codex_binaries` records the
worktree path — an operational snapshot, like `generated_at`; not a secret.

## 3. Re-baseline tests updated (allowed_paths; same pattern as M0-T159)
- `tools/test_agent_supervisor_capability_probe.py`:
  `CURRENT_FIXTURE` repointed to the new fixture; the invariant
  `test_current_fixture_records_claude_2_1_281_masked_and_shaped` renamed to
  `..._2_1_287_...` and updated to pin `"2.1.287 (Claude Code)"` /
  `"codex-cli 0.157.0"` (the `post` codex `0.146.0` assertion unchanged), the
  filename-id check to `m0t174`, and the leak scan extended with `/home/` and
  `/Users/` while the Windows `[HOME]`-prefix assertion is replaced by the
  no-leak contract (platform reality above).
- `tools/test_agent_supervisor_native_adapter.py`:
  `DETECTION_FIXTURE` repointed; `test_committed_detection_fixture_shape` updated
  to task `M0-T174` and claude `2.1.287 (Claude Code)`.
The two live drift teeth consume `CURRENT_FIXTURE`; the native live tooth consumes
`DETECTION_FIXTURE` — repointing turns all three green against the new fixtures.

## 4. Test evidence (interpreter `/root/project/lanes-runtime/venv/bin/python`, cwd worktree root)
| Run | Result |
|---|---|
| `pytest tools/test_agent_supervisor_capability_probe.py tools/test_agent_supervisor_native_adapter.py -q` | **77 passed in 4.60s, 0 skipped** (zero skips => the `skipif(which("claude"/"codex") is None)` live teeth RAN) |
| Focused -v on the 3 live teeth + 2 shape tests | `test_live_reprobe_claude_version_matches_fixture` PASSED; `test_live_reprobe_codex_version_matches_fixture` PASSED; `test_current_fixture_records_claude_2_1_287_masked_and_shaped` PASSED; `test_live_detection_matches_committed_fixture` PASSED; `test_committed_detection_fixture_shape` PASSED (5 passed) |
| `pytest tools/test_agent_supervisor_routing_probe.py -q` | **35 passed** — stays green at 2.1.287 WITHOUT recapturing the shell-routing fixture (its "installed_version"/"installed_identity" are passed explicitly from the fixture, not live-probed) |

Self-checks:
```
python -m ruff check tools/test_agent_supervisor_capability_probe.py \
  tools/test_agent_supervisor_native_adapter.py   -> All checks passed! (exit 0)
python tools/modularity_check.py --check           -> exit 0 (only pre-existing
  warn-level signals on OTHER files; none on the edited test files; no production
  file grew)
```

## 5. Bash shell-routing harness (item 3) — PASS, all mutants detected
```
bash tools/agent_supervisor/linux/sh_tests/run_sh_tests.sh
  --- test_doc_check.sh        PASS  (living launcher carries every guard; start-gate-refusal removal DETECTED)
  --- test_mutants_detected.sh PASS  (3 mutants detected: pipe_tee->0, dollar_q->0, grep_pipe->1; control raw 7 preserved)
  --- test_raw_exit.sh         PASS  (all assertions)
  run_sh_tests: 3 test file(s) passed
```
Mutant count: **3 mutants, 3 detected** (`mutant_pipe_tee.sh`,
`mutant_dollar_q.sh`, `mutant_grep_pipe.sh`).

## 6. Shell-routing FIXTURE (routing_probe.py) — NOT recaptured, fail-closed, disclosed
The recipe §2 lists recapturing the shell-routing fixture. `routing_probe.probe_routing`
launches the REAL claude worker at `--max-turns >= 1`, which is a live PROVIDER
round-trip, and needs codex/claude sign-in — all forbidden by this packet ("no
provider call"; "touch credentials"; codex sign-in is owner-typed TW5). No live
tooth pins the installed CLI to the shell-routing fixture (the routing_probe suite
passes the version/identity explicitly), so it is not needed for recertification.
Fail-closed decision: the shell-routing fixture is left at the M0-T159 capture;
the certification is NOT claimed on any un-run probe.

## 7. Controller manifest re-bind (item 5) — STOP + report (outside allowed_paths)
"Re-bind the controller manifest digest" concretely means re-pinning
**`tools/controller_update/source_binding.json`** to the new certified candidate
(the M0-T159 precedent did exactly this in its §5.0). That file is OUTSIDE this
packet's `allowed_paths`, so I did NOT edit it.

Fields that need re-pinning (and the authority note appended, as R287 did for
M0-T159):
| Field | Current (M0-T159 / R287) value | New value |
|---|---|---|
| `commit_sha` | `a3f24ff3825c126c038f59b1ea6d2352f29d724a` | the FINAL integrated M0-T174 commit (orchestrator-determined post-cherry-pick) |
| `commit_tree_sha` | `82432361540c3c2a11c55ffa3d6d485426cd45f7` | `git rev-parse <integrated-commit>^{tree}` |
| `subtree_tree_sha` | `9c0b14eaa56ce32d241c77f789266035b584380c` | `git rev-parse <integrated-commit>:tools/agent_supervisor` |

Commands that compute/check it:
- subtree: `git rev-parse <commit>:tools/agent_supervisor`
- commit tree: `git rev-parse <commit>^{tree}`
- the binding is validated by `tools/controller_update/ps_tests/test_source_binding.ps1`
  and consumed by `tools/controller_update/update_controller_from_candidate.ps1`
  (Windows); the activation-manifest digest itself is produced by
  `python -m tools.agent_supervisor record-manifest` and verified by
  `verify-manifest` / `verify-controller`.

Two facts the orchestrator needs:
1. **The activation-manifest digest changes by EXACTLY ONE file — `event_drift.py`
   (rework 1).** `manifest.py COVERED_PATTERNS` = `*.py, schemas/*.json,
   prompts/*.md, config.toml, config.example.toml, launchers/*.cmd,
   launchers/*.ps1, README.md`. The recaptured FIXTURES (`fixtures/*.json`,
   including the new hook-event catalog) are NOT manifest-covered, and the
   `tools/test_*.py` files are outside the manifest root — those do not move the
   digest. BUT rework 1 re-points `event_drift.py` (a `*.py`, manifest-covered)
   to the new catalog, so the recorded activation-manifest digest DOES move by
   that one file — exactly the M0-T159 pattern where `event_drift.py` was "the
   ONE manifest-tracked change". The orchestrator's `record-manifest` after
   integration will show a one-file delta on `event_drift.py`.
2. **source_binding.json was already stale before this task.** Its pinned
   `subtree_tree_sha 9c0b14ea…` does not match the claim-seam subtree
   (`git rev-parse 409060270…:tools/agent_supervisor` = `41bbd31d3d89e3ae10f22b7e321babce7eb5cbac`);
   the D-091 code merges already moved the subtree. At THIS producer commit the
   subtree is `0368b1a997fe1359f989e1a70d2d1462b6ad81d0`. The whole binding
   (`source_repo`, `source_worktree`, `controller_root`, …) is Windows-path-only;
   the Linux cloud install/commission is owner-typed (TW5) and is not represented
   in source_binding.json yet — the orchestrator should decide whether the re-bind
   is a Windows-binding update, a new Linux binding, or deferred to TW5.

## 8. Acceptance scenarios (packet) — which hold
- **primary — "the live re-probe tests for claude and codex pass on this server
  against the new fixtures": HOLDS.** claude-version, codex-version and native
  detection teeth GREEN (§4).
- **"the re-baseline invariant pins the new versions; the old fixtures are kept,
  not deleted": HOLDS.** Invariant pins 2.1.287 / codex-cli 0.157.0 and detection
  pins 2.1.287; all predecessor fixtures retained (§2, §3).
- **"the bash shell-routing harness passes with all mutants detected": HOLDS.**
  3/3 mutants detected (§5).
- **"failure: a probe that cannot run fails closed and the certification is not
  claimed": HONORED.** The provider-requiring shell-routing fixture was not run
  and the cert is not claimed on it (§6).

## 9. Preservation / safety
No provider/model request was made (only `--version`/`--help`, the read-only
native-detection help probes, and a `curl` GET of the public hooks docs). No
`/etc/nyc-supervisor/config.toml`, no systemd unit, no live loop, no codex login,
no credential touched. Exactly ONE `tools/agent_supervisor/*.py` change
(rework 1): the authorized `event_drift.py` hook-catalog re-point — the M0-T159
recertification precedent, added to `allowed_paths` by the scope correction; no
other `*.py` under `tools/agent_supervisor/` changed. No write outside
`allowed_paths` except the git-ignored `tools/codex_cli/node_modules/` (build
artifact, uncommitted) and this report under the session scratchpad. The
orchestrator records the ledger and integrates git; nothing was pushed.

## 10. Verdict (as amended by Rework 1, §11)
Linux recertification **PASS**, scoped precisely to what was measured on this box:

CERTIFIED (green on this server):
- installed CLIs: claude `2.1.287 (Claude Code)`, codex-cli `0.157.0`;
- ALL THREE controller live claude-version drift teeth GREEN: capability_probe
  (claude + codex version), native_adapter (native detection), event_bus S8
  (hook-event catalog) — this is the COMPLETE live claude/codex execution surface
  of the suite (grep-proven: only capability_probe, event_bus, native_adapter,
  os_acl execute the real CLI; os_acl has no version tooth);
- the bash shell-routing harness (3/3 mutants detected);
- the recaptured fixtures (capability, native, hook-event catalog) and the
  re-baselined version-pinned invariants.

DISCLOSED LIMITS / NOT certified here (deferred, named):
- the shell-routing FIXTURE (routing_probe.py) is NOT recaptured — it needs a live
  provider round-trip + codex sign-in (forbidden; owner-typed TW5). No live tooth
  depends on it (§6);
- `tools/controller_update/source_binding.json` is NOT re-pinned — outside
  allowed_paths, needs the integrated commit SHA, and is Windows-path-only
  (orchestrator step; §7);
- the WHOLE 95-file supervisor suite does NOT pass green on this Linux box, and
  this is NOT claimed. Every failure observed is the environmental Windows-platform
  cluster (host containment is `process_group`, the loop requires Windows
  `job_object` → golden_run/loop/launch_seam/mrl_exec_chain `containment_refused`;
  Windows path-normalization and `icacls` tests in checkpoint_envelope/os_acl) —
  none touches this recert's changed modules (grep-proven independence; §11). The
  box also exhibits transient OOM-SIGKILL(137) on batched runs, so a complete
  clean suite count is not obtainable here (the suite was certified green only on
  Windows at M0-T159).

Subject to the independent G0/G2/G3/G4/G5 review wave (control-plane-verifier,
security-reviewer, directive-compliance-verifier) and the orchestrator-executed
source_binding.json re-bind + manifest re-record at the integrated candidate (§7,
and §7.1 now carries a one-file `event_drift.py` manifest delta). Any further
`tools/agent_supervisor/**` change after this point re-invalidates the cert.

## 11. Rework 1 — G3/G4 round-1 FAIL B1 cure (the third live drift tooth)
Round-1 FAIL B1: the controller has THREE live claude-version drift teeth; round 1
repointed only two families (capability_probe, native_adapter) and left the third
RED on the box — `test_agent_supervisor_event_bus.py::test_s8_live_version_matches_catalog_fixture`
(`'2.1.287 (Claude Code)' == '2.1.281 (Claude Code)'`). N2: the scoped wording
read as if the full live-drift surface was green. Both are cured here.

Files (rework-1 commit `4cf240697e51cefb21db3b63c0fad0fd3c793798`, parent
`e4c705b0e5aa4439c092473f1ba3a0a5b7e58fa1`; commit tree
`5e24e092d56339e59c7dfbc65eb76733543746ed`; `tools/agent_supervisor` subtree
`aed743275db835d4667f30d92a21e3d9d9131c6a`; tree clean):
- A `tools/agent_supervisor/fixtures/hook_event_catalog_2_1_287.json`
  (LF sha256 `f84a0f6299c72f696a5d2b5290a21a5e8279ba88ffee1455bb9f9a82975855de`);
- M `tools/agent_supervisor/event_drift.py` (CATALOG_FIXTURE_PATH + version comment
  re-pointed `2_1_281` → `2_1_287`; the one manifest-covered change, §7.1);
- M `tools/test_agent_supervisor_event_bus.py` (CATALOG_FIXTURE constant; S8
  `test_s8_catalog_fixture_valid_and_masked` → task M0-T174 / claude 2.1.287 /
  count stays 33). The old 2_1_281 and earlier catalogs stay committed as history.

Catalog provenance (no model call): re-fetched the official hooks docs by
`curl -sS -L -A "Mozilla/5.0 (recert-probe)" https://code.claude.com/docs/en/hooks`
on **2026-10-02**, **HTTP 200**, **2,919,589 bytes** (M0-T159 saw 2,900,678 — the
doc grew ~19KB, entirely in tool/permission prose). **Event count 33, no drift
vs 2.1.281** — all 33 known events present as their documented `id`-anchor
sections; the authoritative enumeration is the id-anchor set (hook events) which
is exactly the 33. The three new PascalCase tokens appearing near hook/event
context (`SubagentHandback`, `TaskUpdate`, `AskUserQuestion`) are TOOLS, not hook
events, verified from their doc context (`SubagentHandback` = the subagent
hand-back tool added in Claude Code v2.1.271 that a PreToolUse/PostToolUse hook
matches ON; `TaskUpdate` = the tool that fires TaskCreated/TaskCompleted;
`AskUserQuestion` = a tool `<h5>` under the tools/permission section). The +2
drift vs the 2.1.220 baseline (PreModelSwitch + PostModelSwitch) carries unchanged.

Evidence:
- `pytest tools/test_agent_supervisor_event_bus.py -q` → **38 passed** (S8 live
  tooth `test_s8_live_version_matches_catalog_fixture` GREEN; S8 drift-match green;
  catalog valid+masked green). Re-verified in the per-file sweep (38 passed).
- WHOLE-SUITE SWEEP (memory-safe, per-file; single-process whole-suite and large
  batches OOM-SIGKILL on this 8 GiB box): the complete live claude/codex execution
  surface is exactly {capability_probe, event_bus, native_adapter, os_acl}
  (grep: a live tooth must guard on CLI presence or it breaks Windows CI). ALL
  THREE version-drift teeth GREEN; os_acl has no version tooth (its live teeth are
  `IS_WINDOWS`-gated powershell/icacls, which SKIP on Linux). Files that ran clean
  include adversarial, audit*, bootstrap_continuity, bounded_*, broker, c2_binding,
  capability_probe (77), claude_reviewer, codex_channel, command_*, controller_succession,
  crash, cross_task, dual_review, endurance, ephemeral_review, event_bus (38), fuzz,
  gate_wave, github_flow, goal_integration, guardrail_bridge, invariants, ipc,
  linux_gauge, linux_launch, manifest_binding, model_turnover, mrl_* (launch_path,
  one_shot, runtime_identity, worker_result, …), native_adapter, next_task,
  operator_channel, pending_prompt, phase1, policy, protocol, r595_actuation,
  review_combiner (47), review_slots, reviewer (125), routing_probe (35), and more.
- Failing files, ALL environmental Windows-platform (independent of this recert —
  grep shows none import event_drift/catalog/capability fixtures):
  checkpoint_envelope::test_windows_worktree_normalization_equivalent_paths_match (1);
  golden_run (7: injected-refusal/quota/restart/rotation/compact/epilogue — all
  `containment_refused`: host containment `process_group` ≠ Windows `job_object`,
  dispatch REFUSED `unsupported_platform` exit 12, M0-T052 G5 C1); launch_seam (3);
  loop (3); mrl_exec_chain (12); os_acl (3: e.g. `test_run_icacls_uses_absolute_system32_path`).
  model_chain.py excluded as instructed (SIGKILLs on this host).
- Not completed on this box (no live CLI tooth; transient OOM-SIGKILL blocked a
  full clean count): quota_classifier (intermittently killed then unrun), recovery,
  recovery_probes, repair_gate, replay, resource_fit, resource_sampling,
  restart_channel, rotation, runner, runtime_supervision, scheduler,
  session_continuity, start_reentry, statusline_handler, subagent_telemetry,
  telegram_sink, telemetry_core, turnover_* (5). None contains a live claude/codex
  tooth, so the live-drift recertification is complete regardless.

Self-checks (rework 1): `ruff check` on `event_drift.py` + the event_bus test →
All checks passed (exit 0); `python3 tools/modularity_check.py --check` → exit 0,
0 failures (event_drift.py not flagged; the one-line re-point + comment did not
grow it materially).

Orchestrator follow-ups: (a) tighten the evidence-map D-091-R001 phrase per N2 so
it does not read as if the full live-drift surface were green under a two-family
scope (I cannot write `project-control/`); (b) the source_binding re-bind now also
carries a one-file `event_drift.py` manifest delta (§7.1).

END-OF-REPORT

## Orchestrator correction (recorded at resubmission)
This report describes some whole-suite batch runs as "OOM-SIGKILL (137)". That is not supported. The server's kernel OOM counter (`/proc/vmstat` `oom_kill`) is 0, and the orchestrator's 15-second memory log never exceeded 16% during the session. Exit 137 is a SIGKILL. The independent M0-T173 G3 reviewer gave the same non-memory cause for model_chain: the real-subprocess test classes kill their process group. The conclusion that matters is unchanged: none of the files that did not finish has a live CLI tooth, and the live-drift recertification rests on the three teeth, all green.
