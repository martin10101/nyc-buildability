# G4 QA GATE REPORT — M0-T048 (Close G5-C2 residual, owner am.14 / D-010 R134-R143)

**Reviewer:** qa-engineer (independent, read-only on repo). **Lane:** G4 (QA / evidence integrity).
**Reviewed code identity (confirmed via `git rev-parse`):** worktree `C:/Users/MLFLL/Downloads/nyc-zoning/orch`, branch `task/M0-T048-c2-close`, HEAD `ec0f55d28da90d57467321ad65c922fdde09f043`, base `9c2ec252b509…` (`9c2ec25`, contains accepted M0-T046). Control-plane evidence read from primary checkout (packet `M0-T048.json`, directive `D-010/source-014-amendment.md`, producer report, evidence map, G2 self-check). All heads match the frozen identity in the dispatch.

**Verdict: PASS.** No blocking corrections. Advisory (non-blocking) observations listed in §7; they are explicitly NOT required corrections and do not gate acceptance.

---

## 1. Per-AS conformance vs PACKET text (re-derived independently)

| AS (packet verbatim intent) | Test(s) driving REAL loop/CLI | Conformance |
|---|---|---|
| **AS-1** primary adversarial (owner 7-step): park authentic; mutate BOTH prompt+prompt_bytes_digest consistently; operator digest unchanged; attempt approve/resume; FAIL CLOSED; provider==0; sealed hash-chained refusal; non-vacuous | `c2_binding.TwoFieldForgery.test_two_field_forgery_at_approve_is_refused_fail_closed` (approve), `…after_approval_is_refused_no_provider` (forward), `test_non_vacuity_pre_fix_checks_pass` | **PASS** — see §2 table + §3 mutation proof |
| **AS-2 / R139a** happy path forwards exactly once; forwarded bytes verify against operator-digest binding | `HappyPathBinding.test_happy_path_forwards_once_and_binds`; `park_approve_binding.HappyPath` | **PASS** — asserts `len(forwarded_message_ids)==1` and body(before clock)==`build_forwarded_prompt(instruction)` |
| **AS-3 / R137/R139b** clock-only diff does not invalidate approval (S13.5) | `ClockInvariant.test_clock_only_change_does_not_invalidate_the_approval` | **PASS** (one tautological assertion — §7.3, non-blocking) |
| **AS-4 / R139c** post-approval journal tamper refuses fail-closed at resume | `TwoFieldForgery.…after_approval…`; `park_approve_binding.TamperAfterApproval` | **PASS** (proven non-vacuous, §3) |
| **AS-5 / R139d/R140** no authority/forwarding-guard/activation/tier change; diff confined to allowed_paths; no redesign | `PostureUnchanged.test_shadow_supervised_posture_intact` + grep-proof (reproduced §6) | **PASS** |
| **AS-6** old-shape/missing/malformed binding refuses fail-closed (never falls back to journal-resident-only); distinct honest reason codes | `FailClosedReasonCodes.{old_shape_missing, malformed, not_reproducing_operator_digest, byte_anchor_tamper}` + `ApprovePendingPromptUnitTests` | **PASS** — distinct `pending_prompt_uncovered` vs `pending_prompt_tampered`; old-shape refusal proven non-vacuous (§3) |

## 2. Owner 7-property table (R138/AS-1) — every property concretely asserted

| # | Owner property | Asserted where | Status |
|---|---|---|---|
| 1 | Park an authentic approval | `_park_real()` drives the REAL supervised loop; `_park_real` itself asserts instruction reproduces digest AND body, body is timestamp-free | **YES** |
| 2 | Mutate BOTH prompt and prompt_bytes_digest **consistently** | `_forge_two_fields`: `evil=prompt+marker`, `prompt_bytes_digest=digest_of(evil)`. `test_non_vacuity` explicitly asserts `digest_of(forged.prompt)==forged.prompt_bytes_digest` (self-consistent) | **YES** |
| 3 | Operator-named approval digest left unchanged | `forged=dict(record)` keeps `digest` and `approved_instruction`; `test_non_vacuity` asserts `operator_digest==forged["digest"]` | **YES** |
| 4 | Approval AND resume attempted (both variants) | approve path = real `resume-pending-prompt` CLI; forward path = fresh `SupervisedLoop.run()` | **YES (both)** |
| 5 | Fail closed (no state change / no approval) | approve: `code==1`, `state==WAIT_FOR_OWNER`, `not record.approved`; forward: `LoopError forwarded_prompt_unavailable` | **YES** |
| 6 | **Provider calls == 0 asserted explicitly** | forward variant: `assertEqual(loop3.provider_calls, 0)`. Approve variant is the CLI, which has NO provider client at all (structurally 0) | **YES** (on the forward path — the only path a provider could be reached; verified no provider call-site in the CLI approve path) |
| 7 | Refusal durably recorded as sealed hash-chained audit event AND chain verifies | approve: finds exactly one `operator_resume_pending_prompt_refused` (decision=refuse, reason=`pending_prompt_tampered`) + `AuditLog.verify_chain().ok`; forward: `verify_chain().ok` | **YES** (sealed event on approve path; see §7.2 re forward path) |

