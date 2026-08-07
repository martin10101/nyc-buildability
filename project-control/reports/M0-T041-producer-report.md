# M0-T041 Producer Report — Supervisor 0A.8 gap-closure A

**Task:** M0-T041 — quota-exhaustion classifier, activation-checklist B-rows, R207 live sampling, pending_prompt hardening.
**Lane:** DEFECT-ONLY (D-010 supervisor-freeze; `.claude/rules/supervisor-freeze.md`). Every change cites its qualifying evidence (AD-093).
**Worktree:** `C:/Users/MLFLL/Downloads/nyc-zoning/orch`, branch `task/M0-T041-supervisor-gaps`, base `origin/main f65d716`.
**Producer:** backend-engineer. Producer ≠ reviewer; this report is evidence for the gate, not an acceptance.

---

## 1. Files changed / created (per-file one-line summary)

| File | Kind | Summary |
|---|---|---|
| `tools/agent_supervisor/claude_runner.py` | M | AS-1: added `QuotaSignalFixture`, the `QUOTA_EXHAUSTION_FIXTURES` corpus, `classify_quota_exhaustion`, and derived `QUOTA_EXHAUSTION_SIGNAL_VERIFIED` from the corpus (stays False). |
| `tools/agent_supervisor/cli.py` | M | AS-1: wired `classify_quota_exhaustion` into `make_launch_probe` for orchestrator-role sessions. AS-3: constructed a real `ResourceSampler` in `_run_loop` and passed it to the loop; added the `resource_sampling` doctor disclosure check. AS-4: consume the pending_prompt record in `cmd_resume_pending_prompt` on success. |
| `tools/agent_supervisor/loop.py` | M | AS-3: `resource_sampler` param + `_check_resources` seam called at cycle entry (fail-closed). AS-4: `pending_prompt_key` / `consume_pending_prompt` helpers; consume on the in-loop supervised forward. |
| `tools/agent_supervisor/resource_sampling.py` | NEW | AS-3: stdlib-only, Windows-compatible resource sampler for the R207 gauge set (measured disk/log; structural-unknown cpu/memory/process; distinct sampling-outage path). |
| `tools/test_agent_supervisor_quota_classifier.py` | NEW | AS-1: 10 tests (proven/unknown/absent/malformed + fail-closed production corpus + seam wiring through `probe_model_launch`). |
| `tools/test_agent_supervisor_resource_sampling.py` | NEW | AS-3: 10 tests (sampler unit + loop gate both directions + structural-unknown + no-sampler backward-compat). |
| `tools/test_agent_supervisor_pending_prompt.py` | NEW | AS-4: 4 tests (consume helper, CLI resume consumes, consumed record not re-approvable, in-loop forward consumes). |

No file outside the allowed paths was touched. No dependency manifest/lockfile was edited (stdlib-only). No git/ledger/gh command was run by the producer.

---

## 2. Per-defect evidence, reproducing test, before/after

### AS-1 — Account-quota exhaustion classifier wired
- **Citation:** `project-control/reports/M0-T036-ACTIVATION-CHECKLIST.md` (standing prerequisite: "Live-CLI account-quota exhaustion **classifier wired** (`QUOTA_EXHAUSTION_SIGNAL_VERIFIED=False` today → the model-chain switch fail-closes to PAUSE; disclosed by `doctor`). Needs its own security look (G3-A1 / G5-L-1 / G4-A1)"). Packet risk note: "fail-closed stays default until shapes proven."
- **Before:** `cli.py`'s `make_launch_probe(...)` for orchestrator-role sessions passed **no** `classify_unavailable`, so the `lambda: ""` default ran and no code recognized any quota signal; the seam was unwired.
- **After:** a real, corpus-gated classifier is wired. `classify_quota_exhaustion` returns `quota_exhausted` ONLY when a `verified_live` fixture matches; unknown/absent/malformed/documented-but-unverified all return `""` (fail-closed PAUSE, AD-025). `QUOTA_EXHAUSTION_SIGNAL_VERIFIED` is now **derived** from the corpus (`any(f.verified_live ...)`) and remains `False` because no live capture exists — so production behavior is unchanged (still fail-closed) while the machinery is real and ready to activate when a live signal is captured.
- **Reproducing/behavior tests:** `tools/test_agent_supervisor_quota_classifier.py` — `test_proven_shape_returns_quota_exhausted`, `test_unknown_shape_returns_unknown`, `test_absent_signal_returns_unknown`, `test_malformed_payload_returns_unknown_never_raises`, `test_verified_flag_is_false_and_derived_from_corpus`, `test_documented_candidate_match_still_returns_unknown`, `test_probe_uses_classifier_for_reason_code`, `test_probe_stays_unknown_without_a_verified_signal`. The seam-wiring tests launch a real local fake process and assert the reason flows through `probe_model_launch`.

