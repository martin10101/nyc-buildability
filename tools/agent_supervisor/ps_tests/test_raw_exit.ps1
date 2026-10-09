# test_raw_exit.ps1 - the harness preserves the raw child exit code (D-024-R586).
. (Join-Path $PSScriptRoot 'harness.ps1')

$failures = 0
function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) {
        Write-Output "ASSERT-FAIL: $Message"
        $script:failures = $script:failures + 1
    }
}

# 1. Raw nonzero code preserved exactly (7 stays 7, never collapsed to 1/0).
$r = Invoke-RawExit -FilePath python -ArgumentList @('-c', 'import sys; sys.exit(7)')
Assert-True ($r.exit_code -eq 7) "expected raw exit 7, got '$($r.exit_code)'"
Assert-True (-not $r.ok) 'exit 7 must not be ok'
Assert-True ($r.reason -eq 'raw_lastexitcode') "reason was '$($r.reason)'"

# 2. Success is exit 0, from the same unpiped read.
$r0 = Invoke-RawExit -FilePath python -ArgumentList @('-c', 'import sys; sys.exit(0)')
Assert-True ($r0.exit_code -eq 0) "expected raw exit 0, got '$($r0.exit_code)'"
Assert-True ($r0.ok) 'exit 0 must be ok'

# 3. A command that never launches FAILS CLOSED: $LASTEXITCODE stays $null
#    (CommandNotFoundException leaves it unchanged; the harness reset it).
$rx = Invoke-RawExit -FilePath 'no-such-executable-m0t136-xyzzy' -ArgumentList @()
Assert-True ($null -eq $rx.exit_code) "not-found exit_code was '$($rx.exit_code)'"
Assert-True (-not $rx.ok) 'a command with no exit code must never be ok'
Assert-True ($rx.reason -eq 'no_exit_code_fail_closed') "reason was '$($rx.reason)'"

# 4. The JSON record reproduces the verdict (a durable record, not a claim).
$record = Join-Path $env:TEMP 'm0t136_ps_raw_exit_record.json'
$null = Invoke-RawExit -FilePath python -ArgumentList @('-c', 'import sys; sys.exit(7)') -RecordPath $record
$doc = Get-Content -Path $record -Raw | ConvertFrom-Json
Assert-True ($doc.exit_code -eq 7) "JSON record exit_code was '$($doc.exit_code)'"
Assert-True ($doc.ok -eq $false) 'JSON record ok must be false for exit 7'
Remove-Item -Path $record -ErrorAction SilentlyContinue

# 5. Captured stdout/stderr land in the named files, and the raw code (5) rides
#    along. The payload uses doubled SINGLE quotes: PowerShell 5.1 native-arg
#    quoting mangles embedded double quotes (measured; a mangled payload made
#    python fail with exit 1 and an empty stdout).
$out = Join-Path $env:TEMP 'm0t136_ps_raw_exit_out.txt'
$err = Join-Path $env:TEMP 'm0t136_ps_raw_exit_err.txt'
$r5 = Invoke-RawExit -FilePath python `
    -ArgumentList @('-c', 'import sys; sys.stdout.write(''OUT-MARK''); sys.stderr.write(''ERR-MARK''); sys.exit(5)') `
    -StdoutPath $out -StderrPath $err
Assert-True ($r5.exit_code -eq 5) "expected raw exit 5, got '$($r5.exit_code)'"
Assert-True (([string](Get-Content -Path $out -Raw)) -like '*OUT-MARK*') 'stdout capture missing OUT-MARK'
Assert-True (([string](Get-Content -Path $err -Raw)) -like '*ERR-MARK*') 'stderr capture missing ERR-MARK'
Remove-Item -Path $out, $err -ErrorAction SilentlyContinue

if ($failures -gt 0) {
    Write-Output "test_raw_exit: $failures assertion failure(s)"
    exit 1
}
Write-Output 'test_raw_exit: all assertions passed'
exit 0
