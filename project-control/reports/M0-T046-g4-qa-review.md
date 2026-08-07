# G4 QA GATE REPORT — M0-T046 (owner am.12 pre-activation hardening)

**Reviewer:** qa-engineer (independent; read-only per ADR-005). **Gate lane:** G4 (QA / evidence integrity). **Date:** 2026-08-07 (UTC).
**Frozen identity verified by `git rev-parse`:** code worktree `C:/Users/MLFLL/Downloads/nyc-zoning/orch`, branch `task/M0-T046-preactivation`, HEAD `569d1a7bc2447b6884753b813de431a1def365a8`, base `ae627e514be65be2b52a0526ad880cd026b17c80` (`ae627e5`). Control-plane evidence read from primary checkout at packet/report paths (`M0-T046.json`, `source-012-amendment.md`, producer report, evidence map, G2 self-check).
**Producer ≠ reviewer confirmed.** I reproduced tests independently on this Windows unelevated machine (Python 3.11.9, win32).

## 1. Per-AS conformance against the PACKET text (verbatim AS-1..AS-6)

The producer's AS table used re-derived labels (disclosed in G2 self-check). I mapped each **packet** scenario to concrete tests and judged sufficiency.

| Packet AS | Requirement (packet text) | Evidence mapped | Verdict |
|---|---|---|---|
| **AS-1** (R124, primary) | approval requires `--approve-prompt-digest`, verifies against parked bytes via same serialization, binds `approved_digest` to operator-named value; resume path unchanged/strengthened | `test_happy_path_operator_digest_binds_and_forwards` (asserts `approved_digest == park anchor`, byte-identical forward exactly once, record consumed); `ApprovePendingPromptUnitTests` (3); CLI arg tests. loop.py:1776 anchor at park, loop.py:660-679 fail-closed binding, resume check loop.py:2042 retained. | **PASS** |
| **AS-2** (R124, adversarial — BOTH variants) | tamper BEFORE approval → refused fail-closed (no `approved_digest`, nothing forwardable); tamper AFTER approval → caught at resume-time digest check; both executable | **Before:** `test_tamper_between_park_and_approval_is_refused` — CLI exits 1, `"byte anchor"` in stderr, state stays `WAIT_FOR_OWNER`, record not approved, exactly one SEALED (hash-chained) `operator_resume_pending_prompt_refused` event, chain still verifies. **After:** `test_tamper_after_approval_is_caught_at_resume` — resume raises `forwarded_prompt_unavailable`, **0 provider calls**. Both present, both pass. | **PASS** |
| **AS-3** (R125/R126, primary) | four owner-acknowledged conditions each locked: fork reported deterministically; fails closed; never silently repaired/hidden; condition recorded (`audit_chain_ok:false`); continuation refused until explicit repair | `test_agent_supervisor_audit_fork_lock.py` (6). (1) `test_1_verify_chain_reports_duplicate_sequence`; (2) `test_2_reopen_records_a_load_error_and_append_refuses`; (3) `test_3_a_refused_append_neither_repairs_nor_hides_the_fork` (byte-equality + verify still reports); (4) `test_4_continuation…refused`, `test_4_surface…audit_chain_ok_false` (real `recovery-status`/`status`, status exits non-zero), `test_4_repair…restores_appendability`. **Mutation-proven non-vacuous (see §2).** | **PASS** |
| **AS-4** (R127/R128, primary) | with hardened ACLs: unelevated CAN read; CANNOT modify/overwrite/delete/rename/replace/re-ACL, nor bypass via parent; modification only via elevated path; digest verification remains | Parser+verdict over PROTECTED_FILE/PROTECTED_DIR fixtures → PROTECTED; `harden_controller_config.ps1` produces exactly the ACL shape the verdict recognizes (user RX-only on file+parent, inheritance stripped, Admin/SYSTEM full); `config.py` untouched (digest gate retained — confirmed absent from diff). **Live PROTECTED verdict against a real hardened file is fixture-proven only** (see §4/§5 carry-forward). | **PASS (bounded)** |
| **AS-5** (R128, ambiguity) | undeterminable ACL state (probe error, ambiguous icacls, unexpected principals) → reports condition and fails closed, NEVER 'protected'; probes bounded | `FailClosedTests`: icacls error, ambiguous output, probe error, missing file, combined-requires-both → all `UNKNOWN`, `is_protected()==False`; `DoctorPostureTests` no-`--config` → `SKIPPED`, not protected. Doctor `protected:true` only when state==PROTECTED (verified in cli.py `_controller_config_acl_posture`). | **PASS** |
| **AS-6** (R123/R129, prohibition over diff surface) | only the three scopes; diff confined to allowed_paths; SHADOW-ONLY untouched; no activation-flag flips | `git diff --stat ae627e5..569d1a7` = **11 files, all inside allowed_paths** (`tools/agent_supervisor/**` + `tools/test_agent_supervisor_*.py` + producer report); **no package.json / package-lock.json / requirements*.txt**; no `.claude/ apps/ services/ .github/ directives/` writes. Doctor ACL is a separate `posture` key, NOT in `checks` → `ok` independent of ACL (shadow not broken). `limited_auto` string unchanged; config.py untouched. | **PASS** |

