# M0-T123 — G5 security review (VERBATIM reviewer return; saved by the orchestrator, transport entity-decoding only)

I have completed all seven verification areas. Here is my G5 report.

---

# G5 SECURITY REVIEW — M0-T123 (Resume-path enforcement seam)

**Frozen head:** `10cebf0` (`git rev-parse HEAD` → `10cebf0d167e...`) — verified. Reviewed material identity = work commit `6aada29`.
**Reviewer:** security-reviewer (read-only). I did not write any file and never wrote the preserved runtime dir / transcripts (read-only hashing only).
**Tests:** `python -m pytest tools/test_agent_supervisor_launch_seam.py tools/test_agent_supervisor_command_authority.py -q` → **90 passed** (45+45); `…loop_turnover.py …session_continuity.py -q` → **11 passed**.

## Verdict summary
No SEC-MAJOR. One SEC-MINOR (latent, no reachable bypass; redundantly covered). The enforcement seam refuses before provider contact on every reachable over-ceiling resume, missing-telemetry resume, and cwd mismatch; the four preserved sources are byte-identical; no secrets; no weakening of policy/broker/breakers/budgets/audit/restart_channel; the fixture is structural shape only. **VERDICT: PASS** (SEC-MINOR is a non-blocking hardening recommendation).

## 1. Fail-closed completeness (Q1) — PASS
The pure seam `launch_seam.enforce_launch` (launch_seam.py:305-323) evaluates cwd (evaluate_cwd:234-266) then ceiling (evaluate_ceiling:269-302); `enforce_or_raise` (:326-338) raises `LaunchSeamError` unless PROCEED. Enforcement points:
- **Runner chokepoint (ironclad, pre-Popen):** claude_runner.py:1208-1230 calls the seam immediately after `build_argv` (line 1207) and before the single `subprocess.Popen` (line 1256); a non-ok decision raises `RunnerError(code, message)`. Over-ceiling resume and cwd mismatch are BOTH hard refusals here (a runner cannot rotate).
- **CLI layer:** cli.py:2644-2653 (`evaluate_packet_worktree_binding`) refuses BEFORE the runner is built when the bound worktree is not the packet's declared worktree (naming the primary-checkout case), riding the existing `LoopError` typed-refusal path.
- **Loop pre-first-dispatch shed:** loop.py:2644-2651 calls `_rotate_over_ceiling_before_first_dispatch` (loop.py:970-1057), which routes through `launch_seam.evaluate_ceiling` and SHEDS a recorded at/above-ceiling session (clears `_provider_session_id`, `sc.clear_provider_session`, consumes `rotation_pending`) so the first unit launches fresh — closing the exact cycle-2 gap.

Bypass hunt:
- **TOCTOU (seam vs Popen):** none. Both the seam (claude_runner.py:1214-1220) and Popen (line 1258 `cwd=self.config.cwd`) read the same `self.config`; nothing between them reassigns `self.config`, and `argv` (incl. `--resume`) is built once at line 1207. The seam's `resuming=bool(self.config.resume_session_id)` is consistent with the argv actually launched.
- **Direct RunnerConfig construction:** enumerated all sites (`grep RunnerConfig(`). Production worker launch = cli.py:2685 (sets `expected_worktree`+`primary_checkout`); cli.py:733/740/747 are argv-preview only (no Popen); preflight.py:91 and routing_probe.py:418 are **fresh** capability/routing probes (no `resume_session_id`); turnover_adapters.py:433 builds a **fresh** handoff argv ("resume rides as metadata rather than `--resume`", :428). No direct-construction path performs an over-ceiling `--resume`.
- **Model launch probe / doctor --live:** `doctor --live` runs a **fresh** control-response probe (cli.py:1291-1333, "runs a fresh one"); no resume. Probes are exempt from the cwd guard (empty `expected_worktree`) but cannot reach a provider with an oversized resume because they never `--resume`.
- **env/argv injection:** the guard reads Python object fields (`self.config.*`), never env or argv; no flag/env toggles it. cli._run_loop hardcodes `expected_worktree=str(worktree)`.
- **Reachability sweep (AS-5) is genuinely bypass-sensitive:** test_agent_supervisor_launch_seam.py:542/562/581 strip the seam/gate/shed statement from the real production functions' AST and assert the stripped shape reaches Popen with no seam call → RED (per-site removal sensitivity).