## 3. Non-vacuity — INDEPENDENTLY PROVEN by in-process mutation (not just producer assertion)

The producer's `test_non_vacuity_pre_fix_checks_pass` only *asserts the pre-fix predicates hold* — it does not execute pre-fix code. I independently reverted the fix in-process (scratchpad monkeypatch of `loop.verify_covered_instruction` and `cli.verify_covered_instruction` to a pre-fix anchor-only emulation; **no repo edits**) and re-ran `tools/test_agent_supervisor_c2_binding.py`:

- `test_two_field_forgery_at_approve_is_refused_fail_closed` → **RED**: `AssertionError: 0 != 1` — under pre-fix the CLI **approves the forgery (code 0)**.
- `test_two_field_forgery_after_approval_is_refused_no_provider` → **RED**: `LoopError not raised` — under pre-fix the loop **forwards the injection** (would call the provider).
- `FailClosedReasonCodes.test_old_shape_missing_instruction_refuses_uncovered` → **RED**: pre-fix accepts an old-shape record whose anchor matches (confirms AS-6 "no fallback to journal-resident-only verification" is genuinely enforced by the new code).
- `ClockInvariant` and `PostureUnchanged` stayed **GREEN**.

Conclusion: the new `verify_covered_instruction` reconstruction check is the sole gate standing between the two-field forgery and a forward. The forgery tests are non-vacuous and load-bearing. (`HappyPathBinding` also turned red under my emulation — this is an **artifact**: the APPROVED record does not carry `prompt_bytes_digest`, and my emulation demanded an anchor; it is not a signal about the fix. Confirmed by reading `approve_pending_prompt` loop.py:736-758, which persists only `approved_instruction`/`prompt`/`approved_digest`.)

## 4. R139 coverage detail
- **(a)** Exactly-once asserted by count (`len(...)==1`) and bytes verify against `build_forwarded_prompt(instruction)`. PASS.
- **(b)** Clock isolated: parked body is timestamp-free (`assertNotIn("FORWARDED AT", parked.prompt)` in `_park_real`), clock appended only by `stamp_forwarded_at` at forward time; `approval_digest` inputs contain no clock; `verify_covered_instruction` returns the timestamp-free body regardless of stamp. Message-id/exactly-once clock-independence is further covered by `LoopResumeForwardExactlyOnceTests`. PASS.
- **(c)** Post-approval tamper refuses (proven non-vacuous §3). PASS.
- **(d)** `PostureUnchanged` asserts `shadow.forwards==False`, `supervised.forwards==True`; grep-proof reproduced independently (§6, zero matches). PASS.

## 5. Weakening audit of the 3 UPDATED test files (`git diff 9c2ec25..ec0f55d`)
No prior assertion was deleted or relaxed without a strictly-stronger/equivalent replacement:
- **`park_approve_binding.py`**: `_park_real` gained 4 assertions (instruction reproduces digest+body, timestamp-free) — strengthened. `TamperAfterApproval` assertion retargeted `approved_digest` from byte-anchor → operator digest (correct new binding); the tamper attack body is unchanged. `HappyPath` byte-identity now partitions off the clock stamp then asserts `body==held_prompt` AND `digest_of(body)==anchor` — equivalent strength. Unit tests: `pending_prompt_unanchored`→`pending_prompt_uncovered` (the unanchored code path was legitimately removed; `test_byte_tamper_against_covered_instruction_refuses` is NEW, preserving the "tampered" reason-code coverage). No dangling refs to removed codes (grep clean).
- **`pending_prompt.py`** (+78 net): the two hardcoded-digest fixtures were replaced with `covered_pending()` because the old shape now (correctly) refuses under the new code; intent preserved and operator-digest binding added. `CrossProcessResumeTests` forwarded-bytes assertion now checks the operator-covered body (== held) + operator-digest binding — strengthened. `LoopResumeForwardExactlyOnceTests` fixture upgraded to a covered record; exactly-once intent preserved.
- **`reviewer.py`**: signature adaptation only; added `assertNotIn("FORWARDED AT", prompt)` (strengthening); the five-required-elements and no-prompt-raises assertions are intact.

