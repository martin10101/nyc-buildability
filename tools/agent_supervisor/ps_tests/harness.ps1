# harness.ps1 - raw-exit-code invocation harness (M0-T136 C-B5; D-024-R586, R589).
#
# The operator launch path lives on real PowerShell 5.1, where the ONLY honest
# carrier of a native command's exit code is $LASTEXITCODE read IMMEDIATELY
# after an UNPIPED call-operator invocation. Measured facts this harness is
# built on (proven by test_mutants_detected.ps1 against mutants/):
#   - "& python ..." sets $LASTEXITCODE to the raw child exit code;
#   - "| Tee-Object" keeps $LASTEXITCODE but flips $? - and a -File script
#     ending in a pipeline WITHOUT an explicit exit reports 0 to its caller;
#   - a CommandNotFoundException leaves $LASTEXITCODE UNCHANGED, so the
#     harness resets it to $null first and FAILS CLOSED when it stays $null;
#   - "cmd /c" piping replaces the code with the LAST pipe stage's code.
#
# Dot-source this file, then call Invoke-RawExit. Never pipe the invocation,
# never judge success by $?, and always end runner scripts with an explicit
# exit statement.

function Invoke-RawExit {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [string[]]$ArgumentList = @(),
        [string]$StdoutPath = '',
        [string]$StderrPath = '',
        [string]$RecordPath = ''
    )
    if ($StdoutPath -eq '') { $StdoutPath = [System.IO.Path]::GetTempFileName() }
    if ($StderrPath -eq '') { $StderrPath = [System.IO.Path]::GetTempFileName() }
    # Reset so a command that never launches (CommandNotFoundException) cannot
    # inherit a previous command's code and report it as its own.
    $global:LASTEXITCODE = $null
    $invocationError = ''
    try {
        # Unpiped call operator; stdout/stderr go to files (redirection is not a
        # pipeline and does not disturb $LASTEXITCODE).
        & $FilePath @ArgumentList 1>$StdoutPath 2>$StderrPath
    } catch {
        $invocationError = $_.Exception.Message
    }
    $raw = $global:LASTEXITCODE
    if ($null -eq $raw) {
        # Fail closed: no exit code observed means NO verdict, never success.
        $result = [pscustomobject]@{
            file      = $FilePath
            args      = @($ArgumentList)
            exit_code = $null
            ok        = $false
            reason    = 'no_exit_code_fail_closed'
            error     = $invocationError
            stdout    = $StdoutPath
            stderr    = $StderrPath
        }
    } else {
        $result = [pscustomobject]@{
            file      = $FilePath
            args      = @($ArgumentList)
            exit_code = [int]$raw
            ok        = ([int]$raw -eq 0)
            reason    = 'raw_lastexitcode'
            error     = $invocationError
            stdout    = $StdoutPath
            stderr    = $StderrPath
        }
    }
    if ($RecordPath -ne '') {
        $result | ConvertTo-Json -Depth 4 | Out-File -FilePath $RecordPath -Encoding ascii
    }
    return $result
}
