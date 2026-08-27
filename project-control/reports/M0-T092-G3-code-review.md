# M0-T092 — G3 independent code review (verbatim reviewer return)

Saved VERBATIM by the orchestrator from the code-reviewer agent-return channel
(report-preservation rule; transport entity-decoding only; HTML entities for angle
brackets decoded). Reviewer: code-reviewer (read-only). Recorded by: orchestrator.

---

# Gate Report

- **Gate ID:** G3 (independent code review — correctness, contracts, maintainability)
- **Task ID:** M0-T092 (D-024 Phase D unit F: controller state machine, safe seams, exact-once succession, outage handling)
- **Reviewer:** code-reviewer (read-only)
- **Producer:** fable-orchestrator-session
- **Result:** **PASS** (with 2 LOW hardening findings + 3 advisories; none blocking)
- **Clean environment/worktree used:** Reviewed at deliverable content identity `b940c90` (live HEAD `8234479` carries only control-plane records on top; the `tools/agent_supervisor/**` and test tree at HEAD is byte-identical to `b940c90` — confirmed the diff-of-interest is entirely in `b940c90`). Ran on Python 3.11.9 (repo targets 3.12; the supervisor tests are stdlib-`unittest`/plain-pytest with no PEP 695 generics, so they collect and run here — consistent with prior supervisor-gate precedent).

## Acceptance criteria reviewed

Task carries `acceptance_scenarios: []`; the executable acceptance pack is the section-16.3 matrix `tools/test_agent_supervisor_controller_succession.py` (S1–S15, 70 tests) plus the frozen-suite baseline duty. I reproduced the matrix and the affected-file deltas rather than trusting the producer's counts.

## Directive/requirement verification (correctness-relevant subset, re-derived at `b940c90`)

The full 65-requirement DCV is the `directive-compliance-verifier`'s independent pass (producer != verifier). This G3 pass independently re-derived the correctness-load-bearing requirements from source and behavior:

| Requirement ID | Reviewed identity | Verdict | Reproduced evidence |
|---|---|---|---|
| R028 renewable bounded epochs / one active lease | b940c90 | PASS | `EpochLease.__post_init__` rejects ttl<=0 (`bad_ttl`) and non-positive epoch; `acquire_first` CAS-against-absence single-winner; `renew` refuses non-owner/released/expired. Probe: dup acquire -> `lease_exists`. |
| R029 18-distinction state set | b940c90 | PASS | 4 additive states + 17 transitions; all four new states have entry+exit edges; `BLOCKING_STATES`/`TERMINAL_STATES` untouched; illegal transitions still raise. §4.1 composite claims verified honest (see below). phase1 count 23->27, no other test hardcodes the count (`cli.py:392` is a dynamic display f-string, not an assertion). |
| R030 idempotent/single-winner CAS | b940c90 | PASS | `compare_and_swap_state` uses `BEGIN IMMEDIATE` on an `isolation_level=None` (autocommit) connection — consistent with every other write path in `durable_state.py`; genuinely atomic. Cross-connection test proves two `DurableJournal`s on the same file -> exactly one winner. Probe: raw CAS race `B True / C False` (exactly-one XOR true). |
| R031 three interruption classes separate | b940c90 | PASS | turnover (`turnover_seam`)+`succeed`; crash (`reconcile_on_boot`) resumes SAME epoch (`OWN_LEASE_LIVE`, `resumes_same_epoch=True`); outage (`outage_policy`). Other-owner live lease -> `may_dispatch_writes=False`, `may_orient_read_only=True`. |
| R033 outage: bounded backoff / blocked / bounded idle | b940c90 | PASS (with L1 below) | Unknown/empty cause -> BLOCKING (fail-closed) reproduced; `BackoffPolicy` rejects `max_attempts<1`; delays bounded+capped (1,2,4); attempt>max -> `attempts_exhausted`; idle>`MAX_IDLE_SECONDS` refused; `permissions_during` transient=(land True, dispatch False), blocking=(False,False). |
| R066 children-reconciled seam condition | b940c90 | PASS | `RotationSafetyState.children_unreconciled:int=0` additive; `UNSAFE_MOMENT_CHECKS` appended; `unsafe_rotation_reasons` treats int 0 as safe / positive as unsafe -> backward-compatible for existing callers. |
| R067 smallest-complete handoff, no silent truncation | b940c90 | PASS (reuse) | `handoff.HANDOFF_FIELDS`/`child_handoff` bounds — unchanged, proven reuse. |
| R125–R128 Bootstrap Gate 0 | b940c90 | PASS | `evaluate_gate0` fail-closed: unknown-MCP fails, added-dir fails, unapproved MCP fails, clean passes; Windows path identity via `canonical_checkout_path` (resolve+normcase) — case-variant cwd PASSES on `os.name=nt`. |
| R042 telemetry honesty | b940c90 | PASS | `succeed(usage=Measurement|None)` stores label or nothing; `test_missing_usage_is_unknown_never_zero`. |
| R045 no worker token pressure | b940c90 | PASS (reuse) | `assert_worker_text_clean` reused; no numeric quota text composed. |
| R102 Phase-D freeze citation | b940c90 | PASS | Packet + commit both cite D-024-R102; per-change R029/R030/R033/R066 citations present; guard packs untouched (forbidden paths). |