### AS-2 — Activation-blocking G3 B-rows (B-1..B-4)
**All four B-rows are ALREADY FIXED and independently RE-GATED in V1.1 at the current frozen HEAD (693df29). No in-lane code change was made; faking a reproducing test that "fails at baseline" is impossible because the baseline already contains the fixes.** Honest per-row status with evidence:

| B-row | Status at HEAD | Fix location (verified in source) | Existing regression test | Re-gate delta verdict |
|---|---|---|---|---|
| B-1 (forwarded prompt never delivered) | FIXED | `loop.py` `run()` threads `prompt = result.forward.sent_prompt`; `ForwardResult.sent_prompt` carries the outbox bytes | `test_agent_supervisor_loop.py::ForwardedPromptThreadingTests` (loop.py:649+) | `M0-T036-V1.1-G3-code-delta-review.md` §(2) "B-1 — FIXED" |
| B-2 (POLICY_CHECK strands the journal) | FIXED | `state_machine.py` `POLICY_CHECK → PREFLIGHT` (`cycle_closed`); `CycleResult.continues` narrowed to CLAUDE_RUNNING; `cmd_start` catches `LoopError` | `test_agent_supervisor_loop.py` B-2 tests (loop.py:716+, :1333) | `...V1.1-G3...` §(2) "B-2 — FIXED" |
| B-3 (last-of-distinct checkpoints chosen) | FIXED | `claude_runner.py` `extract_checkpoint` raises `multiple_distinct_checkpoints` when `len(by_id) > 1` | `test_agent_supervisor_runner.py::test_multiple_distinct_checkpoints_are_refused_not_last_wins` (:515) | `...V1.1-G3...` §(2) "B-3 — FIXED" |
| B-4 (review breaker verdict discarded) | FIXED | `loop.py` honors `codex_reviews_per_checkpoint` verdict (PAUSED_RECOVERY on TRIP) and resets it per checkpoint; edge `CODEX_REVIEW → PAUSED_RECOVERY` | `test_agent_supervisor_loop.py` B-4 tests (loop.py:773+) | `...V1.1-G3...` §(2) "B-4 — FIXED" |

The activation-checklist box "Activation-blocking G3 B-rows (B-1..B-4) fixed and re-gated" is stale relative to the code: the fixes landed in V1.1 (frozen `c193a52`) and were independently reviewed PASS. **See §4 for the honest disposition (no B-row is left in an unaddressed defect state; none required new work).**

