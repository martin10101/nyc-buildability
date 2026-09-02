# update_controller_from_candidate.ps1 - fail-closed controller install from the
# immutable accepted production candidate (D-024 Amendment 41, R608-R611).
#
# The copy source is pinned by the checked-in binding contract
# (source_binding.json): an exact 40-hex commit SHA plus its accepted commit
# tree, tools/agent_supervisor subtree tree, and required-module list. The
# script never resolves origin/main, HEAD, a branch name, or any other mutable
# ref; a binding value that is not a full 40-hex SHA is refused outright. The
# binding contract itself changes only through a reviewed commit - the operator
# compares the printed identity against the acceptance record before continuing.
#
# -Phase install:
#   verify repo + normalized origin identity, commit existence, commit tree,
#   subtree tree, required modules, then create a fresh DETACHED source worktree
#   at exactly the pinned commit, mirror the accepted subtree into the live
#   controller, prove every installed file byte-identical to the accepted source
#   (complete bidirectional raw SHA-256 comparison), and record
#   controller_update_evidence.json binding source commit/tree/subtree and every
#   installed-file digest.
# -Phase verify-manifest:
#   after `record-manifest` (runbook section 5): re-verify the source identity,
#   re-compare the installed tree against the accepted source, and cross-check
#   every manifest-covered digest (LF-normalized, the manifest's own algorithm)
#   against the ACCEPTED SOURCE tree - a manifest merely self-consistent with a
#   wrong or tampered installation is refused - then bind the result into the
#   update evidence.
#
# Every failure prints one typed "REFUSED <reason_code>: <detail>" line and
# exits 1 with nothing further executed. Success prints a summary and exits 0.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][ValidateSet('install', 'verify-manifest')][string]$Phase,
    [string]$BindingFile = ''
)

# Native stderr must never become a terminating error: every native call is
# judged by its raw exit code alone (ps_tests harness discipline), captured via
# temp files, never piped.
$ErrorActionPreference = 'Continue'

if ($BindingFile -eq '') { $BindingFile = Join-Path $PSScriptRoot 'source_binding.json' }

function Exit-Refusal {
    param([string]$Code, [string]$Message)
    Write-Output ("REFUSED " + $Code + ": " + $Message)
    exit 1
}

function Invoke-Native {
    param([string]$FilePath, [string[]]$NativeArgs)
    $so = [System.IO.Path]::GetTempFileName()
    $se = [System.IO.Path]::GetTempFileName()
    $global:LASTEXITCODE = $null
    $invocationError = ''
    try {
        & $FilePath @NativeArgs 1>$so 2>$se
    } catch {
        $invocationError = $_.Exception.Message
    }
    $code = $global:LASTEXITCODE
    $stdout = ''
    $stderr = ''
    if (Test-Path -LiteralPath $so) { $stdout = ([System.IO.File]::ReadAllText($so)).Trim() }
    if (Test-Path -LiteralPath $se) { $stderr = ([System.IO.File]::ReadAllText($se)).Trim() }
    Remove-Item -LiteralPath $so, $se -Force -ErrorAction SilentlyContinue
    if ($null -eq $code) {
        Exit-Refusal 'native_no_exit_code' ("command never produced an exit code (fail closed): " +
            $FilePath + ' ' + ($NativeArgs -join ' ') + ' ' + $invocationError)
    }
    return @{ code = [int]$code; stdout = $stdout; stderr = $stderr }
}

