# G3 CODE REVIEW — M0-T046 (owner am.12 pre-activation hardening)

**Gate:** G3 (correctness / maintainability / contracts / errors / tests)
**Reviewer:** code-reviewer (read-only, independent; producer = backend-engineer)
**Date:** 2026-08-07

## Reviewed identity (confirmed with `git rev-parse`)

| Item | Expected | Confirmed |
|---|---|---|
| Worktree code head (`orch`, `task/M0-T046-preactivation`) | `569d1a7bc2447b6884753b813de431a1def365a8` | **MATCH** |
| Base (origin/main) | `ae627e5` | MATCH (`git diff ae627e5..569d1a7`) |
| Control-plane checkout (`control/M0-T046-preactivation`) | `77a5eef` | **Advanced to `0431377d`** — `77a5eef` is its parent (verified `git merge-base --is-ancestor 77a5eef HEAD` → YES). The extra commit `0431377` is the control-plane "submitted awaiting_gate; G2 PASS recorded" state update; it does **not** change the reviewed code identity. No impact. |

Diff surface: 11 files, `+1949 / -11` — 4 supervisor modules (loop.py, cli.py, audit_log.py, +new os_acl.py), README.md, new harden_controller_config.ps1, 4 test files, producer report. `git diff --name-status` confirms all 11 are inside `allowed_paths`; **no** `.claude/`, `apps/`, `services/`, `.github/`, `directives/`, `config.py`, manifest/lockfile, or activation-surface path is touched.

## Reproduction (sandbox executed)

- `python -m pytest tools/test_agent_supervisor_park_approve_binding.py tools/test_agent_supervisor_audit_fork_lock.py tools/test_agent_supervisor_os_acl.py -q` → **39 passed in 2.97s**.
- Touched pre-existing modules `python -m pytest tools/test_agent_supervisor_pending_prompt.py tools/test_agent_supervisor_audit.py tools/test_agent_supervisor_loop.py tools/test_agent_supervisor_recovery.py -q` → **194 passed** (no regressions).
- Full suite (1356 passed / 2 skipped) treated as orchestrator-captured evidence per instruction; consistent with the two runs above.

---

## SCOPE 1 (R124) — park→approve operator-digest binding

**Correctness of the digest flow (verified end-to-end):**
- Park (`loop.py:1776`) freezes `prompt_bytes_digest = digest_of(forwarded_prompt)` alongside the parked `prompt` and the S13.5 timestamp-free `digest`.
- `approve_pending_prompt` (`loop.py:660-681`) refuses fail-closed (`pending_prompt_unanchored` when no anchor; `pending_prompt_tampered` when `digest_of(prompt) != anchor`) and binds `approved_digest = anchor`, never a fresh re-hash. Distinct, honest reason codes. ✓
- CLI pre-transition check (`cli.py:1704-1723`) re-verifies the anchor **before** any transition/audit; on mismatch/absence it writes a SEALED `operator_resume_pending_prompt_refused` event and returns 1 with no state change. Blank digest refused (`cli.py:1683-1687`); missing arg is argparse-`required`. ✓
- Resume-time check retained and **strengthened**, not weakened: `loop.py:2042` (`digest_of(prompt) != approved_digest`) is the pre-existing M0-T045 line; `approved_digest` is now bound to authentic park-time bytes, so a post-approval tamper is caught here. ✓
- **Old-shape / anchor-less records refuse rather than bypass:** a record carrying `prompt` bytes but no `prompt_bytes_digest` is refused at `cli.py:1707`; a record with no held bytes yields no `approved_digest` and the loop refuses to forward (`loop.py:2036-2041`, unchanged). ✓
- No path forwards parked bytes that fail the anchor — three checkpoints (CLI pre-check, `approve_pending_prompt`, resume `loop.py:2042`), all anchored to the same authentic-byte digest.

**Tests (8):** drive the REAL loop→CLI→loop with durable-journal tampering. `test_tamper_between_park_and_approval_is_refused` (no approval, sealed refusal, chain still verifies), `test_tamper_after_approval_is_caught_at_resume` (0 provider calls), `test_happy_path_...` (forwards byte-identical exactly once; `approved_digest == anchor`; consumed), blank/missing-digest, and 3 direct-function unit tests. They test what they claim. Fixture updates in `test_agent_supervisor_pending_prompt.py` (add `prompt_bytes_digest` to two `CliResumeConsumeTests` fixtures) are in-scope and are the minimal change to keep old tests valid under the new required-anchor behavior. ✓

