# M0-T179 (D-091) — Linux recertification of the supervisor after M0-T177 and M0-T178 (supersedes M0-T174)

Producer: `backend-engineer`, in the assigned isolation worktree `/root/project/w-M0-T179`
(branch `task/M0-T179-linux-recert-2`), cut at the claim-seam commit
`0796efb16a879bd9d6001f7d0baa49bbc8633749`. Worktree guard confirmed BEFORE any work:
`git rev-parse --show-toplevel` == `/root/project/w-M0-T179`, branch
`task/M0-T179-linux-recert-2`, HEAD `0796efb1…`. Recipe: `docs/D091_WAVE3_WIRING_PLAN.md` §2;
precedents: `project-control/reports/M0-T174-producer-report.md` (superseded) and
`M0-T159-recertification.md`. All probes are local — NO provider call (version/help only), NO
systemd/config/credential step. Interpreter `/root/project/lanes-runtime/venv/bin/python`
(Python 3.12.3); cwd = worktree root unless noted.

## VERDICT UP FRONT — NOT CERTIFIED (fail closed; blocked on scope)

**The Linux recertification is NOT claimed.** The installed `claude` CLI auto-updated from
`2.1.287` (M0-T174's certified version) to **`2.1.288`** at some point after M0-T174 was
accepted. That drift turns ALL THREE live claude-version drift teeth RED against the certified
tree's `*_2_1_287` fixtures (reproduced below, §3). Two of the three (capability_probe,
native_adapter) are curable inside this packet's `allowed_paths`. The THIRD — the **event_bus S8
live tooth** — is NOT curable inside `allowed_paths`: making it green requires re-pointing
`tools/agent_supervisor/event_drift.py` `CATALOG_FIXTURE_PATH` to a new `2_1_288` catalog, which
is a `tools/agent_supervisor/*.py` source change that this packet's `forbidden_paths` prohibits
and that would itself re-trigger the certification. Per the packet's own rule ("If any tooth
cannot [be made to] pass, fail closed: say so and do NOT claim the certification") and the M0-T174
round-1 precedent (a cert that left the event_bus S8 tooth red was FAILED at G3/G4, B1), the cert
cannot be claimed as scoped. I made **no edits to the certified tree** (it stays byte-identical to
the accepted M0-T174+M0-T177+M0-T178 tree); this report is the only file written. Remediation for
the orchestrator is in §8.

## 0. Producer / tree identity
| Anchor | Value |
|---|---|
| Worktree / branch | `/root/project/w-M0-T179` / `task/M0-T179-linux-recert-2` |
| Claim-seam commit (base) | `0796efb16a879bd9d6001f7d0baa49bbc8633749` |
| `tools/agent_supervisor` subtree at HEAD | **`5d67e2e4a9b11a56cef0f65c4057ba7f22f793ac`** (`git rev-parse HEAD:tools/agent_supervisor`) |
| commit tree at HEAD | `d0c751d8b7282bfc8f4b601bbaeea1ca8835bda3` |
| Tree edits made by this task | **NONE** to `tools/agent_supervisor/**`; only this report added (outside the subtree, so the certified subtree hash is unchanged by my producer commit) |

Because no source, fixture or test file was changed, the `tools/agent_supervisor` subtree I would
certify is exactly `5d67e2e4…` — the subtree of the accepted M0-T177 (B-027) + M0-T178 (DB-103)
tree. The producer commit adds only `project-control/reports/M0-T179-producer-report.md`.

## 1. Installed CLIs on this server (version probes only — no provider call)
| Tool | `--version` first line | M0-T174 value | Changed? | Path(s) |
|---|---|---|---|---|
| Claude Code | **`2.1.288 (Claude Code)`** | `2.1.287 (Claude Code)` | **YES (2.1.287 → 2.1.288)** | `/usr/bin/claude` (system install) |
| Codex CLI | `codex-cli 0.157.0` | `codex-cli 0.157.0` | no | `/opt/nyc-codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex`; also on PATH as `/usr/local/bin/codex` (same digest; installed from the admitted `tools/codex_cli/package-lock.json`) |

