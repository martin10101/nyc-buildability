# test_junction_containment.ps1 - reparse-point and containment teeth (M0-T139;
# D-024-R628/R634/R635): a relevant junction anywhere in a source tree, the
# backup-root chain, or the mirror destination is a hard stop, and paths that
# escape their approved root refuse before any copy.
. (Join-Path $PSScriptRoot 'fixtures.ps1')

$script:failures = 0
$scriptPath = Join-Path (Split-Path $PSScriptRoot -Parent) 'update_controller_from_candidate.ps1'
$work = New-FixtureWork
$fix = New-FixtureRepo -Root $work

function Assert-True {
    param([bool]$Condition, [string]$Label)
    if ($Condition) {
        Write-Output ("PASS " + $Label)
    } else {
        Write-Output ("ASSERT-FAIL " + $Label)
        $script:failures = $script:failures + 1
    }
}

function Assert-Refused {
    param([hashtable]$Result, [string]$Code, [string]$Label)
    $refused = ($Result.exit_code -ne 0) -and ($Result.stdout -match ('REFUSED ' + $Code))
    if (-not $refused) {
        Write-Output ("  got exit " + $Result.exit_code + "; stdout: " + $Result.stdout.Trim())
    }
    Assert-True -Condition $refused -Label ($Label + ' -> REFUSED ' + $Code)
}

function New-CaseBinding {
    param([string]$Name, [hashtable]$Extra = @{})
    $values = @{
        repo = $fix.repo
        commit_sha = $fix.shaB
        commit_tree_sha = $fix.treeB
        subtree_tree_sha = $fix.subtreeB
        source_worktree = (Join-Path $work ('wt-' + $Name))
        destination = (Join-Path $work ('dest-' + $Name))
        controller_manifest = (Join-Path $work ('manifest-' + $Name + '.json'))
        evidence_out = (Join-Path $work ('evidence-' + $Name + '.json'))
    }
    foreach ($k in $Extra.Keys) { $values[$k] = $Extra[$k] }
    $path = Join-Path $work ('binding-' + $Name + '.json')
    New-BindingFile -Path $path -Values $values | Out-Null
    return @{ path = $path; values = $values }
}

$lureTarget = Join-Path $work 'lure-target'
New-Item -ItemType Directory -Force -Path $lureTarget | Out-Null
Set-Content -LiteralPath (Join-Path $lureTarget 'lured.py') -Value 'print("outside")' -Encoding ascii

# ---- J1: junction INSIDE the controller source tree refuses the backup ------
$j1 = New-CaseBinding -Name 'j1'
Initialize-TxSources -BindingPath $j1.path | Out-Null
$junction = Join-Path $j1.values.destination 'junction_dir'
New-Item -ItemType Junction -Path $junction -Target $lureTarget | Out-Null
$r = Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $j1.path
Assert-Refused -Result $r -Code 'reparse_point_detected' -Label 'J1 junction inside the controller tree'
Assert-True -Condition (-not (Test-Path -LiteralPath ($j1.values.destination + '-backup-evidence.json'))) -Label 'J1 no evidence written'
(Get-Item -LiteralPath $junction).Delete()

# ---- J2: backup root that IS a junction refuses (chain check) ---------------
$j2root = Join-Path $work 'j2-backup-root-junction'
New-Item -ItemType Junction -Path $j2root -Target $lureTarget | Out-Null
$j2 = New-CaseBinding -Name 'j2' -Extra @{ backup_root = $j2root }
Initialize-TxSources -BindingPath $j2.path | Out-Null
$r = Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $j2.path
Assert-Refused -Result $r -Code 'reparse_point_detected' -Label 'J2 backup root is a junction'
(Get-Item -LiteralPath $j2root).Delete()

# ---- J3: junction planted at the DESTINATION refuses the install mirror -----
$j3 = New-CaseBinding -Name 'j3'
Initialize-TxSources -BindingPath $j3.path | Out-Null
$r = Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $j3.path
Assert-True -Condition ($r.exit_code -eq 0) -Label 'J3 clean backup exits 0'
$junction = Join-Path $j3.values.destination 'junction_dir'
New-Item -ItemType Junction -Path $junction -Target $lureTarget | Out-Null
$r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase install -BindingFile $j3.path
# Layered defense: the junction changes the destination inventory, so the
# currency gate (backup_stale) stops the mirror even before the dedicated
# reparse gate would; the reparse gate itself is proven by J1/J2 and by the
# m_reparse mutant. What matters here: never a pass, nothing mirrored.
Assert-True -Condition ($r.exit_code -ne 0) -Label 'J3 install refuses over a junction-bearing destination'
Assert-True -Condition (Test-Path -LiteralPath (Join-Path $j3.values.destination 'legacy_module.py')) -Label 'J3 destination unchanged by the refused install'
(Get-Item -LiteralPath $junction).Delete()

# ---- J4: destination escaping the approved controller root refuses ----------
$outside = Join-Path $work 'outside-root\agent_supervisor'
$j4 = New-CaseBinding -Name 'j4' -Extra @{ destination = $outside; controller_root = (Join-Path $work 'dest-j4-root') }
$bindingJson = Get-Content -LiteralPath $j4.path -Raw | ConvertFrom-Json
New-Item -ItemType Directory -Force -Path $outside | Out-Null
Set-Content -LiteralPath (Join-Path $outside 'cli.py') -Value 'print("x")' -Encoding ascii
New-Item -ItemType Directory -Force -Path $bindingJson.a1_runtime_dir | Out-Null
Set-Content -LiteralPath (Join-Path $bindingJson.a1_runtime_dir 'journal.db') -Value 'j' -Encoding ascii
$r = Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $j4.path
Assert-Refused -Result $r -Code 'path_containment_violation' -Label 'J4 destination outside its approved controller root'

if ($script:failures -gt 0) {
    Write-Output ("test_junction_containment: " + $script:failures + " assertion failure(s); fixtures kept at " + $work)
    exit 1
}
Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
Write-Output 'test_junction_containment: reparse and containment teeth verified'
exit 0
