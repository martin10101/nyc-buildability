# M0-T046 producer report — owner am.12 pre-activation hardening

**Producer:** backend-engineer (implementation only; no self-accept, no ledger/git/gh).
**Worktree:** `C:/Users/MLFLL/Downloads/nyc-zoning/orch`  **Branch:** `task/M0-T046-preactivation`.
**Directive:** D-010 source-012 (owner amendment 12), requirements D-010-R124..R129.
**Posture:** evidence only. This report claims no compliance/acceptance; an independent gate decides.

This report records what was implemented, with file:line anchors, executable evidence, the
prohibition confirmation, the owner hand-back, and honest limitations.

---

## Scope delivered (exactly the three the packet names)

### SCOPE 1 (D-010-R124) — park→approve operator-digest binding

**Defect (M0-T045 G5 LOW-1).** `approve_pending_prompt` froze `approved_digest =
digest_of(parked prompt bytes)` by RE-HASHING whatever bytes were parked *at approval time*,
never cross-checked against a value anchored at park. An attacker with journal write who tampered
the `prompt` field between park and approval got the tampered bytes forwarded under a
self-consistent digest; the only barrier was the journal-file ACL.

**Key discovery that shaped the fix.** The parked `digest` is the *instruction-level* S13.5
approval-envelope digest (`approval_digest`, timestamp-free), while the forwarded prompt bytes
carry an ephemeral `FORWARDED AT` timestamp (`build_forwarded_prompt`, codex_reviewer.py:684), so
the forwarded bytes are non-reproducible and need their **own** byte anchor. Changing what the
operator names to a raw byte digest would have broken S13.5's "change only the clock and the
approval does not change" invariant, so the fix keeps the operator naming the approval digest and
adds a park-time byte anchor for the forwarded bytes.

**Change.**
- `tools/agent_supervisor/loop.py:1776` — park now records `prompt_bytes_digest =
  digest_of(forwarded_prompt)`, frozen when the bytes are authentic.
- `tools/agent_supervisor/loop.py:626-681` (`approve_pending_prompt`) — when the record carries
  held bytes, it now REFUSES fail-closed (`pending_prompt_unanchored` / `pending_prompt_tampered`,
  no approval written) unless the parked bytes still hash to the park-time anchor, and binds
  `approved_digest` to that anchor rather than a fresh re-hash.
- `tools/agent_supervisor/cli.py:1704-1728` (`cmd_resume_pending_prompt`) — before any state
  transition or approval audit event, re-verifies the parked bytes against the anchor; on
  mismatch/absence it writes a SEALED (hash-chained) `operator_resume_pending_prompt_refused`
  audit record and returns non-zero with no state change. cli.py:1683-1688 adds an explicit
  blank/malformed `--approve-prompt-digest` refusal (the arg is argparse-`required`, so a MISSING
  one already exits non-zero). cli.py:137-138,120 import wiring.
- The resume-time check `digest_of(prompt) == approved_digest` (loop.py:2005) is retained and now
  anchored to authentic bytes, so a tamper AFTER approval is caught there.

**Executable evidence** — `tools/test_agent_supervisor_park_approve_binding.py` (8 tests, all pass):
- `test_tamper_between_park_and_approval_is_refused` — attacker path (a): CLI refuses, state stays
  WAIT_FOR_OWNER, record not approved, a sealed refusal event is present and the audit chain still
  verifies.
- `test_tamper_after_approval_is_caught_at_resume` — attacker path (b): resume refuses
  `forwarded_prompt_unavailable`, 0 provider calls.
- `test_happy_path_operator_digest_binds_and_forwards` — path (c): forwards byte-identical exactly
  once; `approved_digest` == park-time anchor; record consumed.
- `test_blank_digest_refused`, `test_missing_digest_arg_exits_nonzero` — CLI arg path.
- `ApprovePendingPromptUnitTests` (3) — the binding function fails closed on missing/mismatched
  anchor and binds to the anchor on a match.