`claude --version` printed `2.1.288 (Claude Code)` on two consecutive probes (stable, not
transient). This is the same auto-update drift class the capability-probe suite already documents
(2.1.246→2.1.247→2.1.248 across prior units). Per the packet's step 1, a changed version means
"recapture per M0-T174 §2" — but see §2/§8: the recapture cannot be completed inside this
packet's `allowed_paths`.

## 2. The blocking scope conflict (event_bus S8 vs forbidden event_drift.py)
- The event_bus S8 live tooth `test_s8_live_version_matches_catalog_fixture`
  (`tools/test_agent_supervisor_event_bus.py:345-356`) compares live `claude --version`
  against `ed.load_catalog_fixture()["claude_version"]`. It calls `load_catalog_fixture()`
  **with no path argument**, so it resolves `event_drift.py`'s module-level
  `CATALOG_FIXTURE_PATH` (`tools/agent_supervisor/event_drift.py:45-46`), hardcoded to
  `fixtures/hook_event_catalog_2_1_287.json` → recorded version `2.1.287 (Claude Code)`.
- To turn this tooth green at claude 2.1.288 the ONLY sound fix is to re-point
  `event_drift.py` `CATALOG_FIXTURE_PATH` to a new `hook_event_catalog_2_1_288.json` (exactly
  what M0-T174 did in its round-1 rework). `event_drift.py` is a `tools/agent_supervisor/*.py`
  source file. This packet's `forbidden_paths` explicitly bans "any `tools/agent_supervisor/*.py`
  source change", and `event_drift.py` is NOT in `allowed_paths`.
- Working around it by editing the event_bus test to load a `2_1_288` catalog via an explicit
  path would make the test GREEN while production `load_catalog_fixture()` still loads the stale
  `2_1_287` catalog — a false certification that defeats the tooth's purpose (it exists to prove
  production is pointed at the right catalog). Rejected.
- M0-T174 accepted exactly one `tools/agent_supervisor/*.py` edit (the `event_drift.py` catalog
  re-point) only because the orchestrator issued a **scope correction** adding `event_drift.py`
  (and the event_bus test) to that task's `allowed_paths`. ADR-005 reserves scope changes to the
  orchestrator; a producer cannot widen its own scope. Hence this is an orchestrator decision.

## 3. Teeth — each run with command, cwd, interpreter, exit code, result
cwd = `/root/project/w-M0-T179`; interpreter `/root/project/lanes-runtime/venv/bin/python` for
pytest, `/usr/bin/bash` for the harness. The exact test ids are the ones M0-T174 ran (its §4/§11).

| Tooth | Command | Result |
|---|---|---|
| capability_probe — live claude reprobe | `pytest … capability_probe.py::test_live_reprobe_claude_version_matches_fixture` | **FAIL** — `assert '2.1.288 (Claude Code)' == '2.1.287 (Claude Code)'` (drift) |
| capability_probe — live codex reprobe | `pytest … capability_probe.py::test_live_reprobe_codex_version_matches_fixture` | **PASS** (codex unchanged at 0.157.0) |
| native_adapter — live detection | `pytest … native_adapter.py::test_live_detection_matches_committed_fixture` | **FAIL** — `assert '2.1.288 (Claude Code)' == '2.1.287 (Claude Code)'` (drift) |
| event_bus — S8 live version | `pytest … event_bus.py::test_s8_live_version_matches_catalog_fixture` | **FAIL** — `installed claude drifted from the committed hook-event catalog fixture`; `'2.1.288' == '2.1.287'` (drift; **not curable in scope — §2**) |

Combined run of the four live teeth: `3 failed, 1 passed in 2.78s` (exit 1). The 3 failures are
the 3 **claude**-version drift teeth; the codex tooth passes.

Non-version teeth (all GREEN — version-independent, so the rest of the certification surface is
sound):

