# test_runbook_parse.ps1 - the exact owner-typed commands are checked in,
# concrete, and parse-clean on PowerShell 5.1 (M0-T138; D-024-R612/R614).
#
# 1. The operator script parses with zero PS 5.1 parser errors.
# 2. Every fenced ```powershell block in docs/CONTROLLER_UPDATE_RUNBOOK.md
#    parses with zero errors (this also rejects PS7-only syntax such as '&&').
# 3. The section-4 install block pins the concrete immutable 40-hex SHA and
#    carries no angle-bracket placeholder; section 5a presents verify-manifest.
# 4. No 'origin/main' instruction remains anywhere in the runbook.
$script:failures = 0

function Assert-True {
    param([bool]$Condition, [string]$Label)
    if ($Condition) {
        Write-Output ("PASS " + $Label)
    } else {
        Write-Output ("ASSERT-FAIL " + $Label)
        $script:failures = $script:failures + 1
    }
}

$toolRoot = Split-Path $PSScriptRoot -Parent
$repoRoot = Split-Path (Split-Path $toolRoot -Parent) -Parent
$scriptPath = Join-Path $toolRoot 'update_controller_from_candidate.ps1'
$runbookPath = Join-Path $repoRoot 'docs\CONTROLLER_UPDATE_RUNBOOK.md'
$pinnedSha = '1489879e1f6787a9d53ed74db4524b24039e03a2'

$tokens = $null
$errors = $null
[System.Management.Automation.Language.Parser]::ParseFile($scriptPath, [ref]$tokens, [ref]$errors) | Out-Null
Assert-True -Condition (@($errors).Count -eq 0) -Label 'operator script parses with zero PS 5.1 errors'
if (@($errors).Count -gt 0) { Write-Output ("  first error: " + @($errors)[0].Message) }

Assert-True -Condition (Test-Path -LiteralPath $runbookPath) -Label 'runbook exists'
$runbookText = [System.IO.File]::ReadAllText($runbookPath)
$lines = [System.IO.File]::ReadAllLines($runbookPath)

Assert-True -Condition ($runbookText -notmatch 'origin/main') -Label 'no origin/main instruction remains in the runbook'

# Collect fenced powershell blocks with the heading section active at each block.
$blocks = @()
$inFence = $false
$currentSection = ''
$blockLines = @()
foreach ($line in $lines) {
    if ($line -match '^##\s+(\S+)') { $currentSection = $Matches[1].TrimEnd('.') }
    if (-not $inFence) {
        if ($line.TrimStart() -match '^```powershell\s*$') {
            $inFence = $true
            $blockLines = @()
        }
        continue
    }
    if ($line.TrimStart() -match '^```\s*$') {
        $inFence = $false
        $blocks += , @{ section = $currentSection; text = ($blockLines -join "`n") }
        continue
    }
    $blockLines += $line
}
Assert-True -Condition ($blocks.Count -ge 8) -Label ('runbook carries fenced powershell blocks (' + $blocks.Count + ' found)')

$blockIndex = 0
foreach ($block in $blocks) {
    $blockIndex = $blockIndex + 1
    $tokens = $null
    $errors = $null
    [System.Management.Automation.Language.Parser]::ParseInput($block.text, [ref]$tokens, [ref]$errors) | Out-Null
    $label = 'block ' + $blockIndex + ' (section ' + $block.section + ') parses with zero PS 5.1 errors'
    Assert-True -Condition (@($errors).Count -eq 0) -Label $label
    if (@($errors).Count -gt 0) { Write-Output ("  first error: " + @($errors)[0].Message) }
}

$section4 = @($blocks | Where-Object { $_.section -eq '4' })
Assert-True -Condition ($section4.Count -ge 1) -Label 'section 4 presents at least one fenced command block'
$installBlocks = @($section4 | Where-Object { $_.text -match 'update_controller_from_candidate\.ps1' })
Assert-True -Condition ($installBlocks.Count -ge 1) -Label 'section 4 invokes the checked-in operator script'
$pinned = @($section4 | Where-Object { $_.text -match '-Phase install' })
Assert-True -Condition ($pinned.Count -ge 1) -Label 'section 4 presents the concrete -Phase install command'
foreach ($block in $section4) {
    Assert-True -Condition (-not $block.text.Contains('<')) -Label 'section 4 block carries no angle-bracket placeholder'
}

$bindingPath = Join-Path $toolRoot 'source_binding.json'
$binding = Get-Content -LiteralPath $bindingPath -Raw | ConvertFrom-Json
Assert-True -Condition ($binding.commit_sha -eq $pinnedSha) -Label 'binding contract pins the immutable accepted SHA'
Assert-True -Condition ($runbookText.Contains($pinnedSha)) -Label 'runbook section 4 states the same immutable SHA'

$section5a = @($blocks | Where-Object { $_.section -eq '5a' -and $_.text -match '-Phase verify-manifest' })
Assert-True -Condition ($section5a.Count -ge 1) -Label 'section 5a presents the concrete -Phase verify-manifest command'

if ($script:failures -gt 0) {
    Write-Output ("test_runbook_parse: " + $script:failures + " assertion failure(s)")
    exit 1
}
Write-Output 'test_runbook_parse: runbook and operator script parse-clean and concrete'
exit 0
