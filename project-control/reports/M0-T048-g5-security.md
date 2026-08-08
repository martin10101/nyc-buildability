# G5 Security Review Gate Report — M0-T048 (close G5-C2: bind forwarded content to the operator-named approval digest; owner am.14 / D-010 R134–R143)

**Reviewer:** security-reviewer (independent, read-only). This task closes **my own** prior M0-T046 G5 finding C2 / MEDIUM M-1.
**Lane split:** G3 = correctness, G4 = QA/evidence, G5 (this) = security; DCV rules the R136/R137/R140 wording separately.

## Frozen reviewed identity (confirmed with `git rev-parse`)
- Code worktree `C:/Users/MLFLL/Downloads/nyc-zoning/orch`, branch `task/M0-T048-c2-close`, HEAD `ec0f55d28da90d57467321ad65c922fdde09f043` ✓ (matches frozen `ec0f55d`).
- Base `9c2ec252b509ddf6bb067325c6aa28c2cdc6ff4d` (`9c2ec25`, contains accepted M0-T046) ✓. Diff = `git diff 9c2ec25..ec0f55d`.
- Control-plane primary checkout branch `control/M0-T048-c2-close` @ `ce432c1de851bc54c09d84d1adfae96c490d2fe1` ✓ (packet, directive source-014, producer report, my M0-T046 finding).

## Evidence reproduced in-sandbox
- Targeted 4-file pack: `python -m pytest tools/test_agent_supervisor_c2_binding.py tools/test_agent_supervisor_park_approve_binding.py tools/test_agent_supervisor_pending_prompt.py tools/test_agent_supervisor_reviewer.py -q` → **112 passed in 13.17s** (matches the 112 expected).
- Full supervisor suite: `python -m pytest tools/test_agent_supervisor_*.py -q` → **1374 passed, 2 skipped in 105.18s** — independently reproduced, matching the orchestrator-captured 1374/2 and the producer's +11/0-fail delta.
- Diff confined to allowed_paths (`git diff --stat`): only `tools/agent_supervisor/{cli,codex_reviewer,loop}.py`, `tools/test_agent_supervisor_*.py`, and `project-control/reports/M0-T048-producer-report.md`. Every forbidden path (`.claude/`, `apps/`, `services/`, `.github/`, `directives/`, `package.json`, lockfiles, `requirements*.txt`) untouched.

---

## RULING ON THE CENTRAL GATE QUESTION — **C2 IS CLOSED**

**R136 property:** an attacker who modifies BOTH the parked prompt bytes AND `prompt_bytes_digest`, while leaving the operator-named approval digest unchanged, MUST NOT be able to cause altered content to be forwarded; the forwarded content must be cryptographically bound to information independently covered by the operator-named `approval_digest`.

**How the design achieves it (verified against source):**
- The forwarded content is no longer the journal `prompt` bytes. At approve, `approve_pending_prompt` sets `record["prompt"] = expected_body` where `expected_body = verify_covered_instruction(...)` (loop.py:748–754); at resume, `_resume_approved_forward` forwards `stamp_forwarded_at(body)` where `body` is that reconstruction (loop.py:2138–2152). **The mutable `prompt`/`prompt_bytes_digest` journal fields are never what gets forwarded** — the reconstruction is.
- `verify_covered_instruction` (loop.py:639–695) accepts only if `approval_digest(**fields) == operator_digest`, where `fields` are read from the **journal-resident `approved_instruction` at verification time** (loop.py:659–670, 683) and `approval_digest` is `digest_of` (SHA-256 of canonical JSON) over the same five canonical fields (loop.py:567–582). `build_forwarded_prompt` renders the body from those identical canonical fields (codex_reviewer.py:663–702). Therefore a digest match pins **every variable byte** of the body (the rest is constant source text); the binding is SHA-256 second-preimage-hard, not "solely mutable journal fields."
- The operator-named digest is genuinely operator-anchored at approve: the CLI refuses unless `supplied == recorded` (cli.py:1688), i.e. the operator's independently-typed `--approve-prompt-digest` equals the journal `digest`; `approved_digest`/`prior_digest` are then bound to that operator digest (loop.py:744, 757; asserted by `TamperAfterApproval` expecting `parked["digest"]`).

