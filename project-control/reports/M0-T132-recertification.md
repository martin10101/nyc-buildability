# M0-T132 — combined R247 recertification + 2.1.252 admission record (D-024 Amendment 34/35)

Executed by the orchestrator (`orchestrator-admission-runner`) in the primary control checkout
`ctl24`, 2026-09-01, campaign seq 65. **ONE combined recertification at ONE final frozen identity**
covering BOTH accepted M0-T131 (the codex-reviewer stdin contract, accepted at `00220b8c` but never
recertified — R431 forbade recert against the obsolete 2.1.251 pin) AND the admitted 2.1.252 runtime
(R441/R442). Supervisor-freeze qualifying evidence: **D-024-R440/R441/R447**.

## 1. The final frozen identity
| Anchor | Value |
|---|---|
| Material commit | the commit bundling this report (branch `control/D-024-fable-codex-loop`) |
| `tools/agent_supervisor` manifest delta | 125 files, digest **`c228b7ca5526840e…`** (from M0-T130's `26a05096…`); the TWO changed files are **`codex_reviewer.py`** (M0-T131's accepted fix, now certified) + **`event_drift.py`** (M0-T132's catalog re-point) — exactly the combined scope |
| Provider CLI (ADMITTED) | Claude Code **2.1.252**, executable digest **`e713c5a6c8bc71af…`** (sha256_head+size), 217,406,624 B; old `d6f6c29a` (2.1.251) retired |
| Codex CLI | codex-cli 0.146.0 unchanged |

## 2. Test evidence at the frozen identity
| Pack | Result |
|---|---|
| Golden certification pack | **42 passed** (30.09s) |
| Four re-pointed packs (event_bus, capability_probe, native_adapter, routing_probe) | **150 passed** |
| Affected packs (recovery_probes, process, claude_runner_env, operator_channel, bounded_mode, start_reentry) | **291 passed, 1 skipped** |
| WHOLE supervisor suite (`tools/test_agent_supervisor_*.py`, one process) | **3,043 passed, 2 skipped, 0 failed** (3,045 collected; 628s) |

**Baseline reconciliation (freeze rule, exact):** M0-T130 recert baseline 3,039 passed / 2 skipped
(3,041 collected) → M0-T131 added 4 test nodes (3,045 collected) and was accepted showing **3,040
passed / 2 skipped / 3 FAILED** — the 3 failures being EXACTLY the CLI-drift live teeth
(`capability_probe::test_live_reprobe_claude_version_matches_fixture`,
`event_bus::test_s8_live_version_matches_catalog_fixture`,
`native_adapter::test_live_detection_matches_committed_fixture`) stuck on
`'2.1.252 (Claude Code)' == '2.1.251 (Claude Code)'`. **This admission RESOLVES all three**: 3,040 + 3
= **3,043 passed, 0 failed**, same 3,045 collected, 2 skipped. No test removed, no unexplained drift.

## 3. R282-style admission pass-list (2.1.252)
| Item | Evidence |
|---|---|
| Fixtures | Four measured 2.1.252 fixtures (capability_probe, hook_event_catalog [33 events, docs re-fetched 2026-09-01, no drift], native_runtime_detection, shell_routing) — old 2_1_251 pack kept append-only |
| Drift teeth | The three version teeth **GREEN at 2.1.252** and removal-sensitive (the routing tooth bit version drift during development); S8/capability/native live teeth match the installed 2.1.252 |
| Live probes | capability + native probes measured live (bounded --version/--help); **shell-routing measured live at `e713c5a6` on the approved worker model `claude-opus-4-8`** — verdict `native_preferred`, 3 native tool uses, Edit brokered+denied (this observed a live **`can_use_tool` control request** at 2.1.252 — the control protocol works) |
| Golden suites | 42/42 at this identity (§2) |
| Manifest binding | 125-file manifest `c228b7ca…` recorded, external `config.toml` bound, round-trip verified; **`verify-controller` PASS**; **`doctor` (non-live) overall PASS** |
| Combined scope | codex_reviewer.py (M0-T131) + event_drift.py (M0-T132) both bound at the one final tree |

**ADMITTED: Claude Code `2.1.252` (executable digest `e713c5a6c8bc71af…`; codex-cli 0.146.0
unchanged).** The one-time `--repin-cli-identity` on the next certified start (R285 precedent)
completes the admission at the journal level (a per-launch owner act, deferred — §5).

## 4. Honest disclosures (Fable-cap artifacts; not certification failures)
1. **Shell-routing captured on `claude-opus-4-8`, not Fable 5** (R447/R448): the routing probe's bare
   `claude` uses the account-default (Fable 5), which is under its seven-day usage cap and rejects
   model calls; `claude-opus-4-8` is APPROVED in `config.toml` and is the model the loop runs under
   while Fable is unavailable, so it is the correct capture model. Routing behavior (`native_preferred`)
   reproduces the M0-T120 verdict; the gate keys on the `e713c5a6` digest, which is stamped. Fully
   reproducible: `project-control/reports/M0-T132-routing-capture.py`.
2. **`doctor --live` control-response probe FAILED (Fable-cap artifact, NOT a protocol break, NOT a
   start gate).** The probe (`preflight.control_response_round_trip`) hardcodes the account-default
   model (Fable) and ignores `--model-selection`; under the cap its worker emits no tool → no
   `can_use_tool` request → the wrapper is "never exercised". This is the SAME cap, not a 2.1.252
   protocol change: the M0-T132 routing probe **did** observe a live `can_use_tool` brokered request at
   `e713c5a6` on opus. The start's pre-dispatch (`run_live_probes`) relies on `cli_capability_manifest`
   + `shell_routing`, **not** a live control-response round-trip, so this does not gate the start.
   A fresh `doctor --live` once Fable is available re-records it VERIFIED (an S8.5 follow-up).
3. **Journal probe-record touch (transitions/audit INTACT):** running `doctor --live` overwrote the
   journal's `control_response_round_trip` probe record (previously VERIFIED@`d6f6c29a`, the now-stale
   2.1.251 identity) with a FAILED@`e713c5a6` — a designed doctor side effect and part of the S8.5
   admission re-verification (M0-T119 recorded this probe the same way). **`journal_integrity`
   transitions = 35 and `audit_chain` = 85 are UNCHANGED** (preservation-critical state intact); the
   replaced probe was for an identity no longer installed, and the honest current state (FAILED under
   cap / to be re-VERIFIED on opus or when Fable returns) is more truthful than a stale VERIFIED.

