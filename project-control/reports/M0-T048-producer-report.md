# M0-T048 producer report — close the G5 C2 residual (D-010 am.14, R136/R137)

**Producer:** backend-engineer. **Worktree:** `C:/Users/MLFLL/Downloads/nyc-zoning/orch`,
branch `task/M0-T048-c2-close`, base `9c2ec25` (contains accepted M0-T046). Evidence
only — no compliance claims; the independent gate rules.

## 0. Packet/directive availability (disclosure)

`project-control/tasks/M0-T048.json` and
`project-control/directives/D-010-.../source-014-amendment.md` are **ABSENT** from this
branch (base predates the control-branch merge that carries them; the directive dir
holds source-001..013 only). I implemented against the AS-1..AS-6 / R136–R140 spec
reproduced verbatim in the dispatch prompt and the two governing M0-T046 reports
(`M0-T046-g5-security.md` C2/M-1; `M0-T046-dcv-final.md` R124 predicates). **If the
packet on the control branch differs in any AS wording, the packet governs and this
work should be re-checked against it.**

## 1. Design chosen and why

**Hybrid of the owner's two candidate constructions (R137):** move the `FORWARDED AT:`
clock to actual forward time **and** persist/recompute the structured approved
instruction at approve/resume time. Concretely:

1. `build_forwarded_prompt` (codex_reviewer.py) now emits a **deterministic,
   timestamp-free body** that is a pure function of exactly the five fields the
   operator-named `approval_digest` covers, **canonicalised identically** to that digest
   (sorted permitted paths, sorted stop conditions, stripped action). The `FORWARDED AT:`
   clock is appended only at forward time by the new `stamp_forwarded_at`, excluded from
   the binding (S13.5 preserved).
2. The parked record persists the **structured approved instruction**
   (`approved_instruction`). At approve (CLI) and at resume (loop), the new module
   function `verify_covered_instruction` **reconstructs** the body from that instruction
   and refuses fail-closed unless `approval_digest(instruction) == the operator-named
   digest`. `approved_digest` is then bound to the **operator-named approval digest
   itself** (not a journal-resident byte anchor).

Because `build_forwarded_prompt` and `approval_digest` are pure functions of the *same*
canonical material, an `approval_digest` match proves the reconstructed body is exactly
what the operator approved. The forwarded content is therefore derived from
operator-covered material and never trusted from the mutable `prompt`/`prompt_bytes_digest`
journal fields.

### Determinism inventory of `build_forwarded_prompt` inputs (the required gap analysis)