## Steps independently executed

```
python -m pytest tools/test_agent_supervisor_controller_succession.py -q   -> 70 passed
python -m pytest tools/test_agent_supervisor_phase1.py -q                   -> 80 passed
python -m pytest tools/test_agent_supervisor_capability_probe.py \
                tools/test_agent_supervisor_event_bus.py \
                tools/test_agent_supervisor_native_adapter.py -q            -> 115 passed
python tools/modularity_check.py --check                                    -> failures 0 (5 pre-existing warns, none the new modules)
```
Plus a hand-written behavioral probe (piped via stdin, no files written) exercising exact-once succession across two connections, live-predecessor protection, boot reconciliation, outage classification/bounds, and Gate-0 fail-closed — all invariants held (outputs quoted inline above). Delta consumer subset = 70+80+115 = **265/265**, matching the producer's "265/265" claim.

## Expected versus actual

- Exact-once succession: two contenders can never both win — CONFIRMED (cross-connection CAS + `LosingJournal` test that asserts the loser writes nothing and raises `succession_race_lost`).
- A live predecessor is never taken over — CONFIRMED (`succeed` re-reads inside itself and raises `predecessor_live`; the epoch check + full-record CAS close the read->write interleaving).
- State machine: no stranded states, no fail-open path — CONFIRMED (every new state has entry+exit; `transition()` refuses anything not in the table).
- Drift re-capture faithful — CONFIRMED (2.1.248 catalog = 31 events, set-identical to 2.1.247; codex unchanged; masking preserved; T1 log's 3 failures are exactly the three LIVE version-match teeth, which pass at the committed SHA).

## Evidence paths (absolute)

- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\epoch_lease.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\stop_intent.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\outage_policy.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\bootstrap_gate.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\durable_state.py` (CAS at lines 397-431; connection `isolation_level=None` at line 227)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\state_machine.py` (new states 68-71; transitions 276-332)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\rotation.py` (field 605; check 623)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\turnover_seam.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\test_agent_supervisor_controller_succession.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T092-controller-succession.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T092-full-suite-T1.txt`

## Regression/security/provenance findings

- Additive-extension discipline holds: every edit to accepted code is additive with a safe default (`children_unreconciled=0`, `unreconciled_children=()`), so existing `RotationSafetyState`/`safety_state_from_run` callers are unaffected. No behavior change to existing accepted code beyond the cited additions.
- Guard packs (`readonly_agent_guard.py`, `agent_dispatch_guard.py`) and all forbidden paths untouched (confirmed by the `git show --stat` file list).
- All cited reuse symbols exist and imports resolve (`resume_scheduler.EMERGENCY_STOP_KEY/MANUAL_PAUSE_KEY`, `telemetry_records.Measurement`, `child_handoff.unreconciled_children/successor_*`, `codex_reviewer.REQUIRED_BY_DECISION["REVISE"]`, `loop.effective_model`, `session_continuity.CONTEXT_SHEDDING_REASONS`) — the §4.1 composite claims ("correcting" via REVISE decision; "lower-model bridge" via `effective_model` journal read) are HONEST, not fabricated to dodge a state.
- Provenance/masking intact in the new drift fixtures (no `Users`/`MLFLL` leakage; `confidence: official-docs`).

## Defects

None blocking. Findings:

- **LOW-1 — `outage_policy._REASON_KEYWORDS` first-match-wins biases mixed reason strings toward TRANSIENT (fail-open in ambiguity).** `tools/agent_supervisor/outage_policy.py:59-72,101-111`. Transient keywords are scanned before blocking keywords, so a blocking failure whose bounded reason text also contains a transport token is routed to the retry path. Reproduced: `"authentication failed: connection reset" -> ('network','transient')`, `"billing problem, request timed out" -> ('timeout','transient')`, `"revoked access after timeout" -> ('timeout','transient')`. This contradicts R033's letter ("auth/billing/revoked is not retried; it enters blocked-with-handoff"). **Why non-blocking:** the retry is bounded (`max_attempts`) and self-corrects to blocked-with-handoff via `attempts_exhausted -> CODEX_OUTAGE_BACKOFF->WAIT_FOR_OWNER`, never an unbounded loop or silent swallow; and the module docstring designates `classify_cause(known_cause)` as the primary path with text-sniffing as a convenience fallback. **Recommend:** scan `BLOCKING_CAUSES` keywords first (or return BLOCKING if any blocking token is present), matching the module's own unknown->BLOCKING fail-closed stance.

- **LOW-2 — `epoch_lease.may_dispatch_writes` uses a permissive default `external_effects_reconciled=True`.** `tools/agent_supervisor/epoch_lease.py:350-363`. Its docstring says it "mirrors `child_handoff.TurnoverCoordinator.successor_may_dispatch_writes`", but that mirror makes `external_effects_reconciled` a keyword-required argument with NO default (`child_handoff.py:203-205`), forcing the caller to be explicit. Here a caller that omits it obtains write authority on an owned-live lease even with unreconciled external effects. **Why non-blocking:** pure predicate with no live caller in this diff (SHADOW-ONLY, R595 not activated); `OWN_LEASE_LIVE` is still required. **Recommend:** make `external_effects_reconciled` keyword-required (no default) to match the mirrored predicate and the fail-closed posture.

- **ADVISORY-1 — succession-log append is non-atomic w.r.t. the lease CAS.** `epoch_lease.succeed` commits the epoch via CAS, then appends `SUCCESSION_LOG_KEY` in a separate `set_state`. A crash in that window loses only the bounded convenience-log entry; the lease record (authoritative) and the transitions table (full audit) are intact, so exact-once is unaffected. No action required.

- **ADVISORY-2 — whole-suite green run at the committed SHA is composed, not a single captured artifact.** The captured `M0-T092-full-suite-T1.txt` is the pre-recapture tree (2911 passed / 3 failed = the version-match teeth / 3 skipped); the committed SHA's evidence is that composition minus the 3 now-fixed teeth plus the 265-test delta re-run, with whole-suite confirmation deferred to CI. The T1->T2 delta is fixture pointers + test files only (no production logic), and I reproduced 265/265, so this is acceptable for G3; G4/CI should confirm the full suite green at the frozen identity.

- **ADVISORY-3 — repeated bounded idles are not globally capped.** Each `begin_bounded_idle` window is bounded by `MAX_IDLE_SECONDS` (24h) and re-validates through `PREFLIGHT`, but a long "no eligible work" period becomes a sequence of bounded idles (`recheck_count` grows). This is the designed daily-recheck behavior (not a busy loop) and is durably visible; noted only for the record.

## Required rework

None. LOW-1/LOW-2 are recommended hardening (they do not break exact-once, the state machine, the Gate-0 fail-closed contract, or additive discipline, and each self-corrects/has no live caller). If the orchestrator elects to fold them in as PASS-with-corrections, they are small, local changes; otherwise they can carry to the M0-T109 guard/hardening backlog alongside the existing advisory bundle.

## Reviewer conclusion

The four new modules are correct, focused, well-documented, and fail-closed on their central invariants. Exact-once succession is genuinely atomic (BEGIN IMMEDIATE on an autocommit connection, cross-connection-proven, loser writes nothing), a live predecessor is never taken over, the 17 new transitions are sound with no stranded or fail-open states, unknown/empty outage causes fail closed to BLOCKING, backoff/idle are bounded, and Bootstrap Gate 0 fails closed with correct Windows path identity. The additive edits are backward-compatible and the drift re-capture is faithful (31-event parity, nothing behavioral papered over). The two LOW findings are ambiguity-hardening and API-hygiene items, non-blocking. Independent execution reproduced 265/265 relevant tests and every claimed invariant.

**VERDICT: PASS**
