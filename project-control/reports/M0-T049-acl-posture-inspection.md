# M0-T049 — read-only ACL posture inspection of the relocated config (D-010 R175)

Orchestrator-captured 2026-08-08, immediately after the owner's report that the elevated
relocation succeeded but the hardening script failed PowerShell 5.1 parsing before any ACL
change. Read-only (`icacls` + `Get-Acl` owner read + SHA-256). Nothing modified.

## HONEST POSTURE: relocated, NOT PROTECTED at the file level (measured, not assumed)

**File `C:\Program Files\SupervisorConfig\config.toml` — NOT protected:**

```
NT AUTHORITY\Authenticated Users:(M)
NT AUTHORITY\SYSTEM:(F)
BUILTIN\Administrators:(F)
BUILTIN\Users:(RX)
Owner: LAPTOP-M7D730QA\MLFLL
```

Exactly the owner's predicted mechanism: the same-volume NTFS move preserved the file's OLD
explicit security descriptor (inherited-at-birth from `C:\SupervisorController`, whose
Authenticated Users Modify came from the `C:\` root default). The ACEs are now explicit
(non-inherited) on the file. **Any authenticated user can modify the file contents today**, and
the unelevated owner (`MLFLL`) could rewrite its DACL. The planned hardening (ownership transfer
to Administrators + explicit Admin/SYSTEM-only-write ACLs on file AND parent) closes precisely
this once the repaired script runs.

**Parent `C:\Program Files\SupervisorConfig` — protected (inherited Program Files DACL):**

```
NT SERVICE\TrustedInstaller:(I)(F) (+ CI/IO variants)
NT AUTHORITY\SYSTEM:(I)(F) (+ OI/CI/IO)
BUILTIN\Administrators:(I)(F) (+ OI/CI/IO)
BUILTIN\Users:(I)(RX) (+ OI/CI/IO GR,GE)
CREATOR OWNER:(I)(OI)(CI)(IO)(F)
ALL APPLICATION PACKAGES / ALL RESTRICTED APPLICATION PACKAGES: read/execute only
Owner: BUILTIN\Administrators
```

No unelevated identity can create, delete, rename, or replace entries in the parent (Users =
Read+Execute; no Authenticated Users Modify ACE here). The delete/replace exposure that stopped
the `C:\SupervisorConfig` plan does not exist at this parent.

**Contents integrity:** SHA-256 re-measured at the new location =
`29eb765eabce05b81dcbea33fd4d28800479596e9b23fd4d4fa334f6ee7da1cb` — identical to the recorded
pre-move digest. Nothing activated; SHADOW posture intact; the config-content digest gate in
config.py remains the fail-closed backstop while the file-level ACL is open.

## Interim risk statement (until the repaired script runs elevated)

Threat: any local authenticated process may rewrite `config.toml` contents (file-level Modify).
Mitigations in force: contents digest recorded here and in the directive evidence; supervisor is
SHADOW-ONLY and NOT activated; activation gating reads `controller_config_acl.protected`, which
honestly reports this posture (fail-closed: it would NOT report protected today); the parent
blocks file replacement-by-rename, so a tamper must edit in place (detectable by digest).

## Defect localization (for the M0-T049 packet)

`tools/agent_supervisor/harden_controller_config.ps1` — four affected interpolations:
line 130 `"$UnelevatedUser:(M)"` (rollback /grant), line 132 `"$UnelevatedUser:(M)"` (rollback
/grant, dir), line 154 `"$UnelevatedUser:(RX)"` (apply, file), line 165 `"$UnelevatedUser:(RX)"`
(apply, dir). PowerShell parses `':'` after an interpolated variable as a scope/drive qualifier,
so the whole file fails to PARSE. The prior unelevated-execution test passed because a parse
failure also exits non-zero — indistinguishable from the intended "refuses unelevated" exit; the
new regression test must assert ZERO parse errors via the PowerShell parser API
(`[System.Management.Automation.Language.Parser]::ParseFile` under Windows PowerShell 5.1), not
via exit codes.