| Input (old signature) | In forwarded bytes? | Covered by operator `approval_digest`? | Resolution |
|---|---|---|---|
| `task_id` | yes | yes | reconstructed from covered instruction |
| `stage` | yes | yes | reconstructed |
| `allowed_paths` | yes | yes (sorted) | rendered **sorted** to match the digest's canonical form → no reorder residual |
| `decision.next_claude_prompt` (→ `requested_action`) | yes | yes (stripped) | reconstructed |
| `stop_conditions` | yes | yes (sorted) | rendered sorted |
| `packet_reference` | yes (`PERMITTED PATHS (packet X)`) | **NO** — deliberately excluded from `approval_digest` because "its own digest moves with the clock and with live git state" (locked by `ApprovalDigestStabilityTests`, loop test) | **gap closed by removing it from the body.** It is non-deterministic and cannot be covered without breaking the stability invariant; leaving it in would be a non-covered forwardable byte. Provenance of which packet is retained via `task_id`/`reviewed_checkpoint_id` in the outbox payload + audit trail. |
| `FORWARDED AT` timestamp | yes | no (the clock) | **moved to forward time**, excluded from the binding (R137's allowed clock stamp) |

After this, **every byte of the forwarded body is derivable from operator-covered
material, plus only the forward-time clock stamp** — satisfying R136/R137. `packet_reference`
could NOT be closed by adding it to `approval_digest`: that would make the operator digest
move with live git state and re-introduce the "digest-bound approval can never match"
dead-end the stability tests lock. Removing it from the body was the smallest correct
closure.

## 2. What the binding covers end-to-end (park → approve → resume → forward)

- **park** (loop.py ~1783–1866): builds one `instruction` dict; `forwarded_prompt =
  build_forwarded_prompt(**instruction)` (timestamp-free); parks `approved_instruction`,
  `prompt`, `prompt_bytes_digest = digest_of(prompt)`, and `digest = approval_digest`.
- **approve** (cli.py `cmd_resume_pending_prompt` ~1695–1724 → loop `approve_pending_prompt`
  ~692–735): `verify_covered_instruction` recomputes the body from `approved_instruction`,
  requires it to reproduce the operator-named digest, then binds `approved_digest =`
  operator digest. Fail-closed writes a **sealed** `operator_resume_pending_prompt_refused`
  event (reason = distinct code) before any transition.
- **resume/forward** (loop `_resume_approved_forward` ~2124–2145): reconstructs and
  re-verifies against `approved_digest`, then forwards `stamp_forwarded_at(body)` exactly
  once (message id keys on the approval digest, unaffected by the clock).

The M0-T046 checks are preserved or strengthened: park byte anchor still recorded and
now cross-checked against the reconstruction (defense in depth); sealed hash-chained
refusals retained; the resume digest check is replaced by the strictly stronger
reconstruction-vs-operator-digest check.

## 3. Files changed (paths + line anchors)

- `tools/agent_supervisor/codex_reviewer.py` — `build_forwarded_prompt` (~663–702): drop
  `packet_reference` + `FORWARDED AT` from the body; canonicalise (sort) paths/stops;
  new `FORWARDED_AT_PREFIX` + `stamp_forwarded_at` (~705–715).
- `tools/agent_supervisor/loop.py` — import `stamp_forwarded_at` (58); digest-doc comment
  (~527–563); new `verify_covered_instruction` (~627–692); rewritten `approve_pending_prompt`
  (~694–735); park site builds/persists `approved_instruction`, timestamp-free body
  (~1783–1866); in-process forward stamps at forward time (~1882–1887);
  `_resume_approved_forward` reconstruct+verify+stamp (~2124–2149).
- `tools/agent_supervisor/cli.py` — import `verify_covered_instruction`, drop now-unused
  `digest_of` (~109–122); resume pre-transition verification rewritten to reconstruction
  with distinct reason codes (~1695–1724).
- `tools/test_agent_supervisor_reviewer.py` — new `build_forwarded_prompt` signature (2 sites).
- `tools/test_agent_supervisor_park_approve_binding.py` — `_park_real` asserts covered
  instruction; operator-digest / body-plus-stamp assertions; `covered_pending` helper;
  three unit tests rewritten to the operator-digest binding.
- `tools/test_agent_supervisor_pending_prompt.py` — `covered_pending` helper; four
  fixtures/assertions updated to the covered-record shape + operator-digest binding.
- `tools/test_agent_supervisor_c2_binding.py` — **NEW** dedicated AS-1/R139/AS-6 pack.

`LoopConfig.packet_reference` (loop.py:220) is intentionally **left in place** though now
unused by the body (removing a config field is broader cleanup barred by R140).

## 4. Per-scenario evidence map

| Scenario | Test(s) |
|---|---|
| **AS-1** (R138, 7 properties: authentic park; mutate BOTH prompt+prompt_bytes_digest consistently; operator digest unchanged; attempt approve/resume; FAIL CLOSED; provider calls == 0; sealed hash-chained refusal, chain verifies) | `c2_binding.py::TwoFieldForgery::test_two_field_forgery_at_approve_is_refused_fail_closed` (approve path, props 1–5,7) + `::test_two_field_forgery_after_approval_is_refused_no_provider` (forward path, props 4–7 incl. provider_calls==0) |
| **AS-1 non-vacuity** | `TwoFieldForgery::test_non_vacuity_pre_fix_checks_pass` — asserts the forged record satisfies **every pre-fix acceptance predicate** (anchor match + operator-digest match) so pre-fix code would forward the injection, then shows post-fix refuses |
| **R139(a)** happy path forwards once; bytes verify against approval-covered binding | `c2_binding.py::HappyPathBinding::test_happy_path_forwards_once_and_binds`; also `park_approve_binding.py::HappyPath::test_happy_path_operator_digest_binds_and_forwards` |
| **R139(b)** clock-only diff does not invalidate approval (S13.5, executable) | `c2_binding.py::ClockInvariant::test_clock_only_change_does_not_invalidate_the_approval` |
| **R139(c)** post-approval tamper refuses at resume | `TwoFieldForgery::test_two_field_forgery_after_approval_is_refused_no_provider`; `park_approve_binding.py::TamperAfterApproval` |
| **R139(d)** no authority/forwarding-guard/activation surface changed | `c2_binding.py::PostureUnchanged` + grep-proof §6 |
| **AS-6** old-shape/missing/malformed → distinct fail-closed reason codes | `c2_binding.py::FailClosedReasonCodes::{test_old_shape_missing_instruction_refuses_uncovered, test_malformed_instruction_refuses_uncovered, test_instruction_not_reproducing_operator_digest_refuses_uncovered, test_byte_anchor_tamper_refuses_tampered}` (`pending_prompt_uncovered` vs `pending_prompt_tampered`); unit-level in `park_approve_binding.py::ApprovePendingPromptUnitTests` |

## 5. Non-vacuity proof (AS-1)

`test_non_vacuity_pre_fix_checks_pass` is executable and load-bearing: for the two-field
forgery it asserts `digest_of(forged_prompt) == forged_prompt_bytes_digest` (the M0-T046
anchor check **passes**) and `operator_digest == recorded digest` (the CLI operator match
**passes**). Under the pre-fix code those two predicates were the *entire* gate, and
`approve_pending_prompt` re-hashed the evil bytes into `approved_digest` and forwarded
them — exactly the C2/M-1 finding. The test then shows the post-fix reconstruction from
`approved_instruction` can never contain the injected marker and the CLI now refuses
(code 1). This documents that the new `verify_covered_instruction` check is the sole
thing standing between the forgery and a forward.

## 6. R140 prohibition confirmation + R139(d) grep-proof

- **R140** ("No supervisor redesign / no additional features / no new infrastructure / no
  broader cleanup; one bounded security fix"): the change is confined to the park→approve→
  resume→forward binding. No new dependency (stdlib only; no manifest/lockfile touched).
  SHADOW-ONLY posture, activation flags, forwarding guards, autonomy tiers untouched.
- **Grep-proof:** `git diff -- tools/agent_supervisor/loop.py tools/agent_supervisor/cli.py`
  filtered for `assert_forwarding_allowed|forwards *=|default_mode|activate|supervised_auto|
  assert_forward|tier_|autonomy` → **"NO changes to forwarding-guard/activation/tier
  surfaces"**. `assert_forwarding_allowed` remains called unchanged in both forward paths.
- Writes confined to allowed paths (`tools/agent_supervisor/`, `tools/test_agent_supervisor_*.py`,
  this report). No `.claude/`, `apps/`, `services/`, `.github/`, `directives/`, or manifest edits.

## 7. Self-check evidence (exact counts)

- Touched-module subset (`c2_binding + park_approve_binding + pending_prompt + reviewer +
  loop`): **215 passed** in 22.14s.
- FULL suite `python -m pytest tools/test_agent_supervisor_*.py`: **1374 passed, 2 skipped**
  in 90.87s. Baseline at branch base was **1363 passed / 2 skipped**; delta **+11 passing**
  (10 new C2 tests + net +1 in the rewritten binding unit tests), **0 failures, 0 new skips**.

## 8. Limitations / honest disclosures

1. **Packet/directive not on branch** (§0) — spec taken from the dispatch prompt + M0-T046
   reports; the control-branch packet governs on any wording conflict.
2. **`packet_reference` removed from the forwarded prompt text.** This slightly reduces
   in-prompt provenance for the downstream agent (the packet label no longer appears in the
   PERMITTED PATHS header). It was unavoidable: the reference is non-deterministic and cannot
   be covered by the stability-locked `approval_digest`. Packet provenance remains in the
   outbox payload (`task_id`, `reviewed_checkpoint_id`) and audit trail.
3. **Path/stop ordering** is now rendered sorted (matching the digest's canonicalisation) so
   a reorder cannot produce non-covered bytes; this is a cosmetic change to forwarded text
   ordering only (same set), and existing tests assert only fragment presence, not order.
4. The `LoopConfig.packet_reference` field is retained but dead; a future bounded cleanup
   could remove it (out of scope here per R140).
5. Threat model unchanged from M0-T046: this hardens the SHADOW-ONLY pre-activation posture;
   the attacker still requires full journal write. The fix removes the *specific* two-field
   forgery window C2 named; it does not claim to close capabilities outside the journal-write
   trust domain.

## 9. Requested status

`awaiting_gate` — submit for independent G3/G5 (+ DCV for the R136/R137/R140 wording) review.
Producer cannot accept own work.
