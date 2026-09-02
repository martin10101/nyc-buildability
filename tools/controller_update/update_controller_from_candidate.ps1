# update_controller_from_candidate.ps1 - fail-closed controller-update TRANSACTION
# from the immutable accepted production candidate (D-024 Amendment 41 R608-R611;
# Amendment 42 R622-R643).
#
# The copy source is pinned by the checked-in binding contract
# (source_binding.json, schema v2): an exact 40-hex commit SHA plus its accepted
# commit tree, tools/agent_supervisor subtree tree, and required-module list,
# PLUS the transaction paths (controller root, backup root, A1 runtime journal
# directory, backup/rollback evidence). The script never resolves origin/main,
# HEAD, a branch name, or any other mutable ref; a binding value that is not a
# full 40-hex SHA is refused outright. Long hashes and runtime keys live ONLY in
# the reviewed binding contract - never retyped into commands (R636). The
# binding contract itself changes only through a reviewed commit.
#
# -Phase backup (R624-R630):
#   verify every source and the backup destination (exact approved path,
#   containment, no reparse points), create a UNIQUE previously nonexistent
#   backup directory (collision refused), copy the live controller subtree and
#   the A1 runtime journal with each robocopy's raw exit code captured
#   immediately (the first failure can never be masked by the second copy),
#   prove BOTH backups with complete bidirectional raw SHA-256 comparison, and
#   only then atomically record controller_backup_evidence.json binding the run
#   id, exact paths, pre-update controller identity, both raw copy codes, the
#   complete digest sets, and the PASS verdict.
# -Phase install (R609-R611 + R631):
#   REQUIRES the verified backup evidence (never "the newest backup"): the
#   bound backup is re-verified against its evidence (tamper) and the live
#   destination is proven unchanged since that backup (currency) BEFORE the
#   destructive mirror. Then: source identity verification, fresh DETACHED
#   worktree at the pinned commit, containment + reparse checks immediately
#   before the mirror, /MIR of the accepted subtree, cache-residue removal,
#   complete bidirectional SHA-256 proof, and atomic
#   controller_update_evidence.json recording the source identity AND the exact
#   backup-evidence identity it installed over.
# -Phase verify-manifest (R611):
#   after record-manifest: re-verify the source identity, re-compare the
#   installed tree, and cross-check every manifest-covered digest against the
#   ACCEPTED SOURCE tree; bind the result into the update evidence.
# -Phase rollback (R632-R635):
#   restores ONLY the backup bound by controller_backup_evidence.json (never an
#   auto-selected newest directory), after re-verifying that backup against its
#   evidence (a tampered backup is never restored). The mirror is preceded by
#   the same containment + reparse checks and confined to the exact controller
#   subtree; partial-install residue cannot survive (/MIR + cache removal);
#   afterwards the restored tree is proven bidirectionally digest-equal to the
#   bound evidence, stale activation records are removed with checked results,
#   and controller_rollback_evidence.json is written atomically.
#
# Every failure prints one typed "REFUSED <reason_code>: <detail>" line and
# exits 1 with nothing further executed. Success prints a summary and exits 0.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('backup', 'install', 'verify-manifest', 'rollback')][string]$Phase,
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

# Runtime cache directories: never copied, never compared, and removed from the
# live tree after every destructive mirror so no stale cache can shadow the
# accepted source (R633; python regenerates them on demand).
$CacheDirNames = @('__pycache__', '.pytest_cache')

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