**FINDING S1-1 (MAJOR — route to DCV/owner, not a G3 code change):** The implementation diverges from the **literal** packet AS-1 / directive R124 wording. AS-1 requires the operator digest be "verifie[d]…against `digest_of(parked prompt bytes)`" and `approved_digest` bound "to the OPERATOR-NAMED value." In the code the operator names the **S13.5 approval-envelope digest** (matched `supplied == recorded`), while forwarded-byte integrity is bound to a **system-computed park-time anchor** (`prompt_bytes_digest`). The producer's rationale is sound and disclosed (the forwarded bytes carry an ephemeral `FORWARDED AT` stamp, so their digest is non-reproducible and cannot be the operator-named S13.5 digest without breaking the "change only the clock and the approval does not change" invariant). The **security objective of G5 LOW-1 is met** — the tamper-`prompt`-only window between park and approval is closed, tests prove it — so from the G3 correctness lane the code is correct and arguably superior (it preserves both S13.5 and the anti-tamper intent). **But R124 is an owner-directive requirement, and its literal "bind to the OPERATOR-NAMED approval digest" clause is not implemented as written.** This must be explicitly adjudicated by the directive-compliance-verifier (and, if the DCV cannot resolve the wording, the owner) before acceptance. The G2 self-check already flags this as an open gate question; it is not a code defect for the producer to "fix." **Acceptance is contingent on the DCV R124 ruling.**

**FINDING S1-2 (INFO):** Producer residual 3 (a full-journal-forgery attacker who rewrites `prompt` + `prompt_bytes_digest` consistently) is untouched — but this is the pre-existing threat the original G5 finding explicitly scoped out, and SHADOW-ONLY forwards nothing. No new exposure. (Security-lane concern; noted for G5.)

---

## SCOPE 2 (R125/R126) — emergency-stop audit-fork regression lock