## 2. Test quality

- **Determinism:** target set (`park_approve_binding` + `audit_fork_lock` + `os_acl` + `pending_prompt`) run **3×** → `58 passed` every time (10.86s / 6.09s / 5.34s). The estop fork is *injected* as a static forked-chain shape (`_fork()` rewrites `audit.jsonl` with a duplicate sequence sharing `prev_digest`), **not a real-process race** — no timing dependence. ACL states are exercised via icacls-output fixtures + `os_acl._run_icacls`/`probe_write_open` monkeypatch, plus bounded live probes on temp files. No ordering coupling (each `TestCase` uses its own `TemporaryDirectory`).
- **Non-vacuity (regression-catch, mutation-proven):** I reverted each fix in-process (scratchpad monkeypatch, **no repo edit**) and re-ran the locks:
  - Revert `_load_head_from_log` to pre-fix → **4/6** fork-lock tests turn RED: `test_2` (load_error unexpectedly None), `test_3` (`AuditChainError not raised` — append silently succeeded), `test_4_continuation`, `test_4_repair`. The two pure-**reporting** tests (`test_1` verify_chain, `test_4_surface`) correctly stay GREEN — exactly the right partition, confirming the fail-closed locks target the append-refusal behavior. Directly answers the packet's probes: **yes, test 3 fails if append silently repairs; yes, test 4 fails if continuation is allowed.**
  - Revert `approve_pending_prompt` to pre-fix (re-hash, no anchor) → **2/3** binding unit tests turn RED (`test_missing_anchor_refuses`, `test_anchor_mismatch_refuses` — `LoopError not raised`); happy-path stays green as expected (re-hash == anchor on a match).
- **Negative-path coverage:** blank digest (`test_blank_digest_refused`), missing digest arg (`test_missing_digest_arg_exits_nonzero`), missing anchor, anchor mismatch, missing file (`test_missing_file_is_unknown`, `error:missing`), icacls error, ambiguous output, probe error → all covered and fail-closed.
- **Fixture edits do NOT weaken assertions:** the two `CliResumeConsumeTests` fixtures in `test_agent_supervisor_pending_prompt.py` only **add** `prompt_bytes_digest = lp.digest_of(prompt)`. This is *required* alignment with the new park shape (a held-bytes record now needs a valid anchor to be approved), not a masked regression — the "no anchor ⇒ refuse" behavior is independently locked by the new `park_approve_binding` tests. Pre-existing assertions (record approved, `digest` key dropped, re-approval refused) are unchanged; all 19 `pending_prompt` tests pass.

## 3. Evidence integrity (reproduced)

| Claim | Producer/G2 | My independent reproduction | Result |
|---|---|---|---|
| New tests | 8 + 6 + 25 = 39 | park_approve `8`, audit_fork `6`, os_acl `25` | ✅ match |
| Targeted 7-module | 233 passed | `233 passed in 35.36s` | ✅ match |
| New+touched | 58 passed | `58 passed` (×3) | ✅ match |
| Full suite AFTER | 1356 passed / 2 skipped | `1356 passed, 2 skipped in 210.20s` | ✅ match (independent) |
| Delta arithmetic | +39 = 8+6+25; 1356−39=1317 | 1356 reproduced; 39 reproduced ⇒ 1317 consistent | ✅ consistent |
| BEFORE baseline | 1317/2 (M0-T045 G4 figure) | **Not re-run** — base checkout isolated from reviewer worktree | ⚠ accepted (arithmetically consistent with reproduced AFTER+delta; see gap G3) |