No hidden regression.

## 6. Determinism / independence / evidence integrity — reproduced

| Check | Command | Result |
|---|---|---|
| Targeted set 3× | `pytest c2_binding park_approve_binding pending_prompt reviewer -q` ×3 | **112 passed** each run, 12.6/12.6/12.3s — no flakes |
| Ordering coupling | same four files in **reversed** order | **112 passed** |
| C2 file alone | `pytest c2_binding.py` | **10 passed** (matches "C2 file 10") |
| 5-file subset | `+ test_agent_supervisor_loop.py` | **215 passed** (matches producer subset) |
| Full suite | `pytest tools/test_agent_supervisor_*.py -q` | **1374 passed, 2 skipped** in 99.34s (matches after-count exactly; 2 skips are pre-existing POSIX guards) |
| Count arithmetic | +11 delta = 10 new C2 + net +1 park_approve unit tests → baseline 1363 → 1374 | **consistent** |
| R139d grep-proof | grep source diff for `assert_forwarding_allowed\|forwards=\|activate\|supervised_auto\|tier_\|autonomy\|shadow_only` | **zero matches** — no authority/forwarding/activation/tier surface touched |
| Scope | 8 changed files all in `allowed_paths` (`tools/agent_supervisor/`, `tools/test_agent_supervisor_*.py`, producer report); no forbidden path, no manifest/lockfile/directive edit | **confined** |
| Orphan check | `digest_of` no longer referenced in cli.py; `packet_reference` remains only as the dead `LoopConfig.packet_reference` field (loop.py:220), intentionally retained per R140 | **clean, disclosed** |

Producer-report file:line anchors and the `packet_reference` removal disposition match the actual diff. Audit chain is a genuine `prev_digest`/sha256 hash chain with truncation detection (`audit_log.py`, **unchanged** by this task), so property-7's `verify_chain().ok` is a real check.

**Soundness spot-check (G4-adjacent):** `approval_digest` and `build_forwarded_prompt` canonicalise identically (sorted str-cast paths, sorted str-cast stops, stripped action, raw task_id/stage over distinct dict keys). The reconstructed body is therefore uniquely determined by the operator digest up to a SHA-256 second-preimage — the forgery of `approved_instruction` itself is caught because any covered-field edit changes `approval_digest(instruction)` (tested by `test_instruction_not_reproducing_operator_digest_refuses_uncovered`). No field-boundary escape: any injected byte must live in a covered field, which moves the digest.

## 7. Coverage gaps / observations (severity-ranked — ALL NON-BLOCKING, advisory only)
1. **[Low] Property-6 assertion placement.** `provider_calls==0` is asserted on the forward variant only; the approve variant (CLI) has no provider client so it is structurally 0. Satisfied, but an explicit `provider_calls==0` (or a "no provider client instantiated") note on the approve path would make the 7-property mapping self-evident. *Not required — the property is genuinely met.*
2. **[Low] Forward-path refusal is not a dedicated sealed audit event.** `_resume_approved_forward` raises `forwarded_prompt_unavailable` and `run()` propagates it (halt, journal unchanged, chain intact) without appending a `*_refused` event; only the APPROVE path seals a refusal event. This satisfies R139(c) ("post-approval tampering still refuses") and honoring R140 (no broader changes) is correct — but the producer report's per-scenario map lists property 7 (sealed refusal) against the forward test, which is generous. Property 7 is fully satisfied by the approve-path test. *Reporting-accuracy nit, not a functional gap.*
3. **[Trivial] `ClockInvariant` tautology.** `assertEqual(approval_digest(**x), approval_digest(**x))` compares a value to itself. Harmless; the meaningful clock-invariance is demonstrated by the timestamp-free body + forward-time stamp and the exactly-once message-id stability elsewhere.
4. **[Trivial] `packet_reference` dropped from in-prompt text.** Downstream provenance narrows (the `PERMITTED PATHS (packet …)` label is gone); `TASK: <task_id>` remains in the body and packet provenance stays in the outbox payload/audit. Disclosed, unavoidable (the reference is non-deterministic and cannot be covered by the stability-locked `approval_digest`), and consistent with the determinism requirement.

None of these are required corrections. I am not attaching any blocking correction to this PASS.

---

**G4 VERDICT: PASS**