Existing fixtures updated in-scope (they parked a prompt with no anchor):
`tools/test_agent_supervisor_pending_prompt.py` two `CliResumeConsumeTests` fixtures now include
`prompt_bytes_digest`. Old-shape (no held bytes) records are unaffected (the loop still refuses to
forward them), so the loop-test suite is untouched.

### SCOPE 2 (D-010-R125/R126) — emergency-stop audit-fork regression lock

**Known behavior (M0-T045 G4 MATERIAL FINDING).** The `emergency-stop` command and the main loop
can write CONCURRENT audit sequence numbers (a fork sharing `prev_digest`); `verify_chain()` fails
`duplicate_sequence`; the recovery surface reports `audit_chain_ok:false`.

**Gap found and fixed.** A probe confirmed that before this change `verify_chain()` reported the
fork **but `append()` still SUCCEEDED on a forked chain** (`load_error` was `None`), violating the
owner's condition "refuses unsafe continuation … unappendable until repaired." Minimal fail-closed
change: `tools/agent_supervisor/audit_log.py:120-153` (`_load_head_from_log`) now detects a
duplicate sequence at open and raises `AuditChainError("duplicate_sequence")`, which `__init__`
records as `load_error`, so `append()` refuses (`append_to_damaged_chain`). `verify_chain()` is
unchanged and still reports the fork; nothing is repaired or hidden. The fork itself (a same-machine
concurrency race) is the owner-accepted condition; only silent continuation onto it is removed.

**Executable evidence** — `tools/test_agent_supervisor_audit_fork_lock.py` (6 tests, all pass),
locking the four acknowledged conditions on a deterministically injected forked-chain shape (no
real-process race):
- (1) `test_1_verify_chain_reports_duplicate_sequence`.
- (2) `test_2_reopen_records_a_load_error_and_append_refuses`.
- (3) `test_3_a_refused_append_neither_repairs_nor_hides_the_fork` (file bytes unchanged; verify
  still reports the fork).
- (4) `test_4_continuation_on_a_forked_chain_is_refused`,
  `test_4_surface_recovery_status_reports_audit_chain_ok_false` (real `recovery-status`/`status`
  CLI report `audit_chain_ok:false`, `status` exits non-zero),
  `test_4_repair_an_explicit_repair_restores_appendability` (only an explicit repair re-enables
  appends — nothing auto-heals).

### SCOPE 3 (D-010-R127/R128) — Windows OS-ACL boundary for the immutable controller config

**(a) New module `tools/agent_supervisor/os_acl.py`** (stdlib only). Fail-closed verdict
(`PROTECTED` / `NOT_PROTECTED` / `UNKNOWN`) for the config FILE and its PARENT directory:
- ACL inspection via `icacls` (subprocess, defensive parse: strips the first-line path prefix,
  splits combined tokens like `(M,DC)`, ignores inherit-only ACEs, classifies
  Administrators/SYSTEM as elevated-only);
- a bounded, NON-DESTRUCTIVE `probe_write_open` that opens O_WRONLY and writes no bytes (safe on a
  protected or an unprotected target; corroborates writability);
- `evaluate_controller_config_acl(config_path)` → combined verdict, `PROTECTED` only when BOTH the
  file and its parent are protected; `is_protected()` is true only for `PROTECTED`.
- Rename/delete/replace/ACL-change protection is assessed from the governing ACL rights (exactly
  what the OS enforces those operations from), NOT a live destructive attempt against the real
  config — a successful rename/delete on a not-yet-protected config would itself damage it, which
  the non-destructive bound forbids ("restore nothing"). Any ambiguity/probe error → `UNKNOWN`
  (never "protected"); non-Windows → `UNKNOWN`.

**(b) Elevated apply/rollback `tools/agent_supervisor/harden_controller_config.ps1`** (PS 5.1).
Refuses to run unelevated; transfers ownership of the file + parent to Administrators; strips
inheritance and grants `Administrators:(F)`, `SYSTEM:(F)`, and the unelevated user `(RX)` ONLY (no
Write/Delete/WriteDAC/WriteOwner/AddFile/DeleteChild); the parent grants the user Read+Execute only
so it cannot add a sibling, delete, rename, or replace the config; idempotent (`icacls /grant:r`
replaces); reversible with `-Rollback`; `-DryRun` prints commands and changes nothing. It never
edits config contents and never weakens the digest gate (config.py untouched).