**Correctness of `_load_head_from_log` (audit_log.py:120-153):** a `seen: set[int]` catches **any** duplicate integer `sequence` regardless of adjacency (so non-adjacent fork shapes are also caught), and raises `AuditChainError("duplicate_sequence")` at open, which `__init__` records as `load_error`, making `append()` refuse (`append_to_damaged_chain`). No false positives on legitimate chains (sequences are strictly increasing/unique by construction; the full suite's many audit tests still pass). Non-int sequences are skipped (unchanged behavior). ✓

**`verify_chain` genuinely unchanged and independent:** it reads via `read_all()`/`_iter_raw()`, NOT `_load_head_from_log`, so it still reports the fork even when the constructor set `load_error` (confirmed by diff — only the `_load_head_from_log` hunk changed). The status surfaces are correctly wired: `status` (`cli.py:1336`, exits non-zero at 1356) and `recovery-status` (`cli.py:1840`) both report `audit_chain_ok` from `verify_chain().ok`. ✓

**Tests (6):** deterministically inject the observed seq-duplicate/shared-`prev_digest` shape (no real-process race — the sanctioned approach per packet risk note). They lock the four owner-acknowledged conditions 1:1: (1) `verify_chain` reports `duplicate_sequence`; (2) `load_error` + append refused; (3) file bytes unchanged + verify still reports (no silent repair/hide); (4) continuation refused, `audit_chain_ok:false` + `status` non-zero on the real CLI, and only an **explicit** repair restores appendability. ✓

**FINDING S2-1 (INFO):** The test fixture exercises an *adjacent* duplicate only; the set-based implementation also handles a non-adjacent duplicate, but that shape is not explicitly asserted. Optional coverage add; not blocking.

**AS-3 conformance:** Satisfied against the PACKET text. Note the producer's evidence-map LABELS AS-3 as the ACL fixtures — the G2 self-check already flagged this mislabeling; against the packet, AS-3 (audit fork) evidence is `test_agent_supervisor_audit_fork_lock.py` and it exists and passes.

---

## SCOPE 3 (R127/R128) — Windows OS-ACL boundary

**os_acl.py — parse robustness & fail-closed verdict (verified):**
- `parse_icacls` strips the first-line path prefix, splits combined tokens `(M,DC)` via `_split_tokens`, ignores inherit-only ACEs (`IO`), and returns an *error* when no ACE parses (→ caller UNKNOWN). Any principal-parse confusion errs toward an **unrecognized principal → treated as non-elevated → NOT_PROTECTED** (fail-closed direction), so a false PROTECTED is hard to reach. ✓
- Verdict: `NOT_PROTECTED` if any non-elevated principal holds a dangerous right; `evaluate_file` requires probe `denied` **AND** clean ACL for PROTECTED, and a `writable` probe overrides a clean-looking ACL (bypass detection). `evaluate_controller_config_acl` is PROTECTED only when **both** file and parent are PROTECTED; `_combine` returns UNKNOWN unless the other side is the stronger NOT_PROTECTED. `is_protected()`/`protected` true only for PROTECTED. ✓ Treating BUILTIN\Administrators / SYSTEM as elevated-only is **correct** for UAC-filtered tokens (Administrators is deny-only in the unelevated token, so it cannot grant access).
- Probe `probe_write_open` is bounded and non-destructive: `os.open(O_WRONLY)` with no `O_TRUNC` and no `write()`, then close — content/mtime unchanged whether or not it succeeds; distinct `denied` / `writable` / `error:*` results; directory is ACL-only (no probe). No elevation, no destructive fallback anywhere. ✓
- Stdlib only (dataclasses/os/pathlib/re/subprocess/sys/typing); `subprocess.run` list-form, no shell — no injection. ✓

**cli.py doctor wiring:** `controller_config_acl` is reported as **posture**, fail-closed (SKIPPED/exception/UNKNOWN → `protected:False`), and is deliberately NOT in the pass/fail `checks` list, so shadow-mode `ok` is unaffected. ✓

**harden_controller_config.ps1 (PS 5.1):** `[CmdletBinding()]`, `WindowsPrincipal.IsInRole(Administrator)` elevation check that refuses unelevated (exit 2) before any step; `takeown /A` → Administrators; `/inheritance:r` + `/grant:r` (replace → idempotent) granting Admins/SYSTEM `(F)` and the user `(RX)` only on file and parent (no AddFile/DeleteChild/Write/WriteDAC/WriteOwner); `-Rollback` restores inheritance + user Modify; `-DryRun` prints only; never edits config contents; config.py digest gate untouched. All PS 5.1-compatible constructs. ✓

**Tests (25):** parser/verdict fixtures (protected/writable file+dir, `(M,DC)`, inherit-only-ignored, Everyone:(W)); fail-closed (icacls error, ambiguous output, probe error, missing file, combined-requires-both); live bounded probes (writable→NOT_PROTECTED with file byte-unchanged, missing→`error:missing`, ambiguous→UNKNOWN); doctor posture (NOT_PROTECTED without breaking shadow; no-config→SKIPPED); harden script exists + declares the boundary + refuses unelevated. They test what they claim. ✓

**FINDING S3-1 (MINOR — flag to G5 security lane):** The dangerous-rights check is an **allowlist of known dangerous tokens** (`rights & DANGEROUS_RIGHTS`); an icacls right token that is neither in `DANGEROUS_RIGHTS` nor `READ_ONLY_RIGHTS` (e.g. exotic `MA`) is silently treated as non-dangerous, so in principle a non-elevated principal holding *only* an unknown-but-writable token could yield a false PROTECTED. The `DANGEROUS_RIGHTS` set is comprehensive for real modify/write/delete/ownership codes and the fixtures/harden-script use only recognized tokens, so this is a narrow theoretical gap. For a security boundary the owner explicitly demanded fail-closed, consider inverting to a **subset-of-known-safe** rule (any non-inheritance token not in `READ_ONLY_RIGHTS` counts as dangerous). Non-blocking; recommend the G5 reviewer weigh it.

**FINDING S3-2 (MINOR/INFO):** `ELEVATED_PRINCIPALS` is English-name-only. On a non-English Windows locale or when icacls renders SIDs (`*S-1-5-32-544`), Administrators/SYSTEM would be classed non-elevated → NOT_PROTECTED (fail-closed, safe), but a definitive PROTECTED could be **unreachable** on such systems. Safe direction; worth a documented caveat. (Owner machine is presumably English Windows.)

**FINDING S3-3 (INFO):** `-Rollback` restores inheritance + user Modify but does not restore original file *ownership* (leaves Administrators as owner). The user regains write, so the "prior writable posture" is functionally restored; ownership residual is cosmetic. Also `-DryRun` still requires elevation (the elevation check runs first) — minor usability only.

**AS-4 (deferred live proof — NOT a defect):** The live PROTECTED-state proof against the real config is necessarily deferred to the owner's elevated (UAC) apply — an unelevated agent cannot mint an Administrators-owned file, which is a *correct consequence of the R128 boundary itself*. Every unelevated-reachable state (writable→NOT_PROTECTED, ambiguous/error→UNKNOWN, hardened-fixture→PROTECTED) is proven now. **Required follow-up (post-acceptance, consistent with R132 sequencing):** the orchestrator must capture `doctor --config <path> --json` showing `controller_config_acl.protected == true` after the owner runs the script, to close AS-4's live end-to-end leg.

---

## Per-AS conformance (against the verbatim PACKET text)

| AS | Verdict | Basis |
|---|---|---|
| **AS-1** (R124) | **Conditional** | Security effect met + tests pass; **literal "bind to OPERATOR-NAMED digest" not implemented as written** — see S1-1; gated on DCV R124 ruling. |
| **AS-2** (R124 adversarial) | **PASS** | tamper-before → refused fail-closed (sealed refusal, no approval); tamper-after → caught at resume (`forwarded_prompt_unavailable`, 0 provider calls). Executable. |
| **AS-3** (R125/R126) | **PASS** | 6 tests lock all four owner-acknowledged conditions on the deterministically injected fork; `verify_chain` unchanged; `audit_chain_ok:false` + non-zero status wired. (Producer mislabels this in its map — packet evidence exists.) |
| **AS-4** (R127/R128) | **PASS (live leg deferred)** | Read preserved; modify/delete/rename/replace/re-ACL denied via Admin ownership + user-RX; parent bypass blocked; UAC-gated apply; digest gate retained. Live PROTECTED proof deferred to owner elevated apply (correct per boundary) — orchestrator follow-up required. |
| **AS-5** (R128 ambiguity) | **PASS** | Every ambiguity/error → UNKNOWN, never protected; probes bounded, no elevation, no destructive fallback. |
| **AS-6** (R123/R129 prohibition) | **PASS** | Diff = 11 files, all in allowed_paths; stdlib only; no service/daemon/identity-system/redesign; SHADOW/activation untouched (doctor posture is not a pass/fail check); no config.py/manifest edits. |

## Blocking-for-acceptance conditions (stated unambiguously)

1. **[Route to directive-compliance-verifier / owner]** Explicitly adjudicate whether the R124/AS-1 design adaptation (operator names the S13.5 approval-envelope digest; forwarded-byte integrity bound to a system-computed park-time anchor rather than the operator-named value) satisfies R124's literal "bind the forwarded prompt bytes to the OPERATOR-NAMED approval digest at approval time." G3 finds the code correct and the LOW-1 window closed, but the literal directive wording is not met; acceptance must not proceed until DCV rules. **This is not a producer code correction** — do not send to rework on G3's account.
2. **[Orchestrator follow-up, post-apply]** Capture the live AS-4 PROTECTED proof (`doctor --config … --json` showing `controller_config_acl.protected == true`) after the owner's elevated `harden_controller_config.ps1` run.

Non-blocking recommendations: S3-1 (invert ACL check to subset-of-known-safe; flag for G5), S3-2 (document locale/SID caveat), S2-1 (non-adjacent-duplicate test), plus a cosmetic README nit — the edited Tests section produces a slightly garbled sentence "The Phase-4 set. Three of the earlier ones are worth explaining:".

## Verdict rationale

Within the G3 lane (correctness, maintainability, contracts, error paths, tests) the change is correct, well-tested (39 new + 194 touched, reproduced green), fully fail-closed, honestly documented, and strictly confined to the three authorized scopes and allowed paths. No BLOCKING **code** defect was found. The one material contract question (AS-1/R124 literal wording) is an owner-directive interpretation that belongs to the DCV gate, and the AS-4 live proof is a correctly-deferred owner action — both are called out as acceptance gates rather than G3 rework.

**G3 VERDICT: PASS**

(PASS carries the two acceptance-gating conditions above — condition 1 is BLOCKING for acceptance and must be resolved by the directive-compliance-verifier/owner, not by producer rework; condition 2 is a required post-apply orchestrator follow-up.)