**Attack outcomes (all fail closed — code + tests):**
- *Two-field forgery* (prompt + prompt_bytes_digest, instruction and operator digest intact): reconstruction from the untouched `approved_instruction` differs from the forged bytes → `digest_of(expected_body) != anchor` and `digest_of(prompt) != digest_of(expected_body)` → `pending_prompt_tampered` (loop.py:685–695). And even absent those checks, the forged bytes are never forwarded. Proven at approve (`test_two_field_forgery_at_approve_is_refused_fail_closed`, expects `pending_prompt_tampered`) and at resume (`test_two_field_forgery_after_approval_is_refused_no_provider`, `forwarded_prompt_unavailable`, `provider_calls == 0`, chain verifies).
- *Three-field forgery* (also rewrite `approved_instruction` consistently): `approval_digest(attacker_instruction)` is recomputed over the journal instruction and must equal the unchanged operator digest → a SHA-256 second preimage → infeasible → `pending_prompt_uncovered` (loop.py:683–687; `test_instruction_not_reproducing_operator_digest_refuses_uncovered`). **There is no path where a stored/cached digest substitutes for this recomputation** — `verify_covered_instruction` never reads a digest out of the instruction; it always recomputes.
- *Non-vacuity*: `test_non_vacuity_pre_fix_checks_pass` asserts the forged record satisfies BOTH pre-fix predicates (`digest_of(prompt)==anchor` and operator-digest match) that were the entire M0-T046 gate, so pre-fix code would have re-hashed and forwarded the injection; post-fix refuses. Load-bearing and consistent with the exact pre-fix behavior I documented in the M0-T046 finding.

**Second-preimage / field-escape (lane-2 concern):** `approval_digest` and `build_forwarded_prompt` share one canonicalization (sorted `str` paths, sorted `str` stops, `strip()`ped action — loop.py:579–581 vs codex_reviewer.py:679–685). A digest match ⟹ identical canonical fields ⟹ identical body (barring SHA-256 collision); the only non-injectivity is *same body / different digest*, which is harmless (different digest → refused). No covered field can ESCAPE into an attacker-injected instruction line without changing the digest; and a value the operator legitimately approved is approval-covered by definition. **No lossy collapse enabling same-digest/different-body.**

**Conclusion:** the two-field (and three-field) journal-write forgery that R136 names now fails closed at approve and at resume, with zero provider calls and a sealed hash-chained refusal. **C2 CLOSED.**

---

## Per-lane results

**Lane 1 — Instruction-forgery (recompute integrity): PASS.** `verify_covered_instruction` recomputes `approval_digest` over the journal-resident `approved_instruction` every call (loop.py:659–687); the digest computation is byte-identical to `approval_digest_for` (loop.py:1955–1960) which produces the operator-named value at park. No journal field substitutes for the recomputation. Old `if not approved_digest or digest_of(prompt) != approved_digest` predicate fully **replaced** (cli.py:1704–1726; loop.py:2137–2144) — no residual journal-anchor-only branch.

**Lane 2 — Second-preimage / field-escape: PASS.** Shared canonicalization proven above; `digest_of` = SHA-256 of `canonical_json` with `sort_keys=True`, stable separators, UTF-8 (models.py:33–66) — no dict-order/whitespace ambiguity. Static template bytes are non-attacker-controllable source. (INFO N-2 below on inline field rendering — not exploitable.)

**Lane 3 — Forward-time stamp: PASS.** `stamp_forwarded_at(body) = f"{body}FORWARDED AT: {to_utc_iso()}\n"` (codex_reviewer.py:705–715). Appended once, at the very end, OUTSIDE the verified/parked body, AFTER verification. `to_utc_iso` is a fixed `strftime` numeric format from the system clock (models.py:69–79) — no attacker input, no newline injection. Verification reconstructs the timestamp-free body and never inspects the stamp; the message-id keys on the approval digest, so clock differences never mint a second forward or invalidate approval (`test_clock_only_change_does_not_invalidate_the_approval`).

**Lane 4 — Downgrade/fallback: PASS.** Every acceptance predicate enumerated. Approve (cli.py:1657–1726): emergency-stop → state==WAIT_FOR_OWNER → non-empty journal `digest` → non-blank `supplied` → `supplied==recorded` (operator input) → `verify_covered_instruction` (operator-digest-anchored). Resume (loop.py:2104–2145): emergency-stop → `last_trigger==owner_approved_pending_prompt` → `record.approved` → non-empty prompt → `verify_covered_instruction` (anchored to `approved_digest`). Old-shape/missing/malformed records **refuse** (`pending_prompt_uncovered`) with no fallback (`test_old_shape_missing_instruction_refuses_uncovered`, `test_malformed_instruction_refuses_uncovered`).