### AS-3 — R207 live resource sampling wired into the loop
- **Citation:** `M0-T036-ACTIVATION-CHECKLIST.md` ("Live resource **sampling** wired into the loop for the R207 limit set (config/circuit-breaker knobs exist + are fail-closed today; live sampling is the documented Phase-2/3 boundary)"). Knobs: the 4 from commit `c6a2c59` (`max_model_calls_per_day`, `max_external_writes_per_day`, `max_cpu_percent`, `max_memory_bytes`) + earlier gauges (`max_processes`, `min_free_disk_bytes`, `max_retained_log_bytes`, `max_review_packet_bytes`).
- **Before:** the gauge breakers existed and were fail-closed, but **nothing sampled real readings** into them from the loop (Phase-2/3 boundary; `circuit_breakers.py` scope note).
- **After:** `resource_sampling.ResourceSampler` measures what the standard library can on Windows (free disk via `shutil.disk_usage`, retained-log bytes via `os.stat`) and reports the rest honestly. The loop's `_check_resources` runs at cycle entry, **before** spending a provider call, and is fail-closed in both directions:
  - a **measured** limit crossing → synchronous pause at the legal entry state (no dispatch);
  - a **sampling outage** of a measurable gauge → conservative pause (a guard that cannot read the resource never assumes it is fine);
  - a **structurally unmeasurable** gauge (cpu/memory/process-count — not measurable stdlib-only on Windows; psutil is not admitted) is reported as unknown, **never** fed a fabricated OK reading (AD-025), and disclosed by the new `doctor` `resource_sampling` check. It does not spuriously pause every cycle (which would make the supervisor unusable on Windows).
- **Reproducing/behavior tests:** `tools/test_agent_supervisor_resource_sampling.py` — sampler unit tests (`test_measurable_gauges_report_real_readings`, `test_measurement_outage_is_unknown_and_not_structural`, `test_unmeasurable_gauges_are_structural_unknown_never_a_value`, `test_log_size_sums_files_and_tolerates_missing`, `test_capability_report_lists_live_and_unmonitored`) and loop-gate tests (`test_measured_limit_crossing_pauses_before_dispatch`, `test_sampling_outage_degrades_to_conservative_pause`, `test_structural_unknown_neither_pauses_nor_is_treated_as_safe`, `test_measured_within_limits_does_not_pause`, `test_no_sampler_is_a_noop_backward_compatible`).
- **Scope-honest note:** `review_packet_bytes` is a per-packet build-time metric, not a periodic resource, so it is not part of the periodic sampler; the other five gauges are handled as above. The sampler seam defaults to `None`, so every pre-AS-3 caller/test is behaviorally unchanged; only the CLI wires a real sampler.

### AS-4 — pending_prompt consume/clear hardening (G5 LOW)
- **Citation:** `project-control/reports/M0-T036-V1.2.3-G5-security-delta-review.md` LOW finding: "neither it nor the loop consumes/clears the record after use ... Recommend before R595 activation: consume/clear `pending_prompt/<run_id>` on a successful resume".
- **Before:** `cmd_resume_pending_prompt` fired the `owner_approved_pending_prompt` transition and wrote the audit event but left the `pending_prompt/<run_id>` record intact; the in-loop supervised forward likewise left it intact. A later WAIT for a different ask could still carry a prior cycle's digest, re-approvable.
- **After:** `consume_pending_prompt` writes a consumed marker (no truthy `digest`) after a **successful** resume/forward — in both the CLI command (after the durable transition + audit event) and the in-loop supervised forward. A re-approval attempt then fails closed at the "no pending-prompt record" guard.
- **Reproducing tests:** `tools/test_agent_supervisor_pending_prompt.py` — `test_successful_resume_consumes_the_record` (asserts the record has no digest after resume; **fails at baseline**, which left the digest intact), `test_a_consumed_record_cannot_be_re_approved` (regression: consumed marker → fail-closed refusal, no state mutation), `test_supervised_forward_consumes_the_pending_prompt` (in-loop path), `test_consume_writes_a_marker_with_no_truthy_digest` (helper unit).

---

## 3. Full supervisor suite — before AND after

Standard-library `unittest`, Python 3.11.9, the documented 20-module invocation from `M0-T039-supervisor-freeze.md` (baseline), plus the 3 new modules (after).

| Run | Modules | Ran | Passed | Failed | Errors | Skipped | Duration |
|---|---|---|---|---|---|---|---|
| BEFORE (baseline) | 20 | 1165 | 1163 | 0 | 0 | 2 | 81.801 s |
| AFTER (source only, before new tests) | 20 | 1165 | 1163 | 0 | 0 | 2 | 79.924 s |
| AFTER (with 3 new modules) | 23 | **1189** | **1187** | **0** | **0** | 2 | 76.629 s |