## SEC-MINOR — runner ceiling guard co-gated on `expected_worktree`
claude_runner.py:1213 wraps the ENTIRE `enforce_launch` call (both cwd AND ceiling) in `if self.config.expected_worktree:`. Since `enforce_launch` already internally skips the cwd guard when `expected_worktree` is empty (launch_seam.py:312) but ALWAYS evaluates the ceiling (:316), the outer wrapper needlessly co-gates the token-only ceiling check on a worktree being bound. Consequence: a hypothetical resume-capable runner constructed **without** a bound worktree would skip the 400k ceiling at the chokepoint.
- **No current reachable bypass:** every production resume carries `expected_worktree` (loop.runner is built by cli._run_loop; `with_resume`/`actuate_resume` preserve it via `dataclasses.replace`), and every worktree-less launch is a fresh probe that never resumes. The loop-layer pre-first-dispatch shed independently enforces the ceiling for the production resume path. So R332/R333 hold for all reachable paths.
- **Recommendation (non-blocking):** in run_unit, call `enforce_launch` unconditionally (it already internally gates only the cwd guard on `expected_worktree`), so a future resume-capable runner without a bound worktree cannot skip the ceiling. Verification: claude_runner.py:1213 vs launch_seam.py:312-319.

## 2. cwd comparison robustness on Windows (Q2) — PASS (INFO-1)
`normalize_path` = `os.path.normcase(os.path.normpath(path))` (launch_seam.py:162-172): folds drive-letter case, flips `/`→`\`, collapses `.`/`..`/dup-separators, strips trailing separator. `same_path` (:175-178) requires both non-empty and equal. `worktree_matches_packet` (:184-198) supports absolute (exact, folded) or basename-name (`wt-m0t123`) forms.
- Case / slashes / trailing / dot-segments: handled.
- **8.3 short names & symlink/junction:** the seam does NOT resolve these (deliberately filesystem-free so it's testable and a missing worktree still compares — :166-168). Every non-resolution failure mode is toward **REFUSE** (a short/aliased path that doesn't match `expected_worktree` falls to `cwd_mismatch`), never a false-accept of the primary checkout as the worktree. Crucially, the CLI layer resolves the junction/symlink risk upstream: cli.py:2643 `worktree = pathlib.Path(args.worktree or repo).resolve()` performs OS-level realpath resolution before `evaluate_packet_worktree_binding` compares against the packet worktree, so a `--worktree` junction pointing at the primary checkout resolves and is refused. No attacker-shaped path alias can make the primary checkout compare as the packet worktree.
- **INFO-1:** a realpath/samefile cross-check at the seam would additionally harden against a worktree path that is ITSELF a junction to the primary checkout, but that requires filesystem misconfiguration of the worktree value (outside the argv-aliasing threat model) and is already mitigated by the CLI-layer `.resolve()`.

## 3. No weakening (Q3) — PASS
`git diff 7b78d6c 6aada29 --name-only -- <sensitive>` returned EMPTY: **policy.py, broker.py, start_gate.py, recovery_probes.py, restart_channel.py, circuit_breakers.py, run_budget.py, audit_log.py, state_machine.py, recovery.py are byte-unchanged.** Therefore policy tiers, broker approval binding, budgets, breakers, audit chain, start preflight probes (incl. `provider_cli_drift`), and the M0-T121 restart_channel fail-closed preconditions are all intact. The command-authority contract still holds (90-pass run includes the 45 command-authority tests). Changed files are limited to launch_seam.py (new), the five wired modules, tests, fixture, README, runbook, reports, and two agent-memory files.

## 4. Fixture / secrets (Q4) — PASS
- Secret scan of the fixture + both reports (`sk-*|ghp_|xox*|BEGIN|password|secret|api_key|bearer|<botToken>|telegram|chat_id`) → **NONE**.
- The committed fixture (`fixtures/resume_path_defect_2026-08-30_m0t123.json`) is **load-bearing shape only**: home paths are placeholderized (`[HOME]`, `[HOME-SLUG]`), session ids are random UUIDs, and the payload is event-type histograms, record/sequence counts, token totals, policy_result strings, and the recovered terminal event — **no transcript conversation content** (no prompts, assistant text, or tool payloads). The `_provenance.runtime_dir_name` is an explicitly truncated path digest labeled "not a secret" (fixture:5). This is the honest R343/R344 terminal-evidence recovery: `max_turns_reached` (maxTurns 12, turnCount 13), which contradicts and abandons the context-limit hypothesis.

## 5. Preserved-evidence integrity (Q5) — PASS
Re-hashed all four sources read-only; each equals the G0 baseline exactly:
- journal `a4acb370f3a23fd5193c27d16e729a6b6035c53c368a10c52673de8b5de29255` ✓
- audit `e80c057cabc24478ab67d785e2f903696f6cc1fcf7cbf782db9fd6f284430c83` ✓
- transcript_cycle1 (wt-m0t107 slug, 02b014ee) `3a0d1f30664b1deba7b6cd47a0a69bdc84906332eb3ed180aea5e74e2f8b9b17` ✓
- transcript_cycle2 (ctl24 slug, 798d2f00) `3c9185687f12e86a2e066b18e8347a15840be94f981a52af3965f01394adbfaf` ✓
These match the fixture's `source_sha256` block — the derivation was read-only; originals untouched (R341).

## 6. R345 window prohibitions (Q6) — PASS (INFO-3)
- New-code grep for `clear_emergency|clear_recovery|set_emergency|reset_budget|restart` found only docstring prose (launch_seam.py:168-169) — **no calls**. `launch_seam.py` is pure: imports only `dataclasses`, `os`, `typing`, `.rotation` (no subprocess, no network, no journal writes, no set_state).
- **No new external dependencies:** diff of `+import/+from` lines (excluding stdlib and `.`-relative) is empty.
- **INFO-3:** the loop shed writes journal rotation state (`sc.clear_provider_session`, `rotation.clear_rotation_pending`, `ROTATION_REASON_KEY=""` at loop.py:584) — this is the legitimate "rotate at the safe seam" behavior REQUIRED by R332/R333, not a prohibited side effect: it resets NO budget (AS-4 preserves budgets), restarts NO loop, clears NO recovery/emergency durable flag, and never touches the preserved fixture journal (code uses the live/test journal, never the preserved path).
- **INFO-2:** a packet declaring no worktree is not cwd-constrained by `evaluate_packet_worktree_binding` (documented single-checkout/legacy behavior, launch_seam.py:215-216); the reproduced M0-T107 packet declares `wt-m0t107` and is fully constrained.

## 7. Tests (Q7) — PASS
`python -m pytest tools/test_agent_supervisor_launch_seam.py tools/test_agent_supervisor_command_authority.py -q` → **90 passed** in 16.39s (45+45, as expected). Modularity: `python tools/modularity_check.py --check` reports only pre-existing warnings (cli.py, durable_state, policy, process, recovery_probes, refusal_bridge, repair_gate, context_benchmark) — launch_seam.py (338 SLOC, single-responsibility pure decision module) is not flagged; no hard failure.

## Scope / regression
`6aada29` touched only allowed paths plus two `.claude/agent-memory/backend-engineer/` files (outside gate/ledger scope; a producer/identity-naming note, not a security defect). No `tools/**` frozen sensitive module changed; `services/**`, `apps/**`, `.github/**` untouched.

Reproduction commands (read-only):
```
git rev-parse HEAD
git diff 7b78d6c 6aada29 --stat -- tools/agent_supervisor/
git diff 7b78d6c 6aada29 --name-only -- tools/agent_supervisor/policy.py tools/agent_supervisor/broker.py tools/agent_supervisor/start_gate.py tools/agent_supervisor/recovery_probes.py tools/agent_supervisor/restart_channel.py
python -m pytest tools/test_agent_supervisor_launch_seam.py tools/test_agent_supervisor_command_authority.py -q
sha256sum <preserved journal> <audit> <transcript_cycle1> <transcript_cycle2>
```

Relevant files (absolute):
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\launch_seam.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\claude_runner.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\cli.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\loop.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\loop_turnover.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\session_continuity.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\fixtures\resume_path_defect_2026-08-30_m0t123.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\tasks\M0-T123.json`

VERDICT: PASS

---

# G5 DELTA ATTESTATION (VERBATIM reviewer return; hardening 6aada29 -> 16e1b3b; saved by the orchestrator)

The only scan hit is the G5 report echoing my own scan pattern (not an actual secret). Delta confirmed.

## DELTA ATTESTATION — M0-T123 (SEC-MINOR closure 6aada29 → 16e1b3b)

**Control head:** `16e1b3b` (verified via `git rev-parse HEAD`).

**(1) Unwrap-only, no new logic, refusal unchanged.** `git diff 6aada29 16e1b3b --stat -- tools/agent_supervisor/` = **claude_runner.py only** (+26/-21). Reading the run_unit diff: the sole change is removing the `if self.config.expected_worktree:` wrapper (and its indentation) so `launch_seam.enforce_launch(...)` is now called **unconditionally**. The `WorkerLaunchContext` arguments are byte-identical (cwd, expected_worktree, primary_checkout, resuming, session_context_tokens, session_usage_known), and the refusal is byte-identical (`if not _decision.ok: raise RunnerError(_decision.code, _decision.message)`). No weakened refusal, no added branch. This is precisely my recommendation: the seam's internal cwd-guard skip for empty `expected_worktree` (launch_seam.py:312) is untouched, and the 400k ceiling now always evaluates (launch_seam.py:316).

**(2) TOCTOU posture unchanged.** The seam still reads the same immutable `self.config.*`, still sits after `argv = build_argv(self.config)` (line 1207) and before the sole `subprocess.Popen`, with only `handler`/`env` setup in between (no `self.config` mutation). Same self.config.cwd read by seam and Popen; no new window introduced.

**(3) Named hypothetical now refuses.** `python -m pytest tools/test_agent_supervisor_launch_seam.py -k "R332" -q` → **3 passed** (worktree-less over-ceiling resume AND unknown-telemetry resume both refuse at the chokepoint; anti-re-wrap AST tests present). Full suite `…launch_seam.py -q` → **64 passed** (up from 45 — strengthening-only, new unwrap/anti-re-wrap coverage).

**(4) Sensitive modules byte-unchanged.** `git diff 6aada29 16e1b3b --name-only -- policy.py broker.py start_gate.py recovery_probes.py restart_channel.py state_machine.py audit_log.py` → **empty**. Policy tiers, broker binding, breakers/budgets, audit chain, start preflight, and the M0-T121 restart_channel preconditions remain intact.

**(5) No new secrets.** Whole-delta `+`-line scan for the credential patterns returns only one line — the G5 report echoing my own scan pattern string, not an actual secret. The non-code delta is control-plane (gates/reports/state/task, orchestrator-written) plus the test file's +375 anti-re-wrap/worktree-less tests.

My prior G5 basis is preserved and the SEC-MINOR is genuinely closed with a strengthening-only change; behavior on all reachable production paths is identical, and the previously-latent worktree-less over-ceiling resume now fails closed at the runner chokepoint.

DELTA VERDICT: PASS