function Get-RawSha256 {
    param([string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-LfNormalizedSha256 {
    # The controller manifest records LF-normalized digests (manifest._hash_file);
    # Latin-1 round-trips every byte value, so the CRLF->LF replace is byte-exact.
    param([string]$Path)
    $latin1 = [System.Text.Encoding]::GetEncoding(28591)
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    $normalized = $latin1.GetBytes($latin1.GetString($bytes).Replace("`r`n", "`n"))
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { $hash = $sha.ComputeHash($normalized) } finally { $sha.Dispose() }
    return (($hash | ForEach-Object { $_.ToString('x2') }) -join '')
}

function Get-TreeFiles {
    # Forward-slash relative file paths under $Root, excluding runtime cache and
    # VCS directories at any depth (they are neither copied nor compared).
    param([string]$Root)
    $rootFull = (Get-Item -LiteralPath $Root).FullName.TrimEnd('\')
    $files = @()
    foreach ($item in (Get-ChildItem -LiteralPath $rootFull -Recurse -File -Force)) {
        $rel = $item.FullName.Substring($rootFull.Length + 1).Replace('\', '/')
        $excluded = $false
        foreach ($part in $rel.Split('/')) {
            if ($part -in @('__pycache__', '.pytest_cache', '.git')) { $excluded = $true }
        }
        if (-not $excluded) { $files += $rel }
    }
    return @($files | Sort-Object)
}

# The manifest's coverage contract (manifest.COVERED_PATTERNS under fnmatch,
# where * crosses path separators) expressed as anchored regexes, with the
# deliberately-excluded names (manifest.EXCLUDED_NAMES). Any divergence between
# this projection and the recorded manifest FAILS the cross-check - it can
# never silently pass.
$CoveredPatterns = @(
    '^.*\.py$', '^schemas/.*\.json$', '^prompts/.*\.md$', '^config\.toml$',
    '^config\.example\.toml$', '^launchers/.*\.cmd$', '^launchers/.*\.ps1$', '^README\.md$')
$ExcludedNames = @('model_selection.toml', 'controller_manifest.json')

function Get-CoveredFiles {
    param([string]$Root)
    $covered = @()
    foreach ($rel in (Get-TreeFiles -Root $Root)) {
        if (($rel.Split('/'))[-1] -in $ExcludedNames) { continue }
        foreach ($pattern in $CoveredPatterns) {
            if ($rel -match $pattern) { $covered += $rel; break }
        }
    }
    return @($covered | Sort-Object)
}

# ---- binding contract ------------------------------------------------------

if (-not (Test-Path -LiteralPath $BindingFile)) {
    Exit-Refusal 'binding_unreadable' ("binding contract not found: " + $BindingFile)
}
try {
    $binding = Get-Content -LiteralPath $BindingFile -Raw -ErrorAction Stop | ConvertFrom-Json
} catch {
    Exit-Refusal 'binding_unreadable' ("binding contract is not valid JSON: " + $_.Exception.Message)
}
foreach ($key in @('source_repo', 'expected_origin_url', 'commit_sha', 'commit_tree_sha',
        'subtree_path', 'subtree_tree_sha', 'required_modules', 'source_worktree',
        'destination', 'controller_manifest', 'evidence_out')) {
    if ($null -eq $binding.PSObject.Properties[$key]) {
        Exit-Refusal 'binding_incomplete' ("binding contract is missing key '" + $key + "'")
    }
}

$repo = [string]$binding.source_repo
$sourceWorktree = [string]$binding.source_worktree
$destination = [string]$binding.destination
$manifestPath = [Environment]::ExpandEnvironmentVariables([string]$binding.controller_manifest)
$evidencePath = [Environment]::ExpandEnvironmentVariables([string]$binding.evidence_out)

# The immutable-source rule (R608): only a full 40-hex commit SHA is ever
# accepted - origin/main, HEAD, a branch, a tag, or a short SHA all refuse here.
if ($binding.commit_sha -notmatch '^[0-9a-f]{40}$') {
    Exit-Refusal 'not_a_full_sha' ("the pinned source must be an immutable full 40-hex commit SHA, " +
        "never a mutable ref such as origin/main; got '" + $binding.commit_sha + "'")
}
if ($binding.commit_tree_sha -notmatch '^[0-9a-f]{40}$') {
    Exit-Refusal 'not_a_full_sha' ("commit_tree_sha must be a full 40-hex tree SHA; got '" +
        $binding.commit_tree_sha + "'")
}
if ($binding.subtree_tree_sha -notmatch '^[0-9a-f]{40}$') {
    Exit-Refusal 'not_a_full_sha' ("subtree_tree_sha must be a full 40-hex tree SHA; got '" +
        $binding.subtree_tree_sha + "'")
}

function Assert-SourceIdentity {
    # Pre-copy identity verification (R609): repo, normalized origin, commit
    # existence, accepted commit tree, accepted subtree tree, required modules.
    $topProbe = Invoke-Native 'git' @('-C', $repo, 'rev-parse', '--show-toplevel')
    if ($topProbe.code -ne 0) {
        Exit-Refusal 'source_repo_missing' ("no git repository at '" + $repo + "': " + $topProbe.stderr)
    }
    $observedTop = [System.IO.Path]::GetFullPath($topProbe.stdout.Replace('/', '\')).TrimEnd('\').ToLowerInvariant()
    $expectedTop = [System.IO.Path]::GetFullPath($repo).TrimEnd('\').ToLowerInvariant()
    if ($observedTop -ne $expectedTop) {
        Exit-Refusal 'source_repo_identity_mismatch' ("git toplevel '" + $observedTop +
            "' is not the bound source repository '" + $expectedTop + "'")
    }
    $originProbe = Invoke-Native 'git' @('-C', $repo, 'remote', 'get-url', 'origin')
    if ($originProbe.code -ne 0) {
        Exit-Refusal 'origin_mismatch' ("the source repository has no 'origin' remote: " + $originProbe.stderr)
    }
    $normalizedObserved = $originProbe.stdout.Trim().TrimEnd('/').ToLowerInvariant()
    if ($normalizedObserved.EndsWith('.git')) { $normalizedObserved = $normalizedObserved.Substring(0, $normalizedObserved.Length - 4) }
    $normalizedExpected = ([string]$binding.expected_origin_url).Trim().TrimEnd('/').ToLowerInvariant()
    if ($normalizedExpected.EndsWith('.git')) { $normalizedExpected = $normalizedExpected.Substring(0, $normalizedExpected.Length - 4) }
    if ($normalizedObserved -ne $normalizedExpected) {
        Exit-Refusal 'origin_mismatch' ("normalized origin '" + $normalizedObserved +
            "' does not match the bound origin '" + $normalizedExpected + "'")
    }
    $script:ObservedOrigin = $originProbe.stdout.Trim()
    $typeProbe = Invoke-Native 'git' @('-C', $repo, 'cat-file', '-t', $binding.commit_sha)
    if ($typeProbe.code -ne 0) {
        Exit-Refusal 'commit_missing' ("the pinned commit " + $binding.commit_sha +
            " does not exist in the source repository: " + $typeProbe.stderr)
    }
    if ($typeProbe.stdout -ne 'commit') {
        Exit-Refusal 'not_a_commit' ("the pinned object " + $binding.commit_sha + " is a '" +
            $typeProbe.stdout + "', not a commit")
    }
    $treeProbe = Invoke-Native 'git' @('-C', $repo, 'rev-parse', ($binding.commit_sha + '^{tree}'))
    if ($treeProbe.code -ne 0) {
        Exit-Refusal 'tree_unobservable' ("could not resolve the commit tree: " + $treeProbe.stderr)
    }
    if ($treeProbe.stdout -ne $binding.commit_tree_sha) {
        Exit-Refusal 'tree_mismatch' ("the pinned commit's tree " + $treeProbe.stdout +
            " does not match the accepted evidence tree " + $binding.commit_tree_sha +
            " - a wrong (even internally self-consistent) commit is refused")
    }
    $subtreeProbe = Invoke-Native 'git' @('-C', $repo, 'rev-parse', ($binding.commit_sha + ':' + $binding.subtree_path))
    if ($subtreeProbe.code -ne 0) {
        Exit-Refusal 'subtree_missing' ("the pinned commit has no '" + $binding.subtree_path +
            "' subtree: " + $subtreeProbe.stderr)
    }
    if ($subtreeProbe.stdout -ne $binding.subtree_tree_sha) {
        Exit-Refusal 'subtree_mismatch' ("the '" + $binding.subtree_path + "' subtree " +
            $subtreeProbe.stdout + " does not match the accepted subtree " + $binding.subtree_tree_sha)
    }
    foreach ($module in @($binding.required_modules)) {
        $moduleProbe = Invoke-Native 'git' @('-C', $repo, 'cat-file', '-e', ($binding.commit_sha + ':' + $module))
        if ($moduleProbe.code -ne 0) {
            Exit-Refusal 'missing_module' ("required Tranche-B module '" + $module +
                "' does not exist at the pinned commit " + $binding.commit_sha)
        }
    }
}

function Assert-SourceWorktreeState {
    # The source worktree must be DETACHED at exactly the pinned commit and
    # clean (R609) - a branch checkout could silently advance under the copy.
    $symProbe = Invoke-Native 'git' @('-C', $sourceWorktree, 'symbolic-ref', '-q', 'HEAD')
    if ($symProbe.code -eq 0) {
        Exit-Refusal 'source_not_detached' ("the source worktree is on ref '" + $symProbe.stdout +
            "'; it must be DETACHED at " + $binding.commit_sha)
    }
    $headProbe = Invoke-Native 'git' @('-C', $sourceWorktree, 'rev-parse', 'HEAD')
    if ($headProbe.code -ne 0) {
        Exit-Refusal 'source_worktree_invalid' ("not a usable git worktree: " + $headProbe.stderr)
    }
    if ($headProbe.stdout -ne $binding.commit_sha) {
        Exit-Refusal 'source_wrong_commit' ("the source worktree HEAD " + $headProbe.stdout +
            " is not the pinned commit " + $binding.commit_sha)
    }
    $statusProbe = Invoke-Native 'git' @('-C', $sourceWorktree, 'status', '--porcelain')
    if ($statusProbe.code -ne 0) {
        Exit-Refusal 'source_worktree_invalid' ("git status failed: " + $statusProbe.stderr)
    }
    if ($statusProbe.stdout -ne '') {
        Exit-Refusal 'source_unclean' ("the source worktree is not clean: " +
            (($statusProbe.stdout -split "`n" | Select-Object -First 5) -join '; '))
    }
}

function Compare-InstalledTree {
    # Complete bidirectional per-file raw SHA-256 comparison (R610): every
    # accepted source file present and byte-identical, nothing extra installed.
    param([string]$SourceSubtree)
    if (-not (Test-Path -LiteralPath $destination)) {
        Exit-Refusal 'destination_missing' ("installed controller tree not found: " + $destination)
    }
    $sourceFiles = Get-TreeFiles -Root $SourceSubtree
    if ($sourceFiles.Count -eq 0) {
        Exit-Refusal 'source_subtree_empty' ("no files under the accepted source subtree: " + $SourceSubtree)
    }
    $destFiles = Get-TreeFiles -Root $destination
    $comparisonFailures = @()
    $digests = @{}
    foreach ($rel in $sourceFiles) {
        if ($rel -notin $destFiles) { $comparisonFailures += ('missing at destination: ' + $rel) }
    }
    foreach ($rel in $destFiles) {
        if ($rel -notin $sourceFiles) { $comparisonFailures += ('unexpected at destination: ' + $rel) }
    }
    foreach ($rel in $sourceFiles) {
        if ($rel -in $destFiles) {
            $sourceHash = Get-RawSha256 (Join-Path $SourceSubtree ($rel.Replace('/', '\')))
            $destinationHash = Get-RawSha256 (Join-Path $destination ($rel.Replace('/', '\')))
            if ($sourceHash -ne $destinationHash) { $comparisonFailures += ('content differs: ' + $rel) }
            $digests[$rel] = $sourceHash
        }
    }
    if ($comparisonFailures.Count -gt 0) {
        Exit-Refusal 'content_mismatch' ("installed tree does not match the accepted source (" +
            $comparisonFailures.Count + " difference(s)): " +
            (($comparisonFailures | Select-Object -First 10) -join '; '))
    }
    return $digests
}

$sourceSubtreePath = Join-Path $sourceWorktree (([string]$binding.subtree_path).Replace('/', '\'))

if ($Phase -eq 'install') {
    Assert-SourceIdentity
    if (Test-Path -LiteralPath $sourceWorktree) {
        Exit-Refusal 'source_worktree_exists' ("a source worktree already exists at '" + $sourceWorktree +
            "'; remove it first: git -C " + $repo + " worktree remove --force " + $sourceWorktree)
    }
    $addProbe = Invoke-Native 'git' @('-C', $repo, 'worktree', 'add', '--detach', $sourceWorktree, $binding.commit_sha)
    if ($addProbe.code -ne 0) {
        Exit-Refusal 'worktree_create_failed' ("git worktree add failed: " + $addProbe.stderr)
    }
    Assert-SourceWorktreeState
    if (-not (Test-Path -LiteralPath $sourceSubtreePath)) {
        Exit-Refusal 'subtree_missing' ("checked-out source subtree not found: " + $sourceSubtreePath)
    }
    $copyProbe = Invoke-Native 'robocopy' @($sourceSubtreePath, $destination, '/MIR', '/XD', '__pycache__',
        '.pytest_cache', '/R:2', '/W:2', '/NJH', '/NJS', '/NFL', '/NDL', '/NP')
    if ($copyProbe.code -ge 8) {
        Exit-Refusal 'copy_failed' ("robocopy reported failure (exit " + $copyProbe.code + "): " + $copyProbe.stderr)
    }
    $digests = Compare-InstalledTree -SourceSubtree $sourceSubtreePath
    $evidence = [ordered]@{
        schema = 'controller_update_evidence/v1'
        phase = 'install'
        generated_at_utc = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
        binding_file = (Get-Item -LiteralPath $BindingFile).FullName
        source_repo = $repo
        observed_origin_url = $script:ObservedOrigin
        commit_sha = [string]$binding.commit_sha
        commit_tree_sha = [string]$binding.commit_tree_sha
        subtree_path = [string]$binding.subtree_path
        subtree_tree_sha = [string]$binding.subtree_tree_sha
        required_modules_verified = @($binding.required_modules)
        destination = $destination
        installed_file_count = $digests.Count
        installed_files_sha256 = $digests
        comparison = 'PASS'
    }
    $evidenceDir = Split-Path -Parent $evidencePath
    New-Item -ItemType Directory -Force -Path $evidenceDir | Out-Null
    $evidence | ConvertTo-Json -Depth 6 | Out-File -FilePath $evidencePath -Encoding utf8
    Write-Output ("INSTALLED from immutable commit " + $binding.commit_sha)
    Write-Output ("  commit tree   " + $binding.commit_tree_sha)
    Write-Output ("  subtree tree  " + $binding.subtree_tree_sha)
    Write-Output ("  files         " + $digests.Count + " byte-identical source-to-destination")
    Write-Output ("  evidence      " + $evidencePath)
    Write-Output ("Compare this identity against the acceptance record before continuing (runbook section 4).")
    exit 0
}

if ($Phase -eq 'verify-manifest') {
    Assert-SourceIdentity
    if (-not (Test-Path -LiteralPath $sourceWorktree)) {
        Exit-Refusal 'source_worktree_missing' ("the accepted source worktree is gone from '" +
            $sourceWorktree + "'; re-run -Phase install")
    }
    Assert-SourceWorktreeState
    if (-not (Test-Path -LiteralPath $evidencePath)) {
        Exit-Refusal 'install_evidence_missing' ("no install evidence at '" + $evidencePath +
            "'; run -Phase install first")
    }
    $digests = Compare-InstalledTree -SourceSubtree $sourceSubtreePath
    if (-not (Test-Path -LiteralPath $manifestPath)) {
        Exit-Refusal 'manifest_unreadable' ("recorded controller manifest not found: " + $manifestPath)
    }
    try {
        $manifest = Get-Content -LiteralPath $manifestPath -Raw -ErrorAction Stop | ConvertFrom-Json
    } catch {
        Exit-Refusal 'manifest_unreadable' ("recorded controller manifest is not valid JSON: " + $_.Exception.Message)
    }
    if ($null -eq $manifest.PSObject.Properties['files']) {
        Exit-Refusal 'manifest_unreadable' 'recorded controller manifest has no files map'
    }
    $recorded = @{}
    foreach ($property in $manifest.files.PSObject.Properties) { $recorded[$property.Name] = [string]$property.Value }
    $covered = Get-CoveredFiles -Root $sourceSubtreePath
    $recordedKeys = @($recorded.Keys | Where-Object { $_ -ne 'config.toml' } | Sort-Object)
    $manifestKeyFailures = @()
    foreach ($rel in $recordedKeys) {
        if ($rel -notin $covered) { $manifestKeyFailures += ('manifest covers a file the accepted source does not have: ' + $rel) }
    }
    foreach ($rel in $covered) {
        if ($rel -notin $recordedKeys) { $manifestKeyFailures += ('manifest is missing a covered accepted-source file: ' + $rel) }
    }
    if ($manifestKeyFailures.Count -gt 0) {
        Exit-Refusal 'manifest_key_set_mismatch' ("the recorded manifest does not cover the accepted source tree (" +
            $manifestKeyFailures.Count + " difference(s)): " +
            (($manifestKeyFailures | Select-Object -First 10) -join '; '))
    }
    $manifestDigestFailures = @()
    foreach ($rel in $covered) {
        $expectedDigest = Get-LfNormalizedSha256 (Join-Path $sourceSubtreePath ($rel.Replace('/', '\')))
        if ($recorded[$rel] -ne $expectedDigest) {
            $manifestDigestFailures += ('manifest digest for ' + $rel + ' does not match the accepted source')
        }
    }
    if ($manifestDigestFailures.Count -gt 0) {
        Exit-Refusal 'manifest_digest_mismatch' ("the recorded manifest was not generated from the accepted source (" +
            $manifestDigestFailures.Count + " mismatch(es)): " +
            (($manifestDigestFailures | Select-Object -First 10) -join '; '))
    }
    try {
        $evidence = Get-Content -LiteralPath $evidencePath -Raw -ErrorAction Stop | ConvertFrom-Json
    } catch {
        Exit-Refusal 'install_evidence_missing' ("install evidence unreadable: " + $_.Exception.Message)
    }
    $manifestBinding = [ordered]@{
        manifest_path = $manifestPath
        manifest_digest = [string]$manifest.manifest_digest
        covered_file_count = $covered.Count
        verdict = 'PASS'
        checked_at_utc = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
    }
    $evidence | Add-Member -NotePropertyName 'manifest_binding' -NotePropertyValue $manifestBinding -Force
    $evidence | ConvertTo-Json -Depth 6 | Out-File -FilePath $evidencePath -Encoding utf8
    Write-Output ("MANIFEST VERIFIED against the accepted source at " + $binding.commit_sha)
    Write-Output ("  covered files " + $covered.Count + "; installed files re-compared " + $digests.Count)
    Write-Output ("  evidence      " + $evidencePath)
    exit 0
}

Exit-Refusal 'unknown_phase' ("unsupported phase '" + $Phase + "'")
