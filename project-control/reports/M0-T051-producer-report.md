# M0-T051 producer report — explicit-ACE strip in `harden_controller_config.ps1`

Owner directive D-010 source-021 (R196–R207). THIRD demonstrated pre-activation
defect. Producer evidence only — no control-plane writes, no git/gh, no
project_control.py.

- Worktree: `C:/Users/MLFLL/Downloads/nyc-zoning/orch`
- Branch: `task/M0-T051-explicit-ace-strip`
- Base HEAD: `33b2e24` (M0-T049 + M0-T050 fixes merged)
- Pre-fix script blob: `9625514e79a34c901258975d4964529a9c02378e` (confirmed = HEAD:tools/agent_supervisor/harden_controller_config.ps1)

## 1. Root cause — explicit vs inherited ACE semantics

The owner's REAL elevated apply "succeeded" yet the immutable config remained
unelevated-writable (unelevated doctor: NOT_PROTECTED, "an unelevated
open-for-write SUCCEEDED"). The surviving ACE was a pre-existing EXPLICIT
`NT AUTHORITY\Authenticated Users:(M)`.

Two icacls facts combine to leave it behind:

- **`/inheritance:r` removes only INHERITED ACEs.** It converts the DACL to a
  protected (non-inheriting) DACL and drops the inherited entries. An ACE that is
  EXPLICIT (not flagged `(I)`) is untouched.
- **`/grant:r <p>:(...)` replaces the grant only for the NAMED principal `p`.** It
  rewrites the ACEs for Administrators, SYSTEM, and `${UnelevatedUser}` — and no
  one else. An explicit ACE for an UNRELATED principal (Authenticated Users) is
  never named, so it survives.

So the old sequence `/inheritance:r` → `/grant:r (three principals)` leaves any
pre-existing explicit ACE for a fourth principal fully effective. `Authenticated
Users:(M)` includes Modify/Write/Delete → the file is unelevated-writable → the
whole hardening is defeated while appearing to succeed.

Empirically reproduced (real icacls, unelevated, on a disposable fixture — see §5):
the OLD sequence yields a 4-ACE DACL still containing `NT AUTHORITY\Authenticated
Users:(M)`; the inherited poison ACEs were stripped by `/inheritance:r` but the
explicit one survived — exactly the mechanism above.

## 2. Chosen mechanism + justification (option (a)) and ordering reasoning

**Chosen: option (a) — `/reset` FIRST, then `/inheritance:r`, then the three
`/grant:r` calls, per target (file and parent).**

`icacls <t> /reset` replaces the DACL with the default inherited ACL: it removes
ALL explicit ACEs and re-enables inheritance. The immediately-following
`/inheritance:r` then removes the re-inherited ACEs too, leaving an EMPTY DACL,
which the three `/grant:r` calls fill deterministically. End state on BOTH file
and parent is exactly:

- file: `Administrators:(F)`, `SYSTEM:(F)`, `${UnelevatedUser}:(RX)` — nothing else
- dir : `Administrators:(OI)(CI)(F)`, `SYSTEM:(OI)(CI)(F)`, `${UnelevatedUser}:(RX)` — nothing else

regardless of any explicit ACE that existed before. This is the smallest correct
change inside the existing icacls path (R207): it adds exactly one flag invocation
(`/reset`) per target ahead of the existing calls; it does NOT redesign the ACL
architecture, add ACL-parsing/enumeration logic, or introduce new principals.

Why not option (b) (enumerate remaining ACEs and `/remove` each non-intended
principal): it requires parsing icacls/Get-Acl output in PowerShell and a
conditional `/remove` loop — more code, more parse/edge-case failure modes, and it
is a "clean up afterwards" pattern rather than a deterministic construction.
Option (a) makes the END STATE independent of the STARTING DACL by construction,
which is the stronger guarantee.

**Ordering trap addressed.** `/reset` and `/inheritance:r` run back-to-back inside
the ONE elevated session. On `/reset` the target briefly re-inherits its parent's
(for the file) or grandparent's (for the dir) — possibly permissive — ACEs, but
the very next line strips inheritance before any window matters, and no unelevated
process can observe the transient state (the script refuses to run unelevated at
all). `/reset` on the directory is NON-recursive (no `/T`), so it rewrites only the
directory's own DACL and never the already-hardened config file inside it. Idempotence
holds because `/reset` re-derives from inheritance and `/inheritance:r` empties it
every run, and `/grant:r` REPLACES the named grants — run twice → identical DACL
(proven in §5).

`${UnelevatedUser}` braces, `$CommandArgs`, the `$file`/`$dir` array shapes,
absolute System32 tool binding, the elevation-refusal ordering, and DryRun gating
through `Invoke-Step` are all unchanged; the new `/reset` calls flow through
`Invoke-Step`, so DryRun prints them like every other command.

**Rollback:** unchanged and NOT broken. The `-Rollback` path re-enables
inheritance (`/inheritance:e`) and grants the user Modify back — this restores the
intended prior "single-account writable" posture and is independent of how apply
CLEARED the DACL. Adding `/reset` to the apply path does not alter rollback's
inputs or outputs. (The known rollback WORDING advisory is deliberately left
bounded-out per the task.)

## 3. Files changed

| File | Change |
|---|---|
| `tools/agent_supervisor/harden_controller_config.ps1` | Apply path §2/§3: add `Invoke-Step $Icacls @($file,"/reset")` and `Invoke-Step $Icacls @($dir,"/reset")` before the existing `/inheritance:r`; expanded root-cause/ordering comments. 8-step apply sequence (2 takeown + 6 icacls). LF preserved (0 CRLF). |
| `tools/test_agent_supervisor_os_acl.py` | `APPLY_VECTORS` extended 6→8 (two `/reset` vectors); A2 (`test_dryrun_replays_all_apply_path_vectors`, renamed from `_six_`) + B1 (`test_apply_path_call_sites_carry_full_argument_arrays`) expected sets updated to include `/reset`; new class `HardenExplicitAceStripTests` (5 tests); added `import hashlib`. |

Both files remain LF-only (byte check: committed 0 CRLF, working 0 CRLF).

## 4. New / updated tests

New class `HardenExplicitAceStripTests` (fixture = disposable temp dir OUTSIDE the
repo; drives the REAL script's apply-path icacls subset extracted from the WinPS
5.1 AST — same technique as M0-T050 — with `$file/$dir/$UnelevatedUser` resolved to
the fixture; takeown asserted PRESENT but not executed, since ownership transfer
needs elevation):

1. `test_adversarial_explicit_ace_is_stripped_file_and_parent` (R199/R200) — poison
   FILE and PARENT with explicit `Authenticated Users:(M)`; assert takeown
   commands present (2, each `/F`+`/A`); assert the 6 DACL-affecting icacls calls
   with `/reset` first; execute them; assert poison GONE, DACL == exactly the three
   intended principals, and `evaluate_acl_entries` == PROTECTED on both file and dir.
2. `test_red_on_current_cleared_blob_leaves_poison_effective` (R205) — same fixture
   through blob 9625514e's sequence (`git show 33b2e24:...`) leaves poison EFFECTIVE
   and the ACE verdict NOT_PROTECTED (old fails property); then the fixed sequence
   removes it (GREEN corroboration on the same file).
3. `test_new_sequence_is_idempotent` (R204) — run new sequence twice; identical
   end-state DACL (file and parent).
4. `test_new_sequence_preserves_file_contents_byte_for_byte` (R202) — sha256 of the
   fixture file identical before/after (icacls/takeown never write content).
5. `test_new_sequence_preserves_unelevated_user_read` (R201) — the unelevated user
   retains exactly one ACE holding RX, and the bytes remain readable.

Updated (M0-T050 full-vector, R188/R195): A2 and B1 now assert the EIGHT apply
vectors including both `/reset` calls, still asserting every path, `/F`, `/A`,
`/reset`, `/inheritance:r`, `/grant:r`, and every ACL principal.

## 5. Counts + evidence

**os_acl file:** baseline 38 → **43 passed** (+5 new; A2/B1 modified in place).

```
python -m pytest tools/test_agent_supervisor_os_acl.py -q
43 passed in 12.22s
```

New class, verbose (none skipped):
```
HardenExplicitAceStripTests::test_adversarial_explicit_ace_is_stripped_file_and_parent PASSED
HardenExplicitAceStripTests::test_new_sequence_is_idempotent PASSED
HardenExplicitAceStripTests::test_new_sequence_preserves_file_contents_byte_for_byte PASSED
HardenExplicitAceStripTests::test_new_sequence_preserves_unelevated_user_read PASSED
HardenExplicitAceStripTests::test_red_on_current_cleared_blob_leaves_poison_effective PASSED
5 passed in 2.65s
```

**FULL supervisor suite:** baseline 1387 passed / 2 skipped → **1392 passed / 2
skipped** (delta = exactly the 5 new tests; no regressions).
```
python -m pytest tools/test_agent_supervisor_*.py -q
1392 passed, 2 skipped in 98.89s
```

**RED-on-9625514e transcript** (standalone proof the new adversarial property is
load-bearing — the three property assertions FAIL against the defective blob):
```
resulting FILE DACL after DEFECTIVE sequence:
...\config.toml LAPTOP-M7D730QA\MLFLL:(RX)
                NT AUTHORITY\SYSTEM:(F)
                BUILTIN\Administrators:(F)
                NT AUTHORITY\Authenticated Users:(M)
principals: {Authenticated Users, SYSTEM, Administrators, LAPTOP-M7D730QA\MLFLL}
ACE verdict: NOT_PROTECTED

=== RED RESULT: adversarial property vs DEFECTIVE blob 9625514e ===
PROPERTY FAILED (required - proves tests are load-bearing):
  - FAIL: poison NOT gone (Authenticated Users:(M) still present)
  - FAIL: DACL not exactly three intended ACEs
  - FAIL: ACE verdict is NOT_PROTECTED, expected PROTECTED
```

**NEW sequence (GREEN)** on the same poison, real icacls:
```
after NEW seq (file): MLFLL:(RX)  SYSTEM:(F)  Administrators:(F)   [Authenticated Users GONE]
after NEW seq (dir):  MLFLL:(RX)  SYSTEM:(OI)(CI)(F)  Administrators:(OI)(CI)(F)   [poison GONE]
POISON SURVIVED (NEW)? False
content hash before==after? True (58b6ac8ccf1506f4 == 58b6ac8ccf1506f4)
idempotent equal? True
```

## 6. Honest unelevated-vs-elevated proof boundary

- **Proven unelevated (fixture, real icacls):** the DACL-level R199 property — after
  the new apply sequence the FILE and PARENT DACLs contain EXACTLY
  Administrators/SYSTEM/`${UnelevatedUser}(RX)`; the pre-existing explicit
  `Authenticated Users:(M)` is GONE; `evaluate_acl_entries` reports no
  unelevated-writable principal (PROTECTED). Idempotence, byte-for-byte content
  preservation, and unelevated read-retention are all proven for real. The takeown
  commands are proven PRESENT in the extracted sequence.
- **Only the owner's real ELEVATED run can prove end-to-end:** (a) `takeown /A`
  actually transferring OWNERSHIP to Administrators (needs elevation) — so
  `evaluate_file`'s owner-elevation check (G5 L-1) and the DENIED open-for-write
  probe pass. Unelevated, the fixture stays user-owned and therefore user-writable,
  so a full `evaluate_file`/`evaluate_controller_config_acl` verdict correctly still
  reads NOT_PROTECTED even though the DACL is exactly the three intended ACEs. This
  is the honest boundary: these tests prove the ACE-level DACL construction (the
  sub-property the defect actually violated); the owner's elevated apply + an
  unelevated doctor re-check remain required to confirm the full PROTECTED verdict
  end-to-end.

## 7. Per-requirement table (R198–R205; R196/R197/R206/R207 orchestrator/owner-lane)

| Req | Requirement | Status | Evidence |
|---|---|---|---|
| R198 | Fix inside existing icacls path, no ACL redesign | MET | `/reset` added to existing apply sequence; no new architecture (§2) |
| R199 | Post-apply FILE+PARENT DACLs contain no non-elevated principal with any write/modify/delete/rename/WriteDAC/WriteOwner right; not merely re-grant the three | MET (DACL-level, unelevated) | adversarial test: poison gone, exactly three ACEs, verdict PROTECTED on both targets (§5); full verdict needs elevated owner (§6) |
| R200 | Adversarial fixture (owner steps 1–5): poison explicit `Authenticated Users:(M)`, drive real behavior | MET | `test_adversarial_...`; real icacls poison + AST-extracted apply subset |
| R201 | Preserve unelevated user READ | MET | `test_new_sequence_preserves_unelevated_user_read` (RX retained, bytes readable) |
| R202 | Preserve contents byte-for-byte | MET | `test_new_sequence_preserves_file_contents_byte_for_byte` (sha256 equal) |
| R203 | Preserve parent protections | MET | parent asserted to exactly three ACEs, verdict PROTECTED (adversarial + idempotence tests) |
| R204 | Idempotent (run twice → same end state) | MET | `test_new_sequence_is_idempotent` (file+dir DACL identical) |
| R205 | RED on the current cleared blob 9625514e | MET | `test_red_on_current_...` + standalone RED transcript (§5); old sequence leaves poison NOT_PROTECTED |

## Deviations / uncertainty / limitations

- Full `evaluate_file` PROTECTED verdict is NOT provable unelevated (owner cannot be
  set to Administrators without elevation; the user-owned fixture stays writable).
  Documented as the honest boundary (§6); the DACL-construction sub-property that
  the defect violated IS proven. This is the same class of boundary the existing
  M0-T046/T050 tests already declare.
- New DACL tests are Windows+PowerShell-gated (`@unittest.skipUnless`); on this
  machine they RAN (not skipped) — confirmed by the verbose run (§5). On a
  non-Windows CI they would skip, matching the pre-existing HardenScript test
  posture.
- The `-Rollback` path was intentionally NOT modified (mechanism does not break it,
  §2); the rollback WORDING advisory remains bounded out per the task.
- Files kept LF-only to match the committed blobs (git autocrlf warning is about
  checkout behavior, not stored content; byte check confirms 0 CRLF in both).
