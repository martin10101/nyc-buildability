<#
.SYNOPSIS
  M0-T046 SCOPE 3 (D-010-R127/R128): harden the immutable controller config so the
  ordinary UNELEVATED supervisor process may READ it but cannot modify, overwrite,
  delete, rename, replace, or change ACLs on it. Modification then requires an
  elevated owner action (this script, run via UAC).

.DESCRIPTION
  Owner decision (source-012-amendment.md): the current single-account writable ACL
  is NOT sufficient for supervised-auto activation. This script:

    * transfers ownership of the config FILE and its PARENT directory to the
      Administrators group;
    * removes inheritance and sets EXPLICIT ACLs granting:
        - BUILTIN\Administrators : Full control (elevated only)
        - NT AUTHORITY\SYSTEM     : Full control (service context)
        - <UnelevatedUser>        : Read + Execute ONLY
          (no Write / Delete / WriteDAC / WriteOwner / AddFile / DeleteChild)
    * on the parent directory, the unelevated user gets Read+Execute only, so it
      cannot add a sibling, delete, rename, or replace the config file (the
      DeleteChild / AddFile rights are withheld), which blocks the replace-in-place
      and drop-a-sibling bypasses;
    * retains the fail-closed digest/identity verification in config.py (untouched).

  It is IDEMPOTENT (re-running yields the same ACL state), REVERSIBLE (-Rollback
  restores inheritance and grants the user Modify back), and REFUSES to run
  unelevated. It NEVER edits the config CONTENTS and never weakens the digest gate.

  Verify the result from an unelevated process with:
     python -m tools.agent_supervisor.cli doctor --config <ConfigPath> --json
  and read `controller_config_acl.protected` (must be true), OR directly:
     python -c "from tools.agent_supervisor import os_acl, json; \
       print(json.dumps(os_acl.evaluate_controller_config_acl(r'<ConfigPath>').to_dict(), indent=2))"

.PARAMETER ConfigPath
  Absolute path to the immutable controller config file (e.g. config.toml).

.PARAMETER UnelevatedUser
  The account granted Read+Execute. Defaults to the interactive owner account
  ("$env:USERDOMAIN\$env:USERNAME"). This must be the account the ordinary
  (unelevated) supervisor runs as.

.PARAMETER Rollback
  Restore the prior posture: re-enable inheritance and grant the user Modify.

.PARAMETER DryRun
  Print the exact icacls/takeown commands that WOULD run, and change nothing.

.EXAMPLE
  # Run from an ELEVATED PowerShell (UAC):
  powershell -ExecutionPolicy Bypass -File harden_controller_config.ps1 `
    -ConfigPath "C:\controller\config.toml"

.EXAMPLE
  # Reverse it:
  powershell -ExecutionPolicy Bypass -File harden_controller_config.ps1 `
    -ConfigPath "C:\controller\config.toml" -Rollback

.NOTES
  PowerShell 5.1 compatible. Windows only.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ConfigPath,

    [string]$UnelevatedUser = "$env:USERDOMAIN\$env:USERNAME",

    [switch]$Rollback,

    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# G5 L-2: resolve the trusted tools by ABSOLUTE System32 path. Invoking `icacls`/
# `takeown` by bare name would let CreateProcess resolve them through the CWD (or a
# tampered PATH) before System32 - a hijack vector even under elevation. Bind them
# to System32 explicitly.
$System32 = Join-Path $env:SystemRoot "System32"
$Icacls = Join-Path $System32 "icacls.exe"
$Takeown = Join-Path $System32 "takeown.exe"

function Test-IsElevated {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Invoke-Step {
    param([string]$Exe, [string[]]$Args)
    $shown = "$Exe " + ($Args -join " ")
    if ($DryRun) {
        Write-Host "[dry-run] $shown"
        return
    }
    Write-Host "[run] $shown"
    & $Exe @Args
    if ($LASTEXITCODE -ne 0) {
        throw "command failed (exit $LASTEXITCODE): $shown"
    }
}

# --- refuse to run unelevated ------------------------------------------------
if (-not (Test-IsElevated)) {
    Write-Error ("refusing to run: this script MUST run elevated (UAC). It transfers " +
        "ownership and rewrites ACLs, which requires administrative rights. Re-launch " +
        "an elevated PowerShell and run it again.")
    exit 2
}

if (-not (Test-Path -LiteralPath $ConfigPath)) {
    Write-Error "config file not found: $ConfigPath"
    exit 3
}

$fileItem = Get-Item -LiteralPath $ConfigPath
$file = $fileItem.FullName
$dir = $fileItem.DirectoryName

Write-Host "controller config : $file"
Write-Host "parent directory  : $dir"
Write-Host "unelevated user   : $UnelevatedUser"
Write-Host ""

if ($Rollback) {
    Write-Host "=== ROLLBACK: restoring inheritance + user Modify ==="
    # Re-enable inheritance and give the user Modify back on both objects.
    Invoke-Step $Icacls @($file, "/inheritance:e")
    Invoke-Step $Icacls @($file, "/grant", "${UnelevatedUser}:(M)")
    Invoke-Step $Icacls @($dir, "/inheritance:e")
    Invoke-Step $Icacls @($dir, "/grant", "${UnelevatedUser}:(M)")
    Write-Host ""
    Write-Host "=== resulting ACLs ==="
    Invoke-Step $Icacls @($file)
    Invoke-Step $Icacls @($dir)
    Write-Host ""
    Write-Host "rollback complete: the prior single-account-writable posture is restored."
    exit 0
}

Write-Host "=== APPLY: Administrators owns; unelevated user READ+EXECUTE only ==="

# 1) Ownership -> Administrators group (/A) for both the file and its parent.
Invoke-Step $Takeown @("/F", $file, "/A")
Invoke-Step $Takeown @("/F", $dir, "/A")

# 2) File: strip inheritance, then explicit ACL. /grant:r REPLACES any existing
#    grant for the principal, so re-running is idempotent.
Invoke-Step $Icacls @($file, "/inheritance:r")
Invoke-Step $Icacls @($file, "/grant:r",
    "BUILTIN\Administrators:(F)",
    "NT AUTHORITY\SYSTEM:(F)",
    "${UnelevatedUser}:(RX)")

# 3) Parent directory: strip inheritance, then explicit ACL. The unelevated user
#    gets Read+Execute only (no AddFile / DeleteChild / Write / WriteDAC /
#    WriteOwner), which blocks delete/rename/replace of the config and dropping a
#    sibling to bypass. Administrators/SYSTEM keep full control with (OI)(CI) so
#    future contents inherit their control, not the user's.
Invoke-Step $Icacls @($dir, "/inheritance:r")
Invoke-Step $Icacls @($dir, "/grant:r",
    "BUILTIN\Administrators:(OI)(CI)(F)",
    "NT AUTHORITY\SYSTEM:(OI)(CI)(F)",
    "${UnelevatedUser}:(RX)")

Write-Host ""
Write-Host "=== resulting ACLs (verify the unelevated user shows only (RX)) ==="
Invoke-Step $Icacls @($file)
Invoke-Step $Icacls @($dir)

Write-Host ""
Write-Host ("apply complete. Verify from an UNELEVATED shell that the OS-ACL verdict is " +
    "PROTECTED (doctor --config, or os_acl.evaluate_controller_config_acl). NOTE: this " +
    "hardens the config file and its IMMEDIATE parent; if the parent is a SHARED " +
    "directory, place the controller config in a DEDICATED directory so removing " +
    "inheritance does not affect unrelated files, and consider hardening the " +
    "grandparent's DeleteChild for the parent to block renaming the parent itself.")
exit 0