After-count 1189 ≥ baseline 1165 + 24 new tests (10 quota + 10 resource + 4 pending). Zero failures/errors; the 2 skips are the pre-existing POSIX-only guards.

`python tools/validate_directive_compliance.py` → **exit 0** ("directive registry OK: 9 directive(s), 9 active ...") both before and after.

### New-module test invocation (append to the freeze suite)
```
python -m unittest \
  tools.test_agent_supervisor_quota_classifier \
  tools.test_agent_supervisor_resource_sampling \
  tools.test_agent_supervisor_pending_prompt
```

---

## 4. B-rows left OPEN (honest disposition)

**No B-row is left in an unaddressed defect state.** All four (B-1..B-4) were fixed and independently re-gated PASS in V1.1 (`M0-T036-V1.1-G3-code-delta-review.md`, frozen `c193a52`) and the fixes are present and test-covered at the current HEAD (see §2 AS-2 table). Per the packet instruction ("If a B-row turns out to be already-fixed ... do NOT fake it — report honestly with evidence"), I made no in-lane change for AS-2 and did not author a reproducing test that cannot fail at the baseline. If the gate requires the activation-checklist box to be formally re-checked against this task, that is a control-plane/ledger act for the orchestrator; the code evidence is as above.

---

## 5. Fixture provenance (AS-1)

The `QUOTA_EXHAUSTION_FIXTURES` corpus in `claude_runner.py` seeds two DOCUMENTED-CANDIDATE shapes; **none is captured from a live account-quota exhaustion**, so every entry is `verified_live=False` and the production classifier is fail-closed.

| Fixture | Shape | `cli_version` | `verified_live` | Provenance |
|---|---|---|---|---|
| `usage_limit_reached_prose` | stderr matches `\busage limit\b\|\bquota\b\|\bplan limit\b` | `UNCAPTURED - ... base CLI probed at claude 2.1.220` | False | Derived from `resume_scheduler.classify_limit`'s documented "usage limit" vocabulary. |
| `rate_limit_429_prose` | stderr matches `\b429\b\|\brate limit(ed)?\b` | `UNCAPTURED - ... claude 2.1.220` | False | Derived from `resume_scheduler.classify_limit`'s 429/rate-limit vocabulary; a 429 is usually a temporary rate limit, not account-quota exhaustion — kept unverified. |

- **Where the shapes come from:** the vocabulary the codebase already documents in `tools/agent_supervisor/resume_scheduler.py::classify_limit` (usage-limit / quota / 429 / rate-limit prose). The base CLI version the codebase records is **claude 2.1.220** (`claude_runner.py` module docstring); the exact stderr/exit code emitted on a *live account-quota exhaustion* was never captured on this build, which is exactly why `QUOTA_EXHAUSTION_SIGNAL_VERIFIED` stayed False and stays False here.
- **Activation path:** a real exhaustion captured under owner credentials (adjacent to the R595 supervised-rehearsal territory) records its exact bytes/version with `verified_live=True`; the derived flag and the model-chain switch then recognize it — no other code change.

---

## 6. Confirmations

- Nothing outside the allowed paths was touched. `git status` shows exactly: `M` `tools/agent_supervisor/{claude_runner,cli,loop}.py`; new `tools/agent_supervisor/resource_sampling.py`, `tools/test_agent_supervisor_{quota_classifier,resource_sampling,pending_prompt}.py`.
- No git commit/push, no `gh`, no `tools/project_control.py` lifecycle command was run by the producer.
- No dependency was added; no manifest or lockfile was edited; stdlib-only throughout.
- Every AS-1/AS-3/AS-4 change carries its evidence citation as a code comment where explanation is warranted (matching existing comment density) and is listed here with its citation (AS-5); AS-2 is reported honestly as already-fixed/re-gated.
- The supervisor stays SHADOW-ONLY; nothing here activates it or lifts the R595 blocking prerequisite. The classifier and sampler are wired but fail-closed (no live-verified quota signal; unmeasurable gauges disclosed as unknown).

**Requested status: awaiting_gate.**