| Tooth | Command | Result |
|---|---|---|
| bash shell-routing harness + mutants | `bash tools/agent_supervisor/linux/sh_tests/run_sh_tests.sh` (direct exit) | **PASS, exit 0** — `3 test file(s) passed`; **3 mutants detected** (`mutant_pipe_tee`→0, `mutant_dollar_q`→0, `mutant_grep_pipe`→1; control raw 7 preserved) + the start-gate-refusal removal detected |
| Linux containment suite (no R3) | `pytest … test_agent_supervisor_linux_containment.py -k "not R3"` | **PASS** — `42 passed, 1 deselected`, exit 0 |
| containment R1 (single id) | `pytest …::LinuxContainmentRealProcessTests::test_R1_timeout_kill_spares_the_harness_and_worker_has_its_own_group` | **PASS** — `1 passed` (3.16 s) |
| containment R2 (single id) | `pytest …::LinuxContainmentRealProcessTests::test_R2_group_kill_of_harness_leaves_a_setsid_grandchild_alive` | **PASS** — `1 passed` (1.89 s) |
| dual_review suite (M0-T178 DB-103) | `pytest … test_agent_supervisor_dual_review.py` | **PASS** — `21 passed`, exit 0 |

R3 (`R3RealSystemdUnitTests::test_R3_kill_of_main_pid_reaps_the_whole_control_group`) was **NOT
run on this host** (needs a real systemd transient unit; packet forbids systemd-run / live start).
It is cited from CI in §4. Whole `RealProcess` classes and the whole `model_chain.py` were NOT run
here (packet forbidden; R1/R2 were run by single id only, as instructed).

## 4. Containment on this host + CI real-unit R3 proof
- This host's default containment:
  `python3 -c "from tools.agent_supervisor import process; print(process.default_containment_kind())"`
  → **`process_group`** (exit 0). Correct by design (M0-T177 B-027): on this box euid is 0 and the
  cgroup is a `.scope`, so the systemd-service proof refuses and the loop would REFUSE to dispatch
  outside a hardened `.service` — nothing is newly enabled here. The containment suite's
  `process_group`/`taskkill` refusal teeth are among the 42 that pass.
- Real-unit R3 proof (cited; not run here): the additive `supervisor-linux-containment` ubuntu CI
  job ran `test_R3_kill_of_main_pid_reaps_the_whole_control_group` GREEN — **run 37072153749, job
  111053843200 at 8fc412e0**. The orchestrator confirmed the same job GREEN on the merged heads of
  **PR #344 and PR #345** (both PRs' CI fully green before merge).

## 5. Supervisor-freeze baseline (cited; not run here — host safety)
The whole supervisor glob was deliberately NOT run on this Linux host (documented OOM/exit-137
history on the whole-suite single process; packet host-safety bound). The supervisor-freeze
baseline is re-established by CI **`supervisor-bridge` (windows-latest, the whole supervisor
glob)** GREEN on the merged heads of **PR #344 and PR #345** (orchestrator-attested; the
≥1165-test freeze baseline is a CI responsibility, `.claude/rules/supervisor-freeze.md` §4).

## 6. Recapture feasibility (proven to scratch; certified tree NOT modified)
To confirm the §2 blocker is the only obstacle (not a broken probe), I ran the capability probe to
a **scratch** path, leaving the tree byte-clean:
```
python -m tools.agent_supervisor.capability_probe --out <scratch>/cap_probe_288.json   → exit 0
→ claude_version.first_line = "2.1.288 (Claude Code)"; codex_version.first_line = "codex-cli 0.157.0"
git status --porcelain → (clean)
```
So the capability + native fixtures CAN be recaptured to 2.1.288 inside `allowed_paths`
(`tools/agent_supervisor/fixtures/`, `test_agent_supervisor_capability_probe.py`,
`test_agent_supervisor_native_adapter.py`) — but doing only those two while `event_drift.py` stays
pinned at the 2_1_287 catalog would leave the tree internally inconsistent (two drift families at
2.1.288, the event-catalog family at 2.1.287) and still would not let the cert be claimed. I
therefore made **no** partial recapture; the three drift families must be recaptured together once
the scope is corrected (§8). The probe uses `--version`/`--help` only (enforced by
`test_probe_allowlist_is_read_only`): no provider/model round-trip.

## 7. What remains owner-typed (unchanged from M0-T174/M0-T159; commissioning = M0-T175)
None of these was performed; they are owner-typed, not agent-executable:
- create the root-owned `/etc/nyc-supervisor/config.toml`;
- Codex sign-in (and therefore the live shell-routing / routing_probe fixture, which needs a
  provider round-trip) — deferred to commissioning;