**Lane 5 — Prior-check preservation: PASS (strictly strengthened).** Park byte anchor retained (loop.py:1862) and now cross-checked against the reconstruction (defense-in-depth step 3, loop.py:688–695). Sealed hash-chained refusal retained (cli.py:1711–1718; chain verifies in tests). Resume digest check replaced by the strictly stronger reconstruction-vs-operator-digest check. Blank/whitespace-digest refusal (cli.py:1683), argparse-required digest, and re-approval-dead (`digest` key dropped) all intact. No weakened path.

**Lane 6 — Posture invariants: PASS.** `assert_forwarding_allowed` unchanged (loop.py:859–865), still called first in `forward_exactly_once` (1977) and `_resume_forward` (2007). Grep of `+/-` diff lines for `assert_forwarding_allowed|forwards=|activate|supervised_auto|tier_|autonomy|SHADOW|_guard` → none. Zero new dependencies (only new import is `stamp_forwarded_at` from the same module, loop.py:58); no manifest/lockfile touched. No new `subprocess`/`socket`/`urllib`/`eval`/`exec`/`os.system` in added lines. No secrets/PII added (scan clean). `PostureUnchanged` test asserts shadow.forwards==False, supervised.forwards==True.

**Lane 7 — R138 adversarial tests: PASS.** They attack the right surfaces at BOTH approve-time and post-approval+resume, driving the REAL loop (park), REAL CLI (approve), REAL loop (forward) and forging the durable journal between steps. The 7 properties are asserted: authentic park, consistent two-field mutation, operator digest unchanged, attempt approve/resume, fail-closed (exit 1 / LoopError), `provider_calls == 0` (real counter, loop.py:1539/1658), sealed refusal with `verify_chain().ok`. Non-vacuity, happy-path-forwards-once, clock-invariant, posture, and AS-6 distinct-reason-code tests all present and passing.

---

## Findings (severity-ranked)

No CRITICAL, HIGH, or MEDIUM findings. No blocking corrections.

**INFO N-1 — cross-process resume anchors on the durable `approved_digest` (acknowledged full-journal-write residual; NOT a regression, OUTSIDE R136).** loop.py:2145, 2137–2140. At cross-process resume there is no live operator; the operator-named digest is read from the journal (`approved_digest`). A full-journal-write attacker who, **post-approval**, rewrites `approved_digest` AND `approved_instruction` (and prompt/anchor) *all consistently* could forward a reconstruction of their own instruction. This **changes the operator-named digest** and so falls outside R136's explicit "leaving the operator-named approval digest unchanged" premise. It is the identical trust-boundary that existed in M0-T046 (there: rewrite `prompt`+`approved_digest`), requires cross-journal cryptographic signing to truly close (explicitly excluded by R140 "no new infrastructure"), and is honestly disclosed (producer report §8.5). **Activation-relevance:** none for the C2 property; it is the standing full-journal-write trust-domain limit, unchanged by this task. Recorded for provenance only.

**INFO N-2 — covered field VALUES render inline in the forwarded body.** codex_reviewer.py:679–690. A stop_condition/allowed_path/action string containing newline + pseudo-header text renders as additional body lines. This is **approval-covered by definition** (the operator approved those exact bytes; the digest covers them) and cannot be induced by an attacker without changing the digest → refusal. Not exploitable within the journal-write threat model. Note only.

**INFO N-3 — `packet_reference` dropped from the forwarded body.** codex_reviewer.py (removed from the PERMITTED PATHS header); `LoopConfig.packet_reference` retained but dead (loop.py:220). Minor downstream-provenance reduction, disclosed (producer §8.2/§8.4); the enforced authority scope (allowed_paths) and packet provenance in the outbox payload/audit are retained. No security implication (the packet label was informational, not an enforcement mechanism). Out of my lane / product note.

---

## Corrections attached to this PASS

**None.** There are no blocking corrections. C2 is closed; the M0-T046 protections are preserved or strengthened; posture, dependency, injection, subprocess/network/eval/exec, and secrets/PII invariants all hold; the diff is confined to allowed_paths.

(Note: the DCV lane independently rules whether the R136/R137/R140 *wording* is met — my security ruling is that the property is genuinely and cryptographically closed.)

**G5 VERDICT: PASS**