All reproducible figures match exactly. The G2 orchestrator full-suite figure (1356/2, 537.84s) is corroborated by my own 1356/2 (210s, warmer machine).

## 4. Honest-limitation accuracy

1. **Deferred live PROTECTED proof (R128):** ACCURATE. An unelevated process genuinely cannot mint an Administrators-owned UAC-gated file; the parser/verdict recognize a PROTECTED fixture and the harden script produces exactly that shape. Every unelevated-reachable state (writable→NOT_PROTECTED; ambiguous/error→UNKNOWN) is proven now. Genuinely out of the R128 non-destructive + R129 no-redesign bound.
2. **Parent-container / grandparent DeleteChild residual:** ACCURATE and disclosed in both the report and the script itself. Renaming/deleting the parent depends on the grandparent's DeleteChild; not built to avoid an invasive ACL rewrite of unrelated directories. Within the no-redesign bound.
3. **SCOPE-1 full-journal-forgery residual:** ACCURATE. The fix closes the tamper-`prompt`-only window; a consistent rewrite of BOTH `prompt` and `prompt_bytes_digest` is the pre-existing full-write threat the original G5 finding itself scoped out ("same access already forges checkpoints/decisions"). I verified this against the finding's own scope note.

No undisclosed defect found in the targeted hunt: (a) **no code path forwards an anchor-less record** — a held-bytes record with no/invalid anchor is refused at approval (`pending_prompt_unanchored`/`_tampered`); an old-shape no-bytes record is refused at forward (`forwarded_prompt_unavailable`, loop.py:2036); (b) doctor reports `protected:true` **only** for a definitive PROTECTED; (c) the estop fork lock is enforced at open on `audit.jsonl` and is not bypassable by ordinary appends.

## 5. Coverage gaps (severity-ranked)

- **G1 — LOW / carry-forward (NOT a blocking correction).** AS-4's live `PROTECTED` verdict and the "cannot rename/delete/replace" end-state against a *real hardened* config are fixture-proven only; the harden script's runtime correctness is verified by string-presence + refuses-unelevated, not by an elevated automated test. This is inherent to an unelevated reviewer/CI and correctly disclosed. **Required orchestrator verification AFTER the owner's elevated apply, BEFORE activation** (not before accepting M0-T046): run the documented `harden_controller_config.ps1` under UAC, then confirm `doctor --config … --json` reports `controller_config_acl.protected: true`. This is the R128 live proof + sequenced by the directive itself (R131/R132), so it does not block acceptance of this task.
- **G2 — LOW / informational.** Deleting `audit.jsonl` entirely resets `_load_head_from_log` to genesis (no `load_error`, appends re-enabled). This is loud data-destruction by an attacker who already holds full audit-write — the same threat class as the disclosed SCOPE-1 full-forgery residual, and outside R126's scope (which acknowledges *forked/unappendable-until-repaired* and forbids *silent continuation onto a fork*, both of which are correctly enforced). Worth a one-line note in a future audit-integrity task; not in-scope here.
- **G3 — INFORMATIONAL.** BEFORE=1317 not independently re-run (reviewer worktree is git-isolated from the base checkout). Mitigated: AFTER=1356 and delta=+39 both independently reproduced, making 1317 arithmetically consistent, and 1317 matches the M0-T045 G4 figure.

None of G1–G3 require a code change to the producer's deliverable.

## Verdict

All six packet scenarios are covered by concrete, deterministic, independent, mutation-proven-non-vacuous tests; the AS-2 adversarial pair (before/after) and the four R126 conditions are each locked and demonstrably catch a regression; evidence-integrity figures reproduce exactly (58, 233, 1356/2); the diff surface is 11 files all within allowed_paths with no manifest/lockfile/forbidden-path edits, SHADOW-ONLY and config.py untouched, no activation-flag flips; and all three disclosed residuals are accurate and genuinely within the bounded (R129 no-redesign) scope. **No blocking corrections attached.** Gap G1 is an inherent, directive-sequenced pre-activation verification for the orchestrator, not a defect in M0-T046.

**G4 VERDICT: PASS**