- `record-manifest` + `verify-controller` / `verify-manifest` on the installed tree;
- systemd unit install and the live `start`;
- the activation-PIN amendment **D-091-R009** is owner-applied.
The `tools/controller_update/source_binding.json` re-pin is likewise outside this packet and is a
Windows-path-only / owner B-026 decision.

## 8. Remediation recommended to the orchestrator (blocker)
This is a SCOPE blocker created by an environmental fact (claude auto-updated 2.1.287→2.1.288).
Recommended path — the same shape M0-T174 round-1 took:
1. Orchestrator issues a scope correction: add `tools/agent_supervisor/event_drift.py` to
   M0-T179's `allowed_paths` (with the source-change prohibition excepting that one catalog
   re-point), and flip the packet premise from "cite existing m0t174 fixtures" to "recapture all
   three drift families for 2.1.288" (old `*_2_1_287` fixtures kept as history). Re-record G0 at
   the corrected head.
2. Then one consistent recapture pass (all inside the corrected `allowed_paths`):
   - `capability_probe_live_<date>_m0t179_2_1_288.json` + repoint `CURRENT_FIXTURE` and update the
     re-baseline invariant to 2.1.288 (rename `…_2_1_287_…` → `…_2_1_288_…`, filename-id `m0t179`);
   - `native_runtime_detection_<date>_m0t179.json` + repoint `DETECTION_FIXTURE` and
     `test_committed_detection_fixture_shape` to 2.1.288;
   - `hook_event_catalog_2_1_288.json` (re-fetch the official hooks docs by `curl`, no model call;
     count events; record reconciled drift) + re-point `event_drift.py` `CATALOG_FIXTURE_PATH` and
     the event_bus `CATALOG_FIXTURE` + S8 shape test to 2.1.288.
3. All three live drift teeth then green at 2.1.288; the non-version teeth already pass (§3); the
   cert can then be claimed. (A later re-record of the activation manifest would move by the one
   manifest-covered file `event_drift.py`, as at M0-T159/M0-T174 — an orchestrator step.)

Alternatively, if the owner prefers to pin the host claude back to 2.1.287 (owner-typed), the
existing m0t174 fixtures would match and the cert could be claimed with no tree change — but a pin
is an owner action, not an agent one.

## 9. Preservation / safety
No provider/model request was made (only `--version`/`--help` probes and the capability probe to a
scratch path). No `/etc/nyc-supervisor/config.toml`, no systemd unit, no `systemd-run`, no live
loop, no codex login, no credential touched, no supervisor killed. R3 and whole `RealProcess`
classes and the whole `model_chain.py` were NOT run on this host (packet-forbidden). Zero edits to
`tools/agent_supervisor/**`; the certified subtree stays `5d67e2e4…`. The only write is this report
under `project-control/reports/` (in `allowed_paths`); the scratch probe wrote only under the
session scratchpad. Nothing pushed; no `tools/project_control.py` run (orchestrator-only, ADR-005).

## 10. Acceptance scenarios (packet) — status
- identity: HOLDS (subtree `5d67e2e4…` pinned; CLIs recorded — claude **2.1.288 ≠ M0-T174's 2.1.287**, codex 0.157.0 unchanged). The "matching M0-T174's or recapturing" branch resolves to "recapture", which cannot complete in scope (§2/§8).
- teeth: **NOT MET** — the 3 claude-version drift teeth are RED at 2.1.288 (codex tooth green); one of them (event_bus S8) is not curable in `allowed_paths`.
- shell harness: **HOLDS** — passes, every mutant detected (§3).
- containment: **HOLDS** — suite green here (42 + R1 + R2), default kind `process_group` (refusal by design), real-unit R3 cited from CI (§4).
- baseline: **HOLDS (cited)** — `supervisor-bridge` windows-latest green on #344/#345 merged heads (§5).
- failure: **HONORED** — the un-greenable tooth fails closed and the certification is NOT claimed.

Subject to the orchestrator's scope decision (§8). Requested status: **blocked**.

END-OF-REPORT