function Get-TreeFilesFull {
    # COMPLETE inventory - no exclusions. Used for the A1 runtime journal
    # backup, where every byte is preserved and proven (R629).
    param([string]$Root)
    $rootFull = (Get-Item -LiteralPath $Root).FullName.TrimEnd('\')
    $files = @()
    foreach ($item in (Get-ChildItem -LiteralPath $rootFull -Recurse -File -Force)) {
        $files += $item.FullName.Substring($rootFull.Length + 1).Replace('\', '/')
    }
    return @($files | Sort-Object)
}

function Get-CanonicalPath {
    param([string]$Path)
    return [System.IO.Path]::GetFullPath($Path).TrimEnd('\')
}

function Assert-ContainedIn {
    # $Child must be $Root or live strictly under it (R628/R635 containment).
    param([string]$Child, [string]$Root, [string]$Label)
    $childCanon = (Get-CanonicalPath $Child).ToLowerInvariant()
    $rootCanon = (Get-CanonicalPath $Root).ToLowerInvariant()
    if ($childCanon -ne $rootCanon -and -not $childCanon.StartsWith($rootCanon + '\')) {
        Exit-Refusal 'path_containment_violation' ($Label + " '" + $Child +
            "' is not contained in its approved root '" + $Root + "'")
    }
}

function Assert-NoReparseChain {
    # $Path (if it exists) and every existing ancestor up to the drive root must
    # be a plain directory - a junction/symlink/mount point anywhere in the
    # chain lets a mirror escape the approved subtree (R628; robocopy /MIR can
    # follow a junction).
    param([string]$Path, [string]$Label)
    $current = Get-CanonicalPath $Path
    while ($current -and $current.Length -gt 3) {
        if (Test-Path -LiteralPath $current) {
            $item = Get-Item -LiteralPath $current -Force
            if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
                Exit-Refusal 'reparse_point_detected' ($Label + ": '" + $current +
                    "' is a reparse point (junction/symlink/mount point) - hard stop")
            }
        }
        $current = Split-Path -Path $current -Parent
    }
}

function Assert-TreeNoReparse {
    # No reparse point anywhere INSIDE $Root (R628): a planted junction would be
    # silently followed by robocopy and by the digest walk alike.
    param([string]$Root, [string]$Label)
    $reparseHit = $null
    foreach ($item in (Get-ChildItem -LiteralPath $Root -Recurse -Force -ErrorAction SilentlyContinue)) {
        if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
            $reparseHit = $item.FullName
            break
        }
    }
    if ($null -ne $reparseHit) {
        Exit-Refusal 'reparse_point_detected' ($Label + ": '" + $reparseHit +
            "' inside '" + $Root + "' is a reparse point - hard stop")
    }
}

function Get-TreeDigestMap {
    # Sorted rel-path -> raw SHA-256 map for a tree (R629/R610).
    param([string]$Root, [bool]$FullInventory)
    if ($FullInventory) { $rels = Get-TreeFilesFull -Root $Root }
    else { $rels = Get-TreeFiles -Root $Root }
    $map = [ordered]@{}
    foreach ($rel in $rels) {
        $map[$rel] = Get-RawSha256 (Join-Path $Root ($rel.Replace('/', '\')))
    }
    return $map
}

function Get-DigestCompareFailures {
    # Complete bidirectional comparison of a live tree against a recorded digest
    # map: missing, extra, and changed files are all failures (R629/R633).
    param([string]$Root, $Map, [bool]$FullInventory, [string]$Label)
    $failures = @()
    if (-not (Test-Path -LiteralPath $Root)) {
        return @($Label + ": tree missing entirely: " + $Root)
    }
    $expected = @{}
    if ($Map -is [System.Collections.IDictionary]) {
        foreach ($k in $Map.Keys) { $expected[[string]$k] = [string]$Map[$k] }
    } else {
        foreach ($prop in $Map.PSObject.Properties) { $expected[$prop.Name] = [string]$prop.Value }
    }
    if ($FullInventory) { $observed = @(Get-TreeFilesFull -Root $Root) }
    else { $observed = @(Get-TreeFiles -Root $Root) }
    foreach ($rel in ($expected.Keys | Sort-Object)) {
        if ($rel -notin $observed) { $failures += ($Label + ': missing file: ' + $rel) }
    }
    foreach ($rel in $observed) {
        if (-not $expected.ContainsKey($rel)) { $failures += ($Label + ': extra file: ' + $rel) }
    }
    foreach ($rel in $observed) {
        if ($expected.ContainsKey($rel)) {
            $liveHash = Get-RawSha256 (Join-Path $Root ($rel.Replace('/', '\')))
            if ($liveHash -ne $expected[$rel]) { $failures += ($Label + ': content differs: ' + $rel) }
        }
    }
    return @($failures)
}

function Invoke-RobocopyRecorded {
    # One robocopy with its RAW exit code captured immediately and recorded for
    # evidence (R625/R626). The CALLER refuses on an unacceptable code with a
    # site-specific guard, so the first copy's failure is judged before any
    # second copy can run and can never be overwritten by it.
    param([string]$Source, [string]$Destination, [string[]]$Switches, [string]$CopyLabel)
    $robocopyArgs = @($Source, $Destination) + $Switches + @('/R:2', '/W:2', '/NJH', '/NJS', '/NFL', '/NDL', '/NP')
    $result = Invoke-Native 'robocopy' $robocopyArgs
    $script:RobocopyExitCodes[$CopyLabel] = $result.code
    return $result.code
}

function Write-JsonAtomic {
    # Evidence is written to a temp file in the same directory and renamed into
    # place, so a crash mid-write can never leave a truncated record (R630).
    param($Payload, [string]$Path)
    $dir = Split-Path -Parent $Path
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    $tmp = Join-Path $dir ((Split-Path -Leaf $Path) + '.tmp-' + [guid]::NewGuid().ToString('N'))
    $Payload | ConvertTo-Json -Depth 8 | Out-File -FilePath $tmp -Encoding utf8
    Move-Item -LiteralPath $tmp -Destination $Path -Force
}

function Remove-CacheDirs {
    # Remove runtime cache directories under $Root after a destructive mirror -
    # the accepted source carries none, so anything here is stale residue that
    # every digest comparison is blind to by construction (R633).
    param([string]$Root)
    $caches = @(Get-ChildItem -LiteralPath $Root -Recurse -Force -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -in $CacheDirNames } |
        Sort-Object { $_.FullName.Length } -Descending)
    foreach ($cache in $caches) {
        Remove-Item -LiteralPath $cache.FullName -Recurse -Force -ErrorAction SilentlyContinue
    }
    $left = @(Get-ChildItem -LiteralPath $Root -Recurse -Force -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -in $CacheDirNames })
    if ($left.Count -gt 0) {
        Exit-Refusal 'residue_removal_failed' ("stale cache directories could not be removed under '" +
            $Root + "': " + (($left | ForEach-Object { $_.FullName } | Select-Object -First 5) -join '; '))
    }
}

# ---- binding contract (schema v2) ------------------------------------------

if (-not (Test-Path -LiteralPath $BindingFile)) {
    Exit-Refusal 'binding_unreadable' ("binding contract not found: " + $BindingFile)
}
try {
    $binding = Get-Content -LiteralPath $BindingFile -Raw -ErrorAction Stop | ConvertFrom-Json
} catch {
    Exit-Refusal 'binding_unreadable' ("binding contract is not valid JSON: " + $_.Exception.Message)
}
foreach ($key in @('schema', 'source_repo', 'expected_origin_url', 'commit_sha', 'commit_tree_sha',
        'subtree_path', 'subtree_tree_sha', 'required_modules', 'source_worktree',
        'destination', 'controller_root', 'backup_root', 'a1_runtime_dir',
        'backup_evidence', 'rollback_evidence', 'controller_manifest', 'evidence_out')) {
    if ($null -eq $binding.PSObject.Properties[$key]) {
        Exit-Refusal 'binding_incomplete' ("binding contract is missing key '" + $key + "'")
    }
}
if ([string]$binding.schema -ne 'controller_update_source_binding/v2') {
    Exit-Refusal 'binding_schema_unsupported' ("expected schema 'controller_update_source_binding/v2', got '" +
        $binding.schema + "'")
}

$repo = [string]$binding.source_repo
$sourceWorktree = [string]$binding.source_worktree
$destination = [string]$binding.destination
$controllerRoot = [string]$binding.controller_root
$backupRoot = [string]$binding.backup_root
$a1RuntimeDir = [Environment]::ExpandEnvironmentVariables([string]$binding.a1_runtime_dir)
$backupEvidencePath = [Environment]::ExpandEnvironmentVariables([string]$binding.backup_evidence)
$rollbackEvidencePath = [Environment]::ExpandEnvironmentVariables([string]$binding.rollback_evidence)
$manifestPath = [Environment]::ExpandEnvironmentVariables([string]$binding.controller_manifest)
$evidencePath = [Environment]::ExpandEnvironmentVariables([string]$binding.evidence_out)
$script:RobocopyExitCodes = [ordered]@{}

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
# The A1 runtime key lives ONLY here, machine-validated (R636): its final path
# segment must be the exact 64-hex sha256(checkout) journal key.
if ((Split-Path -Leaf $a1RuntimeDir) -notmatch '^[0-9a-f]{64}$') {
    Exit-Refusal 'runtime_key_invalid' ("a1_runtime_dir must end in the 64-hex runtime journal key; got '" +
        (Split-Path -Leaf $a1RuntimeDir) + "'")
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

function Read-BackupEvidence {
    # The ONE binding between install/rollback and the backup they trust
    # (R631/R632): the recorded evidence file - never a directory listing,
    # never "the newest backup".
    if (-not (Test-Path -LiteralPath $backupEvidencePath)) {
        Exit-Refusal 'backup_evidence_missing' ("no verified backup evidence at '" + $backupEvidencePath +
            "'; run -Phase backup first")
    }
    try {
        $evidence = Get-Content -LiteralPath $backupEvidencePath -Raw -ErrorAction Stop | ConvertFrom-Json
    } catch {
        Exit-Refusal 'backup_evidence_invalid' ("backup evidence is not valid JSON: " + $_.Exception.Message)
    }
    foreach ($key in @('schema', 'run_id', 'backup_dir', 'sources', 'backup_paths',
            'robocopy_exit_codes', 'pre_update_controller_identity', 'runtime_a1_identity', 'verdict')) {
        if ($null -eq $evidence.PSObject.Properties[$key]) {
            Exit-Refusal 'backup_evidence_invalid' ("backup evidence is missing key '" + $key + "'")
        }
    }
    if ([string]$evidence.schema -ne 'controller_backup_evidence/v1') {
        Exit-Refusal 'backup_evidence_invalid' ("unexpected backup evidence schema '" + $evidence.schema + "'")
    }
    if ([string]$evidence.verdict -ne 'PASS') {
        Exit-Refusal 'backup_verdict_not_pass' ("backup evidence verdict is '" + $evidence.verdict +
            "', not PASS - never install over or restore from an unverified backup")
    }
    # Wrong-evidence-file tooth (R634): the evidence must describe THIS bound
    # controller subtree and a backup inside THIS bound backup root.
    $evidenceSource = Get-CanonicalPath ([string]$evidence.sources.controller)
    if ($evidenceSource.ToLowerInvariant() -ne (Get-CanonicalPath $destination).ToLowerInvariant()) {
        Exit-Refusal 'evidence_binding_mismatch' ("backup evidence describes source '" + $evidenceSource +
            "', not the bound controller subtree '" + $destination + "'")
    }
    Assert-ContainedIn ([string]$evidence.backup_dir) $backupRoot 'bound backup directory'
    return @{ evidence = $evidence; file_sha256 = (Get-RawSha256 $backupEvidencePath) }
}

$sourceSubtreePath = Join-Path $sourceWorktree (([string]$binding.subtree_path).Replace('/', '\'))

# ============================================================================
if ($Phase -eq 'backup') {
    # -- source existence + approved-path/containment/reparse checks (R628) --
    if (-not (Test-Path -LiteralPath $destination)) {
        Exit-Refusal 'backup_source_missing' ("live controller subtree not found: " + $destination)
    }
    if (-not (Test-Path -LiteralPath $a1RuntimeDir)) {
        Exit-Refusal 'backup_source_missing' ("A1 runtime journal directory not found: " + $a1RuntimeDir)
    }
    Assert-ContainedIn $destination $controllerRoot 'controller subtree'
    if ((Split-Path -Leaf (Split-Path -Parent $a1RuntimeDir)) -ne 'NYCBuildabilitySupervisor') {
        Exit-Refusal 'path_not_approved' ("a1_runtime_dir '" + $a1RuntimeDir +
            "' is not inside the NYCBuildabilitySupervisor runtime root")
    }
    Assert-NoReparseChain $destination 'controller subtree chain'
    Assert-TreeNoReparse $destination 'controller subtree'
    Assert-NoReparseChain $a1RuntimeDir 'A1 runtime chain'
    Assert-TreeNoReparse $a1RuntimeDir 'A1 runtime directory'
    if (-not (Test-Path -LiteralPath $backupRoot)) {
        New-Item -ItemType Directory -Path $backupRoot -ErrorAction SilentlyContinue | Out-Null
        if (-not (Test-Path -LiteralPath $backupRoot)) {
            Exit-Refusal 'backup_root_unavailable' ("backup root could not be created: " + $backupRoot)
        }
    }
    Assert-NoReparseChain $backupRoot 'backup root chain'

    # -- unique, previously nonexistent backup directory (R627) --------------
    $runId = (Get-Date -Format 'yyyyMMdd-HHmmssfff') + '-' + [guid]::NewGuid().ToString('N').Substring(0, 8)
    $backupDir = Join-Path $backupRoot $runId
    if (Test-Path -LiteralPath $backupDir) {
        Exit-Refusal 'backup_dir_collision' ("backup directory already exists (reuse refused): " + $backupDir)
    }
    try {
        New-Item -ItemType Directory -Path $backupDir -ErrorAction Stop | Out-Null
    } catch {
        Exit-Refusal 'backup_dir_create_failed' ("could not create backup directory '" + $backupDir +
            "': " + $_.Exception.Message)
    }
    if (@(Get-ChildItem -LiteralPath $backupDir -Force).Count -ne 0) {
        Exit-Refusal 'backup_dir_not_empty' ("freshly created backup directory is not empty: " + $backupDir)
    }
    $controllerBackupDir = Join-Path $backupDir 'agent_supervisor'
    $runtimeBackupDir = Join-Path $backupDir 'runtime-a1'

    # -- copy 1: controller subtree; raw code captured IMMEDIATELY (R625/R626)
    $rcControllerCopy = Invoke-RobocopyRecorded -Source $destination -Destination $controllerBackupDir `
        -Switches @('/E', '/XD', '__pycache__', '.pytest_cache') -CopyLabel 'controller_tree'
    if ($rcControllerCopy -lt 0 -or $rcControllerCopy -ge 4) {
        Exit-Refusal 'copy_failed' ("controller-tree backup robocopy returned unacceptable raw exit " +
            $rcControllerCopy + " (accepted: 0-3); the second copy was NOT attempted")
    }
    # -- copy 2: A1 runtime journal; judged by its OWN raw code --------------
    $rcRuntimeCopy = Invoke-RobocopyRecorded -Source $a1RuntimeDir -Destination $runtimeBackupDir `
        -Switches @('/E') -CopyLabel 'runtime_a1'
    if ($rcRuntimeCopy -lt 0 -or $rcRuntimeCopy -ge 4) {
        Exit-Refusal 'copy_failed' ("A1 runtime backup robocopy returned unacceptable raw exit " +
            $rcRuntimeCopy + " (accepted: 0-3)")
    }

    # -- prove BOTH backups: complete bidirectional raw SHA-256 (R629) -------
    $controllerDigests = Get-TreeDigestMap -Root $destination -FullInventory $false
    if ($controllerDigests.Count -eq 0) {
        Exit-Refusal 'backup_source_missing' ("no comparable files under the live controller subtree: " + $destination)
    }
    $controllerBackupFailures = @(Get-DigestCompareFailures -Root $controllerBackupDir -Map $controllerDigests `
        -FullInventory $false -Label 'controller backup')
    if ($controllerBackupFailures.Count -gt 0) {
        Exit-Refusal 'backup_verify_failed' ("controller backup does not match the live source (" +
            $controllerBackupFailures.Count + " difference(s)): " +
            (($controllerBackupFailures | Select-Object -First 10) -join '; '))
    }
    $runtimeDigests = Get-TreeDigestMap -Root $a1RuntimeDir -FullInventory $true
    $runtimeBackupFailures = @(Get-DigestCompareFailures -Root $runtimeBackupDir -Map $runtimeDigests `
        -FullInventory $true -Label 'runtime backup')
    if ($runtimeBackupFailures.Count -gt 0) {
        Exit-Refusal 'backup_verify_failed' ("A1 runtime backup does not match the live source (" +
            $runtimeBackupFailures.Count + " difference(s)): " +
            (($runtimeBackupFailures | Select-Object -First 10) -join '; '))
    }

    # -- atomic evidence, only after verification (R630) ---------------------
    $backupEvidence = [ordered]@{
        schema = 'controller_backup_evidence/v1'
        run_id = $runId
        generated_at_utc = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
        binding_file = (Get-Item -LiteralPath $BindingFile).FullName
        sources = [ordered]@{
            controller = (Get-CanonicalPath $destination)
            runtime_a1 = (Get-CanonicalPath $a1RuntimeDir)
        }
        backup_dir = (Get-CanonicalPath $backupDir)
        backup_paths = [ordered]@{
            controller = (Get-CanonicalPath $controllerBackupDir)
            runtime_a1 = (Get-CanonicalPath $runtimeBackupDir)
        }
        robocopy_exit_codes = $script:RobocopyExitCodes
        pre_update_controller_identity = [ordered]@{
            file_count = $controllerDigests.Count
            files_sha256 = $controllerDigests
        }
        runtime_a1_identity = [ordered]@{
            file_count = $runtimeDigests.Count
            files_sha256 = $runtimeDigests
        }
        comparison_scope = ('controller: raw SHA-256, cache/VCS dirs excluded (' +
            'never copied, removed after every mirror); runtime-a1: complete inventory, no exclusions')
        verdict = 'PASS'
    }
    Write-JsonAtomic -Payload $backupEvidence -Path $backupEvidencePath
    Write-Output ("BACKUP VERIFIED run " + $runId)
    Write-Output ("  controller    " + $controllerDigests.Count + " file(s), robocopy raw exit " + $rcControllerCopy)
    Write-Output ("  runtime-a1    " + $runtimeDigests.Count + " file(s), robocopy raw exit " + $rcRuntimeCopy)
    Write-Output ("  backup dir    " + $backupDir)
    Write-Output ("  evidence      " + $backupEvidencePath)
    exit 0
}

# ============================================================================
if ($Phase -eq 'install') {
    Assert-SourceIdentity

    # -- the install is bound to the VERIFIED backup, never "newest" (R631) --
    $backupBinding = Read-BackupEvidence
    $boundBackup = $backupBinding.evidence
    $boundControllerBackup = [string]$boundBackup.backup_paths.controller
    if (-not (Test-Path -LiteralPath $boundControllerBackup)) {
        Exit-Refusal 'backup_missing' ("the bound backup tree is gone: " + $boundControllerBackup)
    }
    $backupTamperFailures = @(Get-DigestCompareFailures -Root $boundControllerBackup `
        -Map $boundBackup.pre_update_controller_identity.files_sha256 -FullInventory $false -Label 'bound backup')
    if ($backupTamperFailures.Count -gt 0) {
        Exit-Refusal 'backup_tampered' ("the bound backup no longer matches its recorded evidence (" +
            $backupTamperFailures.Count + " difference(s)): " +
            (($backupTamperFailures | Select-Object -First 10) -join '; '))
    }
    $backupStaleFailures = @(Get-DigestCompareFailures -Root $destination `
        -Map $boundBackup.pre_update_controller_identity.files_sha256 -FullInventory $false -Label 'live destination')
    if ($backupStaleFailures.Count -gt 0) {
        Exit-Refusal 'backup_stale' ("the live controller changed after the bound backup was taken (" +
            $backupStaleFailures.Count + " difference(s)); re-run -Phase backup: " +
            (($backupStaleFailures | Select-Object -First 10) -join '; '))
    }

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

    # -- containment + reparse checks IMMEDIATELY before the mirror (R628) ---
    Assert-ContainedIn $destination $controllerRoot 'mirror destination'
    Assert-NoReparseChain $destination 'mirror destination chain'
    Assert-TreeNoReparse $destination 'mirror destination'
    Assert-TreeNoReparse $sourceSubtreePath 'mirror source'

    $rcInstallMirror = Invoke-RobocopyRecorded -Source $sourceSubtreePath -Destination $destination `
        -Switches @('/MIR', '/XD', '__pycache__', '.pytest_cache') -CopyLabel 'install_mirror'
    if ($rcInstallMirror -lt 0 -or $rcInstallMirror -ge 8) {
        Exit-Refusal 'copy_failed' ("install mirror robocopy returned unacceptable raw exit " +
            $rcInstallMirror + " (accepted: 0-7)")
    }
    Remove-CacheDirs -Root $destination
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
        backup_binding = [ordered]@{
            run_id = [string]$boundBackup.run_id
            backup_dir = [string]$boundBackup.backup_dir
            backup_evidence_sha256 = $backupBinding.file_sha256
            reverified = 'PASS'
        }
        robocopy_exit_codes = $script:RobocopyExitCodes
        installed_file_count = $digests.Count
        installed_files_sha256 = $digests
        comparison = 'PASS'
    }
    Write-JsonAtomic -Payload $evidence -Path $evidencePath
    Write-Output ("INSTALLED from immutable commit " + $binding.commit_sha)
    Write-Output ("  commit tree   " + $binding.commit_tree_sha)
    Write-Output ("  subtree tree  " + $binding.subtree_tree_sha)
    Write-Output ("  files         " + $digests.Count + " byte-identical source-to-destination")
    Write-Output ("  backup bound  run " + $boundBackup.run_id + " (evidence sha256 " +
        $backupBinding.file_sha256.Substring(0, 16) + "...)")
    Write-Output ("  evidence      " + $evidencePath)
    Write-Output ("Compare this identity against the acceptance record before continuing (runbook section 4).")
    exit 0
}

# ============================================================================
if ($Phase -eq 'verify-manifest') {
    # The manifest's coverage contract (manifest.COVERED_PATTERNS under fnmatch,
    # where * crosses path separators) expressed as anchored regexes, with the
    # deliberately-excluded names (manifest.EXCLUDED_NAMES). Any divergence
    # between this projection and the recorded manifest FAILS the cross-check.
    $CoveredPatterns = @(
        '^.*\.py$', '^schemas/.*\.json$', '^prompts/.*\.md$', '^config\.toml$',
        '^config\.example\.toml$', '^launchers/.*\.cmd$', '^launchers/.*\.ps1$', '^README\.md$')
    $ExcludedNames = @('model_selection.toml', 'controller_manifest.json')

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
    $covered = @()
    foreach ($rel in (Get-TreeFiles -Root $sourceSubtreePath)) {
        if (($rel.Split('/'))[-1] -in $ExcludedNames) { continue }
        foreach ($pattern in $CoveredPatterns) {
            if ($rel -match $pattern) { $covered += $rel; break }
        }
    }
    $covered = @($covered | Sort-Object)
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
    Write-JsonAtomic -Payload $evidence -Path $evidencePath
    Write-Output ("MANIFEST VERIFIED against the accepted source at " + $binding.commit_sha)
    Write-Output ("  covered files " + $covered.Count + "; installed files re-compared " + $digests.Count)
    Write-Output ("  evidence      " + $evidencePath)
    exit 0
}

# ============================================================================
if ($Phase -eq 'rollback') {
    # Deliberately needs NO git and no source repository: rollback must work in
    # exactly the disaster it exists for. It trusts ONLY the recorded backup
    # evidence (R632) - never a directory listing, never the newest name.
    $backupBinding = Read-BackupEvidence
    $boundBackup = $backupBinding.evidence
    $boundControllerBackup = [string]$boundBackup.backup_paths.controller
    if (-not (Test-Path -LiteralPath $boundControllerBackup)) {
        Exit-Refusal 'backup_missing' ("the bound backup tree is gone: " + $boundControllerBackup)
    }
    # A tampered backup is never restored (R634).
    $rollbackTamperFailures = @(Get-DigestCompareFailures -Root $boundControllerBackup `
        -Map $boundBackup.pre_update_controller_identity.files_sha256 -FullInventory $false -Label 'bound backup')
    if ($rollbackTamperFailures.Count -gt 0) {
        Exit-Refusal 'backup_tampered' ("the bound backup no longer matches its recorded evidence (" +
            $rollbackTamperFailures.Count + " difference(s)); restoring it would install unknown content: " +
            (($rollbackTamperFailures | Select-Object -First 10) -join '; '))
    }
    # Containment + reparse checks immediately before the destructive mirror
    # (R635): the mirror can only ever write the exact controller subtree.
    Assert-ContainedIn $destination $controllerRoot 'rollback destination'
    Assert-NoReparseChain $destination 'rollback destination chain'
    if (Test-Path -LiteralPath $destination) {
        Assert-TreeNoReparse $destination 'rollback destination'
    }
    Assert-NoReparseChain $boundControllerBackup 'bound backup chain'
    Assert-TreeNoReparse $boundControllerBackup 'bound backup'

    $rcRollbackMirror = Invoke-RobocopyRecorded -Source $boundControllerBackup -Destination $destination `
        -Switches @('/MIR', '/XD', '__pycache__', '.pytest_cache') -CopyLabel 'rollback_mirror'
    if ($rcRollbackMirror -lt 0 -or $rcRollbackMirror -ge 8) {
        Exit-Refusal 'copy_failed' ("rollback mirror robocopy returned unacceptable raw exit " +
            $rcRollbackMirror + " (accepted: 0-7)")
    }
    Remove-CacheDirs -Root $destination

    # The restored tree is proven bidirectionally digest-equal to the BOUND
    # evidence (R633): no new module and no partial-install file can survive.
    $rollbackVerifyFailures = @(Get-DigestCompareFailures -Root $destination `
        -Map $boundBackup.pre_update_controller_identity.files_sha256 -FullInventory $false -Label 'restored tree')
    if ($rollbackVerifyFailures.Count -gt 0) {
        Exit-Refusal 'rollback_verify_failed' ("restored tree does not match the bound backup evidence (" +
            $rollbackVerifyFailures.Count + " difference(s)): " +
            (($rollbackVerifyFailures | Select-Object -First 10) -join '; '))
    }

    # Stale activation records are removed with CHECKED results - a rollback
    # never "succeeds" while the invalidated certification records survive.
    $removedRecords = @()
    foreach ($stale in @($manifestPath, $evidencePath)) {
        if (Test-Path -LiteralPath $stale) {
            Remove-Item -LiteralPath $stale -Force -ErrorAction SilentlyContinue
            if (Test-Path -LiteralPath $stale) {
                Exit-Refusal 'stale_record_removal_failed' ("could not remove the invalidated record: " + $stale)
            }
            $removedRecords += $stale
        }
    }

    $rollbackEvidence = [ordered]@{
        schema = 'controller_rollback_evidence/v1'
        generated_at_utc = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
        binding_file = (Get-Item -LiteralPath $BindingFile).FullName
        restored_from = [ordered]@{
            run_id = [string]$boundBackup.run_id
            backup_dir = [string]$boundBackup.backup_dir
            backup_evidence_sha256 = $backupBinding.file_sha256
        }
        destination = (Get-CanonicalPath $destination)
        robocopy_exit_codes = $script:RobocopyExitCodes
        restored_file_count = [int]$boundBackup.pre_update_controller_identity.file_count
        removed_stale_records = $removedRecords
        comparison = 'PASS'
        verdict = 'PASS'
    }
    Write-JsonAtomic -Payload $rollbackEvidence -Path $rollbackEvidencePath
    Write-Output ("ROLLBACK VERIFIED to backup run " + $boundBackup.run_id)
    Write-Output ("  restored      " + $boundBackup.pre_update_controller_identity.file_count +
        " file(s), robocopy raw exit " + $rcRollbackMirror)
    Write-Output ("  from          " + $boundControllerBackup)
    Write-Output ("  stale records " + $removedRecords.Count + " removed")
    Write-Output ("  evidence      " + $rollbackEvidencePath)
    Write-Output ("Journals were not touched. Re-run the section-10 doctor before any further action.")
    exit 0
}

Exit-Refusal 'unknown_phase' ("unsupported phase '" + $Phase + "'")