## 5. Deferred to owner-typed commissioning (NOT done here)
- **Stored controller-manifest overwrite.** The certified stored manifest at
  `%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json` still holds the
  old `26a05096…`. Re-recording it to `c228b7ca…` (writing the certified activation manifest) is a
  consequential operator act and is presented as an owner-typed step (§6 of the seam report). The
  recert's binding proof stands on the re-recorded manifest + verify-controller/doctor PASS.
- **Journal CLI-identity repin** (`start --repin-cli-identity`) — per-launch owner act (R285).
- **Runtime model pin** `model_selection.toml [claude] model = "claude-opus-4-8"` — required to run
  under Fable unavailability (opus is approved; R447). Presented, owner-typed.

## 6. Preservation (R443/R444)
Journal HALTED, transitions **35**, audit **85** — unchanged (only the stale control-response probe
record was refreshed, §4.3). No supervisor start, no journal clear/restart, no reset, no PR #241
action. `wt-m0t107` `c5c6ff7` + its two untracked drafts, `wt-m0t109` `1c06957`, queue digest
`11eaa5a7`, owner-touch 3-of-2, budgets — all preserved. This unit wrote only its allowed_paths
(event_drift.py, four 2_1_252 fixtures, four fixture-consuming test files) + its reports + control-plane
records.

## 7. Verdict
R247 combined recertification: **PASS at the one final frozen identity** (manifest `c228b7ca…`;
admitted CLI `2.1.252`/`e713c5a6`), covering accepted M0-T131 + the admitted 2.1.252 runtime, subject
to the independent G3/G4 + DCV wave. Any supervisor/operator-channel change after this point
re-invalidates certification and re-triggers R247.