**(c) Wiring.** `tools/agent_supervisor/cli.py:428-465` (`_controller_config_acl_posture`) +
cli.py:1266,1282 (doctor payload) + cli.py:1245-1249 (printed posture line) + cli.py:137-138
(imports). `doctor --config <path>` reports the verdict as **posture**, fail-closed, and it is NOT
in the pass/fail `checks` list, so shadow mode is not broken before hardening is applied.
Activation gating (a separate future owner act) reads `controller_config_acl.protected`, true only
for a definitive `PROTECTED`. README documented in `tools/agent_supervisor/README.md`.

**Executable evidence** — `tools/test_agent_supervisor_os_acl.py` (25 tests, all pass on this
Windows unelevated producer machine):
- Parser + verdict over ACL FIXTURES: protected/writable file, protected/writable directory,
  `(M,DC)` combined token, inherit-only dangerous ACE ignored, Everyone:(W) → NOT_PROTECTED.
- Fail-closed: icacls error → UNKNOWN, ambiguous output → UNKNOWN, probe error → UNKNOWN, clean
  ACL but writable probe → NOT_PROTECTED, missing file → UNKNOWN, combined `PROTECTED` requires
  both file and parent.
- Live bounded probes (Windows): a writable temp file → NOT_PROTECTED with `write_open_probe:
  writable` and the file byte-unchanged; probe non-destructive; missing-file probe → `error:missing`;
  an inaccessible/ambiguous state → fail-closed UNKNOWN.
- Doctor posture surface: reports NOT_PROTECTED without breaking shadow; no `--config` → SKIPPED
  and never "protected".
- Harden script: exists with the boundary contract; **refuses to run unelevated** (this test RAN
  on the unelevated producer and PASSED — `powershell` exit non-zero with an "elevated" refusal).

---

## Acceptance-scenario evidence map (AS-1..AS-6)

Note/limitation: `project-control/tasks/M0-T046.json` does NOT exist in this worktree (the ledger
task has not been created; that is the orchestrator's action per ADR-005), so the AS-1..AS-6 text
could not be read verbatim. The mapping below is to the packet-described scenarios (the three
scopes' adversarial requirements). If the created task's AS text differs, re-map at gate.

| AS | Scenario (packet-derived) | Executable evidence |
|----|---------------------------|---------------------|
| AS-1 | SCOPE 1 park→approve binding: tamper-before-approval refused, tamper-after caught at resume, happy path, CLI arg | `tools/test_agent_supervisor_park_approve_binding.py` (8) |
| AS-2 | SCOPE 2 audit-fork: the four acknowledged conditions locked | `tools/test_agent_supervisor_audit_fork_lock.py` (6) |
| AS-3 | SCOPE 3 ACL parser/verdict fixtures + fail-closed on ambiguity/error | `tools/test_agent_supervisor_os_acl.py` ParseTests/VerdictLogicTests/FailClosedTests |
| AS-4 | SCOPE 3 bounded live probes at reachable trust levels | `tools/test_agent_supervisor_os_acl.py` LiveProbeTests |
| AS-5 | SCOPE 3 doctor posture surface fail-closed, shadow-safe | `tools/test_agent_supervisor_os_acl.py` DoctorPostureTests |
| AS-6 | SCOPE 3 elevated apply/rollback script refuses unelevated | `tools/test_agent_supervisor_os_acl.py` HardenScriptTests |

---

## Test-suite counts (before / after)

Documented invocation (README): `python -m pytest tools/test_agent_supervisor_*.py`.

- BEFORE (frozen baseline at branch base): **1317 passed, 2 skipped** (213.71s) — matches the
  M0-T045 G4 review figure exactly.
- AFTER (all M0-T046 changes): **1356 passed, 2 skipped** (173.98s).
- Delta: **+39 passed** = 8 (SCOPE 1) + 6 (SCOPE 2) + 25 (SCOPE 3). Zero regressions; zero
  pre-existing failures touched. The 2 skips are the same platform-conditional POSIX guards present
  at baseline (unchanged).

Targeted re-run of all touched modules + new tests: `python -m pytest
tools/test_agent_supervisor_loop.py tools/test_agent_supervisor_pending_prompt.py
tools/test_agent_supervisor_audit.py tools/test_agent_supervisor_recovery.py
tools/test_agent_supervisor_park_approve_binding.py tools/test_agent_supervisor_audit_fork_lock.py
tools/test_agent_supervisor_os_acl.py` → **233 passed**.

---

## R129 prohibition — what I did NOT build (explicit confirmation)

Per D-010-R129 and the packet's hard boundary, I did NOT: create a service, daemon, enterprise
identity system, separate infrastructure project, or broader supervisor redesign; touch
SHADOW-ONLY posture, activation flags, or the forwarding guards; add ANY dependency (stdlib only —
no manifest/lockfile edits); or edit `.claude/`, `apps/`, `services/`, `.github/`, or
`project-control/directives/`. No config CONTENTS were changed and the fail-closed digest/identity
verification in `config.py` is untouched. The OS-ACL work inspects/probes and reports posture only;
it never applies hardening, never attempts elevation, and never repairs.

## Owner touch-back (elevated action the owner must run under UAC)

Applying the OS-ACL hardening requires an elevated owner action; it is intentionally NOT performed
by any agent. From an ELEVATED (UAC) PowerShell:

```
powershell -ExecutionPolicy Bypass -File tools\agent_supervisor\harden_controller_config.ps1 -ConfigPath "<ABSOLUTE PATH TO config.toml>"
```

Reverse (restore the prior writable posture):

```
powershell -ExecutionPolicy Bypass -File tools\agent_supervisor\harden_controller_config.ps1 -ConfigPath "<ABSOLUTE PATH TO config.toml>" -Rollback
```

After apply, verify from an UNELEVATED shell (expect `protected: true`):

```
python -m tools.agent_supervisor doctor --config "<ABSOLUTE PATH TO config.toml>" --json
```

## Limitations / honest disclosures

1. **Live PROTECTED-state proof deferred.** An unelevated process cannot mint an
   Administrators-owned, UAC-required file, so the real `PROTECTED` verdict against the owner's
   config is proven by fixture here and must be confirmed AFTER the owner's elevated apply (the
   orchestrator's step). Every reachable state (writable → NOT_PROTECTED; ambiguous/error →
   UNKNOWN; parser over a hardened fixture → PROTECTED) is proven now.
2. **Parent-container residual.** The script hardens the config file and its IMMEDIATE parent. Full
   protection of the parent against being renamed/deleted depends on the GRANDPARENT's
   DeleteChild; the script documents this and recommends a dedicated config directory. Not built to
   avoid an invasive, unbounded ACL rewrite of unrelated directories (kept within the "no redesign"
   bound).
3. **SCOPE 1 residual (unchanged, pre-existing).** A journal-write attacker who rewrites BOTH the
   `prompt` and its `prompt_bytes_digest` consistently, leaving the approval digest intact, is the
   same full-journal-forgery threat the G5 finding already noted ("same access already forges
   checkpoints/decisions/flags — no new privilege escalation"), and SHADOW-ONLY forwards nothing
   regardless. The fix closes the specific tamper-`prompt`-only window the finding described and
   moves the byte binding from an approval-time re-hash to a park-time anchor.
4. **AS text unavailable** (see the AS map note): `M0-T046.json` is absent from the worktree.
5. **No ledger/git/gh actions taken** (ADR-005): the orchestrator records the transition and
   integrates.

---

## Rework increment (G5 C1 + hardening)

Gate results on the first increment: G3 PASS, G4 PASS (no corrections), G5 PASS with one blocking
correction (C1) plus recommended hardening. Applied exactly the coordinator's list; SCOPE-1 code
(loop.py/cli.py binding) deliberately untouched (G5 C2 is an owner decision at activation time).

**C1 (MANDATORY, G5 M-2 — blocks acceptance).** `os_acl.py` invoked the ACL tools by BARE NAME, so
Windows `CreateProcess` could resolve a planted `icacls.exe`/`powershell.exe` from the
attacker-writable CWD before System32 and spoof a clean parent ACL into a false PROTECTED. Fixed:
`_system32(exe)` (os_acl.py:255-266) resolves `%SystemRoot%\System32\<exe>`; `_run_icacls`
(os_acl.py:269) now calls `_system32("icacls.exe")`; the new owner query uses the absolute
System32 `powershell.exe`. Tests: `AbsoluteToolPathTests.test_run_icacls_uses_absolute_system32_path`
and `test_query_owner_uses_absolute_system32_powershell` (monkeypatch `subprocess.run`, assert
`argv[0]` is the absolute System32 path).

**L-1 (G5, owner check).** A clean DACL is not proof: a non-elevated file/parent OWNER retains
implicit WRITE_DAC/WRITE_OWNER and can re-grant write. Added `_query_owner` (bounded, read-only
`Get-Acl ... .Owner` via absolute-path PowerShell), `_owner_is_elevated`, and
`_confirm_owner_elevated` (os_acl.py:302-360); wired into the PROTECTED path of both `evaluate_file`
(os_acl.py:~430) and `evaluate_directory` (os_acl.py:~455). Elevated owner + clean DACL → PROTECTED;
user owner → NOT_PROTECTED; owner-query error → fail-closed UNKNOWN. Tests:
`OwnerVerdictTests` (3).

**L-2 (G5, script hardening).** `harden_controller_config.ps1` now resolves `icacls`/`takeown` via
absolute `$env:SystemRoot\System32\...` (`$Icacls`/`$Takeown`, script lines 76-82; all `Invoke-Step`
calls updated) — defense-in-depth against a tampered PATH under elevation. PowerShell tokenizer
parse: OK.

**S3-1 (G3, safe-subset inversion).** `os_acl.py` rights gate inverted to an allowlist:
`AceEntry.dangerous_rights` is now `rights - READ_ONLY_RIGHTS` (os_acl.py:111-116), so any
unrecognised/new right token fails TOWARD NOT_PROTECTED. `READ_ONLY_RIGHTS` is now the authoritative
safe subset; `DANGEROUS_RIGHTS` is retained illustratively only. Test:
`VerdictLogicTests.test_unrecognised_token_fails_toward_not_protected` (`(RX,ZZ)` → NOT_PROTECTED).

**S2-1 (G3, non-adjacent duplicate).** Added
`ForkIsReported.test_1_non_adjacent_duplicate_is_also_detected`: an earlier sequence re-appearing
after later records is caught (verify_chain → duplicate_sequence at seq 2, reopened `load_error`,
append refuses). The `_load_head_from_log` `seen`-set spans the whole file, so this already held;
the test locks it.

**README nit (G3 S3).** Fixed the garbled Tests-section sentence to "Three of the Phase-4 tests are
worth explaining:".

**Files changed in this increment:** `tools/agent_supervisor/os_acl.py`,
`tools/agent_supervisor/harden_controller_config.ps1`, `tools/agent_supervisor/README.md`,
`tools/test_agent_supervisor_os_acl.py`, `tools/test_agent_supervisor_audit_fork_lock.py`. No
SCOPE-1/SCOPE-2 production logic changed (SCOPE-2 gained only a test); no other surface widened; no
dependency added; no forbidden path touched.

**Counts after rework:**
- `python -m pytest tools/test_agent_supervisor_os_acl.py tools/test_agent_supervisor_audit_fork_lock.py -q` → **38 passed** (os_acl 31, audit_fork_lock 7).
- FULL suite `python -m pytest tools/test_agent_supervisor_*.py -q` → **1363 passed, 2 skipped**
  (197.27s), up from 1356 pre-rework; +7 new tests (os_acl +6: 2 abs-path, 3 owner, 1 unknown-token;
  audit_fork_lock +1 non-adjacent). Zero regressions; the 2 skips are the same POSIX guards.

**Deviation:** none. All six items (C1, L-1, L-2, S3-1, S2-1, README) applied; SCOPE-1 binding code
untouched per the instruction.
